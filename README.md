# MoinMoin CLI

A Python command-line interface for interacting with MoinMoin wiki servers via XML-RPC, with built-in support for serving as an MCP (Model Context Protocol) server for Claude Code.

## Features

### CLI Client
- Connect to MoinMoin wiki servers via XML-RPC
- Perform wiki operations from the command line
- Read, write, and manage wiki pages
- Search and navigate wiki content
- Multi-server support with secure token authentication

### MCP Server
- Serve as an MCP server for Claude Code integration
- Provide wiki content access and manipulation tools
- Enable AI-assisted wiki content management
- Support for structured wiki operations

## Quick Start

```bash
# Install
git clone <repository-url>
cd moin-cli
pip install -e .

# Setup your first server
moin server add work --url https://wiki.company.com
moin server set-default work

# Start using
moin get HomePage
moin put Documentation
moin search "installation"
```

## Usage Examples

### Basic Operations
```bash
# Read a page
moin get PageName

# Edit a page (opens editor)
moin put PageName

# Write from file
moin put PageName --file content.txt

# Search pages
moin search "search term"

# List all pages
moin list
```

### Multi-Server Management
```bash
# Add multiple servers
moin server add work --url https://work.wiki.com
moin server add personal --url https://personal.wiki.com

# Use specific server
moin get HomePage --server personal

# List configured servers
moin server list
```

### MCP Server for Claude Code
```bash
# Start MCP server
moin serve

# Or with specific settings
moin serve --host localhost --port 8000 --server work
```

## Configuration

- **Configuration file**: `~/.moin/config.toml`
- **Token-based authentication**: Secure, Azure CLI-like authentication flow
- **Multi-server support**: Manage multiple MoinMoin wiki servers
- **Environment variables**: Support for automation and CI/CD

## Documentation

📖 **[Complete Documentation](docs/README.md)**

### Quick Links
- **[Getting Started](docs/user-guide/getting-started.md)** - Installation and setup
- **[Commands](docs/user-guide/commands.md)** - Complete command reference  
- **[Configuration](docs/user-guide/configuration.md)** - Settings and server management
- **[Architecture](docs/developer/architecture.md)** - Technical design and security

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Roadmap

- [ ] Basic XML-RPC client functionality
- [ ] CLI interface for common operations
- [ ] MCP server implementation
- [ ] Configuration management
- [ ] Authentication handling
- [ ] Batch operations
- [ ] Plugin system for custom operations