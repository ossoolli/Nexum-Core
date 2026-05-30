import os
import pytest
from agents.deployment_hand import deployment_hand
from agents.accountant_agent import accountant_agent
from agents.marketing_agent import marketing_agent
from agents.tool_hunter import tool_hunter
from services.bi_service import bi_service
from services.email_service import email_service
from core.self_healer import self_healer
from core.plugin_loader import plugin_loader

def test_agents_instantiation():
    """Verify that all new agents are successfully instantiated and have expected metadata."""
    assert deployment_hand.name == "deployment_hand"
    assert accountant_agent.name == "accountant_agent"
    assert marketing_agent.name == "marketing_agent"
    assert tool_hunter.name == "tool_hunter"

def test_bi_service_initialization():
    """Verify that BIService is properly initialized with a dynamic, valid path."""
    assert bi_service.db_path is not None
    assert os.path.exists(os.path.dirname(bi_service.db_path))
    assert "nexum_business.db" in bi_service.db_path

def test_self_healer_initialization():
    """Verify that SelfHealer has a dynamic base directory and uses correct dynamic paths."""
    assert self_healer.base_dir is not None
    assert os.path.isabs(self_healer.base_dir)

def test_plugin_loader_initialization():
    """Verify that DynamicPluginLoader points to a dynamic active plugins directory."""
    assert plugin_loader.plugins_dir is not None
    assert "plugins" in plugin_loader.plugins_dir
    assert "active" in plugin_loader.plugins_dir
