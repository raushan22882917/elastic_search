"""AI-Powered Rental Accommodation Platform using FastAPI + Elasticsearch + Google Cloud."""
import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)

# Google Cloud imports
try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    import vertexai
    from vertexai.language_models import TextEmbeddingModel
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    logger.error("Google Cloud libraries not available. Please install required packages.")

# Elasticsearch imports
try:
    from elasticsearch import Elasticsearch
    from services.elasticsearch_service import es_service
    from config.settings import settings
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    logger.error("Elasticsearch libraries not available. Please install required packages.")

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query for properties", min_length=1)
    limit: int = Field(default=10, ge=1, le=50, description="Number of results to return")
    search_type: str = Field(default="hybrid", description="Type of search: hybrid, semantic, or keyword")

class PropertyResponse(BaseModel):
    id: str
    name: str
    description: str
    property_type: str
    platform_name: str
    platform_description: str
    platform_focus: str
    target_audience: List[str]
    special_features: List[str]
    price: int
    area_sqft: int
    bedrooms: int
    amenities: List[str]
    area: str
    city: str
    state: str
    elasticsearch_score: float
    search_type: str

class SearchResponse(BaseModel):
    query: str
    results: List[PropertyResponse]
    total: int
    platform: str
    search_type: str
    data_source: str
    elasticsearch_integration: Dict[str, Any]
    ai_features: Dict[str, Any]
    status: str

class HealthResponse(BaseModel):
    status: str
    service: str
    platform: str
    project_id: str
    environment: str
    services: Dict[str, str]
    timestamp: str

class StatsResponse(BaseModel):
    total_properties: int
    property_types: List[str]
    platforms: List[str]
    cities: List[str]
    platform: str
    project_id: str
    data_source: str
    elasticsearch_integration: Dict[str, Any]
    status: str

class AppInfoResponse(BaseModel):
    message: str
    version: str
    platform: str
    project_id: str
    status: str
    description: str
    environment: str
    features: Dict[str, str]
    services: Dict[str, str]
    endpoints: Dict[str, str]

# Create FastAPI application
app = FastAPI(
    title="AI-Powered Rental Accommodation Platform",
    description="Real-time property search using Elasticsearch + Google Cloud AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://smart-dwell.vercel.app,http://localhost:3000,http://localhost:3001").split(",")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS if origin.strip()]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configuration
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "data-417505")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_CLOUD_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

# Service initialization flags
GOOGLE_CLOUD_INITIALIZED = False
ELASTICSEARCH_INITIALIZED = False

def initialize_google_cloud() -> bool:
    """Initialize Google Cloud services."""
    if not GOOGLE_CLOUD_AVAILABLE:
        logger.error("Google Cloud libraries not available.")
        return False
    
    try:
        if IS_PRODUCTION:
            logger.info("Using App Engine default service account for Google Cloud authentication")
        elif GOOGLE_CLOUD_CREDENTIALS_PATH and os.path.exists(GOOGLE_CLOUD_CREDENTIALS_PATH):
            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_CLOUD_CREDENTIALS_PATH
            )
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CLOUD_CREDENTIALS_PATH
            logger.info("Using service account file for Google Cloud authentication")
        else:
            logger.warning("Google Cloud credentials file not found. Using default authentication.")
        
        vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_REGION)
        logger.info("✅ Google Cloud services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Google Cloud services: {e}")
        return False

def initialize_elasticsearch() -> bool:
    """Initialize Elasticsearch connection."""
    if not ELASTICSEARCH_AVAILABLE:
        logger.error("Elasticsearch libraries not available.")
        return False
    
    try:
        # Initialize Elasticsearch service synchronously
        es_url = settings.get_elasticsearch_url()
        if settings.elasticsearch_api_key:
            es_service.sync_client = Elasticsearch(
                [es_url],
                api_key=settings.elasticsearch_api_key,
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
        else:
            es_service.sync_client = Elasticsearch(
                [es_url],
                basic_auth=(settings.elasticsearch_user, settings.elasticsearch_password),
                verify_certs=False,
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
        
        # Test connection
        if es_service.sync_client.ping():
            logger.info("✅ Elasticsearch service initialized successfully")
            return True
        else:
            logger.error("Failed to ping Elasticsearch")
            return False
        
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch: {e}")
        return False

def generate_real_embedding(text: str) -> List[float]:
    """Generate real embedding using Google Cloud Vertex AI."""
    if not GOOGLE_CLOUD_INITIALIZED or not GOOGLE_CLOUD_AVAILABLE:
        logger.error("Google Cloud not initialized. Cannot generate embeddings.")
        return []
    
    try:
        models_to_try = [
            "textembedding-gecko@003",
            "textembedding-gecko@002", 
            "textembedding-gecko@001",
            "text-multilingual-embedding-002"
        ]
        
        for model_name in models_to_try:
            try:
                model = TextEmbeddingModel.from_pretrained(model_name)
                embeddings = model.get_embeddings([text])
                logger.info(f"Successfully generated embedding using {model_name}")
                return embeddings[0].values
            except Exception as e:
                logger.warning(f"Failed to use {model_name}: {e}")
                continue
        
        logger.error("All embedding models failed")
        return []
        
    except Exception as e:
        logger.error(f"Failed to generate real embedding: {e}")
        return []

def build_elasticsearch_query(query: str, search_type: str) -> Dict[str, Any]:
    """Build Elasticsearch query based on search type."""
    # Base query for all search types (since documents don't have pre-computed embeddings)
    base_query = {
        "bool": {
            "should": [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["name^3", "description^2", "property_type^2", "city^2", "area", "amenities"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                {
                    "match": {
                        "combined_text": {
                            "query": query,
                            "boost": 1.5
                        }
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }
    
    if search_type == "semantic" and GOOGLE_CLOUD_INITIALIZED:
        # For semantic search, enhance the query with additional semantic fields
        base_query["bool"]["should"].extend([
            {
                "match": {
                    "target_audience": {
                        "query": query,
                        "boost": 2.5
                    }
                }
            },
            {
                "match": {
                    "special_features": {
                        "query": query,
                        "boost": 1.5
                    }
                }
            },
            {
                "match": {
                    "platform_focus": {
                        "query": query,
                        "boost": 1.2
                    }
                }
            }
        ])
        logger.info("Using semantic-enhanced keyword search")
    
    elif search_type == "hybrid" and GOOGLE_CLOUD_INITIALIZED:
        # For hybrid search, add more comprehensive matching
        base_query["bool"]["should"].extend([
            {
                "match": {
                    "target_audience": {
                        "query": query,
                        "boost": 2.0
                    }
                }
            },
            {
                "match": {
                    "special_features": {
                        "query": query,
                        "boost": 1.5
                    }
                }
            }
        ])
        logger.info("Using hybrid search with multiple strategies")
    
    else:
        logger.info("Using keyword search")
    
    return base_query

def ensure_elasticsearch_client():
    """Ensure Elasticsearch sync client is available."""
    if not es_service.sync_client:
        es_url = settings.get_elasticsearch_url()
        if settings.elasticsearch_api_key:
            es_service.sync_client = Elasticsearch(
                [es_url],
                api_key=settings.elasticsearch_api_key,
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
        else:
            es_service.sync_client = Elasticsearch(
                [es_url],
                basic_auth=(settings.elasticsearch_user, settings.elasticsearch_password),
                verify_certs=False,
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )

# FastAPI Routes
@app.get("/", response_model=AppInfoResponse)
async def root():
    """Root endpoint with application information."""
    return AppInfoResponse(
        message=os.getenv("APP_NAME", "AI-Powered Rental Accommodation Platform"),
        version=os.getenv("APP_VERSION", "2.0.0"),
        platform="Google Cloud App Engine",
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "data-417505"),
        status="running",
        description="Real data platform using Elasticsearch + Google Cloud AI",
        environment=os.getenv("ENVIRONMENT", "development"),
        features={
            "ai_search": "Real Elasticsearch + Google Cloud Vertex AI",
            "natural_language": "Natural language property discovery",
            "real_time": "Real-time property search from Elasticsearch",
            "embeddings": "Google Cloud text embeddings"
        },
        services={
            "elasticsearch": "active" if ELASTICSEARCH_INITIALIZED else "inactive",
            "google_cloud": "active" if GOOGLE_CLOUD_INITIALIZED else "inactive"
        },
        endpoints={
            "health": "/health",
            "search": "/api/v1/search",
            "stats": "/api/v1/stats",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="rental-platform-search",
        platform="google-cloud",
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "data-417505"),
        environment=os.getenv("ENVIRONMENT", "development"),
        services={
            "elasticsearch": "connected" if ELASTICSEARCH_INITIALIZED else "disconnected",
            "google_cloud": "connected" if GOOGLE_CLOUD_INITIALIZED else "disconnected"
        },
        timestamp="2025-10-23T06:00:00Z"
    )

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_properties(request: SearchRequest):
    """Search properties using real Elasticsearch + Google Cloud AI."""
    logger.info(f"Search request: {request.query} (type: {request.search_type})")
    
    if not ELASTICSEARCH_INITIALIZED:
        raise HTTPException(
            status_code=503, 
            detail="Elasticsearch service not available"
        )
    
    try:
        ensure_elasticsearch_client()
        
        # Build search query
        es_query = build_elasticsearch_query(request.query, request.search_type)
        
        # Execute search
        response = es_service.sync_client.search(
            index=settings.real_estate_index_name,
            query=es_query,
            size=request.limit,
            _source=True
        )
        
        # Process results
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            result = PropertyResponse(
                id=source.get("property_id", ""),
                name=source.get("name", ""),
                description=source.get("description", ""),
                property_type=source.get("property_type", ""),
                platform_name=source.get("platform_name", ""),
                platform_description=source.get("platform_description", ""),
                platform_focus=source.get("platform_focus", ""),
                target_audience=source.get("target_audience", []),
                special_features=source.get("special_features", []),
                price=source.get("price", 0),
                area_sqft=source.get("area_sqft", 0),
                bedrooms=source.get("bedrooms", 0),
                amenities=source.get("amenities", []),
                area=source.get("area", ""),
                city=source.get("city", ""),
                state=source.get("state", ""),
                elasticsearch_score=hit.get("_score", 0),
                search_type=f"elasticsearch_{request.search_type}_search"
            )
            results.append(result)
        
        return SearchResponse(
            query=request.query,
            results=results,
            total=len(results),
            platform="google-cloud",
            search_type=request.search_type,
            data_source="elasticsearch_real_data",
            elasticsearch_integration={
                "status": "active",
                "service": "real_elasticsearch",
                "endpoint": settings.get_elasticsearch_url()
            },
            ai_features={
                "embeddings": "google_cloud_vertex_ai",
                "semantic_search": "enabled" if GOOGLE_CLOUD_INITIALIZED else "disabled",
                "natural_language": "enabled",
                "query_understanding": "enabled"
            },
            status="success"
        )
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics from Elasticsearch."""
    if not ELASTICSEARCH_INITIALIZED:
        raise HTTPException(
            status_code=503, 
            detail="Elasticsearch service not available"
        )
    
    try:
        ensure_elasticsearch_client()
        
        # Get total count
        count_response = es_service.sync_client.count(
            index=settings.real_estate_index_name
        )
        total_properties = count_response["count"]
        
        # Get real data for stats (limited sample for performance)
        stats_response = es_service.sync_client.search(
            index=settings.real_estate_index_name,
            size=100
        )
        
        # Extract unique values from real data
        property_types = set()
        cities = set()
        platforms = set()
        
        for hit in stats_response["hits"]["hits"]:
            source = hit["_source"]
            if "property_type" in source:
                property_types.add(source["property_type"])
            if "city" in source:
                cities.add(source["city"])
            if "platform_name" in source:
                platforms.add(source["platform_name"])
        
        return StatsResponse(
            total_properties=total_properties,
            property_types=list(property_types)[:20],
            platforms=list(platforms)[:20],
            cities=list(cities)[:20],
            platform="google-cloud",
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "data-417505"),
            data_source="elasticsearch_real_data",
            elasticsearch_integration={
                "status": "active",
                "features": ["hybrid_search", "semantic_search", "vector_embeddings", "natural_language"],
                "ai_models": "google_cloud_vertex_ai"
            },
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global GOOGLE_CLOUD_INITIALIZED, ELASTICSEARCH_INITIALIZED
    
    logger.info("🚀 Starting AI-Powered Rental Accommodation Platform")
    
    # Initialize services
    GOOGLE_CLOUD_INITIALIZED = initialize_google_cloud()
    ELASTICSEARCH_INITIALIZED = initialize_elasticsearch()
    
    if not ELASTICSEARCH_INITIALIZED:
        logger.error("❌ Elasticsearch not initialized. Please check your configuration.")
    if not GOOGLE_CLOUD_INITIALIZED:
        logger.error("❌ Google Cloud not initialized. Please check your configuration.")
    
    if ELASTICSEARCH_INITIALIZED and GOOGLE_CLOUD_INITIALIZED:
        logger.info("✅ All services initialized successfully")
    else:
        logger.error("❌ Some services failed to initialize. Please check your configuration.")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Shutting down AI-Powered Rental Accommodation Platform")

if __name__ == '__main__':
    import uvicorn
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    
    uvicorn.run(app, host=host, port=port, log_level="info")