
# Get a token
    curl -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])"

# Get Settings
    curl -X GET "http://localhost:8000/api/settings" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MzkwMTQ4NH0.2eienrNsV2MECrBgHlcBi1Kf3DF-8rE9qx7XYNiiDSI" -H "Content-Type: application/json" 2>/dev/null | python3 -m json.tool

# Write GIT settings
curl -X POST "http://localhost:8000/api/settings/git" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MzkwMDk4MH0.YTkDaOudHRT4DshXj9rSrfQ_zDQeBEnh3pdSotpTq1Y" -H "Content-Type: application/json" -d '{
  "repo_url": "https://github.com/nerdfunk-net/test-repo.git",
  "branch": "main", 
  "username": "nerdfunk-net",
  "token": "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",
  "config_path": "configs/",
  "sync_interval": 15,
  "verify_ssl": false
}' 2>/dev/null | python3 -m json.tool

# SQLite schema
  sqlite3 data/settings/cockpit_settings.db ".schema git_settings"