# Sentiment & Topic Classification Rubric

Used to classify Instagram comments for the Telkomsel / Indosat (IOH) / XLSMART
dashboards. Applied by manual judgment (by Claude, reading each comment), not a
keyword script — this doc exists so future runs stay consistent with past ones.

## Process
1. Exclude the brand's own official reply comments and blank/emoji-only rows
   from manual reading — auto-tag pure emoji/symbol comments (no Latin letters)
   as `Corporate & Brand` / `positive`.
2. Check `classification_cache.json` first — if a comment's exact trimmed text
   already has a cached label, reuse it instead of re-classifying. Comments get
   reposted verbatim often (spam templates, recurring complaints); this keeps
   labels stable across days and avoids redoing work.
3. For genuinely new text, read the comment in context (post caption helps
   disambiguate short comments like "keren" or "🔥🔥🔥") and assign one topic +
   one sentiment below. Add the result to the cache, keyed by the trimmed
   comment text.

## Topics
- **Network Experience** — signal, 5G/4G, jaringan, lemot, gangguan, coverage
- **Package & Pricing** — paket, kuota, harga, tarif, pulsa, billing, promo
- **Customer Service** — CS, DM/admin response, complaint handling, escalation
- **App & Account** — myXL/myIM3/MyTelkomsel app, OTP, eSIM, registration/NIK
- **Corporate & Brand** — awards, financials, generic praise/congrats, merger news
- **Events & CSR** — sponsorships, concerts, sports events, community programs
- **Other** — spam, off-topic, unrelated business disputes, gibberish

## Sentiment
- **positive** / **negative** / **neutral** — based on the comment's own tone,
  not the topic's usual valence (e.g. a "when is 5G coming" question is usually
  neutral, not automatically negative).

## Known caveats to preserve
- Recurring near-duplicate complaints (same complaint reposted many times,
  sometimes across multiple posts) inflate a topic's negative count — flag
  clusters of 5+ repeats in dashboard copy so readers don't mistake one viral
  complaint for many independent customers.
- Small-n breakdowns (under ~15 comments) should be labeled "(small n)" in
  charts — percentages on tiny samples are noisy.
