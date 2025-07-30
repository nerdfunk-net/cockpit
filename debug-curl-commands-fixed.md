# SSL Verification Testing Commands

## Authentication Commands

### Get a token
```bash
curl -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])"
```

### Get a token (store in variable)
```bash
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
echo "Token: $TOKEN"
```

### Test token validity
```bash
curl -X GET "http://localhost:8000/auth/verify" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Logout
```bash
curl -X POST "http://localhost:8000/auth/logout" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

## Settings Commands

### Get current settings
```bash
curl -X GET "http://localhost:8000/api/settings" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" 2>/dev/null | python3 -m json.tool
```

### GIT settings - Set SSL verification to TRUE
```bash
curl -X POST "http://localhost:8000/api/settings/git" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "repo_url": "https://github.com/nerdfunk-net/test-repo.git",
  "branch": "main", 
  "username": "nerdfunk-net",
  "token": "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",
  "config_path": "configs/",
  "sync_interval": 15,
  "verify_ssl": true
}' 2>/dev/null | python3 -m json.tool
```

### GIT settings - Set SSL verification to FALSE
```bash
curl -X POST "http://localhost:8000/api/settings/git" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "repo_url": "https://github.com/nerdfunk-net/test-repo.git",
  "branch": "main", 
  "username": "nerdfunk-net",
  "token": "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",
  "config_path": "configs/",
  "sync_interval": 15,
  "verify_ssl": false
}' 2>/dev/null | python3 -m json.tool
```

### Nautobot settings
```bash
curl -X POST "http://localhost:8000/api/settings/nautobot" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "url": "https://your-nautobot.com",
  "token": "your-nautobot-token-here",
  "timeout": 30,
  "verify_ssl": true
}' 2>/dev/null | python3 -m json.tool
```

## Status & Health Check Commands

### Test Nautobot connection
```bash
curl -X GET "http://localhost:8000/api/nautobot/test" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get Nautobot statistics
```bash
curl -X GET "http://localhost:8000/api/nautobot/stats" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Backend health check
```bash
curl -X GET "http://localhost:8000/health" 2>/dev/null | python3 -m json.tool
```

## Device Onboarding Commands

### Check IP availability
```bash
curl -X POST "http://localhost:8000/api/nautobot/check-ip" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "ip_address": "192.168.178.1"
}' 2>/dev/null | python3 -m json.tool
```

### Get locations
```bash
curl -X GET "http://localhost:8000/api/nautobot/locations" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get namespaces
```bash
curl -X GET "http://localhost:8000/api/nautobot/namespaces" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get device roles
```bash
curl -X GET "http://localhost:8000/api/nautobot/roles" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get platforms
```bash
curl -X GET "http://localhost:8000/api/nautobot/platforms" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get device statuses
```bash
curl -X GET "http://localhost:8000/api/nautobot/statuses/device" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get interface statuses
```bash
curl -X GET "http://localhost:8000/api/nautobot/statuses/interface" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get IP address statuses
```bash
curl -X GET "http://localhost:8000/api/nautobot/statuses/ipaddress" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get secret groups
```bash
curl -X GET "http://localhost:8000/api/nautobot/secret-groups" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Onboard a device (example)
```bash
curl -X POST "http://localhost:8000/api/nautobot/devices/onboard" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "ip_address": "192.168.178.10",
  "location_id": "550e8400-e29b-41d4-a716-446655440000",
  "namespace_id": "550e8400-e29b-41d4-a716-446655440001",
  "role_id": "550e8400-e29b-41d4-a716-446655440002",
  "status_id": "550e8400-e29b-41d4-a716-446655440003",
  "platform_id": "detect",
  "secret_groups_id": "550e8400-e29b-41d4-a716-446655440004",
  "interface_status_id": "550e8400-e29b-41d4-a716-446655440005",
  "ip_address_status_id": "550e8400-e29b-41d4-a716-446655440006",
  "port": 22,
  "timeout": 30
}' 2>/dev/null | python3 -m json.tool
```

## Sync Devices Commands

### Get all devices (no filter)
```bash
curl -X GET "http://localhost:8000/api/nautobot/devices" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get devices with pagination
```bash
curl -X GET "http://localhost:8000/api/nautobot/devices?limit=10&offset=0" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Filter devices by name
```bash
curl -X GET "http://localhost:8000/api/nautobot/devices?filter_type=name&filter_value=lab" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Filter devices by location
```bash
curl -X GET "http://localhost:8000/api/nautobot/devices?filter_type=location&filter_value=lab" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Filter devices by IP prefix
```bash
curl -X GET "http://localhost:8000/api/nautobot/devices?filter_type=prefix&filter_value=192.168.178.0/24" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get specific device by ID
```bash
curl -X GET "http://localhost:8000/api/nautobot/devices/ba9c0e96-2ab5-4eca-9f29-f6d49b319180" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Sync network data (example)
```bash
curl -X POST "http://localhost:8000/api/nautobot/sync-network-data" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "data": {
    "devices": ["ba9c0e96-2ab5-4eca-9f29-f6d49b319180"],
    "default_prefix_status": "550e8400-e29b-41d4-a716-446655440007",
    "interface_status": "550e8400-e29b-41d4-a716-446655440008",
    "ip_address_status": "550e8400-e29b-41d4-a716-446655440009",
    "namespace": "550e8400-e29b-41d4-a716-446655440010",
    "sync_cables": true,
    "sync_software_version": true,
    "sync_vlans": true,
    "sync_vrfs": true
  }
}' 2>/dev/null | python3 -m json.tool
```

## Git Repository Commands

### Get repository status
```bash
curl -X GET "http://localhost:8000/api/git/repo/status" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Clone repository
```bash
curl -X POST "http://localhost:8000/api/git/repo/clone" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Sync repository
```bash
curl -X POST "http://localhost:8000/api/git/repo/sync" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get branches
```bash
curl -X GET "http://localhost:8000/api/git/branches" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get commits for a branch
```bash
curl -X GET "http://localhost:8000/api/git/commits?branch=main" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Get commit details
```bash
curl -X GET "http://localhost:8000/api/git/commit/COMMIT_HASH_HERE" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Search files
```bash
curl -X POST "http://localhost:8000/api/git/search" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "pattern": "interface",
  "is_regex": false
}' 2>/dev/null | python3 -m json.tool
```

### Search files with regex
```bash
curl -X POST "http://localhost:8000/api/git/search" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "pattern": "interface.*GigabitEthernet",
  "is_regex": true
}' 2>/dev/null | python3 -m json.tool
```

## Compare Commands

### Get file content from specific commit
```bash
curl -X GET "http://localhost:8000/api/git/file/configs/device1.cfg?commit=COMMIT_HASH_HERE" -H "Authorization: Bearer $TOKEN" 2>/dev/null
```

### Get current file content
```bash
curl -X GET "http://localhost:8000/api/git/file/configs/device1.cfg" -H "Authorization: Bearer $TOKEN" 2>/dev/null
```

### Get file history
```bash
curl -X GET "http://localhost:8000/api/git/file-complete-history/configs/device1.cfg" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### Compare two commits (diff)
```bash
curl -X POST "http://localhost:8000/api/git/diff" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "commit1": "COMMIT_HASH_1",
  "commit2": "COMMIT_HASH_2",
  "file_path": "configs/device1.cfg"
}' 2>/dev/null
```

### Compare commit with working directory
```bash
curl -X POST "http://localhost:8000/api/git/diff" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "commit1": "COMMIT_HASH_HERE",
  "commit2": "HEAD",
  "file_path": "configs/device1.cfg"
}' 2>/dev/null
```

### List files in a commit
```bash
curl -X GET "http://localhost:8000/api/git/files?commit=COMMIT_HASH_HERE" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

### List all files in repository
```bash
curl -X GET "http://localhost:8000/api/git/files" -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -m json.tool
```

## Database Debug Commands

### SQLite schema
```bash
sqlite3 data/settings/cockpit_settings.db ".schema git_settings"
```

### SQLite data
```bash
sqlite3 data/settings/cockpit_settings.db "SELECT id, repo_url, verify_ssl, updated_at FROM git_settings ORDER BY id DESC LIMIT 3;"
```

### All settings tables
```bash
sqlite3 data/settings/cockpit_settings.db ".tables"
```

### Nautobot settings
```bash
sqlite3 data/settings/cockpit_settings.db "SELECT * FROM nautobot_settings ORDER BY id DESC LIMIT 1;"
```

## Quick Test Scripts

### Complete authentication test
```bash
echo "=== Testing Authentication ==="
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
if [ -n "$TOKEN" ]; then
  echo "✅ Login successful"
  curl -s -X GET "http://localhost:8000/auth/verify" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
else
  echo "❌ Login failed"
fi
```

### Complete onboarding test
```bash
echo "=== Testing Onboarding Flow ==="
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
echo "1. Checking Nautobot connection..."
curl -s -X GET "http://localhost:8000/api/nautobot/test" -H "Authorization: Bearer $TOKEN" | python3 -c "import json,sys; data=json.load(sys.stdin); print('✅ Connected' if data.get('success') else '❌ Failed')"
echo "2. Checking IP availability..."
curl -s -X POST "http://localhost:8000/api/nautobot/check-ip" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"ip_address": "192.168.178.1"}' | python3 -c "import json,sys; data=json.load(sys.stdin); print('✅ Available' if data.get('is_available') else '❌ Not available')"
echo "3. Getting locations count..."
curl -s -X GET "http://localhost:8000/api/nautobot/locations" -H "Authorization: Bearer $TOKEN" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f'📍 {len(data)} locations found')"
```

### Complete sync devices test
```bash
echo "=== Testing Sync Devices ==="
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
echo "1. Getting all devices..."
curl -s -X GET "http://localhost:8000/api/nautobot/devices?limit=5" -H "Authorization: Bearer $TOKEN" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f'📱 {data.get(\"count\", 0)} total devices, showing first 5')"
echo "2. Testing location filter..."
curl -s -X GET "http://localhost:8000/api/nautobot/devices?filter_type=location&filter_value=lab" -H "Authorization: Bearer $TOKEN" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f'🏢 {len(data.get(\"devices\", []))} devices in lab locations')"
echo "3. Testing name filter..."
curl -s -X GET "http://localhost:8000/api/nautobot/devices?filter_type=name&filter_value=lab" -H "Authorization: Bearer $TOKEN" | python3 -c "import json,sys; data=json.load(sys.stdin); print(f'🏷️ {len(data.get(\"devices\", []))} devices with 'lab' in name')"
```

## Frontend Fix Applied
The issue was in the frontend `settings.html` file:

1. **Inconsistent property names**: The fallback code was using `verifySSL` instead of `verify_ssl`
2. **Incorrect boolean logic**: Using `!== false` instead of `=== true` caused `undefined`/`null` values to default to `true` (checked)

### Fixed in settings.html:
- Line ~582: Changed `settings.git.verify_ssl !== false` to `settings.git.verify_ssl === true`
- Line ~622: Changed `settings.git.verifySSL !== false` to `settings.git.verify_ssl === true`
- Line ~613: Changed `settings.nautobot.verifySSL !== false` to `settings.nautobot.verify_ssl !== false`
