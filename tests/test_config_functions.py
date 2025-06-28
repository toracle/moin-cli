import pytest
from pathlib import Path
from unittest.mock import mock_open, patch
import toml
from moin_cli.config import (
    get_config_path,
    save_config,
    load_config,
    get_wiki_config,
    Config,
    ServerConfig,
    Settings,
    MCPSettings
)

# Test data constants
VALID_URL = "https://example.com/"
VALID_TOKEN = "test-token-123"
VALID_USERNAME = "testuser"
VALID_SERVER_NAME = "testserver"

@pytest.fixture
def valid_config_data():
    return {
        "settings": {
            "default_server": VALID_SERVER_NAME,
            "format": "markdown",
            "editor": "vim",
            "cache_enabled": True
        },
        "servers": {
            VALID_SERVER_NAME: {
                "name": VALID_SERVER_NAME,
                "url": VALID_URL,
                "username": VALID_USERNAME,
                "access_token": VALID_TOKEN
            }
        }
    }

@pytest.fixture
def valid_config(valid_config_data):
    return Config(**valid_config_data)

def test_get_config_path():
    """Test config path is constructed correctly"""
    path = get_config_path()
    assert isinstance(path, Path)
    assert path == Path.home() / ".moin" / "config.toml"

def test_save_config_creates_directory(tmp_path, valid_config):
    """Test save_config creates parent directory if needed"""
    config_path = tmp_path / "config.toml"
    
    with patch('moin_cli.config.get_config_path', return_value=config_path):
        save_config(valid_config)
    
    assert config_path.exists()
    assert config_path.parent.exists()

def test_save_config_writes_valid_toml(tmp_path, valid_config):
    """Test save_config writes a readable file with essential fields"""
    config_path = tmp_path / "config.toml"
    
    with patch('moin_cli.config.get_config_path', return_value=config_path):
        save_config(valid_config)
    
    # Verify file can be loaded and contains essential fields
    loaded = toml.load(config_path)
    assert "settings" in loaded
    assert "servers" in loaded
    assert loaded["settings"]["default_server"] == VALID_SERVER_NAME
    assert VALID_SERVER_NAME in loaded["servers"]
    assert VALID_URL in loaded["servers"][VALID_SERVER_NAME]["url"]

def test_load_config_success(valid_config_data):
    """Test load_config loads and validates config successfully"""
    mock_data = toml.dumps(valid_config_data)
    
    with patch('builtins.open', mock_open(read_data=mock_data)):
        with patch('moin_cli.config.get_config_path'):
            config = load_config()
    
    assert isinstance(config, Config)
    assert config.settings.default_server == VALID_SERVER_NAME
    assert VALID_SERVER_NAME in config.servers

def test_load_config_file_not_found():
    """Test load_config raises FileNotFoundError when file doesn't exist"""
    with patch('moin_cli.config.get_config_path') as mock_path:
        mock_path.return_value.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            load_config()

def test_load_config_invalid_toml():
    """Test load_config raises TOML parse errors"""
    with patch('builtins.open', mock_open(read_data="invalid toml")):
        with patch('moin_cli.config.get_config_path'):
            with pytest.raises(toml.TomlDecodeError):
                load_config()

def test_get_wiki_config_default(valid_config):
    """Test get_wiki_config returns default server when no alias given"""
    with patch('moin_cli.config.load_config', return_value=valid_config):
        server = get_wiki_config()
    
    assert server.name == VALID_SERVER_NAME
    assert VALID_URL in str(server.url)

def test_get_wiki_config_specific_alias(valid_config):
    """Test get_wiki_config returns specific server when alias given"""
    with patch('moin_cli.config.load_config', return_value=valid_config):
        server = get_wiki_config(VALID_SERVER_NAME)
    
    assert server.name == VALID_SERVER_NAME
    assert str(server.url) == VALID_URL

def test_get_wiki_config_missing_alias(valid_config):
    """Test get_wiki_config raises ValueError for missing server alias"""
    with patch('moin_cli.config.load_config', return_value=valid_config):
        with pytest.raises(ValueError):
            get_wiki_config("nonexistent")

def test_get_wiki_config_no_default(valid_config):
    """Test get_wiki_config handles missing default_server setting"""
    valid_config.settings.default_server = None
    with patch('moin_cli.config.load_config', return_value=valid_config):
        with pytest.raises(ValueError):
            get_wiki_config()
