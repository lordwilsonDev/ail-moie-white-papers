# Black Swan Labs — Invoicing & Payments Checklist

**Purpose:** everything needed to take payment for a consulting / done-for-you engagement, cleanly and legally, using **Stripe Invoicing** as the primary rail.

Status: operational reference. Fill the `<< >>` placeholders once with your real details, then reuse.

---

## 0. Your fill-in-once details

| Field | Value |
|---|---|
| Legal / trading name | `<< Black Swan Labs LLC / your legal entity >>` |
| Business address | `<< address for invoices — required on every invoice >>` |
| Tax ID (EIN / VAT / etc.) | `<< EIN if US; VAT number if applicable >>` |
| Contact email for billing | `<< billing@... >>` |
| Default day rate | `<< $X,XXX / day >>` |
| Default terms | 50% deposit on signature, 50% net-7 on delivery |
| Client base | `<< mostly US / mostly international / mixed >>` |

> Two of these change your setup: **day rate** sets your deposit sizes, and **client base** decides which payment methods and tax lines you enable (see §4).

---

## 1. One-time Stripe setup (~30 min)

1. Create a **Stripe account** at stripe.com → activate it (business details, bank account for payouts).
2. **Branding:** Settings → Branding. Upload logo, set brand color, business name. This appears on every hosted invoice + receipt.
3. **Invoicing defaults:** Settings → Invoicing:
   - Set default **payment terms** (e.g. *Due on receipt* for deposits, *Net 7* for finals).
   - Turn on **automatic reminders** (before due, on due, after due). This alone recovers most late payments without you chasing.
   - Turn on **automatic receipts**.
   - Set invoice number prefix (e.g. `BSL-`).
4. **Payment methods** (Settings → Payment methods):
   - Enable **Card** always.
   - Enable **ACH Direct Debit** (US bank transfer) — **0.8% capped at $5**, vs ~2.9% for card. Push any invoice over ~$600 to ACH to save money.
   - International clients: enable relevant local methods; consider **Wise** as a parallel bank-transfer option for low-FX cross-border payment.
5. **Tax:** if you must charge sales tax/VAT, enable **Stripe Tax** (auto-calculates by client location). Most B2B consulting between businesses is either reverse-charge or exempt — confirm with an accountant for your entity; don't guess.

---

## 2. Every invoice MUST contain

A "legally clean" invoice needs all of these — Stripe prompts for most, but verify:

- [ ] The word **"Invoice"** and a **unique invoice number** (`BSL-0001`, sequential)
- [ ] **Issue date** and **due date**
- [ ] **Your** legal name, address, tax ID
- [ ] **Client's** legal name + address
- [ ] **Line items**: description, quantity/days, unit rate, line total
- [ ] **Subtotal, tax (if any), total due** — in the correct currency
- [ ] **Payment terms** ("50% deposit due on receipt", "balance net-7")
- [ ] **What the payment is for** — reference the SOW/engagement name & date
- [ ] Accepted payment methods

---

## 3. The engagement payment flow (per client)

```
Client says yes
      │
      ▼
Send SOW / engagement letter  ──►  client signs
      │
      ▼
Invoice #1  — 50% deposit, "Due on receipt"
      │        (do NOT start work until this clears)
      ▼
Do the work
      │
      ▼
Deliver
      │
      ▼
Invoice #2  — remaining 50%, "Net 7"
      │        auto-reminders handle chasing
      ▼
Paid → send receipt (automatic) → archive both invoices
```

**Rules that keep you out of trouble:**
- **No deposit, no work.** The deposit is non-refundable once work begins — state this in the SOW.
- **Never 100%-on-completion** for a new/unknown client. Milestone or 50/50 only.
- For ongoing work, switch to a **monthly retainer**: fixed fee invoiced on the 1st, net-7, auto-renewing until 30-day notice.

---

## 4. US vs international — what changes

| | Mostly US clients | International clients |
|---|---|---|
| Primary method | ACH (cheap) + card | Card + Wise bank transfer |
| Currency | USD | Invoice in USD or client's currency; watch FX |
| Tax line | US sales tax rarely applies to B2B consulting — confirm per state | VAT/GST may be reverse-charged to the client — put their VAT # on the invoice |
| Payout speed | 2 business days | Can be slower; Wise often faster/cheaper for the client |

> This table is operational guidance, not tax advice. Before your first invoice, get a 30-minute call with an accountant to confirm how your specific entity handles tax on services. It's cheap insurance.

---

## 5. Ready-to-send invoice template (copy into Stripe or a doc)

```
INVOICE  BSL-0001

Black Swan Labs
<< address >>
Tax ID: << EIN/VAT >>
billing@blackswanlabs.<< tld >>

Bill to:
<< Client legal name >>
<< Client address >>
<< Client tax ID if international >>

Issue date: YYYY-MM-DD        Due date: YYYY-MM-DD (Due on receipt)

Re: << Engagement name >>, per SOW dated YYYY-MM-DD

──────────────────────────────────────────────────────────────
Description                          Days    Rate        Amount
──────────────────────────────────────────────────────────────
<< MMVP Reliability Audit >> —        X.0    $X,XXX     $XX,XXX
50% deposit
──────────────────────────────────────────────────────────────
                                          Subtotal      $XX,XXX
                                          Tax                $0
                                          TOTAL DUE     $XX,XXX
──────────────────────────────────────────────────────────────

Payment: Card or ACH via the secure link in this invoice.
Terms: 50% deposit due on receipt. Work begins on cleared payment.
       Balance (50%) invoiced on delivery, net-7.
```

---

## 6. Go-live checklist

- [ ] Stripe account activated + bank account connected
- [ ] Branding, default terms, reminders, receipts configured
- [ ] Card + ACH (and Wise if international) enabled
- [ ] Tax question resolved with an accountant
- [ ] SOW / engagement-letter template ready (see `business/engagement-letter.md` when drafted)
- [ ] Pricing sheet ready (see `business/pricing.md` when drafted)
- [ ] Test invoice sent to yourself and paid in **test mode** end-to-end
- [ ] First real invoice number reserved: `BSL-0001`

Once these are checked, Black Swan Labs can take money the same day a client says yes.
