"""Unit tests for cost center count queries (R1)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.fixture
def mock_tools(add_agent_to_path):
    """Return mock structured tools from mcp-mock.json via the conftest patch."""
    from mcp_tools import get_mcp_tools
    import asyncio
    return asyncio.get_event_loop().run_until_complete(get_mcp_tools())


@pytest.mark.asyncio
async def test_count_query_returns_numeric_answer(add_agent_to_path):
    """Agent returns a numeric count when asked how many cost centers exist."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    mock_tools[0].name = "count_a_costcenter_2_for_sap_self"

    fake_result = {
        "messages": [MagicMock(content="You currently have 342 active cost centers.")]
    }

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        chunks = []
        async for chunk in agent.stream("How many cost centers do we have?", "ctx-1", tools=mock_tools):
            chunks.append(chunk)

    completed = [c for c in chunks if c.get("is_task_complete")]
    assert len(completed) == 1
    assert "342" in completed[0]["content"]


@pytest.mark.asyncio
async def test_count_query_phrasing_variation(add_agent_to_path):
    """Agent handles phrasing variations for count queries."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    fake_result = {
        "messages": [MagicMock(content="The total number of cost centers is 342.")]
    }

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        response = await agent.invoke("What is the total number of cost centers?", "ctx-2", tools=mock_tools)

    assert response.status == "completed"
    assert "342" in response.message


@pytest.mark.asyncio
async def test_m2_milestone_logged_on_count_query(add_agent_to_path, caplog):
    """M2 milestone is logged on successful count query."""
    import logging
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    fake_result = {
        "messages": [MagicMock(content="You have 342 cost centers.")]
    }

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        with caplog.at_level(logging.INFO, logger="agent"):
            response = await agent.invoke("How many cost centers do we have?", "ctx-3", tools=mock_tools)

    assert response.status == "completed"
    assert any("M2.achieved" in record.message for record in caplog.records)
