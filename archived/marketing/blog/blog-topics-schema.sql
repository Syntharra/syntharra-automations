-- ============================================================
-- Syntharra Blog Auto-Publisher — Topic Queue
-- Run this in Supabase SQL Editor
-- ============================================================

CREATE TABLE IF NOT EXISTS blog_topics (
  id            SERIAL PRIMARY KEY,
  slug          TEXT UNIQUE NOT NULL,          -- e.g. "hvac-after-hours-calls"
  title         TEXT NOT NULL,                 -- Full article title
  tag           TEXT NOT NULL,                 -- Display tag: HVAC | Plumbing | Electrical | AI | Operations | Growth
  hero_emoji    TEXT NOT NULL,                 -- Single emoji for hero background
  hero_gradient TEXT NOT NULL,                 -- CSS gradient string
  target_keyword TEXT NOT NULL,               -- Primary SEO keyword
  brief         TEXT NOT NULL,                 -- 1-2 sentence brief for Claude prompt
  status        TEXT NOT NULL DEFAULT 'queued', -- queued | published | skipped
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  published_at  TIMESTAMPTZ
);

-- ============================================================
-- SEED: 40 topic queue
-- ============================================================

INSERT INTO blog_topics (slug, title, tag, hero_emoji, hero_gradient, target_keyword, brief) VALUES

-- HVAC
('hvac-after-hours-answering', 'Why HVAC companies lose 40% of their revenue after 5PM', 'HVAC', '🌙', 'linear-gradient(135deg,#1a0a0a,#3d0f0f)', 'hvac after hours answering service', 'Most HVAC revenue is lost outside business hours. Cover the data on after-hours call volumes, what happens when calls go to voicemail, and how AI solves it.'),
('hvac-dispatcher-guide', 'The modern HVAC dispatcher: why the role is changing fast', 'HVAC', '📡', 'linear-gradient(135deg,#1a0a0a,#3d0f0f)', 'hvac dispatcher software', 'Explain how the dispatcher role in HVAC is evolving with AI tools, what modern dispatching looks like, and why contractors who adapt win more jobs.'),
('hvac-emergency-response-time', 'Response time is everything in HVAC — here''s the data', 'HVAC', '⏱️', 'linear-gradient(135deg,#1a0a0a,#3d0f0f)', 'hvac emergency response time', 'Deep dive into why speed-to-answer determines who gets the job in HVAC emergencies, with stats on how quickly customers move on to competitors.'),
('hvac-weekend-calls', 'Weekend HVAC calls: the goldmine most contractors ignore', 'HVAC', '📅', 'linear-gradient(135deg,#1a0a0a,#3d0f0f)', 'hvac weekend calls', 'Weekend breakdowns are high-value, high-urgency leads. Cover why most HVAC businesses miss weekend calls and how capturing them changes profitability.'),
('hvac-summer-peak-preparation', 'How to prepare your HVAC business for the summer call surge', 'HVAC', '☀️', 'linear-gradient(135deg,#1a0a0a,#3d0f0f)', 'hvac summer preparation', 'Practical guide to preparing an HVAC operation for the summer peak season, covering staffing, systems, and call handling automation.'),
('hvac-customer-callbacks', 'Why HVAC customers don''t call back — and what to do about it', 'HVAC', '📵', 'linear-gradient(135deg,#1a0a0a,#3d0f0f)', 'hvac customer callbacks', 'When HVAC businesses miss a call and try to call back, most customers have already moved on. Explain the psychology and how to fix it at the source.'),
('hvac-repeat-customers', 'How to turn a one-time HVAC call into a lifetime customer', 'HVAC', '🔄', 'linear-gradient(135deg,#1a0a0a,#3d0f0f)', 'hvac repeat customers', 'Retention strategies for HVAC businesses: follow-up timing, maintenance reminders, and how AI receptionists create the first impression that drives return calls.'),

-- Plumbing
('plumbing-emergency-calls', 'Plumbing emergencies don''t wait — why your phone can''t either', 'Plumbing', '🚿', 'linear-gradient(135deg,#001a2e,#003a5e)', 'plumbing emergency answering service', 'Plumbing emergencies are immediate-need calls. Cover the data on how fast plumbing customers make decisions and what happens when no one answers.'),
('plumbing-after-hours', 'After-hours plumbing calls: the highest-value leads you''re missing', 'Plumbing', '🌙', 'linear-gradient(135deg,#001a2e,#003a5e)', 'plumbing after hours service', 'After-hours plumbing calls tend to be high-urgency and high-value. Explain why they''re the easiest wins to capture and hardest to handle manually.'),
('plumbing-lead-response', 'The 5-minute rule for plumbing leads (and why most contractors fail it)', 'Plumbing', '⚡', 'linear-gradient(135deg,#001a2e,#003a5e)', 'plumbing lead response time', 'Research shows leads go cold in minutes. Apply this specifically to plumbing contractors — the stats, the cost, and how automation closes the gap.'),
('plumbing-small-business-growth', 'How small plumbing businesses compete with the big guys on calls', 'Plumbing', '📈', 'linear-gradient(135deg,#001a2e,#003a5e)', 'plumbing small business growth', 'Solo and small plumbing operators often lose work simply because they can''t answer phones during jobs. Cover how AI receptionists level the playing field.'),
('plumbing-customer-experience', 'Why plumbing customers choose you before they''ve even met you', 'Plumbing', '⭐', 'linear-gradient(135deg,#001a2e,#003a5e)', 'plumbing customer experience', 'First impressions in plumbing happen on the phone. Cover how the initial call experience determines whether someone books or moves on.'),

-- Electrical
('electrical-after-hours', 'Electrical emergencies at 2AM: are you capturing them?', 'Electrical', '⚡', 'linear-gradient(135deg,#001a1a,#003d3d)', 'electrical contractor after hours', 'Electrical faults don''t follow business hours. Cover the frequency and value of after-hours electrical calls and how to never miss one.'),
('electrical-lead-capture', 'How electrical contractors lose commercial jobs to slow response', 'Electrical', '🏗️', 'linear-gradient(135deg,#001a1a,#003d3d)', 'electrical contractor lead capture', 'Commercial electrical opportunities often go to the first qualified contractor who responds. Cover the response-speed advantage and how to build it.'),
('electrical-small-contractor', 'The solo electrician''s guide to never missing a lead', 'Electrical', '🔌', 'linear-gradient(135deg,#001a1a,#003d3d)', 'solo electrician lead generation', 'Solo electricians are on the tools all day and can''t answer their phone. A practical guide to capturing every lead without interrupting your work.'),
('electrical-busy-season', 'Electrical contractor busy season: how to handle the call surge', 'Electrical', '📊', 'linear-gradient(135deg,#001a1a,#003d3d)', 'electrical contractor busy season', 'Cover how electrical contractors manage call volume spikes during busy periods and how AI receptionists scale automatically.'),

-- AI / Technology
('ai-receptionist-vs-virtual-assistant', 'AI receptionist vs virtual assistant: what''s the actual difference?', 'AI', '🤖', 'linear-gradient(135deg,#0a0a2e,#1a1a5e)', 'ai receptionist vs virtual assistant', 'Contractors confuse AI receptionists and virtual assistants. Clearly explain the differences in capability, cost, and use case — positioning Syntharra as the better option.'),
('ai-phone-calls-explained', 'How AI phone calls actually work (no jargon)', 'AI', '📱', 'linear-gradient(135deg,#0a0a2e,#1a1a5e)', 'how ai phone calls work', 'Plain-language explainer on how AI receptionists handle phone calls: speech recognition, response generation, live transfer logic. Written for trade business owners, not tech people.'),
('ai-receptionist-objections', 'The 5 things contractors say before they get an AI receptionist — and the truth', 'AI', '💬', 'linear-gradient(135deg,#0a0a2e,#1a1a5e)', 'ai receptionist for contractors', 'Address the most common objections: "customers won''t like it", "it''s too expensive", "I don''t trust AI", etc. Counter each with data and examples.'),
('ai-vs-hire-receptionist-2025', 'Hire a receptionist or get an AI? The 2025 cost breakdown', 'AI', '💰', 'linear-gradient(135deg,#0a0a2e,#1a1a5e)', 'hire receptionist vs ai 2025', 'Updated cost comparison for 2025: full-time receptionist salary, benefits, turnover vs AI receptionist flat monthly cost. Include break-even analysis.'),
('ai-receptionist-roi', 'The ROI of an AI receptionist: how to calculate it for your business', 'AI', '📊', 'linear-gradient(135deg,#0a0a2e,#1a1a5e)', 'ai receptionist roi', 'Walk through a simple ROI model: average job value, missed call rate, recovery rate, monthly cost. Make the math obvious for a trade contractor.'),
('ai-receptionist-accuracy', 'How accurate are AI receptionists? The honest answer', 'AI', '🎯', 'linear-gradient(135deg,#0a0a2e,#1a1a5e)', 'ai receptionist accuracy', 'Address AI receptionist accuracy honestly: what they get right, where they struggle, and how Syntharra''s system handles edge cases and difficult callers.'),

-- Operations
('trade-business-phone-system', 'Your phone system is costing you jobs — here''s what to change', 'Operations', '☎️', 'linear-gradient(135deg,#1a1a00,#3a3a00)', 'trade business phone system', 'Review the common phone system setups trade businesses use, why they fail at scale, and what a modern call handling setup looks like.'),
('contractor-missed-call-cost', 'How to calculate exactly how much your missed calls cost you', 'Operations', '🧮', 'linear-gradient(135deg,#1a1a00,#3a3a00)', 'contractor missed call cost calculator', 'Step-by-step guide for any trade contractor to calculate the real dollar cost of missed calls using their own numbers: call volume, job value, conversion rate.'),
('trade-business-automation', 'The 5 things every trade business should automate before hiring', 'Operations', '⚙️', 'linear-gradient(135deg,#1a1a00,#3a3a00)', 'trade business automation', 'Cover the top automation wins for trade businesses: call handling, scheduling, lead capture, follow-up, reporting. Position AI receptionist as the #1 priority.'),
('contractor-lead-management', 'Lead management for contractors: from first call to booked job', 'Operations', '📋', 'linear-gradient(135deg,#1a1a00,#3a3a00)', 'contractor lead management', 'Walk through the lead lifecycle for a trade contractor: inbound call → qualification → booking → job completion. Identify where leads are lost and how to fix each stage.'),
('contractor-voicemail-problem', 'Why voicemail is killing your contracting business', 'Operations', '📭', 'linear-gradient(135deg,#1a1a00,#3a3a00)', 'contractor voicemail problem', 'Cover why voicemail is not a solution for trade businesses: low callback rates, customer frustration, and competitor advantage. Make the case for live answer every time.'),
('call-handling-best-practices', 'Call handling best practices for trade businesses in 2025', 'Operations', '📞', 'linear-gradient(135deg,#1a1a00,#3a3a00)', 'trade business call handling', 'Comprehensive guide to call handling excellence for contractors: answer speed, greeting, qualification, booking, and follow-up. Practical and actionable.'),

-- Growth
('contractor-competitive-advantage', 'The one competitive advantage most contractors overlook', 'Growth', '🏆', 'linear-gradient(135deg,#0a1a0a,#1a3a1a)', 'contractor competitive advantage', 'Most contractors compete on price or reputation. Cover how speed-to-answer and availability are becoming the key differentiators — and how to win on both.'),
('trade-business-scaling', 'How to scale a trade business without adding headcount', 'Growth', '📈', 'linear-gradient(135deg,#0a1a0a,#1a3a1a)', 'scale trade business', 'Practical guide to scaling a trade business using systems and automation rather than hiring more staff. Lead capture, scheduling, reporting — all the levers.'),
('contractor-online-reviews', 'How your phone answer rate is silently affecting your Google reviews', 'Growth', '⭐', 'linear-gradient(135deg,#0a1a0a,#1a3a1a)', 'contractor google reviews', 'The connection between call handling quality and review ratings — customers who get great first phone experiences leave better reviews. Data-backed.'),
('trade-business-referrals', 'How to generate more referrals from your trade business without asking', 'Growth', '🤝', 'linear-gradient(135deg,#0a1a0a,#1a3a1a)', 'trade business referrals', 'Referrals come from great experiences, and experiences start on the phone. Cover how first-call impressions drive word-of-mouth growth.'),
('contractor-off-season', 'How to keep revenue coming in during the off-season', 'Growth', '❄️', 'linear-gradient(135deg,#0a1a0a,#1a3a1a)', 'contractor off season revenue', 'Practical strategies for keeping a trade business revenue-positive during slow months: maintenance contracts, outreach, and staying available.'),
('trade-business-first-impression', 'Your trade business''s most important marketing moment (it''s not your website)', 'Growth', '💡', 'linear-gradient(135deg,#0a1a0a,#1a3a1a)', 'trade business first impression', 'Make the case that the first phone call is more important than any marketing spend. Cover what happens when that moment is handled well vs poorly.'),

-- Pest Control / Cleaning (vertical expansion)
('pest-control-call-handling', 'Why pest control companies lose 1 in 3 jobs before they start', 'Operations', '🐛', 'linear-gradient(135deg,#1a0f00,#3d2400)', 'pest control call handling', 'Apply the missed-call problem to pest control: urgency of infestations, customer speed to book, and what happens when no one answers the first call.'),
('cleaning-business-phone', 'How cleaning businesses lose recurring clients on the first call', 'Operations', '🧹', 'linear-gradient(135deg,#1a0f00,#3d2400)', 'cleaning business phone answering', 'Cleaning businesses live on recurring revenue. Cover how the initial call experience determines whether a customer books once or becomes a long-term client.'),
('seasonal-contractor-calls', 'Seasonal contractors: how to handle the feast-or-famine call cycle', 'Seasonal', '🍂', 'linear-gradient(135deg,#001a0a,#003d1a)', 'seasonal contractor call handling', 'Seasonal trade businesses face extreme call volume swings. Cover how to manage peaks without burning out staff and valleys without missing the few calls that come in.');

-- Index for efficient querying
CREATE INDEX IF NOT EXISTS blog_topics_status_idx ON blog_topics(status);
