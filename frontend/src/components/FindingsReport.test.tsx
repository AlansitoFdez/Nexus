import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FindingsReport } from "./FindingsReport";
import type { Finding } from "@/lib/api/types";

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

const finalReport = "Resumen ejecutivo del análisis.\n\n---\n\n## Hallazgos completos\n- ...";

describe("FindingsReport", () => {
  it("shows only the narrative portion of final_report as the summary", () => {
    render(<FindingsReport finalReport={finalReport} findings={[]} />);

    expect(screen.getByText("Resumen ejecutivo del análisis.")).toBeInTheDocument();
    expect(screen.queryByText(/Hallazgos completos/)).not.toBeInTheDocument();
  });

  it("shows a placeholder message when there are no findings", () => {
    render(<FindingsReport finalReport={finalReport} findings={[]} />);

    expect(screen.getByText("No se encontraron hallazgos.")).toBeInTheDocument();
  });

  it("renders each finding's description, specialist label and severity group", () => {
    const findings = [
      makeFinding({ id: 1, severity: "critical", description: "SQL injection en login" }),
      makeFinding({ id: 2, severity: "low", specialist: "performance", description: "N+1 query" }),
    ];

    render(<FindingsReport finalReport={finalReport} findings={findings} />);

    expect(screen.getByText("SQL injection en login")).toBeInTheDocument();
    expect(screen.getByText("N+1 query")).toBeInTheDocument();
    expect(screen.getByText("Rendimiento")).toBeInTheDocument();
  });

  it("shows the file path only when the finding has one", () => {
    const findings = [
      makeFinding({ id: 1, file_path: "app/main.py" }),
      makeFinding({ id: 2, file_path: null, description: "sin archivo" }),
    ];

    render(<FindingsReport finalReport={finalReport} findings={findings} />);

    expect(screen.getByText("app/main.py")).toBeInTheDocument();
  });

  it("shows the suggestion box only when the finding has one", () => {
    const findings = [
      makeFinding({ id: 1, suggestion: "Usa parámetros preparados" }),
      makeFinding({ id: 2, suggestion: null, description: "sin sugerencia" }),
    ];

    render(<FindingsReport finalReport={finalReport} findings={findings} />);

    expect(screen.getByText("Usa parámetros preparados")).toBeInTheDocument();
  });

  it("filters findings down to a single severity when its chip is clicked", async () => {
    const user = userEvent.setup();
    const findings = [
      makeFinding({ id: 1, severity: "critical", description: "hallazgo crítico" }),
      makeFinding({ id: 2, severity: "low", description: "hallazgo menor" }),
    ];

    render(<FindingsReport finalReport={finalReport} findings={findings} />);

    await user.click(screen.getByRole("button", { name: /Crítico/ }));

    expect(screen.getByText("hallazgo crítico")).toBeInTheDocument();
    expect(screen.queryByText("hallazgo menor")).not.toBeInTheDocument();
  });

  it("shows every finding again after switching back to the Todas filter", async () => {
    const user = userEvent.setup();
    const findings = [
      makeFinding({ id: 1, severity: "critical", description: "hallazgo crítico" }),
      makeFinding({ id: 2, severity: "low", description: "hallazgo menor" }),
    ];

    render(<FindingsReport finalReport={finalReport} findings={findings} />);

    await user.click(screen.getByRole("button", { name: /Crítico/ }));
    await user.click(screen.getByRole("button", { name: /Todas/ }));

    expect(screen.getByText("hallazgo crítico")).toBeInTheDocument();
    expect(screen.getByText("hallazgo menor")).toBeInTheDocument();
  });

  it("uses the singular form for exactly one finding in the count", () => {
    render(<FindingsReport finalReport={finalReport} findings={[makeFinding({ id: 1 })]} />);

    expect(screen.getByText("1 hallazgo")).toBeInTheDocument();
  });
});
