import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
from moin_cli.main import main

@patch('moin_cli.xmlrpc_client.WikiRPCClient.from_config')
def test_get_command_with_version_option(mock_from_config):
    """Test 'moin get pagename --version 5' calls get_page(pagename, revision=5)."""
    # Setup mock client
    mock_client = Mock()
    mock_client.get_page.return_value = "Version 5 content"
    mock_from_config.return_value = mock_client
    
    runner = CliRunner()
    result = runner.invoke(main, ['get', 'TestPage', '--version', '5'])
    
    assert result.exit_code == 0
    assert "Version 5 content" in result.output
    mock_client.get_page.assert_called_once_with('TestPage', revision=5)

@patch('moin_cli.xmlrpc_client.WikiRPCClient.from_config')
def test_get_command_without_version_option(mock_from_config):
    """Test 'moin get pagename' calls get_page(pagename, revision=None)."""
    # Setup mock client
    mock_client = Mock()
    mock_client.get_page.return_value = "Current content"
    mock_from_config.return_value = mock_client
    
    runner = CliRunner()
    result = runner.invoke(main, ['get', 'TestPage'])
    
    assert result.exit_code == 0
    assert "Current content" in result.output
    mock_client.get_page.assert_called_once_with('TestPage', revision=None)

@patch('moin_cli.xmlrpc_client.WikiRPCClient.from_config')
def test_get_command_with_history_option(mock_from_config):
    """Test 'moin get pagename --history' calls get_page_history(pagename)."""
    # Setup mock client
    mock_client = Mock()
    mock_client.get_page_history.return_value = [
        {'version': 5, 'lastModified': '2023-01-01', 'author': 'user1', 'comment': 'fixed typo'},
        {'version': 4, 'lastModified': '2022-12-01', 'author': 'user2', 'comment': 'initial'}
    ]
    mock_from_config.return_value = mock_client
    
    runner = CliRunner()
    result = runner.invoke(main, ['get', 'TestPage', '--history'])
    
    assert result.exit_code == 0
    assert "REV" in result.output
    assert "5" in result.output
    assert "fixed typo" in result.output
    mock_client.get_page_history.assert_called_once_with('TestPage')
