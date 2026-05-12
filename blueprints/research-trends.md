# Blueprint: Content Marketing Trends Research Report

## Goal
Research the latest content creation and marketing trends, identify the top 3 most important findings, write them with copywriting quality, generate a branded PDF, and email it to Mohamed.

## Trigger
On-demand. Run when Mohamed says "research trends", "latest marketing trends", or invokes `/research-trends`.
Optional argument overrides the topic (default: content creation and marketing).

## Required Inputs
- Topic — defaults to "content creation and marketing trends"
- Recipient email — defaults to `mohamed.build30@gmail.com`

## Pre-flight Checks
1. `equipment/generate-trends-pdf.py` exists — if missing, stop and report
2. Zapier Gmail send action is enabled — call `list_enabled_zapier_actions` to confirm. If missing, stop.
3. Dependencies installed: `pip install -r equipment/requirements.txt`
4. `briefings/` directory will be created automatically by the script

## Equipment
`equipment/generate-trends-pdf.py` — generates branded PDF and sends email with attachment

## Sequence

### Phase 1 — Research (Architect, natively)

1. Run these searches in sequence:
   - `"content creation marketing trends 2026"`
   - `"top content marketing strategies brands 2025 2026"`
   - `"B2B content marketing trends SME 2026"`
   - `"social media content trends creators 2026"`

2. For each search, WebFetch the top 2 results for source depth — prioritise:
   - HubSpot, Content Marketing Institute, Sprout Social, Hootsuite, SEMrush, Nielsen, Forrester
   - Recent publications (2025–2026 only — discard anything older)

3. Synthesise across all sources. Look for signal, not noise:
   - What appears across 3+ independent sources? That is a real trend.
   - What is genuinely new vs. recycled content from 2023?
   - Weight relevance to AGENCINA's clients: SME owners, HR consultants, property developers, MENA market

### Phase 2 — Analysis (Architect, natively)

4. Identify the top 3 findings. Scoring criteria (rank highest on all three):
   - **Relevance** — applies to AGENCINA or its clients
   - **Actionability** — something that can be acted on within 90 days
   - **Novelty** — not already common knowledge among marketers

5. For each finding, draft:
   - **Heading**: Clear, specific, no jargon. Max 12 words.
   - **Body**: 3–5 sentences. What is the trend, what is the evidence, what is driving it.
   - **Why it matters**: 2–3 sentences. Direct impact on AGENCINA or its SME clients.

   Apply copywriting principles from the `/copywriting` skill:
   - Specific over vague — use real numbers and outcomes
   - Benefits over features — what does this mean for the reader?
   - No buzzwords — "AI-assisted" not "leveraging cutting-edge AI"
   - Active voice — "Brands that do X see Y"

### Phase 3 — PDF Generation (Equipment)

6. Build the data JSON:
   ```json
   {
     "title": "Content Marketing Trends — [Month YYYY]",
     "subtitle": "Top 3 findings from cross-source analysis",
     "intro": "2–3 sentence executive summary of what this report covers and why these three trends were selected.",
     "findings": [
       {
         "rank": 1,
         "heading": "...",
         "body": "...",
         "why_it_matters": "..."
       },
       {
         "rank": 2,
         "heading": "...",
         "body": "...",
         "why_it_matters": "..."
       },
       {
         "rank": 3,
         "heading": "...",
         "body": "...",
         "why_it_matters": "..."
       }
     ]
   }
   ```

7. Write data to `briefings/.tmp-trends-data.json`

8. Run:
   ```bash
   python equipment/generate-trends-pdf.py --data-file briefings/.tmp-trends-data.json --recipient mohamed.build30@gmail.com
   ```

9. Delete `briefings/.tmp-trends-data.json` after the script completes

### Phase 4 — Delivery

10. Call `mcp__zapier__execute_zapier_write_action` with the Gmail send action. Include:
    - To: `mohamed.build30@gmail.com`
    - Subject: `[AGENCINA Research] [title] — [DD Mon YYYY]`
    - Body: full formatted findings (heading + body + why it matters for each), plus the PDF path at the top
11. Report: PDF filename, email subject, delivery status

## Expected Output
- `briefings/trends-YYYYMMDD-HHMM.pdf` — branded research PDF, saved permanently
- Email delivered to `mohamed.build30@gmail.com` with PDF attached (or Gmail draft as fallback)

## Failure Handling

| Problem | Action |
|---------|--------|
| No web results | Try 2 alternative search queries before stopping |
| Fewer than 3 credible sources | Widen search — try "content marketing report 2025" and "marketing trends whitepaper" |
| `fpdf2` not installed | "Run: pip install -r equipment/requirements.txt" |
| No Gmail action in Zapier | Stop. "Enable a Gmail Send Email action in Zapier first." |
| Script exits non-zero | Show the error, do not retry automatically |
| Temp JSON file can't write | Check `briefings/` directory permissions |

## Notes
- Research must be grounded in 2025–2026 sources. Discard anything published before 2025.
- AGENCINA context: clients are SME owners — often non-technical, time-poor, results-focused. Trends that help them get more from less score highest.
- "Why it matters" is the most important section of each finding — that is what Mohamed uses when talking to clients.
- PDF is saved permanently in `briefings/` regardless of email outcome. Never delete it.
- For SMTP: uses `BUSINESS_EMAIL` as sender via Gmail's SMTP SSL on port 465. Requires an App Password (not account password). See `.env.example` for setup notes.
