"""
Prompt Templates Package

包含各種 Agent 的 System Prompts 和指令模板。
"""

from .inspire_agent_instructions import (
    INSPIRE_AGENT_SYSTEM_PROMPT,
    INSPIRE_AGENT_SYSTEM_PROMPT_SHORT,
    TOOL_USAGE_HINTS,
    PHASE_PROMPTS,
    get_system_prompt,
    get_tool_hint,
)

__all__ = [
    "INSPIRE_AGENT_SYSTEM_PROMPT",
    "INSPIRE_AGENT_SYSTEM_PROMPT_SHORT",
    "TOOL_USAGE_HINTS",
    "PHASE_PROMPTS",
    "get_system_prompt",
    "get_tool_hint",
]

