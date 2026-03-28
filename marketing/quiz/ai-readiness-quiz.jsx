import { useState } from "react";

const questions = [
  {
    q: "How many inbound calls does your business get per week?",
    options: [
      { text: "Less than 10", score: 5 },
      { text: "10 — 25", score: 15 },
      { text: "25 — 50", score: 20 },
      { text: "50+", score: 20 },
    ],
  },
  {
    q: "What percentage of calls do you think you miss?",
    options: [
      { text: "Almost none — we answer everything", score: 5 },
      { text: "Maybe 10 — 20%", score: 10 },
      { text: "Probably 30 — 40%", score: 18 },
      { text: "Honestly, no idea", score: 15 },
    ],
  },
  {
    q: "What happens when you miss a call?",
    options: [
      { text: "They leave a voicemail and we call back", score: 8 },
      { text: "Some leave voicemails, most don't", score: 15 },
      { text: "We just lose them", score: 20 },
      { text: "We have a receptionist but not 24/7", score: 12 },
    ],
  },
  {
    q: "How do you currently handle after-hours calls?",
    options: [
      { text: "We have someone answering 24/7", score: 5 },
      { text: "Voicemail", score: 15 },
      { text: "They go unanswered", score: 20 },
      { text: "Answering service (outsourced)", score: 10 },
    ],
  },
  {
    q: "What's the average value of a job for your business?",
    options: [
      { text: "Under $150", score: 8 },
      { text: "$150 — $350", score: 15 },
      { text: "$350 — $750", score: 18 },
      { text: "$750+", score: 20 },
    ],
  },
];

function getScoreData(score) {
  if (score >= 75) return { label: "High Potential", color: "#10B981", bg: "#ECFDF5", explanation: "Your business has significant call volume and is likely losing substantial revenue to missed calls. An AI receptionist would have an immediate, measurable impact on your bottom line." };
  if (score >= 50) return { label: "Strong Candidate", color: "#6C63FF", bg: "#F0EEFF", explanation: "You're missing enough calls to feel the impact, and the value of each missed call makes this a clear ROI-positive investment. An AI receptionist would pay for itself within the first month." };
  if (score >= 30) return { label: "Good Fit", color: "#F59E0B", bg: "#FEF3C7", explanation: "While your call volume might be moderate, there's still real revenue being lost. An AI receptionist ensures you never miss an opportunity, especially after hours and on weekends." };
  return { label: "Room to Grow", color: "#6B7280", bg: "#F3F4F6", explanation: "Your current setup handles calls reasonably well, but there's always room to improve. As your business grows, an AI receptionist will become increasingly valuable." };
}

export default function AIReadinessQuiz() {
  const [currentQ, setCurrentQ] = useState(0);
  const [totalScore, setTotalScore] = useState(0);
  const [phase, setPhase] = useState("quiz");
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const progress = phase === "quiz" ? Math.round((currentQ / questions.length) * 100) : phase === "email" ? 90 : 100;

  function selectAnswer(idx) {
    const q = questions[currentQ];
    const newScore = totalScore + q.options[idx].score;
    setTotalScore(newScore);
    if (currentQ + 1 < questions.length) {
      setCurrentQ(currentQ + 1);
    } else {
      setPhase("email");
    }
  }

  function submitEmail() {
    if (!email || !email.includes("@")) {
      setEmailError(true);
      return;
    }
    setSubmitting(true);
    setTimeout(() => setPhase("results"), 800);
  }

  const scoreData = getScoreData(totalScore);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Accent bar */}
        <div className="h-1" style={{ background: "linear-gradient(90deg, #6C63FF, #8B7FFF)" }} />

        {/* Header */}
        <div className="px-8 pt-7">
          <p className="text-xs font-bold tracking-widest uppercase" style={{ color: "#6C63FF" }}>
            Free Assessment
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-1" style={{ fontFamily: "Georgia, serif" }}>
            {phase === "quiz" && "How AI-Ready is Your Business?"}
            {phase === "email" && "Your score is ready"}
            {phase === "results" && "Your AI Readiness Score"}
          </h2>
          {phase === "quiz" && (
            <p className="text-sm text-gray-500 mt-2">Answer 5 quick questions to get your personalised score and free report.</p>
          )}
          {phase === "email" && (
            <p className="text-sm text-gray-500 mt-2">Enter your email to reveal your score and get your personalised report.</p>
          )}
        </div>

        {/* Progress */}
        <div className="px-8 pt-4">
          <div className="flex justify-between text-xs font-semibold mb-1">
            <span className="text-gray-500">
              {phase === "quiz" ? `Question ${currentQ + 1} of ${questions.length}` : phase === "email" ? "Almost done!" : "Complete!"}
            </span>
            <span style={{ color: "#6C63FF" }}>{progress}%</span>
          </div>
          <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${progress}%`, background: "linear-gradient(90deg, #6C63FF, #00D4FF)" }}
            />
          </div>
        </div>

        {/* Body */}
        <div className="px-8 py-6">
          {/* Quiz Phase */}
          {phase === "quiz" && (
            <div>
              <p className="text-base font-semibold text-gray-900 mb-5 leading-snug">{questions[currentQ].q}</p>
              <div className="space-y-3">
                {questions[currentQ].options.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => selectAnswer(i)}
                    className="w-full text-left px-4 py-3.5 border-2 border-gray-200 rounded-xl text-sm text-gray-900 transition-all duration-150 hover:border-purple-400 hover:bg-purple-50 active:scale-98"
                  >
                    {opt.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Email Phase */}
          {phase === "email" && (
            <div>
              <div className="text-center mb-5">
                <div
                  className="inline-flex items-center justify-center w-20 h-20 rounded-full"
                  style={{ background: "linear-gradient(135deg, #6C63FF, #8B7FFF)" }}
                >
                  <span className="text-3xl font-bold text-white">?</span>
                </div>
                <p className="text-sm text-gray-500 mt-2">Your score has been calculated.</p>
              </div>
              <input
                type="email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setEmailError(false); }}
                placeholder="your@email.com"
                className="w-full px-4 py-3.5 border-2 rounded-xl text-base outline-none transition-colors"
                style={{ borderColor: emailError ? "#EF4444" : "#E5E7EB", fontFamily: "inherit" }}
                onFocus={(e) => (e.target.style.borderColor = "#6C63FF")}
                onBlur={(e) => (e.target.style.borderColor = emailError ? "#EF4444" : "#E5E7EB")}
              />
              <button
                onClick={submitEmail}
                disabled={submitting}
                className="w-full mt-3 py-4 rounded-xl text-base font-bold text-white transition-transform hover:-translate-y-0.5"
                style={{ background: "#6C63FF", opacity: submitting ? 0.7 : 1, boxShadow: "0 4px 14px rgba(108,99,255,0.35)" }}
              >
                {submitting ? "Calculating..." : "Get My AI Readiness Score"}
              </button>
              <p className="text-center text-xs text-gray-400 mt-3">No spam. Unsubscribe anytime.</p>
            </div>
          )}

          {/* Results Phase */}
          {phase === "results" && (
            <div>
              <div className="text-center mb-6">
                <div
                  className="inline-flex items-center justify-center w-24 h-24 rounded-full border-4"
                  style={{ borderColor: scoreData.color, background: scoreData.bg }}
                >
                  <span className="text-4xl font-bold" style={{ color: scoreData.color }}>{totalScore}</span>
                </div>
                <p className="text-lg font-bold text-gray-900 mt-3">{scoreData.label}</p>
                <p className="text-xs text-gray-500">out of 100</p>
              </div>

              <div className="bg-gray-50 rounded-xl p-4 mb-5">
                <p className="text-sm text-gray-700 leading-relaxed">{scoreData.explanation}</p>
              </div>

              <div className="rounded-xl p-4 mb-5 text-center" style={{ background: "#F0EEFF" }}>
                <p className="text-xs text-gray-500 mb-1">Full report sent to</p>
                <p className="text-sm font-semibold text-gray-900">{email}</p>
              </div>

              <a
                href="https://calendar.app.google/jxUu7XfiMXMqvdiw6"
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full py-4 rounded-xl text-base font-bold text-white text-center no-underline transition-transform hover:-translate-y-0.5"
                style={{ background: "#6C63FF", boxShadow: "0 4px 14px rgba(108,99,255,0.35)" }}
              >
                Book a Free Demo Call
              </a>
              <p className="text-center mt-3">
                <a href="https://syntharra-checkout-production.up.railway.app/" target="_blank" rel="noopener noreferrer" className="text-sm font-semibold no-underline" style={{ color: "#6C63FF" }}>
                  Or view pricing →
                </a>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
