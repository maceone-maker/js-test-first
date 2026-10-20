"""Unit tests for top 5 cost centers by spend queries (R2)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.mark.asyncio
async def test_top5_query_returns_ranked_list(add_agent_to_path):
    """Agent returns a ranked list when asked for top 5 cost centers by spend."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    mock_tools[0].name = "list_a_costcenter_2_for_sap_self"

    response_text = (
        "Here are the top 5 cost centers by actual spend:\n"
        "1. Corporate IT (1000) — $1,250,000\n"
        "2. Finance & Controlling (2000) — $980,000\n"
        "3. Human Resources (3000) — $750,000\n"
        "4. Sales & Marketing (4000) — $620,000\n"
        "5. Operations (5000) — $540,000"
    )
    fake_result = {"messages": [MagicMock(content=response_text)]}

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        response = await agent.invoke(
            "Which are the top 5 cost centers by actual spend?", "ctx-top5", tools=mock_tools
        )

    assert response.status == "completed"
    assert "Corporate IT" in response.message
    assert "1,250,000" in response.message


@pytest.mark.asyncio
async def test_top5_query_includes_cost_amount(add_agent_to_path):
    """Top 5 response includes cost center ID, name, and cost amount."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    response_text = "1. Corporate IT (CC 1000): USD 1,250,000.00"
    fake_result = {"messages": [MagicMock(content=response_text)]}

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        response = await agent.invoke(
            "Show me the highest spending cost centers", "ctx-top5b", tools=mock_tools
        )

    assert response.status == "completed"
    assert "1000" in response.message


@pytest.mark.asyncio
async def test_m3_milestone_logged_on_top5_query(add_agent_to_path, caplog):
    """M3 milestone is logged on successful top-5 query."""
    import logging
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    fake_result = {
        "messages": [MagicMock(content="Top 5 cost centers: Corporate IT, Finance...")]
    }

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        with caplog.at_level(logging.INFO, logger="agent"):
            await agent.invoke("Top 5 cost centers by spend?", "ctx-m3", tools=mock_tools)

    assert any("M3.achieved" in record.message for record in caplog.records)
