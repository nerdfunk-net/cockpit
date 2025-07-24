"""
Configuration module for Cockpit backend.
Handles loading configuration from environment variables and config files.
Docker-compatible with environment variable override support.
"""

import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    Environment variables take precedence over .env file values.
    Docker-compatible configuration system.
    """
    
    # Server Configuration
    server_host: str = Field(
        default="0.0.0.0", 
        env="SERVER_HOST",
        description="Server host address (0.0.0.0 for Docker)"
    )
    server_port: int = Field(
        default=8000, 
        env="SERVER_PORT",
        description="Server port number"
    )
    debug: bool = Field(
        default=False, 
        env="DEBUG",
        description="Enable debug mode"
    )
    
    # Nautobot Configuration
    nautobot_host: str = Field(
        default="http://localhost:8080", 
        env="NAUTOBOT_HOST",
        description="Nautobot instance URL"
    )
    nautobot_token: str = Field(
        default="your-nautobot-token-here", 
        env="NAUTOBOT_TOKEN",
        description="Nautobot API token"
    )
    nautobot_timeout: int = Field(
        default=30, 
        env="NAUTOBOT_TIMEOUT",
        description="Request timeout in seconds"
    )
    
    # Authentication Configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production", 
        env="SECRET_KEY",
        description="JWT signing secret key"
    )
    algorithm: str = Field(
        default="HS256", 
        env="ALGORITHM",
        description="JWT algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30, 
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="JWT token expiration time in minutes"
    )
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173", 
        env="CORS_ORIGINS",
        description="Allowed CORS origins (comma-separated)"
    )
    cors_allow_credentials: bool = Field(
        default=True, 
        env="CORS_ALLOW_CREDENTIALS",
        description="Allow CORS credentials"
    )
    cors_allow_methods: List[str] = Field(
        default=["*"], 
        env="CORS_ALLOW_METHODS",
        description="Allowed CORS methods"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"], 
        env="CORS_ALLOW_HEADERS",
        description="Allowed CORS headers"
    )
    
    # Database Configuration (for future use)
    database_url: Optional[str] = Field(
        default=None, 
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO", 
        env="LOG_LEVEL",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        env="LOG_FORMAT",
        description="Log message format"
    )
    
    
    @field_validator('cors_origins', mode='before')
    @classmethod  
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(',') if origin.strip()]
            return origins if origins else ["http://localhost:3000"]
        return v if v else ["http://localhost:3000"]
    
    @field_validator('cors_allow_methods', mode='before')
    @classmethod
    def parse_cors_methods(cls, v):
        """Parse CORS methods from comma-separated string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(',') if method.strip()]
        return v
    
    @field_validator('cors_allow_headers', mode='before')
    @classmethod
    def parse_cors_headers(cls, v):
        """Parse CORS headers from comma-separated string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(',') if header.strip()]
        return v
    
    @field_validator('nautobot_host')
    @classmethod
    def validate_nautobot_host(cls, v):
        """Ensure nautobot_host doesn't end with a slash."""
        return v.rstrip('/')
    
    @field_validator('secret_key')  
    @classmethod
    def validate_secret_key(cls, v):
        """Ensure secret key is not the default in production."""
        if not os.getenv('DEBUG', '').lower() == 'true':
            if v == "your-secret-key-change-in-production":
                # Only warn in Docker, don't fail
                if os.getenv('DOCKER_CONTAINER'):
                    print("WARNING: Using default secret key in production!")
                else:
                    raise ValueError("Secret key must be changed for production use")
        return v
    
    @field_validator('nautobot_token')
    @classmethod
    def validate_nautobot_token(cls, v):
        """Warn if using default Nautobot token."""
        if v == "your-nautobot-token-here":
            print("WARNING: Using default Nautobot token. Please set NAUTOBOT_TOKEN environment variable.")
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()

# Print configuration summary for Docker debugging
if os.getenv('DEBUG', '').lower() == 'true' or os.getenv('DOCKER_CONTAINER'):
    print(f"🐳 Cockpit Configuration:")
    print(f"  Server: {settings.server_host}:{settings.server_port}")
    print(f"  Debug: {settings.debug}")
    print(f"  Nautobot: {settings.nautobot_host}")
    print(f"  Log Level: {settings.log_level}")
    print(f"  CORS Origins: {settings.cors_origins}")
