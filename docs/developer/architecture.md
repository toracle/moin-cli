# MoinMoin CLI Architecture

## Overview
The `moin` CLI is built on WikiRPC v2 standard, providing secure token-based authentication and comprehensive server management for MoinMoin wikis.

## System Architecture

### Core Components
```
moin_cli/
├── client/                  # WikiRPC v2 client implementation
│   ├── xmlrpc_client.py     # Core XML-RPC client
│   ├── auth.py              # Authentication management
│   └── exceptions.py        # Custom exceptions
├── config/                  # Configuration management
│   ├── manager.py           # Configuration file handling
│   ├── models.py            # Configuration data models
│   └── defaults.py          # Default settings
├── commands/                # CLI command implementations
│   ├── server.py            # Server management commands
│   ├── pages.py             # Page operations (read/write/list/search)
│   └── config.py            # Configuration commands
├── mcp/                     # MCP server implementation
│   ├── server.py            # MCP server for Claude Code
│   └── tools.py             # MCP tools definition
└── utils/                   # Utility functions
    ├── security.py          # Token encryption, secure input
    ├── output.py            # Output formatting
    └── errors.py            # Error handling
```

## WikiRPC v2 Protocol

### Key Features
- **UTF-8 Native**: Direct UTF-8 string handling without encoding
- **Token Authentication**: Secure session-based authentication
- **Standard XML-RPC**: Compatible with standard XML-RPC libraries

### Endpoint Configuration
- **URL Format**: `http://your-wiki-domain/?action=xmlrpc2`
- **Protocol**: HTTP/HTTPS with POST method
- **Content-Type**: text/xml
- **Encoding**: UTF-8

### Core Methods

#### Page Operations
```python
# Read operations (no auth required)
pages = server.getAllPages()           # List all pages
content = server.getPage("PageName")   # Get page content
results = server.searchPages("term")   # Search pages

# Write operations (authentication required)
server.putPage("PageName", "content") # Update/create page
```

#### Authentication Flow
```python
# 1. Get authentication token
token = server.getAuthToken("username", "password")

# 2. Apply token for session
server.applyAuthToken(token)

# 3. Perform authenticated operations
server.putPage("PageName", "New content")
```

#### Multicall Pattern (Recommended)
```python
# Efficient batch operations
server.system.multicall([
    {'methodName': 'applyAuthToken', 'params': [token]}, 
    {'methodName': 'putPage', 'params': ['PageName', 'Content']}
])
```

## Authentication System

### Token-Based Security

#### Token Characteristics
- **Format**: Server-generated string (implementation-specific)
- **Lifetime**: Server-dependent, may expire
- **Scope**: Per-session, not persistent across client restarts
- **Security**: Treated as sensitive credential

#### Token Management
```python
class AuthManager:
    def get_valid_token(self, server, username, password):
        if self.token and not self.is_expired():
            return self.token
        
        # Re-authenticate
        self.token = server.getAuthToken(username, password)
        self.token_expiry = time.time() + TOKEN_LIFETIME
        return self.token
```

### Security Considerations

#### Password Security
- **Never store passwords** in configuration files
- **Use secure input** (`getpass.getpass()`)
- **Clear from memory** after use
- **Support environment variables** for automation

#### Transport Security
- **Production**: Always use HTTPS
- **Development**: HTTP acceptable for localhost only
- **Certificate validation**: Enabled by default

#### Token Storage
- **File-based**: Persistent with secure permissions (600)
- **In-memory**: Secure but lost on restart
- **Future**: Keyring integration for enhanced security

## Error Handling

### Authentication Errors
```python
def handle_auth_error(server_name, error):
    if "authentication" in str(error).lower():
        print(f"Authentication failed for server '{server_name}'")
        print(f"Run 'moin server login {server_name}' to re-authenticate")
        return False
    return True
```

### Token Expiration
```python
def is_token_expired(error):
    error_msg = str(error).lower()
    return any(keyword in error_msg for keyword in [
        'expired', 'invalid token', 'unauthorized'
    ])
```

### Retry Logic
- Connection retry with exponential backoff
- Automatic token refresh on authentication errors
- Graceful degradation for server unavailability

## MCP Integration

### MCP Server Architecture
The CLI includes an MCP server for Claude Code integration:

```python
class MoinMCPServer(McpServer):
    @self.tool()
    async def read_page(self, pagename: str, server: str = None) -> str:
        """Read a wiki page"""
        # Implementation with authentication handling
    
    @self.tool()
    async def write_page(self, pagename: str, content: str, server: str = None) -> bool:
        """Write to a wiki page"""
        # Implementation with authentication handling
```

### Available Tools
- `read_page`: Read wiki page content
- `write_page`: Update wiki page content
- `search_pages`: Search for pages
- `list_pages`: List all pages

## Performance Considerations

### Optimization Strategies
- **Multicall usage** for batch operations
- **Token caching** to avoid re-authentication
- **Connection pooling** for multiple operations
- **Optional page caching** for frequently accessed content

### Caching System
```python
# Future enhancement
class PageCache:
    def __init__(self, ttl=300):  # 5 minute TTL
        self.cache = {}
        self.ttl = ttl
    
    def get_page(self, server, pagename):
        # Check cache first, then fetch if needed
        pass
```

## Configuration Architecture

### Server Configuration Model
```python
class ServerConfig(BaseModel):
    name: str
    url: str
    username: str
    access_token: Optional[str] = None
    token_expires: Optional[datetime] = None
    verify_ssl: bool = True
    timeout: int = 30
```

### Environment Integration
- `MOIN_TOKEN_{SERVERNAME}`: Server-specific token override
- `MOIN_DEFAULT_SERVER`: Default server selection
- `MOIN_CONFIG`: Configuration file path override

## Future Enhancements

### Planned Features
1. **Enhanced Security**
   - Keyring integration for token storage
   - Certificate-based authentication
   - Multi-factor authentication support

2. **Performance Improvements**
   - Intelligent caching system
   - Connection pooling
   - Batch operation optimization

3. **Extended Protocol Support**
   - WikiRPC v3 when available
   - Alternative authentication methods
   - Extended metadata support

### Scalability Considerations
- Multiple server management
- Concurrent operation support
- Large wiki handling
- Bandwidth optimization

## Integration Points

### Claude Code Integration
- MCP server provides seamless wiki access
- Real-time page editing and reading
- Search functionality for research
- Content management for documentation

### CI/CD Integration
- Environment variable authentication
- Batch operation support
- Non-interactive operation mode
- Exit code standards for scripting

## Standards Compliance

### WikiRPC v2 Compliance
- Full implementation of core methods
- Proper UTF-8 string handling
- Standard XML-RPC error responses
- Multicall support for efficiency

### Security Standards
- No credential storage in configuration
- Secure file permissions
- HTTPS enforcement for production
- Token lifecycle management