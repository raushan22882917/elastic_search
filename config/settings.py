"""Application settings and configuration."""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    app_name: str = Field(default="AI-Powered Search Platform", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=4, alias="WORKERS")
    
    # Elasticsearch Settings
    elasticsearch_url: Optional[str] = Field(default=None, alias="ELASTICSEARCH_URL")
    elasticsearch_host: str = Field(default="localhost", alias="ELASTICSEARCH_HOST")
    elasticsearch_port: int = Field(default=9200, alias="ELASTICSEARCH_PORT")
    elasticsearch_scheme: str = Field(default="http", alias="ELASTICSEARCH_SCHEME")
    elasticsearch_user: Optional[str] = Field(default="elastic", alias="ELASTICSEARCH_USER")
    elasticsearch_password: Optional[str] = Field(default="changeme", alias="ELASTICSEARCH_PASSWORD")
    elasticsearch_api_key: Optional[str] = Field(default=None, alias="ELASTICSEARCH_API_KEY")
    elasticsearch_index_prefix: str = Field(default="ai_search", alias="ELASTICSEARCH_INDEX_PREFIX")
    
    # Google Maps API Settings
    google_maps_api_key: Optional[str] = Field(default=None, alias="GOOGLE_MAPS_API_KEY")
    
    # Gemini API Settings (Alternative to Vertex AI)
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    
    # Google Cloud Settings
    google_cloud_project: str = Field(default="data-417505", alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="us-central1", alias="GOOGLE_CLOUD_LOCATION")
    vertex_ai_model: str = Field(default="gemini-1.5-flash-002", alias="VERTEX_AI_MODEL")
    vertex_ai_embedding_model: str = Field(default="text-embedding-004", alias="VERTEX_AI_EMBEDDING_MODEL")
    google_application_credentials: Optional[str] = Field(default=None, alias="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Search Settings
    hybrid_search_weight_vector: float = Field(default=0.7, alias="HYBRID_SEARCH_WEIGHT_VECTOR")
    hybrid_search_weight_keyword: float = Field(default=0.3, alias="HYBRID_SEARCH_WEIGHT_KEYWORD")
    max_search_results: int = Field(default=20, alias="MAX_SEARCH_RESULTS")
    min_relevance_score: float = Field(default=0.5, alias="MIN_RELEVANCE_SCORE")
    
    # Agent Settings
    agent_max_context_messages: int = Field(default=10, alias="AGENT_MAX_CONTEXT_MESSAGES")
    agent_temperature: float = Field(default=0.7, alias="AGENT_TEMPERATURE")
    agent_max_output_tokens: int = Field(default=1024, alias="AGENT_MAX_OUTPUT_TOKENS")
    
    # Cache Settings
    cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")
    enable_cache: bool = Field(default=True, alias="ENABLE_CACHE")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")
    
    @field_validator("hybrid_search_weight_vector", "hybrid_search_weight_keyword")
    @classmethod
    def validate_weights(cls, v: float) -> float:
        """Validate that weights are between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Weight must be between 0 and 1")
        return v
    
    def get_elasticsearch_url(self) -> str:
        """Get full Elasticsearch URL."""
        if self.elasticsearch_url:
            return self.elasticsearch_url
        return f"{self.elasticsearch_scheme}://{self.elasticsearch_host}:{self.elasticsearch_port}"
    
    @property
    def conversations_index_name(self) -> str:
        """Get conversations index name."""
        return f"{self.elasticsearch_index_prefix}_conversations"
    
    @property
    def real_estate_index_name(self) -> str:
        """Get real estate index name."""
        return f"{self.elasticsearch_index_prefix}_real_estate"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


# Global settings instance
settings = Settings()

