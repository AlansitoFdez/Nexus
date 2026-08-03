"use client";

import { useState, type FormEvent } from "react";
import { createAnalysisRequest, ApiError } from "@/lib/api/client";
import type { AnalysisRequest, SourceType } from "@/lib/api/types";

interface NewAnalysisFormProps {
  onCreated: (request: AnalysisRequest) => void;
}

export function NewAnalysisForm({ onCreated }: NewAnalysisFormProps) {
  const [sourceType, setSourceType] = useState<SourceType>("github_repo");
  const [repoUrl, setRepoUrl] = useState("");
  const [pastedCode, setPastedCode] = useState("");
  const [reviewRequest, setReviewRequest] = useState("");
  const [postToPr, setPostToPr] = useState(false);
  const [prNumber, setPrNumber] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const request =
        sourceType === "pasted_code"
          ? await createAnalysisRequest({
              source_type: "pasted_code",
              pasted_code: pastedCode,
              review_request: reviewRequest,
            })
          : postToPr
            ? await createAnalysisRequest({
                source_type: "github_repo",
                repo_url: repoUrl,
                review_request: reviewRequest,
                post_to_pr: true,
                pr_number: Number(prNumber),
              })
            : await createAnalysisRequest({
                source_type: "github_repo",
                repo_url: repoUrl,
                review_request: reviewRequest,
                post_to_pr: false,
              });

      onCreated(request);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "No se pudo crear el análisis, inténtalo de nuevo.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <div className="flex gap-4">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="radio"
            name="source_type"
            checked={sourceType === "github_repo"}
            onChange={() => setSourceType("github_repo")}
          />
          Repositorio de GitHub
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="radio"
            name="source_type"
            checked={sourceType === "pasted_code"}
            onChange={() => setSourceType("pasted_code")}
          />
          Código pegado
        </label>
      </div>

      {sourceType === "github_repo" ? (
        <div className="space-y-2">
          <input
            type="url"
            required
            placeholder="https://github.com/owner/repo"
            value={repoUrl}
            onChange={(event) => setRepoUrl(event.target.value)}
            className="w-full rounded border px-3 py-1.5 text-sm"
          />
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={postToPr}
              onChange={(event) => setPostToPr(event.target.checked)}
            />
            Comentar en un PR
          </label>
          {postToPr && (
            <input
              type="number"
              required
              min={1}
              placeholder="Número de PR"
              value={prNumber}
              onChange={(event) => setPrNumber(event.target.value)}
              className="w-full rounded border px-3 py-1.5 text-sm"
            />
          )}
        </div>
      ) : (
        <textarea
          required
          rows={6}
          placeholder="Pega el código a revisar"
          value={pastedCode}
          onChange={(event) => setPastedCode(event.target.value)}
          className="w-full rounded border px-3 py-1.5 text-sm font-mono"
        />
      )}

      <textarea
        required
        rows={2}
        placeholder="¿Qué quieres que se revise? (seguridad, rendimiento, patrones de diseño, buenas prácticas…)"
        value={reviewRequest}
        onChange={(event) => setReviewRequest(event.target.value)}
        className="w-full rounded border px-3 py-1.5 text-sm"
      />

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="rounded bg-blue-600 px-4 py-1.5 text-sm font-medium text-white disabled:opacity-50"
      >
        {submitting ? "Creando…" : "Analizar"}
      </button>
    </form>
  );
}
