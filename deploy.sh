#!/bin/bash

# AbsensiPro Docker Deployment Script
# Usage: ./deploy.sh [build|start|stop|restart|logs|status]

set -e

COMPOSE_FILE="docker-compose.yaml"
SERVICE_NAME="web"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_requirements() {
    print_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f ".env" ]; then
        print_error ".env file not found. Copy .env.example and configure it."
        exit 1
    fi
    
    if [ ! -f "credentials.json" ]; then
        print_error "credentials.json not found"
        exit 1
    fi
    
    print_success "All requirements met"
}

build() {
    print_info "Building Docker image..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    print_success "Build completed"
}

start() {
    print_info "Starting application..."
    docker-compose -f $COMPOSE_FILE up -d
    print_success "Application started"
    print_info "Waiting for health check..."
    sleep 5
    status
}

stop() {
    print_info "Stopping application..."
    docker-compose -f $COMPOSE_FILE down
    print_success "Application stopped"
}

restart() {
    stop
    start
}

logs() {
    docker-compose -f $COMPOSE_FILE logs -f $SERVICE_NAME
}

status() {
    print_info "Container status:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    print_info "Health status:"
    docker inspect --format='{{.State.Health.Status}}' absensipro 2>/dev/null || echo "No health check available"
    
    echo ""
    print_info "Recent logs:"
    docker-compose -f $COMPOSE_FILE logs --tail=20 $SERVICE_NAME
}

# Main
case "$1" in
    build)
        check_requirements
        build
        ;;
    start)
        check_requirements
        start
        ;;
    stop)
        stop
        ;;
    restart)
        check_requirements
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {build|start|stop|restart|logs|status}"
        echo ""
        echo "Commands:"
        echo "  build   - Build Docker image"
        echo "  start   - Start application"
        echo "  stop    - Stop application"
        echo "  restart - Restart application"
        echo "  logs    - View application logs"
        echo "  status  - Check application status"
        exit 1
        ;;
esac
