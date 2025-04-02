# FastMCP Documentation

## Overview

FastMCP is a high-level, Pythonic framework for building Model Context Protocol (MCP) servers. It provides a simple, intuitive interface for creating tools, resources, and prompts that can be used by Large Language Models (LLMs) like Claude.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) is a standardized way to provide context and tools to LLMs. It allows developers to build servers that expose data and functionality to LLM applications in a secure, standardized way. Think of it like a web API, but specifically designed for LLM interactions.

MCP servers can:

- Expose data through **Resources** (similar to GET endpoints; used to load information into the LLM's context)
- Provide functionality through **Tools** (similar to POST endpoints; used to execute code or produce side effects)
- Define interaction patterns through **Prompts** (reusable templates for LLM interactions)

## Installation

### Recommended Installation

We strongly recommend installing FastMCP with [uv](https://docs.astral.sh/uv/), as it is required for deploying servers:

```bash
uv pip install fastmcp
```

Note: on macOS, uv may need to be installed with Homebrew (`brew install uv`) in order to make it available to the Claude Desktop app.

### Alternative Installation

To use the SDK without deploying, you may use pip:

```bash
pip install fastmcp
```

## Core Concepts

### Server

The FastMCP server is your core interface to the MCP protocol. It handles connection management, protocol compliance, and message routing:

```python
from fastmcp import FastMCP

# Create a named server
mcp = FastMCP("My App")

# Specify dependencies for deployment and development
mcp = FastMCP("My App", dependencies=["pandas", "numpy"])
```

### Resources

Resources are how you expose data to LLMs. They're similar to GET endpoints in a REST API - they provide data but shouldn't perform significant computation or have side effects. Some examples:

- File contents
- Database schemas
- API responses
- System information

Resources can be static:

```python
@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"
```

Or dynamic with parameters (FastMCP automatically handles these as MCP templates):

```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Dynamic user data"""
    return f"Profile data for user {user_id}"
```

### Tools

Tools let LLMs take actions through your server. Unlike resources, tools are expected to perform computation and have side effects. They're similar to POST endpoints in a REST API.

Simple calculation example:

```python
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m ** 2)
```

HTTP request example:

```python
import httpx

@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/{city}"
        )
        return response.text
```

Complex input handling example:

```python
from pydantic import BaseModel, Field
from typing import Annotated

class ShrimpTank(BaseModel):
    class Shrimp(BaseModel):
        name: Annotated[str, Field(max_length=10)]

    shrimp: list[Shrimp]

@mcp.tool()
def name_shrimp(
    tank: ShrimpTank,
    # You can use pydantic Field in function signatures for validation.
    extra_names: Annotated[list[str], Field(max_length=10)],
) -> list[str]:
    """List all shrimp names in the tank"""
    return [shrimp.name for shrimp in tank.shrimp] + extra_names
```

### Prompts

Prompts are reusable templates that help LLMs interact with your server effectively. They're like "best practices" encoded into your server. A prompt can be as simple as a string:

```python
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
```

Or a more structured sequence of messages:

```python
from fastmcp.prompts.base import UserMessage, AssistantMessage

@mcp.prompt()
def debug_error(error: str) -> list[Message]:
    return [
        UserMessage("I'm seeing this error:"),
        UserMessage(error),
        AssistantMessage("I'll help debug that. What have you tried so far?")
    ]
```

### Images

FastMCP provides an `Image` class that automatically handles image data in your server:

```python
from fastmcp import FastMCP, Image
from PIL import Image as PILImage

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    
    # FastMCP automatically handles conversion and MIME types
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def load_image(path: str) -> Image:
    """Load an image from disk"""
    # FastMCP handles reading and format detection
    return Image(path=path)
```

Images can be used as the result of both tools and resources.

### Context

The Context object gives your tools and resources access to MCP capabilities. To use it, add a parameter annotated with `fastmcp.Context`:

```python
from fastmcp import FastMCP, Context

@mcp.tool()
async def long_task(files: list[str], ctx: Context) -> str:
    """Process multiple files with progress tracking"""
    for i, file in enumerate(files):
        ctx.info(f"Processing {file}")
        await ctx.report_progress(i, len(files))
        
        # Read another resource if needed
        data = await ctx.read_resource(f"file://{file}")
        
    return "Processing complete"
```

The Context object provides:

- Progress reporting through `report_progress()`
- Logging via `debug()`, `info()`, `warning()`, and `error()`
- Resource access through `read_resource()`
- Request metadata via `request_id` and `client_id`

## Running Your Server

There are three main ways to use your FastMCP server, each suited for different stages of development:

### Development Mode (Recommended for Building & Testing)

The fastest way to test and debug your server is with the MCP Inspector:

```bash
fastmcp dev server.py
```

This launches a web interface where you can:

- Test your tools and resources interactively
- See detailed logs and error messages
- Monitor server performance
- Set environment variables for testing

During development, you can:

- Add dependencies with `--with`:  

  ```bash
  fastmcp dev server.py --with pandas --with numpy
  ```

- Mount your local code for live updates:  

  ```bash
  fastmcp dev server.py --with-editable .
  ```

### Claude Desktop Integration (For Regular Use)

Once your server is ready, install it in Claude Desktop to use it with Claude:

```bash
fastmcp install server.py
```

Your server will run in an isolated environment with:

- Automatic installation of dependencies specified in your FastMCP instance:  

  ```python
  mcp = FastMCP("My App", dependencies=["pandas", "numpy"])
  ```

- Custom naming via `--name`:  

  ```bash
  fastmcp install server.py --name "My Analytics Server"
  ```

- Environment variable management:  

  ```bash
  # Set variables individually  
  fastmcp install server.py -e API_KEY=abc123 -e DB_URL=postgres://...  
  # Or load from a .env file  
  fastmcp install server.py -f .env
  ```

### Direct Execution (For Advanced Use Cases)

For advanced scenarios like custom deployments or running without Claude, you can execute your server directly:

```python
from fastmcp import FastMCP

mcp = FastMCP("My App")

if __name__ == "__main__":
    mcp.run()
```

Run it with:

```bash
# Using the FastMCP CLI
fastmcp run server.py

# Or with Python/uv directly
python server.py
uv run python server.py
```

Note: When running directly, you are responsible for ensuring all dependencies are available in your environment. Any dependencies specified on the FastMCP instance are ignored.

Choose this method when you need:

- Custom deployment configurations
- Integration with other services
- Direct control over the server lifecycle

### Server Object Names

All FastMCP commands will look for a server object called `mcp`, `app`, or `server` in your file. If you have a different object name or multiple servers in one file, use the syntax `server.py:my_server`:

```bash
# Using a standard name
fastmcp run server.py

# Using a custom name
fastmcp run server.py:my_custom_server
```

## Examples

Here are a few examples of FastMCP servers:

### Echo Server

A simple server demonstrating resources, tools, and prompts:

```python
from fastmcp import FastMCP

mcp = FastMCP("Echo")

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"

@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"

@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"
```

### SQLite Explorer

A more complex example showing database integration:

```python
from fastmcp import FastMCP
import sqlite3

mcp = FastMCP("SQLite Explorer")

@mcp.resource("schema://main")
def get_schema() -> str:
    """Provide the database schema as a resource"""
    conn = sqlite3.connect("database.db")
    schema = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return "\n".join(sql[0] for sql in schema if sql[0])

@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely"""
    conn = sqlite3.connect("database.db")
    try:
        result = conn.execute(sql).fetchall()
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.prompt()
def analyze_table(table: str) -> str:
    """Create a prompt template for analyzing tables"""
    return f"""Please analyze this database table:
Table: {table}
Schema: 
{get_schema()}

What insights can you provide about the structure and relationships?"""
```

### File Server

A server for reading and writing files:

```python
from fastmcp import FastMCP

mcp = FastMCP("File Server")

@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """Read a file from disk"""
    with open(path) as f:
        return f.read()

@mcp.tool()
def append_to_file(path: str, content: str) -> None:
    """Append content to a file"""
    with open(path, 'a') as f:
        f.write(content)
```

## Key Features

FastMCP is designed to be high-level and Pythonic, with key features including:

- **Fast**: High-level interface means less code and faster development
- **Simple**: Build MCP servers with minimal boilerplate
- **Pythonic**: Feels natural to Python developers
- **Complete**: FastMCP aims to provide a full implementation of the core MCP specification

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended for deployment)

## Resources

- [GitHub Repository](https://github.com/jlowin/fastmcp)
- [PyPI Package](https://pypi.org/project/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io)
