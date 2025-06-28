from pathlib import Path
from typing import Optional
import toml
from .models import Config, ServerConfig, Settings, MCPSettings

class ConfigManager:
    """Manages configuration file operations for the MoinMoin CLI"""
    
    def __init__(self):
        self._config_path = None

    def get_config_path(self) -> Path:
        """Get the path to the configuration file"""
        if self._config_path is None:
            self._config_path = Path.home() / ".moin" / "config.toml"
        return self._config_path

    def save_config(self, config: Config) -> None:
        """Save configuration to TOML file
        
        Args:
            config: Config object to save
        """
        config_path = self.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            toml.dump(config.model_dump(), f)

    def load_config(self) -> Config:
        """Load and validate configuration from TOML file"""
        config_path = self.get_config_path()
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = toml.load(f)
        
        # Convert to Pydantic model which will handle validation
        return Config(**config_data)

    def get_wiki_config(self, alias: str = None) -> ServerConfig:
        """Get configuration for a specific wiki alias"""
        config = self.load_config()
        
        if alias is None:
            alias = config.settings.default_server
        
        if alias not in config.servers:
            available = list(config.servers.keys())
            raise ValueError(f"Server '{alias}' not found. Available: {', '.join(available)}")
        
        server_config = config.servers[alias]
        if server_config.name is None:
            server_config.name = alias  # Ensure name is set
        
        return server_config
