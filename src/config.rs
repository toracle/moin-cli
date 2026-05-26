use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use directories::ProjectDirs;
use std::fs;
use anyhow::{Context, Result};

#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    pub settings: Settings,
    pub servers: std::collections::HashMap<String, ServerConfig>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    pub default_server: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ServerConfig {
    pub name: String,
    pub url: String,
    pub username: String,
    pub access_token: Option<String>,
}

pub fn get_config_dir() -> PathBuf {
    let project_dirs = ProjectDirs::from("com", "moin", "moin-cli")
        .expect("Could not determine config directory");
    project_dirs.config_dir().to_path_buf()
}

pub fn get_config_path() -> PathBuf {
    get_config_dir().join("config.toml")
}

pub fn load_config() -> Result<Config> {
    let config_path = get_config_path();
    let config_content = fs::read_to_string(&config_path)
        .with_context(|| format!("Failed to read config file: {}", config_path.display()))?;
    
    toml::from_str(&config_content)
        .with_context(|| "Failed to parse config file".to_string())
}

pub fn save_config(config: &Config) -> Result<()> {
    let config_dir = get_config_dir();
    if !config_dir.exists() {
        fs::create_dir_all(&config_dir)
            .with_context(|| format!("Failed to create config directory: {}", config_dir.display()))?;
    }
    
    let config_content = toml::to_string(config)
        .with_context(|| "Failed to serialize config".to_string())?;
    
    fs::write(get_config_path(), config_content)
        .with_context(|| "Failed to write config file".to_string())
}
