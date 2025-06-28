import click
from moin_cli.xmlrpc_client import WikiRPCClient

@click.group()
def main():
    """A Python CLI for MoinMoin wiki servers via XML-RPC with MCP server support."""
    pass

@main.command()
@click.argument('pagename')
def read(pagename):
    """Read a wiki page."""
    try:
        client = WikiRPCClient.from_config()
        content = client.get_page(pagename)
        click.echo(content)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    main()
