# Session State

*Updated at the end of each session. Read this FIRST on startup.*

## Last Session
- **Date:** 2026-05-18
- **Summary:** Built batch invoice PDF generation from Google Sheet data. New equipment: `equipment/generate-invoice.py` (reads `templates/invoice_reference/invoice_template.docx`, fills {{TOKEN}} placeholders, converts to PDF via docx2pdf). Paid invoices get a diagonal PAID watermark (`#ededed`). Generated 15 PDFs from "AAA Operations — Internal Dashboard" Invoices tab — saved to `live/invoices/` (gitignored). Updated `blueprints/invoice-creation.md` to match real script. Dependencies added: `python-docx`, `docx2pdf`.

## Open Tasks
- Define quarterly goals in detail (intel/wins.md is seeded — refine together)
- Complete HR Consultant Automation project
- **REVIEW & SEND** Foster & Marsh Legal follow-up — Gmail draft ready (ID: r-560701422834561800), go to Gmail Drafts
- **FOLLOW UP** Zayd Property — $6,500 quote sent, follow-up overdue
- Review and send Sahel Cafe Group proposal PDF (`live/proposals/PROP-20260428-2016_sahel-cafe-group.pdf`)
- Fill in remaining .env fields: BUSINESS_ADDRESS, BUSINESS_PHONE, bank details
- **OVERDUE** Website / landing page — deadline was 2026-05-15

## Current Priorities
1. Finding clients
2. Website / landing page — overdue, needs immediate action
3. Pricing structure finalised

## Active Projects
- **HR Consultant Automation** — client onboarding, data scraping, market research. Status: Active.

## Skill Registry (live)

| Skill | Trigger | Status | Scope |
|-------|---------|--------|-------|
| `/frontend-design` | build UI, landing page, component, design | Live | Global |
| `/copywriting` | write copy, rewrite page, marketing copy | Live | Global |
| `/eisenhower` | prioritise tasks, eisenhower matrix | Live | Global |

## Subagent Registry (live)

| Agent | Trigger | Status | Location |
|-------|---------|--------|----------|
| `research-trends` | research trends, content trends, trend report, trends PDF | Live | `.claude/agents/research-trends.md` |
