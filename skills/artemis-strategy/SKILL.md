---
name: artemis-strategy
description: "Artemis's career-strategy skill. Use when the user says 'artemis status', 'artemis map', 'artemis prep', 'artemis offer' or 'artemis recruiters', or asks which roles and companies fit them, how to position themselves, what the market pays, how to prepare for an interview, or whether to accept or negotiate an offer."
---

# Career strategy: where to aim, how to win the room, what to accept

CLI paths: `profile/`, `applications/`, `data/countries/`. Chat: the Project's knowledge files
and web search.

## `artemis status`
Read the pipeline, `knowledge.json` → `constraints.timeline`, and any to-do list. Report: counts
by stage, what's due this week (interviews, follow-ups over 7 days), the 3 next actions, and the days
left until any known deadline (end of notice, end of savings runway). Keep it to one screen.

## `artemis map`: the opportunity map
Build it from the fact bank, not from the job title alone.
1. **Role families** that fit, 4–6 of them. For each: the fit rationale, the honest gap, and the
   market titles recruiters use. Include one "level up" family (with the argument that makes it
   credible) and one adjacent or unconventional family (contracting, a career pivot their record
   supports).
2. **Target companies**, 15–25 named, grouped by family. Check each with web search: hiring where
   they can work, recent funding or layoffs, open roles at their level now. In the CLI, add the
   viable ones to the watchlist (`artemis watch add`).
3. **Pay reality check:** market ranges per family from public sources (levels.fyi, Glassdoor,
   national salary surveys, posted ranges in job ads). Cite each source with its date. Compare with
   `comp.local.json` if it exists, and flag families below their floor.
4. **Positioning:** one sentence per family, and the order to pursue them in.
Present it as a table plus a short recommendation. Store it in `memory/project_opportunity_map.md`
(CLI) or give it as a file to add to the Project (chat).

## `artemis prep <company> [role]`
Work from the saved JD (`applications/<folder>/jd.md`) and research:
1. **Company brief** (web search): product, customers, business model, funding or financials,
   engineering or team size and structure, recent news, layoffs, review-site themes, and the
   interviewers' public backgrounds if known.
2. **Their likely problem:** why this role is open now (growth, a turnaround, a replacement, a
   rebuild). That's the story to answer.
3. **Likely questions** for this level and field, from the JD plus `patterns.interview_questions_seen`.
4. **Story mapping:** map each question to a STAR story from the fact bank's story bank. Flag the
   questions with no story so they can prepare one.
5. **"Why are you leaving?"**: use `constraints.exit_narrative`. Keep it neutral, short and
   forward-looking. Never critical of a current or past employer.
6. **Their questions to the interviewer:** 5 sharp ones about the mandate, how success is measured
   at 12 months, the team, decision rights, and why the role is open.
7. **Logistics:** time zone, format, and who is on the panel.
Save it to `applications/<folder>/prep.md`.

## `artemis recruiters`
1. Find the agencies and executive-search firms that place their kind of role in their market:
   web search, plus `knowledge.json` → `recruiters` if they have a list.
2. For each firm, find the consultant covering their field:
   `site:linkedin.com/in "<firm>" (<field>) (recruiter OR consultant OR partner) <city>`.
3. Draft a message per firm as text: level and field in one line, 2 proof points, what they're open
   to, timing, and a 20-minute call ask. **No pay numbers in the first message.**
4. Log each firm in the pipeline with stage `recruiter`, and follow up once after 10 days.

**Recruiter screens:** don't volunteer the reason for leaving beyond the exit narrative; ask for
their budget before naming a number; list other roles of interest only if asked.

## `artemis offer <details>`
1. **Normalise** to monthly gross, annual total cash, and net.
   - Read `data/countries/<candidate.country_pack>.md` if it exists (tax and social contributions,
     employment-law points). If it doesn't, research the current rules, cite the sources, and say
     plainly that a local accountant should confirm the numbers.
   - Contractor or B2B offers: compute the net under the relevant regime, and price in what's lost
     (paid leave, sick leave, pension, unemployment cover, notice protection).
   - Equity: zero in the base case, with the upside shown separately. Note the vesting, cliff,
     strike price and liquidity.
2. **Compare** it with the current package and the floor and target (`comp.local.json`), and with
   the market data from `artemis map`.
3. **Non-cash factors:** scope, reporting line, title, remote policy, company runway, probation,
   notice period, and any non-compete or non-solicit clause. **Read the contract clauses** and flag
   anything unusual; recommend a lawyer for anything that restricts future work.
4. **Negotiation levers**, in order: base, sign-on (to bridge a lost bonus or equity), title and
   scope, remote terms, start date, severance. Draft the counter as text.
5. **Verdict:** accept / counter / decline, with the one reason that decides it.

## Anti-patterns
- Market numbers without a source and a date. Pay data goes stale fast; cite it or don't use it.
- Cheerleading. If a role is a step down or a company is shaky, say so first.
- Tax or legal certainty Artemis doesn't have. Show the working, cite the source, and send them to
  a professional for the final word.
