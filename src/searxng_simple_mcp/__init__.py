"""
SearxNG Simple MCP package.

This package provides a FastMCP server for SearxNG web search.
"""

# Import all modules from the package
from searxng_simple_mcp.config import Settings, DEFAULT_LANGUAGE, DEFAULT_FORMAT
from searxng_simple_mcp.searxng_client import SearxNGClient
from searxng_simple_mcp.server import mcp, logger, settings

# Define what should be available when importing from this package
__all__ = [
    "Settings",
    "DEFAULT_LANGUAGE",
    "DEFAULT_FORMAT",
    "SearxNGClient",
    "mcp",
    "logger",
    "settings",
]

# Version of the package
__version__ = "1.0.0"
