"""
MCP Package for Phase III.

Provides the MCP server and tools for AI-powered todo management.
"""
from .server import mcp_server, ToolResult, ToolContext, ToolDefinition, tool

# Import tools to register them with the server
from . import tools

__all__ = [
    "mcp_server",
    "ToolResult",
    "ToolContext",
    "ToolDefinition",
    "tool",
    "tools",
]
