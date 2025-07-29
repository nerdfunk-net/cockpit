"""
Git Repository Management for Cockpit
Handles Git operations for configuration synchronization
"""

import os
import shutil
import logging
import subprocess
import time
from typing import Dict, Any, Tuple, Optional
from urllib.parse import urlparse
from settings_manager import settings_manager

logger = logging.getLogger(__name__)

class GitManager:
    """Manages Git repository operations for configuration files"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Use ./data/git/configs relative to the project root
            # Go up one directory from backend/ to get to project root
            project_root = os.path.dirname(os.path.dirname(__file__))
            self.base_path = os.path.join(project_root, 'data', 'git', 'configs')
        else:
            self.base_path = base_path
        
        # Ensure base directory exists
        os.makedirs(self.base_path, exist_ok=True)
        
    def _configure_git_ssl(self) -> Dict[str, str]:
        """Configure Git SSL settings and return environment variables"""
        from config_manual import settings as env_settings
        
        env = os.environ.copy()
        
        # Get Git settings from database (preferred) or fall back to environment
        git_settings = settings_manager.get_git_settings()
        if git_settings:
            ssl_verify = git_settings.get('verify_ssl', True)
        else:
            ssl_verify = env_settings.git_ssl_verify
        
        # Configure SSL verification
        if not ssl_verify:
            env['GIT_SSL_NO_VERIFY'] = '1'
            logger.warning("Git SSL verification disabled - not recommended for production")
        
        # Configure custom CA certificate (still from environment as these are file paths)
        if env_settings.git_ssl_ca_info and os.path.exists(env_settings.git_ssl_ca_info):
            env['GIT_SSL_CAINFO'] = env_settings.git_ssl_ca_info
            logger.info(f"Using custom CA certificate: {env_settings.git_ssl_ca_info}")
        
        # Configure client certificate (still from environment as these are file paths)
        if env_settings.git_ssl_cert and os.path.exists(env_settings.git_ssl_cert):
            env['GIT_SSL_CERT'] = env_settings.git_ssl_cert
            logger.info(f"Using client certificate: {env_settings.git_ssl_cert}")
        
        return env
        
    def is_git_repository(self) -> bool:
        """Check if the configs directory is a valid Git repository"""
        try:
            git_dir = os.path.join(self.base_path, '.git')
            return os.path.exists(git_dir) and os.path.isdir(git_dir)
        except Exception as e:
            logger.error(f"Error checking Git repository: {e}")
            return False
    
    def is_directory_empty(self) -> bool:
        """Check if the configs directory is empty (excluding hidden files)"""
        try:
            items = [item for item in os.listdir(self.base_path) if not item.startswith('.')]
            return len(items) == 0
        except Exception as e:
            logger.error(f"Error checking directory contents: {e}")
            return True
    
    def get_git_settings(self) -> Optional[Dict[str, Any]]:
        """Get Git settings from the database"""
        try:
            return settings_manager.get_git_settings()
        except Exception as e:
            logger.error(f"Error getting Git settings: {e}")
            return None
    
    def clone_repository(self) -> Tuple[bool, str]:
        """Clone the Git repository using settings from database"""
        try:
            git_settings = self.get_git_settings()
            if not git_settings:
                return False, "Git settings not found in database. Please configure Git settings first."
            
            repo_url = git_settings.get('repo_url', '').strip()
            branch = git_settings.get('branch', 'main').strip()
            username = git_settings.get('username', '').strip()
            token = git_settings.get('token', '').strip()
            
            if not repo_url:
                return False, "Git repository URL not configured. Please set up Git settings."
            
            # If directory exists and is not empty, back it up first
            if os.path.exists(self.base_path) and not self.is_directory_empty():
                backup_path = f"{self.base_path}_backup_{int(time.time())}"
                shutil.move(self.base_path, backup_path)
                logger.info(f"Backed up existing directory to {backup_path}")
            
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(self.base_path), exist_ok=True)
            
            # Prepare repository URL with authentication if provided
            clone_url = repo_url
            if username and token:
                parsed = urlparse(repo_url)
                if parsed.scheme in ['http', 'https']:
                    clone_url = f"{parsed.scheme}://{username}:{token}@{parsed.netloc}{parsed.path}"
            
            # Clone the repository with SSL configuration
            env = self._configure_git_ssl()
            cmd = ['git', 'clone', '--branch', branch, clone_url, self.base_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
            
            if result.returncode == 0:
                logger.info(f"Successfully cloned repository to {self.base_path}")
                return True, f"Repository cloned successfully from {repo_url} (branch: {branch})"
            else:
                error_msg = result.stderr.strip()
                logger.error(f"Git clone failed: {error_msg}")
                
                # Provide user-friendly error messages
                if 'authentication failed' in error_msg.lower():
                    return False, "Authentication failed. Please check your Git username and token in settings."
                elif 'not found' in error_msg.lower() or 'repository not found' in error_msg.lower():
                    return False, f"Repository not found: {repo_url}. Please verify the URL in settings."
                elif 'branch' in error_msg.lower() and 'not found' in error_msg.lower():
                    return False, f"Branch '{branch}' not found. Please check the branch name in settings."
                else:
                    return False, f"Git clone failed: {error_msg}"
        
        except subprocess.TimeoutExpired:
            return False, "Git clone operation timed out. Please check your network connection."
        except FileNotFoundError:
            return False, "Git command not found. Please ensure Git is installed on the server."
        except Exception as e:
            logger.error(f"Unexpected error during Git clone: {e}")
            return False, f"Unexpected error: {str(e)}"
    
    def pull_latest_changes(self) -> Tuple[bool, str]:
        """Pull latest changes from the remote repository"""
        try:
            if not self.is_git_repository():
                return False, "Directory is not a Git repository. Please sync repository first."
            
            # Change to repository directory
            original_cwd = os.getcwd()
            os.chdir(self.base_path)
            
            try:
                # Check if there are any remotes configured
                remote_check = subprocess.run(['git', 'remote'], capture_output=True, text=True)
                if not remote_check.stdout.strip():
                    return False, "No Git remote configured. Please configure a Git repository first."
                
                # Check if current branch has upstream tracking
                upstream_check = subprocess.run(['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'], 
                                              capture_output=True, text=True)
                
                if upstream_check.returncode != 0:
                    # No upstream tracking, try to set it up
                    # First, get the current branch name
                    branch_result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
                    if branch_result.returncode == 0:
                        current_branch = branch_result.stdout.strip()
                        if current_branch:
                            # Try to set upstream to origin/current_branch
                            upstream_result = subprocess.run(['git', 'branch', '--set-upstream-to=origin/' + current_branch], 
                                                           capture_output=True, text=True)
                            if upstream_result.returncode != 0:
                                return False, f"No upstream tracking configured and unable to set it automatically. Please configure Git repository settings."
                
                # Pull latest changes with SSL configuration
                env = self._configure_git_ssl()
                result = subprocess.run(['git', 'pull'], capture_output=True, text=True, timeout=30, env=env)
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    if 'Already up to date' in output:
                        return True, "Repository is already up to date."
                    else:
                        return True, f"Successfully pulled latest changes: {output}"
                else:
                    error_msg = result.stderr.strip()
                    logger.error(f"Git pull failed: {error_msg}")
                    return False, f"Failed to pull changes: {error_msg}"
            
            finally:
                os.chdir(original_cwd)
        
        except subprocess.TimeoutExpired:
            return False, "Git pull operation timed out."
        except Exception as e:
            logger.error(f"Error during Git pull: {e}")
            return False, f"Error pulling changes: {str(e)}"
    
    def get_repository_status(self) -> Dict[str, Any]:
        """Get detailed status of the Git repository"""
        status = {
            'is_git_repo': False,
            'is_empty': True,
            'has_configs': False,
            'remote_url': None,
            'current_branch': None,
            'last_commit': None,
            'config_files': []
        }
        
        try:
            status['is_git_repo'] = self.is_git_repository()
            status['is_empty'] = self.is_directory_empty()
            
            # Count configuration files
            if os.path.exists(self.base_path):
                config_files = []
                for root, dirs, files in os.walk(self.base_path):
                    # Skip .git directory
                    if '.git' in dirs:
                        dirs.remove('.git')
                    
                    for file in files:
                        if file.endswith(('.cfg', '.conf', '.config', '.txt', '.yml', '.yaml', '.json')):
                            rel_path = os.path.relpath(os.path.join(root, file), self.base_path)
                            config_files.append(rel_path)
                
                status['config_files'] = config_files
                status['has_configs'] = len(config_files) > 0
            
            # Get Git repository information if it's a valid repo
            if status['is_git_repo']:
                original_cwd = os.getcwd()
                os.chdir(self.base_path)
                
                try:
                    # Get remote URL
                    result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        status['remote_url'] = result.stdout.strip()
                    
                    # Get current branch
                    result = subprocess.run(['git', 'branch', '--show-current'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        status['current_branch'] = result.stdout.strip()
                    
                    # Get last commit info
                    result = subprocess.run(['git', 'log', '-1', '--pretty=format:%h - %s (%an, %ar)'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        status['last_commit'] = result.stdout.strip()
                
                finally:
                    os.chdir(original_cwd)
        
        except Exception as e:
            logger.error(f"Error getting repository status: {e}")
        
        return status
    
    def validate_repository_configuration(self) -> Dict[str, Any]:
        """
        Validate if the current repository matches the configured settings
        Returns validation status and recommendations
        """
        validation = {
            'is_valid': True,
            'needs_reconfiguration': False,
            'issues': [],
            'current_repo': None,
            'configured_repo': None,
            'current_branch': None,
            'configured_branch': None,
            'action_required': None
        }
        
        try:
            # Get current Git settings
            git_settings = self.get_git_settings()
            if not git_settings:
                validation['is_valid'] = False
                validation['issues'].append("Git settings not configured")
                validation['action_required'] = "configure_settings"
                return validation
            
            configured_repo = git_settings.get('repo_url', '').strip()
            configured_branch = git_settings.get('branch', 'main').strip()
            
            validation['configured_repo'] = configured_repo
            validation['configured_branch'] = configured_branch
            
            if not configured_repo:
                validation['is_valid'] = False
                validation['issues'].append("Repository URL not configured in settings")
                validation['action_required'] = "configure_settings"
                return validation
            
            # Check if directory exists and is a Git repository
            if not self.is_git_repository():
                if self.is_directory_empty():
                    validation['needs_reconfiguration'] = True
                    validation['issues'].append("No repository found, needs initial clone")
                    validation['action_required'] = "clone_repository"
                else:
                    validation['is_valid'] = False
                    validation['needs_reconfiguration'] = True
                    validation['issues'].append("Directory contains files but is not a Git repository")
                    validation['action_required'] = "clear_and_clone"
                return validation
            
            # Get current repository information
            original_cwd = os.getcwd()
            os.chdir(self.base_path)
            
            try:
                # Get current remote URL
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    current_repo = result.stdout.strip()
                    validation['current_repo'] = current_repo
                    
                    # Normalize URLs for comparison (remove credentials)
                    def normalize_url(url):
                        try:
                            parsed = urlparse(url)
                            # Remove credentials from netloc if present
                            netloc = parsed.netloc
                            if '@' in netloc:
                                netloc = netloc.split('@')[-1]  # Take part after @
                            return f"{parsed.scheme}://{netloc}{parsed.path}"
                        except:
                            return url
                    
                    normalized_current = normalize_url(current_repo)
                    normalized_configured = normalize_url(configured_repo)
                    
                    if normalized_current != normalized_configured:
                        validation['is_valid'] = False
                        validation['needs_reconfiguration'] = True
                        validation['issues'].append(f"Repository URL mismatch: current='{current_repo}', configured='{configured_repo}'")
                        validation['action_required'] = "reconfigure_repository"
                else:
                    validation['is_valid'] = False
                    validation['issues'].append("Could not determine current repository URL")
                    validation['action_required'] = "reconfigure_repository"
                
                # Get current branch
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    current_branch = result.stdout.strip()
                    validation['current_branch'] = current_branch
                    
                    if current_branch != configured_branch:
                        validation['is_valid'] = False
                        validation['needs_reconfiguration'] = True
                        validation['issues'].append(f"Branch mismatch: current='{current_branch}', configured='{configured_branch}'")
                        if validation['action_required'] != "reconfigure_repository":
                            validation['action_required'] = "switch_branch"
                else:
                    validation['issues'].append("Could not determine current branch")
            
            finally:
                os.chdir(original_cwd)
        
        except Exception as e:
            logger.error(f"Error validating repository configuration: {e}")
            validation['is_valid'] = False
            validation['issues'].append(f"Validation error: {str(e)}")
            validation['action_required'] = "manual_check"
        
        return validation
    
    def clear_and_reconfigure_repository(self) -> Tuple[bool, str]:
        """
        Clear the current repository directory and clone the configured repository
        """
        try:
            # Backup existing content if any
            if os.path.exists(self.base_path) and not self.is_directory_empty():
                backup_path = f"{self.base_path}_backup_{int(time.time())}"
                shutil.move(self.base_path, backup_path)
                logger.info(f"Backed up existing content to {backup_path}")
            
            # Remove the directory completely
            if os.path.exists(self.base_path):
                shutil.rmtree(self.base_path)
            
            # Recreate the directory
            os.makedirs(self.base_path, exist_ok=True)
            
            # Clone the configured repository
            success, message = self.clone_repository()
            
            if success:
                return True, f"Repository successfully reconfigured. {message}"
            else:
                return False, f"Failed to reconfigure repository: {message}"
        
        except Exception as e:
            logger.error(f"Error clearing and reconfiguring repository: {e}")
            return False, f"Failed to clear and reconfigure: {str(e)}"
    
    def sync_repository(self) -> Tuple[bool, str]:
        """Sync repository - clone if not exists, pull if exists"""
        try:
            if not self.is_git_repository():
                if self.is_directory_empty():
                    return self.clone_repository()
                else:
                    return False, "Directory contains files but is not a Git repository. Please clear the directory or configure Git manually."
            else:
                return self.pull_latest_changes()
        
        except Exception as e:
            logger.error(f"Error during repository sync: {e}")
            return False, f"Repository sync failed: {str(e)}"

# Global git manager instance
git_manager = GitManager()
