"use client";

import { useState, type FormEvent } from "react";
import { createAnalysisRequest, ApiError } from "@/lib/api/client";
import type { AnalysisRequest, SourceType } from "@/lib/api/types";

interface NewAnalysisFormProps {
  onCreated: (request: AnalysisRequest) => void;
}

const REVIEW_SUGGESTIONS = ["seguridad", "rendimiento", "patrones de diseño", "buenas prácticas"];

const textInputClasses =
  "border-line bg-canvas text-ink focus:border-accent focus:ring-accent/10 w-full rounded-[9px] border px-3 py-2.5 font-mono text-[12.5px] outline-none focus:ring-[3px]";

export function NewAnalysisForm({ onCreated }: NewAnalysisFormProps) {
  const [sourceType, setSourceType] = useState<SourceType>("github_repo");
  const [repoUrl, setRepoUrl] = useState("");
  const [pastedCode, setPastedCode] = useState("");
  const [reviewRequest, setReviewRequest] = useState("");
  const [postToPr, setPostToPr] = useState(false);
  const [prNumber, setPrNumber] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Appends to whatever's already there instead of replacing it, so
  // clicking two suggestions composes "seguridad, rendimiento" — mirrors
  // how someone would type a second concern after the first, not start over.
  function addSuggestion(label: string) {
    setReviewRequest((current) => {
      const trimmed = current.trim();
      return trimmed ? `${trimmed.replace(/[.\s]+$/, "")}, ${label}` : `Revisa ${label}`;
    });
  }

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
    <form onSubmit={handleSubmit} className="flex flex-col gap-[18px]">
      <div className="flex flex-col gap-2">
        <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
          Origen del código
        </span>
        <div className="border-line-soft bg-canvas grid grid-cols-2 gap-1 rounded-[10px] border p-1">
          <label className="cursor-pointer">
            <input
              type="radio"
              name="source_type"
              className="peer sr-only"
              checked={sourceType === "github_repo"}
              onChange={() => setSourceType("github_repo")}
            />
            <span className="peer-checked:border-line-strong peer-checked:bg-active peer-checked:text-ink text-ink-muted block rounded-[7px] border border-transparent px-1.5 py-2 text-center text-[12.5px] font-medium">
              Repositorio de GitHub
            </span>
          </label>
          <label className="cursor-pointer">
            <input
              type="radio"
              name="source_type"
              className="peer sr-only"
              checked={sourceType === "pasted_code"}
              onChange={() => setSourceType("pasted_code")}
            />
            <span className="peer-checked:border-line-strong peer-checked:bg-active peer-checked:text-ink text-ink-muted block rounded-[7px] border border-transparent px-1.5 py-2 text-center text-[12.5px] font-medium">
              Código pegado
            </span>
          </label>
        </div>
      </div>

      {sourceType === "github_repo" ? (
        <div className="flex flex-col gap-3">
          <label className="flex flex-col gap-1.5">
            <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
              URL del repositorio
            </span>
            <input
              type="url"
              required
              placeholder="https://github.com/owner/repo"
              value={repoUrl}
              onChange={(event) => setRepoUrl(event.target.value)}
              className={textInputClasses}
            />
          </label>

          <label className="border-line bg-canvas flex cursor-pointer items-start gap-2.5 rounded-[9px] border px-3 py-[11px]">
            <input
              type="checkbox"
              aria-label="Comentar en un PR"
              checked={postToPr}
              onChange={(event) => setPostToPr(event.target.checked)}
              className="accent-accent mt-0.5 size-[15px] cursor-pointer"
            />
            <span className="flex flex-col gap-0.5">
              <span className="text-ink text-[13px] font-medium">Comentar en un PR</span>
              <span className="text-ink-dim text-[11.5px]">
                Pedirá tu aprobación antes de publicar
              </span>
            </span>
          </label>

          {postToPr && (
            <label className="flex flex-col gap-1.5">
              <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
                Número de PR
              </span>
              <input
                type="number"
                required
                min={1}
                placeholder="Número de PR"
                value={prNumber}
                onChange={(event) => setPrNumber(event.target.value)}
                className={textInputClasses}
              />
            </label>
          )}
        </div>
      ) : (
        <label className="flex flex-col gap-1.5">
          <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
            Código a revisar
          </span>
          <textarea
            required
            rows={9}
            placeholder="Pega el código a revisar"
            value={pastedCode}
            onChange={(event) => setPastedCode(event.target.value)}
            className={`${textInputClasses} leading-[1.6]`}
          />
        </label>
      )}

      <div className="flex flex-col gap-2">
        <span className="text-ink-dim font-mono text-[9.5px] tracking-[0.1em] uppercase">
          ¿Qué quieres que se revise?
        </span>
        <textarea
          required
          rows={3}
          placeholder="¿Qué quieres que se revise? (seguridad, rendimiento, patrones de diseño, buenas prácticas…)"
          value={reviewRequest}
          onChange={(event) => setReviewRequest(event.target.value)}
          className="border-line bg-canvas text-ink focus:border-accent focus:ring-accent/10 w-full rounded-[9px] border px-3 py-2.5 text-[13px] leading-[1.55] outline-none focus:ring-[3px]"
        />
        <div className="flex flex-wrap gap-1.5">
          {REVIEW_SUGGESTIONS.map((label) => (
            <button
              key={label}
              type="button"
              onClick={() => addSuggestion(label)}
              className="border-line bg-canvas text-ink-muted hover:border-line-strong hover:text-ink rounded-full border px-2.5 py-1 text-[11.5px]"
            >
              + {label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <p className="bg-critical/[0.08] border-critical/30 text-danger-ink rounded-[9px] border px-3 py-2.5 text-[12.5px]">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={submitting}
        className="bg-accent text-accent-ink hover:brightness-[1.08] w-full rounded-[10px] py-3 text-[13.5px] font-semibold disabled:opacity-55"
      >
        {submitting ? "Creando…" : "Analizar"}
      </button>
    </form>
  );
}
