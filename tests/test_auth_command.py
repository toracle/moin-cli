import pytest
from click.testing import CliRunner
from moin_cli.main import main
from unittest.mock import patch, MagicMock

@patch('moin_cli.main.WikiRPCClient')
@patch('moin_cli.config.save_config')
@patch('pathlib.Path.mkdir') # Avoid creating real directories
def test_auth_success(mock_mkdir, mock_save, mock_client_class):
    """Verify auth command creates proper config with token"""
    # Setup mock client instance
    mock_client = MagicMock()
    mock_client.get_auth_token.return_value = 'test_token123'
    mock_client_class.return_value = mock_client
    
    # Run command with simulated input
    # 1. alias: test_wiki
    # 2. url: https://wiki.test
    # 3. username: test_user
    # 4. password: test_pass
    runner = CliRunner()
    result = runner.invoke(main, ['auth'], input='test_wiki\nhttps://wiki.test\ntest_user\ntest_pass\n')
    
    # Verify success message
    assert result.exit_code == 0
    assert 'Configuration saved successfully' in result.output
    
    # Verify API called with correct credentials
    mock_client_class.assert_called_once_with('https://wiki.test/?action=xmlrpc2')
    mock_client.get_auth_token.assert_called_once_with('test_user', 'test_pass')
    
    # Verify saved config structure
    from moin_cli.config.models import Config
    saved_config = mock_save.call_args[0][0]
    assert isinstance(saved_config, Config)
    server_config = saved_config.servers['test_wiki']
    assert server_config.name == 'test_wiki'
    assert str(server_config.url).rstrip('/') == 'https://wiki.test'
    assert server_config.access_token == 'test_token123'