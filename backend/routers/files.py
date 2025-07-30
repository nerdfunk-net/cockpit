"""
File management router for configuration comparison and file operations.
"""

from __future__ import annotations
import difflib
import logging
import os
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from core.auth import verify_token
from models.files import FileCompareRequest, FileExportRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/files", tags=["files"])


def get_sample_config_content(filename: str) -> str:
    """Generate sample configuration content for demo purposes."""
    base_config = """!
! Configuration file for network device
!
version 15.1
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname NetworkDevice
!
boot-start-marker
boot-end-marker
!
enable secret 5 $1$XXXX$XXXXXXXXXXXXXXXXXXXXXXXXX
!
username admin privilege 15 secret 5 $1$XXXX$XXXXXXXXXXXXXXXXXXXXXXXXX
!
interface GigabitEthernet0/0
 description Connection to Core Switch
 ip address 192.168.1.1 255.255.255.0
 duplex auto
 speed auto
!
interface GigabitEthernet0/1
 description Management Interface
 ip address 10.0.1.10 255.255.255.0
 duplex auto
 speed auto
!
router ospf 1
 router-id 1.1.1.1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.1.0 0.0.0.255 area 0
!
ip route 0.0.0.0 0.0.0.0 192.168.1.254
!
access-list 10 permit 10.0.1.0 0.0.0.255
access-list 10 permit 192.168.1.0 0.0.0.255
!
snmp-server community public RO
snmp-server location "Network Closet A"
snmp-server contact "admin@company.com"
!
line con 0
 login local
line vty 0 4
 access-class 10 in
 login local
 transport input ssh
!
end"""
    
    # Modify content based on filename to create differences
    if "v2" in filename or "new" in filename:
        modified_config = base_config.replace(
            "ip address 192.168.1.1 255.255.255.0",
            "ip address 192.168.1.2 255.255.255.0"
        ).replace(
            "router-id 1.1.1.1",
            "router-id 1.1.1.2"
        ).replace(
            "snmp-server location \"Network Closet A\"",
            "snmp-server location \"Network Closet B\""
        )
        # Add a new interface in v2
        modified_config += "\n!\ninterface GigabitEthernet0/2\n description Additional Port\n shutdown\n!"
        return modified_config
    elif "switch" in filename:
        return base_config.replace("NetworkDevice", "CoreSwitch").replace(
            "hostname NetworkDevice",
            "hostname CoreSwitch"
        ).replace(
            "router ospf 1",
            "!\n! Switch configuration - no OSPF"
        ).replace(
            " router-id 1.1.1.1\n network 192.168.1.0 0.0.0.255 area 0\n network 10.0.1.0 0.0.0.255 area 0",
            ""
        )
    elif "baseline" in filename:
        return base_config.replace(
            "snmp-server community public RO",
            "! SNMP disabled for security"
        ).replace(
            "snmp-server location \"Network Closet A\"\nsnmp-server contact \"admin@company.com\"",
            ""
        )
    
    return base_config


def create_sample_files(config_dir: Path):
    """Create sample configuration files for demo purposes."""
    sample_files = {
        "router-config-v1.txt": get_sample_config_content("router-config-v1.txt"),
        "router-config-v2.txt": get_sample_config_content("router-config-v2.txt"),
        "switch-config-old.txt": get_sample_config_content("switch-config-old.txt"),
        "switch-config-new.txt": get_sample_config_content("switch-config-new.txt"),
        "baseline-config.txt": get_sample_config_content("baseline-config.txt")
    }
    
    for filename, content in sample_files.items():
        file_path = config_dir / filename
        file_path.write_text(content, encoding='utf-8')


@router.get("/list")
async def list_files(current_user: str = Depends(verify_token)):
    """List all configuration files."""
    try:
        # Use GitManager to get the correct repository path
        from git_manager import GitManager
        git_manager = GitManager()
        config_dir = Path(git_manager.base_path)
        
        # Check if directory exists
        if not config_dir.exists():
            return {"files": []}
        
        files = []
        # Use common config file extensions
        allowed_extensions = ['.txt', '.conf', '.cfg', '.config', '.ini', '.yml', '.yaml', '.json']
        
        for file_path in config_dir.rglob('*'):
            if file_path.is_file() and any(file_path.name.endswith(ext) for ext in allowed_extensions):
                # Skip .git directory
                if '.git' in file_path.parts:
                    continue
                    
                relative_path = file_path.relative_to(config_dir)
                files.append({
                    "name": file_path.name,
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        
        return {"files": sorted(files, key=lambda x: x["name"])}
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@router.post("/compare")
async def compare_files(
    request: FileCompareRequest,
    current_user: str = Depends(verify_token)
):
    """Compare two configuration files."""
    try:
        # Use GitManager to get the correct repository path
        from git_manager import GitManager
        git_manager = GitManager()
        config_dir = Path(git_manager.base_path)
        
        left_file_path = config_dir / request.left_file
        right_file_path = config_dir / request.right_file
        
        # Check if files exist
        if not left_file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Left file not found: {request.left_file}"
            )
        
        if not right_file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Right file not found: {request.right_file}"
            )
        
        # Read file contents
        left_content = left_file_path.read_text(encoding='utf-8')
        right_content = right_file_path.read_text(encoding='utf-8')
        
        # Generate unified diff
        left_lines = left_content.splitlines(keepends=True)
        right_lines = right_content.splitlines(keepends=True)
        
        diff_lines = list(difflib.unified_diff(
            left_lines,
            right_lines,
            fromfile=request.left_file,
            tofile=request.right_file,
            n=3
        ))
        
        # Calculate statistics
        additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        # Prepare side-by-side comparison
        left_file_lines = []
        right_file_lines = []
        
        lines1_list = left_content.splitlines()
        lines2_list = right_content.splitlines()
        
        # Use difflib.SequenceMatcher to get line-by-line comparison
        matcher = difflib.SequenceMatcher(None, lines1_list, lines2_list)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for i in range(i1, i2):
                    left_file_lines.append({"line_number": i + 1, "content": lines1_list[i], "type": "equal"})
                for j in range(j1, j2):
                    right_file_lines.append({"line_number": j + 1, "content": lines2_list[j], "type": "equal"})
            elif tag == 'delete':
                for i in range(i1, i2):
                    left_file_lines.append({"line_number": i + 1, "content": lines1_list[i], "type": "delete"})
            elif tag == 'insert':
                for j in range(j1, j2):
                    right_file_lines.append({"line_number": j + 1, "content": lines2_list[j], "type": "insert"})
            elif tag == 'replace':
                for i in range(i1, i2):
                    left_file_lines.append({"line_number": i + 1, "content": lines1_list[i], "type": "replace"})
                for j in range(j1, j2):
                    right_file_lines.append({"line_number": j + 1, "content": lines2_list[j], "type": "replace"})
        
        return {
            "left_file": request.left_file,
            "right_file": request.right_file,
            "diff_lines": [line.rstrip('\n') for line in diff_lines],
            "left_lines": left_file_lines,
            "right_lines": right_file_lines,
            "stats": {
                "additions": additions,
                "deletions": deletions,
                "changes": additions + deletions,
                "total_lines": len(diff_lines)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare files: {str(e)}"
        )


@router.post("/export-diff")
async def export_diff(
    request: FileExportRequest,
    current_user: str = Depends(verify_token)
):
    """Export diff in unified format."""
    try:
        # Use GitManager to get the correct repository path
        from git_manager import GitManager
        git_manager = GitManager()
        config_dir = Path(git_manager.base_path)
        
        left_file_path = config_dir / request.left_file
        right_file_path = config_dir / request.right_file
        
        # Check if files exist
        if not left_file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Left file not found: {request.left_file}"
            )
        
        if not right_file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Right file not found: {request.right_file}"
            )
        
        # Read file contents
        left_content = left_file_path.read_text(encoding='utf-8')
        right_content = right_file_path.read_text(encoding='utf-8')
        
        # Generate unified diff
        left_lines = left_content.splitlines(keepends=True)
        right_lines = right_content.splitlines(keepends=True)
        
        diff_content = ''.join(difflib.unified_diff(
            left_lines,
            right_lines,
            fromfile=request.left_file,
            tofile=request.right_file,
            n=3
        ))
        
        # Return as downloadable file
        filename = f"diff_{request.left_file.replace('/', '_')}_vs_{request.right_file.replace('/', '_')}.diff"
        
        return Response(
            content=diff_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting diff: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export diff: {str(e)}"
        )


@router.get("/config")
async def get_file_config(current_user: str = Depends(verify_token)):
    """Get file storage configuration information."""
    try:
        # Use GitManager to get the correct repository path
        from git_manager import GitManager
        git_manager = GitManager()
        config_dir = Path(git_manager.base_path)
        
        return {
            "directory": str(config_dir.absolute()),
            "directory_exists": config_dir.exists(),
            "allowed_extensions": ['.txt', '.conf', '.cfg', '.config', '.ini', '.yml', '.yaml', '.json'],
            "max_file_size_mb": 10,
            "directory_writable": config_dir.exists() and os.access(config_dir, os.W_OK)
        }
    except Exception as e:
        logger.error(f"Error getting file config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file configuration: {str(e)}"
        )
