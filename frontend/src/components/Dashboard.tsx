import { Metrics } from "../api";

function fmt(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

export default function Dashboard({ metrics }: { metrics: Metrics | null }) {
  if (!metrics) {
    return (
      <div className="border border-ink-700 rounded-sm p-6 text-slate-400 text-sm">
        No batch run yet. Seed data and run a batch to see the ledger.
      </div>
    );
  }

  const pct = Math.min(100, metrics.recovery_rate);

  return (
    <div className="space-y-6">
      {/* Signature element: the recovery ledger bar */}
      <div className="border border-ink-700 rounded-sm p-6 bg-ink-900">
        <div className="flex items-baseline justify-between mb-3">
          <span className="text-xs uppercase tracking-widest text-slate-400">Recovery Ledger</span>
          <span className="ledger-number text-signal-green text-sm">{metrics.recovery_rate}% recovered</span>
        </div>
        <div className="relative h-8 bg-ink-800 rounded-sm overflow-hidden border border-ink-700">
          <div
            className="absolute inset-y-0 left-0 bg-signal-green/80 transition-all duration-700"
            style={{ width: `${pct}%` }}
          />
          {/* ledger tick marks every 10% */}
          <div className="absolute inset-0 flex">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="flex-1 border-r border-ink-950/40 last:border-r-0" />
            ))}
          </div>
        </div>
        <div className="flex justify-between mt-2 text-xs text-slate-400 ledger-number">
          <span>$0</span>
          <span>{fmt(metrics.total_at_risk)} total at risk</span>
        </div>
      </div>

      {/* Metric strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Metric label="At Risk" value={fmt(metrics.total_at_risk)} tone="amber" />
        <Metric label="Recovered" value={fmt(metrics.total_recovered)} tone="green" />
        <Metric label="Escalated" value={String(metrics.escalated_count)} tone="slate" />
        <Metric label="Stopped (rules)" value={String(metrics.stopped_count)} tone="slate" />
      </div>

      {/* By root cause */}
      <div className="border border-ink-700 rounded-sm p-6 bg-ink-900">
        <span className="text-xs uppercase tracking-widest text-slate-400">Recovery by Root Cause</span>
        <div className="mt-4 space-y-2">
          {metrics.by_cause
            .sort((a, b) => b.recovered - a.recovered)
            .map((c) => (
              <div key={c.root_cause} className="flex items-center gap-3 text-sm">
                <span className="w-48 truncate text-slate-400">{c.root_cause}</span>
                <div className="flex-1 h-2 bg-ink-800 rounded-sm overflow-hidden">
                  <div
                    className="h-full bg-signal-amber/70"
                    style={{ width: `${Math.min(100, (c.recovered / (metrics.total_recovered || 1)) * 100)}%` }}
                  />
                </div>
                <span className="ledger-number w-24 text-right text-paper">{fmt(c.recovered)}</span>
                <span className="w-12 text-right text-slate-500 text-xs">n={c.count}</span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone: "amber" | "green" | "slate" }) {
  const toneClass =
    tone === "amber" ? "text-signal-amber" : tone === "green" ? "text-signal-green" : "text-paper";
  return (
    <div className="border border-ink-700 rounded-sm p-4 bg-ink-900">
      <div className="text-xs uppercase tracking-widest text-slate-400 mb-1">{label}</div>
      <div className={`ledger-number text-2xl font-semibold ${toneClass}`}>{value}</div>
    </div>
  );
}
