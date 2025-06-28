from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

class ServerConfig(BaseModel):
    """Configuration for a single wiki server"""
    name: str
    url: HttpUrl
    username: str
    access_token: str
    token_expires: Optional[datetime] = None
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    verify_ssl: bool = True
    timeout: int = Field(default=30, ge=1, le=300)

    @field_validator('url')
    def ensure_trailing_slash(cls, v: HttpUrl) -> HttpUrl:
        """Ensure URL ends with trailing slash"""
        if not str(v).endswith('/'):
            return HttpUrl(f"{str(v)}/")
        return v

class Settings(BaseModel):
    """Global settings configuration"""
    default_server: str
    format: str = "markdown"
    editor: str = "vim"
    cache_enabled: bool = True

class MCPSettings(BaseModel):
    """MCP (Moin Control Panel) settings"""
    host: str = "localhost"
    port: int = Field(default=8000, ge=1024, le=65535)
    default_server: str

class Config(BaseModel):
    """Root configuration model"""
    settings: Settings
    mcp: Optional[MCPSettings] = None
    servers: dict[str, ServerConfig] = {}

    @model_validator(mode='before')
    def transform_server_keys(cls, data: dict) -> dict:
        """Move server.* keys into servers dict before validation"""
        if not isinstance(data, dict):
            return data
            
        servers = {}
        other = {}
        
        for k, v in data.items():
            if k.startswith('server.'):
                server_name = k.split('.')[1]
                servers[server_name] = v
            else:
                other[k] = v
                
        if servers:
            other['servers'] = servers
            
        return other
