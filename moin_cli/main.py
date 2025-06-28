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
        alias = click.prompt("Enter wiki name/alias (e.g. local, production)")
        url = click.prompt("Enter wiki server URL (e.g. http://localhost:8080)")
        username = click.prompt("Enter wiki username")
        password = getpass("Enter wiki password: ")

        # Create client and get token
        endpoint = f"{url}/?action=xmlrpc2"
        client = WikiRPCClient(endpoint)
        token = client.get_auth_token(username, password)
        
        # Save complete config with sections
        config = {
            'wikis': {
                alias: {
                    'url': url,
                    'username': username,
                    'token': token
                }
            }
        }
        save_config(config)
        click.echo("Configuration saved successfully")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.argument('pagename')
@click.option('--server', '-s', help='Wiki server alias to use')
@click.option('--quiet', '-q', is_flag=True, help='Suppress status messages')
def get(pagename, server, quiet):
    """Get a page's content."""
    try:
        client = WikiRPCClient.from_config(server)
        content = client.get_page(pagename)
        if not quiet:
            click.echo(f"Retrieved content for {pagename}")
        click.echo(content)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.argument('pagename')
@click.argument('content')
@click.option('--server', '-s', help='Wiki server alias to use')
def put(pagename, content, server):
    """Update a page's content."""
    try:
        client = WikiRPCClient.from_config(server)
        success = client.put_page(pagename, content, alias=server)
        if success:
            click.echo(f"Successfully updated {pagename}")
        else:
            click.echo(f"Failed to update {pagename}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.option('--server', '-s', help='Wiki server alias to use')
def list(server):
    """List all pages on the wiki."""
    try:
        client = WikiRPCClient.from_config(server)
        pages = client.get_all_pages()
        for page in pages:
            click.echo(page)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.argument('query')
@click.option('--server', '-s', help='Wiki server alias to use')
def search(query, server):
    """Search for pages containing the query text."""
    try:
        client = WikiRPCClient.from_config(server)
        results = client.search_pages(query)
        for page in results:
            click.echo(page)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.option('--days', '-d', type=int, default=7, help='Number of days to look back (default: 7)')
@click.option('--server', '-s', help='Wiki server alias to use')
def recent(days, server):
    """Show pages changed in the last N days."""
    try:
        client = WikiRPCClient.from_config(server)
        pages = client.get_recent_changes(days)
        if not pages:
            click.echo(f"No changes in the last {days} days")
            return
            
        for page in pages:
            click.echo(page)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    main()
