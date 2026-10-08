---
name: artemis-self-evolve
description: "Artemis's learning loop. Use after a search sweep, an application, a recruiter reply, an interview, a rejection or an offer, after the user corrects Artemis, or when a tool breaks, so the next session starts from what actually worked."
---

# Self-evolution: remember what worked

## When to trigger
1. A search sweep that surfaced good roles, or nothing.
2. An application sent, or a reply (screen invite, rejection, silence for more than 14 days).
3. An interview: the questions asked, what landed, what didn't.
4. An offer, or a pay number learned from a recruiter.
5. A new fact about the user: a number, a story, a preference, a constraint.
6. A correction: a framing they didn't like, or a role type they don't want.
7. A tool broke: LinkedIn markup changed, a careers-board slug moved, a 429.

## Where each learning goes

| Learning | CLI file |
|---|---|
| New or corrected fact about their experience | `profile/master_cv.md` (replace the marker, cite `S3` + date) |
| Preference: titles, locations, pay, industries | `profile/knowledge.json` → `search_criteria` (and `filters` if the scanners need it) |
| Constraint: timeline, legal, discretion | `profile/knowledge.json` → `constraints` |
| Query that worked or didn't | `knowledge.json` → `patterns.queries_that_work` / `queries_that_dont` |
| Resume framing that got a reply | `knowledge.json` → `patterns.resume_framings_that_got_replies` |
| Interview question seen | `knowledge.json` → `patterns.interview_questions_seen` (+ map it to a story) |
| Dead-end company (not hiring at their level, ghosted) | `patterns.dead_end_companies`, and remove it from `watchlist` |
| How they want Artemis to behave | `memory/feedback_<topic>.md` + a pointer in `memory/MEMORY.md` |
| A tool fix or quirk | `tools/*.py`, and consider sending it upstream (see README → Contributing) |
| Application state | `applications/pipeline.md` |

Memory files use this format:
```markdown
---
name: <short-kebab-case>
description: <one line, used to decide relevance later>
metadata:
  type: feedback | project | reference
---
<the rule or fact>. **Why:** <what happened, with the date>. **How to apply:** <when it matters>.
```

**In chat (Claude app):** Project files can't be written. When something worth keeping comes up,
say so in one line ("Worth remembering: …"). At the end of the session, offer the updated files
(`knowledge.json`, `master_cv.md`, `pipeline.md`) as downloads to replace in the Project. Short
behavioural preferences can also go in the Project's instructions.

## How to update
1. Be specific: the exact query, the company, the phrase, the date.
2. Update entries in place. One fact has one home.
3. Never commit `profile/`, `applications/` or `memory/`; they're gitignored for a reason.

## Anti-patterns
- Recording a recruiter's pay claim as market data without a source and a date.
- Letting `[GAP]` markers sit for weeks. Ask during the next `artemis profile`.
- Saving things that only mattered to this one conversation.
