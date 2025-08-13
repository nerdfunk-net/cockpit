from __future__ import annotations
"""API router for Scan & Add wizard operations."""

import asyncio
import os
import json
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
import ipaddress

from core.auth import verify_token
from services.scan_service import scan_service
from services.nautobot import nautobot_service
from template_manager import template_manager
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/scan", tags=["scan"], dependencies=[Depends(verify_token)])


# Request/Response Models
class ScanStartRequest(BaseModel):
    cidrs: List[str] = Field(..., max_items=10, description="List of CIDR networks to scan")
    credential_ids: List[int] = Field(..., description="List of credential IDs to try")
    discovery_mode: str = Field(default="napalm", description="Discovery mode: napalm or ssh-login")
    parser_template_ids: Optional[List[int]] = Field(default=None, description="Template IDs to use for parsing 'show version' output (textfsm)")

    @validator("discovery_mode")
    def validate_discovery_mode(cls, v: str):
        if v not in ["napalm", "ssh-login"]:
            raise ValueError("discovery_mode must be 'napalm' or 'ssh-login'")
        return v

    @validator("cidrs")
    def validate_cidrs(cls, v: List[str]):
        if not v:
            raise ValueError("At least one CIDR required")
        
        cleaned = []
        seen = set()
        
        for cidr in v:
            try:
                network = ipaddress.ip_network(cidr, strict=False)
            except Exception:
                raise ValueError(f"Invalid CIDR format: {cidr}")
            
            # Enforce /22 minimum (max ~1024 hosts per spec)
            if network.prefixlen < 22:
                raise ValueError(f"CIDR too large (minimum /22): {cidr}")
            
            # Deduplicate
            if cidr not in seen:
                seen.add(cidr)
                cleaned.append(cidr)
                
        return cleaned

    @validator("credential_ids")
    def validate_credentials(cls, v: List[int]):
        if not v:
            raise ValueError("At least one credential ID required")
        return v


class ScanStartResponse(BaseModel):
    job_id: str
    total_targets: int
    state: str


class ScanProgress(BaseModel):
    total: int
    scanned: int
    alive: int
    authenticated: int
    unreachable: int
    auth_failed: int
    driver_not_supported: int


class ScanStatusResponse(BaseModel):
    job_id: str
    state: str
    progress: ScanProgress
    results: List[Dict[str, Any]]


class OnboardDevice(BaseModel):
    ip: str
    credential_id: int
    device_type: str  # 'cisco' | 'linux'
    hostname: Optional[str] = None
    platform: Optional[str] = None
    
    # Cisco-specific fields
    location: Optional[str] = None
    namespace: Optional[str] = "Global"
    role: Optional[str] = None
    status: Optional[str] = "Active"
    interface_status: Optional[str] = "Active"
    ip_status: Optional[str] = "Active"


class OnboardRequest(BaseModel):
    devices: List[OnboardDevice]


class OnboardResponse(BaseModel):
    accepted: int
    cisco_queued: int
    linux_added: int
    inventory_path: Optional[str] = None
    job_ids: List[str] = Field(default_factory=list)


# API Endpoints
@router.post("/start", response_model=ScanStartResponse)
async def start_scan(request: ScanStartRequest):
    """Start a new network scan job."""
    try:
        job = await scan_service.start_job(
            request.cidrs,
            request.credential_ids,
            request.discovery_mode,
            parser_template_ids=request.parser_template_ids,
        )
        
        return ScanStartResponse(
            job_id=job.job_id,
            total_targets=job.total_targets,
            state=job.state
        )
    except Exception as e:
        logger.error(f"Failed to start scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scan: {str(e)}"
        )


@router.get("/{job_id}/status", response_model=ScanStatusResponse)
async def get_scan_status(job_id: str):
    """Get status and results of a scan job."""
    job = await scan_service.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan job not found"
        )
    
    return ScanStatusResponse(
        job_id=job.job_id,
        state=job.state,
        progress=ScanProgress(
            total=job.total_targets,
            scanned=job.scanned,
            alive=job.alive,
            authenticated=job.authenticated,
            unreachable=job.unreachable,
            auth_failed=job.auth_failed,
            driver_not_supported=job.driver_not_supported
        ),
        results=[
            {
                "ip": result.ip,
                "credential_id": result.credential_id,
                "device_type": result.device_type,
                "hostname": result.hostname,
                "platform": result.platform
            }
            for result in job.results
        ]
    )


@router.post("/{job_id}/onboard", response_model=OnboardResponse)
async def onboard_devices(job_id: str, request: OnboardRequest):
    """Onboard selected devices from scan results."""
    # Verify job exists
    job = await scan_service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan job not found"
        )
    
    # Validate devices against scan results
    result_ips = {result.ip for result in job.results}
    valid_devices = [device for device in request.devices if device.ip in result_ips]
    
    if not valid_devices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid devices selected for onboarding"
        )
    
    # Separate Cisco and Linux devices
    cisco_devices = [d for d in valid_devices if d.device_type == "cisco"]
    linux_devices = [d for d in valid_devices if d.device_type == "linux"]
    
    cisco_queued = 0
    linux_added = 0
    inventory_path = None
    job_ids = []
    
    # Handle Cisco device onboarding via Nautobot
    if cisco_devices:
        try:
            cisco_queued, cisco_job_ids = await _onboard_cisco_devices(cisco_devices)
            job_ids.extend(cisco_job_ids)
        except Exception as e:
            logger.error(f"Cisco onboarding failed: {e}")
            # Continue with Linux devices even if Cisco fails
    
    # Handle Linux device inventory creation
    if linux_devices:
        try:
            linux_added, inventory_path = await _create_linux_inventory(linux_devices, job_id)
        except Exception as e:
            logger.error(f"Linux inventory creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create Linux inventory: {str(e)}"
            )
    
    return OnboardResponse(
        accepted=len(valid_devices),
        cisco_queued=cisco_queued,
        linux_added=linux_added,
        inventory_path=inventory_path,
        job_ids=job_ids
    )


async def _onboard_cisco_devices(cisco_devices: List[OnboardDevice]) -> tuple[int, List[str]]:
    """Onboard Cisco devices via Nautobot API."""
    job_ids = []
    queued_count = 0
    
    for device in cisco_devices:
        try:
            # Prepare device data for Nautobot onboarding
            device_data = {
                "ip_address": device.ip,
                "hostname": device.hostname or device.ip,
                "platform": device.platform or "cisco_ios",
                "location": device.location,
                "namespace": device.namespace or "Global",
                "role": device.role or "network",
                "status": device.status or "Active",
                "interface_status": device.interface_status or "Active",
                "ip_status": device.ip_status or "Active"
            }
            
            # Call Nautobot onboarding API
            response = await nautobot_service.onboard_device(device_data)
            
            if response.get("job_id"):
                job_ids.append(response["job_id"])
                queued_count += 1
                logger.info(f"Cisco device {device.ip} queued for onboarding with job {response['job_id']}")
            else:
                logger.warning(f"Cisco device {device.ip} onboarding returned no job ID")
                
        except Exception as e:
            logger.error(f"Failed to onboard Cisco device {device.ip}: {e}")
            # Continue with other devices
    
    return queued_count, job_ids


async def _create_linux_inventory(linux_devices: List[OnboardDevice], job_id: str) -> tuple[int, str]:
    """Create inventory file for Linux devices using template."""
    # Create inventory directory if it doesn't exist
    inventory_dir = os.path.join("data", "inventory")
    os.makedirs(inventory_dir, exist_ok=True)
    
    # Create inventory file with job ID per spec
    inventory_path = os.path.join(inventory_dir, f"inventory_{job_id}.yaml")
    
    # Build all_devices dictionary for template rendering
    all_devices = {}
    for device in linux_devices:
        all_devices[device.ip] = {
            "credential_id": device.credential_id,
            "hostname": device.hostname or device.ip,
            "platform": device.platform or "linux",
            "location": device.location,
            "role": device.role or "server",
            "status": device.status or "Active"
        }
    
    # Try to get template from Settings Templates App
    rendered_content = ""
    try:
        template_name = template_manager.get_selected_template_name()
        if template_name:
            template_content = template_manager.get_template_content(template_name)
            
            # Render template with all_devices context
            env = Environment(loader=FileSystemLoader("."))
            template = env.from_string(template_content)
            rendered_content = template.render(all_devices=all_devices)
        else:
            # Fallback to JSON if no template selected
            rendered_content = json.dumps({"all_devices": all_devices}, indent=2)
            
    except Exception as e:
        logger.warning(f"Template rendering failed, using JSON fallback: {e}")
        rendered_content = json.dumps({"all_devices": all_devices}, indent=2)
    
    # Write inventory file
    with open(inventory_path, 'w', encoding='utf-8') as f:
        f.write(rendered_content)
    
    logger.info(f"Created Linux inventory file: {inventory_path} with {len(linux_devices)} devices")
    
    return len(linux_devices), inventory_path


@router.delete("/{job_id}")
async def delete_scan_job(job_id: str):
    """Delete a scan job (cleanup endpoint)."""
    job = await scan_service.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan job not found"
        )
    
    # Remove job from service
    scan_service._jobs.pop(job_id, None)
    
    return {"message": f"Scan job {job_id} deleted successfully"}


@router.get("/jobs")
async def list_scan_jobs():
    """List all active scan jobs."""
    scan_service._purge_expired()
    
    jobs = []
    for job in scan_service._jobs.values():
        jobs.append({
            "job_id": job.job_id,
            "state": job.state,
            "created": job.created,
            "total_targets": job.total_targets,
            "authenticated": job.authenticated
        })
    
    return {"jobs": jobs}
