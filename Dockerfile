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

# Create agent user and home directory
# Use numeric UID/GID for cross-platform compatibility
RUN groupadd -g 1000 agent 2>/dev/null || true \
    && useradd -u 1000 -g 1000 -m -d /home/agent -s /bin/bash agent 2>/dev/null || true \
    && mkdir -p /home/agent

# Create application directory structure
RUN mkdir -p /app/mcp-servers/rss_fetcher/config \
    && mkdir -p /app/mcp-servers/text_analyzer \
    && mkdir -p /app/outputs \
    && mkdir -p /home/agent/.claude/agents \
    && mkdir -p /home/agent/.claude/skills

# Copy MCP servers (use numeric UID:GID for reliability)
COPY --chown=1000:1000 src/mcp-servers/rss_fetcher/ /app/mcp-servers/rss_fetcher/
COPY --chown=1000:1000 src/mcp-servers/text_analyzer/ /app/mcp-servers/text_analyzer/

# Copy agent definitions
COPY --chown=1000:1000 src/claude-code/agents/ /home/agent/.claude/agents/

# Copy skills
COPY --chown=1000:1000 src/claude-code/skills/ /home/agent/.claude/skills/

# Copy MCP server configuration to correct location for Claude Code
COPY --chown=1000:1000 src/claude-code/.mcp.json /home/agent/.claude/.mcp.json

# Create inline init script for credentials setup
RUN echo '#!/bin/bash\n\
if [ -n "$CLAUDE_CODE_OAUTH_TOKEN" ]; then\n\
  mkdir -p ~/.claude\n\
  echo "{\"oauth\":{\"access_token\":\"$CLAUDE_CODE_OAUTH_TOKEN\"}}" > ~/.claude/.credentials.json\n\
  chmod 600 ~/.claude/.credentials.json\n\
fi\n\
exec "$@"' > /usr/local/bin/init.sh && chmod +x /usr/local/bin/init.sh

# Set permissions for output directory (use numeric UID:GID for reliability)
RUN chown -R 1000:1000 /app/outputs /home/agent

# Set environment variables
ENV DEFAULT_FEEDS_PATH="/app/mcp-servers/rss_fetcher/config/default_feeds.json" \
    OUTPUT_DIR="/app/outputs" \
    HOME="/home/agent"

# Switch to non-root user (UID 1000)
USER 1000

# Set working directory
WORKDIR /home/agent

# Use inline init script for credentials
ENTRYPOINT ["/usr/local/bin/init.sh"]

# Default to interactive bash shell
CMD ["/bin/bash"]
