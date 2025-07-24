#!/bin/bash
# Test script for the file comparison system

echo "=== Testing File Comparison System ==="
echo

# Test login
echo "1. Testing login..."
TOKEN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' http://localhost:3000/auth/login)
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Login successful! Token: ${TOKEN:0:20}..."
echo

# Test file listing
echo "2. Testing file listing..."
FILES_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:3000/api/files/list)

if echo "$FILES_RESPONSE" | grep -q '"files"'; then
    echo "✅ File listing successful!"
    echo "Found files:"
    echo "$FILES_RESPONSE" | grep -o '"filename":"[^"]*"' | cut -d'"' -f4 | sed 's/^/  - /'
else
    echo "❌ File listing failed!"
    echo "Response: $FILES_RESPONSE"
    exit 1
fi
echo

# Test file comparison
echo "3. Testing file comparison..."
COMPARISON_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"left_file":"../configs/router1.cfg","right_file":"../configs/router1-updated.cfg"}' http://localhost:3000/api/files/compare)

if echo "$COMPARISON_RESPONSE" | grep -q '"left_file"'; then
    echo "✅ File comparison successful!"
    LEFT_LINES=$(echo "$COMPARISON_RESPONSE" | grep -o '"left_lines":\[[^]]*\]' | wc -c)
    RIGHT_LINES=$(echo "$COMPARISON_RESPONSE" | grep -o '"right_lines":\[[^]]*\]' | wc -c)
    echo "  - Comparison data generated (left: ${LEFT_LINES} chars, right: ${RIGHT_LINES} chars)"
else
    echo "❌ File comparison failed!"
    echo "Response: $COMPARISON_RESPONSE"
    exit 1
fi
echo

# Test export
echo "4. Testing export..."
EXPORT_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"left_file":"../configs/router1.cfg","right_file":"../configs/router1-updated.cfg","format":"unified"}' http://localhost:3000/api/files/export-diff)

if echo "$EXPORT_RESPONSE" | grep -q '"content"'; then
    echo "✅ Export successful!"
    FILENAME=$(echo "$EXPORT_RESPONSE" | grep -o '"filename":"[^"]*"' | cut -d'"' -f4)
    echo "  - Generated file: $FILENAME"
else
    echo "❌ Export failed!"
    echo "Response: $EXPORT_RESPONSE"
    exit 1
fi
echo

echo "🎉 All tests passed! The file comparison system is working correctly."
echo
echo "To use the system:"
echo "1. Open http://localhost:3000/production/login.html"
echo "2. Login with admin/admin"
echo "3. Navigate to http://localhost:3000/production/compare.html"
echo "4. Select files and compare!"
