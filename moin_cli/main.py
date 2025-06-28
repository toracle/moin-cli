import click
from getpass import getpass
from moin_cli.xmlrpc_client import WikiRPCClient

@click.group()
def main():
    """A Python CLI for MoinMoin wiki servers via XML-RPC with MCP server support.
    
    Supports authentication token management and page operations.
    """
    pass

@main.command()
def auth():
    """Get and store authentication token."""
    try:
        from moin_cli.config import load_config, save_config
        
        config = load_config()
        client = WikiRPCClient.from_config()
        password = getpass("Enter wiki password: ")
        token = client.get_auth_token(config['username'], password)
        
        # Save token to config
        config['token'] = token
        save_config(config)
        click.echo("Authentication token saved successfully")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.argument('pagename')
def get(pagename):
    """Get a page's content."""
    try:
        client = WikiRPCClient.from_config()
        content = client.get_page(pagename)
        click.echo(content)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.argument('pagename')
@click.argument('content')
def put(pagename, content):
    """Update a page's content."""
    try:
        client = WikiRPCClient.from_config()
        success = client.put_page(pagename, content)
        if success:
            click.echo(f"Successfully updated {pagename}")
        else:
            click.echo(f"Failed to update {pagename}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    main()
