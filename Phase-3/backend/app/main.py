"""
Phase III: Todo AI Chatbot - Main Application

This is the FastAPI application entry point for the AI-powered Todo chatbot.
It provides:
- POST /api/chat - Stateless chat endpoint
- GET /api/chat/conversations - List conversations
- GET /api/chat/conversations/{id} - Get conversation details
- DELETE /api/chat/conversations/{id} - Delete conversation

The application is designed to be STATELESS - all conversation history
is read from and written to the PostgreSQL database on every request.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.chat import router as chat_router
from app.api.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Handles startup and shutdown events.
    """
    # Startup
    print("=" * 60)
    print("🤖 Phase III: Todo AI Chatbot")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"OpenAI Model: {settings.OPENAI_MODEL}")
    print(f"MCP Server: {settings.MCP_SERVER_NAME} v{settings.MCP_SERVER_VERSION}")
    print("=" * 60)
    
    # Import MCP tools to register them
    from app.mcp import mcp_server
    tools = mcp_server.get_all_tools()
    print(f"📦 Loaded {len(tools)} MCP tools:")
    for tool in tools:
        print(f"   • {tool.name}: {tool.description[:50]}...")
    print("=" * 60)
    
    yield
    
    # Shutdown
    print("👋 Shutting down Phase III server...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Set all CORS enabled origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure CORS (this block will now be redundant if the above is always active,
# but keeping it as per instruction to add, not replace)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router)
app.include_router(tasks_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "todo-ai-chatbot",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Todo AI Chatbot",
        "version": "1.0.0",
        "phase": "III",
        "description": "AI-powered Todo management through conversation",
        "endpoints": {
            "chat": "POST /api/chat",
            "conversations": "GET /api/chat/conversations",
            "conversation_detail": "GET /api/chat/conversations/{id}",
            "delete_conversation": "DELETE /api/chat/conversations/{id}",
            "health": "GET /health"
        }
    }
