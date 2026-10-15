export const meta = {
  name: 'chip-diagram-fix',
  description: 'Apply the verified fixes and the settled line citations to the chip diagram sources: six fixers, each owning its own files',
  phases: [{ title: 'Fix', detail: 'six groups of source files, edited in parallel, no file shared' }],
}
const W = '/home/yaroslavvb/claude/work/chip-check-1014'
const GROUPS = ['A1-archfacts', 'A2-numfacts', 'B-deepzoom', 'C-pagescript', 'D-memlevels', 'E-ladder']
const SCHEMA = {
  type: 'object',
  properties: {
    group: { type: 'string' },
    items: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' },
      status: { type: 'string', enum: ['applied', 'partly', 'not-applied', 'not-mine'] },
      changes: { type: 'array', items: { type: 'string' }, description: 'file:line and what changed' },
      note: { type: 'string' },
    }, required: ['key', 'status', 'changes', 'note'] } },
    citations: { type: 'object', properties: { applied: { type: 'integer' }, skipped: { type: 'integer' }, notes: { type: 'string' } }, required: ['applied', 'skipped', 'notes'] },
    builders_run: { type: 'array', items: { type: 'string' } },
    needs_other_groups: { type: 'array', items: { type: 'string' }, description: 'edits a fix needs in files you do not own: file and exact change' },
    notes: { type: 'string' },
  },
  required: ['group', 'items', 'citations', 'builders_run', 'needs_other_groups', 'notes'],
}
const prompt = g => `You are fixer ${g} for the chip diagram. Read ${W}/fixbrief.md first, in full: it says what you may edit, how the page is built and the rules. Your work list is ${W}/fixes/${g}.json: its "owns" lists the files (or path prefixes) you own; its "items" are the verified findings to apply (use each item's "fix", the skeptic's, which supersedes "checker_fix"; items with verdict "unverified" you confirm from their evidence before applying); its "citations" are the settled line citations of facts your files generate (apply "remap" and "rewrite" rows; an entry with "other" is a citation outside the facts, to fix if it is in your files).

Work in the repository /home/yaroslavvb/claude/et-soc1-prototyping (main). Five other fixers edit other files there at the same time: touch only your own files. When you are done, run git diff --stat on your files and check that each of your live builders, run once more, leaves its output unchanged (a fixed point), and that python3 -m json.tool parses every JSON you edited.

Return the structured report: every item with its status and the file:line of each change; how many citations you applied and skipped (and why); the builders you ran; and, in needs_other_groups, every edit a fix needs in a file you do not own (the file and the exact change), so it can be routed.`
const res = await parallel(GROUPS.map(g => () => agent(prompt(g), { label: `fix:${g}`, phase: 'Fix', schema: SCHEMA })))
return res
