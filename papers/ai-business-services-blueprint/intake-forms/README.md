# Intake Forms — Index

One async intake form per service in `BLUEPRINT.md`. Every form follows the
same rule: **the form alone must be enough to scope and price the job — no
discovery call, no Zoom, no phone call.** If a field is unclear, the client
is emailed a follow-up question; the job is never gated on a live meeting.

## How to use these
1. Each `## N. Service Name` block is one form. Fields marked **Uploads:**
   are file-upload fields; everything else is a form field (text/select).
2. Every form ends the same way — `Turnaround`, `Budget range`, and
   `Delivery` — so pricing and scheduling are self-serve.
3. Build each block as a real form (Google Form, Typeform, Tally, etc.) or a
   structured intake email template. The fields listed are the field list,
   not prose to paste verbatim.
4. Revisions are handled by email or a short async screen recording, never
   a live call, for every service listed here.

## Files
| File | Category |
|---|---|
| `01-ai-virtual-employee-services.md` | AI Virtual Employee Services |
| `02-document-pdf-services.md` | Document & PDF Services |
| `03-administrative-services.md` | Administrative Services |
| `04-business-automation.md` | Business Automation |
| `05-sales-marketing.md` | Sales & Marketing |
| `06-customer-experience.md` | Customer Experience |
| `07-business-intelligence.md` | Business Intelligence |
| `08-industry-specific.md` | Industry-Specific AI Solutions |
| `09-ai-consulting.md` | AI Consulting |
| `10-subscription-services.md` | Subscription Services |
| `11-future-expansion.md` | Future Expansion |

## Coverage
All 109 services in `BLUEPRINT.md` have a corresponding form. Phase 0
services (see `../CHECKLIST.md`) are the ones to build first as real,
live forms; the rest can stay as this reference until the business
expands into that category.

## Generating live Google Forms
`generate_google_forms.gs` turns the 10 Phase 0 forms into real Google
Forms in one run — no manual form-building required:
1. Go to https://script.google.com → New project.
2. Paste in the contents of `generate_google_forms.gs`.
3. Run `createIntakeForms`, authorize the prompts (it only touches
   Forms/Sheets/Drive files it creates itself).
4. It creates a Google Sheet, **"Intake Forms — Links"**, in your Drive
   with the editor URL and the public "send to clients" URL for each of
   the 10 forms.

Re-running creates a fresh set rather than updating existing ones — delete
the old forms first if regenerating. To add the remaining 99 services from
the other category files, copy a form-definition block in
`getFormDefinitions()` and adapt the fields from the matching `.md` file.

## Common fields (every form, not repeated per-service below)
- Business name
- Contact name
- Contact email
- Contact phone (optional — text/SMS only, not a call request)
- How did you hear about us? (optional)
