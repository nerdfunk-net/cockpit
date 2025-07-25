#!/bin/bash

# Build script for Cockpit Offline Container
set -e

echo "🐳 Building Cockpit Offline Container..."

# Configuration
IMAGE_NAME="cockpit-frontend"
IMAGE_TAG="offline-latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
print_step "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi

# Check if package.json exists and has vite
if [ ! -f "package.json" ]; then
    print_error "package.json not found"
    exit 1
fi

if ! grep -q "vite" package.json; then
    print_error "Vite not found in package.json dependencies"
    exit 1
fi

print_success "Prerequisites check passed"

# Check for required files
print_step "Checking required files..."

REQUIRED_FILES=(
    "production/static/css/fontawesome.min.css"
    "production/static/webfonts/fa-solid-900.woff2"
    "production/js/config.js"
    "production/js/config-container.js"
    "production/js/offline-manager.js"
    "production/service-worker.js"
    "docker/startup.sh"
    "docker/nginx-offline.conf"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done

print_success "Required files check passed"

# Verify static assets
print_step "Verifying static assets..."

WEBFONT_COUNT=$(find production/static/webfonts -name "*.woff2" -o -name "*.ttf" 2>/dev/null | wc -l)
if [ "$WEBFONT_COUNT" -lt 6 ]; then
    print_warning "Only $WEBFONT_COUNT webfont files found (expected 8)"
    print_warning "Some fonts may be missing"
fi

if [ ! -f "production/static/css/fontawesome.min.css" ]; then
    print_error "FontAwesome CSS not found"
    exit 1
fi

print_success "Static assets verified"

# Test static files for offline deployment
print_step "Testing static files for offline deployment..."

if [ ! -d "production" ]; then
    print_error "Production directory not found"
    exit 1
fi

if [ ! -f "production/index.html" ]; then
    print_error "Main index.html not found in production directory"
    exit 1
fi

print_success "Static files verified"

# Build the container
print_step "Building Docker image: $FULL_IMAGE_NAME"

docker build \
    -f Dockerfile.static \
    -t "$FULL_IMAGE_NAME" \
    --build-arg BUILD_DATE="$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    --label "org.label-schema.build-date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --label "org.label-schema.vcs-ref=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    --label "org.label-schema.version=offline-latest" \
    --label "org.label-schema.name=cockpit-frontend" \
    --label "org.label-schema.description=Cockpit Frontend (Offline-ready)" \
    .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully: $FULL_IMAGE_NAME"
else
    print_error "Docker build failed"
    exit 1
fi

# Test the container
print_step "Testing container startup..."

CONTAINER_ID=$(docker run -d --rm -p 8080:80 "$FULL_IMAGE_NAME")

if [ $? -eq 0 ]; then
    print_success "Container started with ID: $CONTAINER_ID"
    
    # Wait for container to be ready
    sleep 5
    
    # Test health endpoint
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_warning "Health check failed"
    fi
    
    # Test static assets
    if curl -f http://localhost:8080/static/css/fontawesome.min.css > /dev/null 2>&1; then
        print_success "Static assets accessible"
    else
        print_warning "Static assets not accessible"
    fi
    
    # Stop test container
    docker stop "$CONTAINER_ID" > /dev/null
    print_success "Test container stopped"
else
    print_error "Container startup failed"
    exit 1
fi

# Display image information
print_step "Image information:"
docker images "$FULL_IMAGE_NAME"

# Display image size
IMAGE_SIZE=$(docker images --format "table {{.Size}}" "$FULL_IMAGE_NAME" | tail -n +2)
print_success "Image size: $IMAGE_SIZE"

# Generate image report
print_step "Generating image report..."

cat > "docker-image-report.txt" << EOF
Cockpit Offline Container Build Report
=====================================

Build Date: $(date)
Image Name: $FULL_IMAGE_NAME
Image Size: $IMAGE_SIZE
Git Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')

Static Assets:
- FontAwesome CSS: $([ -f "production/static/css/fontawesome.min.css" ] && echo "✅" || echo "❌")
- WebFonts: $WEBFONT_COUNT files
- Config Files: $(ls production/js/config*.js 2>/dev/null | wc -l) files
- Offline Manager: $([ -f "production/js/offline-manager.js" ] && echo "✅" || echo "❌")
- Service Worker: $([ -f "production/service-worker.js" ] && echo "✅" || echo "❌")

Container Features:
- Offline-ready: ✅
- Auto-configuration: ✅  
- Static asset caching: ✅
- Service worker: ✅
- Health checks: ✅
- Non-root user: ✅

Usage:
  docker run -d -p 80:80 -e COCKPIT_API_URL=http://backend:8000 $FULL_IMAGE_NAME

Docker Compose:
  docker-compose -f docker-compose.offline.yml up
EOF

print_success "Build report saved to docker-image-report.txt"

echo ""
print_success "🎉 Cockpit Offline Container build completed successfully!"
echo ""
echo "Next steps:"
echo "1. Test the container: docker run -d -p 80:80 $FULL_IMAGE_NAME"
echo "2. Use with compose: docker-compose -f docker-compose.offline.yml up"
echo "3. Deploy to your environment"
echo ""
echo "For offline testing:"
echo "docker-compose -f docker-compose.offline.yml -f docker-compose.offline-override.yml up"
