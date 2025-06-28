# Authentication System Design

## Overview
The `moin` CLI uses a token-based authentication system similar to Azure CLI, where users authenticate once and receive a token that's stored locally for subsequent operations.

## Authentication Flow

### Initial Authentication
1. User runs `moin server add work --url https://wiki.company.com`
2. CLI prompts for username and password (hidden input)
3. CLI sends credentials to MoinMoin server to obtain access token
4. Token is stored securely in `~/.moin/config.toml`
5. Credentials are not stored, only the token

### Token Usage
1. For each operation, CLI reads token from config
2. Token is sent with XML-RPC requests for authentication
3. If token expires, CLI prompts for re-authentication
4. Token refresh is automatic when possible

## Configuration Directory Structure

### Location: `~/.moin/`
```
~/.moin/
├── config.toml          # Main configuration with tokens
├── cache/               # Optional page cache
├── logs/                # Operation logs
└── profiles/            # Alternative: separate profile files
    ├── work.toml
    ├── personal.toml
    └── default.toml
```

## Configuration File Format

### Option 1: Single Config with Profiles
```toml
# ~/.moin/config.toml

[settings]
default_profile = "work"
format = "markdown"
cache_enabled = true

[profile.work]
name = "work"
url = "https://wiki.company.com/"
username = "john.doe"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
token_expires = "2024-12-31T23:59:59Z"
created_at = "2024-06-28T10:00:00Z"
last_used = "2024-06-28T14:30:00Z"

[profile.personal]
name = "personal"
url = "https://mywiki.example.com/"
username = "john"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
token_expires = "2024-07-28T12:00:00Z"

[profile.local]
name = "local"
url = "http://localhost:8080/"
username = "admin"
access_token = "simple-token-123"
# Local servers might use simple tokens
```

### Option 2: Server-based Configuration
```toml
# ~/.moin/config.toml

[settings]
default_server = "work"
format = "markdown"

[server.work]
name = "work"
url = "https://wiki.company.com/"
username = "john.doe"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
token_expires = "2024-12-31T23:59:59Z"

[server.personal]
name = "personal"
url = "https://mywiki.example.com/"
username = "john"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
token_expires = "2024-07-28T12:00:00Z"
```

### Option 3: Wiki-based Configuration (Original)
```toml
# ~/.moin/config.toml

[settings]
default_wiki = "work"

[wiki.work]
name = "work"
url = "https://wiki.company.com/"
username = "john.doe"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
token_expires = "2024-12-31T23:59:59Z"
```

## Server Management Commands

### Add New Server
```bash
# Interactive mode
moin server add work
# Prompts for:
# - URL: https://wiki.company.com/
# - Username: john.doe
# - Password: [hidden input]

# Non-interactive mode
moin server add work --url https://wiki.company.com --username john.doe
# Still prompts for password securely

# With all details (for scripting)
moin server add work --url https://wiki.company.com --username john.doe --password-stdin
echo "secret123" | moin server add work --url https://wiki.company.com --username john.doe --password-stdin
```

### List Servers
```bash
# List all configured servers
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

### Server Management
```bash
# Remove server configuration
moin server remove personal

# Update server URL
moin server update work --url https://newwiki.company.com

# Re-authenticate (get new token)
moin server login work

# Test server connection
moin server test work

# Set default server
moin server set-default work

# Logout (remove token)
moin server logout work
```

## Authentication Commands

### Login/Logout
```bash
# Login to specific server (re-authenticate)
moin login work

# Login to default server
moin login

# Logout from specific server
moin logout work

# Logout from all servers
moin logout --all

# Check current authentication status
moin auth status

# Show token details (masked)
moin auth show work
```

## Token Management

### Token Storage
- Tokens stored in configuration file with 600 permissions
- Consider future keyring integration for enhanced security
- Token rotation handled automatically when supported

### Token Validation
- Check token expiration before each operation
- Automatic re-authentication prompts
- Graceful handling of expired/invalid tokens

### Token Types
Support for different MoinMoin authentication methods:
- JWT tokens (preferred)
- Session tokens  
- API keys
- Basic auth fallback (legacy)

## Security Considerations

### File Permissions
```bash
# Ensure secure permissions
chmod 700 ~/.moin/
chmod 600 ~/.moin/config.toml
```

### Password Handling
- Never store passwords in config files
- Use `getpass` for secure password input
- Support reading password from stdin for automation
- Clear password from memory after use

### Token Security
- Store tokens with appropriate metadata (expiration, scope)
- Implement token refresh when possible
- Secure token transmission (HTTPS only)
- Support token revocation

## Usage Examples

### First-Time Setup
```bash
# Add work server
moin server add work
# URL: https://wiki.company.com/
# Username: john.doe
# Password: [hidden]
# ✓ Successfully authenticated and saved token

# Set as default
moin server set-default work

# Verify setup
moin server list
```

### Daily Usage
```bash
# Operations use default server automatically
moin read HomePage
moin write Documentation
moin search "project"

# Use specific server when needed
moin read HomePage --server personal
```

### Multi-Server Workflow
```bash
# Check all servers
moin server list

# Re-authenticate expired server
moin server login personal

# Switch default server
moin server set-default personal

# Now operations use personal server by default
moin read Notes
```

## Error Handling

### Common Scenarios
1. **Expired token**: Prompt for re-authentication
2. **Invalid credentials**: Clear error message and retry option
3. **Network issues**: Retry with exponential backoff
4. **Server unavailable**: Graceful degradation

### User Experience
```bash
# Example expired token flow
$ moin read HomePage
Error: Authentication token expired for server 'work'
Run 'moin server login work' to re-authenticate

$ moin server login work
Password for john.doe@wiki.company.com: [hidden]
✓ Successfully authenticated

$ moin read HomePage
[page content]
```

## Implementation Priority

### Phase 1: Basic Token Auth
1. Server add/list/remove commands
2. Token storage in config file
3. Basic authentication flow

### Phase 2: Enhanced Security
1. Token expiration handling
2. Automatic refresh
3. Secure file permissions

### Phase 3: Advanced Features
1. Multiple authentication methods
2. Keyring integration
3. SSO support (future)

## Configuration Section Name Decision

**Recommendation: `[server.name]`**

Reasoning:
- Clear semantic meaning
- Aligns with `moin server` commands
- Distinguishes from other configuration sections
- Similar to Azure CLI's subscription concept

Alternative options:
- `[profile.name]` - Good for user profiles, but servers are resources
- `[wiki.name]` - Too specific to wiki concept
- `[server.name]` - **Best choice** - clear and consistent