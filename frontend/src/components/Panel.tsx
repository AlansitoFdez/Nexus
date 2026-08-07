import type { ReactNode } from "react";

/**
 * The bordered card every top-level section of the dashboard sits in:
 * a header rule with a title (plus optional meta on the right) over a
 * padded body. Extracted because the exact same chrome repeats five
 * times in page.tsx, and the design's whole readability depends on those
 * paddings and border tones staying identical across all of them.
 *
 * `tone` is not decoration: "warn" is the human-approval gate (the one
 * place the graph stops and waits for a person) and "danger" is a failed
 * run. Both need to read as different from a normal result panel at a
 * glance, before any text is read.
 */
type PanelTone = "default" | "warn" | "danger";

const TONE_STYLES: Record<PanelTone, { shell: string; rule: string; title: string }> = {
  default: {
    shell: "bg-panel border-line",
    rule: "border-line-soft",
    title: "text-ink",
  },
  warn: {
    shell: "border-high/30 bg-gradient-to-b from-high/[0.07] to-high/[0.02]",
    rule: "border-high/20",
    title: "text-warn-ink",
  },
  danger: {
    shell: "border-critical/30 bg-critical/5",
    rule: "border-critical/20",
    title: "text-danger-ink",
  },
};

interface PanelProps {
  title: ReactNode;
  meta?: ReactNode;
  tone?: PanelTone;
  children: ReactNode;
}

export function Panel({ title, meta, tone = "default", children }: PanelProps) {
  const styles = TONE_STYLES[tone];

  return (
    <section className={`overflow-hidden rounded-[14px] border ${styles.shell}`}>
      <div
        className={`flex flex-wrap items-center justify-between gap-3 border-b px-[18px] py-[15px] ${styles.rule}`}
      >
        <h2 className={`text-sm font-semibold tracking-[-0.01em] ${styles.title}`}>{title}</h2>
        {meta}
      </div>
      <div className="p-[18px]">{children}</div>
    </section>
  );
}
