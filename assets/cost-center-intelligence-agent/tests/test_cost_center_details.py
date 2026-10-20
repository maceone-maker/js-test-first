"""Unit tests for cost center detail drill-down queries (R3)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.mark.asyncio
async def test_detail_query_returns_all_attributes(add_agent_to_path):
    """Agent returns name, responsible person, actual costs, and hierarchy for a specific cost center."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock(), MagicMock()]
    response_text = (
        "Cost Center 1000 — Corporate IT\n"
        "Responsible Person: John Smith\n"
        "Actual Costs: USD 1,250,000.00\n"
        "Hierarchy: Corporate > Finance > Corporate IT"
    )
    fake_result = {"messages": [MagicMock(content=response_text)]}

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        response = await agent.invoke(
            "Tell me about cost center 1000", "ctx-detail", tools=mock_tools
        )

    assert response.status == "completed"
    assert "John Smith" in response.message
    assert "1,250,000" in response.message
    assert "Corporate IT" in response.message


@pytest.mark.asyncio
async def test_detail_query_by_name(add_agent_to_path):
    """Agent handles drill-down queries by cost center name."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    fake_result = {
        "messages": [MagicMock(content="Cost Center: Corporate IT (1000), Responsible: John Smith")]
    }

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        response = await agent.invoke(
            "What are the details for the Corporate IT cost center?",
            "ctx-detail-name",
            tools=mock_tools,
        )

    assert response.status == "completed"
    assert "Corporate IT" in response.message


@pytest.mark.asyncio
async def test_m4_milestone_logged_on_detail_query(add_agent_to_path, caplog):
    """M4 milestone is logged on successful drill-down query."""
    import logging
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    fake_result = {
        "messages": [MagicMock(content="Cost Center 1000: Corporate IT, John Smith, USD 1,250,000")]
    }

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        with caplog.at_level(logging.INFO, logger="agent"):
            await agent.invoke("Tell me more about cost center 1000", "ctx-m4", tools=mock_tools)

    assert any("M4.achieved" in record.message for record in caplog.records)
