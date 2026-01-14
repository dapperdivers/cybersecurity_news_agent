# Cybersecurity News Agent Container
# Self-contained container with Claude Code CLI and security-focused agents

FROM node:20-bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    sudo \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Install minimal Python libraries for MCP servers
RUN pip3 install --no-cache-dir --break-system-packages \
    requests \
    feedparser \
    beautifulsoup4 \
    python-dateutil \
    anthropic

# Create application directory structure
# User creation is handled at runtime by entrypoint.sh
RUN mkdir -p /app/mcp-servers/rss_fetcher/config \
    && mkdir -p /app/mcp-servers/text_analyzer \
    && mkdir -p /app/outputs \
    && mkdir -p /home/agent/.claude/agents \
    && mkdir -p /home/agent/.claude/skills

# Copy MCP servers
COPY src/mcp-servers/rss_fetcher/ /app/mcp-servers/rss_fetcher/
COPY src/mcp-servers/text_analyzer/ /app/mcp-servers/text_analyzer/

# Copy agent definitions
COPY src/claude-code/agents/ /home/agent/.claude/agents/

# Copy skills (if any)
COPY src/claude-code/skills/ /home/agent/.claude/skills/

# Copy MCP server configuration to correct location for Claude Code
COPY src/claude-code/.mcp.json /home/agent/.claude/.mcp.json

# Copy entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set environment variables with defaults
ENV DEFAULT_FEEDS_PATH="/app/mcp-servers/rss_fetcher/config/default_feeds.json" \
    OUTPUT_DIR="/app/outputs" \
    HOME="/home/agent"

# Set working directory (entrypoint will chown as needed)
WORKDIR /home/agent

# Use entrypoint script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default to interactive bash shell
CMD ["/bin/bash"]
