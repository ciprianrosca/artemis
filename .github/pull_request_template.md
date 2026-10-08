## What this changes

<!-- One or two sentences. Link the issue if there is one. -->

## Type

- [ ] Playbook (`skills/`) or instructions (`chat/`, `identity.md`)
- [ ] Tool (`tools/`)
- [ ] Data: companies (`data/catalog.json`) or a country pack (`data/countries/`)
- [ ] Docs

## Checklist

- [ ] No personal data: no real CVs, pay numbers, contacts or application details
- [ ] Guardrails intact: Artemis still never invents facts, and never applies or sends anything itself
- [ ] Tools: standard-library Python only (except the renderer), public APIs or feeds only
- [ ] Playbooks changed: I ran `python tools/build_chat_pack.py` and it passed
- [ ] Tested: what I ran, and on which app (Claude Code, Codex, Gemini CLI, ChatGPT, Gemini, Claude app)
