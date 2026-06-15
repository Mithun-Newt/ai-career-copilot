# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package management files
COPY package*.json ./

# Install dependencies cleanly
RUN npm ci

# Copy all source files
COPY . .

# Build the production application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built static assets from the build stage to Nginx default public directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 internally
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
