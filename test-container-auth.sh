#!/bin/bash

echo "=== Docker Container Authentication Test ==="
echo

# Function to test URL accessibility
test_url() {
    local url="$1"
    local description="$2"
    echo "Testing: $description"
    echo "URL: $url"
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|302"; then
        echo "✅ SUCCESS"
    else
        echo "❌ FAILED"
    fi
    echo
}

# Get container IP if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running inside Docker container"
    CONTAINER_IP=$(hostname -i | awk '{print $1}')
    echo "Container IP: $CONTAINER_IP"
else
    echo "Running on host system"
    CONTAINER_IP="localhost"
fi

echo

# Test different access methods
test_url "http://localhost:3000/test-auth-config.html" "Frontend via localhost:3000"
test_url "http://localhost:3000/auth/login" "Auth endpoint via localhost:3000 (should proxy to backend)"
test_url "http://localhost:8000/auth/login" "Direct backend access on localhost:8000"

if [ "$CONTAINER_IP" != "localhost" ]; then
    test_url "http://$CONTAINER_IP:3000/test-auth-config.html" "Frontend via container IP:3000"
    test_url "http://$CONTAINER_IP:3000/auth/login" "Auth endpoint via container IP:3000 (should proxy)"
fi

# Test external hostname if provided
if [ -n "$1" ]; then
    echo "Testing external hostname: $1"
    test_url "http://$1:3000/test-auth-config.html" "Frontend via $1:3000"
    test_url "http://$1:3000/auth/login" "Auth endpoint via $1:3000 (should proxy)"
    test_url "http://$1:8000/auth/login" "Direct backend via $1:8000"
fi

echo "=== Test Complete ==="
echo
echo "Open these URLs in your browser to test the authentication configuration:"
echo "- http://localhost:3000/test-auth-config.html"
if [ -n "$1" ]; then
    echo "- http://$1:3000/test-auth-config.html"
fi
