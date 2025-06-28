import xmlrpc.client
from typing import Optional
import toml
from pathlib import Path
from moin_cli.config import get_config_path, load_config, save_config

class WikiRPCClient:
    def __init__(self, endpoint: str):
        """Initialize client with WikiRPC v2 endpoint URL."""
        self.server = xmlrpc.client.ServerProxy(endpoint)

    @classmethod
    def from_config(cls, alias: str = None) -> "WikiRPCClient":
        """Create client from config file."""
        from moin_cli.config import get_wiki_config
        wiki_config = get_wiki_config(alias)
        endpoint = f"{wiki_config['url']}/?action=xmlrpc2"
        return cls(endpoint)

    def get_page(self, pagename: str) -> str:
        """Get page content using WikiRPC v2 getPage."""
        return self.server.getPage(pagename)

    def get_auth_token(self, username: str, password: str) -> str:
        """Get authentication token from MoinMoin server."""
        return self.server.getAuthToken(username, password)

    def put_page(self, pagename: str, content: str, token: Optional[str] = None, alias: str = None) -> bool:
        """Update page content using WikiRPC v2 putPage with authentication.
        
        Args:
            pagename: Name of page to update
            content: New page content
            token: Optional auth token. If None, will try to load from config.
            alias: Wiki alias to use for token lookup
        """
        if token is None:
            from moin_cli.config import get_wiki_config
            wiki_config = get_wiki_config(alias)
            token = wiki_config.get('access_token')
            if token is None:
                raise ValueError("No auth token provided and none found in config")

        # Use multicall to apply token and put page in one request
        multicall = xmlrpc.client.MultiCall(self.server)
        multicall.applyAuthToken(token)
        multicall.putPage(pagename, content)
        return tuple(multicall())[-1]  # Return just the putPage result
