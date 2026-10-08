# Artemis: an AI job-hunting partner

Artemis finds roles worth your time, tells you honestly how well you fit each one, and builds the
application: a tailored, ATS-safe resume, a cover letter, outreach to the right person, and
interview prep. She tracks every application and learns what works for you.

It runs on **Claude Code**, **Codex CLI** and the **Claude app** (claude.ai / desktop / mobile).

An illustrative run with the demo persona:

```
> artemis find
Apply: Senior Backend Engineer, Mollie (86/100). Payments + Go + ledger work match; gap: Kotlin depth.
Apply: Staff Engineer, Elastic (78/100). Remote Europe; gap: no search-engine experience, frame the Kafka pipeline.
Stretch: Backend Tech Lead, Wise (68/100). Hybrid London only: remote-restricted, check for an EOR.
Skip the other 23. Apply to Mollie and Elastic now.
```

## What makes it different

- **It never invents anything.** Every resume line comes from your *fact bank*, a master CV
  where each fact has a source. If a job wants something you don't have, Artemis says so and
  suggests an honest framing. If a number would help, it asks you.
- **Honest scoring.** Each role gets a 100-point fit score (level, must-haves, location, domain,
  pay, company health, upside) and a verdict: apply, stretch or skip.
- **Direct sources.** It reads companies' own careers boards (Greenhouse, Lever, Ashby,
  SmartRecruiters, Workable, Workday), HN "Who is hiring?", Himalayas, VC portfolio boards, We Work
  Remotely and LinkedIn's public job search. It's not limited to aggregators.
- **Draft only.** It never applies, sends a message or logs in for you. You review everything
  and press send yourself.
- **Your data stays yours.** Your profile, pay and applications live in gitignored folders on your
  machine (or in your private Claude Project).

## Pick your setup

| | Claude Code / Codex CLI | Claude app |
|---|---|---|
| Fit checks, tailored resume + cover letter, outreach, interview prep, offer maths | ✅ | ✅ |
| Job search | careers-board feeds + boards + LinkedIn (most complete) | web search |
| Discover companies (~1,000 tech careers boards) | ✅ | — |
| Pipeline and learning | automatic (local files) | you re-upload updated files |
| Needs | a terminal, Python 3.10+ | a Claude plan with Projects and Skills |

### Claude Code

```bash
git clone https://github.com/<you>/artemis.git
cd artemis
pip install -r requirements.txt      # only for rendering DOCX/PDF
claude
> artemis demo                       # try it as Sam, a fictional engineer
> artemis setup                      # then make it yours (about 10 minutes, starts from your CV)
```

### Codex CLI

Same steps, but run `codex` instead of `claude`. Codex reads `AGENTS.md`, which maps the same
commands to the same playbooks.

### Claude app (no terminal)

1. Download this repo (Code → Download ZIP), or ask someone to run `python tools/build_chat_pack.py`
   and send you `dist/chat/`.
2. **Upload the skills:** Settings → Capabilities → Skills → upload each zip from
   `dist/chat/skills/` (or zip each folder in `skills/` yourself, keeping the folder inside the zip).
3. **Create a Project** called "Artemis". Paste `chat/PROJECT_INSTRUCTIONS.md` into its instructions.
4. In the Project, say **`artemis setup`** and attach your CV. Artemis interviews you and gives you
   `master_cv.md`, `knowledge.json`, `contact.json` and `pipeline.md`. Upload them to the Project's
   knowledge. To try it first, upload the files from `examples/demo/` instead.

## Commands

```
# Start
artemis demo                       # load the fictional demo profile (CLI)
artemis setup                      # onboarding: CV + LinkedIn → fact bank + search settings
artemis profile                    # fill gaps in your fact bank

# Find
artemis find ["title"] [place]     # full sweep, deduped, scored, ranked
artemis scan                       # your watchlist's careers boards only (CLI)
artemis boards [hn|himalayas|getro|wwr]
artemis discover                   # scan ~1,000 tech companies for matches (CLI)
artemis watch add <company>        # add a company's careers board to your watchlist
artemis fit <url | pasted ad>      # scored fit, gaps, apply/stretch/skip

# Apply
artemis tailor <url>               # resume + cover letter → DOCX + PDF
artemis cover <url>                # cover letter only
artemis answers <url>              # drafts for application-form questions
artemis outreach <person|company>  # connection note, InMail, referral ask (text you send)
artemis linkedin people <company>  # hiring manager, recruiter, warm paths (public search)
artemis linkedin profile           # rewrite your headline, About and experience

# Track and decide
artemis pipeline | status | followups
artemis log <company> <stage>
artemis map                        # role families + target companies + pay reality check
artemis prep <company>             # company brief, likely questions, your stories mapped
artemis offer <details>            # gross → net, vs. your floor, negotiation levers
artemis recruiters                 # agencies and exec-search firms + outreach drafts
```

Plain language works too: "find me staff roles in Berlin", "is this a fit?", "prep me for Wise on Thursday".

## How it's built

```
CLAUDE.md, AGENTS.md     entry points for Claude Code and Codex
identity.md              who Artemis is, and the guardrails
skills/                  the playbooks: one SKILL.md per area, shared by all three surfaces
tools/                   standard-library Python: careers boards, job boards, LinkedIn public pages,
                         company discovery, DOCX/PDF renderer, chat-pack builder
templates/               blank fact bank, settings, contact line, pipeline
examples/demo/           Sam Rivera, a fictional backend engineer, for trying things out
data/catalog.json        ~1,000 tech companies' careers-board slugs (unverified, PRs welcome)
data/countries/          offer maths and employment-law notes per country
chat/                    Project instructions for the Claude app
profile/ applications/ memory/   YOUR data, gitignored
```

Every personal setting (target titles, where you can work, remote rules) lives in
`profile/knowledge.json`, so the tools contain nothing specific to any one person.

## Good to know

- **LinkedIn:** Artemis reads public, logged-out pages only, a few requests at a time, and stops
  when LinkedIn rate-limits. It's for one person's search, not bulk collection. Using it is your
  call under LinkedIn's terms; everything else works without it.
- **Pay, tax and law:** offer maths comes with sources and dates, but it isn't financial or legal
  advice. Have a professional check anything that decides a contract.
- **Your data:** `profile/`, `applications/` and `memory/` are gitignored. If you fork this repo
  publicly, they stay on your machine.

## Contributing

Pull requests are welcome, especially:
- new country packs in `data/countries/` (see the README there)
- more careers-board slugs in `data/catalog.json`
- new job sources in `tools/`, which must use public APIs or feeds and the standard library only
- fixes when a job board changes its format

## License

MIT. Built by [Ciprian Rosca](https://www.linkedin.com/in/ciprianrosca/) with Claude.
