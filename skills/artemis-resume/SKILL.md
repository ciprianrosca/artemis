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
   - **knock-out check** (see "Getting to a human" below): every hard filter the ad or form can
     apply, the user's truthful answer, pass/fail. A failed hard filter means no cold application:
     go through a person or skip, and say which.
3. **Write `resume.md`**:
   ```markdown
   # <Full Name>
   <Market title> — <the target's language, e.g. Payments Platforms>
   {{contact}}

   ## Summary
   3–4 lines: level + years + domain match + 2 proof points + what I'm strongest at.

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
   **A CV is a standalone document about the candidate.** Tailor through choice, order and the ad's
   vocabulary, never by addressing the employer: no "this role", "your team", "the ground this role
   covers", "what you need", the company's name or its product. A CV that talks to one employer reads
   as mass-generated. Talking to the employer belongs in the cover letter and the form answers.
   `{{contact}}` is filled from `contact.json` at render time. In chat, write the contact line in
   directly from `contact.json`.
4. **Write `cover.md`** if the application takes one or it's a direct email: ≤250 words and 3
   paragraphs. Why this company and role (specific and researched); the 2 proof points that map to
   their top needs; a close with availability. Don't restate the resume.
5. **Render.**
   CLI: `python tools/render_resume.py applications/<folder>/resume.md --name <First>_<Last>_CV`
   (and `cover.md --name <First>_<Last>_Cover_Letter`). This gives `.docx` and `.pdf`. Use the PDF by
   default, for ATS forms and humans alike: once the renderer's ATS check passes, the PDF parses as cleanly
   as Word and looks the same on every screen, and the hiring manager usually opens the file the ATS stored.
   After uploading, check the fields the ATS autofilled from the CV. If they come out garbled, upload the
   DOCX instead; use the DOCX too when a form asks for Word, or when the ATS check flagged the PDF. If
   PyMuPDF is missing, the DOCX still renders; export the PDF from Word or Google Docs.
   Chat: create the DOCX (and PDF if available) with the document tools: one column, standard
   headings, no tables, text boxes, icons or photos, and contact details in the body, not a header.
   If file creation isn't available, give clean markdown they can paste into a document.
   The renderer reads the PDF back like a parser and prints `ATS check: ... reads back cleanly`.
   If it prints `ATS CHECK:` problems (ligature glyphs like "Staﬀ", missing headings), don't hand
   the PDF over: hand over the DOCX, or have them export the PDF from Word.
6. **Check before handing over** (one line per check):
   - [ ] the renderer's ATS check passed
   - [ ] one employer per `###` entry (two companies on one line become one garbled employer)
   - [ ] section headings are the standard ones parsers expect: Summary, Experience, Projects,
     Skills, Education (put extras like a GitHub link in the line under the heading, not in it)
   - [ ] 1 page for under 10 years of relevant history, otherwise 2 pages at most
   - [ ] every must-have keyword they truly have appears at least once, spelled as in the JD
   - [ ] every number traces to the fact bank
   - [ ] no `[GAP]`, `[VERIFY]`, `[CONF]`, `{{` or `**` left in the output
   - [ ] the CV never addresses the employer ("this role", "your team", their name): it would read
     the same if someone else picked it up
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
user pastes and submits them. Artemis never fills in or submits the form. Write them by the
answer rules below.

## Getting to a human

A cold application meets machines first: knock-out questions, location and salary fields, keyword
search and, more and more, an AI match score (Ashby, Workday, Eightfold, Rippling, LinkedIn's
"screening questions"). A rejection within 48 hours is almost always one of these, not a person.
Every rule here stays inside "never invent": we choose what to show first, never what's true.

**1. Knock-out check, before writing anything** (in `fit.md`). List each hard filter and the
truthful answer:
- location and work eligibility ("must be based in Spain or Poland"; the country list on a remote role)
- years of X, in the ad's own words ("7+ years managing managers")
- named must-have tech or domain ("production C#", "PCI DSS")
- languages, degree, on-site days, travel, notice period, posted pay range vs `search_criteria`
A truthful "no" on a hard filter fails the form no matter how good the CV is. Then the honest
moves are: a warm intro or a message to the hiring manager first (`artemis-linkedin`), or skip.
Don't spend a cold application on it.

**2. CV for the match score** (on top of the tailoring rules above):
- The headline under the name uses the ad's title family when it's true ("Engineering Manager —
  …" for an EM role, not "Director of Engineering"). The job lines keep the real titles.
- Must-have keywords go in the Summary **and** in the current role's bullets. Recent experience
  weighs more, and a keyword that appears only in Skills counts least.
- Spell the term as the ad does, and give both forms once: "Site Reliability Engineering (SRE)".
- State counts as numbers the parser can read: "15 years", "40+ engineers", "4 Engineering Managers".
- The contact line says where they can work from: "Bucharest, Romania (EU citizen)".

**3. Answer rules** (forms are read by an AI evaluator or a recruiter skimming 200 of them):
- **Yes/no and dropdowns: answer exactly and truthfully.** If the truthful answer fails, the
  knock-out check should have caught it. Never tick "yes" to get through.
- **Free text: lead with the strongest true fact, in the question's words.** First sentence =
  the answer. "Yes: I led a 40+ engineer division on a Java core-banking platform…", not
  "Limited. I haven't…". For a real gap: adjacent experience first, the gap plainly second,
  the plan third. Never open with the gap.
- **Short.** 2–4 sentences unless the field asks for more. One number per answer at least.
- **Mirror the ad's must-have words** where they're true: the evaluator compares answer to ad.
- **Salary:** a numeric field above the posted maximum is an automatic filter. If the user's
  floor is inside the posted range, give a number inside it. If the field is free text, give the
  range they'd accept and "depending on the total package". If their floor is above the range,
  tell them before they apply. The number is always theirs to choose.
- **Optional fields that feed the score** (LinkedIn URL, portfolio/GitHub, "anything else"):
  fill them. Empty fields score lower.
- **Notice / start date:** state it plainly ("available now").

**4. Channel and timing.**
- Apply within 72 hours of the posting date. Ranked lists favour early applicants, and recruiters
  often stop reading at the first good shortlist.
- Prefer the company's own ATS over LinkedIn Easy Apply or aggregators: Easy Apply carries the
  strictest auto-reject screening questions and the most volume.
- Every application to a role scoring 70+ gets a same-day message to the hiring manager or
  recruiter (`artemis-linkedin`). A person who has seen the name can pull the CV out of the pile.
- Fewer, better: one well-targeted application with a message beats five sprayed ones.

## Anti-patterns
- Keyword stuffing: a skill they can't talk about for 5 minutes doesn't go on the resume.
- One generic resume sent everywhere. The Summary and the order of the first 3 bullets change
  for every role.
- Two-column templates, tables, icons, photos, or contact details in headers and footers. ATS
  parsers drop them.
- Inflating titles. Use the title they actually held; the Summary can describe the real scope.
