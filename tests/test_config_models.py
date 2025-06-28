import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from moin_cli.config.models import (
    ServerConfig,
    Settings,
    MCPSettings,
    Config
)

# Test data constants
VALID_URL = "https://example.com/"
VALID_TOKEN = "test-token-123"
VALID_USERNAME = "testuser"
VALID_SERVER_NAME = "testserver"

# Fixtures
@pytest.fixture
def valid_server_data():
    return {
        "name": VALID_SERVER_NAME,
        "url": VALID_URL,
        "username": VALID_USERNAME,
        "access_token": VALID_TOKEN
    }

@pytest.fixture
def valid_settings_data():
    return {
        "default_server": VALID_SERVER_NAME,
        "format": "markdown",
        "editor": "vim",
        "cache_enabled": True
    }

@pytest.fixture
def valid_mcp_data():
    return {
        "host": "localhost",
        "port": 8000,
        "default_server": VALID_SERVER_NAME
    }

# ServerConfig Tests
def test_server_config_minimal(valid_server_data):
    """Test minimal valid ServerConfig"""
    server = ServerConfig(**valid_server_data)
    assert server.name == VALID_SERVER_NAME
    assert str(server.url) == VALID_URL
    assert server.username == VALID_USERNAME
    assert server.access_token == VALID_TOKEN
    assert server.verify_ssl is True
    assert server.timeout == 30

@pytest.mark.parametrize("url", [
    "https://example.com",
    "https://example.com/",
    "https://example.com/path/",
    "https://example.com:8080/",
])
def test_server_url_normalization(url, valid_server_data):
    """Test URL normalization adds trailing slash"""
    valid_server_data["url"] = url
    server = ServerConfig(**valid_server_data)
    assert str(server.url).endswith("/")

@pytest.mark.parametrize("timeout,valid", [
    (1, True),
    (30, True),
    (300, True),
    (0, False),
    (301, False),
    (-1, False),
])
def test_server_timeout_validation(valid_server_data, timeout, valid):
    """Test timeout validation constraints"""
    valid_server_data["timeout"] = timeout
    if valid:
        server = ServerConfig(**valid_server_data)
        assert server.timeout == timeout
    else:
        with pytest.raises(ValidationError):
            ServerConfig(**valid_server_data)

def test_server_optional_fields(valid_server_data):
    """Test optional fields can be set"""
    now = datetime.now()
    valid_server_data.update({
        "token_expires": now.isoformat(),
        "created_at": now.isoformat(),
        "last_used": now.isoformat(),
        "verify_ssl": False,
        "timeout": 15
    })
    server = ServerConfig(**valid_server_data)
    assert server.token_expires == now
    assert server.created_at == now
    assert server.last_used == now
    assert server.verify_ssl is False
    assert server.timeout == 15

# Settings Tests
def test_settings_minimal(valid_settings_data):
    """Test minimal valid Settings"""
    settings = Settings(**valid_settings_data)
    assert settings.default_server == VALID_SERVER_NAME
    assert settings.format == "markdown"
    assert settings.editor == "vim"
    assert settings.cache_enabled is True

@pytest.mark.parametrize("field,value", [
    ("format", "markdown"),
    ("format", "html"),
    ("format", "text"),
    ("editor", "vim"),
    ("editor", "nano"),
    ("editor", "code --wait"),
    ("cache_enabled", True),
    ("cache_enabled", False),
])
def test_settings_field_validation(valid_settings_data, field, value):
    """Test Settings field validation"""
    valid_settings_data[field] = value
    settings = Settings(**valid_settings_data)
    assert getattr(settings, field) == value

# MCPSettings Tests
def test_mcp_settings_minimal(valid_mcp_data):
    """Test minimal valid MCPSettings"""
    mcp = MCPSettings(**valid_mcp_data)
    assert mcp.host == "localhost"
    assert mcp.port == 8000
    assert mcp.default_server == VALID_SERVER_NAME

@pytest.mark.parametrize("port,valid", [
    (1024, True),
    (8000, True),
    (65535, True),
    (1023, False),
    (65536, False),
    (0, False),
])
def test_mcp_port_validation(valid_mcp_data, port, valid):
    """Test MCP port validation constraints"""
    valid_mcp_data["port"] = port
    if valid:
        mcp = MCPSettings(**valid_mcp_data)
        assert mcp.port == port
    else:
        with pytest.raises(ValidationError):
            MCPSettings(**valid_mcp_data)

# Config Tests
def test_config_minimal(valid_settings_data, valid_server_data):
    """Test minimal valid configuration"""
    config = Config(settings=valid_settings_data, servers={"test": valid_server_data})
    assert config.settings.default_server == VALID_SERVER_NAME
    assert "test" in config.servers
    assert config.servers["test"].name == VALID_SERVER_NAME
    assert config.mcp is None

def test_config_with_mcp(valid_settings_data, valid_server_data, valid_mcp_data):
    """Test config with MCP settings"""
    config = Config(
        settings=valid_settings_data,
        servers={"test": valid_server_data},
        mcp=valid_mcp_data
    )
    assert config.mcp is not None
    assert config.mcp.host == "localhost"
    assert config.mcp.port == 8000

def test_config_server_transformation(valid_settings_data, valid_server_data):
    """Test server.* keys are transformed into servers dict"""
    raw_data = {
        "settings": valid_settings_data,
        "server.test": valid_server_data
    }
    config = Config.model_validate(raw_data)
    assert "test" in config.servers
    assert config.servers["test"].name == VALID_SERVER_NAME

def test_config_multiple_servers(valid_settings_data, valid_server_data):
    """Test multiple servers in config"""
    server2_data = valid_server_data.copy()
    server2_data["name"] = "server2"
    raw_data = {
        "settings": valid_settings_data,
        "server.test": valid_server_data,
        "server.server2": server2_data
    }
    config = Config.model_validate(raw_data)
    assert len(config.servers) == 2
    assert "test" in config.servers
    assert "server2" in config.servers

# Error Cases
@pytest.mark.parametrize("missing_field", ["name", "url", "username", "access_token"])
def test_server_required_fields(valid_server_data, missing_field):
    """Test missing required fields raise validation errors"""
    del valid_server_data[missing_field]
    with pytest.raises(ValidationError):
        ServerConfig(**valid_server_data)

def test_settings_required_fields(valid_settings_data):
    """Test missing required fields in Settings"""
    del valid_settings_data["default_server"]
    with pytest.raises(ValidationError):
        Settings(**valid_settings_data)

def test_invalid_url(valid_server_data):
    """Test invalid URL raises validation error"""
    valid_server_data["url"] = "not-a-url"
    with pytest.raises(ValidationError):
        ServerConfig(**valid_server_data)

def test_invalid_datetime(valid_server_data):
    """Test invalid datetime format raises validation error"""
    valid_server_data["token_expires"] = "not-a-datetime"
    with pytest.raises(ValidationError):
        ServerConfig(**valid_server_data)
