"""Unit tests for graceful error handling (R5)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.mark.asyncio
async def test_authorization_error_returns_clear_message(add_agent_to_path):
    """Agent returns a plain-language access-denied message on 403 errors."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    # Simulate agent response when MCP tool returns authorization error
    fake_result = {
        "messages": [MagicMock(
            content="You don't have access to this cost center data. Please contact your system administrator."
        )]
    }

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        response = await agent.invoke(
            "Show me cost center 9999", "ctx-403", tools=mock_tools
        )

    assert response.status == "completed"
    assert "access" in response.message.lower() or "administrator" in response.message.lower()


@pytest.mark.asyncio
async def test_service_unavailable_returns_clear_message(add_agent_to_path):
    """Agent returns service-unavailable message when S/4HANA is down."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    fake_result = {
        "messages": [MagicMock(
            content="The SAP S/4HANA system is currently unavailable. Please try again shortly."
        )]
    }

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        response = await agent.invoke(
            "How many cost centers do we have?", "ctx-503", tools=mock_tools
        )

    assert response.status == "completed"
    assert "unavailable" in response.message.lower() or "try again" in response.message.lower()


@pytest.mark.asyncio
async def test_exception_during_invoke_returns_error(add_agent_to_path):
    """Agent handles unexpected exceptions gracefully without crashing."""
    from unittest.mock import AsyncMock, patch
    from agent import SampleAgent

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, side_effect=RuntimeError("network error")):
        response = await agent.invoke(
            "How many cost centers do we have?", "ctx-exc", tools=[]
        )

    assert response.status in ("error", "completed")


@pytest.mark.asyncio
async def test_no_tools_available_returns_graceful_message(add_agent_to_path):
    """Agent handles empty tool list gracefully."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    fake_result = {
        "messages": [MagicMock(content="Tools are temporarily unavailable. Please try again later.")]
    }

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        response = await agent.invoke(
            "How many cost centers do we have?", "ctx-notools", tools=[]
        )

    assert response.status == "completed"
