# SearxNG MCP Server

A Model Context Protocol (MCP) server that provides web search capabilities using SearxNG, allowing AI assistants like Claude to search the web.

## Overview

This project implements an MCP server that connects to SearxNG, a privacy-respecting metasearch engine. The server provides a simple and efficient way for Large Language Models to search the web without tracking users.

### Features

- Privacy-focused web search through SearxNG
- Simple API for LLM integration
- Compatible with Claude Desktop and other MCP-compliant clients
- Configurable search parameters
- Clean, formatted search results optimized for LLMs

## Quick Start

### Prerequisites

- Python 3.10 or higher
- A SearxNG instance (public or self-hosted)

### Installation

```bash
# Clone the repository
git clone https://github.com/Sacode/searxng-simple-mcp.git
cd searxng-simple-mcp

# Install dependencies
pip install uv
uv pip install -e .
```

### Using with Claude Desktop

Install the server in Claude Desktop:

```bash
# Navigate to the project directory
cd searxng-simple-mcp

# Install the server
npm run install:claude
# Or directly:
# fastmcp install src/searxng_simple_mcp/server.py
```

You can now use web search in Claude! Try prompts like:

- "Search for recent news about quantum computing."
- "Find information about climate change solutions and summarize the findings."
- "Search for Python programming tutorials and list the best ones."

### Configuration

You can configure the server using environment variables:

```bash
# Set a custom SearxNG instance
fastmcp install src/searxng_simple_mcp/server.py -e SEARXNG_MCP_SEARXNG_URL=https://your-instance.example.com

# Set default result count
fastmcp install src/searxng_simple_mcp/server.py -e SEARXNG_MCP_DEFAULT_RESULT_COUNT=15

# Or use a .env file
fastmcp install src/searxng_simple_mcp/server.py -f .env
```

The following environment variables are available for configuration:

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| SEARXNG_MCP_SEARXNG_URL | URL of the SearxNG instance to use | https://paulgo.io/ |
| SEARXNG_MCP_TIMEOUT | HTTP request timeout in seconds | 10 |
| SEARXNG_MCP_DEFAULT_RESULT_COUNT | Default number of results to return in searches | 10 |
| SEARXNG_MCP_DEFAULT_LANGUAGE | Language code for search results (e.g., 'en', 'ru', 'all') | all |
| SEARXNG_MCP_DEFAULT_FORMAT | Default format for search results ('text', 'json') | text |
| TRANSPORT_PROTOCOL | Transport protocol for MCP server ('stdio' or 'sse') | sse |

You can find a list of public SearxNG instances at [https://searx.space](https://searx.space) if you don't want to host your own.

## Development

For development and testing:

```bash
# Run in development mode
npm run dev
# Or directly:
# fastmcp dev src/searxng_simple_mcp/server.py

# This launches the MCP Inspector, a web interface for testing your server

# Run in development mode with editable dependencies
npm run dev:editable

# Install dependencies
npm run install:deps
# Or directly:
# uv pip install -e .

# Run linter
npm run lint
# Or fix linting issues automatically:
npm run lint:fix
# Format code:
npm run lint:format

# Run the server directly
npm start
# Or using FastMCP run:
npm run run

# Run with specific transport protocol
npm run run:stdio  # Use stdio transport
npm run run:sse    # Use sse transport
```

## Docker Usage

You can also run this application using Docker, which provides an isolated and consistent environment.

### Using Docker

```bash
# Build the Docker image
npm run docker:build

# Run the container (uses sse transport by default)
npm run docker:run

# Run with specific transport protocol
npm run docker:run:stdio  # Use stdio transport
npm run docker:run:sse    # Use sse transport
```

### Using Docker Compose

Docker Compose allows you to run the application along with any dependencies as a multi-container application.

```bash
# Start services (uses sse transport by default)
npm run docker:compose:up

# Start services with specific transport protocol
npm run docker:compose:up:stdio  # Use stdio transport
npm run docker:compose:up:sse    # Use sse transport

# Stop services
npm run docker:compose:down

# View logs
npm run docker:compose:logs

# Build services
npm run docker:compose:build

# Restart services
npm run docker:compose:restart
```

### Docker Configuration

The Docker setup uses the following configuration:

- The application runs on port 8000 inside the container, mapped to port 8000 on your host
- Environment variables can be set in the `.env` file or in the `docker-compose.yml` file
- The `src` directory is mounted as a volume, allowing code changes without rebuilding the image
- Transport protocol can be configured using the `TRANSPORT_PROTOCOL` environment variable (values: `stdio` or `sse`, default: `sse`)

#### Transport Protocol Options

The MCP server supports two transport protocols:

- **SSE (Server-Sent Events)**: Default protocol, suitable for web-based clients and most use cases
- **STDIO (Standard Input/Output)**: Alternative protocol, useful for certain integration scenarios

You can specify the transport protocol in several ways:

1. Using environment variables:
   ```
   TRANSPORT_PROTOCOL=stdio docker-compose up -d
   ```

2. Using the provided npm scripts:
   ```
   npm run docker:run:stdio
   npm run docker:compose:up:sse
   ```

3. By editing the `.env` file or `docker-compose.yml` file to set the `TRANSPORT_PROTOCOL` variable

## Continuous Integration and Deployment

This project uses GitHub Actions for continuous integration and deployment. When changes are pushed to the `main` branch, the following automated processes occur:

1. The code is checked out
2. A Docker image is built using the project's Dockerfile
3. The image is tagged with:
   - `latest` - Always points to the most recent build
   - Short SHA of the commit - For precise version tracking
   - Branch name - For feature branch identification
   - Semantic version (if tagged) - For release versioning
4. The image is published to GitHub Container Registry (ghcr.io)

You can find the published Docker images at: `ghcr.io/[your-username]/searxng-simple-mcp`

To use the published Docker image:

```bash
# Pull the latest image
docker pull ghcr.io/[your-username]/searxng-simple-mcp:latest

# Run the container
docker run -p 8000:8000 --env-file .env ghcr.io/[your-username]/searxng-simple-mcp:latest
```
The CI/CD workflow configuration can be found in `.github/workflows/docker-build-publish.yml`. The workflow has been configured with the minimum required permissions to push to the GitHub Container Registry.

### Automated Testing and Linting

In addition to the Docker build and publish workflow, this project also includes automated testing and linting:

- **When**: Runs on pull requests to the main branch and on pushes to the main branch
- **What**:
  - Runs code linting with Ruff to ensure code quality
  - Checks code formatting to maintain consistent style
  - (Future) Runs unit tests to verify functionality
This helps maintain code quality and catch issues early in the development process. The workflow configuration can be found in `.github/workflows/test-lint.yml`. This workflow uses read-only permissions for security.

### Automated Version Updates

When a new release is created on GitHub, the version number is automatically updated in the project files:

- **When**: Runs when a new release is created
- **What**:
  - Updates the version in package.json
  - Updates the version in pyproject.toml
  - Commits and pushes the changes back to the repository
This ensures that the version numbers in the project files always match the latest release. The workflow configuration can be found in `.github/workflows/release-version.yml`. This workflow has been granted write permissions to update files in the repository.




## Project Structure

```
searxng-simple-mcp/
│
├── src/
│   ├── run_server.py         # Entry point script
│   └── searxng_simple_mcp/
│       ├── __init__.py       # Package initialization
│       ├── server.py         # Main MCP server implementation
│       ├── searxng_client.py # Client for SearxNG API
│       └── config.py         # Configuration settings
│
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker configuration
├── pyproject.toml            # Python project configuration
├── package.json              # NPM scripts and metadata
└── .env.example              # Example environment variables
```

## Why SearxNG?

SearxNG offers several advantages for AI-powered search:

1. **Privacy**: SearxNG doesn't track users or store search history
2. **Diverse Sources**: Aggregates results from multiple search engines
3. **Customization**: Configurable engines, filters, and result formats
4. **Self-hostable**: Can be run on your own infrastructure
5. **Open Source**: Transparent and community-driven

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
