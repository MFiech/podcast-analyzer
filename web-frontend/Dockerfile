# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build arguments for external service URLs
# Note: NEXT_PUBLIC_API_BASE_URL is no longer needed as we use runtime detection
ARG NEXT_PUBLIC_DOZZLE_URL=http://localhost:5000
ARG NEXT_PUBLIC_LANGFUSE_URL=https://cloud.langfuse.com
ARG NEXT_PUBLIC_GITHUB_URL=https://github.com/MFiech/podcast-analyzer

ENV NEXT_PUBLIC_DOZZLE_URL=$NEXT_PUBLIC_DOZZLE_URL
ENV NEXT_PUBLIC_LANGFUSE_URL=$NEXT_PUBLIC_LANGFUSE_URL
ENV NEXT_PUBLIC_GITHUB_URL=$NEXT_PUBLIC_GITHUB_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install dumb-init to handle signals properly
RUN apk add --no-cache dumb-init

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Expose port 3000
EXPOSE 3000

# Use dumb-init to handle signals
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["npm", "start"]
