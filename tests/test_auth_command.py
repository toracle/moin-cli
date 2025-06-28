import pytest
from click.testing import CliRunner
from moin_cli.main import auth
from moin_cli.config.models import ServerConfig

def test_auth_success(mocker):
    """Verify auth command creates proper config with token"""
    # Mock user inputs
    mocker.patch('click.prompt', side_effect=['test_wiki', 'https://wiki.test', 'test_user'])
    mocker.patch('getpass.getpass', return_value='test_pass')
    
    # Mock API to return token
    mock_rpc = mocker.patch('moin_cli.xmlrpc_client.WikiRPCClient.get_auth_token')
    mock_rpc.return_value = {'token': 'test_token123'}
    
    # Mock config save
    mock_save = mocker.patch('moin_cli.config.save_config')
    
    # Run command
    runner = CliRunner()
    result = runner.invoke(auth)
    
    # Debug output first
    print("\nDEBUG OUTPUT:")
    print(result.output)
    print(f"Exit code: {result.exit_code}")
    print(f"Mock call counts - RPC: {mock_rpc.call_count}, Save: {mock_save.call_count}")
    
    # Verify API called with correct credentials
    mock_rpc.assert_called_once_with(
        username='test_user',
        password='test_pass',
        wiki_url='https://wiki.test'
    )
    
    # Verify saved config structure
    saved_config = mock_save.call_args[0][0]
    assert isinstance(saved_config, ServerConfig)
    assert saved_config.name == 'test_wiki'
    assert saved_config.url == 'https://wiki.test'
    assert saved_config.access_token == 'test_token123'
    
    # Verify success message
    assert 'Authentication successful' in result.output
