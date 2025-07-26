#!/usr/bin/env python3
"""
Test script for new Git Repository Management API endpoints
"""
import requests
import json

# First login to get a token
def login():
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    
    response = requests.post("http://localhost:8000/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Login failed: {response.text}")
        return None

# Test Git repository status endpoint
def test_git_repo_status(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get("http://localhost:8000/api/git/repo/status", headers=headers)
    print(f"Git Repository Status Response ({response.status_code}):")
    print(json.dumps(response.json(), indent=2))
    return response.json()

# Test Git repository sync endpoint
def test_git_repo_sync(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post("http://localhost:8000/api/git/repo/sync", headers=headers)
    print(f"Git Repository Sync Response ({response.status_code}):")
    print(json.dumps(response.json(), indent=2))
    return response.json()

if __name__ == "__main__":
    print("Testing Git Repository Management API endpoints...")
    
    # Login first
    token = login()
    if not token:
        print("Failed to get authentication token")
        exit(1)
    
    print(f"Got token: {token[:50]}...")
    
    # Test Git repository status
    print("\n=== Testing Repository Status ===")
    status_result = test_git_repo_status(token)
    
    # Test Git repository sync
    print("\n=== Testing Repository Sync ===")
    sync_result = test_git_repo_sync(token)
    
    print("\nTest completed!")
