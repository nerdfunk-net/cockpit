# Dockerfile for Cockpit - Frontend + Backend
FROM node:18-alpine

# Install Python and other dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    build-base \
    git \
    curl \
    && ln -sf python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy and install frontend dependencies
COPY package*.json ./
RUN npm install

# Copy and install backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --break-system-packages -r backend/requirements.txt

# Copy all source code
COPY . .

# Copy and make startup script executable
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 3000 8000

# Health check that verifies both services
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:3000/ && curl -f http://localhost:8000/docs || exit 1

# Use the startup script
CMD ["/app/start.sh"]
