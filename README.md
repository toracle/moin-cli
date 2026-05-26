# moin-cli (Rust)

A Rust CLI tool for interacting with MoinMoin wiki servers via XML-RPC.

This is the Rust rewrite of the original Python moin-cli project.

## Installation

### Quick Install (one-liner)

```bash
curl -sSL https://raw.githubusercontent.com/toracle/moin-cli/main/install.sh | sh
```

This will detect your platform, download the latest release binary, and install it to `~/.local/bin`.

### Download from Releases

Pre-built binaries for Linux (x86_64, aarch64), macOS (Apple Silicon), and Windows (x86_64) are available on the [GitHub Releases](https://github.com/toracle/moin-cli/releases) page.

### Manual Installation

1. Make sure you have [Rust](https://rustup.rs) installed:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. Clone this repository and install:
   ```bash
   git clone https://github.com/toracle/moin-cli.git
   cd moin-cli
   cargo install --path .
   ```

## Usage

### Setup

First, configure your wiki connection:

```bash
moin auth
```

This will prompt you for:
- Wiki name/alias (e.g., `local`, `production`)
- Wiki server URL (e.g., `http://localhost:8080`)
- Username
- Password

### Commands

| Command | Description |
|---------|-------------|
| `auth` | Set up authentication for a MoinMoin wiki |
| `version` / `v` | Show version, check for updates, or self-update |
| `get <pagename>` | Get page content |
| `get --history <pagename>` | Show page revision history |
| `get --version <n> <pagename>` | Get specific page version |
| `put <pagename> [content]` | Update page content |
| `put --file <file> <pagename>` | Update page from file |
| `list` | List all pages |
| `search <query>` | Search for pages containing query |
| `recent [--days N]` | Show recently changed pages |

### Examples

```bash
# Get a page
moin get Home

# Get page history
moin get --history Home

# Update a page
moin put Home "Welcome to my wiki!"

# Update page from file
moin put --file welcome.txt Home

# List all pages
moin list

# Search for pages
moin search "important stuff"

# Recent changes
moin recent --days 7

# Version and Update
moin --version          # Show version (standard flag)
moin version            # Show version
moin v                  # Show version (short alias)
moin version --check   # Check for newer version
moin v -c               # Check for newer version (short)
moin version --update  # Self-update to latest version
moin v -u               # Self-update (short)
moin version --check --update  # Check and update if available
```

## Version Checking and Self-Update

moin includes built-in version checking and self-update capabilities:

- **Version Display**: Use `moin --version`, `moin version`, or `moin v` to display the current version
- **Update Checking**: Use `moin version --check` to query GitHub for the latest release
- **Self-Update**: Use `moin version --update` to automatically download and install the latest version

The self-update feature:
- Queries GitHub's releases API to find the latest version
- Detects your platform automatically (Linux, macOS, Windows)
- Downloads the appropriate binary for your system
- Creates a backup of your current binary before updating
- Asks for confirmation before replacing the current executable
- Preserves executable permissions on Unix systems

## Configuration

Configuration is stored in `~/.config/moin-cli/config.toml` (or the appropriate location for your OS).

## Development

```bash
# Build
cargo build

# Run
cargo run -- --help

# Test
cargo test

# Format code
cargo fmt

# Lint
cargo clippy
```

## GitHub Actions

The project includes a CI/CD workflow (`.github/workflows/rust.yml`) that:
- Runs format, clippy, build, and test checks on push/PR to main
- Tests on multiple platforms (Linux, macOS, Windows)
- Builds cross-platform release binaries on tag push (`v*`)
- Publishes binaries to GitHub Releases automatically

## License

MIT License
