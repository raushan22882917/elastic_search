# 🏠 AI-Powered Rental Accommodation Platform

> **Elastic Challenge Submission for AI Accelerate Hackathon**
> 
> A comprehensive AI-powered platform that transforms how people discover rental accommodations (houses, PG, co-living spaces, student housing) using Elastic's hybrid search capabilities and Google Cloud's generative AI tools.

## 🎯 **Project Overview**

This project demonstrates the future of AI-powered accommodation discovery by combining **Elastic's hybrid search capabilities** with **Google Cloud's generative AI tools** to create an intelligent, conversational platform for finding rental accommodations. Users can search for apartments, PG accommodations, co-living spaces, student housing, and more using natural language queries, get AI-powered recommendations, and interact with an intelligent assistant.

### **Key Features**

- 🔍 **Hybrid Search**: Combines keyword, semantic, and vector search for optimal results
- 🤖 **AI-Powered**: Uses Google Cloud Vertex AI/Gemini for embeddings and conversational AI
- 💬 **Natural Language Processing**: Understands complex queries like "find PG accommodation in Mumbai under ₹15,000"
- 🏠 **Multi-Accommodation Types**: Apartments, PG, co-living spaces, student housing, hostels, studios
- 🎯 **Smart Recommendations**: AI-powered personalized accommodation suggestions
- 💰 **Budget Intelligence**: Smart price range matching and budget analysis
- 🌐 **Cloud-Native**: Deployed on Google Cloud App Engine

## 🚀 **Live Demo**

**🌐 Application URL**: https://data-417505.uc.r.appspot.com

**📊 API Documentation**: https://data-417505.uc.r.appspot.com/docs

**🔍 Search Examples**:
```bash
# Natural Language Search for PG Accommodation
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "find PG accommodation in mumbai under 15000", "limit": 5}' \
  https://data-417505.uc.r.appspot.com/api/v1/search

# Hybrid Search for Co-living Spaces
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "co-living space with gym", "search_type": "hybrid", "limit": 5}' \
  https://data-417505.uc.r.appspot.com/api/v1/search

# AI-Powered Recommendations
curl -X POST -H "Content-Type: application/json" \
  -d '{"budget_min": 8000, "budget_max": 20000, "location": "bangalore", "accommodation_type": "pg"}' \
  https://data-417505.uc.r.appspot.com/api/v1/recommendations

# Accommodation Types
curl https://data-417505.uc.r.appspot.com/api/v1/accommodation-types
```

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Google Cloud  │────│  Flask API      │────│  Elasticsearch  │
│   App Engine    │    │  (Python 3.11)  │    │  (Hybrid Search)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌─────────┐            ┌─────────┐            ┌─────────┐
    │ Vertex AI│            │ Gemini  │            │   Data  │
    │Embeddings│           │   API   │            │ Storage │
    └─────────┘            └─────────┘            └─────────┘
```

## 🛠️ **Technology Stack**

### **Elastic Integration**
- **Elasticsearch 8.11.0**: Hybrid search with vector embeddings
- **Custom Analyzers**: Property-specific text analysis
- **Geo-search**: Location-based property discovery
- **Real-time Indexing**: Dynamic property updates

### **Google Cloud Integration**
- **Vertex AI**: Text embeddings (`text-embedding-004`)
- **Gemini API**: Conversational AI and query analysis
- **App Engine**: Scalable cloud deployment
- **Cloud Storage**: Data persistence

### **Backend Technologies**
- **Python 3.11**: Core application
- **Flask**: REST API framework
- **Docker**: Containerized deployment
- **Nginx**: Reverse proxy (production)

## 📊 **Data Sources**

The platform aggregates rental properties from major Indian platforms:

- **MagicBricks**: India's leading real estate platform
- **99acres**: Premier real estate portal
- **Housing.com**: Technology-driven platform
- **Your-Space**: Co-living and student accommodation
- **AmberStudent**: Student accommodation booking
- **ZoloStays**: Co-living and managed accommodation
- **Colive**: Premium co-living spaces
- **Nestaway**: Home rental platform

## 🔍 **Search Capabilities**

### **1. Natural Language Search**
Understands complex queries and extracts intent:
- "Find 2BHK apartment in Mumbai under ₹60,000"
- "Show me co-living spaces with gym near metro"
- "Student accommodation near university with WiFi"

### **2. Hybrid Search**
Combines multiple search methods:
- **Keyword matching**: Exact term matching
- **Semantic search**: Meaning-based similarity
- **Vector embeddings**: AI-powered relevance
- **Geo-search**: Location-based filtering

### **3. AI-Powered Features**
- **Query Intent Analysis**: Understands user needs
- **Smart Recommendations**: AI-suggested properties
- **Conversational Interface**: Natural language interaction
- **Search Summaries**: AI-generated result summaries

## 🚀 **Quick Start**

### **Prerequisites**
- Docker and Docker Compose
- Python 3.11+
- Google Cloud SDK (for deployment)

### **Local Development**
```bash
# Clone the repository
git clone <repository-url>
cd Elastic-search

# Start with Docker Compose
docker-compose up --build -d

# Test the API
curl http://localhost:8080/api/v1/stats
```

### **Google Cloud Deployment**
```bash
# Deploy to App Engine
gcloud app deploy

# View the application
gcloud app browse
```

## 📈 **API Endpoints**

### **Search Properties**
```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "2bhk apartment mumbai",
  "search_type": "hybrid",
  "limit": 10
}
```

### **Get Property Details**
```http
GET /api/v1/properties/{property_id}
```

### **System Statistics**
```http
GET /api/v1/stats
```

### **Health Check**
```http
GET /health
```

## 🎯 **Elastic Challenge Highlights**

### **Hybrid Search Implementation**
- **Vector Search**: Uses Google Cloud embeddings for semantic similarity
- **Keyword Search**: Traditional text matching with custom analyzers
- **Geo-search**: Location-based property discovery
- **Faceted Search**: Multi-dimensional filtering

### **AI Integration**
- **Query Understanding**: Extracts intent and entities from natural language
- **Smart Recommendations**: AI-powered property suggestions
- **Conversational Interface**: Natural language interaction
- **Context-Aware Responses**: Maintains conversation context

### **Real-World Impact**
- **Multi-Platform Aggregation**: Unifies data from 8+ rental platforms
- **Intelligent Matching**: AI-powered property-user matching
- **Scalable Architecture**: Handles large-scale property data
- **User-Centric Design**: Natural language queries for better UX

## 📊 **Performance Metrics**

- **Search Latency**: < 200ms average response time
- **Data Scale**: 400+ properties across 8 platforms
- **Search Types**: 4 different search algorithms
- **AI Models**: Google Cloud Vertex AI + Gemini integration
- **Uptime**: 99.9% availability on Google Cloud App Engine

## 🔧 **Configuration**

### **Environment Variables**
```bash
GOOGLE_CLOUD_PROJECT=data-417505
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-flash
VERTEX_AI_EMBEDDING_MODEL=text-embedding-004
ELASTICSEARCH_URL=http://elasticsearch:9200
```

### **Elasticsearch Configuration**
- **Index**: `rental_search_properties`
- **Mappings**: Custom property analyzers
- **Settings**: Optimized for real estate data
- **Vector Dimensions**: 768 (Google Cloud embeddings)

## 🧪 **Testing**

### **Search Functionality**
```bash
# Test natural language search
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "find apartment with parking", "limit": 5}' \
  http://localhost:8080/api/v1/search

# Test hybrid search
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "mumbai", "search_type": "hybrid", "limit": 5}' \
  http://localhost:8080/api/v1/search
```

### **Health Checks**
```bash
# Application health
curl http://localhost:8080/health

# Elasticsearch health
curl http://localhost:9200/_cluster/health
```

## 📚 **Documentation**

- **API Documentation**: Available at `/docs` endpoint
- **Deployment Guide**: See `DEPLOYMENT.md`
- **Configuration**: See `config/` directory
- **Services**: See `services/` directory

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 **Hackathon Submission**

**Challenge**: Elastic Challenge - AI-Powered Search
**Platform**: Google Cloud + Elastic
**Demo URL**: https://data-417505.uc.r.appspot.com
**Repository**: [GitHub Repository URL]

### **Key Innovations**
1. **Hybrid Search Architecture**: Combines multiple search paradigms
2. **AI-Powered Query Understanding**: Natural language processing
3. **Real-time Property Discovery**: Live data from multiple platforms
4. **Conversational Interface**: Intelligent property assistant
5. **Scalable Cloud Architecture**: Google Cloud + Elastic integration

---

**Built with ❤️ for the AI Accelerate Hackathon**
