export const meta = {
  name: 'chip-diagram-citations',
  description: 'Settle every drifted line citation in the chip diagram facts: four readers, each a batch, each line checked by reading it',
  phases: [{ title: 'Citations', detail: 'four batches of line citations, each adjudicated against the file at HEAD' }],
}
const W = '/home/yaroslavvb/claude/work/chip-check-1014'
const REPO = '/home/yaroslavvb/claude/et-soc1-prototyping'
const BATCHES = ['b1-claims-a', 'b2-claims-b', 'b3-docs', 'b4-code']
const SCHEMA = {
  type: 'object',
  properties: {
    batch: { type: 'string' },
    rows: { type: 'array', items: { type: 'object', properties: {
      fact: { type: 'string' },
      field: { type: 'string', enum: ['source', 'note'] },
      path: { type: 'string' },
      old: { type: 'string', description: 'the line spec as cited now, e.g. "366, 409"' },
      action: { type: 'string', enum: ['keep', 'remap', 'rewrite', 'content-error'] },
      new: { type: 'string', description: 'remap: the new line spec; rewrite: the replacement citation text; else empty' },
      head_quote: { type: 'string', description: 'the text at HEAD of the new (or kept) lines, abridged to 200 characters' },
      reason: { type: 'string' },
    }, required: ['fact', 'field', 'path', 'old', 'action', 'new', 'head_quote', 'reason'] } },
    other: { type: 'array', items: { type: 'string' }, description: 'line citations found outside the facts (scales, asks, outside meta, panel text) that are wrong, with where and the fix' },
  },
  required: ['batch', 'rows', 'other'],
}
const prompt = b => `You are settling line-number citations in the facts of the published page "The ET-SoC-1, interactively" (the chip diagram), built from the lab repository ${REPO} (main at bd8e731a; read-only for you: never edit a file there).

The page promises that every fact has a source, often a repository file and line ("docs/findings/05-claims.md:366, 409"). Many of those files have grown since 26-30 Sep, when the citations were written, so many cited lines now hold other text. A tool (${W}/citecheck.py) scored each citation against the fact and proposed new lines; its proposals are often right but not always (it can pick a duplicated row, miss a row whose values were superseded by a later row with the corrected numbers, or fail on HTML and code). Your batch: ${W}/cites/${b}.json, one object per citation: fact id, field (source or note), path, cited (the line spec), status (drifted, better-elsewhere, weak, ok), proposed, how, the old and new text, better_elsewhere.

For each citation:
1. Read the fact in full: python3 -I -c "import json; d={**json.load(open('${REPO}/docs/reports/data/2026-09-27-chip-diagram/facts.json'))['facts'], **json.load(open('${REPO}/docs/reports/ladder-img/ladder-data.json'))['facts']}; print(json.dumps(d['FACT_ID'], indent=1, ensure_ascii=False))" (put the id in).
2. Read the cited lines at HEAD (sed -n 'N,Mp' FILE) and the proposed ones, with some context.
3. Decide: keep (the cited lines at HEAD support the fact as cited), remap (give the line spec at HEAD that holds what the fact cites; for the claims ledger prefer the current row with the values the fact states over a superseded row), rewrite (no single line range fits, e.g. a section: give the replacement citation text), or content-error (no line of the file supports the fact at all: say so, with what the file does say). Quote the HEAD text you rely on.
Keep the same number of ranges as the citation where you can (a citation "366, 409" with two rows becomes two rows).

Also look for line citations outside the facts that a reader sees: in ${REPO}/docs/reports/data/2026-09-27-chip-diagram/facts.json outside the "facts" block (the "outside" block's clock_source, "scales", "asks", "comp" text) and in ${REPO}/docs/reports/sources/chip-diagram.script.js prose, only for files in your batch's paths; report wrong ones in "other".

Bash rules: a multi-line or looping script goes in a file you write under ${W}/cites/${b}-work/ and run as python3 FILE; never bash -c; rm only literal absolute paths; no background &. Return every citation of your batch in "rows", in the batch's order.`
const res = await parallel(BATCHES.map(b => () => agent(prompt(b), { label: `cites:${b}`, phase: 'Citations', schema: SCHEMA })))
return res
