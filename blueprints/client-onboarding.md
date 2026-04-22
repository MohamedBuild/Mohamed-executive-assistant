# Blueprint: Client Onboarding

## Goal
From "client says yes" to a ready-to-go project workspace in one command. Generates: project folder structure, onboarding questionnaire PDF, welcome email draft, and CRM entry. Nothing gets sent automatically — Mohamed reviews and sends.

## Trigger
Client confirms quote / signs contract.

## Required Inputs
- Client business name
- Contact person name
- Client email
- Project name
- Project type (e.g. "Agentic Workflow", "CRM Automation")
- Goals / objectives
- Timeline
- Payment structure: `upfront` | `50-50` | `on-delivery`

## Optional Inputs
- Phone number
- Scope details (pre-fills questionnaire)
- Budget range
- `--nda` flag (adds NDA note to welcome email)

## Pre-flight Checks
1. `.env` has `BUSINESS_NAME` and `BUSINESS_EMAIL`
2. `equipment/generate-onboarding-pack.py` is present
3. `fpdf2` and `python-dotenv` installed

## Equipment
`equipment/generate-onboarding-pack.py` — main script
`templates/contract.md` — contract template (fill manually, attach to email)

## Sequence

1. Confirm all inputs
2. Run:
   ```
   python equipment/generate-onboarding-pack.py \
     --client "Client Business Name" \
     --contact "Jane Smith" \
     --email "jane@client.com" \
     --project "Project Name" \
     --project-type "Agentic Workflow" \
     --goals "What the client wants to achieve" \
     --timeline "6 weeks from start" \
     --phone "+1234567890" \
     --scope "Detailed scope" \
     --budget "5000" \
     --payment 50-50 \
     [--nda]
   ```
3. Outputs:
   - `live/[project-slug]/` — full folder structure
   - `live/[project-slug]/onboarding/onboarding-form_[slug].pdf` — questionnaire for client
   - `live/[project-slug]/comms/welcome-email.md` — email draft
   - `live/[project-slug]/README.md` — project brief
   - `live/crm.csv` — CRM row appended
4. Mohamed's actions before sending:
   - Review `welcome-email.md`
   - Copy `templates/contract.md`, fill in scope/fees/terms, save to project folder
   - Attach contract + questionnaire PDF to email
   - Send manually from Gmail

## Expected Output Structure
```
live/[project-slug]/
├── README.md              — project brief
├── assets/                — logos, brand files, credentials
├── deliverables/          — completed work
├── comms/
│   └── welcome-email.md   — review before sending
└── onboarding/
    └── onboarding-form_[slug].pdf
```

## After Client Returns Questionnaire
1. File responses in `live/[project-slug]/onboarding/`
2. Update `live/[project-slug]/README.md` with confirmed scope
3. Update `live/crm.csv` status → "Active"
4. Update `intel/focus.md` if this is a priority project

## Failure Handling
| Problem | Action |
|---------|--------|
| Missing .env values | Report what's missing — do not run |
| fpdf2 not installed | `pip install fpdf2 python-dotenv` |
| Project folder already exists | Script skips folder creation silently — safe to re-run |
| CRM file missing | Script creates it with headers automatically |

## Notes
- CRM writes to `live/crm.csv` until Google Sheets credentials are connected
- Contract must be filled manually from `templates/contract.md` — never auto-sent
- `--nda` only adds a note to the email and reminder to attach — does not generate NDA content
- Re-running for the same project is safe — only the CRM adds a new row each time
