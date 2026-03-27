import { useState, useEffect, useCallback } from "react";

const SB_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co";
const SB_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyOTUzNTIsImV4cCI6MjA4OTg3MTM1Mn0.dDzlIEgPvV2KVZOpCBYGbHJ2_LZnXoL6KKmQrAwfyL0";

const fetchSB = async (path) => {
  const r = await fetch(`${SB_URL}/rest/v1/${path}`, {
    headers: { apikey: SB_ANON, Authorization: `Bearer ${SB_ANON}` },
  });
  return r.json();
};

const fmtDate = (iso) => {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit", hour12: true });
};

const fmtDuration = (s) => {
  if (!s) return "—";
  return s >= 60 ? `${Math.floor(s / 60)}m ${s % 60}s` : `${s}s`;
};

const ScoreBadge = ({ score }) => {
  const bg = score >= 8 ? "#fef2f2" : score >= 6 ? "#fffbeb" : "#f1f5f9";
  const color = score >= 8 ? "#dc2626" : score >= 6 ? "#d97706" : "#64748b";
  const border = score >= 8 ? "#fecaca" : score >= 6 ? "#fde68a" : "#e2e8f0";
  return (
    <span style={{ background: bg, color, border: `2px solid ${border}`, borderRadius: 20, padding: "2px 10px", fontWeight: 700, fontSize: 13 }}>
      {score}/10
    </span>
  );
};

const TierBadge = ({ tier }) => {
  const map = {
    Emergency: { bg: "#dc2626", label: "🚨 Emergency" },
    Urgent: { bg: "#d97706", label: "⚡ Urgent" },
    Standard: { bg: "#6C63FF", label: "Standard" },
  };
  const t = map[tier] || map.Standard;
  return (
    <span style={{ background: t.bg, color: "#fff", padding: "3px 10px", borderRadius: 14, fontSize: 11, fontWeight: 700, letterSpacing: 0.5 }}>
      {t.label}
    </span>
  );
};

const StatCard = ({ label, value, accent, sub }) => (
  <div style={{ background: "#fff", borderRadius: 14, padding: "20px 22px", border: "1px solid #f0eeff", flex: 1, minWidth: 140 }}>
    <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: 1.5, textTransform: "uppercase", color: "#9ca3af", marginBottom: 6 }}>{label}</div>
    <div style={{ fontSize: 32, fontWeight: 800, color: accent || "#111827", lineHeight: 1.1 }}>{value}</div>
    {sub && <div style={{ fontSize: 12, color: "#9ca3af", marginTop: 4 }}>{sub}</div>}
  </div>
);

export default function Dashboard() {
  const [calls, setCalls] = useState([]);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [expanded, setExpanded] = useState(null);
  const [range, setRange] = useState("7");
  const [error, setError] = useState(null);

  const params = new URLSearchParams(window.location.search);
  const agentId = params.get("agent_id") || params.get("a");

  const load = useCallback(async () => {
    if (!agentId) { setError("No agent_id in URL"); setLoading(false); return; }
    setLoading(true);
    try {
      const days = parseInt(range);
      const since = new Date(Date.now() - days * 86400000).toISOString();
      const [callData, agentData] = await Promise.all([
        fetchSB(`hvac_call_log?agent_id=eq.${agentId}&call_timestamp=gte.${since}&select=*&order=call_timestamp.desc`),
        fetchSB(`hvac_standard_agent?agent_id=eq.${agentId}&select=company_name,agent_name,service_area,lead_email,lead_phone`),
      ]);
      setCalls(Array.isArray(callData) ? callData : []);
      setCompany(Array.isArray(agentData) && agentData[0] ? agentData[0] : null);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  }, [agentId, range]);

  useEffect(() => { load(); }, [load]);

  if (error) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#f8f7ff", fontFamily: "'DM Sans', sans-serif" }}>
        <div style={{ textAlign: "center", padding: 40 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🔒</div>
          <h2 style={{ margin: "0 0 8px", color: "#111827", fontSize: 22, fontWeight: 700 }}>Dashboard Access</h2>
          <p style={{ color: "#6b7280", fontSize: 14 }}>Add your agent ID to the URL: <code style={{ background: "#f3f0ff", padding: "2px 8px", borderRadius: 6, color: "#6C63FF" }}>?agent_id=your_id</code></p>
        </div>
      </div>
    );
  }

  const filtered = filter === "all" ? calls : filter === "leads" ? calls.filter((c) => c.is_lead) : filter === "emergency" ? calls.filter((c) => c.call_tier === "Emergency") : filter === "missed" ? calls.filter((c) => c.transfer_attempted && !c.transfer_success) : calls;

  const totalCalls = calls.length;
  const totalLeads = calls.filter((c) => c.is_lead).length;
  const hotLeads = calls.filter((c) => c.lead_score >= 8).length;
  const emergencies = calls.filter((c) => c.call_tier === "Emergency").length;
  const missedTransfers = calls.filter((c) => c.transfer_attempted && !c.transfer_success).length;
  const avgScore = totalCalls > 0 ? (calls.reduce((s, c) => s + (c.lead_score || 0), 0) / totalCalls).toFixed(1) : "—";
  const totalMinutes = Math.round(calls.reduce((s, c) => s + (c.duration_seconds || 0), 0) / 60);

  return (
    <>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Serif+Display&display=swap" rel="stylesheet" />
      <div style={{ minHeight: "100vh", background: "#f8f7ff", fontFamily: "'DM Sans', sans-serif", padding: 0 }}>
        {/* Header */}
        <div style={{ background: "linear-gradient(135deg, #6C63FF 0%, #4F46E5 50%, #3730A3 100%)", padding: "28px 32px 24px", color: "#fff" }}>
          <div style={{ maxWidth: 1100, margin: "0 auto" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
              <div>
                <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 3, textTransform: "uppercase", opacity: 0.6, marginBottom: 4 }}>SYNTHARRA</div>
                <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800, fontFamily: "'DM Serif Display', serif" }}>
                  {company?.company_name || "Call Dashboard"}
                </h1>
                {company?.service_area && <div style={{ fontSize: 13, opacity: 0.7, marginTop: 2 }}>{company.service_area}</div>}
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                {["7", "14", "30"].map((d) => (
                  <button key={d} onClick={() => setRange(d)} style={{ background: range === d ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.2)", borderRadius: 8, padding: "6px 14px", color: "#fff", fontSize: 12, fontWeight: 600, cursor: "pointer", transition: "all 0.2s" }}>
                    {d}d
                  </button>
                ))}
                <button onClick={load} style={{ background: "rgba(255,255,255,0.12)", border: "1px solid rgba(255,255,255,0.2)", borderRadius: 8, padding: "6px 12px", color: "#fff", fontSize: 14, cursor: "pointer" }}>
                  ↻
                </button>
              </div>
            </div>
          </div>
        </div>

        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 16px 40px" }}>
          {/* Stats Row */}
          <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
            <StatCard label="Total Calls" value={totalCalls} sub={`${totalMinutes} min total`} />
            <StatCard label="Leads Captured" value={totalLeads} accent="#16a34a" sub={`${hotLeads} hot leads`} />
            <StatCard label="Avg Score" value={avgScore} accent="#6C63FF" />
            <StatCard label="Emergencies" value={emergencies} accent="#dc2626" />
            {missedTransfers > 0 && <StatCard label="Missed Transfers" value={missedTransfers} accent="#d97706" sub="Callback needed" />}
          </div>

          {/* Filters */}
          <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
            {[
              { key: "all", label: "All Calls", count: totalCalls },
              { key: "leads", label: "Leads", count: totalLeads },
              { key: "emergency", label: "Emergency", count: emergencies },
              ...(missedTransfers > 0 ? [{ key: "missed", label: "Missed Transfers", count: missedTransfers }] : []),
            ].map((f) => (
              <button key={f.key} onClick={() => setFilter(f.key)} style={{ background: filter === f.key ? "#6C63FF" : "#fff", color: filter === f.key ? "#fff" : "#6b7280", border: filter === f.key ? "none" : "1px solid #e5e7eb", borderRadius: 10, padding: "8px 16px", fontSize: 13, fontWeight: 600, cursor: "pointer", transition: "all 0.2s" }}>
                {f.label} <span style={{ opacity: 0.6, marginLeft: 4 }}>({f.count})</span>
              </button>
            ))}
          </div>

          {/* Call List */}
          {loading ? (
            <div style={{ textAlign: "center", padding: 60, color: "#9ca3af" }}>
              <div style={{ fontSize: 28, marginBottom: 8 }}>⏳</div>
              Loading calls...
            </div>
          ) : filtered.length === 0 ? (
            <div style={{ textAlign: "center", padding: 60, color: "#9ca3af", background: "#fff", borderRadius: 14, border: "1px solid #f0eeff" }}>
              <div style={{ fontSize: 36, marginBottom: 8 }}>📭</div>
              <p style={{ margin: 0, fontWeight: 600 }}>No calls in this period</p>
              <p style={{ margin: "4px 0 0", fontSize: 13 }}>Try expanding the date range</p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {filtered.map((call, i) => {
                const isOpen = expanded === call.call_id;
                const isMissedTransfer = call.transfer_attempted && !call.transfer_success;
                const borderColor = call.call_tier === "Emergency" ? "#fecaca" : isMissedTransfer ? "#fde68a" : "#f0eeff";

                return (
                  <div key={call.call_id || i} onClick={() => setExpanded(isOpen ? null : call.call_id)} style={{ background: "#fff", borderRadius: 12, border: `1px solid ${borderColor}`, cursor: "pointer", transition: "all 0.2s", overflow: "hidden" }}>
                    {/* Row */}
                    <div style={{ padding: "14px 18px", display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
                      <div style={{ width: 36, height: 36, borderRadius: 10, background: call.is_lead ? "#f0fdf4" : "#f8f7ff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, flexShrink: 0 }}>
                        {call.call_tier === "Emergency" ? "🚨" : isMissedTransfer ? "📵" : call.is_lead ? "📞" : "📋"}
                      </div>
                      <div style={{ flex: 1, minWidth: 160 }}>
                        <div style={{ fontSize: 14, fontWeight: 700, color: "#111827" }}>{call.caller_name || "Unknown Caller"}</div>
                        <div style={{ fontSize: 12, color: "#9ca3af" }}>
                          {call.service_requested || "General"} · {fmtDuration(call.duration_seconds)} · {fmtDate(call.call_timestamp)}
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                        <TierBadge tier={call.call_tier} />
                        {call.lead_score > 0 && <ScoreBadge score={call.lead_score} />}
                        {isMissedTransfer && <span style={{ background: "#fffbeb", color: "#d97706", border: "1px solid #fde68a", borderRadius: 14, padding: "2px 8px", fontSize: 11, fontWeight: 700 }}>📵 Missed</span>}
                      </div>
                      <div style={{ color: "#c4b5fd", fontSize: 18, transition: "transform 0.2s", transform: isOpen ? "rotate(180deg)" : "rotate(0deg)" }}>▾</div>
                    </div>

                    {/* Expanded Detail */}
                    {isOpen && (
                      <div style={{ padding: "0 18px 18px", borderTop: "1px solid #f3f0ff" }}>
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 14, padding: "14px 0" }}>
                          <div>
                            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", color: "#9ca3af", marginBottom: 3 }}>Phone</div>
                            <a href={`tel:${call.caller_phone || call.from_number}`} style={{ fontSize: 14, fontWeight: 600, color: "#6C63FF", textDecoration: "none" }}>{call.caller_phone || call.from_number || "—"}</a>
                          </div>
                          <div>
                            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", color: "#9ca3af", marginBottom: 3 }}>Address</div>
                            <div style={{ fontSize: 14, color: "#374151" }}>{call.caller_address || "Not provided"}</div>
                          </div>
                          <div>
                            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", color: "#9ca3af", marginBottom: 3 }}>Property Type</div>
                            <div style={{ fontSize: 14, color: "#374151" }}>{call.job_type || "Residential"}</div>
                          </div>
                          <div>
                            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", color: "#9ca3af", marginBottom: 3 }}>Urgency</div>
                            <div style={{ fontSize: 14, color: "#374151" }}>{call.urgency || "Medium"}</div>
                          </div>
                        </div>
                        {call.summary && (
                          <div style={{ background: "#f8f7ff", borderRadius: 10, padding: "12px 16px", marginTop: 4 }}>
                            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", color: "#9ca3af", marginBottom: 6 }}>Summary</div>
                            <div style={{ fontSize: 13, color: "#374151", lineHeight: 1.6 }}>{call.summary}</div>
                          </div>
                        )}
                        {call.notes && (
                          <div style={{ background: "#fffbeb", borderRadius: 10, padding: "10px 14px", marginTop: 8, fontSize: 12, color: "#92400e", borderLeft: "3px solid #f59e0b" }}>
                            <strong>Note:</strong> {call.notes}
                          </div>
                        )}
                        {isMissedTransfer && (
                          <div style={{ background: "#fef2f2", borderRadius: 10, padding: "10px 14px", marginTop: 8, fontSize: 12, color: "#991b1b", borderLeft: "3px solid #dc2626" }}>
                            <strong>📵 Transfer Failed</strong> — This caller was unable to be connected and is expecting a callback.
                          </div>
                        )}
                        {call.geocode_formatted && (
                          <div style={{ marginTop: 8 }}>
                            <a href={`https://maps.google.com/?q=${encodeURIComponent(call.geocode_formatted)}`} target="_blank" rel="noopener noreferrer" style={{ fontSize: 12, color: "#6C63FF", fontWeight: 600, textDecoration: "none" }}>
                              📍 View on Google Maps
                            </a>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Footer */}
          <div style={{ textAlign: "center", marginTop: 32, padding: "16px 0" }}>
            <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 3, color: "#6C63FF" }}>SYNTHARRA</div>
            <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 2 }}>AI Receptionist · syntharra.com</div>
          </div>
        </div>
      </div>
    </>
  );
}
