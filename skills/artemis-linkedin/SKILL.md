---
name: artemis-linkedin
description: "Artemis's LinkedIn and outreach skill. Use when the user says 'artemis linkedin ...' or 'artemis outreach', or asks to search LinkedIn jobs, read a LinkedIn job posting, find the hiring manager or recruiter at a company, improve their LinkedIn profile (headline, About, experience), or draft a connection note, InMail, referral ask or recruiter reply. Public, logged-out data only: Artemis never logs in, messages or applies on the user's behalf."
---

# LinkedIn: search, people, profile, outreach

**Access model.** There's no LinkedIn API or login. Artemis reads LinkedIn's **public, logged-out**
pages: job search and postings through `tools/linkedin_jobs.py` (CLI), and public profiles through
web search. Keep the volume personal-scale. The tool pauses between requests and stops on HTTP 429.
Anything behind a login (messaging, Easy Apply, connection degrees) the user does in their browser.
In chat, use web search and web fetch for the same public pages.

## `artemis linkedin search <keywords> [location] [--remote]` (CLI)

```bash
python tools/linkedin_jobs.py search "<keywords>" --location "<location>" --days 7 \
  [--remote|--hybrid|--onsite] [--level mid-senior,director] [--pages 2]
```
- Location is free text ("Portugal", "Berlin", "European Union"). Use `--geo-id` for precision once
  you know a geoId, and record working ones in `knowledge.json` → `search`.
- `--days` 1, 7 or 30 map to LinkedIn presets; any other value works as N days.
- LinkedIn's level tags are unreliable (many director roles are tagged "Mid-Senior"), so drop
  `--level` if results look thin.
- Pass the results through the rubric in `artemis-job-search`. Don't dump raw JSON.

## `artemis linkedin job <id|url>`
Take the numeric id (the digits at the end of `/jobs/view/...-<id>`) and run
`python tools/linkedin_jobs.py detail <id>`. It returns the title, company, location, posted date,
applicant count, criteria and full description. "Not found" means the posting was closed: say so
and check the company's own careers page.

Read the applicant count as a signal: "Be among the first 25" means apply today; "over 200
applicants" means the application needs a referral or a direct note to the hiring manager.

## `artemis linkedin people <company> [role]`
Find the people behind a posting with **public** web search:
- Hiring manager: `site:linkedin.com/in "<company>" ("<likely manager title>")`. Infer the title
  from the JD's reporting line.
- Recruiter: `site:linkedin.com/in "<company>" ("Technical Recruiter" OR "Talent Acquisition") <region>`
- Warm paths: `site:linkedin.com/in "<company>" ("<past employer 1>" OR "<past employer 2>")`, using
  the user's past employers from the fact bank. Former colleagues now at the target are the
  strongest route in. Respect `constraints.non_solicit`: asking a current colleague for a referral to
  another company is fine; recruiting them away may not be.

To read a found profile: `python tools/linkedin_jobs.py profile <url>`. Read a handful per company,
never in bulk. Return names, titles and profile URLs (bare, one per line) with a confidence note
("likely hiring manager: the title matches the JD's reporting line"). Never guess email addresses.

## `artemis linkedin profile`
Read what recruiters see now: `python tools/linkedin_jobs.py profile <knowledge.json → candidate.linkedin_slug>`
(in chat: web fetch, or ask them to paste it). Diff it against the fact bank and flag mismatches in
titles, dates or numbers, because a resume that contradicts LinkedIn is a red flag in screening. Then
rewrite it for the target role family, using only the fact bank:
- **Headline** (≤220 chars): role + domain + differentiator. Give 3 options.
- **About** (≤2,600 chars): a first-person opening (what they do and for whom), 3 proof points with
  numbers, how they work, what they're looking for (skip this if the search is confidential), and the
  keywords recruiters search for.
- **Experience:** 3–5 bullets per role, taken from the resume bullets. Use market titles; recruiters
  search on titles.
- **Skills:** the top 3 to pin.
- **Settings:** if they're employed, turn off "Share profile updates with your network" before
  editing, and use Open to Work as **recruiters only**, never the public banner.

## `artemis outreach <person|company> [context]`
Draft the message **as text** for the user to send. Never send it through any connector.
- **Connection note** (≤300 chars): a specific hook, one line of relevance, a light ask.
- **InMail / email to the hiring manager** (≤120 words): why this role, one proof point matched to
  their JD, a 20-minute ask.
- **Referral ask to a former colleague** (≤100 words): the role link, why they fit, an offer to
  send a tailored CV, and an easy out.
- **Recruiter reply:** interested / not now / not interested, each keeping the door open. Include
  pay or availability only if the user approves.
Give 2 variants per message. The tone is peer to peer, not supplicant, with no flattery. Log every
sent message in the pipeline under last contact once the user says they sent it.
