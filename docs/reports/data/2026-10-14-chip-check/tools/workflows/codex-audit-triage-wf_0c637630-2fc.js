export const meta = {
  name: 'codex-audit-triage',
  description: 'Check each of Codex\'s 68 chip-diagram audit observations against the sources and decide: covered, implement (with an exact fix), owner decision, or reject',
  phases: [{ title: 'Triage', detail: 'five readers, each a block of observations, each checked against the ground truth' }],
}
const W = '/home/yaroslavvb/claude/work/chip-check-1014'
const BATCHES = [
  { name: 'TA', ids: ['T01', 'T02', 'T03', 'T04', 'T05', 'T06', 'T07', 'T08', 'T09', 'T10'], what: 'hardware facts and units' },
  { name: 'TB', ids: ['T11', 'T12', 'T13', 'T14', 'T15', 'T16', 'T17', 'T18', 'T19', 'T20'], what: 'notation, the device and the teaching circuits' },
  { name: 'LA', ids: ['L01', 'L02', 'L03', 'L04', 'L05', 'L06', 'L07', 'L08', 'L09', 'L10', 'L11', 'L12', 'L13', 'L14', 'L15'], what: 'charge, particles and the geometry of the outer levels' },
  { name: 'LB', ids: ['L16', 'L17', 'L18', 'L19', 'L20', 'L21', 'L22', 'L23', 'L24', 'L25', 'L26', 'L27', 'L28', 'L29'], what: 'particle physics, the outer ladder, sizes and dates' },
  { name: 'IR', ids: ['I01', 'I02', 'I03', 'I04', 'I05', 'I06', 'I07', 'I08', 'I09', 'I10', 'I11', 'I12', 'I13', 'I14', 'I15', 'I16', 'R01', 'R02', 'R03'], what: 'interaction, mobile, the 3D companion, reliability and page metadata' },
]
const SCHEMA = {
  type: 'object',
  properties: {
    batch: { type: 'string' },
    items: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' },
      decision: { type: 'string', enum: ['covered', 'implement', 'owner-decision', 'reject', 'stale'] },
      covered_by: { type: 'string', description: 'our finding key(s) when covered (or partly: say what is left, and decide implement for the rest)' },
      severity: { type: 'string', enum: ['major', 'minor', 'none'] },
      reason: { type: 'string' },
      evidence: { type: 'array', items: { type: 'object', properties: { path: { type: 'string' }, locator: { type: 'string' }, quote: { type: 'string' } }, required: ['path', 'locator', 'quote'] } },
      fix: { type: 'string', description: 'implement: the exact change in the SOURCE files (old -> new text, or the code change), as a fixer would apply it' },
      fix_files: { type: 'array', items: { type: 'string' } },
    }, required: ['id', 'decision', 'covered_by', 'severity', 'reason', 'evidence', 'fix', 'fix_files'] } },
  },
  required: ['batch', 'items'],
}
const prompt = b => `Another agent (Codex) audited the published chip diagram "The ET-SoC-1, interactively" (spacesheep @yaroslavvb/et-soc1-chip-diagram, published version c753607a8c79) and its linked 3D companion, and wrote 68 observations. The owner asked: "Go through the suggestions/fixes and implement everything which is appropriate." You decide, for each observation in your block, whether and how. You change no file yourself.

Read first: ${W}/brief.md (what the page is, where its text comes from, the ground truth, the rules) and ${W}/fixbrief.md (where each kind of fix must go: the source files, never the generated ones; the live and record-only builders).

Your block (${b.what}): ${b.ids.join(', ')}. The observations, each with Codex's evidence and suggested fix: ${W}/codex/items.json (ids T.., I.., L.., R..); the whole report as text: ${W}/codex/audit.txt. Codex's line numbers ("index.html:4182") refer to the published page, saved at ${W}/codex/snapshot-c753607a8c79.html: grep its text there, then find the source that generates it.

Read the sources at the commit that was audited, in the pristine worktree ${W}/wt-buildtest (bd8e731a; the main checkout is being edited by fixers right now, so do not read the chip diagram's sources there). The 3D companion was rebuilt since the audit: read its current sources in /home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/sources/chip-3d/ and docs/reports/chip-3d.html (built by scripts/build-chip-3d.mjs; nobody is editing them now).

A separate check of this page already found and verified 97 errors, now being fixed: ${W}/codex/our-findings-index.json (key, where, what the page says, the fix). For each observation:
- covered: our finding already fixes it (name the key; if it covers only part, say what is left and decide that part separately);
- implement: a real error (check it against the ground truth yourself, as a skeptic would; Codex's arithmetic and readings can be wrong), or a contained bug in the page's behaviour (a broken connection in a circuit drawing, a mislabelled sign, a control that does the wrong thing, a stale count or label) with a clear, local fix. Give the exact fix in the source files and list them;
- owner-decision: a redesign, a new feature, a change of style or of the page's conventions, or anything that contradicts a choice the owner made (the levels above the rack are an easter egg by his decision; the page's voice and layout are his) — say in one line what it would take;
- reject: Codex is wrong (say why, with evidence) or the change would make the page worse;
- stale: it no longer applies to the current sources.
Keep the page's verified strengths intact (Codex itself lists: compressor arithmetic, Booth recoding table, SECDED matrix, rounding rule, LPDDR4 DBI polarity, the documented L1 split).

Bash rules: multi-line or looping scripts go in a file under ${W}/codex/${b.name}-work/ and run as python3 FILE or node FILE; never bash -c; rm only literal absolute paths; no background &; never touch the cards. Return every observation of your block.`
const res = await parallel(BATCHES.map(b => () => agent(prompt(b), { label: `triage:${b.name}`, phase: 'Triage', schema: SCHEMA })))
return res
