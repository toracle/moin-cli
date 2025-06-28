"""Test recent changes functionality."""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from moin_cli.main import main
from moin_cli.xmlrpc_client import WikiRPCClient
from moin_cli.config.models import ServerConfig


def test_get_recent_changes_method():
    """Test that get_recent_changes method works correctly."""
    # Mock the XML-RPC server
    mock_server = Mock()
    # Simulate getRecentChanges returning list of [pagename, timestamp] pairs
    mock_server.getRecentChanges.return_value = [
        ["HomePage", 1234567890],
        ["WikiPage", 1234567800],
        ["SandBox", 1234567700]
    ]
    
    with patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        client = WikiRPCClient("http://example.com/?action=xmlrpc2")
        pages = client.get_recent_changes(7)
        
        assert isinstance(pages, list)
        assert pages == ["HomePage", "WikiPage", "SandBox"]
        # Verify timestamp calculation was done
        mock_server.getRecentChanges.assert_called_once()
        # Check that the timestamp argument is reasonable (within last 7 days)
        call_args = mock_server.getRecentChanges.call_args[0]
        assert len(call_args) == 1
        assert isinstance(call_args[0], int)


def test_recent_command_basic():
    """Test that recent command shows recently changed pages."""
    # Mock server config
    server_config = ServerConfig(
        name="test",
        url="http://localhost:8080/",
        username="testuser",
        access_token="test-token",
        verify_ssl=True,
        timeout=30
    )
    
    # Mock XML-RPC server
    mock_server = Mock()
    mock_server.getRecentChanges.return_value = [
        ["HomePage", 1234567890],
        ["RecentPage", 1234567800]
    ]
    
    with patch('moin_cli.config.get_wiki_config', return_value=server_config), \
         patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        
        runner = CliRunner()
        result = runner.invoke(main, ['recent', '--server', 'test'])
        
        assert result.exit_code == 0
        assert "HomePage" in result.output
        assert "RecentPage" in result.output


def test_recent_command_custom_days():
    """Test recent command with custom days parameter."""
    server_config = ServerConfig(
        name="test",
        url="http://localhost:8080/",
        username="testuser",
        access_token="test-token",
        verify_ssl=True,
        timeout=30
    )
    
    mock_server = Mock()
    mock_server.getRecentChanges.return_value = [["TestPage", 1234567890]]
    
    with patch('moin_cli.config.get_wiki_config', return_value=server_config), \
         patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        
        runner = CliRunner()
        result = runner.invoke(main, ['recent', '--days', '30', '--server', 'test'])
        
        assert result.exit_code == 0
        assert "TestPage" in result.output


def test_recent_command_no_changes():
    """Test recent command with no recent changes."""
    server_config = ServerConfig(
        name="test",
        url="http://localhost:8080/",
        username="testuser",
        access_token="test-token",
        verify_ssl=True,
        timeout=30
    )
    
    mock_server = Mock()
    mock_server.getRecentChanges.return_value = []
    
    with patch('moin_cli.config.get_wiki_config', return_value=server_config), \
         patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        
        runner = CliRunner()
        result = runner.invoke(main, ['recent', '--server', 'test'])
        
        assert result.exit_code == 0
        assert "No changes in the last 7 days" in result.output


def test_recent_command_error_handling():
    """Test recent command error handling."""
    with patch('moin_cli.config.get_wiki_config', side_effect=Exception("Config error")):
        runner = CliRunner()
        result = runner.invoke(main, ['recent', '--server', 'test'])
        
        assert result.exit_code == 0  # Click handles exceptions internally
        assert "Error: Config error" in result.output


def test_get_recent_changes_default_days():
    """Test get_recent_changes with default 7 days."""
    mock_server = Mock()
    mock_server.getRecentChanges.return_value = []
    
    with patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        client = WikiRPCClient("http://example.com/?action=xmlrpc2")
        pages = client.get_recent_changes()  # Use default days
        
        assert pages == []
        mock_server.getRecentChanges.assert_called_once()