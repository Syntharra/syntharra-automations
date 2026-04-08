FROM n8nio/n8n:latest

# Hardcode port 5678 - Railway domain is configured to target this port
ENV N8N_PORT=5678

# Ensure n8n home dir exists
RUN mkdir -p /home/node/.n8n

EXPOSE 5678

CMD ["n8n", "start"]
