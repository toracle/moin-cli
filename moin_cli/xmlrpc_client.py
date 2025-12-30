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
        endpoint = f"{wiki_config.url}/?action=xmlrpc2"
        return cls(endpoint)

    def get_page(self, pagename: str, revision: Optional[int] = None) -> str:
        """Get page content using WikiRPC v2 getPage or getPageVersion.
        
        Args:
            pagename: Name of the page to retrieve
            revision: Optional revision number. If provided, uses getPageVersion.
        """
        if revision:
            return self.server.getPageVersion(pagename, revision)
        return self.server.getPage(pagename)

    def get_page_history(self, pagename: str) -> list[dict]:
        """Get history of a page using getRecentChangesWithAttributes.
        
        Args:
            pagename: Name of the page to get history for
            
        Returns:
            List of dictionaries containing version information
        """
        from datetime import datetime, timedelta
        # Look back far enough to get history, e.g., 10 years
        since = datetime.utcnow() - timedelta(days=3650)
        
        try:
            # getRecentChangesWithAttributes(date, pagenames)
            results = self.server.getRecentChangesWithAttributes(since, [pagename])
            if not results or not isinstance(results, list):
                return []
            
            # The result is a list of results per pagename. 
            # Since we requested one pagename, we look at results[0].
            history = results[0]
            if not isinstance(history, list):
                return []
                
            return history
        except Exception:
            # Fallback or just return empty if method not supported
            return []

    def get_auth_token(self, username: str, password: str) -> str:
        """Get authentication token from MoinMoin server."""
        return self.server.getAuthToken(username, password)

    def get_all_pages(self) -> list[str]:
        """Get list of all page names from the wiki using WikiRPC v2 getAllPages."""
        return self.server.getAllPages()

    def search_pages(self, query: str) -> list[str]:
        """Search for pages containing the query string using WikiRPC v2 searchPages.
        
        Args:
            query: Search string to look for in page contents
            
        Returns:
            List of page names that match the search
        """
        return self.server.searchPages(query)

    def get_recent_changes(self, days: int = 7) -> list[str]:
        """Get list of recently changed pages using WikiRPC v2 getRecentChanges.
        
        Args:
            days: Number of days to look back for changes (default: 7)
            
        Returns:
            List of page names that were recently changed
        """
        from datetime import datetime, timedelta
        since = datetime.utcnow() - timedelta(days=days)
        changes = self.server.getRecentChanges(since)
        
        # Handle different response formats:
        if not changes:
            return []
        # If first item is a dictionary with 'name' field
        if isinstance(changes[0], dict) and 'name' in changes[0]:
            return [change['name'] for change in changes]
        # If first item is a tuple (pagename, timestamp)
        if isinstance(changes[0], (tuple, list)) and len(changes[0]) == 2:
            return [page for page, _ in changes]
        # If just page names are returned
        return list(changes)

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
            token = wiki_config.access_token
            if token is None:
                raise ValueError("No auth token provided and none found in config")

        # Use multicall to apply token and put page in one request
        multicall = xmlrpc.client.MultiCall(self.server)
        multicall.applyAuthToken(token)
        multicall.putPage(pagename, content)
        return tuple(multicall())[-1]  # Return just the putPage result
