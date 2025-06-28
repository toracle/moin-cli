# MoinMoin CLI

A Python command-line interface for interacting with MoinMoin wiki servers via XML-RPC, with built-in support for serving as an MCP (Model Context Protocol) server for Claude Code.

## Features

### CLI Client
- Connect to MoinMoin wiki servers via XML-RPC
- Perform wiki operations from the command line
- Read, write, and manage wiki pages
- Search and navigate wiki content
- Batch operations for content management

### MCP Server
- Serve as an MCP server for Claude Code integration
- Provide wiki content access and manipulation tools
- Enable AI-assisted wiki content management
- Support for structured wiki operations

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd moin-cli

# Install dependencies
pip install -e .
```

## Usage

### CLI Mode

```bash
# Connect to a MoinMoin server
moin-cli --server https://wiki.example.com --user username

# Read a page
moin-cli read "PageName"

# Write to a page
moin-cli write "PageName" --content "New content"

# Search pages
moin-cli search "search term"

# List all pages
moin-cli list
```

### MCP Server Mode

```bash
# Start as MCP server
moin-cli serve --mcp

# Configure in Claude Code settings
# Add server configuration pointing to this instance
```

## Configuration

Configuration can be provided via:
- Command line arguments
- Environment variables
- Configuration file (`~/.moin-cli.conf`)

### Environment Variables

- `MOIN_SERVER_URL`: Default MoinMoin server URL
- `MOIN_USERNAME`: Default username for authentication
- `MOIN_PASSWORD`: Default password for authentication

## MCP Integration

When running as an MCP server, moin-cli provides these tools to Claude Code:

- `read_page`: Read content from a wiki page
- `write_page`: Write content to a wiki page
- `search_pages`: Search for pages matching criteria
- `list_pages`: List all available pages
- `get_page_info`: Get metadata about a page

## Requirements

- Python 3.11+
- MoinMoin server with XML-RPC enabled
- Network access to the target MoinMoin server

## Development

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black .
isort .
```

## License

MIT License - see LICENSE file for details

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