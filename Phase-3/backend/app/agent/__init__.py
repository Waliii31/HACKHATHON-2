"""
AI Agent Package for Phase III.

Provides the AI agent brain for natural language task management.
"""
from .brain import process_message, build_context, get_conversation_starter
from .prompts import SYSTEM_PROMPT, CONVERSATION_STARTER, ERROR_FALLBACK_MESSAGE

__all__ = [
    "process_message",
    "build_context",
    "get_conversation_starter",
    "SYSTEM_PROMPT",
    "CONVERSATION_STARTER",
    "ERROR_FALLBACK_MESSAGE",
]
