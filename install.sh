#!/bin/bash

# MoinMoin CLI Installer
# This script installs the moin-cli tool built in Rust

set -e

echo "🚀 Installing moin-cli..."

# Check if cargo is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust/Cargo not found!"
    echo "Installing Rust toolchain..."
    
    # Install Rust using rustup
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    
    # Source the rustup environment
    source "$HOME/.cargo/env"
    
    # Verify installation
    if ! command -v cargo &> /dev/null; then
        echo "❌ Failed to install Rust. Please install it manually from https://rustup.rs"
        exit 1
    fi
    
    echo "✅ Rust toolchain installed successfully!"
fi

# Check if we're installing from git or local directory
if [ -f "Cargo.toml" ]; then
    # Install from local directory
    echo "📦 Installing from local directory..."
    cargo install --path . --force
else
    # Install from GitHub repository
    echo "📦 Installing from GitHub repository..."
    cargo install --git https://github.com/toracle/moin-cli.git --branch rust-conversion --force
fi

# Verify installation
if command -v moin-cli &> /dev/null; then
    echo ""
    echo "✅ moin-cli installed successfully!"
    echo ""
    echo "Try it out:"
    echo "  moin-cli --help"
    echo "  moin-cli auth    # Set up your wiki connection"
    echo "  moin-cli list    # List all pages"
    echo ""
    echo "💡 Tip: Add ~/.cargo/bin to your PATH if 'moin-cli' command is not found"
else
    echo "❌ Failed to install moin-cli"
    echo "Make sure ~/.cargo/bin is in your PATH"
    exit 1
fi
