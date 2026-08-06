import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { AgentTrace } from "./AgentTrace";
import type { WSEvent } from "@/lib/api/types";

describe("AgentTrace", () => {
  it("shows a connecting message while there is no socket connection yet", () => {
    render(<AgentTrace events={[]} isConnected={false} />);

    expect(screen.getByText("Conectando…")).toBeInTheDocument();
  });

  it("shows a waiting message once connected but before the router picks specialists", () => {
    render(<AgentTrace events={[]} isConnected={true} />);

    expect(screen.getByText("Esperando a que el router elija especialistas…")).toBeInTheDocument();
  });

  it("renders a running badge for each specialist the router just started", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security", "performance"] },
    ];

    render(<AgentTrace events={events} isConnected={true} />);

    expect(screen.getByText("Seguridad")).toBeInTheDocument();
    expect(screen.getByText("Rendimiento")).toBeInTheDocument();
  });

  it("shows the findings count once a specialist finishes successfully", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security"] },
      { type: "specialist_finished", specialist: "security", findings_count: 3, failed: false },
    ];

    render(<AgentTrace events={events} isConnected={true} />);

    expect(screen.getByText(/3 hallazgos/)).toBeInTheDocument();
  });

  it("uses the singular form for exactly one finding", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["security"] },
      { type: "specialist_finished", specialist: "security", findings_count: 1, failed: false },
    ];

    render(<AgentTrace events={events} isConnected={true} />);

    expect(screen.getByText(/1 hallazgo\b/)).toBeInTheDocument();
  });

  it("marks a failed specialist with an error marker instead of a findings count", () => {
    const events: WSEvent[] = [
      { type: "specialists_started", specialists: ["performance"] },
      { type: "specialist_finished", specialist: "performance", findings_count: 0, failed: true },
    ];

    render(<AgentTrace events={events} isConnected={true} />);

    expect(screen.getByText("error", { exact: false })).toBeInTheDocument();
    expect(screen.queryByText("0 hallazgos")).not.toBeInTheDocument();
  });
});
