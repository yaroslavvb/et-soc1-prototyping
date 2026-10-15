# Brief for every fixer of the chip diagram (14 Oct 2026)

The page "The ET-SoC-1, interactively" (https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram) was checked for
correctness today against the manuals, the core-et documents, the RTL, the firmware source and the lab's data. Each
finding was then checked by an independent skeptic. You apply the surviving fixes **in the source files you own**, in
the lab repository `/home/yaroslavvb/claude/et-soc1-prototyping` (branch main, at `bd8e731a`, the one checkout everyone
edits; other fixers edit other files in it at the same time).

## Your inputs

- `/home/yaroslavvb/claude/work/chip-check-1014/fixes/<group>.json`: your work list. Each item is a finding (what the
  page says, what is true, the evidence) with the skeptic's verdict (`confirmed` or `partly`) and **the skeptic's fix,
  which supersedes the checker's** when they differ. Items whose fix spans other groups' files list those files too:
  do only the part in your files, exactly as written (another fixer does the rest, from the same text, so keep the names
  of new numbers and keys exactly as the fix gives them).
- The same file may list `citations`: line-number citations of facts your files generate, settled by readers who checked
  each line at HEAD (`action` remap: replace the cited line spec `old` with `new` for that fact's `field`; rewrite:
  replace the citation text; keep: nothing to do; content-error: do nothing, list it in your report).
- The brief the checkers had, for context: `/home/yaroslavvb/claude/work/chip-check-1014/brief.md`.

## Where text comes from (fix the source, never a generated file)

Generated, never edit by hand: `docs/reports/2026-09-27-et-soc1-chip-diagram.html`,
`docs/reports/2026-09-28-et-soc1-memory-levels.html`, `docs/reports/data/2026-09-27-chip-diagram/facts.json`,
`docs/reports/data/2026-09-28-memory-levels/facts.json`, `docs/reports/ladder-img/ladder-data.json`,
`docs/reports/data/2026-10-01-ladder/ladder.json`, `docs/reports/sources/circuitkit.js` (copied from the memory levels'
kit by `research/make_circuitkit.py`).

Live builders (edit the builder, then run it to regenerate its own output, and check `git diff` of that output shows
only your intended change): `research/build_layout_facts.py` (facts-layout.json, layout.json), `research/build_facts_v2.py`
(facts-v2.json), `research/make_asks.py` (asks.json), `research/build_inside.py` (inside.json, research-inside.md),
`research/build_outside.py` (outside.json) in `docs/reports/data/2026-09-27-chip-diagram/`; the ladder's
`research/build_process.py`, `build_particles.py`, `build_studio45.py`, `build_circuits.py` in
`docs/reports/data/2026-10-01-ladder/`; the memory levels' `research/build_facts_{l1,l2,l3,dram,scp}.py` in
`docs/reports/data/2026-09-28-memory-levels/` (build_facts_l1.py writes `../facts-l1.json`: copy it over
`research/facts-l1.json`, or better, fix its OUT to write `research/facts-l1.json`).

Record-only builders (their OUT is an old scratchpad): `research/build_facts_arch.py` and `research/build_facts_numbers.py`.
Their facts live in `research/facts-arch.json` and `research/facts-numbers.json`: edit the JSON (keep its formatting:
`json.dump(..., indent=1, ensure_ascii=False)` reproduces it; check with `git diff`) and make the same edit in the record
builder so the two stay in step.

Dicts inside `docs/reports/data/2026-09-27-chip-diagram/build_facts.py` (ADD, AMEND, AMEND2, AMEND3, BC, N, COMP) and
`docs/reports/data/2026-09-28-memory-levels/build_facts.py` (its amendments) are sources too. The N table pairs each
displayed number with a fact and asserts that its text occurs in the fact's statement (`rounds_to`): when a statement's
number changes, change its N row with it. `build_ladder.py`'s num table does the same for the ladder.

`docs/reports/sources/circuitkit.js` is the memory levels' kit: fix `docs/reports/sources/memory-levels.script.js` (and
`research/circuitkit.head.js`/`circuitkit.tail.js` for the chip's own additions), then run
`python3 docs/reports/data/2026-09-27-chip-diagram/research/make_circuitkit.py` and its `--check`.

## Rules

- Edit only the files your group owns (listed in your work file). If a fix needs a file you do not own, do not touch it:
  say so in your report.
- Do not run the page builds or the chip's or memory levels' `build_facts.py`: the whole chain runs once, after every
  fixer is done. Running your own live builders is fine and expected.
- Knowledge-base files (`docs/findings/*.md`, `docs/et-soc1-notes.md`, `docs/energy-manual/*.md`) are cited by line:
  edit them only within existing lines, never adding or removing a line.
- Keep the page's voice: plain declarative English, numbers with their units, the same terms the page uses. A fix that
  changes a measured or documented number cites its source in the fact's source. Facts keep their ids.
- Where a fix says "or" (two ways), pick the one that is simpler and keeps the drawing and the page's behaviour intact.
- If you find that a fix is wrong when you look at the evidence yourself, do not apply it: report why.
- Bash: multi-line or looping scripts go in a file you write (under `/home/yaroslavvb/claude/work/chip-check-1014/fixes/<group>-work/`)
  and run as `python3 FILE` or `bash FILE`; never `bash -c`; `rm` only literal absolute paths; no background `&`; never
  touch the cards. Run Python with `python3 -I` when it reads downloaded files.
- Report: for every item, applied / partly applied / not applied, with the file:line of each change and why for anything
  not applied; for citations, how many remaps and rewrites you applied.
