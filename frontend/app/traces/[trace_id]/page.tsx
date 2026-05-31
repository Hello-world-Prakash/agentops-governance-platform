"use client";

import { ArrowLeft, BadgeCheck, ClipboardList, FileText, Gavel, ShieldAlert, ShieldCheck, UserRound } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { AuditLog, TraceEvent } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

function titleize(value: string) {
  return value.replaceAll("_", " ");
}

function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function statusKind(value: string) {
  return value.includes("block") ? "danger" : value.includes("manual") || value.includes("human") || value.includes("pending") ? "warn" : "ok";
}

export default function TraceDetailPage({ params }: { params: Promise<{ trace_id: string }> }) {
  const [traceId, setTraceId] = useState<string>("");
  const [auditLog, setAuditLog] = useState<AuditLog | null>(null);
  const [traceEvents, setTraceEvents] = useState<TraceEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then((resolved) => setTraceId(resolved.trace_id)).catch(() => setError("Unable to load trace id"));
  }, [params]);

  useEffect(() => {
    if (!traceId) {
      return;
    }

    const controller = new AbortController();
    async function loadTrace() {
      setError(null);
      try {
        const response = await fetch(`${API_BASE}/audit-logs/${traceId}`, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`Trace lookup failed with ${response.status}`);
        }
        setAuditLog((await response.json()) as AuditLog);
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : "Unable to load trace");
        }
      }
    }

    void loadTrace();
    return () => controller.abort();
  }, [traceId]);

  useEffect(() => {
    if (!traceId) {
      return;
    }

    const source = new EventSource(`${API_BASE}/audit-logs/${traceId}/stream`);
    source.onmessage = (event) => {
      try {
        setTraceEvents((current) => [...current, JSON.parse(event.data) as TraceEvent]);
      } catch {
        return;
      }
    };
    source.addEventListener("audit_log_created", (event) => {
      setTraceEvents((current) => [...current, JSON.parse((event as MessageEvent).data) as TraceEvent]);
    });
    source.addEventListener("approval_created", (event) => {
      setTraceEvents((current) => [...current, JSON.parse((event as MessageEvent).data) as TraceEvent]);
    });
    source.addEventListener("approval_decided", (event) => {
      setTraceEvents((current) => [...current, JSON.parse((event as MessageEvent).data) as TraceEvent]);
    });

    return () => source.close();
  }, [traceId]);

  const timeline = useMemo(() => {
    if (!auditLog) {
      return [];
    }

    return [
      {
        icon: <UserRound size={18} />,
        title: "User Request",
        status: `${auditLog.user_request.customer_id ?? "Unknown customer"} / $${auditLog.user_request.claim_amount ?? 0}`,
        body: auditLog.user_request.claim_text ?? "No request text recorded.",
      },
      {
        icon: <FileText size={18} />,
        title: "Agent Output",
        status: titleize(auditLog.action_requested),
        body: auditLog.agent_output.reasoning ?? JSON.stringify(auditLog.agent_output),
      },
      {
        icon: <ClipboardList size={18} />,
        title: "Retrieved Evidence",
        status: `${auditLog.agent_output.evidence?.length ?? 0} evidence items`,
        body: auditLog.agent_output.evidence?.join(" ") ?? "No policy evidence recorded in this trace.",
      },
      {
        icon: <ShieldAlert size={18} />,
        title: "Risk Score",
        status: `${titleize(auditLog.risk_level)} / ${percent(auditLog.risk_score)}`,
        body: auditLog.prompt_injection_detected ? "Prompt-injection indicators were detected." : "Prompt-injection detector passed.",
      },
      {
        icon: <Gavel size={18} />,
        title: "Governance Decision",
        status: titleize(auditLog.governance_decision),
        body: auditLog.policy_reasons.join(" "),
      },
      {
        icon: <BadgeCheck size={18} />,
        title: "Approval And Final Status",
        status: `${titleize(auditLog.approval_status)} / ${titleize(auditLog.final_status)}`,
        body: `Audit record ${auditLog.id} was written at ${new Date(auditLog.timestamp).toLocaleString()}.`,
      },
    ];
  }, [auditLog]);

  return (
    <main className="traceShell">
      <section className="traceHeader">
        <Link href="/" className="iconTextButton">
          <ArrowLeft size={17} />
          Dashboard
        </Link>
        <div>
          <p className="eyebrow">Trace Timeline</p>
          <h1>{traceId || "Loading trace"}</h1>
        </div>
        {auditLog && <span className={`statusBadge ${statusKind(auditLog.governance_decision)}`}>{titleize(auditLog.governance_decision)}</span>}
      </section>

      {error && (
        <section className="alert">
          <ShieldAlert size={18} />
          <span>{error}</span>
        </section>
      )}

      {!auditLog && !error && (
        <section className="panel mutedPanel">
          <ShieldCheck size={28} />
          <h2>Loading Trace</h2>
          <p>Fetching audit evidence and governance decision history.</p>
        </section>
      )}

      {auditLog && (
        <section className="traceGrid">
          <aside className="panel traceSummary">
            <h2>Trace Summary</h2>
            <div>
              <span>Agent</span>
              <strong>{titleize(auditLog.agent_name)}</strong>
            </div>
            <div>
              <span>Recommended Action</span>
              <strong>{titleize(auditLog.action_requested)}</strong>
            </div>
            <div>
              <span>Risk</span>
              <strong>{titleize(auditLog.risk_level)} / {percent(auditLog.risk_score)}</strong>
            </div>
            <div>
              <span>Approval</span>
              <strong>{titleize(auditLog.approval_status)}</strong>
            </div>
            <div>
              <span>Final Status</span>
              <strong>{titleize(auditLog.final_status)}</strong>
            </div>
            <div>
              <span>Live Events</span>
              <strong>{traceEvents.length}</strong>
            </div>
          </aside>

          <section className="panel traceTimeline">
            {timeline.map((item) => (
              <article className="timelineItem" key={item.title}>
                <div className="timelineIcon">{item.icon}</div>
                <div>
                  <span>{item.title}</span>
                  <strong>{item.status}</strong>
                  <p>{item.body}</p>
                </div>
              </article>
            ))}
            {traceEvents.length > 0 && (
              <article className="timelineItem">
                <div className="timelineIcon"><ShieldCheck size={18} /></div>
                <div>
                  <span>Real-time Stream</span>
                  <strong>{traceEvents.length} event{traceEvents.length === 1 ? "" : "s"}</strong>
                  <p>{traceEvents.map((event) => event.event_type).join(", ")}</p>
                </div>
              </article>
            )}
          </section>
        </section>
      )}
    </main>
  );
}
