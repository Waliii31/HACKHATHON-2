"""
MCP Server for Phase III Todo AI Chatbot.

This module provides the MCP (Model Context Protocol) server that exposes
todo management operations as tools for the AI agent.

The MCP server follows the official MCP SDK patterns and provides:
- add_task: Add a new task
- list_tasks: List user's tasks
- complete_task: Mark task as done
- delete_task: Remove a task
- update_task: Update task details
"""
from dataclasses import dataclass
from typing import Dict, Any, Callable, List, Optional
from app.config import settings


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str = ""
    error: Optional[str] = None


@dataclass
class ToolContext:
    """
    Context passed to tool execution.
    
    Contains the authenticated user's ID for data isolation.
    The stateless API sets this for each request.
    """
    user_id: str


@dataclass
class ToolDefinition:
    """Definition of an MCP tool."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable


class MCPServer:
    """
    MCP Server for Todo operations.
    
    Registers and manages tools for the AI agent to use.
    Tools are executed with user context for data isolation.
    """
    
    def __init__(self, name: str = None, version: str = None):
        self.name = name or settings.MCP_SERVER_NAME
        self.version = version or settings.MCP_SERVER_VERSION
        self.description = "MCP server for AI-powered todo management"
        self._tools: Dict[str, ToolDefinition] = {}
    
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool with the server."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[ToolDefinition]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get tool schemas in OpenAI function calling format.
        
        This format is compatible with OpenAI Agents SDK.
        """
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return schemas
    
    async def execute_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any],
        context: ToolContext
    ) -> ToolResult:
        """
        Execute a tool with the given arguments and context.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            context: Execution context with user_id
            
        Returns:
            ToolResult with success status and data
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        try:
            result = await tool.handler(context=context, **arguments)
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


# Singleton instance
mcp_server = MCPServer()


def tool(name: str, description: str, parameters: Dict[str, Any]):
    """
    Decorator for registering MCP tools.
    
    Usage:
        @tool(
            name="add_task",
            description="Add a new task",
            parameters={...}
        )
        async def add_task(title: str, context: ToolContext) -> ToolResult:
            ...
    """
    def decorator(func: Callable) -> Callable:
        tool_def = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            handler=func
        )
        mcp_server.register_tool(tool_def)
        return func
    return decorator
