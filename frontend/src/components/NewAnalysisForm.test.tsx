import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NewAnalysisForm } from "./NewAnalysisForm";
import { createAnalysisRequest, ApiError } from "@/lib/api/client";
import type { AnalysisRequest } from "@/lib/api/types";

vi.mock("@/lib/api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/api/client")>();
  return { ...actual, createAnalysisRequest: vi.fn() };
});

const createAnalysisRequestMock = vi.mocked(createAnalysisRequest);

const FAKE_REQUEST: AnalysisRequest = {
  id: 1,
  source_type: "github_repo",
  repo_url: "https://github.com/owner/repo",
  pasted_code: null,
  review_request: "seguridad",
  post_to_pr: false,
  pr_number: null,
  status: "pending",
  final_report: null,
  pr_comment_url: null,
  findings: [],
  created_at: "2026-08-06T00:00:00Z",
  updated_at: null,
};

describe("NewAnalysisForm", () => {
  beforeEach(() => {
    createAnalysisRequestMock.mockReset();
  });

  it("defaults to the GitHub repo source with the repo URL field visible", () => {
    render(<NewAnalysisForm onCreated={vi.fn()} />);

    expect(screen.getByPlaceholderText("https://github.com/owner/repo")).toBeInTheDocument();
    expect(screen.queryByPlaceholderText("Pega el código a revisar")).not.toBeInTheDocument();
  });

  it("switches to the pasted-code field when that source is selected", async () => {
    const user = userEvent.setup();
    render(<NewAnalysisForm onCreated={vi.fn()} />);

    await user.click(screen.getByLabelText("Código pegado"));

    expect(screen.getByPlaceholderText("Pega el código a revisar")).toBeInTheDocument();
    expect(screen.queryByPlaceholderText("https://github.com/owner/repo")).not.toBeInTheDocument();
  });

  it("submits a pasted_code payload without repo_url or post_to_pr", async () => {
    const user = userEvent.setup();
    createAnalysisRequestMock.mockResolvedValue(FAKE_REQUEST);
    const onCreated = vi.fn();
    render(<NewAnalysisForm onCreated={onCreated} />);

    await user.click(screen.getByLabelText("Código pegado"));
    await user.type(screen.getByPlaceholderText("Pega el código a revisar"), "print(1)");
    await user.type(
      screen.getByPlaceholderText(/Qué quieres que se revise/),
      "seguridad",
    );
    await user.click(screen.getByRole("button", { name: "Analizar" }));

    await waitFor(() => {
      expect(createAnalysisRequestMock).toHaveBeenCalledWith({
        source_type: "pasted_code",
        pasted_code: "print(1)",
        review_request: "seguridad",
      });
    });
    expect(onCreated).toHaveBeenCalledWith(FAKE_REQUEST);
  });

  it("submits a github_repo payload with post_to_pr false when the checkbox is left unchecked", async () => {
    const user = userEvent.setup();
    createAnalysisRequestMock.mockResolvedValue(FAKE_REQUEST);
    render(<NewAnalysisForm onCreated={vi.fn()} />);

    await user.type(
      screen.getByPlaceholderText("https://github.com/owner/repo"),
      "https://github.com/owner/repo",
    );
    await user.type(
      screen.getByPlaceholderText(/Qué quieres que se revise/),
      "rendimiento",
    );
    await user.click(screen.getByRole("button", { name: "Analizar" }));

    await waitFor(() => {
      expect(createAnalysisRequestMock).toHaveBeenCalledWith({
        source_type: "github_repo",
        repo_url: "https://github.com/owner/repo",
        review_request: "rendimiento",
        post_to_pr: false,
      });
    });
  });

  it("reveals the PR number field and submits post_to_pr true when the checkbox is checked", async () => {
    const user = userEvent.setup();
    createAnalysisRequestMock.mockResolvedValue(FAKE_REQUEST);
    render(<NewAnalysisForm onCreated={vi.fn()} />);

    await user.type(
      screen.getByPlaceholderText("https://github.com/owner/repo"),
      "https://github.com/owner/repo",
    );
    await user.click(screen.getByLabelText("Comentar en un PR"));
    expect(screen.getByPlaceholderText("Número de PR")).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText("Número de PR"), "42");
    await user.type(
      screen.getByPlaceholderText(/Qué quieres que se revise/),
      "patrones de diseño",
    );
    await user.click(screen.getByRole("button", { name: "Analizar" }));

    await waitFor(() => {
      expect(createAnalysisRequestMock).toHaveBeenCalledWith({
        source_type: "github_repo",
        repo_url: "https://github.com/owner/repo",
        review_request: "patrones de diseño",
        post_to_pr: true,
        pr_number: 42,
      });
    });
  });

  it("shows the ApiError message when the request is rejected", async () => {
    const user = userEvent.setup();
    createAnalysisRequestMock.mockRejectedValue(new ApiError(422, "review_request es obligatorio"));
    render(<NewAnalysisForm onCreated={vi.fn()} />);

    await user.type(
      screen.getByPlaceholderText("https://github.com/owner/repo"),
      "https://github.com/owner/repo",
    );
    await user.type(screen.getByPlaceholderText(/Qué quieres que se revise/), "x");
    await user.click(screen.getByRole("button", { name: "Analizar" }));

    expect(await screen.findByText("review_request es obligatorio")).toBeInTheDocument();
  });

  it("shows a generic error message for a non-ApiError failure", async () => {
    const user = userEvent.setup();
    createAnalysisRequestMock.mockRejectedValue(new Error("network down"));
    render(<NewAnalysisForm onCreated={vi.fn()} />);

    await user.type(
      screen.getByPlaceholderText("https://github.com/owner/repo"),
      "https://github.com/owner/repo",
    );
    await user.type(screen.getByPlaceholderText(/Qué quieres que se revise/), "x");
    await user.click(screen.getByRole("button", { name: "Analizar" }));

    expect(
      await screen.findByText("No se pudo crear el análisis, inténtalo de nuevo."),
    ).toBeInTheDocument();
  });
});
