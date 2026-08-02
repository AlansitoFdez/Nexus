"use client";

/**
 * Subscribes to backend/app/api/websocket.py's per-analysis-request
 * WebSocket channel and splits incoming messages into two buckets:
 *
 * - Structured trace events (WSEvent) — always JSON objects carrying a
 *   "type" field, produced by ws_events.build_event() in runner.py's
 *   astream() loop. These power the agent trace UI.
 * - Plain-text notices — a handful of human-readable strings some nodes
 *   (entry_node, post_comment_node) send directly, predating the
 *   structured event stream and left as-is rather than folded into it,
 *   since they're informational log lines, not state this UI derives
 *   anything from.
 *
 * Anything that fails to parse as JSON, or parses but has no "type"
 * field, is treated as a plain-text notice — this is what tells the two
 * apart on the same socket, not a separate channel or prefix.
 */

import { useEffect, useState } from "react";
import type { WSEvent } from "@/lib/api/types";

function wsUrlFor(analysisRequestId: number): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const wsBase = apiUrl.replace(/^http/, "ws");
  return `${wsBase}/ws/analysis-requests/${analysisRequestId}`;
}

interface UseAnalysisRequestSocketResult {
  events: WSEvent[];
  logs: string[];
  isConnected: boolean;
}

export function useAnalysisRequestSocket(
  analysisRequestId: number | null,
): UseAnalysisRequestSocketResult {
  const [events, setEvents] = useState<WSEvent[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (analysisRequestId === null) {
      return;
    }

    // Reset when switching from watching one analysis request to
    // another — otherwise a previous run's events would linger and mix
    // in with the new one's trace.
    setEvents([]);
    setLogs([]);

    const socket = new WebSocket(wsUrlFor(analysisRequestId));

    socket.onopen = () => setIsConnected(true);
    socket.onclose = () => setIsConnected(false);

    socket.onmessage = (message: MessageEvent<string>) => {
      try {
        const parsed: unknown = JSON.parse(message.data);
        if (parsed && typeof parsed === "object" && "type" in parsed) {
          setEvents((previous) => [...previous, parsed as WSEvent]);
          return;
        }
      } catch {
        // Not JSON at all — falls through to the plain-text branch below.
      }
      setLogs((previous) => [...previous, message.data]);
    };

    return () => socket.close();
  }, [analysisRequestId]);

  return { events, logs, isConnected };
}
