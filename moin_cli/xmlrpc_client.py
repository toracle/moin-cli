import xmlrpc.client
from typing import Optional
import toml
from pathlib import Path

class WikiRPCClient:
    def __init__(self, endpoint: str):
        """Initialize client with WikiRPC v2 endpoint URL."""
        self.server = xmlrpc.client.ServerProxy(endpoint)

    @classmethod
    def from_config(cls, config_path: str = "~/.moin/config.toml") -> "WikiRPCClient":
        """Create client from config file."""
        config_file = Path(config_path).expanduser()
        config = toml.load(config_file)
        endpoint = f"{config['url']}/?action=xmlrpc2"
        return cls(endpoint)

    def get_page(self, pagename: str) -> str:
        """Get page content using WikiRPC v2 getPage."""
        return self.server.getPage(pagename)

    def put_page(self, pagename: str, content: str) -> bool:
        """Update page content using WikiRPC v2 putPage."""
        return self.server.putPage(pagename, content)
