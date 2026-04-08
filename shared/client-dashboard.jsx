import { useState, useEffect, useCallback } from "react";

const SB_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co";
const SB_ANON =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhnaGV5cXducmN2d3RnbmdxZG5xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQyOTUzNTIsImV4cCI6MjA4OTg3MTM1Mn0.dDzlIEgPvV2KVZOpCBYGbHJ2_LZnXoL6KKmQrAwfyL0";

const N8N_PROXY = "https://n8n.syntharra.com/webhook/retell-calls";

// ─── colours (design tokens) ───────────────────────────────────────────────
const C = {
  violet: "#6C63FF",
  green: "#10B981",
  red: "#EF4444",
  grey: "#9CA3AF",
  blue: "#3B82F6",
  bg: "#F7F7FB",
  card: "#FFFFFF",
  border: "#E8E8F0",
  text: "#1A1A2E",
  muted: "#4A4A6A",
  label: "#9CA3AF",
};

// ─── mock data (6 calls) ─────────────────────────────────────────────────
const MOCK_CALLS = [
  {
    call_id: "mock_001",
    start_timestamp: Date.now() - 3600000,
    end_timestamp: Date.now() - 3460000,
    duration_ms: 140000,
    call_status: "ended",
    call_analysis: {
      call_summary:
        "Homeowner Mike called about AC unit not cooling — system running but not reaching set temp. Left callback details.",
      user_sentiment: "Positive",
    },
    transcript: [
      { role: "agent", content: "Thank you for calling, this is Sophie with Arctic Breeze HVAC. How can I help you today?" },
      { role: "user", content: "Hi, my AC is running but it's not cooling the house at all. It's 85 degrees in here." },
      { role: "agent", content: "I'm sorry to hear that, that's definitely uncomfortable. Can I get your name and address so a technician can call you back?" },
      { role: "user", content: "Sure, I'm Mike Johnson at 142 Oak Street." },
      { role: "agent", content: "Perfect, Mike. A technician will call you back within the hour. Is your current number the best to reach you?" },
      { role: "user", content: "Yes, this number works." },
    ],
    recording_url: null,
  },
  {
    call_id: "mock_002",
    start_timestamp: Date.now() - 86400000,
    end_timestamp: Date.now() - 86264000,
    duration_ms: 136000,
    call_status: "ended",
    call_analysis: {
      call_summary:
        "Emergency call — furnace completely out overnight. Customer has elderly parent at home. Flagged priority.",
      user_sentiment: "Negative",
    },
    transcript: [
      { role: "agent", content: "Thank you for calling Arctic Breeze HVAC. How can I help?" },
      { role: "user", content: "My furnace stopped working and it's freezing. My mom is 80 years old and I'm really worried." },
      { role: "agent", content: "I understand this is urgent. I'm flagging this as an emergency right now. A technician will call you back as soon as possible — typically within 30 minutes for emergencies. Can I confirm your address?" },
    ],
    recording_url: "https://example.com/recording_002.mp3",
  },
  {
    call_id: "mock_003",
    start_timestamp: Date.now() - 172800000,
    end_timestamp: null,
    duration_ms: null,
    call_status: "no_answer",
    call_analysis: { call_summary: null, user_sentiment: null },
    transcript: [],
    recording_url: null,
  },
  {
    call_id: "mock_004",
    start_timestamp: Date.now() - 259200000,
    end_timestamp: Date.now() - 259050000,
    duration_ms: 150000,
    call_status: "ended",
    call_analysis: {
      call_summary:
        "Annual maintenance inquiry — customer wants to schedule a tune-up before summer. Happy with previous service.",
      user_sentiment: "Positive",
    },
    transcript: [
      { role: "agent", content: "Thank you for calling Arctic Breeze HVAC. How can I help you today?" },
      { role: "user", content: "I'd like to schedule a maintenance check before summer hits. You guys serviced my unit last year and did a great job." },
      { role: "agent", content: "Wonderful, we'd love to help. A technician will reach out to schedule a time that works for you. Can I grab your name and number?" },
    ],
    recording_url: null,
  },
  {
    call_id: "mock_005",
    start_timestamp: Date.now() - 432000000,
    end_timestamp: Date.now() - 431820000,
    duration_ms: 180000,
    call_status: "ended",
    call_analysis: {
      call_summary:
        "Strange noise from HVAC unit — banging sound when starting up. Customer wants same-day inspection if possible.",
      user_sentiment: "Neutral",
    },
    transcript: [
      { role: "agent", content: "Arctic Breeze HVAC, how can I help?" },
      { role: "user", content: "My AC is making a really loud banging sound every time it kicks on. It's been going on for two days." },
      { role: "agent", content: "That definitely needs attention — banging sounds can indicate a loose component. I'll have a technician call you to arrange an inspection. What's the best number and address?" },
    ],
    recording_url: "https://example.com/recording_005.mp3",
  },
  {
    call_id: "mock_006",
    start_timestamp: Date.now() - 604800000,
    end_timestamp: Date.now() - 604710000,
    duration_ms: 90000,
    call_status: "ended",
    call_analysis: {
      call_summary:
        "Quick inquiry about service area — caller confirmed we cover their zip code and asked for a callback quote.",
      user_sentiment: "Neutral",
    },
    transcript: [
      { role: "agent", content: "Arctic Breeze HVAC, how can I help?" },
      { role: "user", content: "Do you service the 46205 area?" },
      { role: "agent", content: "Yes, we do cover that area. A technician will call you to discuss your needs. Can I get your name and number?" },
    ],
    recording_url: null,
  },
];

// ─── helpers ────────────────────────────────────────────────────────────────
const fmtDate = (ts) => {
  if (!ts) return "—";
  return new Date(ts).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
};

const fmtDuration = (ms) => {
  if (!ms) return "—";
  const s = Math.round(ms / 1000);
  return s >= 60 ? `${Math.floor(s / 60)}m ${s % 60}s` : `${s}s`;
};

const statusBadge = (call) => {
  const s = call.call_status;
  if (s === "no_answer" || s === "failed")
    return { label: "Missed", bg: "#F3F4F6", color: C.grey };
  if (s === "in_progress")
    return { label: "In Progress", bg: "#EFF6FF", color: C.blue };
  if (s === "error")
    return { label: "Error", bg: "#FEF2F2", color: C.red };
  const hasSummary = call.call_analysis?.call_summary;
  return hasSummary
    ? { label: "Lead Captured", bg: "#EDE9FE", color: C.violet }
    : { label: "Ended", bg: "#F3F4F6", color: C.grey };
};

const sentimentBadge = (sentiment) => {
  if (!sentiment) return null;
  const map = {
    Positive: { label: "Positive", bg: "#ECFDF5", color: C.green },
    Negative: { label: "Negative", bg: "#FEF2F2", color: C.red },
    Neutral: { label: "Neutral", bg: "#F3F4F6", color: C.grey },
  };
  return map[sentiment] || null;
};

const isLead = (call) => !!call.call_analysis?.call_summary;
const isMissed = (call) =>
  call.call_status === "no_answer" || call.call_status === "failed";

const filterCalls = (calls, tab, days) => {
  const cutoff = Date.now() - days * 86400000;
  let result = calls.filter((c) => (c.start_timestamp || 0) >= cutoff);
  if (tab === "leads") result = result.filter(isLead);
  if (tab === "missed") result = result.filter(isMissed);
  return result;
};

const avgDuration = (calls) => {
  const valid = calls.filter((c) => c.duration_ms);
  if (!valid.length) return "—";
  const ms = valid.reduce((s, c) => s + c.duration_ms, 0) / valid.length;
  return fmtDuration(ms);
};

// ─── sub-components ──────────────────────────────────────────────────────────
const Badge = ({ label, bg, color }) => (
  <span
    style={{
      display: "inline-block",
      padding: "2px 10px",
      borderRadius: 20,
      fontSize: 11,
      fontWeight: 700,
      background: bg,
      color,
      letterSpacing: 0.3,
    }}
  >
    {label}
  </span>
);

const StatCard = ({ label, value, accent }) => (
  <div
    style={{
      background: C.card,
      border: `1px solid ${C.border}`,
      borderRadius: 14,
      padding: "20px 22px",
      flex: 1,
      minWidth: 140,
    }}
  >
    <div
      style={{
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: 1.5,
        textTransform: "uppercase",
        color: C.label,
        marginBottom: 6,
      }}
    >
      {label}
    </div>
    <div
      style={{
        fontSize: 30,
        fontWeight: 800,
        color: accent || C.text,
        lineHeight: 1.1,
      }}
    >
      {value}
    </div>
  </div>
);

const SkeletonCard = () => (
  <div
    style={{
      background: C.card,
      border: `1px solid ${C.border}`,
      borderRadius: 14,
      padding: "20px 22px",
      flex: 1,
      minWidth: 140,
    }}
  >
    <div
      style={{
        height: 10,
        width: "60%",
        background: "#E8E8F0",
        borderRadius: 4,
        marginBottom: 10,
        animation: "pulse 1.5s ease-in-out infinite",
      }}
    />
    <div
      style={{
        height: 30,
        width: "40%",
        background: "#E8E8F0",
        borderRadius: 4,
        animation: "pulse 1.5s ease-in-out infinite",
      }}
    />
  </div>
);

const SkeletonRow = () => (
  <div
    style={{
      background: C.card,
      border: `1px solid ${C.border}`,
      borderRadius: 14,
      padding: "18px 20px",
      marginBottom: 8,
    }}
  >
    {[["70%"], ["50%"], ["40%"]].map(([w], i) => (
      <div
        key={i}
        style={{
          height: 10,
          width: w,
          background: "#E8E8F0",
          borderRadius: 4,
          marginBottom: i < 2 ? 10 : 0,
          animation: "pulse 1.5s ease-in-out infinite",
        }}
      />
    ))}
  </div>
);

// ─── transcript viewer ────────────────────────────────────────────────────────
const Transcript = ({ lines }) => {
  if (!lines || !lines.length)
    return (
      <p style={{ color: C.label, fontSize: 13, marginTop: 12 }}>
        No transcript available.
      </p>
    );
  return (
    <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 8 }}>
      {lines.map((l, i) => {
        const isAgent = l.role === "agent";
        return (
          <div
            key={i}
            style={{
              display: "flex",
              flexDirection: isAgent ? "row" : "row-reverse",
              gap: 8,
            }}
          >
            <div
              style={{
                fontSize: 10,
                fontWeight: 700,
                color: C.label,
                minWidth: 44,
                paddingTop: 4,
                textAlign: isAgent ? "left" : "right",
                textTransform: "uppercase",
                letterSpacing: 0.5,
              }}
            >
              {isAgent ? "Agent" : "Caller"}
            </div>
            <div
              style={{
                background: isAgent ? "#EDE9FE" : "#F3F4F6",
                color: isAgent ? "#3730A3" : C.text,
                borderRadius: 10,
                padding: "8px 12px",
                fontSize: 13,
                lineHeight: 1.55,
                maxWidth: "80%",
              }}
            >
              {l.content}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ─── call card ────────────────────────────────────────────────────────────────
const CallCard = ({ call, expanded, onToggle }) => {
  const sb = statusBadge(call);
  const sent = sentimentBadge(call.call_analysis?.user_sentiment);
  const summary = call.call_analysis?.call_summary;
  const truncSummary = summary && summary.length > 120 ? summary.slice(0, 117) + "…" : summary;

  return (
    <div
      style={{
        background: C.card,
        border: `1px solid ${C.border}`,
        borderRadius: 14,
        overflow: "hidden",
        marginBottom: 8,
        cursor: "pointer",
      }}
      onClick={onToggle}
    >
      {/* Row */}
      <div
        style={{
          padding: "16px 20px",
          display: "flex",
          alignItems: "center",
          gap: 16,
          flexWrap: "wrap",
        }}
      >
        <div style={{ flex: 1, minWidth: 180 }}>
          <div style={{ fontSize: 13, color: C.muted, marginBottom: 2 }}>
            {fmtDate(call.start_timestamp)}
            <span style={{ marginLeft: 10, color: C.label }}>
              {fmtDuration(call.duration_ms)}
            </span>
          </div>
          {truncSummary && (
            <div style={{ fontSize: 13, color: C.text, lineHeight: 1.45 }}>
              {truncSummary}
            </div>
          )}
        </div>
        <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
          <Badge {...sb} />
          {sent && <Badge {...sent} />}
        </div>
        <div
          style={{
            color: C.label,
            fontSize: 16,
            transition: "transform 0.2s",
            transform: expanded ? "rotate(180deg)" : "none",
            flexShrink: 0,
          }}
        >
          ▾
        </div>
      </div>

      {/* Expanded */}
      {expanded && (
        <div
          style={{
            borderTop: `1px solid ${C.border}`,
            padding: "16px 20px",
          }}
        >
          {call.recording_url && (
            <a
              href={call.recording_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              style={{
                display: "inline-block",
                marginBottom: 12,
                background: C.violet,
                color: "#fff",
                padding: "6px 14px",
                borderRadius: 8,
                fontSize: 12,
                fontWeight: 600,
                textDecoration: "none",
              }}
            >
              ▶ Play Recording
            </a>
          )}
          <Transcript lines={call.transcript} />
        </div>
      )}
    </div>
  );
};

// ─── main component ───────────────────────────────────────────────────────────
export default function ClientDashboard() {
  const params = new URLSearchParams(
    typeof window !== "undefined" ? window.location.search : ""
  );
  const agentId = params.get("a") || params.get("agent_id");

  const [calls, setCalls] = useState([]);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mockBanner, setMockBanner] = useState(false);
  const [tab, setTab] = useState("all");
  const [days, setDays] = useState(30);
  const [expanded, setExpanded] = useState(null);

  const load = useCallback(async () => {
    if (!agentId) return;
    setLoading(true);
    setMockBanner(false);

    // Fetch company info from Supabase
    try {
      const r = await fetch(
        `${SB_URL}/rest/v1/hvac_standard_agent?agent_id=eq.${agentId}&select=company_name,agent_name,service_area`,
        { headers: { apikey: SB_ANON, Authorization: `Bearer ${SB_ANON}` } }
      );
      const data = await r.json();
      setCompany(Array.isArray(data) && data[0] ? data[0] : null);
    } catch (_) {
      // non-fatal
    }

    // Fetch calls via n8n proxy
    try {
      const r = await fetch(N8N_PROXY, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: agentId }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const list = Array.isArray(data) ? data : data.calls || [];
      setCalls(list);
    } catch (_) {
      setCalls(MOCK_CALLS);
      setMockBanner(true);
    }

    setLoading(false);
  }, [agentId]);

  useEffect(() => {
    load();
  }, [load]);

  // ── no agent_id ──
  if (!agentId) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: C.bg,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "Inter, system-ui, sans-serif",
        }}
      >
        <div style={{ textAlign: "center", padding: 40, maxWidth: 420 }}>
          <h2 style={{ color: C.text, fontWeight: 700, marginBottom: 8 }}>
            Dashboard unavailable
          </h2>
          <p style={{ color: C.muted, fontSize: 14, lineHeight: 1.6 }}>
            Missing agent ID. Contact{" "}
            <a href="mailto:support@syntharra.com" style={{ color: C.violet }}>
              support@syntharra.com
            </a>
          </p>
        </div>
      </div>
    );
  }

  const filtered = filterCalls(calls, tab, days);
  const allPeriod = filterCalls(calls, "all", days);
  const totalCalls = allPeriod.length;
  const leads = allPeriod.filter(isLead).length;
  const missed = allPeriod.filter(isMissed).length;
  const avgDur = avgDuration(allPeriod);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: C.bg,
        fontFamily: "Inter, system-ui, sans-serif",
        overflowX: "clip",
      }}
    >
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        @media (max-width: 768px) {
          .stats-row { flex-direction: column !important; }
          .filter-bar { flex-direction: column !important; gap: 8px !important; }
        }
      `}</style>

      {/* Header */}
      <div
        style={{
          background: C.card,
          borderBottom: `1px solid ${C.border}`,
          padding: "16px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <svg xmlns="http://www.w3.org/2000/svg" width="130" height="28" viewBox="0 0 158 34" role="img">
            <g fill={C.violet}>
              <rect x="0" y="21" width="4" height="9" rx="1" />
              <rect x="7" y="17" width="4" height="13" rx="1" />
              <rect x="14" y="13" width="4" height="17" rx="1" />
              <rect x="21" y="9" width="4" height="21" rx="1" />
            </g>
            <text x="37" y="21" fontFamily="Inter,Arial,sans-serif" fontWeight="700" fontSize="16" fill={C.text} letterSpacing="-0.48">Syntharra</text>
            <text x="37" y="32" fontFamily="Inter,Arial,sans-serif" fontWeight="500" fontSize="8" fill={C.violet} letterSpacing="1.2">GLOBAL AI SOLUTIONS</text>
          </svg>
          {company && (
            <>
              <div style={{ width: 1, height: 28, background: C.border }} />
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, color: C.text }}>
                  {company.company_name}
                </div>
                {company.agent_name && (
                  <div style={{ fontSize: 12, color: C.muted }}>
                    {company.agent_name}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Mock data banner */}
      {mockBanner && (
        <div
          style={{
            background: "#FFFBEB",
            borderBottom: "1px solid #FDE68A",
            padding: "10px 24px",
            fontSize: 13,
            color: "#92400E",
          }}
        >
          ⚠️ Connecting to live call data — if this persists contact{" "}
          <a href="mailto:support@syntharra.com" style={{ color: "#92400E", fontWeight: 600 }}>
            support@syntharra.com
          </a>
        </div>
      )}

      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 16px 48px" }}>

        {/* Stats row */}
        {loading ? (
          <div className="stats-row" style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
            {[1, 2, 3, 4].map((i) => <SkeletonCard key={i} />)}
          </div>
        ) : (
          <div className="stats-row" style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
            <StatCard label="Total Calls" value={totalCalls} />
            <StatCard label="Leads Captured" value={leads} accent={C.violet} />
            <StatCard label="Missed Calls" value={missed} accent={missed > 0 ? C.red : C.grey} />
            <StatCard label="Avg Duration" value={avgDur} />
          </div>
        )}

        {/* Filter bar */}
        <div
          className="filter-bar"
          style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16, flexWrap: "wrap" }}
        >
          {["all", "leads", "missed"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                background: tab === t ? C.violet : C.card,
                color: tab === t ? "#fff" : C.muted,
                border: `1px solid ${tab === t ? C.violet : C.border}`,
                borderRadius: 10,
                padding: "7px 16px",
                fontSize: 13,
                fontWeight: 600,
                cursor: "pointer",
                textTransform: "capitalize",
              }}
            >
              {t === "all" ? "All" : t === "leads" ? "Leads" : "Missed"}
            </button>
          ))}
          <div style={{ marginLeft: "auto" }}>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              style={{
                border: `1px solid ${C.border}`,
                borderRadius: 10,
                padding: "7px 12px",
                fontSize: 13,
                color: C.muted,
                background: C.card,
                cursor: "pointer",
              }}
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
        </div>

        {/* Call list */}
        {loading ? (
          [1, 2, 3].map((i) => <SkeletonRow key={i} />)
        ) : filtered.length === 0 ? (
          <div
            style={{
              background: C.card,
              border: `1px solid ${C.border}`,
              borderRadius: 14,
              textAlign: "center",
              padding: "56px 24px",
              color: C.label,
            }}
          >
            <div style={{ fontSize: 32, marginBottom: 12 }}>📭</div>
            <p style={{ fontWeight: 600, color: C.muted, marginBottom: 4 }}>
              No calls yet — your AI receptionist is ready.
            </p>
            <p style={{ fontSize: 13 }}>Share your number to start receiving calls.</p>
          </div>
        ) : (
          filtered.map((call) => (
            <CallCard
              key={call.call_id}
              call={call}
              expanded={expanded === call.call_id}
              onToggle={() =>
                setExpanded(expanded === call.call_id ? null : call.call_id)
              }
            />
          ))
        )}

        {/* Footer */}
        <div style={{ textAlign: "center", marginTop: 40, color: C.label, fontSize: 12 }}>
          <div style={{ fontWeight: 700, letterSpacing: 2, color: C.violet, marginBottom: 4 }}>
            SYNTHARRA
          </div>
          AI Receptionist ·{" "}
          <a href="mailto:support@syntharra.com" style={{ color: C.label }}>
            support@syntharra.com
          </a>
        </div>
      </div>
    </div>
  );
}
