# Simple Dockerfile for Cockpit
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application with host binding for Docker and disable browser opening
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000", "--no-open"]
