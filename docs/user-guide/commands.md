# CLI Reference

## Overview
Complete command reference for the `moin` CLI tool, including all commands, options, and usage examples.

## Command Structure

### Basic Pattern
```bash
moin <command> [arguments] [options]
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

## Core Commands

### Page Operations

#### `moin get <pagename>`
Read a page from the wiki.

```bash
# Read from default server
moin get HomePage

# Read from specific server
moin get PageName --server work

# Read specific version/revision
moin get HomePage --version 5

# Show revision history
moin get HomePage --history

# Output formatting
moin get PageName --format raw|markdown|html|json
```

**Options:**
- `--server SERVERNAME`: Target server
- `--version VERSION`: Specific revision/version number
- `--history`: Show revision history (list of versions, dates, authors)
- `--format FORMAT`: Output format
- `--quiet`: Suppress status messages

#### `moin put <pagename>`
Write content to a wiki page.

```bash
# Direct content input
moin put PageName "content goes here"

# From file
moin put PageName --file content.txt

# From stdin
echo "content" | moin put PageName

# To specific server
moin put PageName "content" --server work
```

**Options:**
- `--server SERVERNAME`: Target server
- `--file FILE`: Read content from file

#### `moin list`
List all pages in the wiki.

```bash
# List all pages
moin list

# Filter with pattern
moin list --pattern "HomePage*"

# From specific server
moin list --server work

# JSON output for scripting
moin list --format json
```

**Options:**
- `--server SERVERNAME`: Target server
- `--pattern PATTERN`: Filter pattern (glob-style)
- `--format FORMAT`: Output format

#### `moin search <query>`
Search for pages containing the specified term.

```bash
# Basic search
moin search "search term"

# Search with regex
moin search --regex "pattern"

# Search specific server
moin search "term" --server work
```

**Options:**
- `--server SERVERNAME`: Target server
- `--regex`: Use regular expression matching
- `--format FORMAT`: Output format

## Server Management Commands

### `moin server add <name>`
Add a new wiki server configuration.

```bash
# Interactive setup
moin server add work
# Prompts for:
# - URL: https://wiki.company.com/
# - Username: john.doe
# - Password: [hidden input]

# Non-interactive with URL
moin server add work --url https://wiki.company.com --username john.doe
# Still prompts for password securely

# For automation (password from stdin)
echo "secret123" | moin server add work --url https://wiki.company.com --username john.doe --password-stdin
```

**Options:**
- `--url URL`: Wiki server URL
- `--username USERNAME`: Username for authentication
- `--password-stdin`: Read password from stdin
- `--verify-ssl`: Enable/disable SSL verification (default: true)
- `--timeout SECONDS`: Request timeout (default: 30)

### `moin server list`
List all configured servers.

```bash
# Basic list
moin server list

# Example output:
# NAME      URL                           USERNAME    STATUS      EXPIRES
# work      https://wiki.company.com/     john.doe    active      2024-12-31
# personal  https://mywiki.example.com/   john        expired     2024-06-15
# local     http://localhost:8080/        admin       active      never

# Detailed view
moin server list --detailed

# Check specific server
moin server show work
```

**Options:**
- `--detailed`: Show additional information
- `--format FORMAT`: Output format (table, json)

### `moin server show <name>`
Show detailed information about a specific server.

```bash
# Show server details (masks sensitive data)
moin server show work

# Show with credentials (use carefully)
moin server show work --show-credentials
```

**Options:**
- `--show-credentials`: Display actual token (security risk)

### `moin server remove <name>`
Remove a server configuration.

```bash
# Remove server configuration
moin server remove personal

# Confirm removal
moin server remove old-server --confirm
```

**Options:**
- `--confirm`: Skip confirmation prompt

### `moin server update <name>`
Update server configuration.

```bash
# Update server URL
moin server update work --url https://newwiki.company.com

# Update username
moin server update work --username new.user

# Update multiple settings
moin server update work --url https://new.com --timeout 60
```

**Options:**
- `--url URL`: New server URL
- `--username USERNAME`: New username
- `--timeout SECONDS`: Request timeout
- `--verify-ssl BOOL`: SSL verification setting

### `moin server set-default <name>`
Set the default server for operations.

```bash
# Set default server
moin server set-default work

# Clear default (requires explicit --server option)
moin server set-default --clear
```

**Options:**
- `--clear`: Remove default server setting

### `moin server test <name>`
Test connection to a server.

```bash
# Test server connection
moin server test work

# Test with verbose output
moin server test work --verbose

# Test all servers
moin server test --all
```

**Options:**
- `--verbose`: Show detailed connection information
- `--all`: Test all configured servers

## Authentication Commands

### `moin server login [name]`
Authenticate to a server (get new token).

```bash
# Login to specific server
moin server login work

# Login to default server
moin server login

# Force re-authentication
moin server login work --force
```

**Options:**
- `--force`: Force new authentication even if token is valid

### `moin server logout [name]`
Remove authentication token.

```bash
# Logout from specific server
moin server logout work

# Logout from all servers
moin server logout --all
```

**Options:**
- `--all`: Logout from all configured servers

### `moin auth status`
Check authentication status for all servers.

```bash
# Show authentication status
moin auth status

# Example output:
# SERVER    STATUS      EXPIRES     LAST USED
# work      active      2024-12-31  2 hours ago
# personal  expired     2024-06-15  3 days ago
# local     active      never       1 minute ago
```

### `moin auth show <name>`
Show authentication information for a specific server.

```bash
# Show auth info (masked token)
moin auth show work

# Show with actual token (security risk)
moin auth show work --show-token
```

**Options:**
- `--show-token`: Display actual authentication token

## Configuration Commands

### `moin config show`
Display current configuration.

```bash
# Show all configuration
moin config show

# Show specific server configuration
moin config show --server work

# Show configuration file location
moin config locate
```

**Options:**
- `--server SERVERNAME`: Show specific server config
- `--format FORMAT`: Output format (toml, json, yaml)

### `moin config validate`
Validate configuration file.

```bash
# Validate current configuration
moin config validate

# Validate specific config file
moin config validate --config /path/to/config.toml
```

**Options:**
- `--config PATH`: Validate specific config file

### `moin config edit`
Open configuration file in editor.

```bash
# Edit with default editor
moin config edit

# Edit with specific editor
moin config edit --editor nano
```

**Options:**
- `--editor EDITOR`: Specify editor to use

## MCP Server Commands

### `moin serve`
Start MCP server for Claude Code integration.

```bash
# Start MCP server with default settings
moin serve

# Start on specific address and port
moin serve --host 0.0.0.0 --port 8080

# Use specific server as default
moin serve --server work

# Start with debug logging
moin serve --debug
```

**Options:**
- `--host HOST`: Server host (default: localhost)
- `--port PORT`: Server port (default: 8000)
- `--server SERVERNAME`: Default server for MCP operations
- `--debug`: Enable debug logging

## Environment Variables

### Server Selection
- `MOIN_DEFAULT_SERVER`: Override default server
- `MOIN_SERVER_URL`: Direct server URL (bypasses configuration)

### Authentication
- `MOIN_USERNAME`: Default username for new servers
- `MOIN_TOKEN`: Direct access token (bypasses configuration)
- `MOIN_TOKEN_{SERVERNAME}`: Server-specific token (e.g., `MOIN_TOKEN_WORK`)

### Behavior Control
- `MOIN_CONFIG`: Configuration file path
- `MOIN_FORMAT`: Default output format
- `MOIN_EDITOR`: Editor for interactive editing
- `MOIN_NO_COLOR`: Disable colored output

## Usage Examples

### Daily Workflow
```bash
# Quick operations with default server
moin get HomePage
moin put Documentation
moin search "installation"
moin list --pattern "Project*"
```

### Multi-Server Setup
```bash
# Initial setup
moin server add work --url https://work.wiki.com
moin server add personal --url https://personal.wiki.com
moin server set-default work

# Using different servers
moin get Project --server work
moin get Notes --server personal
moin get HomePage  # uses default (work)
```

### Automation and Scripting
```bash
# Batch operations
export MOIN_TOKEN_WORK="your-token-here"
moin list --format json | jq '.[]' | while read page; do
    moin get "$page" --server work >> backup.txt
done

# Configuration management
moin config validate || exit 1
moin server test --all || echo "Some servers unreachable"
```

### MCP Integration
```bash
# Start MCP server for Claude Code
moin serve --server work

# Start on custom address for remote access
moin serve --host 0.0.0.0 --port 8080 --server personal
```

## Error Handling

### Common Exit Codes
- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Authentication error
- `4`: Network error
- `5`: Permission error

### Error Messages
```bash
# Authentication required
$ moin put PageName
Error: Authentication required for server 'work'
Run 'moin server login work' to authenticate

# Server not configured
$ moin get HomePage --server missing
Error: Server 'missing' not found in configuration
Run 'moin server list' to see available servers

# Network timeout
$ moin get HomePage
Error: Connection timeout to server 'work'
Check server URL and network connectivity
```

## Configuration Priority

Commands resolve configuration in this order:
1. Command-line options (`--server servername`)
2. Environment variables (`MOIN_DEFAULT_SERVER`)
3. Configuration file default
4. Error if no server configured

## Security Notes

### Best Practices
- Never store passwords in scripts or configuration
- Use environment variables for automation tokens
- Verify SSL certificates in production
- Regularly rotate authentication tokens
- Use least-privilege access for automation accounts

### File Permissions
```bash
# Ensure secure permissions
chmod 700 ~/.moin/
chmod 600 ~/.moin/config.toml
```
