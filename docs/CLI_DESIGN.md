# CLI Design Specification

## Executable Name
- **Binary name**: `moin`
- **Package name**: `moin-cli` (for PyPI)

## Command Structure

### Basic Pattern
```bash
moin <command> [arguments] [options]
```

### Core Commands

#### Read Operations
```bash
# Read a page from default wiki
moin get PageName

# Read a page from specific wiki
moin get PageName --wiki wikiname

# Read with output formatting
moin get PageName --format raw|markdown|html
```

#### Write Operations
```bash
# Write to a page (interactive editor)
moin put PageName

# Write from file
moin put PageName --file content.txt

# Write from stdin
echo "content" | moin put PageName

# Write to specific wiki
moin put PageName --wiki wikiname
```

#### List Operations
```bash
# List all pages
moin list

# List pages with pattern
moin list --pattern "HomePage*"

# List from specific wiki
moin list --wiki wikiname
```

#### Search Operations
```bash
# Search pages
moin search "search term"

# Search with regex
moin search --regex "pattern"

# Search in specific wiki
moin search "term" --wiki wikiname
```

#### Server Management Commands
```bash
# Add new server with authentication
moin server add work --url https://wiki.company.com
# Prompts for username/password, stores access token

# List all configured servers
moin server list

# Show server details (mask auth token)
moin server show work

# Remove server configuration
moin server remove work

# Update server settings
moin server update work --url https://newwiki.company.com

# Set default server
moin server set-default work

# Test server connection
moin server test work

# Login to server (get new token)
moin server login work

# Login to default server
moin server login

# Logout from server (remove token)
moin server logout work

# Logout from all servers
moin server logout --all

# Check authentication status
moin server auth status

# Show token information (mask auth token)
moin server auth show work

# Show token information
moin server auth show work --show-credentials
```

#### Configuration Commands
```bash
# Show current configuration
moin config show

# Show configuration file location
moin config locate

# Validate configuration
moin config validate
```

#### MCP Server Commands
```bash
# Start MCP server
moin serve

# Start with specific configuration
moin serve --host 0.0.0.0 --port 8080

# Start with specific wiki
moin serve --wiki wikiname
```

## Global Options

### Server Selection
- `--server SERVERNAME`: Use specific server configuration
- If omitted, uses default server from configuration

### Output Control
- `--format FORMAT`: Output format (raw, markdown, html, json)
- `--quiet`: Suppress informational messages
- `--verbose`: Enable verbose output

### Configuration
- `--config PATH`: Use specific configuration file
- `--no-config`: Don't load configuration file

## Configuration System

### Default Configuration Location
- `~/.moin/config.toml` (main configuration with tokens)

### Environment Variables
- `MOIN_CONFIG`: Path to configuration file
- `MOIN_DEFAULT_SERVER`: Default server name
- `MOIN_SERVER_URL`: Direct server URL (bypasses configuration)
- `MOIN_TOKEN`: Direct access token (for automation)

## Examples

### Daily Usage
```bash
# Quick read from default wiki
moin get HomePage

# Edit a page
moin put Documentation

# Search for content
moin search "installation"

# List recent changes
moin list --recent
```

### Multi-Server Setup
```bash
# Add servers with authentication
moin server add work --url https://work.wiki.com
# Username: john.doe
# Password: [hidden]

moin server add personal --url https://personal.wiki.com
# Username: john
# Password: [hidden]

moin server set-default work

# Use different servers
moin get Project --server work
moin get Notes --server personal
moin get HomePage  # uses default (work)
```

### MCP Integration
```bash
# Start MCP server for Claude Code
moin serve --server work

# Start on specific address
moin serve --host 0.0.0.0 --port 8080 --server personal
```

## Design Principles

1. **Simple default behavior**: `moin get PageName` should "just work"
2. **Explicit when needed**: Use `--wiki` when multiple wikis configured
3. **Consistent patterns**: All commands follow same option patterns
4. **Configuration-driven**: Minimize repetitive typing through good defaults
5. **Pipe-friendly**: Support stdin/stdout for automation
6. **MCP-ready**: Easy transition to MCP server mode

## Implementation Notes

### Command Priority Order
1. Command-line options (`--server servername`)
2. Environment variables (`MOIN_DEFAULT_SERVER`)
3. Configuration file default
4. Error if no server configured

### Error Handling
- Clear error messages for missing configuration
- Helpful suggestions for first-time setup
- Non-zero exit codes for scripting

### Future Extensions
- Plugin system for custom commands
- Batch operations
- Page templates
- Backup/restore operations
