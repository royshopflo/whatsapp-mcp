# WhatsApp MCP Developer Guide

This guide is for developers who want to contribute to, extend, or understand the internal workings of the WhatsApp MCP server.

## Architecture Deep Dive

### System Components

The WhatsApp MCP system consists of two main components that work together:

```
┌─────────────────┐    HTTP/JSON    ┌──────────────────┐    WhatsApp API    ┌─────────────────┐
│                 │◄─────────────────┤                  │◄───────────────────┤                 │
│   Claude/MCP    │                  │   Python MCP     │                    │   Go Bridge     │
│   Client        │                  │   Server         │                    │   (whatsmeow)   │
│                 │──────────────────►│                  │────────────────────►│                 │
└─────────────────┘                  └──────────────────┘                    └─────────────────┘
                                              │                                         │
                                              │                                         │
                                              ▼                                         ▼
                                     ┌──────────────────┐                    ┌─────────────────┐
                                     │   Direct SQLite  │                    │   SQLite Store  │
                                     │   Database       │                    │   (Messages &   │
                                     │   Access         │                    │   WhatsApp DB)  │
                                     └──────────────────┘                    └─────────────────┘
```

### Component Responsibilities

#### Go Bridge (`whatsapp-bridge/`)
- **Primary Purpose**: Interface with WhatsApp's web API
- **Key Responsibilities**:
  - WhatsApp authentication and session management
  - Real-time message synchronization
  - Media download/upload handling
  - Database schema management
  - Message persistence in SQLite

#### Python MCP Server (`whatsapp-mcp-server/`)
- **Primary Purpose**: Expose WhatsApp functionality via MCP protocol
- **Key Responsibilities**:
  - MCP tool definitions and handlers
  - Direct SQLite database queries (for read operations)
  - HTTP requests to Go bridge (for write operations)
  - Audio file format conversion (with FFmpeg)
  - Error handling and validation

## Development Setup

### Prerequisites

- Go 1.19+ (for WhatsApp bridge)
- Python 3.8+ (for MCP server)
- UV package manager
- SQLite3
- FFmpeg (optional, for audio conversion)

### Setting Up Development Environment

1. **Clone and setup the repository**:
   ```bash
   git clone https://github.com/lharries/whatsapp-mcp.git
   cd whatsapp-mcp
   ```

2. **Setup Go bridge for development**:
   ```bash
   cd whatsapp-bridge
   go mod download
   go run main.go
   ```

3. **Setup Python MCP server for development**:
   ```bash
   cd whatsapp-mcp-server
   uv venv
   source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
   uv sync
   python main.py
   ```

### Database Schema

The system uses two SQLite databases:

#### 1. WhatsApp Database (`whatsapp-bridge/store/whatsapp.db`)
Managed by the whatsmeow library for session data and contacts.

#### 2. Messages Database (`whatsapp-bridge/store/messages.db`)
Custom schema for message storage:

```sql
-- Chats table
CREATE TABLE chats (
    jid TEXT PRIMARY KEY,
    name TEXT,
    type TEXT, -- 'individual', 'group', 'broadcast'
    created_at INTEGER,
    last_message_time INTEGER,
    unread_count INTEGER DEFAULT 0,
    participants_count INTEGER DEFAULT 1
);

-- Messages table
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    chat_jid TEXT,
    sender_jid TEXT,
    content TEXT,
    timestamp INTEGER,
    message_type TEXT, -- 'text', 'image', 'video', 'audio', 'document'
    media_url TEXT,
    media_mime_type TEXT,
    media_file_sha256 TEXT,
    media_file_length INTEGER,
    reply_to_message_id TEXT,
    FOREIGN KEY (chat_jid) REFERENCES chats (jid)
);

-- Contacts table
CREATE TABLE contacts (
    jid TEXT PRIMARY KEY,
    name TEXT,
    phone TEXT,
    business_name TEXT,
    push_name TEXT
);
```

## Extending the System

### Adding New MCP Tools

To add a new MCP tool to the Python server:

1. **Define the tool schema** in `main.py`:
   ```python
   # Add to the tools list
   tools.append({
       "name": "your_new_tool",
       "description": "Description of what your tool does",
       "inputSchema": {
           "type": "object",
           "properties": {
               "param1": {"type": "string", "description": "Parameter description"},
               "param2": {"type": "integer", "description": "Another parameter"}
           },
           "required": ["param1"]
       }
   })
   ```

2. **Implement the tool handler** in `main.py`:
   ```python
   async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
       # Add your tool case
       elif name == "your_new_tool":
           return await handle_your_new_tool(arguments)
   
   async def handle_your_new_tool(arguments: dict) -> List[TextContent]:
       param1 = arguments.get("param1")
       param2 = arguments.get("param2", default_value)
       
       # Your implementation here
       result = your_logic(param1, param2)
       
       return [TextContent(type="text", text=json.dumps(result))]
   ```

3. **Add database operations** if needed in `whatsapp.py`:
   ```python
   def your_database_operation(self, param1: str) -> List[dict]:
       query = "SELECT * FROM your_table WHERE field = ?"
       cursor = self.conn.execute(query, (param1,))
       return [dict(row) for row in cursor.fetchall()]
   ```

### Adding New Go Bridge Endpoints

To add new functionality to the Go bridge:

1. **Define the endpoint** in `main.go`:
   ```go
   http.HandleFunc("/api/your-endpoint", handleYourEndpoint)
   ```

2. **Implement the handler**:
   ```go
   func handleYourEndpoint(w http.ResponseWriter, r *http.Request) {
       if r.Method != http.MethodPost {
           http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
           return
       }
       
       var req YourRequestStruct
       if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
           http.Error(w, "Invalid JSON", http.StatusBadRequest)
           return
       }
       
       // Your implementation
       result, err := yourLogic(req)
       if err != nil {
           http.Error(w, err.Error(), http.StatusInternalServerError)
           return
       }
       
       w.Header().Set("Content-Type", "application/json")
       json.NewEncoder(w).Encode(result)
   }
   ```

### Database Migrations

When modifying the database schema:

1. **Add migration logic** to the Go bridge initialization
2. **Update the database version** tracking
3. **Ensure backward compatibility** where possible

Example migration:
```go
func migrateDatabase() error {
    version := getCurrentDBVersion()
    
    if version < 2 {
        // Apply migration for version 2
        _, err := db.Exec("ALTER TABLE messages ADD COLUMN new_field TEXT")
        if err != nil {
            return err
        }
        setDBVersion(2)
    }
    
    return nil
}
```

## Testing

### Unit Tests

For Python components:
```bash
cd whatsapp-mcp-server
uv run pytest tests/
```

For Go components:
```bash
cd whatsapp-bridge
go test ./...
```

### Integration Testing

Test the full system:
```bash
# Start the Go bridge
cd whatsapp-bridge && go run main.go &

# Test MCP server endpoints
cd whatsapp-mcp-server
uv run python test_integration.py
```

### Manual Testing with MCP Inspector

Use the MCP Inspector tool for manual testing:
```bash
npx @modelcontextprotocol/inspector uv --directory whatsapp-mcp-server run main.py
```

## Performance Considerations

### Database Optimization

1. **Indexing**: Add indexes for frequently queried fields:
   ```sql
   CREATE INDEX idx_messages_chat_timestamp ON messages(chat_jid, timestamp);
   CREATE INDEX idx_messages_content ON messages(content) WHERE message_type = 'text';
   ```

2. **Query Optimization**: Use LIMIT and proper WHERE clauses
3. **Connection Pooling**: Reuse database connections

### Memory Management

1. **Go Bridge**: Monitor goroutine usage and memory leaks
2. **Python Server**: Use async/await properly to avoid blocking
3. **Large Media**: Stream large files instead of loading into memory

### Rate Limiting

Implement rate limiting for WhatsApp API calls:
```go
type RateLimiter struct {
    requests chan struct{}
    ticker   *time.Ticker
}

func NewRateLimiter(requestsPerSecond int) *RateLimiter {
    return &RateLimiter{
        requests: make(chan struct{}, requestsPerSecond),
        ticker:   time.NewTicker(time.Second / time.Duration(requestsPerSecond)),
    }
}
```

## Security Best Practices

### Authentication & Authorization

1. **Secure Session Storage**: WhatsApp session tokens are sensitive
2. **Local-Only Access**: MCP server should only accept local connections
3. **Input Validation**: Validate all user inputs to prevent injection attacks

### Data Protection

1. **Database Encryption**: Consider encrypting the SQLite databases
2. **Media File Security**: Secure downloaded media files
3. **Logging**: Avoid logging sensitive information

## Debugging

### Common Issues

1. **Database Locked Errors**:
   ```go
   // Use WAL mode for better concurrency
   db.Exec("PRAGMA journal_mode=WAL")
   ```

2. **WhatsApp Disconnection**:
   - Check session validity
   - Implement reconnection logic
   - Monitor connection events

3. **Media Download Failures**:
   - Verify media URLs are still valid
   - Check file permissions
   - Handle network timeouts

### Logging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

```go
import "log"
log.SetFlags(log.LstdFlags | log.Lshortfile)
```

## Contributing Guidelines

### Code Style

- **Go**: Follow `gofmt` and `golint` standards
- **Python**: Follow PEP 8, use `black` for formatting
- **Comments**: Document public functions and complex logic

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request with clear description

### Versioning

This project follows semantic versioning:
- **Major**: Breaking API changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

## Deployment Considerations

### Production Setup

1. **Process Management**: Use systemd or similar for the Go bridge
2. **Monitoring**: Set up health checks and alerting
3. **Backup**: Regular database backups
4. **Updates**: Plan for seamless updates without losing WhatsApp sessions

### Docker Support

Example Dockerfile:
```dockerfile
# Multi-stage build
FROM golang:1.19 AS go-builder
WORKDIR /app/whatsapp-bridge
COPY whatsapp-bridge/ .
RUN go build -o bridge main.go

FROM python:3.9
WORKDIR /app
COPY --from=go-builder /app/whatsapp-bridge/bridge /app/
COPY whatsapp-mcp-server/ ./whatsapp-mcp-server/
RUN pip install uv && cd whatsapp-mcp-server && uv sync
```

## Future Roadmap

### Planned Features

- [ ] End-to-end encryption for local storage
- [ ] Multi-account support
- [ ] Advanced message search with full-text indexing
- [ ] Webhook support for real-time notifications
- [ ] Web interface for administration
- [ ] Plugin system for custom message handlers

### Performance Improvements

- [ ] Database connection pooling
- [ ] Caching layer for frequently accessed data
- [ ] Async message processing
- [ ] Batch operations for bulk actions

This developer guide should help you understand the codebase and contribute effectively to the WhatsApp MCP project.