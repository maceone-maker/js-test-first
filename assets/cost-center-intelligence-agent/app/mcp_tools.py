"""MCP tool loading indirection layer.

This module is the single point for loading MCP tools from the Agent Gateway.
Import and patch this module in tests — never import directly from sap_cloud_sdk.agentgateway.
"""
from mcp_providers.agw import get_mcp_tools as _agw_get_mcp_tools


async def get_mcp_tools() -> list:
    """Load MCP tools from the Agent Gateway.

    Returns an empty list if the gateway is unavailable (e.g. during local testing
    when IBD_TESTING=true causes conftest.py to patch this function).
    """
    return await _agw_get_mcp_tools()
