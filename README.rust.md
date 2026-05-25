# moin-cli (Rust)

A Rust CLI tool for interacting with MoinMoin wiki servers via XML-RPC.

This is the Rust rewrite of the original Python moin-cli project.

## Installation

### Quick Install (one-liner)

```bash
curl -sSL https://raw.githubusercontent.com/toracle/moin-cli/rust-conversion/install.sh | bash
```

Or using cargo directly:

```bash
cargo install --git https://github.com/toracle/moin-cli.git --branch rust-conversion
```

### Manual Installation

1. Make sure you have [Rust](https://rustup.rs) installed:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. Clone this repository and install:
   ```bash
   git clone https://github.com/toracle/moin-cli.git
   cd moin-cli
   git checkout rust-conversion
   cargo install --path .
   ```

## Usage

### Setup

First, configure your wiki connection:

```bash
moin-cli auth
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
moin-cli get Home

# Get page history
moin-cli get --history Home

# Update a page
moin-cli put Home "Welcome to my wiki!"

# Update page from file
moin-cli put --file welcome.txt Home

# List all pages
moin-cli list

# Search for pages
moin-cli search "important stuff"

# Recent changes
moin-cli recent --days 7
```

## Configuration

Configuration is stored in `~/.config/moin-cli/config.toml` (or the appropriate location for your OS).

## Development

```bash
# Build
git checkout rust-conversion
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
- Tests on multiple Rust toolchains (stable, nightly)
- Runs on multiple platforms (Linux, macOS, Windows)
- Runs clippy and fmt checks
- Builds in both debug and release modes

## License

MIT License
