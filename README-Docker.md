# WhatsApp MCP Docker Setup

This guide explains how to run the WhatsApp MCP application using Docker for easy deployment and consistent environments.

## 🐳 Docker Architecture

The application is containerized into two main services:

1. **WhatsApp Bridge** - Go application that connects to WhatsApp Web API
2. **MCP Server** - Python server providing Model Context Protocol interface

## 📋 Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)
- At least 2GB RAM
- Internet connection for WhatsApp Web API

## 🚀 Quick Start

### 1. Clone and Build

```bash
git clone https://github.com/lharries/whatsapp-mcp.git
cd whatsapp-mcp

# Make the startup script executable
chmod +x docker-start.sh

# Build Docker images
./docker-start.sh build
```

### 2. Start WhatsApp Bridge

```bash
# Start only the WhatsApp Bridge
./docker-start.sh start
```

On first run, you'll see a QR code in the logs. Scan it with your WhatsApp mobile app to authenticate.

### 3. Start Complete System (Optional)

```bash
# Start both WhatsApp Bridge and MCP Server
./docker-start.sh start-all
```

## 📁 File Structure

```
whatsapp-mcp/
├── Dockerfile              # Multi-stage build for WhatsApp Bridge
├── Dockerfile.mcp          # MCP Server container
├── docker-compose.yml      # Service orchestration
├── docker-start.sh         # Helper script for common operations
├── .dockerignore           # Optimize build context
└── README-Docker.md        # This file
```

## 🔧 Configuration

### Environment Variables

The following environment variables can be configured in `docker-compose.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `TZ` | Timezone | `UTC` |
| `WHATSAPP_API_BASE_URL` | API endpoint for MCP server | `http://whatsapp-bridge:8080/api` |
| `MESSAGES_DB_PATH` | Database path | `/app/whatsapp-bridge/store/messages.db` |

### Volumes

- `whatsapp_store` - Persistent storage for WhatsApp session and messages
- `app_logs` - Application logs

### Ports

- `8080` - WhatsApp Bridge REST API

## 🛠️ Usage Commands

The `docker-start.sh` script provides convenient commands:

```bash
# Build images
./docker-start.sh build

# Start services
./docker-start.sh start       # WhatsApp Bridge only
./docker-start.sh start-all   # Both services

# Monitor and debug
./docker-start.sh status      # Check service status
./docker-start.sh logs        # View all logs
./docker-start.sh logs whatsapp-bridge  # Specific service logs

# Stop and cleanup
./docker-start.sh stop        # Stop all services
./docker-start.sh clean       # Remove containers and images
```

## 🔗 Connecting to Claude/Cursor

### For Claude Desktop

Create or update `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "whatsapp-mcp-server",
        "uv",
        "run",
        "main.py"
      ]
    }
  }
}
```

### For Cursor

Create or update `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "docker",
      "args": [
        "exec",
        "-i", 
        "whatsapp-mcp-server",
        "uv",
        "run",
        "main.py"
      ]
    }
  }
}
```

## 📊 Monitoring

### Health Checks

The containers include built-in health checks:

```bash
# Check container health
docker-compose ps

# Manual health check
curl -f http://localhost:8080/api
```

### Logs

View logs for debugging:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f whatsapp-bridge
docker-compose logs -f whatsapp-mcp-server

# Using helper script
./docker-start.sh logs
./docker-start.sh logs whatsapp-bridge
```

## 🔧 Troubleshooting

### Common Issues

#### QR Code Not Appearing
```bash
# Check if container is running
./docker-start.sh status

# View logs for QR code
./docker-start.sh logs whatsapp-bridge
```

#### Database Issues
```bash
# Reset authentication (removes stored session)
docker-compose down -v
./docker-start.sh start
```

#### API Not Responding
```bash
# Check if port 8080 is available
netstat -an | grep 8080

# Restart services
./docker-start.sh stop
./docker-start.sh start
```

#### Build Failures
```bash
# Clean and rebuild
./docker-start.sh clean
./docker-start.sh build
```

### Development Mode

For development, you can mount local code:

```yaml
# Add to docker-compose.yml under whatsapp-bridge service
volumes:
  - ./whatsapp-bridge:/app/whatsapp-bridge
  - whatsapp_store:/app/whatsapp-bridge/store
```

## 🔒 Security Considerations

1. **Database Security**: The SQLite database contains your WhatsApp messages
2. **Container Access**: Limit container access to necessary ports only
3. **Volume Permissions**: Ensure proper file permissions on mounted volumes
4. **Network Security**: Use internal networks for service communication

## 📈 Performance Tips

1. **Resource Allocation**: Allocate adequate memory (2GB+ recommended)
2. **Storage**: Use SSD storage for better database performance
3. **Network**: Ensure stable internet connection for WhatsApp Web API
4. **Monitoring**: Use health checks to monitor service status

## 🔄 Updates

To update the application:

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./docker-start.sh stop
./docker-start.sh build
./docker-start.sh start
```

## 🆘 Support

For issues specific to the Docker setup:

1. Check container logs: `./docker-start.sh logs`
2. Verify Docker installation: `docker --version`
3. Check system resources: `docker system df`
4. Review the main README.md for application-specific issues

## 📝 License

This Docker setup follows the same license as the main project. See LICENSE file for details. 