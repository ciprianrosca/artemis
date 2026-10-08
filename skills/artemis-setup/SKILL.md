---
name: artemis-setup
description: "Artemis onboarding. Use when the user says 'artemis setup', 'artemis demo', 'artemis profile', or is new to Artemis and has no fact bank yet, or wants to update their master CV, target roles, location rules or constraints. Reads their CV and public LinkedIn, interviews them, and writes the fact bank (master_cv.md) and search settings (knowledge.json)."
---

# Setup: from a CV to a working job-hunting partner

## Where things live

| | Claude Code / Codex (CLI) | Claude app (chat) |
|---|---|---|
| Fact bank | `profile/master_cv.md` | `master_cv.md` in the Project's knowledge |
| Settings | `profile/knowledge.json` | `knowledge.json` in the Project's knowledge |
| Contact line | `profile/contact.json` | `contact.json` in the Project's knowledge |
| Pay numbers | `profile/comp.local.json` | keep them in chat, or in a file you upload yourself |
| Templates | `templates/` | the template sections in this skill |

**In the chat app** you can't write to Project files. Produce each file as a downloadable file,
then tell the user: "Download it, open your Project → Project knowledge, upload it, and remove the
old version." Do this once at the end of setup, not after every question.

## `artemis demo`: try it first (CLI)

Copy `examples/demo/*` into `profile/` (only if `profile/knowledge.json` doesn't exist yet: never
overwrite a real profile). Say: "You're now Sam Rivera, a fictional backend engineer in Lisbon. Try
`artemis find`, `artemis fit <any job URL>`, or `artemis tailor <url>`. Run `artemis setup` when you
want to switch to your own profile." When they run setup later, delete the demo files from
`profile/` first (`master_cv.md`, `knowledge.json`, `contact.json`, `pipeline.md`), after confirming.

In a chat app (Claude, ChatGPT, Gemini): use `artemis-demo-sam-rivera.md` from the knowledge
files as the user's files for the session, and say Sam is fictional.

## `artemis setup`: the onboarding

Keep it short and friendly. Work in rounds of 3–5 questions; never dump a 30-question form.
Tell them up front: "About 10 minutes. I'll read your CV first so I only ask what's missing."

### 1. Check the state
- If a real `profile/knowledge.json` exists, this is an update: ask what changed and go to step 6.
- If the demo persona is loaded, offer to clear it.

### 2. Collect the CV: any one of four inputs is enough
Ask once, listing all four options:

> "Send me your CV in whichever form is easiest:
> 1. a **PDF** (including LinkedIn's *More → Save to PDF*),
> 2. a **Word document** (.docx),
> 3. your **LinkedIn profile link**, or
> 4. your **whole LinkedIn profile copied and pasted** (open your profile, select all, copy, paste here).
> More than one is even better. Then I'll only ask about what's missing."

How to read each one:
- **PDF or DOCX.** CLI: `python tools/read_cv.py <path>` (the user gives the path, or drags the file
  into the terminal). Chat: the attachment. If a PDF gives almost no text, it's a scanned image: ask
  for another option. An old `.doc`: ask them to save it as .docx or .pdf.
- **LinkedIn link.** CLI: `python tools/read_cv.py <url>` reads the public, logged-out profile. Chat:
  fetch the page if browsing is available. Public profiles often come back cut short or behind a
  login wall. If so, say so and ask for option 4 or the Save-to-PDF export. Don't guess what's missing.
- **Pasted LinkedIn page.** It arrives messy: navigation text, "Show all", endorsement counts, "…see
  more", and people-also-viewed lists. Keep only Name, Headline, About, Experience (each role with
  dates and description), Education, Licenses & certifications, Skills, Languages and
  Recommendations. Pasted text often truncates long sections ("…see more"); list the roles whose
  description looks cut off and ask for the full text.
- Anything else with facts helps too: performance reviews, a portfolio, award letters, an older CV.

Tag sources by what came in: `S1` = the CV file, `S2` = LinkedIn (link or paste), with the date.

### 3. Build the fact bank
Start from `templates/master_cv.template.md`. Put **every fact on its own line with its source tag**
(`S1` CV, `S2` LinkedIn, `S3` the user in session, with the date). Rules:
- Copy facts; don't polish them yet. Numbers stay exactly as written.
- Where the CV and LinkedIn disagree (titles, dates, numbers), keep both and mark `[VERIFY]`.
- Mark missing numbers `[GAP: ...]`. Each recent role should end up with 2–3 quantified outcomes.
- Mark anything confidential (non-public customer names, internal codenames, incidents) `[CONF]`.
- Never invent, round up or "improve" anything.

### 4. Interview: fill what the CV can't tell you
Round 1 (the search):
1. Which roles? Ask for titles as the market writes them, and the level. Is one step down OK?
2. Where can you work? Home city and country, on-site/hybrid radius, remote (anywhere? one region?),
   relocation, and work authorisation or visa needs.
3. Timing: are you employed (so the search is confidential), between roles, or serving notice?

Round 2 (preferences and limits):
4. Industries you'd love, and any you won't work in. Company stage.
5. What makes a role exciting (upside), and what's a deal-breaker?
6. Pay: current package, floor, target, currency. Say that these go in `comp.local.json`, which is
   gitignored and never committed (in chat: they stay in the conversation unless they upload them).
7. Contract limits: non-compete, non-solicit, confidentiality. If unsure, suggest they check
   their contract; don't guess.

Round 3 (the gaps): the top 3–5 `[GAP]` and `[VERIFY]` markers from step 3, biggest first.
Write each answer into the fact bank with `S3` and today's date, replacing the marker.

### 5. Write the settings
Fill `templates/knowledge.example.json` → `profile/knowledge.json`. Replace every `[ASK]`. Then
**write the filters yourself**. The user should never have to write a regex:
- `filters.title_regex`: matches their target titles and close market variants. Example for
  backend ICs: `\b(senior|staff|lead)\b.*\b(backend|software|platform)\b.*\b(engineer|developer)\b`.
- `filters.scope_regex`: only when titles are ambiguous across fields (a "Director" who must be in
  engineering: `engineer|software|technology|platform`). Otherwise leave it empty.
- `filters.exclude_title_regex`: levels and fields they don't want (junior, manager, sales...).
- `filters.location.onsite_ok_regex`: their country and cities in local and English spelling.
- `filters.location.remote_open_regex`: the remote wording that includes them (their region, its
  time zone, "worldwide|anywhere|global").
- `filters.location.remote_region_regex`: nearby countries whose "Remote, <country>" roles might
  still hire them through an Employer of Record. These are kept but flagged.
- `search.linkedin_locations`: their country, plus a region for remote searches.
- `search.board_queries`: 3–4 lowercase title phrases.
Write `profile/contact.json` from `templates/contact.example.json`, and copy
`templates/pipeline.template.md` → `applications/pipeline.md`.

### 6. Seed the watchlist (CLI)
Ask for 5–10 companies they'd love to work at. Run `artemis watch add` for each
(see `artemis-job-search`). Offer `python tools/discover.py --skip-watchlist` to find more: it
scans ~1,000 tech companies' careers boards with their filters. It takes a few minutes.

### 7. Check, then hand over
CLI: run `python tools/ats_jobs.py scan` and report how many roles passed the filters. If it's 0 or
over 100, adjust the regexes and say what you changed. Then summarise in five lines: who they are
(one line), what they're looking for, where, the open gaps, and the next command:
`artemis map` (where to aim) or `artemis find` (roles now).

## `artemis profile`: keep the fact bank true

Interview in rounds of 3–5 questions, starting with the most valuable gaps:
1. current scope (team, systems, budget) and the `[VERIFY]` lines
2. 2–3 quantified outcomes per recent role (delivery, reliability, cost, revenue, adoption, hiring)
3. technical or craft depth they can defend in an interview
4. the STAR story bank: 5–8 stories covering impact, failure, conflict, leadership and ambiguity

Write each answer with `S3` and today's date. Replace the marker instead of appending a duplicate.
Never "improve" a number they gave.
