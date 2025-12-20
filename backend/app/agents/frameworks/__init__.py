"""
Agent Framework Integrations

Wrappers for various agent frameworks.
"""

from app.agents.frameworks.agentgpt import AgentGPTFramework
from app.agents.frameworks.archon import ArchonFramework
from app.agents.frameworks.autogen import AutoGenFramework
from app.agents.frameworks.autogpt import AutoGPTFramework
from app.agents.frameworks.base import BaseAgentFramework
from app.agents.frameworks.camel import CamelAIFramework
from app.agents.frameworks.crewai import CrewAIFramework
from app.agents.frameworks.kush import KUSHAIFramework
from app.agents.frameworks.kyro import KyroFramework
from app.agents.frameworks.metagpt import MetaGPTFramework
from app.agents.frameworks.riona import RionaFramework
from app.agents.frameworks.swarm import SwarmFramework

__all__ = [
    "BaseAgentFramework",
    "AgentGPTFramework",
    "AutoGPTFramework",
    "MetaGPTFramework",
    "AutoGenFramework",
    "ArchonFramework",
    "CrewAIFramework",
    "SwarmFramework",
    "CamelAIFramework",
    "KUSHAIFramework",
    "KyroFramework",
    "RionaFramework",
]
