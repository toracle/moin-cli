# Documentation

Complete documentation for the MoinMoin CLI tool.

## 🚀 Quick Start

**New to MoinMoin CLI?** Start here:
- [Getting Started](user-guide/getting-started.md) - Installation and first steps

## 📖 User Guide

For end users who want to use the CLI tool:

- **[Getting Started](user-guide/getting-started.md)** - Installation, setup, and basic usage
- **[Commands](user-guide/commands.md)** - Complete command reference
- **[Configuration](user-guide/configuration.md)** - Server configuration and settings

## 🔧 Developer Documentation

For contributors and those wanting to understand the internals:

- **[Architecture](developer/architecture.md)** - System design and technical details
- **[Implementation Plan](developer/implementation.md)** - Development roadmap
- **[Protocols](developer/protocols.md)** - WikiRPC v2 specification

## 📋 Quick Reference

### Essential Commands
```bash
# Setup
moin server add work --url https://wiki.company.com
moin server set-default work

# Daily usage
moin get HomePage              # Read page
moin put Documentation         # Edit page  
moin search "term"            # Search pages
moin list                     # List all pages

# MCP server
moin serve                    # Start MCP server for Claude Code
```

### Key Concepts
- **Servers**: Multiple wiki servers with secure token authentication
- **MCP Integration**: Built-in Model Context Protocol server for AI tools
- **Configuration**: TOML-based config in `~/.moin/config.toml`

## 🎯 Use Cases

### For Wiki Users
- Command-line wiki editing and reading
- Batch operations on wiki content
- Automated content management scripts

### For Claude Code Users  
- AI-assisted wiki content editing
- Research and documentation workflows
- Structured knowledge management

### For Developers
- MoinMoin XML-RPC integration
- Custom wiki automation tools
- MCP server extension

## 📁 Documentation Structure

```
docs/
├── README.md                 # This file - documentation index
├── user-guide/              # For end users
│   ├── getting-started.md   # Quick start guide
│   ├── commands.md          # Complete CLI reference
│   └── configuration.md     # Settings and config
└── developer/               # For contributors
    ├── architecture.md      # Technical design
    ├── implementation.md    # Development plan
    └── protocols.md         # WikiRPC v2 spec
```

## 🤝 Contributing

Want to contribute? Check out:
1. [Architecture](developer/architecture.md) for system understanding
2. [Implementation Plan](developer/implementation.md) for development roadmap
3. Main README.md for contribution guidelines

## 💡 Need Help?

- **User questions**: Start with [Getting Started](user-guide/getting-started.md)
- **Command help**: See [Commands](user-guide/commands.md) or run `moin --help`
- **Configuration issues**: Check [Configuration](user-guide/configuration.md)
- **Technical questions**: See [Architecture](developer/architecture.md)
- **Protocol details**: See [Protocols](developer/protocols.md)