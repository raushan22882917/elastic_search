"""Elasticsearch service for hybrid search capabilities."""
import logging
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Service for managing Elasticsearch operations with hybrid search."""
    
    def __init__(self):
        """Initialize Elasticsearch service."""
        self.client: Optional[AsyncElasticsearch] = None
        self.sync_client: Optional[Elasticsearch] = None
        
    async def connect(self) -> None:
        """Establish connection to Elasticsearch."""
        try:
            es_url = settings.get_elasticsearch_url()
            logger.info(f"Attempting to connect to Elasticsearch at: {es_url}")
            
            # Configure authentication
            if settings.elasticsearch_api_key:
                # Use API key authentication (Elastic Cloud)
                self.client = AsyncElasticsearch(
                    [es_url],
                    api_key=settings.elasticsearch_api_key,
                    request_timeout=60,
                    max_retries=5,
                    retry_on_timeout=True
                )
                logger.info("Using Elasticsearch API key authentication")
            else:
                # Use basic authentication (local/self-hosted)
                self.client = AsyncElasticsearch(
                    [es_url],
                    basic_auth=(settings.elasticsearch_user, settings.elasticsearch_password),
                    verify_certs=False,
                    request_timeout=60,
                    max_retries=5,
                    retry_on_timeout=True
                )
                logger.info("Using Elasticsearch basic authentication")
            
            # Test connection
            info = await self.client.info()
            logger.info(f"Connected to Elasticsearch: {info['version']['number']}")
            logger.info(f"Cluster name: {info['cluster_name']}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            logger.error("This might be due to:")
            logger.error("1. Elasticsearch instance not running")
            logger.error("2. Incorrect hostname/URL")
            logger.error("3. Network connectivity issues")
            logger.error("4. Authentication problems")
            
            # Try fallback to localhost if the configured host fails
            if es_url != "http://localhost:9200":
                logger.info("Attempting fallback connection to localhost:9200")
                try:
                    self.client = AsyncElasticsearch(
                        ["http://localhost:9200"],
                        basic_auth=("elastic", "changeme"),
                        verify_certs=False,
                        request_timeout=10,
                        max_retries=2,
                        retry_on_timeout=True
                    )
                    info = await self.client.info()
                    logger.info(f"✓ Fallback connection successful: {info['version']['number']}")
                    return
                except Exception as fallback_error:
                    logger.error(f"Fallback connection also failed: {fallback_error}")
            
            raise
    
    async def close(self) -> None:
        """Close Elasticsearch connection."""
        if self.client:
            await self.client.close()
            logger.info("Closed Elasticsearch connection")
    
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def create_conversations_index(self) -> None:
        """Create conversations index for chat history."""
        index_name = settings.conversations_index_name
        
        exists = await self.client.indices.exists(index=index_name)
        if exists:
            logger.info(f"Index {index_name} already exists")
            return
        
        mapping = {
            "mappings": {
                "properties": {
                    "session_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "role": {"type": "keyword"},  # user or assistant
                    "message": {"type": "text"},
                    "context": {"type": "object"},
                    "search_results": {"type": "object"},
                    "metadata": {"type": "object"}
                }
            }
        }
        
        await self.client.indices.create(index=index_name, body=mapping)
        logger.info(f"Created index: {index_name}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def create_real_estate_index(self) -> None:
        """Create real estate index with geo-search and property-specific mappings."""
        index_name = settings.real_estate_index_name
        
        # Check if index exists
        exists = await self.client.indices.exists(index=index_name)
        if exists:
            logger.info(f"Index {index_name} already exists")
            return
        
        # Define index mapping for real estate properties
        mapping = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "property_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "asciifolding",
                                "property_stop",
                                "property_synonym",
                                "property_stemmer"
                            ]
                        }
                    },
                    "filter": {
                        "property_stop": {
                            "type": "stop",
                            "stopwords": "_english_"
                        },
                        "property_synonym": {
                            "type": "synonym",
                            "synonyms": [
                                "apartment, flat, unit",
                                "villa, house, bungalow",
                                "bhk, bedroom",
                                "sqft, square feet, sq ft",
                                "metro, subway, train",
                                "school, education, college",
                                "hospital, medical, healthcare"
                            ]
                        },
                        "property_stemmer": {
                            "type": "stemmer",
                            "language": "english"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "property_id": {"type": "keyword"},
                    "name": {
                        "type": "text",
                        "analyzer": "property_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {
                                "type": "completion",
                                "analyzer": "simple"
                            }
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "property_analyzer"
                    },
                    "property_type": {
                        "type": "keyword",
                        "fields": {
                            "text": {"type": "text"}
                        }
                    },
                    "bedrooms": {"type": "integer"},
                    "bathrooms": {"type": "integer"},
                    "area_sqft": {"type": "float"},
                    "carpet_area_sqft": {"type": "float"},
                    "price": {"type": "float"},
                    "price_per_sqft": {"type": "float"},
                    "currency": {"type": "keyword"},
                    "property_status": {"type": "keyword"},
                    "furnishing": {"type": "keyword"},
                    "floor": {"type": "integer"},
                    "total_floors": {"type": "integer"},
                    "age_years": {"type": "float"},
                    "facing": {"type": "keyword"},
                    "parking_spaces": {"type": "integer"},
                    
                    # Geo-location for geo-search
                    "geo_location": {
                        "type": "geo_point"
                    },
                    "geo_location_details": {
                        "type": "object",
                        "properties": {
                            "address": {"type": "text"},
                            "locality": {"type": "keyword"},
                            "city": {"type": "keyword"},
                            "state": {"type": "keyword"},
                            "pincode": {"type": "keyword"},
                            "place_id": {"type": "keyword"}
                        }
                    },
                    
                    # Builder and project information
                    "builder_name": {
                        "type": "keyword",
                        "fields": {
                            "text": {"type": "text"}
                        }
                    },
                    "project_name": {
                        "type": "keyword",
                        "fields": {
                            "text": {"type": "text"}
                        }
                    },
                    "rera_id": {"type": "keyword"},
                    
                    # Amenities
                    "amenities": {
                        "type": "keyword"
                    },
                    
                    # Nearby amenities
                    "nearby_amenities": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "text"},
                            "type": {"type": "keyword"},
                            "distance_km": {"type": "float"},
                            "rating": {"type": "float"},
                            "address": {"type": "text"},
                            "place_id": {"type": "keyword"}
                        }
                    },
                    
                    # Media
                    "image_urls": {"type": "keyword"},
                    "virtual_tour_url": {"type": "keyword"},
                    
                    # Market information
                    "price_trend": {"type": "keyword"},
                    "market_value": {"type": "float"},
                    "investment_score": {"type": "float"},
                    
                    # AI generated content
                    "ai_summary": {"type": "text"},
                    "ai_highlights": {"type": "text"},
                    "ai_recommendations": {"type": "text"},
                    
                    # Vector embedding for semantic search
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 768,
                        "index": True,
                        "similarity": "cosine"
                    },
                    
                    # Combined text for embedding generation
                    "combined_text": {"type": "text"},
                    
                    # Metadata
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "is_featured": {"type": "boolean"},
                    "views_count": {"type": "integer"},
                    "likes_count": {"type": "integer"}
                }
            }
        }
        
        await self.client.indices.create(index=index_name, body=mapping)
        logger.info(f"Created real estate index: {index_name}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def create_inquiries_index(self) -> None:
        """Create inquiries index for contact inquiries."""
        index_name = f"{settings.elasticsearch_index_prefix}_inquiries"
        
        # Check if index exists
        exists = await self.client.indices.exists(index=index_name)
        if exists:
            logger.info(f"Index {index_name} already exists")
            return
        
        mapping = {
            "mappings": {
                "properties": {
                    "inquiry_id": {"type": "keyword"},
                    "property_id": {"type": "keyword"},
                    "user_name": {"type": "text"},
                    "user_email": {"type": "keyword"},
                    "user_phone": {"type": "keyword"},
                    "inquiry_type": {"type": "keyword"},
                    "message": {"type": "text"},
                    "preferred_contact_method": {"type": "keyword"},
                    "budget_range": {"type": "text"},
                    "move_in_date": {"type": "date"},
                    "additional_requirements": {"type": "text"},
                    "status": {"type": "keyword"},
                    "priority": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "property_details": {"type": "object"}
                }
            }
        }
        
        await self.client.indices.create(index=index_name, body=mapping)
        logger.info(f"Created inquiries index: {index_name}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def create_site_visits_index(self) -> None:
        """Create site visits index for scheduled visits."""
        index_name = f"{settings.elasticsearch_index_prefix}_site_visits"
        
        # Check if index exists
        exists = await self.client.indices.exists(index=index_name)
        if exists:
            logger.info(f"Index {index_name} already exists")
            return
        
        mapping = {
            "mappings": {
                "properties": {
                    "visit_id": {"type": "keyword"},
                    "property_id": {"type": "keyword"},
                    "user_name": {"type": "text"},
                    "user_email": {"type": "keyword"},
                    "user_phone": {"type": "keyword"},
                    "preferred_date": {"type": "date"},
                    "preferred_time": {"type": "keyword"},
                    "confirmed_date": {"type": "date"},
                    "confirmed_time": {"type": "keyword"},
                    "group_size": {"type": "integer"},
                    "special_requirements": {"type": "text"},
                    "status": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "property_details": {"type": "object"}
                }
            }
        }
        
        await self.client.indices.create(index=index_name, body=mapping)
        logger.info(f"Created site visits index: {index_name}")
    
    async def index_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Index a single property."""
        try:
            result = await self.client.index(
                index=settings.real_estate_index_name,
                id=property_data.get("property_id"),
                document=property_data,
                refresh=True
            )
            logger.debug(f"Indexed property: {property_data.get('property_id')}")
            return result
        except Exception as e:
            logger.error(f"Failed to index property: {e}")
            raise
    
    async def bulk_index_properties(self, properties: List[Dict[str, Any]]) -> None:
        """Bulk index multiple properties."""
        try:
            actions = [
                {
                    "_index": settings.real_estate_index_name,
                    "_id": property_data.get("property_id"),
                    "_source": property_data
                }
                for property_data in properties
            ]
            
            success, failed = await async_bulk(self.client, actions, raise_on_error=False)
            logger.info(f"Bulk indexed {success} properties, {len(failed)} failed")
            
            if failed:
                logger.error(f"Failed items: {failed}")
                
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            raise
    
    
    
    async def save_conversation_message(self, message_data: Dict[str, Any]) -> None:
        """Save a conversation message to the index."""
        try:
            await self.client.index(
                index=settings.conversations_index_name,
                document=message_data
            )
            logger.debug(f"Saved conversation message for session: {message_data.get('session_id')}")
        except Exception as e:
            logger.error(f"Failed to save conversation message: {e}")
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session."""
        try:
            response = await self.client.search(
                index=settings.conversations_index_name,
                query={"term": {"session_id": session_id}},
                sort=[{"timestamp": {"order": "desc"}}],
                size=limit
            )
            
            messages = [hit["_source"] for hit in response["hits"]["hits"]]
            return list(reversed(messages))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []
    
    async def get_property_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get a property by ID."""
        try:
            response = await self.client.get(
                index=settings.real_estate_index_name,
                id=property_id
            )
            return response["_source"]
        except Exception as e:
            logger.error(f"Failed to get property {property_id}: {e}")
            return None
    
    async def get_property_recommendations(
        self,
        property_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get property recommendations based on a property."""
        try:
            # Get the source property
            property_data = await self.get_property_by_id(property_id)
            if not property_data or "embedding" not in property_data:
                return []
            
            # Find similar properties using vector similarity
            query = {
                "script_score": {
                    "query": {
                        "bool": {
                            "must_not": {"term": {"property_id": property_id}},
                            "filter": [
                                {"term": {"property_status": "available"}}
                            ]
                        }
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": property_data["embedding"]}
                    }
                }
            }
            
            response = await self.client.search(
                index=settings.real_estate_index_name,
                query=query,
                size=limit
            )
            
            return [hit["_source"] for hit in response["hits"]["hits"]]
            
        except Exception as e:
            logger.error(f"Failed to get property recommendations: {e}")
            return []
    
    async def aggregate_properties(self, agg_field: str) -> Dict[str, Any]:
        """Get aggregations for properties (e.g., property_types, cities)."""
        try:
            response = await self.client.search(
                index=settings.real_estate_index_name,
                size=0,
                aggs={
                    f"{agg_field}_counts": {
                        "terms": {
                            "field": agg_field,
                            "size": 50
                        }
                    }
                }
            )
            
            return response["aggregations"]
            
        except Exception as e:
            logger.error(f"Failed to get property aggregations: {e}")
            return {}


# Global service instance
es_service = ElasticsearchService()

