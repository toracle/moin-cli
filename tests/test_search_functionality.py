"""Test search functionality."""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from moin_cli.main import main
from moin_cli.xmlrpc_client import WikiRPCClient
from moin_cli.config.models import ServerConfig


def test_search_pages_method():
    """Test that search_pages method works correctly."""
    # Mock the XML-RPC server
    mock_server = Mock()
    mock_server.searchPages.return_value = ["HomePage", "HelpPage"]
    
    with patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        client = WikiRPCClient("http://example.com/?action=xmlrpc2")
        results = client.search_pages("help")
        
        assert isinstance(results, list)
        assert results == ["HomePage", "HelpPage"]
        mock_server.searchPages.assert_called_once_with("help")


def test_search_command_basic():
    """Test that search command finds matching pages."""
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
    mock_server.searchPages.return_value = ["WikiPage", "WikiHelp", "SandBox"]
    
    with patch('moin_cli.config.get_wiki_config', return_value=server_config), \
         patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        
        runner = CliRunner()
        result = runner.invoke(main, ['search', 'wiki', '--server', 'test'])
        
        assert result.exit_code == 0
        assert "WikiPage" in result.output
        assert "WikiHelp" in result.output
        assert "SandBox" in result.output


def test_search_command_no_results():
    """Test search command with no matching pages."""
    server_config = ServerConfig(
        name="test",
        url="http://localhost:8080/",
        username="testuser",
        access_token="test-token",
        verify_ssl=True,
        timeout=30
    )
    
    mock_server = Mock()
    mock_server.searchPages.return_value = []
    
    with patch('moin_cli.config.get_wiki_config', return_value=server_config), \
         patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        
        runner = CliRunner()
        result = runner.invoke(main, ['search', 'nonexistent', '--server', 'test'])
        
        assert result.exit_code == 0
        # Should show no output for no results


def test_search_command_error_handling():
    """Test search command error handling."""
    with patch('moin_cli.config.get_wiki_config', side_effect=Exception("Config error")):
        runner = CliRunner()
        result = runner.invoke(main, ['search', 'test', '--server', 'test'])
        
        assert result.exit_code == 0  # Click handles exceptions internally
        assert "Error: Config error" in result.output


def test_search_pages_empty_query():
    """Test search with empty query string."""
    mock_server = Mock()
    mock_server.searchPages.return_value = []
    
    with patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        client = WikiRPCClient("http://example.com/?action=xmlrpc2")
        results = client.search_pages("")
        
        assert results == []
        mock_server.searchPages.assert_called_once_with("")