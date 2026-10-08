---
name: artemis-resume
description: "Artemis's resume skill. Use when the user says 'artemis tailor', 'artemis cover', or asks for a tailored resume or CV, a cover letter, or answers to application-form questions for a specific job. Maps the job description to the user's fact bank (master_cv.md), writes an ATS-safe resume and cover letter, renders DOCX + PDF, and never invents facts."
---

# Resume tailoring: one fact bank, one resume per role

CLI paths: `profile/`, `applications/`, `tools/`. Chat: the Project's knowledge files; outputs are
downloadable files.

## The rule

**Every claim on a resume traces to a line in `master_cv.md`.** Tailoring means choosing,
ordering, emphasising, and rephrasing into the job's vocabulary *when the underlying fact is the
same*. It never means adding a number, technology, title, team size or result that isn't in the
fact bank. When the JD asks for something we don't have:
1. If they have it but it isn't recorded, ask, and add it to the fact bank first (with `S3` + date).
2. If they have something adjacent, frame it honestly ("built services on Kafka", not "Kafka expert").
3. If they have nothing close, leave it out and list it as a gap in `fit.md`.

Lines marked `[GAP]` / `[VERIFY]` are never printed as they stand. Lines marked `[CONF]` are
generalised first ("a top-3 European retailer", not the name).

## `artemis tailor <url|id|pasted JD>`

If the user has approved CVs in `profile/cvs/` (CVs they edited by hand and signed off), start
from the latest one: its wording, length and structure are the baseline, and tailoring changes the
Summary, the bullet order and the keyword emphasis.

1. **Get the JD.** CLI: `python tools/linkedin_jobs.py detail <id>` or web fetch the careers page.
   Chat: web fetch, or ask them to paste it. Save the full text to
   `applications/<YYYY-MM-DD>_<company>_<role-slug>/jd.md` with the URL and fetch date at the top.
   Postings disappear, so interview prep works from this saved copy. In chat, include the JD in the
   final download bundle.
2. **Analyse** into `fit.md`:
   - must-haves and nice-to-haves, **quoted**
   - the ATS keyword list: titles, domains, methods, tools, in the JD's own spelling
   - each requirement → fact-bank line (quoted) or **gap**
   - the rubric score (`artemis-job-search`) and the angle: the one-sentence story this resume tells
3. **Write `resume.md`**:
   ```markdown
   # <Full Name>
   <Market title> — <the target's language, e.g. Payments Platforms>
   {{contact}}

   ## Summary
   3–4 lines: level + years + domain match + 2 proof points + what I bring to *this* role.

   ## Experience
   ### <Title> — <Company> | <City (mode)> | <Mon YYYY> – Present
   - 4–6 bullets, ordered by relevance to this JD
   ### <Title> — <Company> | <City> | <Mon YYYY> – <Mon YYYY>
   - 2–4 bullets
   ### Earlier roles
   - <Title> — <Company>, <YYYY>–<YYYY> · <Title> — <Company>, <YYYY>–<YYYY>

   ## Skills
   3–4 grouped lines using the JD's keywords (only ones they can defend in an interview).

   ## Education
   <Degree> — <School>, <Year>
   ```
   **Voice:** first person with the "I" implied, and consistent: "Lead…" for the current role and
   "Led…" for past ones. The Summary may use "I". Never third person ("He leads", "Leads…"), unless
   the user's own CVs use another convention: then follow theirs and note it in `knowledge.json`.
   **Bullet formula:** strong verb + what + scale + outcome, with the number in the first half.
   "Cut p99 latency from 480 ms to 120 ms on the payment API", not "Responsible for performance".
   One or two lines per bullet.
   `{{contact}}` is filled from `contact.json` at render time. In chat, write the contact line in
   directly from `contact.json`.
4. **Write `cover.md`** if the application takes one or it's a direct email: ≤250 words and 3
   paragraphs. Why this company and role (specific and researched); the 2 proof points that map to
   their top needs; a close with availability. Don't restate the resume.
5. **Render.**
   CLI: `python tools/render_resume.py applications/<folder>/resume.md --name <First>_<Last>_CV`
   (and `cover.md --name <First>_<Last>_Cover_Letter`). This gives `.docx` and `.pdf`. Upload the
   DOCX to ATS forms (they parse Word better) and send the PDF to humans. If PyMuPDF is missing, the
   DOCX still renders; export the PDF from Word or Google Docs.
   Chat: create the DOCX (and PDF if available) with the document tools: one column, standard
   headings, no tables, text boxes, icons or photos, and contact details in the body, not a header.
   If file creation isn't available, give clean markdown they can paste into a document.
6. **Check before handing over** (one line per check):
   - [ ] 1 page for under 10 years of relevant history, otherwise 2 pages at most
   - [ ] every must-have keyword they truly have appears at least once, spelled as in the JD
   - [ ] every number traces to the fact bank
   - [ ] no `[GAP]`, `[VERIFY]`, `[CONF]`, `{{` or `**` left in the output
   - [ ] voice is consistent (no stray third person)
   - [ ] no non-public customer names, internal codenames or incident details
   - [ ] reverse-chronological; dates as `Mon YYYY`; tense consistent
   - [ ] the file name the recruiter sees has no job or company name in it (`First_Last_CV.docx`)
7. **Pipeline:** the role is `shortlisted` until the **user** confirms they applied.

## `artemis cover <url|id>`
Run steps 1, 2 and 4 of `tailor`, then render.

## `artemis answers <url>`: application-form questions
Draft answers to the form's questions ("Why us?", "Describe a hard technical problem"...) from
the fact bank and story bank, within each field's character limit, as text in `answers.md`. The
user pastes and submits them. Artemis never fills in or submits the form.

## Anti-patterns
- Keyword stuffing: a skill they can't talk about for 5 minutes doesn't go on the resume.
- One generic resume sent everywhere. The Summary and the order of the first 3 bullets change
  for every role.
- Two-column templates, tables, icons, photos, or contact details in headers and footers. ATS
  parsers drop them.
- Inflating titles. Use the title they actually held; the Summary can describe the real scope.
