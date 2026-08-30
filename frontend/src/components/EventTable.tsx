import { EventRow } from "../api";

const STATUS_COLOR: Record<string, string> = {
  recovered: "text-signal-green",
  open: "text-signal-amber",
  in_progress: "text-signal-amber",
  stopped: "text-slate-500",
  escalated: "text-paper",
  opted_out: "text-slate-500",
};

function fmt(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD" });
}

export default function EventTable({ events }: { events: EventRow[] }) {
  return (
    <div className="border border-ink-700 rounded-sm bg-ink-900 overflow-hidden">
      <div className="px-6 py-4 border-b border-ink-700">
        <span className="text-xs uppercase tracking-widest text-slate-400">Event Ledger ({events.length})</span>
      </div>
      <div className="max-h-[520px] overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-ink-900 text-slate-400 text-xs uppercase tracking-wider">
            <tr>
              <th className="text-left font-medium px-6 py-2">Customer</th>
              <th className="text-left font-medium px-3 py-2">Type</th>
              <th className="text-right font-medium px-3 py-2">Amount</th>
              <th className="text-left font-medium px-3 py-2">Root Cause</th>
              <th className="text-left font-medium px-3 py-2">Status</th>
              <th className="text-right font-medium px-6 py-2">Attempts</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr key={e.id} className="border-t border-ink-800 hover:bg-ink-800/50">
                <td className="px-6 py-2 truncate max-w-[140px]">{e.customer_name}</td>
                <td className="px-3 py-2 text-slate-400">{e.event_type.replace(/_/g, " ")}</td>
                <td className="px-3 py-2 text-right ledger-number">{fmt(e.amount)}</td>
                <td className="px-3 py-2 text-slate-400">{e.root_cause ?? "—"}</td>
                <td className={`px-3 py-2 ${STATUS_COLOR[e.status] ?? "text-paper"}`}>{e.status}</td>
                <td className="px-6 py-2 text-right ledger-number text-slate-400">{e.contact_attempts}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
