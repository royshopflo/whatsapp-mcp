# WhatsApp MCP Server API Documentation

This document provides detailed information about all the available MCP tools in the WhatsApp MCP server, their parameters, return values, and usage examples.

## Overview

The WhatsApp MCP server exposes a set of tools that allow Claude (or other MCP clients) to interact with your WhatsApp account. These tools are categorized into several groups:

- **Contact Management**: Search and manage your WhatsApp contacts
- **Chat Operations**: List, search, and manage conversations
- **Message Operations**: Send, receive, and search messages
- **Media Handling**: Send and download media files
- **Context Retrieval**: Get conversation context and history

## Contact Management Tools

### search_contacts

Search for contacts by name or phone number.

**Parameters:**
- `query` (string, required): Search term to match against contact names or phone numbers

**Returns:**
- Array of contact objects with:
  - `jid`: Contact's WhatsApp ID
  - `name`: Contact's display name
  - `phone`: Phone number (if available)
  - `business_name`: Business name (if applicable)

**Example:**
```json
{
  "tool": "search_contacts",
  "arguments": {
    "query": "John"
  }
}
```

## Chat Operations

### list_chats

List all available chats with optional filtering and pagination.

**Parameters:**
- `limit` (integer, optional): Maximum number of chats to return (default: 50)
- `offset` (integer, optional): Number of chats to skip (default: 0)
- `filter_type` (string, optional): Filter by chat type ("individual", "group", "broadcast")

**Returns:**
- Array of chat objects with:
  - `jid`: Chat's WhatsApp ID
  - `name`: Chat name or contact name
  - `type`: Chat type (individual/group/broadcast)
  - `last_message_time`: Timestamp of last message
  - `unread_count`: Number of unread messages
  - `participants_count`: Number of participants (for groups)

**Example:**
```json
{
  "tool": "list_chats",
  "arguments": {
    "limit": 20,
    "filter_type": "group"
  }
}
```

### get_chat

Get detailed information about a specific chat.

**Parameters:**
- `chat_jid` (string, required): The chat's WhatsApp ID

**Returns:**
- Chat object with detailed information including participants, settings, and metadata

**Example:**
```json
{
  "tool": "get_chat",
  "arguments": {
    "chat_jid": "1234567890@s.whatsapp.net"
  }
}
```

### get_direct_chat_by_contact

Find a direct chat with a specific contact.

**Parameters:**
- `contact_jid` (string, required): The contact's WhatsApp ID

**Returns:**
- Chat object for the direct conversation with the specified contact

**Example:**
```json
{
  "tool": "get_direct_chat_by_contact",
  "arguments": {
    "contact_jid": "1234567890@s.whatsapp.net"
  }
}
```

### get_contact_chats

List all chats involving a specific contact.

**Parameters:**
- `contact_jid` (string, required): The contact's WhatsApp ID

**Returns:**
- Array of chat objects where the contact is a participant

**Example:**
```json
{
  "tool": "get_contact_chats",
  "arguments": {
    "contact_jid": "1234567890@s.whatsapp.net"
  }
}
```

## Message Operations

### list_messages

Retrieve messages with optional filters and context.

**Parameters:**
- `chat_jid` (string, optional): Filter messages from specific chat
- `limit` (integer, optional): Maximum number of messages to return (default: 50)
- `offset` (integer, optional): Number of messages to skip (default: 0)
- `search_query` (string, optional): Search term to filter messages by content
- `from_timestamp` (integer, optional): Unix timestamp to filter messages from
- `to_timestamp` (integer, optional): Unix timestamp to filter messages to
- `sender_jid` (string, optional): Filter messages from specific sender
- `include_media` (boolean, optional): Include media messages (default: true)
- `message_types` (array, optional): Filter by message types (text, image, video, audio, document)

**Returns:**
- Array of message objects with:
  - `id`: Message ID
  - `chat_jid`: Chat where message was sent
  - `sender_jid`: Message sender's WhatsApp ID
  - `content`: Message content (text or media description)
  - `timestamp`: Message timestamp
  - `message_type`: Type of message (text, image, video, etc.)
  - `media_info`: Media metadata (if applicable)
  - `reply_to`: Referenced message (if it's a reply)

**Example:**
```json
{
  "tool": "list_messages",
  "arguments": {
    "chat_jid": "1234567890@s.whatsapp.net",
    "limit": 20,
    "search_query": "meeting",
    "message_types": ["text"]
  }
}
```

### get_last_interaction

Get the most recent message with a contact.

**Parameters:**
- `contact_jid` (string, required): The contact's WhatsApp ID

**Returns:**
- Last message object exchanged with the specified contact

**Example:**
```json
{
  "tool": "get_last_interaction",
  "arguments": {
    "contact_jid": "1234567890@s.whatsapp.net"
  }
}
```

### get_message_context

Retrieve context around a specific message.

**Parameters:**
- `message_id` (string, required): The message ID
- `chat_jid` (string, required): The chat's WhatsApp ID
- `context_size` (integer, optional): Number of messages before and after (default: 5)

**Returns:**
- Array of message objects providing context around the specified message

**Example:**
```json
{
  "tool": "get_message_context",
  "arguments": {
    "message_id": "msg_123456",
    "chat_jid": "1234567890@s.whatsapp.net",
    "context_size": 10
  }
}
```

### send_message

Send a text message to a specified phone number or group JID.

**Parameters:**
- `recipient` (string, required): Phone number (with country code) or group JID
- `message` (string, required): Text content to send
- `reply_to_message_id` (string, optional): Message ID to reply to

**Returns:**
- Success confirmation with sent message details

**Example:**
```json
{
  "tool": "send_message",
  "arguments": {
    "recipient": "+1234567890",
    "message": "Hello! How are you doing today?"
  }
}
```

## Media Handling

### send_file

Send a file (image, video, raw audio, document) to a specified recipient.

**Parameters:**
- `recipient` (string, required): Phone number (with country code) or group JID
- `file_path` (string, required): Local path to the file to send
- `caption` (string, optional): Caption text for the media
- `reply_to_message_id` (string, optional): Message ID to reply to

**Returns:**
- Success confirmation with sent media details

**Example:**
```json
{
  "tool": "send_file",
  "arguments": {
    "recipient": "+1234567890",
    "file_path": "/path/to/image.jpg",
    "caption": "Check out this photo!"
  }
}
```

### send_audio_message

Send an audio file as a WhatsApp voice message.

**Parameters:**
- `recipient` (string, required): Phone number (with country code) or group JID
- `audio_path` (string, required): Local path to the audio file
- `reply_to_message_id` (string, optional): Message ID to reply to

**Returns:**
- Success confirmation with sent audio message details

**Notes:**
- Audio files should be in `.ogg` Opus format for optimal compatibility
- With FFmpeg installed, other formats (MP3, WAV, etc.) will be automatically converted
- Without FFmpeg, use `send_file` for raw audio files

**Example:**
```json
{
  "tool": "send_audio_message",
  "arguments": {
    "recipient": "+1234567890",
    "audio_path": "/path/to/voice_note.ogg"
  }
}
```

### download_media

Download media from a WhatsApp message and get the local file path.

**Parameters:**
- `message_id` (string, required): The message ID containing the media
- `chat_jid` (string, required): The chat's WhatsApp ID
- `download_path` (string, optional): Custom download directory

**Returns:**
- Object with:
  - `file_path`: Local path to the downloaded file
  - `file_size`: Size of the downloaded file
  - `media_type`: Type of media (image, video, audio, document)
  - `original_filename`: Original filename (if available)

**Example:**
```json
{
  "tool": "download_media",
  "arguments": {
    "message_id": "msg_123456",
    "chat_jid": "1234567890@s.whatsapp.net"
  }
}
```

## Error Handling

All tools return standardized error responses when operations fail:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "details": "Additional error context (optional)"
  }
}
```

Common error codes:
- `CHAT_NOT_FOUND`: Specified chat doesn't exist
- `CONTACT_NOT_FOUND`: Specified contact doesn't exist
- `MESSAGE_NOT_FOUND`: Specified message doesn't exist
- `INVALID_RECIPIENT`: Invalid phone number or JID format
- `FILE_NOT_FOUND`: Specified file path doesn't exist
- `MEDIA_DOWNLOAD_FAILED`: Failed to download media content
- `SEND_FAILED`: Failed to send message or media
- `AUTH_REQUIRED`: WhatsApp authentication required
- `RATE_LIMITED`: Too many requests, please wait

## Usage Tips

1. **Phone Number Format**: Always use international format with country code (e.g., "+1234567890")
2. **Group JIDs**: Group JIDs typically end with "@g.us"
3. **Individual JIDs**: Individual contact JIDs typically end with "@s.whatsapp.net"
4. **Media Files**: Ensure media files exist and are readable before attempting to send
5. **Rate Limiting**: Be mindful of WhatsApp's rate limits when sending multiple messages
6. **Authentication**: Ensure the Go bridge is running and authenticated before using any tools

## Security Considerations

- All WhatsApp data is stored locally in SQLite databases
- Media files are downloaded to local storage
- No data is sent to external services except when explicitly requested through MCP tools
- Authentication tokens are stored securely by the whatsmeow library
- Always verify recipient information before sending messages or media

## Integration Examples

### Searching and Responding to Messages

```python
# Search for recent messages containing "meeting"
messages = list_messages(
    search_query="meeting",
    limit=10,
    from_timestamp=yesterday_timestamp
)

# Find the sender's contact
contact = search_contacts(query=message.sender_jid)

# Send a response
send_message(
    recipient=contact.phone,
    message="I'll be there for the meeting!"
)
```

### Media Workflow

```python
# Download a received image
media_info = download_media(
    message_id="msg_123456",
    chat_jid="1234567890@s.whatsapp.net"
)

# Process the image (your custom logic)
processed_image = process_image(media_info.file_path)

# Send the processed image back
send_file(
    recipient="+1234567890",
    file_path=processed_image,
    caption="Here's the processed version!"
)
```