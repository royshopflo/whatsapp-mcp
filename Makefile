# WhatsApp MCP Docker Makefile

.PHONY: help build start start-all stop logs status clean test

# Default target
help:
	@echo "WhatsApp MCP Docker Commands:"
	@echo ""
	@echo "  make build      - Build Docker images"
	@echo "  make start      - Start WhatsApp Bridge only" 
	@echo "  make start-all  - Start both services"
	@echo "  make stop       - Stop all services"
	@echo "  make logs       - Show logs from all services"
	@echo "  make status     - Show service status"
	@echo "  make test       - Test the services"
	@echo "  make clean      - Remove containers and images"
	@echo "  make help       - Show this help message"

# Build Docker images
build:
	@echo "Building WhatsApp MCP Docker images..."
	docker-compose build
	@echo "✅ Build completed!"

# Start WhatsApp Bridge only
start:
	@echo "Starting WhatsApp Bridge..."
	docker-compose up -d whatsapp-bridge
	@echo "✅ WhatsApp Bridge started!"
	@echo "🔗 API available at: http://localhost:8080"
	@echo ""
	@echo "📱 If this is your first run, scan the QR code:"
	@sleep 3
	docker-compose logs whatsapp-bridge

# Start all services
start-all:
	@echo "Starting all WhatsApp MCP services..."
	docker-compose --profile mcp up -d
	@echo "✅ All services started!"
	@echo "🔗 WhatsApp Bridge API: http://localhost:8080"
	@echo "🤖 MCP Server ready for Claude/Cursor"

# Stop services
stop:
	@echo "Stopping WhatsApp MCP services..."
	docker-compose --profile mcp down
	@echo "✅ Services stopped!"

# Show logs
logs:
	docker-compose logs -f

# Show status
status:
	@echo "📊 Service Status:"
	docker-compose ps
	@echo ""
	@echo "🩺 Health Check:"
	@curl -s -f http://localhost:8080/api >/dev/null 2>&1 && echo "✅ WhatsApp Bridge API is healthy" || echo "❌ WhatsApp Bridge API is not responding"

# Test services
test:
	@echo "🧪 Testing services..."
	@curl -s -f http://localhost:8080/api >/dev/null 2>&1 && echo "✅ WhatsApp Bridge API test passed" || echo "❌ WhatsApp Bridge API test failed"

# Clean up everything
clean:
	@echo "🧹 Cleaning up containers and images..."
	@echo "⚠️  This will remove all containers and images. Continue? [y/N]" && read ans && [ $${ans:-N} = y ]
	docker-compose --profile mcp down -v
	docker rmi $$(docker images "whatsapp-mcp-*" -q) 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# Development helpers
dev-logs:
	docker-compose logs -f whatsapp-bridge

mcp-logs:
	docker-compose logs -f whatsapp-mcp-server

restart:
	make stop
	make start

restart-all:
	make stop  
	make start-all 