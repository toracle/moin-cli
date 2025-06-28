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
    
    if 'wikis' not in config:
        raise ValueError("Config must contain 'wikis' section")
    
    return config

def get_wiki_config(alias: str = None) -> dict:
    """Get configuration for a specific wiki alias"""
    config = load_config()
    wikis = config['wikis']
    
    if alias is None:
        # Return first wiki if no alias specified
        if not wikis:
            raise ValueError("No wikis configured")
        alias = next(iter(wikis.keys()))
    
    if alias not in wikis:
        available = ', '.join(wikis.keys())
        raise ValueError(f"Wiki '{alias}' not found. Available: {available}")
    
    return wikis[alias]
