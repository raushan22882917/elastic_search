"""Production deployment configuration for rental platform search system."""
import os
import sys
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class ProductionSettings(BaseSettings):
    """Production settings with security and privacy focus."""
    
    # Application Settings
    app_name: str = Field(default="Rental Platform Search", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="production", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=4, alias="WORKERS")
    
    # Elasticsearch Settings (Production)
    elasticsearch_url: Optional[str] = Field(default=None, alias="ELASTICSEARCH_URL")
    elasticsearch_host: str = Field(default="localhost", alias="ELASTICSEARCH_HOST")
    elasticsearch_port: int = Field(default=9200, alias="ELASTICSEARCH_PORT")
    elasticsearch_scheme: str = Field(default="https", alias="ELASTICSEARCH_SCHEME")
    elasticsearch_user: Optional[str] = Field(default=None, alias="ELASTICSEARCH_USER")
    elasticsearch_password: Optional[str] = Field(default=None, alias="ELASTICSEARCH_PASSWORD")
    elasticsearch_api_key: Optional[str] = Field(default=None, alias="ELASTICSEARCH_API_KEY")
    elasticsearch_index_prefix: str = Field(default="rental_search", alias="ELASTICSEARCH_INDEX_PREFIX")
    
    # Google Cloud Settings (Production)
    google_cloud_project: Optional[str] = Field(default=None, alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="us-central1", alias="GOOGLE_CLOUD_LOCATION")
    vertex_ai_model: str = Field(default="gemini-1.5-flash", alias="VERTEX_AI_MODEL")
    vertex_ai_embedding_model: str = Field(default="text-embedding-004", alias="VERTEX_AI_EMBEDDING_MODEL")
    google_application_credentials: Optional[str] = Field(default=None, alias="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Gemini API Settings (Higher quota)
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    
    # Security Settings
    secret_key: str = Field(default="your-secret-key-change-in-production", alias="SECRET_KEY")
    allowed_hosts: list = Field(default=["*"], alias="ALLOWED_HOSTS")
    cors_origins: list = Field(default=["*"], alias="CORS_ORIGINS")
    
    # Search Settings
    hybrid_search_weight_vector: float = Field(default=0.7, alias="HYBRID_SEARCH_WEIGHT_VECTOR")
    hybrid_search_weight_keyword: float = Field(default=0.3, alias="HYBRID_SEARCH_WEIGHT_KEYWORD")
    max_search_results: int = Field(default=20, alias="MAX_SEARCH_RESULTS")
    min_relevance_score: float = Field(default=0.5, alias="MIN_RELEVANCE_SCORE")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, alias="RATE_LIMIT_PER_MINUTE")
    
    # Cache Settings
    cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")
    enable_cache: bool = Field(default=True, alias="ENABLE_CACHE")
    
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
        env_file = ".env.production"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


# Global production settings instance
production_settings = ProductionSettings()
