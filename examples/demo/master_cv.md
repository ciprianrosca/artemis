# Master CV: fact bank (Sam Rivera)

> Demo persona. Sam Rivera and the employers below are fictional.

Every line on every resume Artemis writes comes from this file. Artemis rephrases, reorders and
chooses what to emphasise. It never adds a number, technology, title, date or result that isn't here.

**Markers:** `[GAP]` missing fact (ask, never guess) · `[VERIFY]` confirm the phrasing ·
`[CONF]` confidential, generalise first.

**Sources:** `S1` = CV PDF, Sep 2026. `S2` = public LinkedIn profile, read 2026-10-01.
`S3` = Sam in session.

## Identity

- **Name:** Sam Rivera — S1
- **Location:** Lisbon, Portugal — S1
- **Contact:** in `contact.json`
- **Work authorisation:** EU citizen — S3
- **Languages:** English (fluent), Portuguese (native), Spanish (conversational) — S1

## Positioning

Backend engineer who builds and runs high-volume payment systems in Go and Kotlin, and takes
services from first design to steady on-call. — S3

## Experience

### Tidewater Pay — Senior Backend Engineer | Lisbon (hybrid) | Mar 2022 – present
Payments scale-up (Series C, ~400 people) processing card and bank payments for European merchants. — S1
- Designed and built the payout ledger service in Go: double-entry, idempotent, ~3M payouts/month — S1
- Led the migration from a monolith to 40 services over 18 months with no payout-related incidents — S1 `[VERIFY: "no incidents" or "no Sev-1 incidents"?]`
- Cut p99 latency of the payment-authorisation API from 480 ms to 120 ms (caching + query rewrite) — S1
- Tech lead for a team of 5 engineers on the reconciliation squad (no line management) — S3
- On-call for the payments platform; wrote 12 runbooks still in use — S2
- Interviewed ~60 backend candidates; designed the take-home exercise — S3
- `[GAP: a cost or revenue number for the ledger work]`
- Large merchant migration for a top-3 European retailer `[CONF]` — S3

### Lumen Logistics — Backend Engineer → Senior Backend Engineer | Porto (on-site) | Jan 2019 – Feb 2022
Route-optimisation SaaS for regional delivery fleets. — S1
- Built the event pipeline (Kotlin, Kafka) feeding live vehicle positions to the planner: 20k events/sec at peak — S1
- Promoted to Senior in 2021 — S2
- Reduced cloud spend for the tracking stack by 35% by moving cold data to object storage — S1

### Brightforge Studio — Software Developer | Porto | Sep 2017 – Dec 2018
Digital agency. — S1
- Built Node.js and PHP backends for 8 client projects (e-commerce, booking) — S1

## Skills you can defend for five minutes in an interview

- **Technical:** Go, Kotlin, PostgreSQL, Kafka, gRPC, AWS (ECS, RDS, S3), Terraform, Datadog — S1
- **Ways of working:** design docs and RFCs, trunk-based development, incident reviews — S3
- **Domain:** payments (payouts, ledgers, reconciliation, PSD2 basics), logistics — S1

## Education & certifications

- BSc Informatics Engineering — Universidade do Porto, 2017 — S1
- AWS Certified Developer – Associate, 2023 — S2

## Story bank (STAR)

### The payout ledger
- **Situation / Task:** payouts were computed in the monolith with no audit trail; finance reconciled by hand.
- **Action:** wrote the design doc, built the double-entry ledger service in Go, ran it in shadow mode for 6 weeks.
- **Result:** ~3M payouts/month on the new ledger; manual reconciliation work removed `[GAP: hours saved]`.
- **Answers:** biggest impact · technical decision · ambiguity

### The latency fix
- **Situation / Task:** merchants complained about slow authorisations at peak.
- **Action:** profiled the API, found N+1 queries and missing caching, fixed both behind a flag.
- **Result:** p99 from 480 ms to 120 ms.
- **Answers:** debugging · performance · ownership
