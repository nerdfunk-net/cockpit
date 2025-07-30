#!/usr/bin/env python3
"""
Test to verify that regular platform_id gets passed through normally
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

# Test the onboard endpoint with a regular platform_id
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Sample onboard data with regular platform_id
onboard_data = {
    "ip_address": "192.168.178.1",
    "location_id": "550e8400-e29b-41d4-a716-446655440000",
    "role_id": "550e8400-e29b-41d4-a716-446655440001", 
    "platform_id": "550e8400-e29b-41d4-a716-446655440002",  # Regular UUID
    "namespace_id": "550e8400-e29b-41d4-a716-446655440003",
    "status_id": "550e8400-e29b-41d4-a716-446655440004",
    "interface_status_id": "550e8400-e29b-41d4-a716-446655440005",
    "ip_address_status_id": "550e8400-e29b-41d4-a716-446655440006",
    "secret_groups_id": "550e8400-e29b-41d4-a716-446655440007",
    "port": 22,
    "timeout": 30
}

print(f"Testing onboard endpoint with regular platform: {json.dumps(onboard_data, indent=2)}")
print(f"Expected: platform should be sent as the UUID to Nautobot")

response = requests.post(
    "http://localhost:8000/api/nautobot/devices/onboard",
    headers=headers,
    json=onboard_data
)

print(f"Response status: {response.status_code}")

print("\nLook at the backend logs to see:")
print("logger.info(f'Job data: {job_data}')")
print("This should show 'platform': '550e8400-e29b-41d4-a716-446655440002' (regular UUID)")
