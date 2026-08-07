import { describe, expect, it } from "vitest";
import { extractSummary, groupBySeverity } from "./findings";
import type { Finding } from "./api/types";

function makeFinding(overrides: Partial<Finding>): Finding {
  return {
    id: 1,
    analysis_request_id: 1,
    specialist: "security",
    severity: "medium",
    file_path: null,
    description: "descripción",
    suggestion: null,
    created_at: "2026-08-07T10:00:00Z",
    ...overrides,
  };
}

describe("extractSummary", () => {
  it("returns everything before the literal separator", () => {
    const report = "Resumen del análisis.\n\n---\n\n## Hallazgos completos\n- ...";

    expect(extractSummary(report)).toBe("Resumen del análisis.");
  });

  it("falls back to the whole trimmed string when the separator is missing", () => {
    expect(extractSummary("  solo narrativa, sin separador  ")).toBe(
      "solo narrativa, sin separador",
    );
  });

  it("only splits on the first occurrence of the separator", () => {
    const report = "narrativa\n\n---\n\nsección uno\n\n---\n\nsección dos";

    expect(extractSummary(report)).toBe("narrativa");
  });
});

describe("groupBySeverity", () => {
  it("returns no groups for an empty findings list", () => {
    expect(groupBySeverity([])).toEqual([]);
  });

  it("orders groups critical to low, skipping severities with no findings", () => {
    const findings = [
      makeFinding({ id: 1, severity: "low" }),
      makeFinding({ id: 2, severity: "critical" }),
      makeFinding({ id: 3, severity: "high" }),
    ];

    expect(groupBySeverity(findings).map((group) => group.severity)).toEqual([
      "critical",
      "high",
      "low",
    ]);
  });

  it("keeps every finding of a severity together, in their original order", () => {
    const findings = [
      makeFinding({ id: 1, severity: "high", description: "primero" }),
      makeFinding({ id: 2, severity: "critical" }),
      makeFinding({ id: 3, severity: "high", description: "segundo" }),
    ];

    const highGroup = groupBySeverity(findings).find((group) => group.severity === "high");

    expect(highGroup?.findings.map((finding) => finding.description)).toEqual([
      "primero",
      "segundo",
    ]);
  });
});
