"""Test list command functionality."""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from moin_cli.main import main
from moin_cli.config.models import ServerConfig


def test_list_command_basic():
    """Test that list command shows all pages."""
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
    mock_server.getAllPages.return_value = ["FrontPage", "HomePage", "SandBox"]
    
    with patch('moin_cli.config.get_wiki_config', return_value=server_config), \
         patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        
        runner = CliRunner()
        result = runner.invoke(main, ['list', '--server', 'test'])
        
        assert result.exit_code == 0
        assert "Pages on wiki:" in result.output
        assert "- FrontPage" in result.output
        assert "- HomePage" in result.output
        assert "- SandBox" in result.output


def test_list_command_empty_wiki():
    """Test list command with empty wiki."""
    server_config = ServerConfig(
        name="test",
        url="http://localhost:8080/",
        username="testuser",
        access_token="test-token", 
        verify_ssl=True,
        timeout=30
    )
    
    mock_server = Mock()
    mock_server.getAllPages.return_value = []
    
    with patch('moin_cli.config.get_wiki_config', return_value=server_config), \
         patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        
        runner = CliRunner()
        result = runner.invoke(main, ['list', '--server', 'test'])
        
        assert result.exit_code == 0
        assert "Pages on wiki:" in result.output
        # Should show header but no page items


def test_list_command_error_handling():
    """Test list command error handling.""" 
    with patch('moin_cli.config.get_wiki_config', side_effect=Exception("Config error")):
        runner = CliRunner()
        result = runner.invoke(main, ['list', '--server', 'test'])
        
        assert result.exit_code == 0  # Click handles exceptions internally
        assert "Error: Config error" in result.output