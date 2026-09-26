#!/usr/bin/env python3
"""Join the reducers' verdicts to the page claims they test (the version-3 page update's map):

    tools/claims-v3/pagemap.py docs/reports/data/2026-09-25-claims-v3/results \
        docs/reports/data/2026-09-25-claims-v3/results/pagemap.md docs/reports/data/2026-09-25-claims-v3/results/pagemap.json

For every page: each claim of plan3.json.gz (id, anchor, text, planned page action) with the items of every reducer
output in the results folder that test it (their `claims` lists), their registered outcome, their all-cards outcome
and reading. JSON files that are not reducer outputs (.runs.json, .passes.json, inputs/) are skipped."""
import gzip, json, os, sys, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
plan = json.load(gzip.open(f'{ROOT}/docs/reports/data/2026-09-25-claims-v3/plan3.json.gz'))
claims = {c['id']: c for c in plan['claims']}
rdir, out_md = sys.argv[1], sys.argv[2]
out_json = sys.argv[3] if len(sys.argv) > 3 else None
by_claim = collections.defaultdict(list)
unmapped = []
for f in sorted(os.listdir(rdir)):
    if not f.endswith('.json') or f.endswith(('.runs.json', '.passes.json')):
        continue
    d = json.load(open(os.path.join(rdir, f)))
    items = d if isinstance(d, list) else d.get('items') or d.get('verdicts') or d.get('results') or []
    for it in items:
        if not isinstance(it, dict) or 'item' not in it:
            continue
        ac = it.get('all_cards')
        rec = {'exp': f[:-5], 'item': it['item'], 'part': it.get('part'), 'outcome': it.get('outcome'),
               'all_cards': ac.get('outcome') if isinstance(ac, dict) else ac,
               'reading': it.get('reading'), 'reading_all_cards': it.get('reading_all_cards')
               or (ac.get('reading') if isinstance(ac, dict) else None)}
        cl = it.get('claims')
        ids = cl if isinstance(cl, list) else []
        if not ids:
            unmapped.append(rec | {'claims_text': cl})
        for cid in ids:
            by_claim[cid].append(rec)
pages = collections.defaultdict(list)
for cid, recs in by_claim.items():
    c = claims.get(cid, {'page': '?', 'anchor': '?', 'text': '(claim not in plan3.json)'})
    pages[c.get('page', '?')].append((cid, c, recs))
L = [f'# Page map: verdicts from {rdir}', '']
for page in sorted(pages):
    L.append(f'## {page} ({len(pages[page])} claims)')
    for cid, c, recs in sorted(pages[page], key=lambda x: x[0]):
        L.append(f'- **{cid}** [{c.get("anchor")}] {c.get("text")}')
        if c.get('page_action'):
            L.append(f'  - planned: {c.get("page_action")}')
        for r in recs:
            part = f' ({r["part"]})' if r.get('part') else ''
            L.append(f'  - {r["item"]}{part}: registered **{r["outcome"]}**, all cards **{r["all_cards"]}** — '
                     f'{(r.get("reading_all_cards") or r.get("reading") or "")[:300]}')
    L.append('')
if unmapped:
    L.append('## Items without claim ids')
    for r in unmapped:
        L.append(f'- {r["exp"]} {r["item"]}: {r["outcome"]} / {r["all_cards"]}; claims: {str(r["claims_text"])[:200]}')
open(out_md, 'w').write('\n'.join(L) + '\n')
if out_json:
    json.dump({p: [{'id': cid, 'claim': c, 'verdicts': recs} for cid, c, recs in v] for p, v in pages.items()},
              open(out_json, 'w'), indent=1)
cnt = collections.Counter((r['all_cards']) for recs in by_claim.values() for r in recs)
print(f'{len(by_claim)} claims on {len(pages)} pages; {len(unmapped)} items without ids; all-cards outcomes {dict(cnt)}')
