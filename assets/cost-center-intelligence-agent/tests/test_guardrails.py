"""Unit tests for agent guardrails — scope restriction and system prompt constraints."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


def test_system_prompt_contains_scope_restriction(add_agent_to_path):
    """System prompt restricts agent to cost center queries only."""
    from agent import get_system_prompt

    prompt = get_system_prompt()
    assert "cost center" in prompt.lower()
    assert "only" in prompt.lower() or "scope" in prompt.lower()


def test_system_prompt_forbids_data_modification(add_agent_to_path):
    """System prompt explicitly prohibits modifying, creating, or deleting data."""
    from agent import get_system_prompt

    prompt = get_system_prompt()
    assert "never modify" in prompt.lower() or "modify" in prompt.lower()
    assert "never fabricate" in prompt.lower() or "fabricate" in prompt.lower()


def test_system_prompt_instructs_live_data_only(add_agent_to_path):
    """System prompt requires using tools for live data — no fabrication."""
    from agent import get_system_prompt

    prompt = get_system_prompt()
    assert "live data" in prompt.lower() or "tools to retrieve" in prompt.lower()


@pytest.mark.asyncio
async def test_off_topic_question_returns_scoped_refusal(add_agent_to_path):
    """Agent declines off-topic questions with a scoped refusal message."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from agent import SampleAgent

    mock_tools = [MagicMock()]
    refusal = "I can only assist with cost center queries. Please ask about cost center counts, top spenders, or specific cost center details."
    fake_result = {"messages": [MagicMock(content=refusal)]}

    agent = SampleAgent()
    with patch.object(agent, "_invoke", new_callable=AsyncMock, return_value=fake_result):
        response = await agent.invoke(
            "What is the weather in Berlin today?", "ctx-offtopic", tools=mock_tools
        )

    assert response.status == "completed"
    assert "cost center" in response.message.lower()


def test_system_prompt_includes_security_guidelines(add_agent_to_path):
    """System prompt includes prompt injection defense guidelines."""
    from agent import get_system_prompt

    prompt = get_system_prompt()
    assert "security" in prompt.lower() or "injection" in prompt.lower() or "tool results" in prompt.lower()
