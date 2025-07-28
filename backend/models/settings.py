"""
Settings-related Pydantic models.
"""

from __future__ import annotations
from pydantic import BaseModel
from typing import Optional


class NautobotSettingsRequest(BaseModel):
    """Nautobot settings request model."""
    url: str
    token: str
    timeout: int = 30
    verify_ssl: bool = True


class GitSettingsRequest(BaseModel):
    """Git settings request model."""
    repo_url: str
    branch: str = "main"
    username: Optional[str] = ""
    token: Optional[str] = ""
    config_path: str = "configs/"
    sync_interval: int = 15


class AllSettingsRequest(BaseModel):
    """All settings request model."""
    nautobot: NautobotSettingsRequest
    git: GitSettingsRequest


class ConnectionTestRequest(BaseModel):
    """Connection test request model."""
    url: str
    token: str
    timeout: int = 30
    verify_ssl: bool = True


class GitTestRequest(BaseModel):
    """Git connection test request model."""
    repo_url: str
    branch: str = "main"
    username: Optional[str] = ""
    token: Optional[str] = ""
