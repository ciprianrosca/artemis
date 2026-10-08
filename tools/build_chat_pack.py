#!/usr/bin/env python3
"""Build the Claude app (chat) pack: one .zip per skill, ready to upload in Settings → Skills,
plus the Project instructions and the demo files.

  python tools/build_chat_pack.py          # writes dist/chat/

It also checks each SKILL.md against the Agent Skills limits (name: lowercase letters, digits and
hyphens, at most 64 characters; description: at most 1,024 characters).
"""
import os
import re
import shutil
import sys
import zipfile

from common import ROOT, utf8_console

utf8_console()

OUT = os.path.join(ROOT, "dist", "chat")


def frontmatter(path):
    with open(path, encoding="utf-8") as f:
        m = re.match(r"---\n(.*?)\n---\n", f.read(), re.S)
    if not m:
        sys.exit(f"{path}: no YAML frontmatter")
    fields = dict(re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', m.group(1), re.M))
    return fields.get("name", ""), fields.get("description", "")


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "skills"))
    problems = []
    skills_dir = os.path.join(ROOT, "skills")
    for name in sorted(os.listdir(skills_dir)):
        src = os.path.join(skills_dir, name)
        skill_md = os.path.join(src, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        fm_name, desc = frontmatter(skill_md)
        if fm_name != name or not re.fullmatch(r"[a-z0-9-]{1,64}", fm_name):
            problems.append(f"{name}: frontmatter name '{fm_name}' must equal the folder name (a-z, 0-9, -)")
        if not desc or len(desc) > 1024:
            problems.append(f"{name}: description is {len(desc)} characters (1–1,024 allowed)")
        zpath = os.path.join(OUT, "skills", f"{name}.zip")
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for dirpath, _, files in os.walk(src):
                for fn in files:
                    full = os.path.join(dirpath, fn)
                    z.write(full, os.path.join(name, os.path.relpath(full, src)))
        print(f"  {os.path.relpath(zpath, ROOT)}")
    shutil.copy(os.path.join(ROOT, "chat", "PROJECT_INSTRUCTIONS.md"), OUT)
    shutil.copytree(os.path.join(ROOT, "examples", "demo"), os.path.join(OUT, "demo"))
    shutil.copytree(os.path.join(ROOT, "templates"), os.path.join(OUT, "templates"))
    if problems:
        print("\n".join("PROBLEM: " + p for p in problems), file=sys.stderr)
        sys.exit(1)
    print(f"Chat pack ready in {os.path.relpath(OUT, ROOT)}/")


if __name__ == "__main__":
    main()
