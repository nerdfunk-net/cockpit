#!/bin/bash

# Cockpit Docker Startup Script
# This script helps you run Cockpit in Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "🚀 Cockpit - Network Device Management Dashboard"
echo "   Docker Deployment Script"
echo -e "${NC}"

# Check if Docker and Docker Compose are installed
check_dependencies() {
    echo -e "${BLUE}📋 Checking dependencies...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dependencies check passed${NC}"
}

# Check if .env file exists
check_env_file() {
    echo -e "${BLUE}🔧 Checking environment configuration...${NC}"
    
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
        cp .env.docker .env
        echo -e "${YELLOW}📝 Please edit .env file with your Nautobot configuration:${NC}"
        echo -e "   - NAUTOBOT_HOST=https://your-nautobot-instance.com"
        echo -e "   - NAUTOBOT_TOKEN=your-api-token"
        echo -e "   - SECRET_KEY=your-secret-key"
        echo ""
        echo -e "${YELLOW}Press Enter when you've configured the .env file...${NC}"
        read -r
    fi
    
    echo -e "${GREEN}✅ Environment configuration ready${NC}"
}

# Build and start containers
start_containers() {
    echo -e "${BLUE}🐳 Building and starting Docker containers...${NC}"
    
    # Build containers
    docker-compose build --no-cache
    
    # Start containers
    docker-compose up -d
    
    echo -e "${GREEN}✅ Containers started successfully${NC}"
}

# Wait for services to be healthy
wait_for_services() {
    echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
    
    # Wait for backend
    echo -e "   Waiting for backend service..."
    timeout 60 bash -c 'while ! curl -f http://localhost:8000/docs >/dev/null 2>&1; do sleep 2; done' || {
        echo -e "${RED}❌ Backend service failed to start${NC}"
        docker-compose logs backend
        exit 1
    }
    
    # Wait for frontend
    echo -e "   Waiting for frontend service..."
    timeout 30 bash -c 'while ! curl -f http://localhost/health >/dev/null 2>&1; do sleep 2; done' || {
        echo -e "${RED}❌ Frontend service failed to start${NC}"
        docker-compose logs frontend
        exit 1
    }
    
    echo -e "${GREEN}✅ All services are healthy${NC}"
}

# Show success message
show_success() {
    echo -e "${GREEN}"
    echo "🎉 Cockpit is now running!"
    echo ""
    echo "📱 Frontend: http://localhost"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "Default login credentials:"
    echo "  Username: admin"
    echo "  Password: secret"
    echo ""
    echo -e "${YELLOW}⚠️  Remember to change default passwords in production!${NC}"
    echo ""
    echo "To stop the application:"
    echo "  docker-compose down"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo -e "${NC}"
}

# Main execution
main() {
    check_dependencies
    check_env_file
    start_containers
    wait_for_services
    show_success
}

# Handle script arguments
case "${1:-}" in
    "stop")
        echo -e "${BLUE}🛑 Stopping Cockpit containers...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Containers stopped${NC}"
        ;;
    "restart")
        echo -e "${BLUE}🔄 Restarting Cockpit containers...${NC}"
        docker-compose down
        main
        ;;
    "logs")
        echo -e "${BLUE}📋 Showing container logs...${NC}"
        docker-compose logs -f
        ;;
    "status")
        echo -e "${BLUE}📊 Container status:${NC}"
        docker-compose ps
        ;;
    *)
        main
        ;;
esac
