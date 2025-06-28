import xmlrpc.client
from typing import List, Optional

class MoinMoinClient:
    def __init__(self, url: str):
        self.server = xmlrpc.client.ServerProxy(url)

    def read_page(self, pagename: str) -> str:
        """Get the content of a wiki page."""
        return self.server.getPage(pagename)

    def write_page(self, pagename: str, content: str) -> bool:
        """Update or create a wiki page."""
        return self.server.putPage(pagename, content)

    def list_pages(self) -> List[str]:
        """List all pages in the wiki."""
        return self.server.getAllPages()

    def search(self, query: str) -> List[str]:
        """Search for pages containing the query."""
        return self.server.searchPages(query)
