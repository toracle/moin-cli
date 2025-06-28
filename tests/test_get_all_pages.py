"""Test get_all_pages functionality."""

import pytest
from unittest.mock import Mock, patch
from moin_cli.xmlrpc_client import WikiRPCClient


def test_get_all_pages():
    """Test that get_all_pages returns list of page names."""
    # Mock the XML-RPC server
    mock_server = Mock()
    mock_server.getAllPages.return_value = ["FrontPage", "HomePage", "SandBox", "WikiWikiWeb"]
    
    with patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        client = WikiRPCClient("http://example.com/?action=xmlrpc2")
        pages = client.get_all_pages()
        
        assert isinstance(pages, list)
        assert pages == ["FrontPage", "HomePage", "SandBox", "WikiWikiWeb"]
        mock_server.getAllPages.assert_called_once()


def test_get_all_pages_empty():
    """Test get_all_pages with empty wiki."""
    mock_server = Mock()
    mock_server.getAllPages.return_value = []
    
    with patch('xmlrpc.client.ServerProxy', return_value=mock_server):
        client = WikiRPCClient("http://example.com/?action=xmlrpc2")
        pages = client.get_all_pages()
        
        assert pages == []
        mock_server.getAllPages.assert_called_once()