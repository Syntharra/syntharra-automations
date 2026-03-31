# Ad Decision Benchmarks — Syntharra Social Leads
# Used by Loop 4 (Ad Scale/Pause Engine) as Claude's decision framework
# Update these benchmarks as real data accumulates

---

## DECISION RULES

### Minimum Data Window
- **NEVER make a scale or pause decision before 3 days of running**
- Exception: if spend > $30 with 0 clicks and 0 impressions — pause immediately (ad delivery issue)

### SCALE Criteria (all must be true)
- Running >= 3 days
- CPC < $1.50
- CTR > 3%
- Landing page visits > 5
- Has NOT been scaled in the last 4 days (prevent runaway spend)
- Daily budget < $100 (hard ceiling — never auto-scale beyond $100/day without Dan's approval)

**Scale action:** Increase daily budget by 50% (e.g. $10 → $15 → $22.50 → $33.75)

### PAUSE Criteria (any one triggers pause)
- Running >= 3 days AND CPC > $3.00
- Running >= 3 days AND CTR < 1%
- Running >= 5 days AND 0 landing page visits
- Daily budget > $50 AND 0 bookings AND 0 attributed revenue (waste protection)

### HOLD Criteria (default — no action)
- Running < 3 days (regardless of metrics)
- Metrics are between good and bad thresholds
- Recently scaled (within 4 days) — let new budget settle

---

## BUDGET SAFETY CAPS

| Rule | Value |
|---|---|
| Max total active ad spend per day | $50 (Phase 2 start) |
| Max single ad daily budget (auto) | $100 |
| Max budget increase per scale action | 50% |
| Min days between scale actions on same ad | 4 days |
| Max auto-boosts per week | 3 posts |

When Dan wants to increase caps — update this file and push to GitHub.

---

## PERFORMANCE BENCHMARKS BY AUDIENCE TYPE

### Cold Audience (HVAC owners, USA, 35–55)
| Metric | Good | Acceptable | Bad |
|---|---|---|---|
| CPC | <$1.00 | $1.00–$2.00 | >$2.00 |
| CTR | >4% | 2–4% | <2% |
| CPM | <$15 | $15–$25 | >$25 |
| Landing page CVR | >5% | 2–5% | <2% |

### Warm Audience (video viewers 50%+)
| Metric | Good | Acceptable | Bad |
|---|---|---|---|
| CPC | <$0.75 | $0.75–$1.50 | >$1.50 |
| CTR | >6% | 3–6% | <3% |
| CPM | <$10 | $10–$20 | >$20 |

### Hot Audience (demo.html visitors)
| Metric | Good | Acceptable | Bad |
|---|---|---|---|
| CPC | <$0.50 | $0.50–$1.00 | >$1.00 |
| CTR | >8% | 4–8% | <4% |
| Booking rate | >10% | 5–10% | <5% |

---

## CLAUDE PROMPT CONTEXT FOR LOOP 4

When calling Claude in Loop 4, inject this as system context:

```
You are a performance marketing analyst for Syntharra, an AI receptionist 
company selling to HVAC business owners in the USA. 

Your job is to analyse Facebook ad performance and recommend SCALE, PAUSE, or HOLD 
for each active ad based on the benchmarks below.

Decision rules:
- NEVER recommend SCALE for ads running less than 3 days
- SCALE if: CPC < $1.50 AND CTR > 3% AND running >= 3 days
- PAUSE if: (CPC > $3.00 OR CTR < 1%) AND running >= 3 days
- PAUSE if: running >= 5 days AND landing_page_views = 0
- HOLD for everything else

Safety rules:
- Never recommend a budget that would exceed $100/day for any single ad
- If an ad was scaled in the last 4 days, recommend HOLD regardless of metrics

Return a JSON array. Each object must include:
{ad_id, recommendation, reasoning (one sentence), confidence_score (1-10)}
```

---

## WEEKLY BUDGET REVIEW (Manual, Every Sunday)

Dan should review:
1. Total spend for the week vs attributed bookings
2. Any ads that Claude scaled that performed worse after scaling
3. Any ads Claude held that Dan thinks should have been paused
4. Update benchmarks here if real-world data differs from assumptions

Update the benchmarks file and push to GitHub — Loop 4 uses these on next run.
