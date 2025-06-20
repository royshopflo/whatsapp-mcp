#!/bin/bash

# WhatsApp MCP Docker Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  build       Build the Docker images"
    echo "  start       Start WhatsApp Bridge only"
    echo "  start-all   Start both WhatsApp Bridge and MCP Server"
    echo "  stop        Stop all services"
    echo "  logs        Show logs from running services"
    echo "  status      Show status of services"
    echo "  clean       Remove containers and images"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build                # Build Docker images"
    echo "  $0 start                # Start WhatsApp Bridge"
    echo "  $0 start-all            # Start both services"
    echo "  $0 logs whatsapp-bridge # Show logs for specific service"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Build images
build_images() {
    print_status "Building WhatsApp MCP Docker images..."
    docker-compose build
    print_success "Docker images built successfully!"
}

# Start WhatsApp Bridge only
start_bridge() {
    print_status "Starting WhatsApp Bridge..."
    docker-compose up -d whatsapp-bridge
    
    print_status "Waiting for WhatsApp Bridge to be ready..."
    sleep 10
    
    if docker-compose ps whatsapp-bridge | grep -q "Up"; then
        print_success "WhatsApp Bridge is running!"
        print_status "API available at: http://localhost:8080"
        print_warning "Please scan the QR code in the logs if this is your first run:"
        echo ""
        docker-compose logs whatsapp-bridge
    else
        print_error "Failed to start WhatsApp Bridge"
        docker-compose logs whatsapp-bridge
        exit 1
    fi
}

# Start all services
start_all() {
    print_status "Starting all WhatsApp MCP services..."
    docker-compose --profile mcp up -d
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    if docker-compose ps | grep -q "Up"; then
        print_success "All services are running!"
        print_status "WhatsApp Bridge API: http://localhost:8080"
        print_status "MCP Server is ready for Claude/Cursor integration"
        
        print_warning "If this is your first run, please check logs for QR code:"
        docker-compose logs whatsapp-bridge
    else
        print_error "Failed to start services"
        docker-compose logs
        exit 1
    fi
}

# Stop services
stop_services() {
    print_status "Stopping WhatsApp MCP services..."
    docker-compose --profile mcp down
    print_success "Services stopped!"
}

# Show logs
show_logs() {
    if [ -n "$2" ]; then
        docker-compose logs -f "$2"
    else
        docker-compose logs -f
    fi
}

# Show status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo ""
    print_status "Health checks:"
    
    # Check WhatsApp Bridge
    if curl -s -f http://localhost:8080/api >/dev/null 2>&1; then
        print_success "WhatsApp Bridge API is healthy"
    else
        print_warning "WhatsApp Bridge API is not responding"
    fi
}

# Clean up
cleanup() {
    print_warning "This will remove all containers and images. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Stopping and removing containers..."
        docker-compose --profile mcp down -v
        
        print_status "Removing images..."
        docker rmi $(docker images "whatsapp-mcp-*" -q) 2>/dev/null || true
        
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Main script logic
main() {
    check_docker
    
    case "${1:-help}" in
        build)
            build_images
            ;;
        start)
            start_bridge
            ;;
        start-all)
            start_all
            ;;
        stop)
            stop_services
            ;;
        logs)
            show_logs "$@"
            ;;
        status)
            show_status
            ;;
        clean)
            cleanup
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 