#!/bin/sh
# MoinMoin CLI Installer
# Downloads the latest pre-built binary from GitHub Releases.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/toracle/moin-cli/main/install.sh | sh

set -e

REPO="toracle/moin-cli"
BINARY_NAME="moin"

# --- Helper functions ---

info() {
    printf '[info] %s\n' "$1"
}

error() {
    printf '[error] %s\n' "$1" >&2
    exit 1
}

need_cmd() {
    if ! command -v "$1" > /dev/null 2>&1; then
        error "Required command not found: $1. Please install it and try again."
    fi
}

# --- Cleanup on exit ---

cleanup() {
    if [ -n "$TMPDIR_CREATED" ] && [ -d "$TMPDIR_CREATED" ]; then
        rm -rf "$TMPDIR_CREATED"
    fi
}
trap cleanup EXIT INT TERM

# --- Detect platform ---

detect_platform() {
    OS="$(uname -s)"
    ARCH="$(uname -m)"

    case "$OS" in
        Linux)
            PLATFORM="linux"
            ;;
        Darwin)
            PLATFORM="macos"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            PLATFORM="windows"
            ;;
        *)
            error "Unsupported operating system: $OS"
            ;;
    esac

    case "$ARCH" in
        x86_64|amd64)
            ARCH="x86_64"
            ;;
        aarch64|arm64)
            ARCH="aarch64"
            ;;
        *)
            error "Unsupported architecture: $ARCH"
            ;;
    esac
}

# --- Map platform to target triple ---

map_target() {
    case "${PLATFORM}-${ARCH}" in
        linux-x86_64)
            TARGET="x86_64-unknown-linux-musl"
            ARCHIVE_EXT="tar.gz"
            ;;
        linux-aarch64)
            TARGET="aarch64-unknown-linux-musl"
            ARCHIVE_EXT="tar.gz"
            ;;
        macos-aarch64)
            TARGET="aarch64-apple-darwin"
            ARCHIVE_EXT="tar.gz"
            ;;
        windows-x86_64)
            TARGET="x86_64-pc-windows-msvc"
            ARCHIVE_EXT="zip"
            ;;
        *)
            error "No pre-built binary available for ${PLATFORM} ${ARCH}"
            ;;
    esac
}

# --- Fetch latest release tag ---

fetch_latest_tag() {
    info "Fetching latest release information..."
    RELEASE_URL="https://api.github.com/repos/${REPO}/releases/latest"
    TAG="$(curl -sS "$RELEASE_URL" | grep '"tag_name"' | head -1 | sed 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/')"

    if [ -z "$TAG" ]; then
        error "Could not determine latest release tag. Check https://github.com/${REPO}/releases"
    fi

    info "Latest release: $TAG"
}

# --- Download and install ---

download_and_install() {
    ARCHIVE_NAME="${BINARY_NAME}-${TARGET}.${ARCHIVE_EXT}"
    DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${TAG}/${ARCHIVE_NAME}"

    TMPDIR_CREATED="$(mktemp -d)"

    info "Downloading ${ARCHIVE_NAME}..."
    curl -sSL -o "${TMPDIR_CREATED}/${ARCHIVE_NAME}" "$DOWNLOAD_URL"

    if [ ! -s "${TMPDIR_CREATED}/${ARCHIVE_NAME}" ]; then
        error "Download failed or file is empty. URL: ${DOWNLOAD_URL}"
    fi

    info "Extracting..."

    case "$ARCHIVE_EXT" in
        tar.gz)
            tar xzf "${TMPDIR_CREATED}/${ARCHIVE_NAME}" -C "$TMPDIR_CREATED"
            BINARY_PATH="${TMPDIR_CREATED}/${BINARY_NAME}-${TARGET}/${BINARY_NAME}"
            ;;
        zip)
            need_cmd unzip
            unzip -q "${TMPDIR_CREATED}/${ARCHIVE_NAME}" -d "$TMPDIR_CREATED"
            BINARY_PATH="${TMPDIR_CREATED}/${BINARY_NAME}-${TARGET}/${BINARY_NAME}.exe"
            ;;
    esac

    if [ ! -f "$BINARY_PATH" ]; then
        error "Binary not found after extraction. Expected: ${BINARY_PATH}"
    fi

    # Determine install directory
    if [ "$PLATFORM" = "windows" ]; then
        INSTALL_DIR="$HOME/bin"
        INSTALL_PATH="${INSTALL_DIR}/${BINARY_NAME}.exe"
    else
        INSTALL_DIR="$HOME/.local/bin"
        INSTALL_PATH="${INSTALL_DIR}/${BINARY_NAME}"
    fi

    mkdir -p "$INSTALL_DIR"

    info "Installing to ${INSTALL_PATH}..."
    cp "$BINARY_PATH" "$INSTALL_PATH"
    chmod +x "$INSTALL_PATH" 2>/dev/null || true

    info "Installed ${BINARY_NAME} to ${INSTALL_PATH}"

    # Check if install directory is in PATH
    case ":${PATH}:" in
        *":${INSTALL_DIR}:"*)
            ;;
        *)
            echo ""
            info "NOTE: ${INSTALL_DIR} is not in your PATH."
            info "Add it by appending this line to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
            echo ""
            echo "  export PATH=\"${INSTALL_DIR}:\$PATH\""
            echo ""
            ;;
    esac
}

# --- Verify installation ---

verify_install() {
    if command -v "$BINARY_NAME" > /dev/null 2>&1; then
        echo ""
        info "Verification:"
        "$BINARY_NAME" --version
        echo ""
        info "Installation complete. Run '${BINARY_NAME} --help' to get started."
    else
        echo ""
        info "Installation complete. You may need to restart your shell or update your PATH."
        info "Then run '${BINARY_NAME} --help' to get started."
    fi
}

# --- Main ---

main() {
    info "Installing ${BINARY_NAME}..."
    echo ""

    need_cmd curl
    need_cmd tar

    detect_platform
    map_target
    info "Detected platform: ${PLATFORM} ${ARCH} (target: ${TARGET})"

    fetch_latest_tag
    download_and_install
    verify_install
}

main
