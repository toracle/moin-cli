from pathlib import Path
import toml

def get_config_path() -> Path:
    """Get the path to the configuration file"""
    return Path.home() / ".moin" / "config.toml"

def save_config(config: dict) -> None:
    """Save configuration to TOML file"""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        toml.dump(config, f)

def load_config() -> dict:
    """Load configuration from TOML file"""
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, 'r') as f:
        config = toml.load(f)
    
    if 'settings' not in config:
        raise ValueError("Config must contain 'settings' section")
    if 'default_server' not in config['settings']:
        raise ValueError("Config must specify 'default_server' in [settings]")
    
    return config

def get_wiki_config(alias: str = None) -> dict:
    """Get configuration for a specific wiki alias"""
    config = load_config()
    
    if alias is None:
        alias = config['settings']['default_server']
    
    server_key = f"server.{alias}"
    if server_key not in config:
        available = [k.split('.')[1] for k in config.keys() if k.startswith('server.')]
        raise ValueError(f"Server '{alias}' not found. Available: {', '.join(available)}")
    
    server_config = config[server_key]
    if 'name' not in server_config:
        server_config['name'] = alias  # Ensure name is set
    
    return server_config
