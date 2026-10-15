export const meta = {
  name: 'codex-fix',
  description: 'Apply the Codex audit observations the triage decided to implement, on top of the first fix pass: four fixers, each owning its own files',
  phases: [{ title: 'Fix', detail: 'page script, ladder, 3D companion, and the remaining facts files' }],
}
const W = '/home/yaroslavvb/claude/work/chip-check-1014'
const GROUPS = ['C-pagescript', 'E-ladder', 'F-3d', 'G-small']
const SCHEMA = {
  type: 'object',
  properties: {
    group: { type: 'string' },
    items: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' },
      status: { type: 'string', enum: ['applied', 'already-applied', 'partly', 'not-applied', 'not-mine'] },
      changes: { type: 'array', items: { type: 'string' } },
      note: { type: 'string' },
    }, required: ['id', 'status', 'changes', 'note'] } },
    builders_run: { type: 'array', items: { type: 'string' } },
    needs_other_groups: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['group', 'items', 'builders_run', 'needs_other_groups', 'notes'],
}
const prompt = g => `You are fixer ${g}, second pass, for the chip diagram. Read ${W}/fixbrief.md first, in full: what you may edit, how the page is built, the rules. A first pass has already applied 97 verified findings and 181 line citations to the sources in /home/yaroslavvb/claude/et-soc1-prototyping (main, uncommitted, git diff shows them): never undo them. This pass applies observations from an audit by another agent (Codex), each checked by a reader and decided "implement": your list is ${W}/fixes/codex-${g}.json ("owns": your files; "items": each with id, the reader's reason, evidence and "fix", which gives the exact change; "fix_files"). Some items also touch files of other groups: do only your part, exactly as written, keeping names of new keys and numbers as the fix gives them. Where a first-pass fix already changed the text an item's "Old" quotes, apply the item's intent to the current text, and say so.
${g === 'F-3d' ? `
You own the 3D companion's sources: docs/reports/sources/chip-3d/ (app.js, viewer.js, models.js, content.js, shell.html, style.css). Do not run npm ci or the build (scripts/build-chip-3d.mjs needs esbuild and three, which are not installed; the build runs after you). Check your edits with node --check where a file is plain JavaScript.` : ''}${g === 'G-small' ? `
You own the files of four first-pass groups at once (A1 architecture facts and build_facts.py, A2 numbers and layout facts, B the deep zoom's inside and outside builders, D the memory levels' research files and the memory levels' kit in memory-levels.script.js with make_circuitkit.py): the "owns" list has them all.` : ''}
Keep a progress log: append one line per item to ${W}/fixes/codex-${g}-progress.md as you finish it, so that a later run can continue if you are cut off. Three other fixers edit other files in the same checkout at the same time: touch only your own. Do not run the page builds or either build_facts.py; running your own live builders is fine.

When you are done: git diff --stat on your files, run each of your live builders once more (a fixed point), and check every JSON you edited parses. Return the structured report: every item with status and the file:line of each change, the builders you ran, and every edit an item needs in a file you do not own.`
const res = await parallel(GROUPS.map(g => () => agent(prompt(g), { label: `codexfix:${g}`, phase: 'Fix', schema: SCHEMA })))
return res
