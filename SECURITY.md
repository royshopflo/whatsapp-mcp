# Security Guide for WhatsApp MCP

This document outlines the security considerations, data protection measures, and best practices for the WhatsApp MCP server. Given that this system handles personal WhatsApp messages and media, security is paramount.

## Security Overview

### Threat Model

The WhatsApp MCP system processes sensitive personal data including:
- Private messages and conversations
- Contact information and phone numbers
- Media files (images, videos, documents, audio)
- WhatsApp authentication tokens and session data

**Primary Threats:**
- **Data Breach**: Unauthorized access to stored messages and media
- **Session Hijacking**: Compromise of WhatsApp authentication
- **Privacy Violation**: Unintended exposure of personal communications
- **Injection Attacks**: Malicious input through MCP tools
- **Local System Compromise**: Access to SQLite databases and session files

### Security Principles

1. **Local-First**: All data is stored and processed locally
2. **Minimal Exposure**: Only requested data is sent to LLMs
3. **User Control**: Users control what data is accessed through MCP tools
4. **Secure Defaults**: Safe configuration out of the box
5. **Defense in Depth**: Multiple layers of security controls

## Data Protection

### Local Data Storage

#### SQLite Database Security

**File Permissions:**
```bash
# Restrict database file access
chmod 600 whatsapp-bridge/store/messages.db
chmod 600 whatsapp-bridge/store/whatsapp.db

# Restrict directory access
chmod 700 whatsapp-bridge/store/
```

**Database Encryption (Recommended):**
Consider implementing SQLite encryption using SQLCipher:

```go
// Example SQLCipher integration
import "github.com/mutecomm/go-sqlcipher/v4"

func openEncryptedDB(path, password string) (*sql.DB, error) {
    db, err := sql.Open("sqlite3", path+"?_pragma_key="+password)
    if err != nil {
        return nil, err
    }
    return db, nil
}
```

#### Session Data Protection

WhatsApp session data contains sensitive authentication tokens:

**Secure Storage:**
- Session files should be readable only by the application user
- Consider encrypting session data at rest
- Implement secure session rotation

**Session File Permissions:**
```bash
# Protect session files
find whatsapp-bridge/store/ -name "*.db" -exec chmod 600 {} \;
find whatsapp-bridge/store/ -name "session*" -exec chmod 600 {} \;
```

### Media File Security

#### Downloaded Media Protection

```go
// Secure media download with proper permissions
func downloadMediaSecurely(mediaPath string) error {
    file, err := os.OpenFile(mediaPath, os.O_CREATE|os.O_WRONLY, 0600)
    if err != nil {
        return err
    }
    defer file.Close()
    
    // Download and write media content
    // ...
    
    return nil
}
```

#### Media File Cleanup

Implement automatic cleanup of temporary media files:

```python
import tempfile
import os
from pathlib import Path

class SecureMediaHandler:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(mode=0o700)
    
    def download_media_securely(self, message_id: str) -> str:
        # Download to secure temporary location
        temp_path = Path(self.temp_dir) / f"media_{message_id}"
        # ... download logic ...
        return str(temp_path)
    
    def cleanup(self):
        # Securely remove temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
```

## Authentication & Access Control

### WhatsApp Authentication

#### QR Code Security

The QR code contains sensitive authentication data:

```go
// Secure QR code handling
func displayQRSecurely(qrCode string) {
    // Clear screen before displaying QR
    fmt.Print("\033[2J\033[H")
    
    // Display QR code
    qrterminal.Generate(qrCode, qrterminal.L, os.Stdout)
    
    // Warn user about QR sensitivity
    fmt.Println("\nWARNING: This QR code contains authentication data.")
    fmt.Println("Do not share or screenshot this QR code.")
    
    // Clear QR after scanning timeout
    time.AfterFunc(60*time.Second, func() {
        fmt.Print("\033[2J\033[H")
        fmt.Println("QR code cleared for security.")
    })
}
```

#### Session Validation

Implement proper session validation:

```go
func validateSession(client *whatsmeow.Client) error {
    if !client.IsConnected() {
        return errors.New("WhatsApp client not connected")
    }
    
    if !client.IsLoggedIn() {
        return errors.New("WhatsApp session expired")
    }
    
    return nil
}
```

### MCP Server Access Control

#### Local-Only Binding

Ensure the MCP server only accepts local connections:

```python
# Bind only to localhost
server = Server("whatsapp-mcp")

# In your server setup
if __name__ == "__main__":
    # Only accept connections from localhost
    server.run(host="127.0.0.1", port=8000)
```

#### Input Validation

Validate all MCP tool inputs:

```python
import re
from typing import Optional

class InputValidator:
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        # Validate international phone number format
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_jid(jid: str) -> bool:
        # Validate WhatsApp JID format
        patterns = [
            r'^[0-9]+@s\.whatsapp\.net$',  # Individual
            r'^[0-9]+-[0-9]+@g\.us$',      # Group
        ]
        return any(re.match(pattern, jid) for pattern in patterns)
    
    @staticmethod
    def sanitize_message_content(content: str) -> str:
        # Remove potentially harmful content
        # Limit message length
        if len(content) > 4096:
            content = content[:4096]
        
        # Remove null bytes and control characters
        content = content.replace('\x00', '').strip()
        return content
```

## Network Security

### HTTPS Communication

For any HTTP communication between components:

```go
// Use TLS for internal communication
func createSecureServer() *http.Server {
    server := &http.Server{
        Addr:         ":8443",
        TLSConfig:    createTLSConfig(),
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }
    return server
}

func createTLSConfig() *tls.Config {
    return &tls.Config{
        MinVersion:               tls.VersionTLS12,
        CurvePreferences:         []tls.CurveID{tls.CurveP521, tls.CurveP384, tls.CurveP256},
        PreferServerCipherSuites: true,
        CipherSuites: []uint16{
            tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
            tls.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305,
            tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
        },
    }
}
```

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
import time
from collections import defaultdict, deque
from typing import Dict, Deque

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        user_requests = self.requests[identifier]
        
        # Remove old requests outside the window
        while user_requests and user_requests[0] < now - self.window_seconds:
            user_requests.popleft()
        
        # Check if under limit
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        
        return False
```

## Privacy Protection

### Data Minimization

Only access and process necessary data:

```python
def search_messages_privacy_aware(
    query: str,
    chat_jid: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """Search messages with privacy protection."""
    
    # Limit search scope
    if limit > 100:
        limit = 100
    
    # Only return essential fields
    query_sql = """
        SELECT id, chat_jid, sender_jid, 
               SUBSTR(content, 1, 200) as content_preview,
               timestamp, message_type
        FROM messages
        WHERE content LIKE ? 
    """
    
    params = [f"%{query}%"]
    
    if chat_jid:
        query_sql += " AND chat_jid = ?"
        params.append(chat_jid)
    
    query_sql += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    # Execute query and return results
    cursor = self.conn.execute(query_sql, params)
    return [dict(row) for row in cursor.fetchall()]
```

### Audit Logging

Implement comprehensive audit logging:

```python
import logging
from datetime import datetime
from typing import Optional

class SecurityAuditLogger:
    def __init__(self, log_file: str = "security_audit.log"):
        self.logger = logging.getLogger("security_audit")
        handler = logging.FileHandler(log_file, mode='a')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_mcp_tool_access(
        self, 
        tool_name: str, 
        arguments: dict,
        user_id: Optional[str] = None
    ):
        # Sanitize sensitive data in arguments
        safe_args = self._sanitize_arguments(arguments)
        
        self.logger.info(
            f"MCP_TOOL_ACCESS - Tool: {tool_name}, "
            f"User: {user_id or 'unknown'}, "
            f"Args: {safe_args}"
        )
    
    def log_whatsapp_action(self, action: str, details: dict):
        safe_details = self._sanitize_arguments(details)
        self.logger.info(
            f"WHATSAPP_ACTION - Action: {action}, "
            f"Details: {safe_details}"
        )
    
    def log_security_event(self, event_type: str, description: str):
        self.logger.warning(
            f"SECURITY_EVENT - Type: {event_type}, "
            f"Description: {description}"
        )
    
    def _sanitize_arguments(self, args: dict) -> dict:
        """Remove sensitive data from logged arguments."""
        sensitive_keys = {'password', 'token', 'session', 'content', 'message'}
        sanitized = {}
        
        for key, value in args.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
```

## Secure Configuration

### Environment Variables

Use environment variables for sensitive configuration:

```bash
# .env file (never commit to version control)
WHATSAPP_DB_ENCRYPTION_KEY=your_secure_key_here
MEDIA_STORAGE_PATH=/secure/path/to/media
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60
```

```python
import os
from pathlib import Path

class SecureConfig:
    def __init__(self):
        self.db_encryption_key = os.getenv('WHATSAPP_DB_ENCRYPTION_KEY')
        self.media_storage_path = Path(os.getenv('MEDIA_STORAGE_PATH', './media'))
        self.mcp_server_port = int(os.getenv('MCP_SERVER_PORT', 8000))
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        if not self.db_encryption_key:
            raise ValueError("DB_ENCRYPTION_KEY environment variable required")
        
        # Ensure media directory exists and is secure
        self.media_storage_path.mkdir(mode=0o700, exist_ok=True)
```

### Secure Defaults

Configure secure defaults in your application:

```python
# Security-first configuration
SECURITY_CONFIG = {
    'max_message_length': 4096,
    'max_file_size': 100 * 1024 * 1024,  # 100MB
    'allowed_media_types': {
        'image/jpeg', 'image/png', 'image/gif',
        'video/mp4', 'video/avi',
        'audio/mpeg', 'audio/ogg',
        'application/pdf', 'text/plain'
    },
    'session_timeout': 30 * 24 * 60 * 60,  # 30 days
    'max_search_results': 100,
    'rate_limit_requests': 10,
    'rate_limit_window': 60,
}
```

## Incident Response

### Security Monitoring

Monitor for security events:

```python
class SecurityMonitor:
    def __init__(self):
        self.failed_auth_attempts = defaultdict(int)
        self.suspicious_activity_threshold = 5
    
    def check_for_threats(self, event_type: str, source: str):
        if event_type == "failed_auth":
            self.failed_auth_attempts[source] += 1
            
            if self.failed_auth_attempts[source] >= self.suspicious_activity_threshold:
                self._handle_security_incident(
                    f"Multiple failed auth attempts from {source}"
                )
    
    def _handle_security_incident(self, description: str):
        # Log the incident
        logging.error(f"SECURITY_INCIDENT: {description}")
        
        # Could implement additional responses:
        # - Send notification
        # - Temporarily block access
        # - Require re-authentication
```

### Breach Response Plan

1. **Immediate Response:**
   - Disconnect from WhatsApp
   - Stop all MCP services
   - Preserve logs and evidence

2. **Assessment:**
   - Determine scope of compromise
   - Identify affected data
   - Assess potential impact

3. **Containment:**
   - Change authentication credentials
   - Rotate encryption keys
   - Update security measures

4. **Recovery:**
   - Restore from secure backups
   - Re-authenticate with WhatsApp
   - Implement additional security controls

## Deployment Security

### Production Hardening

#### System-Level Security

```bash
# Create dedicated user for the application
sudo useradd -r -s /bin/false whatsapp-mcp
sudo mkdir -p /opt/whatsapp-mcp
sudo chown whatsapp-mcp:whatsapp-mcp /opt/whatsapp-mcp
sudo chmod 700 /opt/whatsapp-mcp

# Set up systemd service with security
sudo tee /etc/systemd/system/whatsapp-bridge.service << EOF
[Unit]
Description=WhatsApp MCP Bridge
After=network.target

[Service]
Type=simple
User=whatsapp-mcp
Group=whatsapp-mcp
WorkingDirectory=/opt/whatsapp-mcp/whatsapp-bridge
ExecStart=/opt/whatsapp-mcp/whatsapp-bridge/bridge
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
SystemCallArchitectures=native

[Install]
WantedBy=multi-user.target
EOF
```

#### Container Security

```dockerfile
# Use minimal base image
FROM alpine:3.18

# Create non-root user
RUN addgroup -g 1000 whatsapp && \
    adduser -D -s /bin/sh -u 1000 -G whatsapp whatsapp

# Install minimal dependencies
RUN apk add --no-cache ca-certificates

# Copy application with proper ownership
COPY --chown=whatsapp:whatsapp ./app /app

# Switch to non-root user
USER whatsapp

# Set secure working directory
WORKDIR /app

# Run with minimal privileges
ENTRYPOINT ["./whatsapp-mcp"]
```

## Security Checklist

### Pre-Deployment

- [ ] Database files have restricted permissions (600)
- [ ] Session files are protected
- [ ] Environment variables are configured
- [ ] Audit logging is enabled
- [ ] Rate limiting is implemented
- [ ] Input validation is comprehensive
- [ ] TLS is configured for internal communication
- [ ] Media files are stored securely

### Runtime Security

- [ ] Monitor for failed authentication attempts
- [ ] Check for unusual access patterns
- [ ] Verify session validity regularly
- [ ] Rotate encryption keys periodically
- [ ] Clean up temporary files
- [ ] Monitor disk space and resource usage
- [ ] Review audit logs regularly

### Incident Response

- [ ] Incident response plan is documented
- [ ] Contact information is current
- [ ] Backup and recovery procedures are tested
- [ ] Security monitoring is operational
- [ ] Escalation procedures are defined

## Compliance Considerations

### Data Protection Regulations

Consider compliance with:
- **GDPR** (General Data Protection Regulation)
- **CCPA** (California Consumer Privacy Act)
- **Local privacy laws**

Key requirements:
- User consent for data processing
- Right to data portability
- Right to deletion
- Data minimization
- Security by design

### Implementation Example

```python
class PrivacyCompliance:
    def request_user_consent(self, purpose: str) -> bool:
        """Request user consent for data processing."""
        print(f"This application will process your WhatsApp data for: {purpose}")
        print("Do you consent to this processing? (yes/no)")
        response = input().strip().lower()
        return response in ['yes', 'y']
    
    def export_user_data(self, user_jid: str) -> Dict:
        """Export user's data in portable format."""
        # Implementation for data export
        pass
    
    def delete_user_data(self, user_jid: str) -> bool:
        """Delete all data for a specific user."""
        # Implementation for data deletion
        pass
```

This security guide provides a comprehensive framework for protecting the WhatsApp MCP system and user data. Regular security reviews and updates are essential to maintain protection against evolving threats.