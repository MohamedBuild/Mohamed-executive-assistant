# Decision Ledger

Append-only. Every meaningful call gets logged here.
Format: [YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...

---

[2026-05-01] DECISION: Remove .mcp.json from git and add to .gitignore | REASONING: File contained Zapier auth token — sensitive credential should not be in version control | CONTEXT: Token moved to .claude/settings.local.json (gitignored). Same token, safer location.

[2026-05-01] DECISION: Convert blueprints to Claude Code skills in 3 tiers | REASONING: Tier 1 (invoice, quote, morning-brief) — equipment ready, no external deps, highest build queue priority. Tier 2 (proposal, onboarding) — equipment ready, minor complexity. Tier 3 (lead-followup) — blocked on Zapier action confirmation. | CONTEXT: All SKILL.md files follow recap-pipeline pattern. No new code written — all skills wrap existing equipment scripts.
