# WikiRPC v2 Standard for MoinMoin

## Overview
WikiRPC v2 is the second version of the XML-RPC interface standard for wiki systems, specifically implemented by MoinMoin. It provides remote access to wiki functionality through XML-RPC protocol with improved UTF-8 string handling.

## Key Differences from v1

### String Encoding
- **v1**: Used ASCII-only strings, required URL encoding (%XX) or base64 encoding for UTF-8 content
- **v2**: Uses UTF-8 strings directly with no additional encoding, much more comfortable to use

### Protocol Benefits
- No URL-encoding for page names and content
- No base64 encoding for regular text
- UTF-8 transport encoding throughout
- Base64 only used when necessary (binary files like attachments)

## Endpoint Configuration

### URL Format
- **Endpoint**: `http://your-wiki-domain/?action=xmlrpc2`
- The `2` in `xmlrpc2` specifies WikiRPC v2
- XML-RPC action is disabled by default in MoinMoin, must be configured

### Enabling XML-RPC
MoinMoin requires configuration to enable the XML-RPC endpoint:
```python
# In wikiconfig.py
actions_excluded = []  # Remove 'xmlrpc' from excluded actions
```

## Core Methods

### Page Operations

#### `getAllPages()`
Returns a list of all pages in the wiki.
```python
pages = server.getAllPages()
# Returns: ['HomePage', 'WikiSandBox', 'HelpContents', ...]
```

#### `getPage(pagename)`
Retrieves the content of a specific page.
```python
content = server.getPage("HomePage")
# Returns: UTF-8 encoded page content as string
```

#### `putPage(pagename, content)`
Updates or creates a page with new content.
```python
result = server.putPage("TestPage", "New page content")
# Note: Current implementation has security limitations
```

#### `searchPages(searchterm)`
Searches for pages containing the specified term.
```python
results = server.searchPages("python")
# Returns: List of page names matching the search
```

### System Methods

#### `system.listMethods()`
Lists all available XML-RPC methods.
```python
methods = server.system.listMethods()
# Returns: ['getAllPages', 'getPage', 'putPage', ...]
```

#### `system.methodHelp(methodName)`
Gets help information for a specific method.
```python
help_text = server.system.methodHelp('getPage')
# Returns: Method documentation string
```

#### `system.methodSignature(methodName)`
Gets the method signature for a specific method.
```python
signature = server.system.methodSignature('getPage')
# Returns: Method parameter information
```

## Authentication Methods

### Token-Based Authentication

#### `getAuthToken(username, password)`
Obtains an authentication token using username and password.
```python
token = server.getAuthToken("username", "password")
# Returns: Authentication token string
```

#### `applyAuthToken(token)`
Applies an authentication token for subsequent operations.
```python
server.applyAuthToken(token)
# Authentication token is now active for this session
```

### Multicall Authentication Pattern
For operations requiring authentication:
```python
# Get authentication token
token = server.getAuthToken("ElmerFudd", "elmerspassword")

# Use multicall for authenticated operations
server.system.multicall([
    {'methodName': 'applyAuthToken', 'params': [token]}, 
    {'methodName': 'putPage', 'params': ['SomePageName', 'Page content']}
])
```

### HTTP Authentication
For Apache-based servers, HTTP authentication is supported:
```python
import xmlrpc.client
server = xmlrpc.client.ServerProxy(
    "http://username:password@wiki.example.com/?action=xmlrpc2"
)
```

## Implementation Example

### Basic Client Setup
```python
import xmlrpc.client

# Create server proxy
server = xmlrpc.client.ServerProxy("http://wiki.example.com/?action=xmlrpc2")

# Get all pages
all_pages = server.getAllPages()
print(f"Found {len(all_pages)} pages")

# Read a specific page
content = server.getPage("HomePage")
print(f"HomePage content: {content[:100]}...")

# Search for pages
results = server.searchPages("python")
print(f"Search results: {results}")
```

### Authenticated Operations
```python
import xmlrpc.client

server = xmlrpc.client.ServerProxy("http://wiki.example.com/?action=xmlrpc2")

# Authenticate
token = server.getAuthToken("myusername", "mypassword")

# Perform authenticated operation
server.system.multicall([
    {'methodName': 'applyAuthToken', 'params': [token]}, 
    {'methodName': 'putPage', 'params': ['TestPage', 'New content']}
])
```

## Security Considerations

### Current Limitations
- `putPage()` has security restrictions in default implementation
- Some servers may require configuration changes to allow write operations
- Authentication tokens should be handled securely

### Best Practices
- Use HTTPS for production deployments
- Store authentication tokens securely
- Implement proper error handling for authentication failures
- Validate user permissions before write operations

## Error Handling

### Common Errors
- **Authentication Failed**: Invalid username/password
- **Page Not Found**: Requesting non-existent page
- **Permission Denied**: Insufficient privileges for operation
- **Server Unavailable**: XML-RPC endpoint not enabled

### Error Response Format
Errors are returned as XML-RPC faults:
```python
try:
    content = server.getPage("NonExistentPage")
except xmlrpc.client.Fault as e:
    print(f"Error {e.faultCode}: {e.faultString}")
```

## Future Enhancements (v3 Ideas)

### Proposed Improvements
- Better integration with different authentication methods
- Ability to specify username when making changes
- More efficient search result handling
- Enhanced metadata support
- Attachment handling improvements

### Backward Compatibility
- v2 maintains compatibility with existing XML-RPC clients
- UTF-8 encoding improvements don't break existing functionality
- Authentication methods remain consistent

## Protocol Specifications

### Transport
- **Protocol**: HTTP/HTTPS
- **Content-Type**: text/xml
- **Encoding**: UTF-8
- **Method**: POST

### Data Types
- **String**: UTF-8 encoded text
- **Array**: List of items
- **Struct**: Dictionary/hash of key-value pairs
- **Boolean**: True/false values
- **Int**: Integer numbers
- **Base64**: Binary data (for attachments)

## Integration Notes

### Python Implementation
MoinMoin's WikiRPC v2 is implemented in Python and follows standard XML-RPC conventions.

### Cross-Platform Support
The XML-RPC standard ensures compatibility across different programming languages and platforms.

### Performance Considerations
- Batch operations using `system.multicall()` for efficiency
- Consider caching for frequently accessed pages
- Handle large page lists appropriately

## References

- [MoinMoin WikiRpc Documentation](http://moinmo.in/WikiRpc)
- [XML-RPC Specification](http://xmlrpc.com/)
- [JSPWiki WikiRPC Interface 2](https://jspwiki-wiki.apache.org/Wiki.jsp?page=WikiRPCInterface2)
- [Python xmlrpc.client Documentation](https://docs.python.org/3/library/xmlrpc.client.html)