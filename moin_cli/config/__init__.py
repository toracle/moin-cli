from .manager import ConfigManager
from .models import Config, ServerConfig, Settings, MCPSettings
from . import models

# Create default manager instance
_default_manager = ConfigManager()

# Expose manager methods as module-level functions
get = _default_manager.get_wiki_config
get_wiki_config = _default_manager.get_wiki_config
get_path = _default_manager.get_config_path
get_config_path = _default_manager.get_config_path
save = _default_manager.save_config
save_config = _default_manager.save_config
load = _default_manager.load_config
load_config = _default_manager.load_config

# Keep original class import for advanced usage
__all__ = [
    'ConfigManager', 
    'models',
    'Config', 'ServerConfig', 'Settings', 'MCPSettings',
    'get', 'get_wiki_config',
    'get_path', 'get_config_path',
    'save', 'save_config',
    'load', 'load_config'
]
