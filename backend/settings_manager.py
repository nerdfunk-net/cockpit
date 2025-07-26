"""
Settings Database Management for Cockpit
Handles SQLite database operations for application settings
"""

import sqlite3
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

@dataclass
class NautobotSettings:
    """Nautobot connection settings"""
    url: str = "http://localhost:8080"  # More common Nautobot port
    token: str = ""  # Must be configured by user
    timeout: int = 30
    verify_ssl: bool = True

@dataclass 
class GitSettings:
    """Git repository settings for configs"""
    repo_url: str = ""
    branch: str = "main"
    username: str = ""
    token: str = ""
    config_path: str = "configs/"
    sync_interval: int = 15

class SettingsManager:
    """Manages application settings in SQLite database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Create settings directory if it doesn't exist
            settings_dir = os.path.join(os.path.dirname(__file__), 'settings')
            os.makedirs(settings_dir, exist_ok=True)
            self.db_path = os.path.join(settings_dir, 'cockpit_settings.db')
        else:
            self.db_path = db_path
            
        self.default_nautobot = NautobotSettings()
        self.default_git = GitSettings()
        
        # Initialize database
        self.init_database()
    
    def init_database(self) -> bool:
        """Initialize the settings database with default values"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create nautobot_settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS nautobot_settings (
                        id INTEGER PRIMARY KEY,
                        url TEXT NOT NULL,
                        token TEXT NOT NULL,
                        timeout INTEGER NOT NULL DEFAULT 30,
                        verify_ssl BOOLEAN NOT NULL DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create git_settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS git_settings (
                        id INTEGER PRIMARY KEY,
                        repo_url TEXT NOT NULL,
                        branch TEXT NOT NULL DEFAULT 'main',
                        username TEXT,
                        token TEXT,
                        config_path TEXT NOT NULL DEFAULT 'configs/',
                        sync_interval INTEGER NOT NULL DEFAULT 15,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create settings_metadata table for versioning and status
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Check if we need to insert default values
                cursor.execute('SELECT COUNT(*) FROM nautobot_settings')
                if cursor.fetchone()[0] == 0:
                    logger.info("Inserting default Nautobot settings")
                    self._insert_default_nautobot_settings(cursor)
                
                cursor.execute('SELECT COUNT(*) FROM git_settings')  
                if cursor.fetchone()[0] == 0:
                    logger.info("Inserting default Git settings")
                    self._insert_default_git_settings(cursor)
                
                # Set database version
                cursor.execute('''
                    INSERT OR REPLACE INTO settings_metadata (key, value)
                    VALUES ('db_version', '1.0')
                ''')
                
                conn.commit()
                logger.info(f"Settings database initialized at {self.db_path}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def _insert_default_nautobot_settings(self, cursor):
        """Insert default Nautobot settings"""
        cursor.execute('''
            INSERT INTO nautobot_settings (url, token, timeout, verify_ssl)
            VALUES (?, ?, ?, ?)
        ''', (
            self.default_nautobot.url,
            self.default_nautobot.token,
            self.default_nautobot.timeout,
            self.default_nautobot.verify_ssl
        ))
    
    def _insert_default_git_settings(self, cursor):
        """Insert default Git settings"""
        cursor.execute('''
            INSERT INTO git_settings (repo_url, branch, username, token, config_path, sync_interval)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            self.default_git.repo_url,
            self.default_git.branch,
            self.default_git.username,
            self.default_git.token,
            self.default_git.config_path,
            self.default_git.sync_interval
        ))
    
    def get_nautobot_settings(self) -> Optional[Dict[str, Any]]:
        """Get current Nautobot settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM nautobot_settings ORDER BY id DESC LIMIT 1')
                row = cursor.fetchone()
                
                if row:
                    return {
                        'url': row['url'],
                        'token': row['token'],
                        'timeout': row['timeout'],
                        'verify_ssl': bool(row['verify_ssl'])
                    }
                else:
                    # Fallback to defaults
                    return asdict(self.default_nautobot)
                    
        except sqlite3.Error as e:
            logger.error(f"Error getting Nautobot settings: {e}")
            # Auto-recover by recreating database
            self._handle_database_corruption()
            return asdict(self.default_nautobot)
    
    def get_git_settings(self) -> Optional[Dict[str, Any]]:
        """Get current Git settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM git_settings ORDER BY id DESC LIMIT 1')
                row = cursor.fetchone()
                
                if row:
                    return {
                        'repo_url': row['repo_url'],
                        'branch': row['branch'],
                        'username': row['username'] or '',
                        'token': row['token'] or '',
                        'config_path': row['config_path'],
                        'sync_interval': row['sync_interval']
                    }
                else:
                    # Fallback to defaults
                    return asdict(self.default_git)
                    
        except sqlite3.Error as e:
            logger.error(f"Error getting Git settings: {e}")
            # Auto-recover by recreating database
            self._handle_database_corruption()
            return asdict(self.default_git)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings combined"""
        return {
            'nautobot': self.get_nautobot_settings(),
            'git': self.get_git_settings(),
            'metadata': self._get_metadata()
        }
    
    def update_nautobot_settings(self, settings: Dict[str, Any]) -> bool:
        """Update Nautobot settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO nautobot_settings (url, token, timeout, verify_ssl)
                    VALUES (?, ?, ?, ?)
                ''', (
                    settings.get('url', self.default_nautobot.url),
                    settings.get('token', self.default_nautobot.token),
                    settings.get('timeout', self.default_nautobot.timeout),
                    settings.get('verify_ssl', self.default_nautobot.verify_ssl)
                ))
                
                conn.commit()
                logger.info("Nautobot settings updated successfully")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error updating Nautobot settings: {e}")
            return False
    
    def update_git_settings(self, settings: Dict[str, Any]) -> bool:
        """Update Git settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO git_settings (repo_url, branch, username, token, config_path, sync_interval)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    settings.get('repo_url', self.default_git.repo_url),
                    settings.get('branch', self.default_git.branch),
                    settings.get('username', self.default_git.username),
                    settings.get('token', self.default_git.token),
                    settings.get('config_path', self.default_git.config_path),
                    settings.get('sync_interval', self.default_git.sync_interval)
                ))
                
                conn.commit()
                logger.info("Git settings updated successfully")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error updating Git settings: {e}")
            return False
    
    def update_all_settings(self, settings: Dict[str, Any]) -> bool:
        """Update all settings"""
        success = True
        
        if 'nautobot' in settings:
            success &= self.update_nautobot_settings(settings['nautobot'])
        
        if 'git' in settings:
            success &= self.update_git_settings(settings['git'])
        
        return success
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get database metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT key, value FROM settings_metadata')
                rows = cursor.fetchall()
                
                metadata = {}
                for row in rows:
                    metadata[row['key']] = row['value']
                
                metadata['database_path'] = self.db_path
                metadata['database_exists'] = os.path.exists(self.db_path)
                
                return metadata
                
        except sqlite3.Error as e:
            logger.error(f"Error getting metadata: {e}")
            return {'error': str(e)}
    
    def _handle_database_corruption(self) -> Dict[str, str]:
        """Handle database corruption by recreating with defaults"""
        logger.warning("Database corruption detected, recreating with defaults")
        
        try:
            # Remove corrupted database
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            
            # Recreate database
            success = self.init_database()
            
            if success:
                message = "Database was corrupted and has been recreated with default settings. Please reconfigure your settings."
                logger.info(message)
                return {
                    'status': 'recovered',
                    'message': message
                }
            else:
                raise Exception("Failed to recreate database")
                
        except Exception as e:
            error_msg = f"Failed to recover from database corruption: {e}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg
            }
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clear existing settings
                cursor.execute('DELETE FROM nautobot_settings')
                cursor.execute('DELETE FROM git_settings')
                
                # Insert defaults
                self._insert_default_nautobot_settings(cursor)
                self._insert_default_git_settings(cursor)
                
                conn.commit()
                logger.info("Settings reset to defaults")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error resetting settings: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Test basic operations
                cursor.execute('SELECT COUNT(*) FROM nautobot_settings')
                nautobot_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM git_settings')
                git_count = cursor.fetchone()[0]
                
                return {
                    'status': 'healthy',
                    'database_path': self.db_path,
                    'nautobot_settings_count': nautobot_count,
                    'git_settings_count': git_count,
                    'database_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'recovery_needed': True
            }

# Global settings manager instance
settings_manager = SettingsManager()
