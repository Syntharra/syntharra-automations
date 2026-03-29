# =============================================================
# Dockerfile — Syntharra n8n Self-Hosted
# =============================================================
# Lightweight n8n image with persistent filesystem storage
# =============================================================

FROM n8nio/n8n:latest

# Railway injects PORT env var — n8n needs to listen on it
ENV N8N_PORT=${PORT:-5678}

# Ensure binary data directory exists
RUN mkdir -p /home/node/.n8n

# Expose the port Railway will route to
EXPOSE ${PORT:-5678}

# Start n8n
CMD ["n8n", "start"]
