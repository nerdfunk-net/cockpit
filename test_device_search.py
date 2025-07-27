#!/usr/bin/env python3
"""
Test script to debug device search functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test authentication first
print("Testing authentication...")
auth_data = {
    "username": "admin",
    "password": "admin"
}

try:
    auth_response = requests.post(f"{BASE_URL}/auth/login", json=auth_data)
    print(f"Auth Status: {auth_response.status_code}")
    
    if auth_response.status_code == 200:
        auth_result = auth_response.json()
        token = auth_result.get("access_token")
        print(f"Token received: {token[:20]}...")
        
        # Test device search
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\nTesting device search with name filter...")
        search_response = requests.get(f"{BASE_URL}/api/nautobot/devices?filter_type=name&filter_value=lab", headers=headers)
        print(f"Search Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            response_data = search_response.json()
            devices = response_data.get('devices', [])
            count = response_data.get('count', 0)
            print(f"Found {count} devices matching 'lab' (case-insensitive)")
            if devices:
                for i, device in enumerate(devices):
                    if i >= 3:  # Show first 3
                        break
                    print(f"  - {device.get('display_name', device.get('name', 'N/A'))} ({device.get('primary_ip', 'No IP')})")
        else:
            print(f"Search failed: {search_response.text}")
            
        # Test without filter
        print("\nTesting device search without filter...")
        all_devices_response = requests.get(f"{BASE_URL}/api/nautobot/devices", headers=headers)
        print(f"All devices Status: {all_devices_response.status_code}")
        
        if all_devices_response.status_code == 200:
            response_data = all_devices_response.json()
            all_devices = response_data.get('devices', [])
            count = response_data.get('count', 0)
            print(f"Total devices available: {count}")
            if all_devices:
                print("Available device names:")
                for i, device in enumerate(all_devices):
                    if i >= 10:  # Show first 10
                        print("  ...")
                        break
                    name = device.get('display_name') or device.get('name', 'N/A')
                    ip = device.get('primary_ip', 'No IP')
                    print(f"  - {name} ({ip})")
            else:
                print("  (No devices found)")
        else:
            print(f"All devices failed: {all_devices_response.text}")
            
    else:
        print(f"Auth failed: {auth_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
