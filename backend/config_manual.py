"""
Manual configuration module for Cockpit backend.
Simple approach without complex pydantic parsing.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_env_list(key: str, default: list = None) -> list:
    """Get list from comma-separated environment variable."""
    if default is None:
        default = []
    value = os.getenv(key, '')
    if not value:
        return default
    return [item.strip() for item in value.split(',') if item.strip()]

class Settings:
    # Server Configuration
    host: str = os.getenv('SERVER_HOST', '127.0.0.1')
    port: int = int(os.getenv('SERVER_PORT', '8000'))
    debug: bool = get_env_bool('DEBUG', True)
    
    # Nautobot Configuration
    nautobot_url: str = os.getenv('NAUTOBOT_HOST', 'http://localhost:8080')
    nautobot_token: str = os.getenv('NAUTOBOT_TOKEN', 'your-nautobot-token-here')
    nautobot_timeout: int = int(os.getenv('NAUTOBOT_TIMEOUT', '30'))
    
    # Authentication Configuration
    secret_key: str = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    algorithm: str = os.getenv('ALGORITHM', 'HS256')
    access_token_expire_minutes: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    
    # Demo credentials
    demo_username: str = os.getenv('DEMO_USERNAME', 'admin')
    demo_password: str = os.getenv('DEMO_PASSWORD', 'admin')
    
    # CORS Configuration
    cors_origins: list = get_env_list('CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:3000'])

# Global settings instance
settings = Settings()

if __name__ == "__main__":
    print("Cockpit Backend Configuration:")
    print(f"  Server: http://{settings.host}:{settings.port}")
    print(f"  Debug Mode: {settings.debug}")
    print(f"  Nautobot URL: {settings.nautobot_url}")
    print(f"  CORS Origins: {settings.cors_origins}")
