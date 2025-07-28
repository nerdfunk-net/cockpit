#!/usr/bin/env python3
"""
Test script to check the onboard device API endpoint
"""

import requests
import json

# First, get auth token
auth_response = requests.post("http://localhost:8000/auth/login", json={
    "username": "admin",
    "password": "admin"
})

if auth_response.status_code == 200:
    token = auth_response.json()["access_token"]
    print(f"Got auth token: {token[:20]}...")
else:
    print(f"Auth failed: {auth_response.status_code} - {auth_response.text}")
    exit(1)

# Test the onboard endpoint
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Sample onboard data with valid UUID format
onboard_data = {
    "ip_address": "192.168.1.100",
    "location_id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID format
    "role_id": "550e8400-e29b-41d4-a716-446655440001", 
    "platform_id": "550e8400-e29b-41d4-a716-446655440002",
    "namespace_id": "550e8400-e29b-41d4-a716-446655440003",
    "status_id": "550e8400-e29b-41d4-a716-446655440004",
    "interface_status_id": "550e8400-e29b-41d4-a716-446655440005",
    "ip_address_status_id": "550e8400-e29b-41d4-a716-446655440006",
    "secret_groups_id": "550e8400-e29b-41d4-a716-446655440007",
    "port": 22,
    "timeout": 30
}

print(f"Testing onboard endpoint with data: {json.dumps(onboard_data, indent=2)}")

response = requests.post(
    "http://localhost:8000/api/nautobot/devices/onboard",
    headers=headers,
    json=onboard_data
)

print(f"Response status: {response.status_code}")
print(f"Response headers: {dict(response.headers)}")
print(f"Response body: {response.text}")

if response.status_code == 200:
    try:
        data = response.json()
        print(f"Parsed JSON: {json.dumps(data, indent=2)}")
        if 'job_id' in data:
            print(f"JOB ID FOUND: {data['job_id']}")
        else:
            print("NO JOB ID FOUND IN RESPONSE")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
