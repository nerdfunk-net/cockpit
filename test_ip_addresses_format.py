#!/usr/bin/env python3
"""
Test to verify that ip_addresses is sent as a string format to Nautobot
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

# Test the onboard endpoint with multiple IP addresses (comma-separated string)
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Sample onboard data with multiple IP addresses as a comma-separated string
onboard_data = {
    "ip_address": "192.168.178.1,192.168.178.2,192.168.178.3",  # Multiple IPs as string
    "location_id": "550e8400-e29b-41d4-a716-446655440000",
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
print(f"Expected: ip_addresses should be sent as string '{onboard_data['ip_address']}' to Nautobot")

response = requests.post(
    "http://localhost:8000/api/nautobot/devices/onboard",
    headers=headers,
    json=onboard_data
)

print(f"Response status: {response.status_code}")

# Look for our backend's log output that shows the job_data being sent
print("\nLook at the backend logs to see:")
print("logger.info(f'Job data: {job_data}')")
print("This should show 'ip_addresses': '192.168.178.1,192.168.178.2,192.168.178.3' (as string)")
print("Instead of 'ip_addresses': ['192.168.178.1', '192.168.178.2', '192.168.178.3'] (as array)")
