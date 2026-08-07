import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MetricsPanel } from "./MetricsPanel";
import { getMetrics } from "@/lib/api/client";
import type { Metrics } from "@/lib/api/types";

vi.mock("@/lib/api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/api/client")>();
  return { ...actual, getMetrics: vi.fn() };
});

const getMetricsMock = vi.mocked(getMetrics);

const EMPTY_METRICS: Metrics = {
  total_analysis_requests: 0,
  by_status: {},
  findings_by_specialist: {},
  findings_by_severity: {},
  pr_comments_posted: 0,
  average_analysis_seconds: null,
};

describe("MetricsPanel", () => {
  beforeEach(() => {
    getMetricsMock.mockReset();
  });

  it("shows a loading message while the fetch is in flight", () => {
    getMetricsMock.mockReturnValue(new Promise(() => {}));

    render(<MetricsPanel />);

    expect(screen.getByText("Cargando métricas…")).toBeInTheDocument();
  });

  it("shows an error message when the fetch fails", async () => {
    getMetricsMock.mockRejectedValue(new Error("network down"));

    render(<MetricsPanel />);

    expect(await screen.findByText("No se pudieron cargar las métricas.")).toBeInTheDocument();
  });

  it("shows placeholder text for every count section when there is no data yet", async () => {
    getMetricsMock.mockResolvedValue(EMPTY_METRICS);

    render(<MetricsPanel />);

    expect(await screen.findAllByText("Sin datos todavía.")).toHaveLength(3);
  });

  it("renders the status breakdown using Spanish labels", async () => {
    getMetricsMock.mockResolvedValue({
      ...EMPTY_METRICS,
      total_analysis_requests: 5,
      by_status: { completed: 3, running: 2 },
    });

    render(<MetricsPanel />);

    expect(await screen.findByText("5")).toBeInTheDocument();
    expect(screen.getByText("Completados")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("En curso")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("renders findings by specialist using the shared specialist labels", async () => {
    getMetricsMock.mockResolvedValue({
      ...EMPTY_METRICS,
      findings_by_specialist: { security: 4 },
    });

    render(<MetricsPanel />);

    expect(await screen.findByText("Seguridad")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
  });

  it("renders findings by severity using Spanish labels", async () => {
    getMetricsMock.mockResolvedValue({
      ...EMPTY_METRICS,
      findings_by_severity: { critical: 1 },
    });

    render(<MetricsPanel />);

    expect(await screen.findByText("Crítico")).toBeInTheDocument();
  });

  it("orders the status breakdown by pipeline order, not by input order", async () => {
    getMetricsMock.mockResolvedValue({
      ...EMPTY_METRICS,
      by_status: { failed: 1, pending: 2, completed: 3 },
    });

    render(<MetricsPanel />);
    await screen.findByText("Pendientes");

    const labels = screen.getAllByText(/Pendientes|Completados$|Fallidos/).map((el) => el.textContent);
    expect(labels).toEqual(["Pendientes", "Completados", "Fallidos"]);
  });

  it("scales each bar's width relative to the largest count in its group", async () => {
    getMetricsMock.mockResolvedValue({
      ...EMPTY_METRICS,
      findings_by_severity: { critical: 4, low: 2 },
    });

    render(<MetricsPanel />);
    const criticalRow = (await screen.findByText("Crítico")).closest("li");
    const lowRow = screen.getByText("Bajo").closest("li");

    expect(criticalRow?.querySelector("[style]")).toHaveStyle({ width: "100%" });
    expect(lowRow?.querySelector("[style]")).toHaveStyle({ width: "50%" });
  });

  it("formats an average duration under a minute in seconds", async () => {
    getMetricsMock.mockResolvedValue({ ...EMPTY_METRICS, average_analysis_seconds: 45 });

    render(<MetricsPanel />);

    expect(await screen.findByText("45.0s")).toBeInTheDocument();
  });

  it("formats an average duration of a minute or more in minutes", async () => {
    getMetricsMock.mockResolvedValue({ ...EMPTY_METRICS, average_analysis_seconds: 150 });

    render(<MetricsPanel />);

    expect(await screen.findByText("2.5 min")).toBeInTheDocument();
  });

  it("shows a placeholder when there is no average duration yet", async () => {
    getMetricsMock.mockResolvedValue(EMPTY_METRICS);

    render(<MetricsPanel />);

    expect(await screen.findByText("Sin datos todavía")).toBeInTheDocument();
  });

  it("shows the number of PR comments posted", async () => {
    getMetricsMock.mockResolvedValue({ ...EMPTY_METRICS, pr_comments_posted: 7 });

    render(<MetricsPanel />);

    expect(await screen.findByText("7")).toBeInTheDocument();
  });

  it("refetches metrics when refreshKey changes", async () => {
    getMetricsMock.mockResolvedValue(EMPTY_METRICS);

    const { rerender } = render(<MetricsPanel refreshKey={1} />);
    await waitFor(() => expect(getMetricsMock).toHaveBeenCalledTimes(1));

    rerender(<MetricsPanel refreshKey={2} />);
    await waitFor(() => expect(getMetricsMock).toHaveBeenCalledTimes(2));
  });
});
