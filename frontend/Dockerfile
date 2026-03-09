# ── Stage 1: Build ───────────────────────────────────────────────
FROM node:20-alpine AS builder
# VITE_ variables are baked into the JS bundle at build time.
# Pass this arg when building for cloud (e.g. Render, Fly):
#   docker build --build-arg VITE_API_BASE_URL=https://api.example.com/api/v1 .
# Leave empty for docker-compose (nginx proxy handles /api/ routing).
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# ── Stage 2: Serve with nginx ─────────────────────────────────────
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React app
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
