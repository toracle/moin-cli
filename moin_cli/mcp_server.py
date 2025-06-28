from xmlrpc.server import SimpleXMLRPCServer
from typing import Dict

class MCPServer:
    def __init__(self, host: str = 'localhost', port: int = 8000):
        self.server = SimpleXMLRPCServer((host, port))
        self.pages: Dict[str, str] = {}

    def start(self):
        """Start the MCP server."""
        self.server.register_function(self.read_page, 'getPage')
        self.server.register_function(self.write_page, 'putPage')
        self.server.register_function(self.list_pages, 'getAllPages')
        self.server.register_function(self.search_pages, 'searchPages')
        self.server.serve_forever()

    def read_page(self, pagename: str) -> str:
        return self.pages.get(pagename, "")

    def write_page(self, pagename: str, content: str) -> bool:
        self.pages[pagename] = content
        return True

    def list_pages(self) -> list:
        return list(self.pages.keys())

    def search_pages(self, query: str) -> list:
        return [p for p, c in self.pages.items() if query.lower() in c.lower()]
