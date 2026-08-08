# Multi-stage build: deps/builder stages carry the full node_modules and
# devDependencies needed to build; only the standalone output (see
# next.config.ts's output: "standalone") ships in the final runtime image.

FROM node:22-slim AS deps
WORKDIR /app
RUN npm install -g pnpm@11.2.2
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM node:22-slim AS builder
WORKDIR /app
RUN npm install -g pnpm@11.2.2
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# NEXT_PUBLIC_* variables are inlined into the client bundle at build
# time, not read from the environment when the container starts — so
# this has to be a build arg, not a runtime ENV. Defaults to the same
# value backend/.env.example ships, for a build with no override.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN pnpm build

FROM node:22-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN useradd --create-home --uid 1000 appuser
COPY --from=builder --chown=appuser:appuser /app/.next/standalone ./
COPY --from=builder --chown=appuser:appuser /app/.next/static ./.next/static

USER appuser
EXPOSE 3000

CMD ["node", "server.js"]
