# WhatsApp MCP Complete Documentation

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Core Features](#core-features)
- [Automation Systems](#automation-systems)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Testing & Validation](#testing--validation)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)
- [File Structure](#file-structure)

---

## 🚀 Project Overview

**WhatsApp MCP** is a comprehensive Model Context Protocol (MCP) server that enables AI assistants (like Claude) to interact with your personal WhatsApp account. The system consists of multiple components working together to provide seamless WhatsApp integration with advanced automation and monitoring capabilities.

### Key Capabilities
- 🔍 **Search & Read Messages**: Access your WhatsApp message history, including media files
- 👥 **Contact Management**: Search contacts and manage conversations
- 📱 **Send Messages & Media**: Send text, images, videos, documents, and voice messages
- 🤖 **Automated Analysis**: Real-time group sentiment analysis and monitoring
- 📊 **Business Intelligence**: Automated reporting for team communication insights
- 🔄 **Robust Monitoring**: Self-healing systems with automatic failure recovery

---

## 🏗️ Architecture

The system consists of four main components:

### 1. **WhatsApp Bridge** (`whatsapp-bridge/`)
- **Language**: Go
- **Purpose**: Connects to WhatsApp Web API using whatsmeow library
- **Features**: 
  - QR code authentication
  - Message storage in SQLite
  - REST API server on port 8080
  - Automatic reconnection handling
  - Media download/upload capabilities

### 2. **MCP Server** (`whatsapp-mcp-server/`)
- **Language**: Python
- **Purpose**: Implements Model Context Protocol for AI integration
- **Features**:
  - Standardized tool interface for Claude/Cursor
  - Message search and retrieval
  - Contact management
  - Media handling with FFmpeg support

### 3. **Automation Engine**
- **Components**: Multiple shell and Python scripts
- **Purpose**: Automated group analysis and reporting
- **Features**:
  - Scheduled CRON jobs (3x daily)
  - Intelligent sentiment analysis
  - Automatic report generation
  - Business intelligence insights

### 4. **Monitoring & Recovery Systems**
- **Components**: Health checks, log monitoring, and self-healing scripts
- **Purpose**: Ensure system reliability and uptime
- **Features**:
  - Real-time health monitoring
  - Automatic failure recovery
  - Comprehensive logging
  - Performance metrics

---

## 🛠️ Installation & Setup

### Prerequisites
- **Go** (latest version)
- **Python 3.6+** 
- **UV** (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **FFmpeg** (optional, for audio conversion)
- **Claude Desktop** or **Cursor** IDE
- **SQLite3**

### Step 1: Clone and Setup
```bash
git clone <your-repo-url>
cd whatsapp-mcp-2
chmod +x *.sh
```

### Step 2: Start WhatsApp Bridge
```bash
cd whatsapp-bridge
go run main.go
```
- Scan QR code with WhatsApp mobile app
- Wait for message history sync (may take several minutes)

### Step 3: Configure MCP Integration

**For Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/whatsapp-mcp-2/whatsapp-mcp-server",
        "run",
        "main.py"
      ]
    }
  }
}
```

**For Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "/path/to/uv",
      "args": [
        "--directory", 
        "/path/to/whatsapp-mcp-2/whatsapp-mcp-server",
        "run",
        "main.py"
      ]
    }
  }
}
```

### Step 4: Setup Automation (Optional)
```bash
./setup_cron.sh
```
This configures automated analysis reports for business groups.

---

## ⚡ Core Features

### Message Operations
- **Search Messages**: Find specific conversations or content
- **Message Context**: Get conversation threads around specific messages
- **Media Downloads**: Access shared images, videos, documents, and audio
- **Real-time Sync**: Automatic message synchronization

### Communication Tools
- **Send Text Messages**: To individuals or groups
- **Send Media Files**: Images, videos, documents
- **Send Voice Messages**: Audio files as WhatsApp voice notes
- **Group Management**: Find and interact with group chats

### Contact Management
- **Search Contacts**: By name or phone number
- **Contact History**: View interaction history
- **Direct Chats**: Quick access to one-on-one conversations

---

## 🤖 Automation Systems

### Automated Group Analysis
The system provides intelligent analysis of business communication groups:

#### **Schedule**: 3 times daily
- 🌅 **10:00 AM IST** - Morning analysis
- 🌆 **02:00 PM IST** - Afternoon analysis  
- 🌙 **06:00 PM IST** - Evening analysis

#### **Analysis Features**
- **Sentiment Analysis**: Identifies customer satisfaction levels
- **Issue Detection**: Flags potential problems requiring attention
- **Trend Analysis**: Tracks communication patterns over time
- **Categorization**: Groups classified as:
  - 🚨 **Needs Attention** (critical issues detected)
  - ⚠️ **At Risk** (monitoring required)
  - ✅ **Stable** (healthy communication)

#### **Dynamic Analysis Engine** (`dynamic_analysis.py`)
- **Real-time Data**: Analyzes actual WhatsApp conversations
- **Contextual Timing**: Different analysis windows based on time of day
- **Sentiment Scoring**: Advanced keyword-based sentiment analysis
- **Business Intelligence**: Actionable insights for team management

### Automation Scripts

| Script | Purpose | Features |
|--------|---------|----------|
| `automated_analysis.sh` | Main automation wrapper | Retry logic, connection monitoring, comprehensive logging |
| `send_to_whatsapp_group.py` | Message delivery system | Smart retry, error handling, fallback analysis |
| `setup_cron.sh` | CRON configuration | Automated scheduling setup |

---

## 📊 Monitoring & Maintenance

### Health Monitoring System

#### **Real-time Monitoring** (`monitor_logs.sh`)
Interactive monitoring interface with options:
1. View today's logs
2. Follow live log updates
3. Check CRON job status
4. Review recent execution history
5. Test manual execution
6. Manage automation settings

#### **System Health Checks** (`check_system_status.sh`)
- WhatsApp bridge connectivity
- Database integrity
- API responsiveness
- Process monitoring

#### **Bridge Monitoring** (`bridge_monitor.sh`)
- Automatic restart on failures
- Connection status validation
- Process health verification

### Log Management
- **Daily Rotation**: New log file each day (`logs/analysis_YYYYMMDD.log`)
- **Structured Logging**: Timestamped entries with status indicators
- **Error Tracking**: Detailed failure analysis and recovery steps
- **Performance Metrics**: Execution times and success rates

### Recovery Systems

#### **Automatic Recovery Features**
- **Connection Retry**: Up to 3 attempts with exponential backoff
- **Bridge Restart**: Automatic service recovery
- **Message Retry**: Smart retry logic for failed deliveries
- **Timeout Handling**: Robust timeout management with context switching

#### **Self-Healing Capabilities**
- **Database Corruption Recovery** (`fix_database_corruption.py`)
- **Timeout Fix Implementation** (automatic retry with exponential backoff)
- **Connection Refresh**: Periodic device synchronization
- **Process Monitoring**: Automatic restart of failed services

---

## 🧪 Testing & Validation

### Test Suite
| Test Script | Purpose |
|-------------|---------|
| `test_whatsapp_bridge_health.py` | Bridge connectivity and API functionality |
| `test_timeout_fixes.py` | Timeout handling and retry mechanisms |
| `test_database_corruption.py` | Database integrity and recovery |

### Manual Testing Commands
```bash
# Test bridge connectivity
curl -s http://localhost:8080/api/status

# Test automation pipeline
./automated_analysis.sh

# Test message sending
python3 send_to_whatsapp_group.py

# Monitor real-time logs
./monitor_logs.sh
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### **WhatsApp Authentication Issues**
- **QR Code Problems**: Restart bridge, check terminal QR code support
- **Device Limit**: Remove old devices in WhatsApp Settings > Linked Devices
- **Session Expiry**: Re-authenticate after ~20 days

#### **Connection Issues**
- **Bridge Not Responding**: Check if port 8080 is available
- **WhatsApp Disconnected**: Use `./bridge_monitor.sh` for automatic recovery
- **Message Sync Issues**: Delete database files and re-authenticate

#### **Automation Failures**
- **CRON Not Running**: Verify with `crontab -l`
- **Python Dependencies**: Ensure UV is installed and in PATH
- **Permission Issues**: Check script execute permissions

#### **Database Issues**
- **Corruption**: Run `python3 fix_database_corruption.py`
- **Performance**: Regular maintenance with provided scripts
- **Storage**: Monitor disk space in `whatsapp-bridge/store/`

### Recovery Procedures

#### **Complete System Reset**
```bash
# Stop all services
pkill -f whatsapp-bridge

# Clear databases
rm -f whatsapp-bridge/store/*.db

# Restart bridge
cd whatsapp-bridge && go run main.go

# Re-scan QR code and wait for sync
```

#### **Automation Reset**
```bash
# Remove existing CRON jobs
crontab -r

# Reconfigure automation
./setup_cron.sh

# Test automation
./automated_analysis.sh
```

---

## 📚 API Reference

### MCP Tools Available to Claude

#### **Message Operations**
- `search_contacts(query)` - Search contacts by name/phone
- `list_messages(...)` - Retrieve messages with filters and context
- `list_chats(...)` - Get available chats with metadata
- `get_chat(chat_jid)` - Get specific chat information
- `get_message_context(message_id)` - Get conversation context

#### **Communication Tools**
- `send_message(recipient, message)` - Send text messages
- `send_file(recipient, media_path)` - Send media files
- `send_audio_message(recipient, media_path)` - Send voice messages
- `download_media(message_id, chat_jid)` - Download shared media

#### **Contact & Chat Management**
- `get_direct_chat_by_contact(phone)` - Find direct chat by phone number
- `get_contact_chats(jid)` - List all chats involving a contact
- `get_last_interaction(jid)` - Get most recent message with contact

### REST API Endpoints (Bridge)
```
GET  /api/status           - Bridge connection status
POST /api/send            - Send message
POST /api/send-file       - Send media file
POST /api/download-media  - Download media file
```

---

## 📁 File Structure

```
whatsapp-mcp-2/
├── 📊 Core Components
│   ├── whatsapp-bridge/          # Go WhatsApp bridge
│   │   ├── main.go               # Main bridge application
│   │   ├── go.mod/go.sum         # Go dependencies
│   │   └── store/                # SQLite databases
│   └── whatsapp-mcp-server/      # Python MCP server
│       ├── main.py               # MCP tool definitions
│       ├── whatsapp.py           # WhatsApp API wrapper
│       ├── audio.py              # Audio processing utilities
│       └── pyproject.toml        # Python dependencies
│
├── 🤖 Automation Systems
│   ├── automated_analysis.sh     # Main automation wrapper
│   ├── send_to_whatsapp_group.py # Message delivery system
│   ├── dynamic_analysis.py       # Real-time analysis engine
│   └── setup_cron.sh            # CRON configuration
│
├── 🔧 Monitoring & Maintenance
│   ├── monitor_logs.sh           # Interactive log monitoring
│   ├── bridge_monitor.sh         # Bridge health monitoring
│   ├── check_system_status.sh    # System health checks
│   ├── safe_start_whatsapp_bridge.sh  # Safe bridge startup
│   └── start_whatsapp_bridge.sh  # Bridge startup script
│
├── 🧪 Testing & Validation
│   ├── test_whatsapp_bridge_health.py     # Bridge connectivity tests
│   ├── test_timeout_fixes.py             # Timeout handling tests
│   ├── test_database_corruption.py       # Database integrity tests
│   └── fix_database_corruption.py        # Database recovery tool
│
├── 📋 Documentation
│   ├── README.md                 # Main project documentation
│   ├── README_CRON_SETUP.md     # Automation setup guide
│   ├── CRON_FIX_SUMMARY.md      # Automation fixes documentation
│   ├── timeout_fix_summary.md   # Timeout fixes documentation
│   └── PROJECT_DOCUMENTATION.md # This comprehensive guide
│
└── 📝 Operational Files
    ├── logs/                     # Daily log files
    ├── LICENSE                   # Project license
    ├── example-use.png          # Usage demonstration
    ├── whatsapp_bridge.pid      # Process ID file
    └── crontab_backup_*.txt     # CRON configuration backups
```

---

## 🎯 Best Practices

### Development
- Always test changes with the provided test scripts
- Use the monitoring tools for debugging
- Follow the retry and error handling patterns established
- Maintain comprehensive logging

### Operations
- Monitor daily logs for issues
- Keep backups of working CRON configurations
- Test automation manually before deploying changes
- Maintain WhatsApp Web session by regular usage

### Security
- Keep database files secure (contain personal messages)
- Monitor API access and usage
- Regular updates of dependencies
- Backup critical configurations

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- **Daily**: Check logs for errors or unusual patterns
- **Weekly**: Verify automation is running correctly
- **Monthly**: Review system performance and cleanup old logs
- **As Needed**: Update dependencies and security patches

### Getting Help
1. Check the logs in `logs/` directory
2. Run system health checks with provided scripts
3. Test individual components using test scripts
4. Review troubleshooting section for common issues
5. Check existing documentation files for specific topics

---

**🎉 Your WhatsApp MCP system is now fully documented and ready for operation!**

This comprehensive system provides AI-powered WhatsApp automation with robust monitoring, self-healing capabilities, and business intelligence features.
