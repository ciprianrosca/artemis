---
name: artemis-job-search
description: "Artemis's job-search skill. Use when the user says 'artemis find', 'artemis scan', 'artemis boards', 'artemis discover', 'artemis watch add', 'artemis fit', 'artemis pipeline', 'artemis log', 'artemis followups', or asks to find jobs that match their profile, check how well they fit a job posting, or track applications. Sweeps company careers boards, LinkedIn's public job search and other job boards, scores every role against a 100-point rubric, dedupes, and keeps the pipeline."
---

# Job search: find, score, track

Before searching, read the settings (`knowledge.json` → `search_criteria`, `filters`, `rubric`,
`constraints`), the fact bank (`master_cv.md`) and the pipeline (`pipeline.md`).
CLI paths: `profile/` and `applications/`. Chat: the Project's knowledge files.

## `artemis find [query] [location] [mode]`: the full sweep

1. **Build the query set.** With no query, use `search_criteria.target_titles`: 3–6 variants per
   run, not all of them. Locations and modes come from `search_criteria` and `search`.
2. **Run the sources.**

   **CLI (Claude Code, Codex):** independent commands, in parallel where the agent allows it:
   - Careers boards on the watchlist: `python tools/ats_jobs.py scan`
   - Other boards: `python tools/boards_jobs.py all` (HN "Who is hiring?", Himalayas, VC
     portfolio boards, We Work Remotely)
   - LinkedIn, once per title variant:
     `python tools/linkedin_jobs.py search "<title>" --location "<place>" --days 7`.
     Run one pass per entry in `search.linkedin_locations`; add `--remote` for the region pass.
     **At most 5 LinkedIn searches per run.** Stop LinkedIn for the run on any 429 warning and say so.
   - The manual watchlist (`watchlist_manual`): companies whose careers sites the tools can't
     read. Rotate through 3–4 per run with web search or web fetch.
   - `search.web_queries`: 2–4 per run with web search; open promising hits with web fetch.

   **Chat (Claude app), or when a tool fails:** use web search for the same ground:
   - `site:boards.greenhouse.io OR site:jobs.lever.co OR site:jobs.ashbyhq.com "<title>" <location>`
   - `site:linkedin.com/jobs/view "<title>" "<location>"`
   - each watchlist company: `"<company>" careers "<title>"`, then fetch the careers page
   - `search.web_queries`
   Say once that the chat version searches the web rather than the job boards' own feeds, so it can
   miss roles. The CLI version is more complete.

3. **Dedupe** on company + normalised title, merging locations. Drop anything already in the
   pipeline unless its status changed.
4. **Hard filters.** Drop the role and count it; don't list each one:
   - wrong level or field for `search_criteria.target_levels`. If a title is ambiguous but the JD
     clearly matches, keep it and label it `level-mismatch-title`.
   - on-site or hybrid somewhere they can't work (`work_modes`, `relocation`)
   - "Remote, <country>" outside their remote rule usually means remote *within* that country. The
     tools keep near misses and label them **`remote-restricted`**. Check the JD for an Employer of
     Record or contractor option, or "work from anywhere" / region wording, before scoring location.
   - postings older than 30 days, unless it's a high fit on the company's own board
5. **Score** every survivor with the rubric below. For the top 5–8, **fetch the full JD first**
   (`python tools/linkedin_jobs.py detail <id>` or web fetch). A score from the title alone is a
   guess: mark it `~`. Before recommending a role, check that it's still open on the employer's
   own careers page. A cached or aggregator copy is not proof.
6. **Present** a ranked table (verdict · score · role · company · location/mode · posted · source).
   Put **no links in the table**. Then add a Links block with each URL **bare, on its own line**: a
   markdown link breaks when copied from a terminal. Then add one line per top role (*why it fits ·
   the gap*), and close with the recommendation: "Apply to A and B now, research C, skip the rest."
   Show the top 10–15 roles; the rest become one count line.
7. **Record.** After the user picks, add the chosen roles to the pipeline as `shortlisted`. Log the
   queries that found good roles in `patterns.queries_that_work`.

## Fit rubric (100 points; the weights in `knowledge.json` → `rubric` override these)

| Dimension | Default pts | Full marks when |
|---|---|---|
| Level & scope | 25 | the level and scope match `target_levels`. One step down = about half, and say it's a step down |
| Must-have match | 25 | ≥80% of the JD's stated must-haves are backed by the fact bank (count them; list the misses) |
| Location & mode | 15 | fully inside their location rule. `remote-restricted` with no confirmed route = 5 until checked |
| Domain | 10 | in `industries_preferred`, or they have no preference. 0 and flag it if in `industries_avoid` |
| Comp signal | 10 | posted range or credible market data ≥ their floor. Unknown = 5 |
| Company health | 5 | growing, funded or profitable; no layoffs in the last 6 months |
| Upside | 10 | matches their `upside_signals` |

Verdicts: **≥75 apply** · **60–74 stretch** (apply if the gap has an honest framing) · **<60 skip**
unless they ask. Say the verdict before the number.

Red flags (subtract points and say why): the title says one level and the JD describes another; an
agency or outsourcing role presented as in-house; a posting reposted every month; no company named
(a recruiter fishing); an employer that conflicts with `constraints` (a former employer's client
under a non-solicit: applying may be fine, but they should know).

## `artemis scan`: watchlist only (CLI)
`python tools/ats_jobs.py scan [--company X]`. Report only what's **new** compared with the
pipeline, scored with the rubric.

## `artemis boards [hn|himalayas|getro|wwr]` (CLI)
`python tools/boards_jobs.py <source>`, scored with the rubric. HN posts monthly (the 1st
working day), so check it early in the month.

## `artemis discover` (CLI)
`python tools/discover.py --skip-watchlist` scans ~1,000 tech companies' boards from
`data/catalog.json` with the user's filters. It takes a few minutes; run it in the background if the
agent allows. Present the hits grouped by company, and offer to add the good companies to the watchlist.

## `artemis watch add <company>`
1. Find the careers page with web search and identify the ATS from the URL:
   `boards.greenhouse.io/<slug>` · `jobs.lever.co/<slug>` · `jobs.ashbyhq.com/<slug>` ·
   `jobs.smartrecruiters.com/<slug>` · `apply.workable.com/<slug>` · Workday
   `<tenant>.<wdN>.myworkdayjobs.com/<site>`, where the slug is `tenant/wdN/site`.
2. CLI: confirm with `python tools/ats_jobs.py probe <ats> <slug>`. You need `open_roles` > 0.
3. Append `{"company", "ats", "slug", "why"}` to `watchlist`.
4. Taleo, SuccessFactors, Avature or a custom site: the tools can't read it. Add it to
   `watchlist_manual` with its careers URL.
5. A VC portfolio board: open `https://<host>/jobs`, read `props.pageProps.network.id` from its
   `__NEXT_DATA__` script, and add `{"name", "host", "getro_id"}` to `vc_boards`.
In chat, give the user the updated `knowledge.json` to re-upload, after several additions rather than each one.

## `artemis fit <url|id|pasted JD>`
Get the full JD. Extract the must-haves and nice-to-haves **verbatim**. Map each one to a
fact-bank line (quote it) or mark it **missing**. Score it with the rubric. Give the verdict, the top
3 selling points for *this* role, the gaps with an honest framing for each, and 3 questions for the
recruiter. Don't write the resume yet; that's `artemis tailor`.

## Pipeline (`pipeline.md`)

One row per role:
`| id | company | role | location/mode | source | score | status | applied | last contact | next step (date) | folder |`

- `artemis log <company> <stage>` updates the status and dates (stages: `pipeline_stages`).
  Move a role to `applied` only when the **user** says they applied.
- `artemis followups`: anything `applied` for more than 7 days with no reply, or any interview step
  with no update after 5 working days. Draft the follow-up as text for them to send.
- `artemis pipeline`: the board grouped by stage, totals, the response rate, and what's due this week.
- On a rejection, record the reason if known and add the lesson to `patterns`.
- In chat, end any change with the full updated `pipeline.md` as a file to re-upload.

## Anti-patterns
- Scoring from the title alone and presenting that as a verdict.
- Burying the answer: the ranked table and the recommendation come first, the method last.
- Hammering LinkedIn: no loops of 20 queries. A few variants, a few pages, and stop on a 429.
- Recommending a role you haven't confirmed is still open.
