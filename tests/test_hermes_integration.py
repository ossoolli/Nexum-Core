# -*- coding: utf-8 -*-
import pytest
import os
from unittest.mock import MagicMock, patch
from core.protocols.adapters.slack_adapter import slack_adapter
from core.inter_bot_protocol import inter_bot_protocol
from core.tool_registry import tool_registry
from core.learning.prompt_compiler import prompt_compiler

def test_slack_adapter_init():
    assert slack_adapter is not None
    # Test message sending with mock
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"ok": True}
        
        # Test with Slack Webhook
        slack_adapter.webhook_url = "https://hooks.slack.com/services/test"
        res = slack_adapter.send_message("C12345", "Test message")
        assert res is True
        
        # Test with Slack Bot Token
        slack_adapter.webhook_url = None
        slack_adapter.bot_token = "xoxb-test"
        res = slack_adapter.send_message("C12345", "Test message")
        assert res is True

def test_broadcast_to_platforms_slack():
    with patch("core.protocols.adapters.slack_adapter.slack_adapter.send_message") as mock_send:
        mock_send.return_value = True
        
        res = inter_bot_protocol.broadcast_to_platforms("Hello All", platforms=["slack"])
        assert res.get("slack") is True

def test_tool_registry_advanced_tools():
    all_schemas = tool_registry.get_all_tools_schema()
    assert "semantic_search_web" in all_schemas
    assert "advanced_scrape" in all_schemas

def test_prompt_compiler_registry():
    assert prompt_compiler is not None
    prompt = prompt_compiler.get_optimized_prompt("self_healing", "Standard Instructions")
    assert isinstance(prompt, str)
