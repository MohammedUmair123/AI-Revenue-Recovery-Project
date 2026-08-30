import { AuditRow } from "../api";

const STAGE_COLOR: Record<string, string> = {
  detect: "border-slate-500 text-slate-400",
  diagnose: "border-signal-amber text-signal-amber",
  decide: "border-paper text-paper",
  act: "border-signal-green text-signal-green",
  stop: "border-signal-red text-signal-red",
};

export default function AuditTrail({ logs }: { logs: AuditRow[] }) {
  return (
    <div className="border border-ink-700 rounded-sm bg-ink-900 overflow-hidden">
      <div className="px-6 py-4 border-b border-ink-700 flex items-center justify-between">
        <span className="text-xs uppercase tracking-widest text-slate-400">Audit Trail</span>
        <span className="text-xs text-slate-500">append-only · {logs.length} entries</span>
      </div>
      <div className="max-h-[520px] overflow-y-auto divide-y divide-ink-800">
        {logs.map((l) => (
          <div key={l.id} className="px-6 py-3 text-sm">
            <div className="flex items-center gap-2 mb-1">
              <span
                className={`text-[10px] uppercase tracking-wider border rounded-sm px-1.5 py-0.5 ${
                  STAGE_COLOR[l.stage] ?? "border-slate-500 text-slate-400"
                }`}
              >
                {l.stage}
              </span>
              <span className="text-slate-500 text-xs ledger-number">
                {new Date(l.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <p className="text-paper/90">{l.summary}</p>
          </div>
        ))}
        {logs.length === 0 && (
          <div className="px-6 py-8 text-center text-slate-500 text-sm">No audit entries yet.</div>
        )}
      </div>
    </div>
  );
}
