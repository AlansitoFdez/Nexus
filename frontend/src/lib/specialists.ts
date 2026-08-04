/**
 * Single source of truth for how each specialist is labeled in the UI.
 * Was duplicated identically in AgentTrace.tsx and MetricsPanel.tsx
 * (Fase 4.6 review) — a fifth specialist added on the backend would
 * silently show its raw key instead of a label in whichever of the two
 * a future edit forgot to update.
 */

import type { Specialist } from "./api/types";

export const SPECIALIST_LABELS: Record<Specialist, string> = {
  security: "Seguridad",
  performance: "Rendimiento",
  design_patterns: "Patrones de diseño",
  best_practices: "Buenas prácticas",
};
