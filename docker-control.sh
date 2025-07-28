#!/bin/bash

# Cockpit Container Management Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  dev         Start development container (with hot reload)"
    echo "  prod        Start production container (built assets)"
    echo "  stop        Stop all Cockpit containers"
    echo "  restart     Restart containers"
    echo "  logs        Show container logs"
    echo "  build       Rebuild containers"
    echo "  clean       Remove containers and images"
    echo ""
}

case "$1" in
    "dev")
        echo "Starting Cockpit in development mode..."
        # Ensure data directory exists
        mkdir -p ./data/settings
        docker-compose up -d
        echo "✅ Development container started!"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend:  http://localhost:8000"
        echo "   Database: ./data/settings/"
        echo "   Logs:     docker-compose logs -f"
        ;;
    "prod")
        echo "Starting Cockpit in production mode..."
        # Ensure data directory exists
        mkdir -p ./data/settings
        docker-compose -f docker-compose.production.yml up -d
        echo "✅ Production container started!"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend:  http://localhost:8000"
        echo "   Database: ./data/settings/"
        echo "   Logs:     docker-compose -f docker-compose.production.yml logs -f"
        ;;
    "stop")
        echo "Stopping Cockpit containers..."
        docker-compose down || true
        docker-compose -f docker-compose.production.yml down || true
        echo "✅ Containers stopped!"
        ;;
    "restart")
        echo "Restarting Cockpit containers..."
        docker-compose restart || docker-compose -f docker-compose.production.yml restart
        echo "✅ Containers restarted!"
        ;;
    "logs")
        if docker-compose ps | grep -q cockpit-unified; then
            docker-compose logs -f
        elif docker-compose -f docker-compose.production.yml ps | grep -q cockpit-unified-production; then
            docker-compose -f docker-compose.production.yml logs -f
        else
            echo "❌ No Cockpit containers are running"
        fi
        ;;
    "build")
        echo "Rebuilding Cockpit containers..."
        docker-compose build --no-cache
        docker-compose -f docker-compose.production.yml build --no-cache
        echo "✅ Containers rebuilt!"
        ;;
    "clean")
        echo "Cleaning up Cockpit containers and images..."
        docker-compose down --rmi all --volumes --remove-orphans || true
        docker-compose -f docker-compose.production.yml down --rmi all --volumes --remove-orphans || true
        echo "✅ Cleanup complete!"
        ;;
    *)
        print_usage
        exit 1
        ;;
esac
