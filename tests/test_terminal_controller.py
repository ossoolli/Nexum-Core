import os
import sys
import pytest
import asyncio

# Ensure project root is in PYTHONPATH for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.terminal_controller import terminal_controller, CommandValidationError

@pytest.fixture(autouse=True)
def clear_stats():
    # Reset stats before each test
    terminal_controller._execution_count = 0
    terminal_controller._blocked_count = 0
    yield
    # No cleanup needed

def test_forbidden_command_blocked():
    # rm -rf / should be blocked
    result = terminal_controller.execute('rm -rf /', skip_validation=False)
    assert not result['success']
    assert result['blocked']
    assert 'FORBIDDEN' in result.get('validation', {}).get('level', '')

def test_sensitive_command_allowed_with_warning():
    # "rm" alone is considered sensitive but not forbidden
    result = terminal_controller.execute('rm somefile.txt', skip_validation=False)
    # Since we don't have an approval workflow, it will be treated as safe (level SENSITIVE)
    # The controller does not block it, just marks as safe
    assert result['success'] or result['blocked'] is False
    # Validate that validation reports SENSITIVE level when run through validate_command directly
    validation = terminal_controller.validate_command('rm somefile.txt')
    assert validation['level'] == 'SENSITIVE'

def test_safe_command_execution():
    # Simple safe command
    result = terminal_controller.execute('echo hello', timeout=5)
    assert result['success']
    assert result['output'].strip() == 'hello'
    stats = terminal_controller.get_stats()
    assert stats['total_executions'] == 1
    assert stats['blocked_commands'] == 0

@pytest.mark.asyncio
async def test_async_execution():
    res = await terminal_controller.execute_async('echo async_test', timeout=5)
    assert res['success']
    assert res['output'].strip() == 'async_test'

def test_invalid_command_empty():
    result = terminal_controller.execute('', timeout=5)
    assert not result['success']
    assert 'Empty command' in result['output']

