# Implementation Plan: MoinMoin CLI with WikiRPC v2

## Overview
Implementation roadmap for the `moin` CLI tool based on WikiRPC v2 standard, featuring token-based authentication, server management, and MCP integration.

## Architecture Overview

### Core Components
```
moin_cli/
├── __init__.py              # Package initialization
├── main.py                  # CLI entry point and command routing
├── client/                  # WikiRPC v2 client implementation
│   ├── __init__.py
│   ├── xmlrpc_client.py     # Core XML-RPC client
│   ├── auth.py              # Authentication management
│   └── exceptions.py        # Custom exceptions
├── config/                  # Configuration management
│   ├── __init__.py
│   ├── manager.py           # Configuration file handling
│   ├── models.py            # Configuration data models
│   └── defaults.py          # Default settings
├── commands/                # CLI command implementations
│   ├── __init__.py
│   ├── server.py            # Server management commands
│   ├── pages.py             # Page operations (read/write/list/search)
│   ├── auth.py              # Authentication commands
│   └── config.py            # Configuration commands
├── mcp/                     # MCP server implementation
│   ├── __init__.py
│   ├── server.py            # MCP server
│   └── tools.py             # MCP tools for Claude Code
└── utils/                   # Utility functions
    ├── __init__.py
    ├── security.py          # Token encryption, secure input
    ├── output.py            # Output formatting
    └── errors.py            # Error handling
```

## Phase 1: Core Foundation (Week 1)

### 1.1 Project Structure Setup
- [x] Basic package structure
- [ ] Update pyproject.toml dependencies
- [ ] Configuration directory creation
- [ ] Basic CLI framework with Click

### 1.2 Configuration System
```python
# moin_cli/config/models.py
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ServerConfig(BaseModel):
    name: str
    url: str
    username: str
    access_token: Optional[str] = None
    token_expires: Optional[datetime] = None
    verify_ssl: bool = True
    timeout: int = 30

class Settings(BaseModel):
    default_server: Optional[str] = None
    format: str = "markdown"
    cache_enabled: bool = True

class Config(BaseModel):
    settings: Settings
    servers: Dict[str, ServerConfig]
```

### 1.3 Basic WikiRPC v2 Client
```python
# moin_cli/client/xmlrpc_client.py
import xmlrpc.client
from typing import List, Optional
from .exceptions import AuthenticationError, ConnectionError

class WikiRPCClient:
    def __init__(self, url: str, verify_ssl: bool = True, timeout: int = 30):
        self.url = url
        self.server = xmlrpc.client.ServerProxy(
            f"{url}?action=xmlrpc2",
            timeout=timeout
        )
        self.token = None
    
    def get_auth_token(self, username: str, password: str) -> str:
        """Get authentication token from server"""
        return self.server.getAuthToken(username, password)
    
    def apply_auth_token(self, token: str) -> None:
        """Apply authentication token for session"""
        self.token = token
        self.server.applyAuthToken(token)
    
    def get_all_pages(self) -> List[str]:
        """Get list of all pages"""
        return self.server.getAllPages()
    
    def get_page(self, pagename: str) -> str:
        """Get page content"""
        return self.server.getPage(pagename)
    
    def put_page(self, pagename: str, content: str) -> bool:
        """Update page content (requires authentication)"""
        if not self.token:
            raise AuthenticationError("Authentication required for write operations")
        return self.server.putPage(pagename, content)
    
    def search_pages(self, query: str) -> List[str]:
        """Search for pages"""
        return self.server.searchPages(query)
```

## Phase 2: Authentication System (Week 2)

### 2.1 Token Management
```python
# moin_cli/client/auth.py
import getpass
import os
from typing import Tuple, Optional
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def get_credentials(self, username: str = None) -> Tuple[str, str]:
        """Get username and password securely"""
        if not username:
            username = input("Username: ")
        
        # Try environment variable first
        password = os.getenv(f'MOIN_PASSWORD_{username.upper()}')
        if not password:
            password = getpass.getpass(f"Password for {username}: ")
        
        return username, password
    
    def authenticate_server(self, server_name: str) -> str:
        """Authenticate to server and return token"""
        server_config = self.config_manager.get_server(server_name)
        client = WikiRPCClient(server_config.url)
        
        username, password = self.get_credentials(server_config.username)
        token = client.get_auth_token(username, password)
        
        # Save token to config
        server_config.access_token = token
        server_config.token_expires = datetime.now() + timedelta(hours=24)
        self.config_manager.save_server(server_name, server_config)
        
        return token
```

### 2.2 Server Management Commands
```python
# moin_cli/commands/server.py
import click
from ..config.manager import ConfigManager
from ..client.auth import AuthManager

@click.group()
def server():
    """Server management commands"""
    pass

@server.command()
@click.argument('name')
@click.option('--url', required=True, help='Wiki server URL')
@click.option('--username', help='Username for authentication')
def add(name: str, url: str, username: str):
    """Add a new wiki server"""
    config_manager = ConfigManager()
    auth_manager = AuthManager(config_manager)
    
    if not username:
        username = input("Username: ")
    
    # Test authentication
    try:
        token = auth_manager.authenticate_server_new(name, url, username)
        click.echo(f"✓ Successfully added server '{name}'")
    except Exception as e:
        click.echo(f"✗ Failed to add server: {e}")

@server.command()
def list():
    """List all configured servers"""
    config_manager = ConfigManager()
    servers = config_manager.list_servers()
    
    if not servers:
        click.echo("No servers configured")
        return
    
    # Format output table
    for name, config in servers.items():
        status = "active" if config.access_token else "not authenticated"
        click.echo(f"{name:15} {config.url:40} {config.username:15} {status}")
```

## Phase 3: Core Commands (Week 3)

### 3.1 Page Operations
```python
# moin_cli/commands/pages.py
import click
from ..config.manager import ConfigManager
from ..client.xmlrpc_client import WikiRPCClient

@click.command()
@click.argument('pagename')
@click.option('--server', help='Server name')
@click.option('--format', type=click.Choice(['raw', 'markdown', 'html']), default='raw')
def read(pagename: str, server: str, format: str):
    """Read a wiki page"""
    config_manager = ConfigManager()
    server_config = config_manager.get_active_server(server)
    
    client = WikiRPCClient(server_config.url)
    if server_config.access_token:
        client.apply_auth_token(server_config.access_token)
    
    try:
        content = client.get_page(pagename)
        if format == 'raw':
            click.echo(content)
        elif format == 'markdown':
            # Convert to markdown if needed
            click.echo(content)
        elif format == 'html':
            # Convert to HTML if needed
            click.echo(content)
    except Exception as e:
        click.echo(f"Error reading page: {e}")

@click.command()
@click.argument('pagename')
@click.option('--server', help='Server name')
@click.option('--content', help='Page content')
@click.option('--file', type=click.File('r'), help='Read content from file')
def write(pagename: str, server: str, content: str, file):
    """Write to a wiki page"""
    if not content and not file:
        # Open editor
        content = click.edit() or ""
    elif file:
        content = file.read()
    
    config_manager = ConfigManager()
    server_config = config_manager.get_active_server(server)
    
    client = WikiRPCClient(server_config.url)
    if not server_config.access_token:
        click.echo("Authentication required. Run 'moin login' first.")
        return
    
    client.apply_auth_token(server_config.access_token)
    
    try:
        result = client.put_page(pagename, content)
        if result:
            click.echo(f"✓ Page '{pagename}' updated successfully")
        else:
            click.echo(f"✗ Failed to update page '{pagename}'")
    except Exception as e:
        click.echo(f"Error writing page: {e}")
```

### 3.2 Search and List
```python
@click.command()
@click.option('--server', help='Server name')
@click.option('--pattern', help='Filter pattern')
def list_pages(server: str, pattern: str):
    """List all pages"""
    config_manager = ConfigManager()
    server_config = config_manager.get_active_server(server)
    
    client = WikiRPCClient(server_config.url)
    
    try:
        pages = client.get_all_pages()
        if pattern:
            import fnmatch
            pages = [p for p in pages if fnmatch.fnmatch(p, pattern)]
        
        for page in sorted(pages):
            click.echo(page)
    except Exception as e:
        click.echo(f"Error listing pages: {e}")

@click.command()
@click.argument('query')
@click.option('--server', help='Server name')
def search(query: str, server: str):
    """Search for pages"""
    config_manager = ConfigManager()
    server_config = config_manager.get_active_server(server)
    
    client = WikiRPCClient(server_config.url)
    
    try:
        results = client.search_pages(query)
        for page in results:
            click.echo(page)
    except Exception as e:
        click.echo(f"Error searching: {e}")
```

## Phase 4: MCP Integration (Week 4)

### 4.1 MCP Server Implementation
```python
# moin_cli/mcp/server.py
from mcp import McpServer
from mcp.types import Tool, TextContent

class MoinMCPServer(McpServer):
    def __init__(self, config_manager):
        super().__init__("moin-wiki")
        self.config_manager = config_manager
    
    @self.tool()
    async def read_page(self, pagename: str, server: str = None) -> str:
        """Read a wiki page"""
        server_config = self.config_manager.get_active_server(server)
        client = WikiRPCClient(server_config.url)
        
        if server_config.access_token:
            client.apply_auth_token(server_config.access_token)
        
        return client.get_page(pagename)
    
    @self.tool()
    async def write_page(self, pagename: str, content: str, server: str = None) -> bool:
        """Write to a wiki page"""
        server_config = self.config_manager.get_active_server(server)
        client = WikiRPCClient(server_config.url)
        
        if not server_config.access_token:
            raise Exception("Authentication required")
        
        client.apply_auth_token(server_config.access_token)
        return client.put_page(pagename, content)
    
    @self.tool()
    async def search_pages(self, query: str, server: str = None) -> list:
        """Search for pages"""
        server_config = self.config_manager.get_active_server(server)
        client = WikiRPCClient(server_config.url)
        return client.search_pages(query)
```

### 4.2 MCP Server Command
```python
# In main.py
@main.command()
@click.option('--host', default='localhost', help='Server host')
@click.option('--port', default=8000, help='Server port')
@click.option('--server', help='Default wiki server')
def serve(host: str, port: int, server: str):
    """Start MCP server for Claude Code"""
    config_manager = ConfigManager()
    mcp_server = MoinMCPServer(config_manager)
    
    click.echo(f"Starting MCP server on {host}:{port}")
    if server:
        click.echo(f"Using default server: {server}")
    
    mcp_server.run(host=host, port=port)
```

## Phase 5: Enhanced Features (Week 5)

### 5.1 Error Handling and Retry Logic
- Connection retry with exponential backoff
- Token refresh on authentication errors
- User-friendly error messages
- Detailed logging for debugging

### 5.2 Output Formatting
- JSON output option for scripting
- Rich text formatting for terminal
- Progress bars for long operations
- Configurable output formats

### 5.3 Caching System
- Optional page content caching
- Cache invalidation strategies
- Performance improvements for repeated operations

## Testing Strategy

### Unit Tests
```python
# tests/test_client.py
import pytest
from moin_cli.client.xmlrpc_client import WikiRPCClient

def test_client_initialization():
    client = WikiRPCClient("http://example.com")
    assert client.url == "http://example.com"

@pytest.mark.integration
def test_authentication_flow():
    # Integration test with mock server
    pass
```

### Integration Tests
- Mock WikiRPC v2 server for testing
- Authentication flow testing
- Configuration management testing
- CLI command testing

### Manual Testing
- Real MoinMoin server testing
- Cross-platform compatibility
- Performance testing

## Deployment and Distribution

### Package Distribution
- PyPI package publishing
- Standalone executable builds
- Docker container option

### Documentation
- User manual with examples
- API documentation
- Configuration reference
- Troubleshooting guide

## Timeline Summary

- **Week 1**: Foundation and basic structure
- **Week 2**: Authentication and server management
- **Week 3**: Core page operations
- **Week 4**: MCP integration
- **Week 5**: Polish and advanced features

## Dependencies Update

```toml
dependencies = [
    "click>=8.0.0",
    "pydantic>=2.0.0",
    "rich>=13.0.0",
    "toml>=0.10.0",
    "mcp>=1.0.0",
    "keyring>=24.0.0",  # For secure token storage
    "cryptography>=41.0.0",  # For token encryption
]
```

This implementation plan provides a structured approach to building the MoinMoin CLI with WikiRPC v2 support, focusing on security, usability, and extensibility.