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
    
    if 'url' not in config or 'username' not in config:
        raise ValueError("Config must contain 'url' and 'username' keys")
    
    return config
