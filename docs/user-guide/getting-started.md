# Getting Started

Quick start guide for using the MoinMoin CLI tool.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd moin-cli

# Install dependencies
pip install -e .
```

## First Time Setup

### 1. Add your first server

```bash
# Interactive setup
moin server add work
# You'll be prompted for:
# - URL: https://wiki.company.com/
# - Username: your-username
# - Password: [hidden input]
```

### 2. Set as default

```bash
moin server set-default work
```

### 3. Test connection

```bash
moin server test work
```

## Basic Usage

### Read a page
```bash
moin get HomePage
```

### Edit a page
```bash
# Write content directly
moin put MyPage "This is the new page content"

# Or write from file
moin put MyPage --file content.txt
```

### Search pages
```bash
moin search "documentation"
```

### List all pages
```bash
moin list
```

## Multiple Servers

You can configure multiple wiki servers:

```bash
# Add more servers
moin server add personal --url https://mywiki.example.com
moin server add local --url http://localhost:8080

# List all servers
moin server list

# Use specific server
moin get HomePage --server personal
```

## MCP Integration (Claude Code)

Start the MCP server for Claude Code integration:

```bash
# Start MCP server
moin serve

# Or with specific settings
moin serve --host localhost --port 8000 --server work
```

Then configure Claude Code to connect to this MCP server.

## Next Steps

- See [Commands](commands.md) for complete command reference
- See [Configuration](configuration.md) for advanced configuration options
- Check [Architecture](../developer/architecture.md) for technical details

## Need Help?

```bash
# Show command help
moin --help
moin server --help

# Check authentication status
moin auth status

# Test server connection
moin server test work --verbose
```
