import path from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    // Mirrors tsconfig.json's "@/*": ["./src/*"] — Next.js resolves this
    // alias itself at build time, but vitest runs on plain Vite, which
    // doesn't read tsconfig paths automatically.
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
  },
});
