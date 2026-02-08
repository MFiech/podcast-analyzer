# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build arguments for external service URLs
# Note: NEXT_PUBLIC_API_BASE_URL is no longer needed as we use runtime detection
# Note: Leave DOZZLE_URL empty so the app uses dynamic hostname:5001 at runtime
ARG NEXT_PUBLIC_LANGFUSE_URL=https://cloud.langfuse.com/project/cmh3umme800vzad075pjehiow
ARG NEXT_PUBLIC_GITHUB_URL=https://github.com/MFiech/podcast-analyzer

ENV NEXT_PUBLIC_LANGFUSE_URL=$NEXT_PUBLIC_LANGFUSE_URL
ENV NEXT_PUBLIC_GITHUB_URL=$NEXT_PUBLIC_GITHUB_URL
ENV NEXT_TELEMETRY_DISABLED=1

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

# Disable all outbound connections at runtime
ENV NEXT_TELEMETRY_DISABLED=1
ENV SKIP_UNRS_RESOLVER_FALLBACK=1
ENV NPM_CONFIG_UPDATE_NOTIFIER=false

# Install dumb-init to handle signals properly
RUN apk add --no-cache dumb-init

# Copy package files
COPY package*.json ./

# Install only production dependencies (--omit=dev replaces deprecated --only=production)
RUN npm ci --omit=dev

# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Set ownership and switch to non-root user
RUN chown -R node:node /app
USER node

# Expose port 3000
EXPOSE 3000

# Use dumb-init to handle signals
ENTRYPOINT ["dumb-init", "--"]

# Start the application directly (bypass npm to avoid update checks)
CMD ["node_modules/.bin/next", "start"]
