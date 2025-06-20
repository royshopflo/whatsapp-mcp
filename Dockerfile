# Multi-stage Dockerfile for WhatsApp MCP Application

# Stage 1: Build Go WhatsApp Bridge
FROM golang:1.24-alpine AS go-builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev sqlite-dev

WORKDIR /app/whatsapp-bridge

# Copy Go module files
COPY whatsapp-bridge/go.mod whatsapp-bridge/go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY whatsapp-bridge/ ./

# Build the application with CGO enabled for SQLite
RUN CGO_ENABLED=1 GOOS=linux go build -a -installsuffix cgo -o main .

# Stage 2: Python MCP Server
FROM python:3.11-slim AS python-builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app/whatsapp-mcp-server

# Copy Python project files
COPY whatsapp-mcp-server/ ./

# Install Python dependencies using uv
RUN uv sync

# Stage 3: Final runtime image
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv in final image
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Create app directory
WORKDIR /app

# Copy built Go application
COPY --from=go-builder /app/whatsapp-bridge/main /app/whatsapp-bridge/main

# Copy Python MCP server
COPY --from=python-builder /app/whatsapp-mcp-server /app/whatsapp-mcp-server

# Copy additional scripts and configurations
COPY *.py ./
COPY *.sh ./
COPY *.md ./

# Create necessary directories
RUN mkdir -p /app/whatsapp-bridge/store /app/logs

# Make scripts executable
RUN chmod +x *.sh

# Set working directory for the bridge
WORKDIR /app/whatsapp-bridge

# Expose the API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api || exit 1

# Start the Go WhatsApp bridge
CMD ["./main"] 