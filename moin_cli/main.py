import click
from xmlrpc_client import MoinMoinClient
from mcp_server import MCPServer

@click.group()
def main():
    """A Python CLI for MoinMoin wiki servers via XML-RPC with MCP server support."""
    pass

# XML-RPC Client Commands
@main.group()
def client():
    """MoinMoin XML-RPC client operations."""
    pass

@client.command()
@click.argument('url')
@click.argument('pagename')
def read(url, pagename):
    """Read a wiki page."""
    client = MoinMoinClient(url)
    click.echo(client.read_page(pagename))

@client.command()
@click.argument('url')
@click.argument('pagename')
@click.argument('content')
def write(url, pagename, content):
    """Write to a wiki page."""
    client = MoinMoinClient(url)
    if client.write_page(pagename, content):
        click.echo(f"Page '{pagename}' updated successfully")

@client.command()
@click.argument('url')
def list(url):
    """List all wiki pages."""
    client = MoinMoinClient(url)
    for page in client.list_pages():
        click.echo(page)

@client.command()
@click.argument('url')
@click.argument('query')
def search(url, query):
    """Search wiki pages."""
    client = MoinMoinClient(url)
    for page in client.search(query):
        click.echo(page)

# MCP Server Commands
@main.command()
@click.option('--host', default='localhost', help='Server host')
@click.option('--port', default=8000, help='Server port')
def serve(host, port):
    """Start the MCP server."""
    server = MCPServer(host, port)
    click.echo(f"Starting MCP server on {host}:{port}")
    server.start()

if __name__ == "__main__":
    main()
