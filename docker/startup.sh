#!/bin/sh

# Startup script for Cockpit Frontend Container
# Injects environment variables into JavaScript configuration

set -e

echo "🚀 Starting Cockpit Frontend Container..."

# Default values
COCKPIT_API_URL=${COCKPIT_API_URL:-""}
COCKPIT_CONTAINER_MODE=${COCKPIT_CONTAINER_MODE:-"true"}
COCKPIT_DEBUG=${COCKPIT_DEBUG:-"false"}

# Detect API URL if not provided
if [ -z "$COCKPIT_API_URL" ]; then
    # Try to detect from hostname
    HOSTNAME=$(hostname -i 2>/dev/null || echo "localhost")
    COCKPIT_API_URL="http://${HOSTNAME}:8000"
    echo "🔍 Auto-detected API URL: $COCKPIT_API_URL"
fi

echo "🔧 Configuration:"
echo "   API URL: $COCKPIT_API_URL"
echo "   Container Mode: $COCKPIT_CONTAINER_MODE"
echo "   Debug Mode: $COCKPIT_DEBUG"

# Create container configuration override
cat > /usr/share/nginx/html/js/config-container-runtime.js << EOF
// Runtime Container Configuration (Auto-generated)
// This file is created at container startup

(function() {
    console.log('🐳 Loading runtime container configuration...');
    
    // Override environment variables
    window.COCKPIT_API_URL = '${COCKPIT_API_URL}';
    window.COCKPIT_CONTAINER_MODE = ${COCKPIT_CONTAINER_MODE};
    window.COCKPIT_DEBUG = ${COCKPIT_DEBUG};
    
    // Set hostname for debugging
    window.COCKPIT_HOSTNAME = '$(hostname)';
    window.COCKPIT_START_TIME = new Date().toISOString();
    
    // Add container class to body
    document.addEventListener('DOMContentLoaded', function() {
        document.body.classList.add('container-mode', 'runtime-configured');
        console.log('✅ Runtime configuration applied');
    });
    
    console.log('🔧 Runtime Config Applied:', {
        apiUrl: window.COCKPIT_API_URL,
        containerMode: window.COCKPIT_CONTAINER_MODE,
        debug: window.COCKPIT_DEBUG,
        hostname: window.COCKPIT_HOSTNAME
    });
})();
EOF

echo "✅ Runtime configuration created"

# Update HTML files to include runtime config
for html_file in /usr/share/nginx/html/*.html; do
    if [ -f "$html_file" ]; then
        # Check if runtime config is already included
        if ! grep -q "config-container-runtime.js" "$html_file"; then
            # Add runtime config script before closing head tag
            sed -i 's|</head>|    <!-- Runtime Container Configuration -->\n    <script src="js/config-container-runtime.js"></script>\n  </head>|g' "$html_file"
            echo "✅ Updated $(basename "$html_file") with runtime config"
        fi
    fi
done

# Create offline status file
cat > /usr/share/nginx/html/status.json << EOF
{
    "status": "online",
    "container_mode": ${COCKPIT_CONTAINER_MODE},
    "api_url": "${COCKPIT_API_URL}",
    "debug": ${COCKPIT_DEBUG},
    "hostname": "$(hostname)",
    "start_time": "$(date -Iseconds)",
    "offline_ready": true,
    "static_assets": {
        "fontawesome": true,
        "fonts": true,
        "service_worker": true
    }
}
EOF

echo "✅ Status file created"

# Validate static assets
echo "🔍 Validating offline assets..."

# Check FontAwesome files
if [ -f "/usr/share/nginx/html/static/css/fontawesome.min.css" ]; then
    echo "   ✅ FontAwesome CSS found"
else
    echo "   ❌ FontAwesome CSS missing"
fi

# Check webfonts
WEBFONT_COUNT=$(find /usr/share/nginx/html/static/webfonts -name "*.woff2" -o -name "*.ttf" | wc -l)
if [ "$WEBFONT_COUNT" -ge 6 ]; then
    echo "   ✅ WebFonts found ($WEBFONT_COUNT files)"
else
    echo "   ⚠️  WebFonts incomplete ($WEBFONT_COUNT files)"
fi

# Check offline manager
if [ -f "/usr/share/nginx/html/js/offline-manager.js" ]; then
    echo "   ✅ Offline Manager found"
else
    echo "   ❌ Offline Manager missing"
fi

# Check service worker
if [ -f "/usr/share/nginx/html/service-worker.js" ]; then
    echo "   ✅ Service Worker found"
else
    echo "   ❌ Service Worker missing"
fi

echo "🌐 Starting Nginx..."

# Start nginx in foreground
exec nginx -g "daemon off;"
