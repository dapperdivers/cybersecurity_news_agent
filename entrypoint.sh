#!/bin/bash
set -e

# Entrypoint script for cybersec-agent container
# Handles dynamic UID/GID mapping to match host user

# Default to user 1000:1000 if not specified
USER_UID=${USER_UID:-1000}
USER_GID=${USER_GID:-1000}

# If running as root (UID 0), stay as root
if [ "$USER_UID" -eq 0 ]; then
    exec "$@"
fi

# Only do user mapping if we're currently root
if [ "$(id -u)" -eq 0 ]; then
    # Create group if it doesn't exist with the target GID
    if ! getent group "$USER_GID" >/dev/null 2>&1; then
        groupadd -g "$USER_GID" agent 2>/dev/null || true
        GROUP_NAME="agent"
    else
        # If GID exists, use that group name
        GROUP_NAME=$(getent group "$USER_GID" | cut -d: -f1)
    fi

    # Create user if it doesn't exist with the target UID
    if ! getent passwd "$USER_UID" >/dev/null 2>&1; then
        useradd -u "$USER_UID" -g "$USER_GID" -m -d /home/agent -s /bin/bash agent 2>/dev/null || true
        USER_NAME="agent"
    else
        # If UID exists, use that username but ensure correct GID
        USER_NAME=$(getent passwd "$USER_UID" | cut -d: -f1)
        # Change user's primary group if it doesn't match
        CURRENT_GID=$(id -g "$USER_NAME")
        if [ "$CURRENT_GID" != "$USER_GID" ]; then
            usermod -g "$USER_GID" "$USER_NAME" 2>/dev/null || true
        fi
    fi

    # Ensure directories are accessible
    chown -R "$USER_UID:$USER_GID" /home/agent /app/outputs 2>/dev/null || true
    chmod 755 /home/agent /app/outputs 2>/dev/null || true

    # Setup credentials as the target user
    if [ -n "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
        CREDENTIALS_FILE="/home/agent/.claude/.credentials.json"
        if [ ! -f "$CREDENTIALS_FILE" ]; then
            mkdir -p /home/agent/.claude
            cat > "$CREDENTIALS_FILE" << EOF
{
  "oauth": {
    "access_token": "$CLAUDE_CODE_OAUTH_TOKEN"
  }
}
EOF
            chown "$USER_UID:$USER_GID" "$CREDENTIALS_FILE"
            chmod 600 "$CREDENTIALS_FILE"
        fi
    fi

    # Switch to the user and execute command
    export HOME=/home/agent
    export SHELL=/bin/bash
    exec gosu "$USER_NAME" "$@"
else
    # Already running as non-root, just execute
    exec "$@"
fi
