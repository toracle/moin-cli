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
    """Initial setup and authentication for MoinMoin wiki.
    
    Prompts for server URL, username and password to create initial configuration.
    """
    try:
        from moin_cli.config import save_config
        from pathlib import Path
        import os

        # Create config directory if it doesn't exist
        config_dir = Path.home() / '.moin'
        config_dir.mkdir(exist_ok=True)

        # Prompt for configuration
        url = click.prompt("Enter wiki server URL (e.g. http://localhost:8080)")
        username = click.prompt("Enter wiki username")
        password = getpass("Enter wiki password: ")

        # Create client and get token
        endpoint = f"{url}/?action=xmlrpc2"
        client = WikiRPCClient(endpoint)
        token = client.get_auth_token(username, password)
        
        # Save complete config
        config = {
            'url': url,
            'username': username,
            'token': token
        }
        save_config(config)
        click.echo("Configuration saved successfully")
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
