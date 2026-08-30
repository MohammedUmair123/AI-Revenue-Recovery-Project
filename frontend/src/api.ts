const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface EventRow {
  id: string;
  customer_name: string | null;
  event_type: string;
  amount: number;
  status: string;
  root_cause: string | null;
  diagnosis_confidence: number | null;
  contact_attempts: number;
  amount_recovered: number;
  created_at: string;
}

export interface AuditRow {
  id: string;
  event_id: string | null;
  stage: string;
  actor: string;
  summary: string;
  detail: string | null;
  timestamp: string;
}

export interface Metrics {
  total_at_risk: number;
  total_recovered: number;
  recovery_rate: number;
  total_events: number;
  recovered_count: number;
  stopped_count: number;
  escalated_count: number;
  by_cause: { root_cause: string; count: number; recovered: number }[];
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const api = {
  seed: (n_customers = 40, n_events = 120) =>
    request(`/api/seed?n_customers=${n_customers}&n_events=${n_events}`, { method: "POST" }),
  runBatch: () => request<{ events_processed: number; total_recovered: number; results: any[] }>(
    "/api/run-batch",
    { method: "POST" }
  ),
  getEvents: () => request<EventRow[]>("/api/events"),
  getAudit: () => request<AuditRow[]>("/api/audit"),
  getMetrics: () => request<Metrics>("/api/metrics"),
};
