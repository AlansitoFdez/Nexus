import { defineConfig } from "vitest/config";

/**
 * environment: "node", not "jsdom" — this session only covers pure
 * functions (agent-trace.ts's deriveAgentTrace), not React components,
 * so there's no DOM to simulate yet. Add jsdom + @testing-library/react
 * here if/when component tests are added.
 */
export default defineConfig({
  test: {
    environment: "node",
  },
});
