# Contributing to Artemis

Improvements are welcome. Anyone can propose a change; the maintainer reviews and approves every one
before it reaches `main`.

## How to propose a change

1. **Small fix or clear improvement:** fork the repo, make the change on a branch, and open a pull
   request. The template walks you through the checklist.
2. **Bigger idea, or not sure it fits:** open an issue first (Issues → New → "Idea or improvement"),
   so we can agree on the approach before you spend time on it.

Every pull request needs the maintainer's approval to merge. Expect a review within about a week.

## What's most useful

- **Country packs** in `data/countries/`: offer maths and employment-law notes for your country
  (see the README there).
- **Companies** in `data/catalog.json`: careers-board slugs, probed with
  `python tools/ats_jobs.py probe <ats> <slug>` first.
- **Job sources** in `tools/`: public APIs or feeds only, standard-library Python only.
- **Fixes** when a job board changes its format.
- **Playbook improvements** in `skills/`, especially ones you've tested on a real search.

## Ground rules

- **No personal data**, ever: no real CVs, pay, contact details or application history in commits,
  issues or examples. Use the fictional demo persona (`examples/demo/`) in tests and examples.
- **The guardrails stay.** Changes that let Artemis invent facts, or apply, send or log in on
  someone's behalf, won't be merged.
- **Public data at personal scale.** No bulk scraping, no logged-in automation, no guessed emails.
- **One source for all apps.** Edit `skills/` and `chat/instructions.md`, then run
  `python tools/build_chat_pack.py` to check the ChatGPT, Gemini and Claude packs still build.

By contributing, you agree your contribution is licensed under the repo's MIT license.
