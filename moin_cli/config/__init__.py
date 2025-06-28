from pathlib import Path
from typing import Optional
import toml
from .models import Config, ServerConfig, Settings, MCPSettings

def get_config_path() -> Path:
    """Get the path to the configuration file"""
    return Path.home() / ".moin" / "config.toml"

def save_config(config: Config) -> None:
    """Save configuration to TOML file"""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        toml.dump(config.model_dump(), f)

def load_config() -> Config:
    """Load and validate configuration from TOML file"""
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, 'r') as f:
        config_data = toml.load(f)
    
    # Convert to Pydantic model which will handle validation
    return Config(**config_data)

def get_wiki_config(alias: str = None) -> ServerConfig:
    """Get configuration for a specific wiki alias"""
    config = load_config()
    
    if alias is None:
        alias = config.settings.default_server
    
    if alias not in config.servers:
        available = list(config.servers.keys())
        raise ValueError(f"Server '{alias}' not found. Available: {', '.join(available)}")
    
    server_config = config.servers[alias]
    if server_config.name is None:
        server_config.name = alias  # Ensure name is set
    
    return server_config
