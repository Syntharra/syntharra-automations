## 2026-04-06 — Verify-before-push discipline

What went wrong:
- Pushed "logo fix" to 7 email files without opening the result myself → shipped a version where the hosted PNG was still the old glyph → user saw the same broken state twice in a row → frustration
- Fixed the newsletter "logo missing" without first realizing the sample-data keys didn't match n8n's actual `{{ $json.foo }}` format → preview rendered newsletter as raw variables → user thought the template itself was broken

What I should have done:
1. Render the actual output (playwright headless → screenshot → read image) BEFORE telling user it's fixed
2. When a user reports "X is wrong", reproduce X locally first with evidence, then diagnose, then fix — not fix-by-guess
3. For templated content (n8n $json, Handlebars, Liquid, etc.), grep the actual template variable syntax before writing fill-in code

Pattern to enforce going forward:
- Any visual change to email/web/document → playwright screenshot → eyeball it → only then push
- Never "trust the diff" on visual output — the diff can look correct while the render is wrong
- "pushed 200" is NOT verification — only "screenshot shows expected result" is verification

Enforcement: the pre-action protocol now requires a rendered screenshot for any email/website change before the push step.

