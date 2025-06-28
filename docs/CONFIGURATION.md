# Configuration System

## Overview
The `moin` CLI supports multiple wiki servers through a token-based authentication system that allows users to define named server configurations with secure access tokens.

## Configuration File Format

### TOML Configuration
The configuration uses TOML format for human readability and easy editing, stored in `~/.moin/config.toml`.

```toml
# ~/.moin/config.toml

[settings]
default_server = "work"
format = "markdown"
editor = "vim"
cache_enabled = true

[server.work]
name = "work"
url = "https://work.company.com/"
engine = "moinmoin"
username = "john.doe"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
token_expires = "2024-12-31T23:59:59Z"
created_at = "2024-06-28T10:00:00Z"
last_used = "2024-06-28T14:30:00Z"

[server.personal]
name = "personal"
url = "https://mywiki.example.com/"
engine = "moinmoin"
username = "john"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
token_expires = "2024-07-28T12:00:00Z"

[server.local]
name = "local"
url = "http://localhost:8080/"
engine = "moinmoin"
username = "admin"
access_token = "simple-token-123"
verify_ssl = false

[mcp]
host = "localhost"
port = 8000
default_server = "work"
```

## Configuration Locations

### Primary Location
- `~/.moin/config.toml` (main configuration file)

### Override Options
1. Path specified by `--config` option
2. `MOIN_CONFIG` environment variable

### Directory Structure
```
~/.moin/
├── config.toml          # Main configuration with tokens
├── cache/               # Page cache (optional)
└── logs/                # Operation logs (optional)
```

## Server Configuration

### Required Fields
- `name`: Server identifier
- `url`: MoinMoin wiki URL with XML-RPC endpoint
- `username`: Username for authentication
- `access_token`: Authentication token (obtained via login)

### Optional Fields
- `engine`: Wiki engine
- `token_expires`: Token expiration timestamp (ISO format)
- `timeout`: Request timeout in seconds (default: 30)
- `verify_ssl`: SSL certificate verification (default: true)
- `user_agent`: Custom user agent string
- `created_at`: When server was added
- `last_used`: Last operation timestamp

### Example Server Configurations
```toml
[server.production]
name = "production"
url = "https://wiki.company.com/"
username = "api_user"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
token_expires = "2024-12-31T23:59:59Z"
timeout = 60
verify_ssl = true

[server.development]
name = "development"
url = "http://dev-wiki:8080/"
username = "developer"
access_token = "dev-token-123"
verify_ssl = false

[server.local]
name = "local"
url = "http://localhost:8080/"
username = "admin"
access_token = "simple-token"
# No expiration for local development
```

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

## Default Behavior

### When No Configuration Exists
1. Prompt user to run `moin config add-wiki`
2. Offer to create configuration interactively
3. Suggest example configuration

### Default Wiki Selection
1. Command-line `--wiki` option
2. `MOIN_DEFAULT_WIKI` environment variable
3. `default_wiki` from configuration file
4. First wiki in alphabetical order
5. Error if no wikis configured

## Configuration Commands

### Interactive Setup
```bash
# First-time setup wizard
moin config init

# Add new wiki interactively
moin config add-wiki

# Add wiki with prompts
moin config add-wiki mysite
```

### Direct Configuration
```bash
# Add wiki with all details
moin config add-wiki work \
  --url https://wiki.company.com \
  --username john.doe

# Set default wiki
moin config set-default work

# Remove wiki configuration
moin config remove-wiki old-site
```

### Information Commands
```bash
# Show current configuration
moin config show

# List configured wikis
moin config list-wikis

# Show effective configuration for a wiki
moin config show --wiki work

# Test wiki connection
moin config test --wiki work
```

## Security Considerations

### Password Storage
- **Never store passwords in configuration files**
- Use environment variables for automated scenarios
- Interactive prompting for manual use
- Consider using keyring integration (future enhancement)

### SSL/TLS
- Always verify SSL certificates in production
- Only disable for development/testing environments
- Support custom CA certificates (future enhancement)

### Permissions
- Configuration files should be readable only by user (600)
- Cache and log directories should be user-private (700)

## Migration and Backup

### Configuration Migration
```bash
# Export configuration
moin config export > backup.toml

# Import configuration
moin config import backup.toml

# Merge configurations
moin config merge other-config.toml
```

### Version Compatibility
- Configuration format versioning for future changes
- Automatic migration for backward compatibility
- Warning for unsupported configuration versions

## Examples

### Minimal Configuration
```toml
[settings]
default_wiki = "main"

[wikis.main]
url = "https://wiki.example.com/"
username = "myuser"
```

### Advanced Multi-Wiki Setup
```toml
[settings]
default_wiki = "work"
format = "markdown"
editor = "code --wait"

[wikis.work]
url = "https://internal.company.com/wiki/"
username = "john.doe"
timeout = 45

[wikis.opensource]
url = "https://opensource-project.org/wiki/"
username = "contributor"

[wikis.personal]
url = "http://homelab:8080/"
username = "admin"
verify_ssl = false

[mcp]
host = "0.0.0.0"
port = 8080
default_wiki = "work"
```

## Troubleshooting

### Common Issues
1. **No default wiki**: Set `default_wiki` or use `--wiki` option
2. **Authentication failure**: Check username/password environment variables
3. **Connection timeout**: Increase `timeout` value in wiki configuration
4. **SSL errors**: Verify `verify_ssl` setting and certificate validity

### Debug Mode
```bash
# Show effective configuration
moin config show --debug

# Test wiki connectivity
moin config test --wiki work --verbose

# Show configuration file locations
moin config locate
```
