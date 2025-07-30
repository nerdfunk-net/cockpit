# SSL Verification Testing Commands

## Get a token
```bash
curl -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])"
```

## Get current settings
```bash
curl -X GET "http://localhost:8000/api/settings" -H "Authorization: Bearer TOKEN_HERE" -H "Content-Type: application/json" 2>/dev/null | python3 -m json.tool
```

## GIT settings - Set SSL verification to TRUE
```bash
curl -X POST "http://localhost:8000/api/settings/git" -H "Authorization: Bearer TOKEN_HERE" -H "Content-Type: application/json" -d '{
  "repo_url": "https://github.com/nerdfunk-net/test-repo.git",
  "branch": "main", 
  "username": "nerdfunk-net",
  "token": "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",
  "config_path": "configs/",
  "sync_interval": 15,
  "verify_ssl": true
}' 2>/dev/null | python3 -m json.tool
```

## GIT settings - Set SSL verification to FALSE
```bash
curl -X POST "http://localhost:8000/api/settings/git" -H "Authorization: Bearer TOKEN_HERE" -H "Content-Type: application/json" -d '{
  "repo_url": "https://github.com/nerdfunk-net/test-repo.git",
  "branch": "main", 
  "username": "nerdfunk-net",
  "token": "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",
  "config_path": "configs/",
  "sync_interval": 15,
  "verify_ssl": false
}' 2>/dev/null | python3 -m json.tool
```

## SQLite schema
```bash
sqlite3 data/settings/cockpit_settings.db ".schema git_settings"
```

## SQLite data
```bash
sqlite3 data/settings/cockpit_settings.db "SELECT id, repo_url, verify_ssl, updated_at FROM git_settings ORDER BY id DESC LIMIT 3;"
```

## Frontend Fix Applied
The issue was in the frontend `settings.html` file:

1. **Inconsistent property names**: The fallback code was using `verifySSL` instead of `verify_ssl`
2. **Incorrect boolean logic**: Using `!== false` instead of `=== true` caused `undefined`/`null` values to default to `true` (checked)

### Fixed in settings.html:
- Line ~582: Changed `settings.git.verify_ssl !== false` to `settings.git.verify_ssl === true`
- Line ~622: Changed `settings.git.verifySSL !== false` to `settings.git.verify_ssl === true`
- Line ~613: Changed `settings.nautobot.verifySSL !== false` to `settings.nautobot.verify_ssl !== false`
