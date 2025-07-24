"""
Simple configuration module for Cockpit backend.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server Configuration
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True
    
    # Nautobot Configuration
    nautobot_url: str = "http://localhost:8080"
    nautobot_token: str = "your-nautobot-token-here"
    nautobot_timeout: int = 30
    
    # Authentication Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Demo credentials
    demo_username: str = "admin"
    demo_password: str = "admin"
    
    # CORS Configuration - simple strings for now
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"]
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()


if __name__ == "__main__":
    print("Cockpit Backend Configuration:")
    print(f"  Server: http://{settings.host}:{settings.port}")
    print(f"  Debug Mode: {settings.debug}")
    print(f"  Nautobot URL: {settings.nautobot_url}")
    print(f"  CORS Origins: {settings.cors_origins}")
