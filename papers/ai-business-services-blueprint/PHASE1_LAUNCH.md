# Phase 1 Launch Kit — Pricing & Outreach

Concrete, publishable pricing and a ready-to-send outreach message for the
three chosen Phase 1 services (see `CHECKLIST.md`): Invoice Processing, AI
Data Entry, Spreadsheet Cleanup. Prices are fixed and published up front so
no sales call is ever needed to quote a job — the intake form plus this
price list closes the sale.

## Pricing

### Invoice Processing
| Tier | Volume | Price | Turnaround |
|---|---|---|---|
| Starter | Up to 25 invoices | $75 flat | 2 business days |
| Standard | 26-100 invoices | $150 flat | 3 business days |
| Bulk | 101-300 invoices | $300 flat | 5 business days |
| Recurring | Any volume, monthly | 20% off one-time price | Same-cycle, every month |
- Rush (half the standard turnaround): +50%
- Over 300 invoices: custom quote, still via form (add a "describe your volume" field), not a call

### AI Data Entry
| Tier | Volume | Price | Turnaround |
|---|---|---|---|
| Starter | Up to 200 records | $60 flat | 2 business days |
| Standard | 201-1,000 records | $180 flat | 3 business days |
| Bulk | 1,001-5,000 records | $450 flat | 5 business days |
| Recurring | Any volume, monthly | 20% off one-time price | Same-cycle, every month |
- Rush: +50%
- Over 5,000 records: custom quote via form

### Spreadsheet Cleanup
| Tier | Scope | Price | Turnaround |
|---|---|---|---|
| Starter | Single sheet, up to 1,000 rows | $60 flat | 1-2 business days |
| Standard | Multi-tab workbook, up to 5,000 rows | $150 flat | 3 business days |
| Complex | 5,000+ rows or broken formulas/macros | $300 flat | 5 business days |
- Rush: +50%

### Bundle pricing (referral pitch to bookkeepers/accountants)
"Bookkeeping Cleanup Bundle" — one client's invoices + data entry +
spreadsheet cleanup in a single job: **10% off the combined total** of
whichever tiers apply. Priced this way so an accountant referring a messy
client sees one number, not three separate quotes.

## Publishing the prices
Put this pricing table (or a simplified version) on:
- A one-page site / Notion page / Google Site linked from every intake form
- The intake form's description field itself (Apps Script `description`
  field in `intake-forms/generate_google_forms.gs` — update it to include
  the relevant price tiers)
- Any Upwork/Fiverr gig listing, as a fixed-price gig, not "message me for
  a quote"

## Outreach message — for bookkeepers/accountants (referral channel)
Subject: Take the cleanup work off your plate — I'll handle it, you keep the client

```
Hi [Name],

I run an AI-assisted back-office service — invoice processing, data
entry, and spreadsheet cleanup, turned around in 1-5 business days,
fixed price, no meetings required on either end.

I know a chunk of your time with clients goes to the stuff before the
real bookkeeping can start: unlabeled invoice piles, half-entered
spreadsheets, broken formulas. I'd like to be the person you hand that
to. You send me the files, I send back clean, ready-to-book data — you
stay the one talking to the client.

Pricing's fixed and published, so there's no back-and-forth to get a
quote: [link to pricing page / intake form].

Want me to clean up one file for you at the Starter rate, no commitment,
so you can see the output before referring anyone?

[Your name]
[Business name]
```

## Outreach message — for small business owners (direct, cold or community post)
Subject / post opener: Messy invoices or spreadsheets? Fixed price, 1-5 day turnaround, no calls needed.

```
If your invoices, data entry, or spreadsheets have piled up: send them
over, get them back clean — fixed price, no call required.

- Invoice Processing: from $75, 2-day turnaround
- AI Data Entry: from $60, 2-day turnaround
- Spreadsheet Cleanup: from $60, 1-2 day turnaround

Fill out the form, upload your file, get a price on the spot: [link]
```

## Channel checklist
Primary channels — direct, relationship-driven, and fully in your control:
- [ ] DM/email 5 local bookkeepers or accountants with the referral message
- [ ] DM/email anyone in your existing network who owns or runs a small
      business (contractors, restaurant owners, local shops) directly —
      warm outreach converts fastest for a brand-new offer
- [ ] Post the direct-outreach message in 2-3 relevant local Facebook
      business groups or r/smallbusiness (check each community's
      self-promotion rules first)
- [ ] Add the pricing page link to the description field of each of the
      three Google Forms

Fallback only — do not lead with these; marketplaces put you in a bidding
war and you don't control who lands on the form:
- [ ] Upwork/Fiverr fixed-price listings, only if the primary channels
      above haven't produced a client after a real attempt
