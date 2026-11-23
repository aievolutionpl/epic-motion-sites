# AGENTS.md

This repo is an agent skill. If you are an AI agent asked to build an animated / premium / scroll-driven website:

1. Read `skills/epic-motion-sites/SKILL.md` and follow its workflow.
2. Paths inside the skill are relative to `skills/epic-motion-sites/`.
3. Verification with `scripts/verify.py` is required before hand-off.

If you are changing the skill itself:
- Keep `SKILL.md` under ~200 lines; put detail in `references/`.
- Test template changes by serving `skills/epic-motion-sites/assets/` or `examples/` over HTTP and running `verify.py --mobile`, and once more with `--reduced`.
- Keep `examples/*/index.html` identical to the matching template (the examples are the templates plus real images).
- Log user-visible changes in `CHANGELOG.md` and bump the version in `.claude-plugin/*.json`.
- Add new lessons to "Lessons learned" only when they came from a real build.
