export const meta = {
  name: 'chip-diagram-fix-resume',
  description: 'Resume the four interrupted chip diagram fixers: finish their verified fixes and citations, never applying one twice',
  phases: [{ title: 'Fix', detail: 'four groups of source files, resumed from what is already in the tree' }],
}
const W = '/home/yaroslavvb/claude/work/chip-check-1014'
const GROUPS = ['A2-numfacts', 'B-deepzoom', 'C-pagescript', 'D-memlevels']
const SCHEMA = {
  type: 'object',
  properties: {
    group: { type: 'string' },
    items: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' },
      status: { type: 'string', enum: ['applied', 'already-applied', 'partly', 'not-applied', 'not-mine'] },
      changes: { type: 'array', items: { type: 'string' } },
      note: { type: 'string' },
    }, required: ['key', 'status', 'changes', 'note'] } },
    citations: { type: 'object', properties: { applied: { type: 'integer' }, skipped: { type: 'integer' }, notes: { type: 'string' } }, required: ['applied', 'skipped', 'notes'] },
    builders_run: { type: 'array', items: { type: 'string' } },
    needs_other_groups: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['group', 'items', 'citations', 'builders_run', 'needs_other_groups', 'notes'],
}
const prompt = g => `You are fixer ${g} for the chip diagram, resuming. Read ${W}/fixbrief.md first, in full: what you may edit, how the page is built, the rules. Your work list is ${W}/fixes/${g}.json: "owns" lists your files; "items" are the verified findings to apply (use each item's "fix", the skeptic's, which supersedes "checker_fix"; items with verdict "unverified" you confirm from their evidence before applying); "citations" are settled line citations of facts your files generate (apply "remap" and "rewrite" rows; an "other" entry is a citation outside the facts, to fix if it is in your files); "routed" are edits that other fixers found your files need (apply them too).

An earlier run of your group was cut off by a usage limit partway through, so your files may already hold part of your work: git diff (in /home/yaroslavvb/claude/et-soc1-prototyping) shows it. Before each item or citation, check whether it is already in place (the new text present, the old text gone): never apply anything twice, and do not undo what is there unless it is wrong. Keep a progress log as you go: append one line per item and per batch of citations to ${W}/fixes/${g}-progress.md (key, applied or already-applied or skipped, file:line), so that a later run can continue from it if you are cut off too. Two other groups (A1 and E) have finished; two of the four groups now resuming work in the same checkout at the same time as you: touch only your own files.

When you are done: git diff --stat on your files; run each of your live builders once more and check its output is unchanged (a fixed point); check that every JSON you edited parses (python3 -m json.tool). Return the structured report: every item (applied, already-applied, partly, not-applied, not-mine) with the file:line of each change; the citations applied and skipped; the builders you ran; and every edit a fix needs in a file you do not own (file and exact change).`
const res = await parallel(GROUPS.map(g => () => agent(prompt(g), { label: `fix2:${g}`, phase: 'Fix', schema: SCHEMA })))
return res
