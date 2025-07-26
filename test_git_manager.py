#!/usr/bin/env python3
"""
Test script for Git Manager functionality
"""
import sys
import os
sys.path.append('/Users/mp/programming/cockpit/backend')

from git_manager import git_manager
from settings_manager import settings_manager

def test_git_manager():
    print("Testing Git Manager...")
    
    # Check current settings
    git_settings = settings_manager.get_git_settings()
    print(f"Git Settings: {git_settings}")
    
    # Check repository status
    try:
        status = git_manager.get_repository_status()
        print(f"Repository Status: {status}")
    except Exception as e:
        print(f"Error getting repository status: {e}")
    
    # Check if repository exists
    print(f"Repository exists: {git_manager.is_git_repository()}")
    print(f"Base path: {git_manager.base_path}")
    print(f"Directory exists: {os.path.exists(git_manager.base_path)}")
    
    if os.path.exists(git_manager.base_path):
        print(f"Directory contents: {os.listdir(git_manager.base_path)}")

if __name__ == "__main__":
    test_git_manager()
