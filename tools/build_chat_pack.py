#!/usr/bin/env python3
"""Build the chat packs from skills/, chat/ and examples/: one source, three apps.

  python tools/build_chat_pack.py          # writes dist/claude, dist/chatgpt, dist/gemini (+ zips)

dist/claude/    one .zip per skill (Settings → Skills), PROJECT_INSTRUCTIONS.md, demo, HOW_TO.md
dist/chatgpt/   INSTRUCTIONS.md (custom GPT, ≤8,000 characters) + 3 knowledge files + HOW_TO.md
dist/gemini/    INSTRUCTIONS.md (Gem) + the same 3 knowledge files + HOW_TO.md
dist/artemis-<app>.zip   each folder zipped, for a GitHub release

It also checks each SKILL.md against the Agent Skills limits (name: a-z, 0-9 and hyphens, at most
64 characters, equal to the folder name; description: at most 1,024 characters).
"""
import os
import re
import shutil
import sys
import zipfile

from common import ROOT, utf8_console

utf8_console()

DIST = os.path.join(ROOT, "dist")
GPT_LIMIT = 8000
SKILL_TITLES = {
    "artemis-setup": "Setup and profile",
    "artemis-job-search": "Job search, fit scoring and pipeline",
    "artemis-resume": "Resume, cover letter and form answers",
    "artemis-linkedin": "LinkedIn and outreach",
    "artemis-strategy": "Strategy: status, map, prep, offer, recruiters",
    "artemis-self-evolve": "Learning loop",
}
KNOWLEDGE_NOTE = ("They are the user's files, uploaded in the chat. Your own knowledge files "
                  "(playbooks, templates, demo) are Artemis's, not the user's: never treat the demo "
                  "persona as the user.")
PLATFORMS = {
    "claude": {
        "PLAYBOOKS": "Six Artemis skills are installed: artemis-setup, artemis-job-search, artemis-resume, "
                     "artemis-linkedin, artemis-strategy and artemis-self-evolve.",
        "FILES": "They live in this Project's knowledge. You can't edit Project files: give updated "
                 "files as downloads and remind the user to replace the old ones.",
        "DEMO": "`artemis-demo-sam-rivera.md`, if it's in Project knowledge; otherwise ask the user to add it",
        "DOCS": "Create .docx files (and PDF if you can) for download.",
    },
    "chatgpt": {
        "PLAYBOOKS": "Your knowledge file `artemis-playbooks.md` holds six playbooks: setup, job search, "
                     "resume, LinkedIn, strategy, learning loop. `artemis-templates.md` holds the blank "
                     "fact bank, settings, contact line and pipeline.",
        "FILES": KNOWLEDGE_NOTE + " They last only for this chat unless the user works in a ChatGPT "
                 "Project, so remind them to keep the latest versions.",
        "DEMO": "the knowledge file `artemis-demo-sam-rivera.md`",
        "DOCS": "Use the code tool with python-docx to create a .docx file for download, and a PDF if you can.",
    },
    "gemini": {
        "PLAYBOOKS": "Your knowledge file `artemis-playbooks.md` holds six playbooks: setup, job search, "
                     "resume, LinkedIn, strategy, learning loop. `artemis-templates.md` holds the blank "
                     "fact bank, settings, contact line and pipeline.",
        "FILES": KNOWLEDGE_NOTE + " They last only for this chat, so remind them to keep the latest versions.",
        "DEMO": "the knowledge file `artemis-demo-sam-rivera.md`",
        "DOCS": "Write resumes and cover letters in Canvas so the user can export them to Google Docs "
                "and download them as Word or PDF.",
    },
}


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def split_skill(name):
    text = read("skills", name, "SKILL.md")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        sys.exit(f"skills/{name}/SKILL.md: no YAML frontmatter")
    fields = dict(re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', m.group(1), re.M))
    return fields.get("name", ""), fields.get("description", ""), m.group(2).strip()


def skills():
    return [n for n in SKILL_TITLES if os.path.isfile(os.path.join(ROOT, "skills", n, "SKILL.md"))]


def playbooks_md():
    out = ["# Artemis playbooks\n\nOne section per area. Steps marked CLI need local scripts: in chat, "
           "use the chat fallback each section gives.\n"]
    for n in skills():
        _, desc, body = split_skill(n)
        body = re.sub(r"^(#+) ", lambda m: "#" + m.group(1) + " ", body, flags=re.M)  # demote headings
        out.append(f"\n---\n\n# Playbook: {SKILL_TITLES[n]} (`{n}`)\n\n_When: {desc}_\n\n{body}\n")
    return "".join(out)


def fenced(title, path, lang):
    return f"\n## {title} (`{path}`)\n\n```{lang}\n{read(*path.split('/')).strip()}\n```\n"


def templates_md():
    return ("# Artemis templates\n\nBlank files that setup fills in. Give the user each finished file "
            "with the file name shown.\n"
            + fenced("Fact bank", "templates/master_cv.template.md", "markdown")
            + fenced("Settings", "templates/knowledge.example.json", "json")
            + fenced("Contact line", "templates/contact.example.json", "json")
            + fenced("Pipeline", "templates/pipeline.template.md", "markdown"))


def demo_md():
    return ("# Demo persona: Sam Rivera (fictional)\n\nUse these as the user's files only when they ask "
            "for the demo. Sam and the employers below are made up.\n"
            + fenced("master_cv.md", "examples/demo/master_cv.md", "markdown")
            + fenced("knowledge.json", "examples/demo/knowledge.json", "json")
            + fenced("contact.json", "examples/demo/contact.json", "json")
            + fenced("pipeline.md", "examples/demo/pipeline.md", "markdown"))


def instructions(platform):
    text = read("chat", "instructions.md")
    for key, val in PLATFORMS[platform].items():
        text = text.replace("{{" + key + "}}", val)
    left = re.findall(r"\{\{\w+\}\}", text)
    if left:
        sys.exit(f"chat/instructions.md: unfilled placeholders for {platform}: {left}")
    return text


def zip_dir(src, zpath, prefix=""):
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(src):
            for fn in sorted(files):
                full = os.path.join(dirpath, fn)
                z.write(full, os.path.join(prefix, os.path.relpath(full, src)))


def main():
    shutil.rmtree(DIST, ignore_errors=True)
    problems = []
    knowledge = {"artemis-playbooks.md": playbooks_md(), "artemis-templates.md": templates_md(),
                 "artemis-demo-sam-rivera.md": demo_md()}

    # Claude app: real skills, uploaded as zips
    claude = os.path.join(DIST, "claude")
    for n in skills():
        name, desc, _ = split_skill(n)
        if name != n or not re.fullmatch(r"[a-z0-9-]{1,64}", name):
            problems.append(f"{n}: frontmatter name '{name}' must equal the folder name (a-z, 0-9, -)")
        if not desc or len(desc) > 1024:
            problems.append(f"{n}: description is {len(desc)} characters (1–1,024 allowed)")
        os.makedirs(os.path.join(claude, "skills"), exist_ok=True)
        zip_dir(os.path.join(ROOT, "skills", n), os.path.join(claude, "skills", f"{n}.zip"), prefix=n)
    write(os.path.join(claude, "PROJECT_INSTRUCTIONS.md"), instructions("claude"))
    write(os.path.join(claude, "artemis-demo-sam-rivera.md"), knowledge["artemis-demo-sam-rivera.md"])
    write(os.path.join(claude, "HOW_TO.md"), read("chat", "platforms", "claude.md"))

    # ChatGPT and Gemini: instructions + knowledge files
    for platform in ("chatgpt", "gemini"):
        folder = os.path.join(DIST, platform)
        text = instructions(platform)
        if platform == "chatgpt" and len(text) > GPT_LIMIT:
            problems.append(f"chatgpt INSTRUCTIONS.md is {len(text)} characters (limit {GPT_LIMIT})")
        write(os.path.join(folder, "INSTRUCTIONS.md"), text)
        for fn, body in knowledge.items():
            write(os.path.join(folder, fn), body)
        write(os.path.join(folder, "HOW_TO.md"), read("chat", "platforms", f"{platform}.md"))
        print(f"  {platform}: instructions {len(text):,} characters")

    for platform in PLATFORMS:
        zip_dir(os.path.join(DIST, platform), os.path.join(DIST, f"artemis-{platform}.zip"), prefix=f"artemis-{platform}")
        print(f"  dist/artemis-{platform}.zip")
    if problems:
        print("\n".join("PROBLEM: " + p for p in problems), file=sys.stderr)
        sys.exit(1)
    print("Chat packs ready in dist/")


if __name__ == "__main__":
    main()
