# WikiRPC v2 Authentication Analysis

## Overview
Analysis of authentication methods available in WikiRPC v2 for MoinMoin, including token-based authentication, HTTP authentication, and security considerations for CLI implementation.

## Authentication Methods

### 1. Token-Based Authentication (Recommended)

#### Flow
1. **Get Token**: `getAuthToken(username, password)` → returns token string
2. **Apply Token**: `applyAuthToken(token)` → activates token for session
3. **Perform Operations**: All subsequent calls use the active token

#### Implementation Pattern
```python
# Single operation
token = server.getAuthToken("username", "password")
server.applyAuthToken(token)
result = server.putPage("PageName", "Content")

# Multicall pattern (more efficient)
token = server.getAuthToken("username", "password")
server.system.multicall([
    {'methodName': 'applyAuthToken', 'params': [token]}, 
    {'methodName': 'putPage', 'params': ['PageName', 'Content']}
])
```

#### Advantages
- Password not sent with every request after initial authentication
- Token can be cached and reused
- Supports session-like behavior
- More secure than basic auth for repeated operations

#### Token Characteristics
- **Format**: String (implementation-specific)
- **Lifetime**: Server-dependent (may expire)
- **Scope**: Per-session, not persistent across client restarts
- **Security**: Should be treated as sensitive credential

### 2. HTTP Authentication

#### Basic Authentication
```python
import xmlrpc.client
server = xmlrpc.client.ServerProxy(
    "http://username:password@wiki.example.com/?action=xmlrpc2"
)
```

#### Advantages
- Standard HTTP mechanism
- Works with existing web server authentication
- Simple to implement

#### Disadvantages
- Credentials sent with every request
- Less efficient than token-based auth
- Requires HTTPS for security

### 3. Server Integration Authentication

#### Apache Integration
- MoinMoin can integrate with Apache's authentication modules
- Uses `HttpServletRequest.getUserPrincipal()` pattern
- Supports container-managed security

#### Configuration Example
```python
# In wikiconfig.py
from MoinMoin.auth import http
auth = [http.HTTPAuth()]
```

## Security Analysis

### Token Security

#### Storage Considerations
- **In-Memory**: Secure but lost on restart
- **File-based**: Persistent but requires secure file permissions
- **Keyring**: Most secure for desktop applications
- **Environment Variables**: Suitable for CI/CD scenarios

#### Token Lifecycle
```python
# Recommended pattern for CLI
class AuthManager:
    def __init__(self):
        self.token = None
        self.token_expiry = None
    
    def get_valid_token(self, server, username, password):
        if self.token and not self.is_expired():
            return self.token
        
        # Re-authenticate
        self.token = server.getAuthToken(username, password)
        self.token_expiry = time.time() + TOKEN_LIFETIME
        return self.token
```

### Password Security

#### Best Practices
- **Never store passwords in config files**
- **Use secure input methods** (`getpass.getpass()`)
- **Clear from memory** after use
- **Support environment variables** for automation

#### Implementation
```python
import getpass
import os

def get_credentials(username=None):
    if not username:
        username = input("Username: ")
    
    # Try environment variable first (for automation)
    password = os.getenv(f'MOIN_PASSWORD_{username.upper()}')
    if not password:
        password = getpass.getpass(f"Password for {username}: ")
    
    return username, password
```

### Transport Security

#### HTTPS Requirements
- **Production**: Always use HTTPS
- **Development**: HTTP acceptable for localhost only
- **Token transmission**: Must be encrypted in production

#### Certificate Validation
```python
import ssl
import xmlrpc.client

# Secure context (default)
server = xmlrpc.client.ServerProxy("https://wiki.example.com/?action=xmlrpc2")

# Disable verification for development only
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
server = xmlrpc.client.ServerProxy(
    "https://wiki.example.com/?action=xmlrpc2",
    context=context
)
```

## CLI Authentication Strategy

### Recommended Approach

#### Phase 1: Initial Authentication
```bash
# User adds server and authenticates
moin server add work --url https://wiki.company.com
# Username: john.doe
# Password: [hidden input]
# → Gets token and stores in ~/.moin/config.toml
```

#### Phase 2: Token Storage
```toml
[server.work]
name = "work"
url = "https://wiki.company.com/"
username = "john.doe"
access_token = "server-generated-token"
token_obtained = "2024-06-28T10:00:00Z"
```

#### Phase 3: Token Usage
```python
def authenticate_operation(server_config):
    token = server_config.get('access_token')
    if not token:
        # Re-authenticate
        username = server_config['username']
        password = get_password_securely(username)
        token = server.getAuthToken(username, password)
        save_token(server_config['name'], token)
    
    return token
```

### Error Handling

#### Authentication Failures
```python
def handle_auth_error(server_name, error):
    if "authentication" in str(error).lower():
        print(f"Authentication failed for server '{server_name}'")
        print(f"Run 'moin login {server_name}' to re-authenticate")
        return False
    return True
```

#### Token Expiration
```python
def is_token_expired(error):
    # Check if error indicates token expiration
    error_msg = str(error).lower()
    return any(keyword in error_msg for keyword in [
        'expired', 'invalid token', 'unauthorized'
    ])
```

## Implementation Considerations

### Session Management

#### Per-Operation Authentication
```python
# For each operation
def authenticated_call(server, token, method, *args):
    try:
        server.applyAuthToken(token)
        return getattr(server, method)(*args)
    except xmlrpc.client.Fault as e:
        if is_auth_error(e):
            # Re-authenticate and retry
            new_token = re_authenticate(server)
            server.applyAuthToken(new_token)
            return getattr(server, method)(*args)
        raise
```

#### Multicall Optimization
```python
def authenticated_multicall(server, token, operations):
    calls = [{'methodName': 'applyAuthToken', 'params': [token]}]
    calls.extend(operations)
    return server.system.multicall(calls)
```

### Configuration Integration

#### Server Configuration Structure
```toml
[server.work]
name = "work"
url = "https://wiki.company.com/"
username = "john.doe"
access_token = "encrypted:base64encodedtoken"
auth_method = "token"  # or "http", "none"
verify_ssl = true
timeout = 30
```

#### Environment Variable Support
```bash
# Override token for automation
export MOIN_TOKEN_WORK="automation-token-123"

# Override credentials
export MOIN_USERNAME="automation-user"
export MOIN_PASSWORD_WORK="automation-password"
```

## Security Recommendations

### Development Phase
1. **Use token-based authentication** as primary method
2. **Store tokens securely** with appropriate file permissions
3. **Implement token refresh** when authentication fails
4. **Support HTTP auth** as fallback for simple setups

### Production Phase
1. **Require HTTPS** for all operations
2. **Validate SSL certificates** by default
3. **Implement token encryption** for stored tokens
4. **Support keyring integration** for enhanced security
5. **Audit authentication events** through logging

### Future Enhancements
1. **SSO Integration**: SAML, OAuth, OpenID Connect
2. **API Keys**: Long-lived authentication tokens
3. **Certificate-based Auth**: Client certificates
4. **Multi-factor Authentication**: Additional security layer