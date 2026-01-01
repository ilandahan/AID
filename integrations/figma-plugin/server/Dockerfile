# syntax=docker/dockerfile:1

# ===========================================
# Figma Plugin Server - Docker Image
# AID Methodology - Auto-start with Docker Desktop
# ===========================================

# Base image - matches project pattern
FROM node:18-alpine AS base

# ===========================================
# Dependencies Stage
# ===========================================
FROM base AS deps

# Add libc6-compat for Alpine compatibility
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install production dependencies only
RUN npm ci --only=production

# ===========================================
# Production Stage
# ===========================================
FROM base AS runner

WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV PORT=3001

# Create non-root user (UID 1001 - matches project convention)
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 figmaserver

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source
COPY --chown=figmaserver:nodejs src ./src
COPY --chown=figmaserver:nodejs package.json ./

# Create output directory for exported components
RUN mkdir -p /app/output && chown figmaserver:nodejs /app/output

# Switch to non-root user
USER figmaserver

# Expose the server port
EXPOSE 3001

# Health check - uses server's /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3001/health || exit 1

# Start the server
CMD ["node", "src/index.js"]
