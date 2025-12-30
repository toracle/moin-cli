"""Regression tests for get command functionality."""

import pytest
from unittest.mock import Mock, patch
from moin_cli.xmlrpc_client import WikiRPCClient
from moin_cli.config.models import ServerConfig


def test_get_command_with_server_config_model():
    """Test that get command works with ServerConfig Pydantic model (not dict).
    
    Regression test for: Error: 'ServerConfig' object is not subscriptable
    This occurred when get_wiki_config returns ServerConfig model but code 
    tries to use .get('access_token') as if it's a dictionary.
    """
    # Create a ServerConfig model like the real config system returns
    server_config = ServerConfig(
        name="test",
        url="http://localhost:8080/",
        username="testuser",
        access_token="test-token-123",
        verify_ssl=True,
        timeout=30
    )
    
    # Mock the config loading to return our ServerConfig model
    with patch('moin_cli.config.get_wiki_config', return_value=server_config):
        # Mock the XML-RPC server
        mock_server = Mock()
        mock_server.getPage.return_value = "Test page content"
        
        with patch('xmlrpc.client.ServerProxy', return_value=mock_server):
            # This should not raise 'ServerConfig' object is not subscriptable
            client = WikiRPCClient.from_config("test")
            content = client.get_page("FrontPage")
            
            assert content == "Test page content"
            mock_server.getPage.assert_called_once_with("FrontPage")


def test_get_page_with_revision():
    """Test that get_page calls getPageVersion when revision is provided."""
    server_config = ServerConfig(
        name="test",
        url="http://localhost:8080/",
        username="testuser",
        access_token="test-token-123",
        verify_ssl=True,
        timeout=30
    )
    
    with patch('moin_cli.config.get_wiki_config', return_value=server_config):
        mock_server = Mock()
        mock_server.getPageVersion.return_value = "Test page version 5 content"
        
        with patch('xmlrpc.client.ServerProxy', return_value=mock_server):
            client = WikiRPCClient.from_config("test")
            content = client.get_page("FrontPage", revision=5)
            
            assert content == "Test page version 5 content"
            mock_server.getPageVersion.assert_called_once_with("FrontPage", 5)


def test_put_page_with_server_config_model():
    """Test that put_page works with ServerConfig Pydantic model.
    
    Regression test for the same issue in put_page method.
    """
    server_config = ServerConfig(
        name="test", 
        url="http://localhost:8080/",
        username="testuser",
        access_token="test-token-456",
        verify_ssl=True,
        timeout=30
    )
    
    with patch('moin_cli.config.get_wiki_config', return_value=server_config):
        mock_server = Mock()
        mock_multicall = Mock()
        mock_multicall.return_value = [True, True]  # applyAuthToken, putPage results
        
        with patch('xmlrpc.client.ServerProxy', return_value=mock_server), \
             patch('xmlrpc.client.MultiCall', return_value=mock_multicall):
            
            client = WikiRPCClient.from_config("test")
            result = client.put_page("TestPage", "New content", alias="test")
            
            assert result is True