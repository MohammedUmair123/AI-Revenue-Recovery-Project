import { useState } from "react";
import { api, EventRow, AuditRow, Metrics } from "./api";
import Dashboard from "./components/Dashboard";
import EventTable from "./components/EventTable";
import AuditTrail from "./components/AuditTrail";

export default function App() {
  const [events, setEvents] = useState<EventRow[]>([]);
  const [logs, setLogs] = useState<AuditRow[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refreshAll() {
    const [ev, au, me] = await Promise.all([api.getEvents(), api.getAudit(), api.getMetrics()]);
    setEvents(ev);
    setLogs(au);
    setMetrics(me);
  }

  async function handleSeed() {
    setError(null);
    setLoading("seed");
    try {
      await api.seed(40, 120);
      await refreshAll();
    } catch (e) {
      setError("Could not reach the backend. Is it running on the configured API URL?");
    } finally {
      setLoading(null);
    }
  }

  async function handleRunBatch() {
    setError(null);
    setLoading("batch");
    try {
      await api.runBatch();
      await refreshAll();
    } catch (e) {
      setError("Batch run failed. Check the backend logs.");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="min-h-screen bg-ink-950 text-paper">
      <header className="border-b border-ink-700 px-8 py-6 flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-slate-400 mb-1">AI Revenue Recovery</div>
          <h1 className="text-2xl font-semibold">Recovery Ledger</h1>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSeed}
            disabled={loading !== null}
            className="px-4 py-2 text-sm border border-ink-700 rounded-sm hover:border-slate-400 transition-colors disabled:opacity-50"
          >
            {loading === "seed" ? "Seeding…" : "Seed Batch Data"}
          </button>
          <button
            onClick={handleRunBatch}
            disabled={loading !== null}
            className="px-4 py-2 text-sm bg-signal-green/90 text-ink-950 font-medium rounded-sm hover:bg-signal-green transition-colors disabled:opacity-50"
          >
            {loading === "batch" ? "Running…" : "Run Recovery Batch"}
          </button>
        </div>
      </header>

      <main className="p-8 space-y-6 max-w-7xl mx-auto">
        {error && (
          <div className="border border-signal-red text-signal-red text-sm rounded-sm px-4 py-3">{error}</div>
        )}

        <Dashboard metrics={metrics} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <EventTable events={events} />
          <AuditTrail logs={logs} />
        </div>
      </main>

      <footer className="px-8 py-6 text-xs text-slate-500 border-t border-ink-700">
        Bounded recovery workflow · stopping rules + compliance gates enforced before every action
      </footer>
    </div>
  );
}
