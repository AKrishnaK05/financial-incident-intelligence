import pytest
from investigation.agent_adapter import MockInvestigationAgent
from investigation.agent_factory import build_investigation_provider, create_investigation_agent


def test_create_investigation_agent_mock():
    agent = create_investigation_agent(provider="mock")
    assert isinstance(agent, MockInvestigationAgent)


def test_build_investigation_provider_alias():
    agent = build_investigation_provider(provider="mock")
    assert isinstance(agent, MockInvestigationAgent)


def test_create_investigation_agent_unsupported():
    with pytest.raises(ValueError, match="Unsupported agent provider"):
        create_investigation_agent(provider="unknown_provider")
