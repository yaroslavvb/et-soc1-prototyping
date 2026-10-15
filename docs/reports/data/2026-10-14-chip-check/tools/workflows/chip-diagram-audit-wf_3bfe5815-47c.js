export const meta = {
  name: 'chip-diagram-audit',
  description: 'Audit the rebuilt chip diagram: every verified fix landed and is right, every changed text is explained, nothing new is wrong',
  phases: [{ title: 'Audit', detail: 'five auditors over the crawl diff of the rebuilt page' }],
}
const W = '/home/yaroslavvb/claude/work/chip-check-1014'
const GROUPS = [
  { g: 'a1-chip', what: 'the die, the mesh, the shire and the minion (scales and their facts)' },
  { g: 'a2-flows', what: 'the memory system, messaging, the host link, power and energy, and the eleven flows (their stages, captions and panels)' },
  { g: 'a3-deep', what: 'the memory system in the deep zoom and the textbook circuits (their drawings above all)' },
  { g: 'a4-outer', what: 'the device, the particles and the levels outside the chip' },
  { g: 'a5-prose', what: 'the page\'s prose, the tour, the asks, the electrons table, the page\'s interaction fixes, and the 3D companion\'s five fixes' },
]
const SCHEMA = {
  type: 'object',
  properties: {
    group: { type: 'string' },
    fixes: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' }, status: { type: 'string', enum: ['landed', 'partly', 'missing', 'wrong'] }, note: { type: 'string' },
    }, required: ['key', 'status', 'note'] } },
    unexplained: { type: 'array', items: { type: 'object', properties: {
      section: { type: 'string' }, what: { type: 'string' }, verdict: { type: 'string', enum: ['regression', 'benign', 'unsure'] }, fix: { type: 'string' },
    }, required: ['section', 'what', 'verdict', 'fix'] } },
    new_errors: { type: 'array', items: { type: 'object', properties: {
      where: { type: 'string' }, problem: { type: 'string' }, evidence: { type: 'string' }, source_location: { type: 'string' }, fix: { type: 'string' },
    }, required: ['where', 'problem', 'evidence', 'source_location', 'fix'] } },
    notes: { type: 'string' },
  },
  required: ['group', 'fixes', 'unexplained', 'new_errors', 'notes'],
}
const prompt = a => `You are auditor ${a.g} of the rebuilt chip diagram ("The ET-SoC-1, interactively"). Today 97 verified findings and 40 observations from another agent's audit (Codex) were fixed in the sources of the lab repository /home/yaroslavvb/claude/et-soc1-prototyping (uncommitted: git diff there shows every change), and both pages were rebuilt (docs/reports/2026-09-27-et-soc1-chip-diagram.html, and the memory levels page, which shares the deep zoom). Your scope: ${a.what}. You change no file; you report.

Background: ${W}/brief.md (what the page is, where text comes from, the ground truth) and ${W}/fixbrief.md (how fixes were applied).

Inputs:
- ${W}/audit/${a.g}.md: every text a reader sees that changed in your scope, as a word diff ([-old-] {+new+}), one section per panel, caption, tour slide or fact (made by crawling the page this morning and again after the rebuild).
- ${W}/audit/${a.g}-expected.json: the fixes in your scope: our findings (key, what the page said, what is true, the fix) and the Codex observations decided "implement" or "covered".
- The two crawls in full: ${W}/crawl/out/ (before) and ${W}/crawl/after/ (after): static.json, scales.json, flows.json, tour.json. Screenshots: before in ${W}/crawl/out/shots/, after in ${W}/crawl/after/shots/ (being written as you start; if one you need is missing, wait a minute and look again). Look at the after screenshots for every fix that changes a drawing.

Do three things:
1. For every expected fix in your scope: did it land, and is the new text or drawing right (check it against the evidence, as a skeptic would)? Status landed, partly, missing or wrong, with a note.
2. For every diff section: is the change explained by a fix (or by a fact's corrected citation)? List the ones that are not, as regression (a change for the worse), benign or unsure, with a fix where needed.
3. Read the new texts as a careful reader: report any new error (wrong number, wrong unit, broken sentence, a claim the evidence does not support, a contradiction with another part of the page), with its source location and an exact fix.${a.g === 'a5-prose' ? `
Also the 3D companion (docs/reports/chip-3d.html, rebuilt today from docs/reports/sources/chip-3d/ by node scripts/build-chip-3d.mjs): check that its five Codex fixes (I02, I03, I10, I11, I12, in your expected list) are in the sources and in the built page, and run its regression scripts in docs/reports/data/2026-10-14-chip-3d/ if they run locally against the built file (read each script's header first; never start a long or networked run).` : ''}

Rules: read-only (no edits in the repository); never touch the cards; Bash scripts in a file under ${W}/audit/${a.g}-work/, run as python3 FILE or node FILE; never bash -c; no background &. Precision over volume: report what is wrong, not style.`
const res = await parallel(GROUPS.map(a => () => agent(prompt(a), { label: `audit:${a.g}`, phase: 'Audit', schema: SCHEMA })))
return res
