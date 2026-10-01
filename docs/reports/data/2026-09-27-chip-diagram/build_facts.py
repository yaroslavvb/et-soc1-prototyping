#!/usr/bin/env python3
"""Build facts.json for the chip diagram (docs/reports/sources/chip-diagram.*) from the three research fact files.

    python3 docs/reports/data/2026-09-27-chip-diagram/build_facts.py

Inputs, in research/ next to this script (copied from the session that made them, 27 Sep 2026):
  facts-arch.json    164 facts: the chip's hierarchy, caches, mesh, DRAM and clocks (build_facts_arch.py)
  facts-layout.json   81 facts: die, tile pitch, shire placement, memory-shire fit (build_layout_facts.py)
  facts-numbers.json 136 facts: latency, bandwidth, energy, power, E48 gathers (build_facts_numbers.py)
  layout.json        the logical 6x6 map, the inferred die view, memory-shire positions (build_layout_facts.py)
Each fact has a source (a repo file with line or field, a manual PDF page, or a source file:line) and a kind
(measured, spec, derived, inferred). The builders read the repository directly; they are kept in research/ as a record.

The second version (27 Sep, the owner's feedback) adds two inputs, also in research/:
  facts-v2.json      27 facts read from the data files by build_facts_v2.py: the PCIe link and the launch path timed on
                     three cards (docs/reports/data/2026-09-27-pcie), the firmware's shire map against the measured one
                     (firmware_map.json), the tensor unit's data flow, the same matmul's watts and heat by data, the hot
                     line and the allreduce tree; with the rows of printed numbers they need (num), added to N below
  asks.json          what would settle each inferred part and the hub's row that asks for it (make_asks.py); the rows'
                     titles are read from docs/reports/sources/limits-of-observability.data.json (.improvements)

The page's review (27 Sep) added, here and not in research/: ADD, six facts written for the page, each with its
source (board watts of the three-card matmul, the tensor instructions running on the vector lanes, a minion's 256-bit
ET-Link width, the memory-shire fit's three-card check, why memory shire 2 has one place left, and the LPDDR4X pairing
as inferred); AMEND, the pooled cycles per instruction of DRAM scatters, and after the second version's review the
PCIe facts (bw-pcie and pcie.link say the link was timed; ridge.levels gives the PCIe ridge at the measured DMA rate,
computed here from ../2026-09-27-pcie/pcie.json) and the notes of the layout facts the firmware's map settled (L32,
L33, L34, mesh.orientation, L37); CARDS, card coverage set by hand where the card string's aside names a card that
was not measured.

The broadcast flow (28 Sep, flow B, the owner's request from the page's Talk tab) adds BC, eight facts written for it,
each with its source: the TensorBroadcast rule (PRM §9.4); the 1 KB allreduce, read here from the version-3 raw files
(../2026-09-25-claims-v3/raw/<card>/lat/p*/noc/*allreduce-c32.jsonl, each card's median over its passes); that the
broadcast half was never timed alone; the shire cache's rule for one line read by many; the hot line's one-per-shire
pollers; the ESR broadcast and the IPI; the launch's multicast (firmware source); and what the other 31 shires add to
a queued launch (computed from ../2026-09-27-pcie/pcie.json).

The major pass (29 Sep) adds the measurements of the hub's rungs 31-36, each read from its reduction with its
verdicts asserted: the routing order (E56, fact L104) from ../2026-09-29-nocr/raw/<card>/summary.json; where a host
copy lands (E55, the new fact pcie.write-l3) and which DMA commands collide (pcie.conc) from
../2026-09-29-pcie2/pcie2.json and its dev-aifoundry1-c1.md; the DRAM address map (L50, now measured) and the L2's
hold on TensorLoad lines (minion.tensor-cache-path) from ../2026-09-29-memp2/val-aifoundry3/memp2.json and
dev-aifoundry1-c1/memp2.json (AMEND2, AMEND3). Since the evening of 29 September the same three experiments' third card,
aifoundry2 (run after the DVFS validation there ended), comes in too: its nocr summary.json, pcie2.json's
cards.aifoundry2 and ../2026-09-29-memp2/val-aifoundry2/memp2.json, where R33a missed one condition (PA[17]).

The deep zoom (30 Sep, the owner's request: zoom out to the universe and in to the circuits; DESIGN.md of the
session in ~/claude/work/chipzoom) adds, through research/deepzoom.py: research/inside.json (what is inside every
part, down to the silicon crystal; build_inside.py), research/outside.json (the 18 levels from the package to "beyond
what we can see"; build_outside.py) and research/outside-geo.json (map outlines; make_geo.py); the image manifest of
../../chip-diagram-img/ (sha256; make_rack_photo.py makes rack.webp from the original kept outside the repository);
and the memory levels' facts and numbers that ../../sources/circuitkit.js cites (make_circuitkit.py copies that
page's drawings). Output blocks: scales, geo, img, mlnum, mladdr, onum (the numbers the new drawings print, each
checked against its fact), outside; facts gain in.*, out.*, size.* and ml:* ids, and the page's facts carry only the
fields it reads.

Output, facts.json:
  facts  the facts the page uses, by id, with one page link field (`url`, a spacesheep URL, or null), the lab cards
         each one covers (`cards`: a2, a3, a1c1) and, for the CARDS entries, the text shown for them (`cards_txt`)
  num    every number the page prints outside a fact's own statement: {v, t, u, f}. `f` is the fact it comes from; the
         build asserts that the printed text t occurs in that fact's statement (or equals its value), so no number on
         the page lacks a source. A row may give a rounding to print instead (sixth field); the build checks that each
         of its numbers rounds from the statement's, and keeps the statement's text as `src_t`
  comp   the facts each component's and each flow's details panel lists
  layout layout.json as is
  asks   research/asks.json as is; rungs: the hub rows they link to ({id: {rung, what, status}})
"""
import glob
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, 'research')

ALL = {}
for fn, tag in (('facts-arch.json', 'arch'), ('facts-layout.json', 'layout'), ('facts-numbers.json', 'numbers')):
    for f in json.load(open(os.path.join(R, fn))):
        assert f['id'] not in ALL, 'duplicate fact id ' + f['id']
        f['set'] = tag
        ALL[f['id']] = f
layout = json.load(open(os.path.join(R, 'layout.json')))
# the second version (27 Sep): facts read from the data files by research/build_facts_v2.py (PCIe timed on three
# cards, the firmware's shire map, the tensor data flow, watts and heat by data, the hot line, the allreduce tree)
V2 = json.load(open(os.path.join(R, 'facts-v2.json')))
for f in V2['facts']:
    assert f['id'] not in ALL, 'duplicate fact id ' + f['id']
    f['set'] = 'v2'
    ALL[f['id']] = f
# what would settle each inferred or dashed part, and the hub's ask it links to (research/make_asks.py); the ask's
# title is read from the hub's own data so that the link text matches the row it lands on
ASKS = json.load(open(os.path.join(R, 'asks.json')))
HUBD = json.load(open(os.path.join(HERE, '..', '..', 'sources', 'limits-of-observability.data.json')))
RUNGS = {r['id']: {'rung': r['rung'], 'what': r['what'], 'status': r['status']} for r in HUBD['improvements'] if r.get('id')}
for a in ASKS:
    for k in [a.get('hub_anchor')] + a.get('also', []):
        if k and k not in RUNGS:
            raise SystemExit(f'ask {a["part"]}: no hub row {k}')

# ---- facts written for this page in its review (27 Sep 2026), each with its source. Kinds as in the research files.
MATMUL = 'https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency'
ADD = [
    {'id': 'mm-board-w', 'component': 'board', 'topic': 'power', 'kind': 'derived',
     'statement': 'Board power during the fp32 L2 matmul that runs at 9.51 TFLOP/s, idle before the run plus the watts '
                  'over idle: aifoundry2 33.3 + 25.7 = 59.0 W (die 80 °C), aifoundry3 26.0 + 24.4 = 50.4 W (62 °C), '
                  'aifoundry1-c1 41.83 + 27.25 = 69.1 W (75-76 °C): 50.4-69.1 W across the three cards (die 62-80 °C). '
                  '9.51 TFLOP/s over these is the 161, 189 and 138 GFLOP/s per W of the same run (138-189).',
     'value': 59.0, 'unit': 'W (aifoundry2)',
     'source': 'docs/findings/05-claims.md:418 (E37, MMB-c: docs/reports/data/2026-09-25-claims-v3/results/mmb.json '
               '.items[item=MMB-c].per_card.<card>["fp32-tensor-L2"].board_w, .idle_before_w, .mean, .die_c_mean) and :419 '
               '(MMB-d, GFLOP/s per W)',
     'card': 'aifoundry2, aifoundry3, aifoundry1-c1', 'page': 'Matmul efficiency', 'url': MATMUL,
     'note': 'The sum is this page\'s; 05-claims.md gives the watts over idle and the idle before each run. Idle power '
             'moves with the card and its temperature (26.0-41.8 W here).'},
    {'id': 'minion.vec-peak', 'component': 'minion', 'topic': 'compute', 'kind': 'spec',
     'statement': 'The tensor instructions run on the vector unit\'s own lanes: each of the 8 lanes holds the FMA '
                  '(TxFMA) and the two int8 multiply-add (IMA/TIMA) units, and state machines in the VPU sequence '
                  'the multi-cycle tensor operations on them. An 8-lane fmadd.ps does 16 FLOP per cycle, the same '
                  'fp32 peak as TensorFMA.',
     'value': 16, 'unit': 'fp32 FLOP per minion-cycle',
     'source': 'external/et-man/ET Preliminary Datasheet Rev 1.0.pdf, pdf p.8 (§2.1.1.2: TxFMA, a pair of IMA units '
               'and \'Finite state machines that generate long sequences of vector operations to implement '
               'multi-cycle tensor operations\'); external/core-et/docs/Minion VPU Specification.pdf, pdf p.11 (§2: '
               'TXFMA and two TIMA units per lane); scripts/ridge-points.py:46, 51 (fp32 TensorFMA and vec32 '
               'fmadd.ps, per_cycle 16 each)',
     'card': None, 'page': 'Ridge points', 'url': 'https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points', 'note': None},
    {'id': 'minion.etlink-width', 'component': 'minion', 'topic': 'interconnect', 'kind': 'spec',
     'statement': 'A minion\'s ET-Link request and response interfaces are 256 bits wide: the neighbourhood\'s '
                  'request datapath is 256 bits, up-converted to 512 bits only at its output to the shire, and a '
                  '512-bit response reaches the minion as two 256-bit halves.',
     'value': 256, 'unit': 'bits',
     'source': 'external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf, pdf p.15 (§4.3: \'The data size of the request '
               'datapath is 256 bits\' ... \'a final up-conversion to 512 bits\') and p.23 (§4.4.3: \'the Minion '
               'response interface is 256-bit wide\')',
     'card': None, 'page': None, 'url': None, 'note': None},
    {'id': 'ms-fit-3cards', 'component': 'memory shire', 'topic': 'placement', 'kind': 'measured',
     'statement': 'Left as fitted on aifoundry2 on 19 September (constant 91 and the memory-shire places, not '
                  'refitted), the DRAM latency model is within ±3 cycles for 93-97% of loads on all three cards: '
                  'aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% (5 passes each).',
     'value': 97.0, 'unit': '% of loads within ±3 cycles (aifoundry2)',
     'source': 'docs/findings/05-claims.md:404 (E35, MEM-P2: docs/reports/data/2026-09-25-claims-v3/results/mem.json '
               '[item=MEM-P2].per_card.<card>.tests.P2_dram_within3_frac)',
     'card': 'aifoundry2, aifoundry3, aifoundry1-c1', 'page': 'Anatomy of a memory access',
     'url': 'https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy', 'note': None},
    {'id': 'ms2-forced', 'component': 'memory shire', 'topic': 'placement', 'kind': 'derived',
     'statement': 'Memory shire 2\'s fit ties (3, -1), (5, -1) and (6, 0), but (5, -1) is a corner of the 8 × 6 grid, '
                  'and the corners are empty, while (6, 0) lies outside the grid: within the fit\'s assumptions '
                  '(3, -1) is the only place left.',
     'value': None, 'unit': None,
     'source': 'L42 (docs/reports/2026-09-19-et-soc1-memory-anatomy.html:778-780); external/et-man/ET Preliminary '
               'Datasheet Rev 1.0.pdf, pdf p.21 (§4: \'the corners of the grid are not occupied\')',
     'card': None, 'page': None, 'url': None,
     'note': 'The logical map is 6 rows (x = 0-5) by 8 columns (y = -1 to 6, the memory shires at y = -1 and 6).'},
    {'id': 'dram.pkg-pairing', 'component': 'memory', 'topic': 'placement', 'kind': 'inferred',
     'statement': 'Which two memory shires share each LPDDR4X device is not documented: the datasheet says only that '
                  'two memory shires communicate with each 64-bit device. The diagram pairs neighbouring memory '
                  'shires on each side (0 and 1, 2 and 3, 4 and 5, 6 and 7), after the block diagram\'s two LPDDR4X '
                  'blocks per side, on the inferred die placement.',
     'value': None, 'unit': None,
     'source': 'external/et-man/ET Preliminary Datasheet Rev 1.0.pdf, pdf p.30 (§7: \'Two Memshires communicate with '
               'each 64-bit LPDDR4X memory device\') and p.15 (Figure 2-6, fact L23)',
     'card': None, 'page': None, 'url': None, 'note': None},
]
for f in ADD:
    assert f['id'] not in ALL, 'duplicate fact id ' + f['id']
    f['set'] = 'page'
    ALL[f['id']] = f

# ---- the host link's ridge point at the measured DMA rate (27 Sep review): the fp32 peak (1,024 minions x 16 FLOP x
# 600 MHz: facts chip-minions, minion.vec-peak, op-600) over each card's measured host-to-device DMA rate, 256 MB
PCIE = json.load(open(os.path.join(HERE, '..', '2026-09-27-pcie', 'pcie.json')))
PEAK32 = 1024 * 16 * 600e6
H2D_DMA = [next(e for e in PCIE['bw'][c]['h2d']['dma'] if e['bytes'] == 268435456)['gbs']['mean'] for c in PCIE['cards']]
RIDGE_DMA = f'{PEAK32 / (max(H2D_DMA) * 1e9):,.0f}-{PEAK32 / (min(H2D_DMA) * 1e9):,.0f}'
H2D_RNG = f'{min(H2D_DMA):.2f}-{max(H2D_DMA):.2f}'

# ---- amendments to research facts (27 Sep review): the pooled figure the page prints, with its source. Keys: find and
# statement (a replacement in the statement), source (appended), and note, unit, kind (replaced)
AMEND = {
    # the link was timed on 27 September: the spec facts no longer say it never was, and stay the link's figure only
    'bw-pcie': {'find': 'host transfers have not been timed on these cards.',
                'statement': 'the transfers were timed on three cards on 27 September (facts pcie.h2d and pcie.d2h give '
                             'the measured rates).',
                'source': '; docs/reports/data/2026-09-27-pcie/pcie.json (27 Sep)',
                'note': 'The link figure, not a measurement: measured on 27 September (facts pcie.h2d, pcie.d2h). The '
                        'ridge row of 05-claims.md that called it never measured predates that.'},
    'pcie.link': {'find': 'host transfer bandwidth was never measured here.',
                  'statement': 'the transfers were timed on three cards on 27 September (facts pcie.negotiated, pcie.h2d).',
                  'source': '; docs/reports/data/2026-09-27-pcie/pcie.json (27 Sep)',
                  'unit': 'GB/s (link figure)'},
    # the PCIe ridge: 624 is the link figure's; the measured DMA rate gives its own (computed above from pcie.json)
    'ridge.levels': {'find': 'PCIe 624 (unmeasured link).',
                     'statement': f'PCIe 624 at the link figure of 15.75 GB/s; at the measured host-to-device DMA rate '
                                  f'({H2D_RNG} GB/s, fact pcie.h2d) the PCIe ridge is {RIDGE_DMA}.',
                     'source': '; the measured-DMA ridge computed in build_facts.py: 1,024 minions x 16 FLOP x 600 MHz '
                               '(facts chip-minions, minion.vec-peak, op-600) over docs/reports/data/2026-09-27-pcie/'
                               'pcie.json bw.<card>.h2d.dma[bytes=268435456].gbs.mean'},
    # the die view and the grey cells, inferred before 27 September, now follow the firmware's map (except handedness)
    'L32': {'find': '(0,4) and (0,5) are the I/O and PCIe shires',
            'statement': '(0,4) and (0,5) are the I/O and PCIe shires, in some order',
            'source': '; superseded 27 Sep by fw.grey-cells',
            'note': 'Superseded 27 Sep: the firmware\'s maps name the four cells (fact fw.grey-cells): (0,3) the master '
                    '(shire 32), (5,3) the spare (33), (0,4) the PCIe shire and (0,5) the I/O shire, the order of PRM '
                    'Fig. 1-3. Timing a counter read on shire 32 confirms the master\'s cell on a card: E56 (29 Sep, '
                    'docs/reports/data/2026-09-29-nocr) placed it there on aifoundry1 card 1 and decided nothing on '
                    'aifoundry3 or aifoundry2.'},
    'L33': {'source': '; settled 27 Sep by fw.map-match except the handedness (die.handedness)',
            'note': 'Settled 27 Sep except the east-west handedness: the firmware\'s NoC-spec map, renamed as the boot '
                    'firmware renames the shires, equals the measured map in every pair distance with no rotation or '
                    'mirror (fact fw.map-match); which handedness the silicon has is open (fact die.handedness). '
                    'Distances alone cannot tell a rotation from a reflection.'},
    'L34': {'source': '; settled 27 Sep by fw.map-match except the handedness (die.handedness)',
            'note': 'Settled 27 Sep except the east-west handedness: this view is the firmware\'s NoC-spec map after '
                    'the boot-time renaming (fact fw.map-match), and the firmware names the grey cells (fw.grey-cells). '
                    'Memory shire 2\'s row is still a tie-break of the fit (L42, ms2-forced).'},
    'mesh.orientation': {'source': '; settled 27 Sep by fw.map-match except the handedness (die.handedness)',
                         'note': 'Settled 27 Sep except the east-west handedness (facts fw.map-match, die.handedness).'},
    'L37': {'find': 'It does NOT match the measured map:',
            'statement': 'As written it does not match the measured map:',
            'source': '; superseded 27 Sep by fw.map-match (the map after the boot firmware renames the shires)',
            'note': 'Superseded: this compares the map before NOC_Remap_Shires renames the shires at boot; after the '
                    'renaming it matches all 496 pair distances (fact fw.map-match).'},
    'gs-s-dram-256K': {
        'find': '24,599 cycles per instruction per hart.',
        'statement': '24,584 cycles per instruction per hart (median, pooled over the 9 passes; per card 24,599 on '
                     'aifoundry2 and aifoundry3, 24,554 on aifoundry1-c1). 2,048 harts × 8 elements at 600 MHz over '
                     'that is 0.400 G elements/s, about 5% under the measured aggregate rate.',
        'source': '; .pooled[same key].cpi_med (mean 24,584)'},
}
for fid, a in AMEND.items():
    f = ALL[fid]
    if 'find' in a:
        assert a['find'] in f['statement'], fid
        f['statement'] = f['statement'].replace(a['find'], a['statement'])
    f['source'] += a['source']
    for k in ('note', 'unit', 'kind'):
        if k in a:
            f[k] = a[k]
# the measured range the ridge amendment quotes is the one fact pcie.h2d gives
assert H2D_RNG in ALL['pcie.h2d']['statement'], H2D_RNG

# ---- the mesh's routing order, measured (29 Sep 2026, E56 "nocr", hub rung 32). Until then L104 was inferred: every
# route on this page, and heat-per-mm's link model, assumed x first for every packet. E56 streamed 1 KB tensor loads
# (the data travel as replies) and tensor stores (the data travel as requests) in sets chosen so that their streams
# share one directed link under one order and none under the other. Development on aifoundry1's card 1, then the
# frozen validation on aifoundry3 (tools/claims-v3/nocr/PREREG.md, sha256 2472ab3e...), and on the evening of 29 September
# the same frozen test on aifoundry2 as a third card. The numbers are read here from each card's summary.json
# (reduce.py); the statement quotes them, so a new reduction changes the page with it.
NOCR = os.path.join(HERE, '..', '2026-09-29-nocr', 'raw')
NOCR_CARDS = ['aifoundry1-c1', 'aifoundry3', 'aifoundry2']
NR = {c: json.load(open(os.path.join(NOCR, c, 'summary.json')))['r32'] for c in NOCR_CARDS}
for c in NOCR_CARDS:   # the verdicts this section states
    assert NR[c]['read']['verdict'] == 'yx' and NR[c]['write']['verdict'] == 'xy', c


def rho(mode, sets):
    v = [NR[c][mode]['sets'][s]['rho_pooled'] for c in NOCR_CARDS for s in sets]
    return min(v), max(v)


ROW35, COL35 = ['rowE3', 'rowE5', 'rowF3', 'rowF5', 'rowW3'], ['colS3', 'colS5', 'colN3', 'colN5']
R_FELL, R_HELD = rho('read', COL35), rho('read', ROW35)     # reads: the sets that share a link under y first fell
W_FELL, W_HELD = rho('write', ROW35), rho('write', COL35)   # stores: the sets that share a link under x first fell
assert R_FELL[1] <= 0.90 and W_FELL[1] <= 0.90 and R_HELD[0] >= 0.95 and W_HELD[0] >= 0.95   # the frozen fall and hold
CAP = [NR[c][m]['capacity_gbs_from_dropping_sets'] for c in NOCR_CARDS for m in ('read', 'write')]
f2 = lambda lo_hi: f'{lo_hi[0]:.2f}-{lo_hi[1]:.2f}'   # noqa: E731
ROUTE_CAP = f'{statistics.median(CAP):.0f}'
assert max(CAP) - min(CAP) < 1, CAP
ALL['L104'].update({
    'statement': 'The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x '
                 'first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request\'s '
                 'route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that '
                 'their streams share one directed link under one order and none under the other: 1 KB tensor loads, '
                 f'whose data travel as replies, fell to {f2(R_FELL)} of their bandwidth alone when they shared a link '
                 f'under y first and held at {R_HELD[0]:.2f} when they shared one under x first; tensor stores, whose '
                 f'data travel as requests, showed the mirror ({f2(W_FELL)} against {W_HELD[0]:.2f}). A shared link '
                 f'carried about {ROUTE_CAP} GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen '
                 'validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), '
                 'three passes each.',
    'source': 'tools/claims-v3/nocr/PREREG.md (frozen 29 Sep about 00:10 PDT, sha256 2472ab3e...; the sets: '
              'workloads/nocroute/meshmap.py, tools/claims-v3/nocr/sets.json); docs/reports/data/2026-09-29-nocr/raw/'
              '<card>/summary.json .r32.read and .r32.write: .verdict, .sets.<set>.rho_pooled (sets of 3 and 5 streams), '
              '.capacity_gbs_from_dropping_sets; docs/reports/data/2026-09-29-nocr/README.md',
    'kind': 'measured', 'card': 'aifoundry2, aifoundry3, aifoundry1-c1', 'url': None, 'page': None,
    'note': 'Until 29 September this fact was inferred: the analyses assumed x first for every packet (as Chang infers), '
            'and every route on this page was drawn so (docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md '
            '§1b \'Routing\'; heat-per-mm.script.js\'s route map, x first by default until 29 September: its `order` and the \'Routing order\' toggle). What E56 saw is the data: a load\'s replies '
            'and a store\'s requests. That a load\'s own requests go x first and a store\'s acknowledgements y first '
            'follows if the order is set by the kind of packet; those small packets never slowed a set (each costs a '
            'link under 0.54 of a reply). On the die view x runs down the die\'s rows: a request first moves north or '
            'south, then east or west, and a reply first east or west.'})
AMEND2 = {
    'mesh.shortest-paths': {'find': 'The order in which the mesh routes a request (x first or y first) was not measured.',
                            'statement': 'The order was measured later, on 29 September: requests x first, replies y first '
                                         '(fact L104).',
                            'source': '; the order: fact L104 (E56, docs/reports/data/2026-09-29-nocr)'},
    'addr.load-model': {'source': '', 'note': 'The model counts hops, not routes. The route order inside the mesh was '
                                                'measured on 29 September (fact L104): each request x first, each reply y '
                                                'first.'},
    'mesh.xy-assumption': {'source': '; settled 29 Sep by fact L104 (E56)',
                           'note': 'Settled 29 Sep: an analysis assumption, not a documented routing rule. E56 measured the '
                                   'order (fact L104): requests x first, replies y first, so a load\'s data travel y first '
                                   '(the YX case this analysis also checks) and a store\'s x first.'},
}
for fid, a in AMEND2.items():
    f = ALL[fid]
    if 'find' in a:
        assert a['find'] in f['statement'], fid
        f['statement'] = f['statement'].replace(a['find'], a['statement'])
    f['source'] += a['source']
    if 'note' in a:
        f['note'] = a['note']

# ---- E55 and E57 on this page (29 Sep 2026, the major pass; hub rungs 33, 34, 35 and 36). pcie2 (E55) timed where a
# host copy lands and which DMA commands collide; memp2 (E57) the DRAM address map and a TensorLoad's second load. Each
# was developed on aifoundry1's card 1, frozen, then validated on aifoundry3 (tools/claims-v3/pcie2/PREREG.md, sha256
# f632d6b3...; tools/claims-v3/memp2/prereg/PREREG.md, lock 9712c3d6...), and on the evening of 29 September run the same
# way on aifoundry2 as a third card. The numbers are read from the reductions and the verdicts asserted, so a reduction
# that changes a verdict stops this build.
P2DIR = os.path.join(HERE, '..', '2026-09-29-pcie2')
P2 = json.load(open(os.path.join(P2DIR, 'pcie2.json')))['cards']['aifoundry3']
assert P2['theories']['T34-A'] == 'survives' and P2['theories']['T35-S'] == 'survives', P2['theories']
assert all(P2['theories'][t] == 'refuted' for t in ('T34-B', 'T34-C', 'T34-D', 'T35-A', 'T35-BC', 'T35-E', 'T35-X'))
assert not any(P2['stats']['bad']['values'])   # no first-touch value differed from the last pattern written
P2B = json.load(open(os.path.join(P2DIR, 'pcie2.json')))['cards']['aifoundry2']   # the third card (29 Sep evening)
assert all(P2B['theories'][t] == P2['theories'][t] for t in P2['theories']), P2B['theories']
assert not any(P2B['stats']['bad']['values'])
P2DEV = open(os.path.join(P2DIR, 'dev-aifoundry1-c1.md')).read()   # card 1's development table (reduce.py)
for t, v in (('T35-S', 'survives'), ('T34-A', 'survives')):
    assert re.search(r'\| ' + t + r' \|[^\n]*\| ' + v + r' \|', P2DEV), t


def p2dev(item):
    return float(re.search(r'\| ' + item + r' \|[^\n]*?(?:PASS|FAIL|INCONCLUSIVE): ([\d.]+)', P2DEV).group(1))


L3PCT = f"{100 * min(P2['stats']['fw']['mean'], P2['stats']['fc']['mean']):.1f}"   # h2d_warm, h2d_cold: lines at L3 latency
L3PCT1 = f"{100 * min(p2dev('P34-7'), p2dev('P34-8')):.1f}"
L3PCT2 = f"{100 * min(P2B['stats']['fw']['mean'], P2B['stats']['fc']['mean']):.1f}"
ONE_STREAM2, TWO_STREAMS2 = f"{P2B['stats']['h64']['mean']:.3f}", f"{P2B['stats']['s2']['mean']:.3f}"
ONE_STREAM, TWO_STREAMS, TWO_STREAMS1 = f"{P2['stats']['h64']['mean']:.3f}", f"{P2['stats']['s2']['mean']:.3f}", f"{p2dev('P35-6'):.3f}"
PCIEPG_ = 'https://spacesheep.dev/@yaroslavvb/et-soc1-pcie-link'
ALL['pcie.write-l3'] = {
    'id': 'pcie.write-l3', 'component': 'pcie', 'topic': 'data flow', 'kind': 'measured', 'set': 'page',
    'statement': 'A host-to-card copy goes through each line\'s L3 home, which allocates the line: after a staged 4 MB '
                 f'copy, {L3PCT}% of the lines read at L3 latency on aifoundry3 ({L3PCT2}% on aifoundry2, {L3PCT1}% on aifoundry1-c1), whether '
                 'the L3 held the buffer before or not, and every value read was the last one written. A kernel\'s first '
                 'touch of a freshly copied buffer hits the L3, not DRAM (tested for a 4 MB buffer).',
    'value': float(L3PCT), 'unit': '% of lines at L3 latency (aifoundry3)',
    'source': 'tools/claims-v3/pcie2/PREREG.md (frozen 29 Sep 00:04 PDT, sha256 f632d6b3...); '
              'docs/reports/data/2026-09-29-pcie2/pcie2.json .cards.aifoundry3.stats.fw and .fc (h2d_warm, h2d_cold: '
              'the share of lines whose first touch is L3-like), .stats.bad (wrong values), .theories["T34-A"]; '
              '.cards.aifoundry2 the same (the third card); dev-aifoundry1-c1.md P34-7, P34-8 (card 1, development)',
    'card': 'aifoundry2, aifoundry3, aifoundry1-c1', 'url': PCIEPG_ + '#where-a-host-copy-lands', 'page': 'Over the PCIe link',
    'note': 'E55\'s T34-A (29 September). The rivals, an L3 that updates only lines it already holds (T34-B) and writes '
            'that go to the memory shires with the L3\'s copy invalidated (T34-C) or left stale (T34-D), were refuted on '
            'all three cards. When the L3 writes the lines back to DRAM was not timed; flow 6 draws that leg dashed.'}
M2DIR = os.path.join(HERE, '..', '2026-09-29-memp2')
M2 = {c: json.load(open(os.path.join(M2DIR, d, 'memp2.json')))['cards'][c]['items']
      for c, d in (('aifoundry3', 'val-aifoundry3'), ('aifoundry1-c1', 'dev-aifoundry1-c1'))}
assert M2['aifoundry3']['R33a']['outcome'] == 'PASS' and M2['aifoundry1-c1']['R33a']['outcome'] == 'PASS'
assert M2['aifoundry3']['R33b']['outcome'] == 'PASS' and M2['aifoundry3']['R33b']['refresh_domain_bits'] == ['6', '7', '8', '9']
assert M2['aifoundry1-c1']['R33b']['outcome'] == 'FAIL'
assert all(M2[c]['R33c']['outcome'] == 'INSUFFICIENT' for c in M2)
assert all(M2[c]['R36']['outcome'] == 'PASS' and M2[c]['R36']['tl2_like'] == 'L2' for c in M2)
HITD = sorted({-M2[c]['R33a']['step_bank_bits'] for c in M2})   # the bank-bit step, cycles (a row hit's saving)
assert len(HITD) == 1 and not any(M2[c]['R33a']['misclassified'] for c in M2), HITD
TL2 = {c: M2[c]['R36']['medians'] for c in M2}
# the third card (aifoundry2, 29 Sep evening): R33a missed one condition there, the other items as on aifoundry3
M2B = json.load(open(os.path.join(M2DIR, 'val-aifoundry2', 'memp2.json')))['cards']['aifoundry2']['items']
assert M2B['R33a']['outcome'] == 'FAIL' and M2B['R33a']['misclassified'] == ['col'] and -M2B['R33a']['step_bank_bits'] == HITD[0]
assert sum(1 for c in M2B['R33a']['per_cond'].values() if c['class'] == c['predicted']) == 14
assert M2B['R33b']['outcome'] == 'PASS' and M2B['R33b']['refresh_domain_bits'] == ['6', '7', '8', '9']
assert M2B['R33c']['outcome'] == 'INSUFFICIENT' and M2B['R36']['outcome'] == 'PASS' and M2B['R36']['medians']['tl2'] == TL2['aifoundry3']['tl2']
assert TL2['aifoundry3']['tl2'] == TL2['aifoundry3']['ref_l2'] == TL2['aifoundry1-c1']['tl2']
f_ = lambda v: f'{v:,.0f}' if v == int(v) else f'{v:,.1f}'   # noqa: E731
AMEND3 = {
    'L50': {'find': 'Inferred DRAM address map: ', 'statement': 'DRAM address map: ',
            'append': ' Measured on 29 September (E57): another row in the same bank is a row conflict, and a row that '
                      f'also differs in any of PA[6-12] (the memory shire, the controller, the bank) reads as a row hit, '
                      f'{f_(HITD[0])} cycles faster, on aifoundry1-c1 and aifoundry3 (15 of 15 conditions); on aifoundry3 and '
                      'aifoundry2 PA[6-9] set the refresh phase and PA[10-13] and PA[18] do not, so each controller refreshes on '
                      'its own. On aifoundry2, run the same way as a third card, 14 of 15 conditions came out so: two lines that '
                      'differ only in PA[17], a column bit in this map, read as a row conflict there.',
            'source': '; measured: tools/claims-v3/memp2/prereg/PREREG.md (lock 9712c3d6...), '
                      'docs/reports/data/2026-09-29-memp2/val-aifoundry3/memp2.json, val-aifoundry2/memp2.json and '
                      'dev-aifoundry1-c1/memp2.json .cards.<card>.items.R33a.per_cond, .misclassified, .R33b.refresh_domain_bits, .R33c',
            'kind': 'measured', 'card': 'aifoundry1-c1, aifoundry3',
            'note': 'Inferred until 29 September (from a tool comment, NoC mask values and ADDRMAP registers, not a '
                    'readback). E57 measured the bank and row split on aifoundry1-c1 and aifoundry3 (R33a; on aifoundry2 14 of '
                    '15 conditions, PA[17] reading as a row bit there) and the refresh domain on aifoundry3 and aifoundry2 '
                    '(R33b; on aifoundry1-c1 PA[7] read unclear and no registered reading fitted). Still open: whether two '
                    'accesses on one controller serialise (R33c, insufficient on all three cards), and why PA[17] conflicts '
                    'on aifoundry2.'},
    'minion.tensor-cache-path': {
            'source': '; the L2: docs/reports/data/2026-09-29-memp2/val-aifoundry3/memp2.json, val-aifoundry2/memp2.json '
                      'and dev-aifoundry1-c1/memp2.json .cards.<card>.items.R36.medians (tl1, tl2, ref_l2, ref_l3, probe_tl)',
            'note': 'Settled 29 Sep for the L2: E57 (R36) TensorLoaded the same fresh 1 KB twice, and the second load took '
                    f'{f_(TL2["aifoundry3"]["tl2"])} cycles, the L2 reference\'s {f_(TL2["aifoundry3"]["ref_l2"])} '
                    f'(the L3 reference {f_(TL2["aifoundry3"]["ref_l3"])}, the first load {f_(TL2["aifoundry3"]["tl1"])}), '
                    f'and a scalar load after it {f_(TL2["aifoundry3"]["probe_tl"])}, an L2 hit, on aifoundry3, aifoundry2 and '
                    'aifoundry1-c1: a TensorLoad that misses allocates its lines in the L2. Not measured: whether the L3 '
                    'keeps them and whether tensor stores skip the L2 (the Shire Cache Specification says they do).'},
    'pcie.conc': {'find': '(two streams: 5.96 / 6.00 / 5.96 GB/s in total)',
                  'statement': '(two streams with both of each stream\'s commands in flight, four in all: 5.96 / 6.00 / '
                               '5.96 GB/s in total; with one command in flight in each of two streams nothing is lost, '
                               f'{TWO_STREAMS} of one at a time on aifoundry3, {TWO_STREAMS2} on aifoundry2 and {TWO_STREAMS1} on '
                               'aifoundry1-c1, E55)',
                  'source': '; E55: docs/reports/data/2026-09-29-pcie2/pcie2.json .cards.aifoundry3.stats.s2 and .h64 '
                            '(and .cards.aifoundry2, the third card), '
                            '.theories["T35-S"]; dev-aifoundry1-c1.md P35-6',
                  'note': f'E55 (29 September) found which commands collide: two in flight in one stream move {ONE_STREAM} '
                          f'of one at 2 x 64 MB on aifoundry3, one in each of two streams {TWO_STREAMS} (T35-S; on aifoundry2 '
                          f'{ONE_STREAM2} and {TWO_STREAMS2}); a shared read engine, the IOMMU, a fixed cost per overlap, a '
                          'slow onset and a loss per element were refuted on all three cards.'},
}
for fid, a in AMEND3.items():
    f = ALL[fid]
    if 'find' in a:
        assert a['find'] in f['statement'], fid
        f['statement'] = f['statement'].replace(a['find'], a['statement'])
    f['statement'] += a.get('append', '')
    f['source'] += a['source']
    for k in ('note', 'kind', 'card'):
        if k in a:
            f[k] = a[k]

# ---- card coverage set by hand where the card string's aside names a card that was not measured, or the number the
# page prints covers fewer cards than the fact (27 Sep review). Value: (cards, text shown for them)
CARDS = {
    'clock.minion-opps': (['a2'], 'aifoundry2 (aifoundry3 is pinned at 600 MHz, not measured here)'),
    'mesh.clock': (['a2'], 'aifoundry2 (aifoundry3 is set to 400 MHz by its boot service)'),
    'L101': (['a2'], 'aifoundry2 (telemetry of the hot-line run)'),
    'bw-scp-own': (['a2', 'a3'], 'aifoundry2, aifoundry3 (the read rate); the store rate on three cards'),
    'bw-l1': (['a2', 'a3', 'a1c1'], 'three cards (14.5 TB/s); 6.2 TB/s on aifoundry2, aifoundry3'),
    'relay-bw': (['a2'], 'aifoundry2 pass means (the other cards within 1.5%)'),
}

# ---- the broadcast flow (B; 28 Sep 2026, the owner's request from the page's Talk tab): how one value reaches every
# minion, the ways the chip offers and what each costs. No new measurement: the 1 KB allreduce is read here from the
# version-3 raw files (each card's median over its three passes, as the on-chip communication page's chart merges
# them), the launch's cost per shire from pcie.json; the tree's rule, the launch's multicast and the shire cache's rule
# for one line are read from the manuals and the firmware source. Each fact says what was not measured.
V3RAW = os.path.join(HERE, '..', '2026-09-25-claims-v3', 'raw')
ONCHIP = 'https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'
HOTLINE = 'https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line'
PCIEPG = 'https://spacesheep.dev/@yaroslavvb/et-soc1-pcie-link'
CARD3 = 'aifoundry2, aifoundry3, aifoundry1-c1'


def ar_count32(card, fname, minions):
    """cycles_per_iter of the one-tree, 32-register (1 KB) allreduce over `minions`, one value per version-3 pass"""
    vals = []
    for fn in sorted(glob.glob(os.path.join(V3RAW, card, 'lat', 'p*', 'noc', fname))):
        for line in open(fn):
            if not line.startswith('NOCBENCH'):
                continue
            r = json.loads(line.split(' ', 1)[1])
            if r.get('kind') == 'allreduce' and r['minions'] == minions and r['trees'] == 1 and r['count'] == 32:
                assert r['ok'], (fn, r)
                vals.append(r['cycles_per_iter'])
    assert len(vals) == 3, (card, fname, vals)
    return vals


C3 = ['aifoundry2', 'aifoundry3', 'aifoundry1-c1']
AR32K = {c: ar_count32(c, 'allreduce-c32.jsonl', 32) for c in C3}
AR1KK = {c: ar_count32(c, 'xallreduce-c32.jsonl', 1024) for c in C3}
all32 = [v for c in C3 for v in AR32K[c]]
med1k = [statistics.median(AR1KK[c]) for c in C3]
assert max(all32) - min(all32) < 1 and max(med1k) - min(med1k) < 20, (all32, med1k)
AR32K_T = f'{statistics.median(all32):,.0f}'
AR1K_T = f'{min(med1k):,.0f}-{max(med1k):,.0f}'
AR32K_US = f'{statistics.median(all32) / 600:.2f}'
AR1K_US = f'{min(med1k) / 600:.1f}'
assert AR1K_US == f'{max(med1k) / 600:.1f}', med1k
# an empty kernel queued back to back, on 32 shires and on one (pcie.json, E50): what the other 31 shires add
B32 = [PCIE['launch'][c]['b2b_us']['32']['mean'] for c in PCIE['cards']]
B1 = [PCIE['launch'][c]['b2b_us']['1']['mean'] for c in PCIE['cards']]
DL = [a - b for a, b in zip(B32, B1)]
slash = lambda xs: ' / '.join(f'{x:.1f}' for x in xs)
BC = [
    {'id': 'bc.tensorbroadcast', 'component': 'neigh', 'topic': 'sync', 'kind': 'spec',
     'statement': 'TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node '
                  'height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + '
                  '2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root\'s value. N harts take log2 N '
                  'steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector '
                  'registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from '
                  'minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.',
     'value': 10, 'unit': 'steps for 1,024 minions',
     'source': 'external/et-man/ET Programmer\'s Reference Manual.pdf, pdf p.320-322 (§9.4, TensorBroadcast: '
               '\'performed in a fully-balanced binary-tree fashion\', the sender and receiver rule, \'a sequence of '
               'log2N TensorBroadcast operations\', \'effectively implementing a broadcast of A0\', the stall notes); '
               'workloads/nocbench/kernel/nocbench.c:279-288 (the benchmark\'s tree: TensorBroadcast with MOVE from '
               'the top level down); workloads/nocbench/README.md (the target is a minion ID, shire * 32 + minion, '
               'and the partner is hart 2 * ID)',
     'card': None, 'page': 'On-chip communication', 'url': ONCHIP, 'note': None},
    {'id': 'bc.allreduce-1kb', 'component': 'neigh', 'topic': 'sync', 'kind': 'measured',
     'statement': f'The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: {AR32K_T} cycles over '
                  f'a shire\'s 32 minions ({min(all32):,.2f}-{max(all32):,.2f} in every pass on the three cards, '
                  f'{AR32K_US} µs) and {AR1K_T} cycles over all 1,024 minions (each card\'s median over three passes: '
                  f'aifoundry2 {med1k[0]:,.2f}, aifoundry3 {med1k[1]:,.2f}, aifoundry1-c1 {med1k[2]:,.2f}; '
                  f'{AR1K_US} µs at 600 MHz), against 444 and 1,393 cycles for 32 B.',
     'value': round(max(med1k)), 'unit': 'cycles, 1 KB to all 1,024 minions (aifoundry1-c1)',
     'source': 'docs/reports/data/2026-09-25-claims-v3/raw/<card>/lat/p*/noc/allreduce-c32.jsonl and '
               'xallreduce-c32.jsonl (E36; count 32; cycles_per_iter of the one-tree rows at 32 and 1,024 minions), '
               'read in build_facts.py; the on-chip communication page\'s chart shows the same medians (its embedded '
               'nocbench-data .v3.cards.<card>.allreduce["32"], analyze.py merge_passes)',
     'card': CARD3, 'page': 'On-chip communication', 'url': ONCHIP,
     'note': 'The claims ledger lists the 32 B allreduces of the same passes (05-claims.md, "Barriers and allreduces"); '
             'the 1 KB rows are in the same raw files.'},
    {'id': 'bc.half', 'component': 'neigh', 'topic': 'sync', 'kind': 'derived',
     'statement': 'The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree '
                  'and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is '
                  'part of the allreduce\'s 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half\'s '
                  'energy was measured: the energy manual\'s synchronisation table gives none for the tree.',
     'value': None, 'unit': None,
     'source': 'workloads/nocbench/kernel/nocbench.c:279-288 (tree(): TensorReduce for levels 0..top, then '
               'TensorBroadcast top..0) and :529-534 (one cycle count around the repeated tree); '
               'docs/energy-manual/06-synchronisation.md:12 (TensorReduce + broadcast: energy \'—\')',
     'card': None, 'page': 'On-chip communication', 'url': ONCHIP, 'note': None},
    {'id': 'bc.one-request', 'component': 'l2', 'topic': 'interconnect', 'kind': 'spec',
     'statement': 'Inside a shire, requests to one line are kept in order, and \'Two requests to the mesh will never '
                  'have the same address outstanding\': when every minion of a shire loads one line homed in another '
                  'shire, the shire has at most one request for it on the mesh at a time. The L2\'s 8-entry read '
                  'buffer is there for \'multiple readers of the same cache line\', its hits \'serviced once per '
                  'clock\'; L3 reads at the home do not use it.',
     'value': 1, 'unit': 'mesh request per line and shire at a time',
     'source': 'external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf, pdf p.36 (§2.6.1 Reqq Request '
               'Ordering, rule 1a), p.9 (the Read buffer) and p.40 (§2.8: \'L3 reads do not use the Read buffer\')',
     'card': None, 'page': None, 'url': None,
     'note': 'That the shire\'s other minions then find the line in its L2 follows from the fill; loads of one line by '
             'every minion at once were not measured.'},
    {'id': 'bc.pollers', 'component': 'uc', 'topic': 'sync', 'kind': 'measured',
     'statement': '31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank '
                  'retiring one every 10.00 cycles, while shire 0\'s one minion reading its own scratchpad kept 100% '
                  'of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). '
                  'Whether they would stop a shire whose 32 minions all read was not tested. Each shire\'s leader '
                  'polling one counter hung the relay\'s first barrier (one development run).',
     'value': 100, 'unit': '% of the reader\'s rate alone',
     'source': 'docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json: pollers[card=<card>, '
               'home="scplocal:0"].remote_cycles_per_atomic (9.9993), .frac_of_alone_n (0.99998-0.99999); '
               'docs/reports/data/2026-09-25-claims-v3/results/lat.json [item=LAT-H].per_card.<card>.sub.P5_pollers '
               '(host_over_alone1 1.0 in every pass); docs/findings/17-hot-line.md:137-145; '
               'docs/findings/18-on-chip-relay.md:149-152',
     'card': CARD3, 'page': 'One hot line stops a shire', 'url': HOTLINE, 'note': None},
    {'id': 'bc.esr-ipi', 'component': 'master', 'topic': 'sync', 'kind': 'spec',
     'statement': 'ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for '
                  'the compute shires, 8 for the memory shires): software writes the value to the broadcast data '
                  'register, then the target register and the masks to a broadcast request register. A shire\'s '
                  'IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; '
                  'the firmware\'s broadcast system call writes the first two.',
     'value': 32, 'unit': 'shires in one request',
     'source': 'external/et-man/ET Programmer\'s Reference Manual.pdf, pdf p.511 (§15.4.2 ESR Broadcast, Table '
               '15-85, Figure 15-1, Table 15-86) and p.336 (§13.1 IPI_TRIGGER, Table 13-1); '
               'external/et-platform/device-minion-runtime/src/MachineMinion/src/trap_handler.S:83-97 '
               '(SYSCALL_BROADCAST_INT writes ESR_SHIRE_BROADCAST0, then BROADCAST1 with the shire mask)',
     'card': None, 'page': None, 'url': None, 'note': None},
    {'id': 'bc.launch-multicast', 'component': 'master', 'topic': 'sync', 'kind': 'spec',
     'statement': 'Every kernel launch is a broadcast. The master shire\'s firmware copies the 64-byte launch message '
                  'into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts '
                  'of every shire in the kernel\'s mask with one ESR broadcast, and polls a shire mask beside the '
                  'buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire\'s 64 '
                  'harts clears that shire\'s bit with a global atomic AND. The launch goes on once every bit is '
                  'clear.',
     'value': 64, 'unit': 'bytes, one line',
     'source': 'external/et-platform/device-minion-runtime/src/MasterMinion/src/services/cm_iface.c:75-83 '
               '(broadcast_ipi_trigger), :270-367 (CM_Iface_Multicast_Send: ETSOC_MEM_COPY_AND_EVICT to the L2 at '
               ':318, the interrupt at :322, the poll on the shire mask to :336); src/MasterMinion/src/workers/kw.c:'
               '931-933 (the launch: \'Blocking call that blocks till all shires ack command\'); '
               'src/WorkerMinion/src/mm_to_cm_iface.c:60-73 (notify_mm: the 64th hart clears its shire\'s bit with '
               'atomic_and_global_64), :122-128 (ETSOC_MEM_EVICT before the read); et-common-libs/include/system/'
               'layout.h:51, 112-118 (a 64-byte buffer and its control line in the master shire\'s scratchpad); '
               'et-platform 836a4ab',
     'card': None, 'page': None, 'url': None, 'note': None},
    {'id': 'bc.launch-31', 'component': 'master', 'topic': 'latency', 'kind': 'derived',
     'statement': f'Queued back to back, an empty kernel costs the card {slash(B32)} µs on all 32 shires and '
                  f'{slash(B1)} µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add '
                  f'{slash(DL)} µs ({min(DL):.1f}-{max(DL):.1f} µs), the rest the same for one shire or 32. Which part '
                  f'of that is the launch\'s multicast (the interrupt, every hart reading the message, the shires\' '
                  f'acknowledging atomics) and which the kernel\'s own start and finish was not measured.',
     'value': round(max(DL), 1), 'unit': 'µs for the other 31 shires (aifoundry2)',
     'source': 'docs/reports/data/2026-09-27-pcie/pcie.json launch.<card>.b2b_us."32".mean and ."1".mean (E50), '
               'the difference computed in build_facts.py; the Over the PCIe link page\'s launch note '
               '(docs/reports/sources/pcie-link.script.js:241-243)',
     'card': CARD3, 'page': 'Over the PCIe link', 'url': PCIEPG, 'note': None},
]
for f in BC:
    assert f['id'] not in ALL, 'duplicate fact id ' + f['id']
    f['set'] = 'page'
    ALL[f['id']] = f

# page titles by URL (the arch and numbers files name their page; the layout file gives only the URL)
TITLE = {}
for f in ALL.values():
    u = f.get('page_url') or f.get('url')
    if u and f.get('page') and not str(f['page']).startswith('http'):
        TITLE.setdefault(u.split('#')[0], re.sub(r'\s*\((the )?reports hub\)', '', f['page']))


def norm(f):
    url = f.get('page_url') or f.get('url') or (f['page'] if str(f.get('page') or '').startswith('http') else None)
    title = TITLE.get(url.split('#')[0]) if url else None
    if url and not title:
        raise SystemExit('no title for ' + url)
    c = f.get('card') or ''
    cards = [k for k, pat in (('a2', r'aifoundry2'), ('a3', r'aifoundry3'),
                              ('a1c1', r'aifoundry1-c1|aifoundry1 card 1|aifoundry1 \(both cards\)|aifoundry1, '))
             if re.search(pat, c)]
    cards_txt = None
    if f['id'] in CARDS:
        cards, cards_txt = CARDS[f['id']]
    out = {k: f.get(k) for k in ('id', 'component', 'topic', 'statement', 'value', 'unit', 'source', 'kind', 'card', 'note')}
    out.update(range=f.get('range'), url=url, page=title, cards=cards, set=f['set'])
    if cards_txt:
        out['cards_txt'] = cards_txt
    return out


# ---- numbers the page prints: key -> (fact, value, text, unit). The text must occur in the fact's statement.
N = [
    # the chip
    ('cores', 'chip.cores-total', 1093, '1,093', 'cores'),
    ('minions', 'chip.minions', 1088, '1,088', 'minions'),
    ('shires', 'chip.minion-shires', 34, '34', 'minion shires'),
    ('cshires', 'chip.compute-array', 32, '32', 'compute shires'),
    ('maxions', 'chip.cores-total', 4, '4 ET-Maxions', ''),
    ('die_mm2', 'chip.die-area', 570, '570', 'mm²'),
    ('transistors', 'chip.process', 24, '24 billion', 'transistors'),
    ('process', 'chip.process', 7, '7 nm', ''),
    ('stops', 'mesh.grid', 44, '44', 'mesh stops'),
    ('memshires', 'chip.memshires', 8, 'Eight', 'memory shires'),
    ('channels', 'dram.channels', 16, '16', 'LPDDR4X channels'),
    ('ch_bits', 'dram.channels', 16, '16 bits', ''),
    ('dram_gb', 'dram.capacity', 32, '32 GB', ''),
    ('mts', 'dram.rate-card', 3733, '3,733', 'MT/s'),
    ('dram_peak', 'dram.peak-card', 119, '119', 'GB/s'),
    ('dram_bw', 'bw-dram', 76, '76', 'GB/s'),
    ('cache_mb', 'shire.cache-geometry', 4, '4 MB', ''),
    ('banks', 'shire.cache-geometry', 4, '4 banks', ''),
    ('subbanks', 'shire.cache-geometry', 4, '4 sub-banks', ''),
    ('scp_mb', 'shire.partition-m0', 2.5, '2.5 MB', ''),
    ('l2_kb', 'shire.partition-m0', 512, '512 KB', ''),
    ('l3_mb', 'shire.partition-m0', 1, '1 MB', ''),
    ('scp_chip', 'shire.partition-m0', 80, '80 MB', ''),
    ('l2_chip', 'shire.partition-m0', 16, '16 MB', ''),
    ('l3_chip', 'shire.partition-m0', 32, '32 MB', ''),
    ('neigh', 'shire.composition', 4, '4 neighbourhoods', ''),
    ('per_neigh', 'neigh.composition', 8, '8 minions', ''),
    ('icache', 'neigh.composition', 32, '32 KB', ''),
    ('harts', 'minion.isa', 2, '2 harts', ''),
    ('lanes', 'minion.vpu', 8, '8 identical 32-bit lanes', ''),
    ('vregs', 'minion.vpu-regs', 32, '32 vector registers of 32 bytes', ''),
    ('l1_kb', 'minion.l1d', 4, '4 KB', ''),
    ('l1_scp', 'minion.l1-modes', 3, '3 KB', ''),
    ('l1_hart', 'minion.l1-firmware', 512, '512 B', ''),
    ('tflops', 'mm-rate', 9.51, '9.51', 'TFLOP/s fp32'),
    ('tflops16', 'mm-rate', 19.02, '19.02', 'TFLOP/s fp16'),
    ('tops8', 'mm-rate', 71.77, '71.77', 'TOP/s int8'),
    ('peak32', 'mm-peak', 16, '16 fp32', 'FLOP per minion-cycle'),
    ('peak16', 'mm-peak', 32, '32 fp16', ''),
    ('peak8', 'mm-peak', 128, '128 int8', ''),
    ('mhz', 'op-600', 600, '600 MHz', ''),
    ('noc_mhz', 'mesh.clock', 400, '400 MHz', ''),
    ('noc_v', 'L101', 0.485, '0.485 V', ''),
    ('race_t0', 'heat.race', 80.9, '80.9-81.7 °C', ''),
    ('mmw', 'mm-board-w', 69.1, '50.4-69.1 W', '', '50-69 W'),
    ('mmtemp', 'mm-board-w', 80, '62-80 °C', ''),
    ('perw', 'mm-board-w', 189, '138-189', 'GFLOP/s per W'),
    ('vecpeak', 'minion.vec-peak', 16, '16 FLOP', ''),
    ('etl_min', 'minion.etlink-width', 256, '256 bits', ''),
    ('ms_fit', 'ms-fit-3cards', 97, '93-97%', ''),
    ('chipbar', 'sync-chip-barrier', 5013, '4,998-5,013', 'cycles'),
    ('rs_hops', 'bw-scp-remote', 2.1, '2.1 hops', ''),
    ('pcie_gbs', 'bw-pcie', 15.75, '15.75 GB/s', ''),
    ('pcie_lanes', 'chip.pcie-shire', 8, '8-lane', ''),
    ('master_id', 'chip.master-shire-id', 32, '32', ''),
    ('spare_id', 'chip.spare-shire-id', 33, '33', ''),
    ('mask', 'chip.cm-shire-mask', 0, '0xffffffff', ''),
    ('n1024', 'chip-minions', 1024, '1,024', 'minions'),
    ('per_shire', 'shire.composition', 32, '32 minions', ''),
    ('grid86', 'mesh.grid', 8, '8 × 6', ''),
    ('pkg_ch', 'L47', 4, 'four 16-bit channels', ''),
    ('ch16', 'L47', 16, 'two 16-bit LPDDR4X channels', ''),
    ('esr_ms', 'L25', 232, '232–239', ''),
    ('port512', 'mesh.port-width', 512, '512 bits', ''),
    ('lanes4', 'L103', 4, '4 to_l3 master and 4 L3 slave lanes', ''),
    ('bank1mb', 'shire.cache-geometry', 1, '4 banks × 1 MB', ''),
    ('xbar512', 'shire.crossbar', 512, '512-bit', ''),
    ('etl512', 'shire.neigh-link', 512, '512-bit ET-Link bus', ''),
    ('etl256', 'shire.neigh-link', 256, '256-bit bus', ''),
    ('edges', 'neigh.fln-edges', 7, '0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7', ''),
    ('fln7', 'neigh.fln-edges', 7, '7', ''),
    ('b32', 'ts-rt-fln', 32, '32 B', ''),
    ('flb', 'sync-shire-barrier', 233, '233 cycles', ''),
    ('ar1024', 'sync-allreduce1024', 1393, '1,393 cycles', ''),
    ('hot10', 'hot-cost', 10, '10.00 cycles', ''),
    ('vreg256', 'minion.vpu', 256, '256 bits wide', ''),
    ('tshape', 'minion.tensor-shape', 16, 'M, N ≤ 16', ''),
    ('tenb', 'minion.tenb-tenc', 1, '1 KiB', ''),
    ('h1pen', 'lat-l2', 3, 'hart 1 pays 3 more', ''),
    ('sets011', 'minion.l1-modes', 11, 'sets 0-11', ''),
    ('sets1213', 'minion.l1-modes', 12, 'hart 0 sets 12-13', ''),
    ('sets1415', 'minion.l1-modes', 14, 'hart 1 sets 14-15', ''),
    ('l1geom', 'minion.l1d', 16, '16 sets × 4 ways × 64 B', ''),
    ('awake', 'e-awake', 2, 'about 2 mW', ''),
    ('e_fmadd', 'e-fmadd-ps', 55.8, '55.8', 'pJ'),
    ('rl_13th', 'relay-13x', 13, 'about a thirteenth', ''),
    ('dram_region', 'addr.dram-region', 0, '0x80_0000_0000', ''),
    ('scp_base', 'scp.format0', 0, '0x80000000 + (shire << 23) + offset', ''),
    ('ms_pos_card', 'L40', 2, 'total squared error 2', ''),
    ('lanes_n', 'minion.vpu', 8, '8', 'lanes'),
    ('line64', 'shire.cache-geometry', 64, '64-byte', ''),
    ('l3_b12', 'l3.latency', 12, '12', ''),
    ('rl_stages', 'relay-bw', 8, '8 stages', ''),
    ('gs_8', 'gs-l1', 8, '32-bit gather of 8 lanes', ''),
    ('ms8', 'chip.memshires', 8, '8', ''),
    ('pairs496', 'mesh.shortest-paths', 496, '496', 'shire pairs'),
    # the mesh
    ('hop_cyc', 'mesh-hop-lat', 12, '12 cycles', 'cycles per hop, round trip'),
    ('hop_ns', 'mesh-hop-lat', 20, '20 ns', ''),
    ('hop_mm', 'chip.hop-pitch', 3.72, '3.72 mm', ''),
    ('bitmm', 'mesh-bit-mm-free', 37, '37 fJ', 'per bit·mm (mesh rail, free links)'),
    # the routing order (E56, 29 Sep): what a set of streams sharing one link kept, and what the link carried
    ('route_rd', 'L104', R_FELL[0], f2(R_FELL), "of the loads' bandwidth alone"),
    ('route_wr', 'L104', W_FELL[0], f2(W_FELL), "of the stores' bandwidth alone"),
    ('route_gbs', 'L104', float(ROUTE_CAP), f'{ROUTE_CAP} GB/s', 'a shared link, saturated'),
    # where a host copy lands (E55, 29 Sep): the share of a copied buffer's lines that read at L3 latency
    ('pcie_l3pct', 'pcie.write-l3', float(L3PCT), f'{L3PCT}%', 'of lines at L3 latency (aifoundry3)'),
    # latency (minion cycles at 600 MHz)
    ('lat_l1', 'lat-l1', 5.25, '5.25', 'cycles'),
    ('lat_rb', 'lat-rb', 36, '36', 'cycles'),
    ('lat_l2', 'lat-l2', 47, '47', 'cycles'),
    ('lat_scp', 'lat-scp-own', 47, '47', 'cycles'),
    ('lat_rs_a', 'lat-scp-remote', 99.84, '99.84', 'cycles'),
    ('lat_rs_b', 'lat-scp-remote', 12.00, '12.00', 'cycles per hop'),
    ('lat_l3_a', 'l3.latency', 110, '110', 'cycles'),
    ('lat_l3_b', 'l3.latency', 12, '12 cycles per mesh hop', ''),
    ('lat_l3_avg', 'lat-l3-avg', 159, '159-169', 'cycles'),
    ('lat_ms_a', 'dram.leg', 91, '91', 'cycles'),
    ('lat_ms_b', 'dram.leg', 12, '12', 'cycles per hop'),
    ('lat_dram', 'lat-dram-typical', 299, '299', 'cycles'),
    ('lat_dram_ns', 'lat-dram-typical', 500, '500 ns', ''),
    ('lat_dram_rng', 'lat-dram', 297, '287-297', 'cycles'),
    ('lat_dram_chip', 'lat-dram-chip', 28, 'about 25-28', 'cycles'),
    ('row_conf', 'lat-dram-rowconflict', 37, '+37 cycles', ''),
    ('refresh', 'lat-dram-refresh', 3.88, '3.88 us', ''),
    # bandwidth (chip-wide, 1,024 minions at 600 MHz)
    ('bw_l1', 'bw-l1', 6.2, '6.2', 'TB/s'),
    ('bw_l1b', 'bw-l1', 14.5, '14.5', 'TB/s'),
    ('bw_l2', 'bw-l2', 2.45, '2.45', 'TB/s'),
    ('bw_scp', 'bw-scp-own', 2.46, '2.46', 'TB/s'),
    ('bw_rs', 'bw-scp-remote', 0.96, '0.96', 'TB/s'),
    ('bw_l3', 'bw-l3', 0.98, '0.98', 'TB/s'),
    # energy above idle, per byte read
    ('e_l1', 'e-l1', 0.75, '0.75', 'pJ/B'),
    ('e_l2', 'e-l2', 3.11, '3.11', 'pJ/B', '3.1'),
    ('e_l2_rng', 'e-l2', 4.99, '1.42-4.99', 'pJ/B', '1.4-5.0'),
    ('e_scp0', 'e-scp-own-zeros', 2.25, '2.25', 'pJ/B'),
    ('e_scp1', 'e-scp-own-rand', 4.40, '4.40', 'pJ/B'),
    ('e_rs0', 'e-scp-remote-zeros', 5.10, '5.10', 'pJ/B'),
    ('e_rs1', 'e-scp-remote-rand', 11.8, '11.8', 'pJ/B'),
    ('e_l3', 'e-l3', 14.7, '14.7', 'pJ/B', '15'),
    ('e_l3_rng', 'e-l3', 20.5, '7.1-20.5', 'pJ/B', '7-21'),
    ('e_dram', 'e-dram', 114.6, '114.6', 'pJ/B', '115'),
    ('e_dram_rng', 'e-dram', 141.3, '89.0-141.3', 'pJ/B', '89-141'),
    ('e_mac32', 'e-tfma-fp32', 5.782, '5.782', 'pJ per fp32 multiply-add', '5.8'),
    ('e_mac32_rng', 'e-tfma-fp32', 6.133, '5.347-6.133', 'pJ', '5.3-6.1'),
    # TensorSend
    ('ts_a', 'ts-rt-mesh', 150, '150', 'cycles'),
    ('ts_b', 'ts-rt-mesh', 12.02, '12.02', 'cycles per hop'),
    ('ts_fln', 'ts-rt-fln', 68, '68 cycles', ''),
    ('ts_xbar', 'ts-rt-fln', 114, '114-115', 'cycles'),
    ('ts_e_a', 'mesh-hop-ring', 9.2, '9.2 pJ/B', ''),
    ('ts_e_b', 'mesh-hop-ring', 1.75, '1.75 pJ/B', 'per mean hop'),
    ('ts_bw_mesh', 'bw-tsend-mesh', 156, '87-156 GB/s', ''),
    # relay
    ('rl_e_dram', 'relay-energy', 116.2, '116.2', 'pJ/B'),
    ('rl_e_next', 'relay-energy', 8.9, '8.9', 'pJ/B'),
    ('rl_e_own', 'relay-energy', 4.3, '4.3', 'pJ/B'),
    ('rl_x', 'relay-13x', 12.97, '12.9x, 13.0x and 13.1x', ''),
    ('rl_bw_dram', 'relay-bw', 47.7, '47.7', 'GB/s'),
    ('rl_bw_next', 'relay-bw', 592.5, '592.5', 'GB/s'),
    ('rl_bw_own', 'relay-bw', 1487, '1487', 'GB/s'),
    ('rl_speed', 'relay-bw', 12.4, '12.4x', ''),
    # gathers and scatters (E48): rate (G elements/s), energy (pJ per element), cycles per instruction per hart
    ('g_l1_r', 'gs-g-dram-512B', 452, '452', 'G elements/s'),
    ('g_l1_e', 'gs-g-dram-512B', 12.76, '12.76', 'pJ per element'),
    ('g_l1_c', 'gs-g-dram-512B', 21.78, '21.78', 'cycles per instruction'),
    ('g_l2_r', 'gs-g-dram-4K', 27.4, '27.4', 'G elements/s'),
    ('g_l2_e', 'gs-g-dram-4K', 354.5, '354.5', 'pJ per element'),
    ('g_l2_c', 'gs-g-dram-4K', 359.3, '359.3', 'cycles per instruction'),
    ('g_sp_r', 'gs-g-scp-16K', 27.4, '27.4', 'G elements/s'),
    ('g_sp_e', 'gs-g-scp-16K', 367.8, '367.8', 'pJ per element'),
    ('g_sp_c', 'gs-g-scp-16K', 359.3, '359.3', 'cycles per instruction'),
    ('g_rs_r', 'gs-g-rscp-16K', 10.2, '10.2', 'G elements/s'),
    ('g_rs_e', 'gs-g-rscp-16K', 903.1, '903.1', 'pJ per element'),
    ('g_rs_c', 'gs-g-rscp-16K', 969.0, '969.0', 'cycles per instruction'),
    ('g_dr_r', 'gs-g-dram-256K', 1.19, '1.19', 'G elements/s'),
    ('g_dr_e', 'gs-g-dram-256K', 9830, '9,830', 'pJ per element'),
    ('g_dr_c', 'gs-g-dram-256K', 8232, '8,232', 'cycles per instruction'),
    ('s_l1_r', 'gs-s-dram-512B', 452, '452', 'G elements/s'),
    ('s_l1_e', 'gs-s-dram-512B', 14.69, '14.69', 'pJ per element'),
    ('s_l1_c', 'gs-s-dram-512B', 21.78, '21.78', 'cycles per instruction'),
    ('s_l2_r', 'gs-s-dram-4K', 23.5, '23.5', 'G elements/s'),
    ('s_l2_e', 'gs-s-dram-4K', 731.5, '731.5', 'pJ per element'),
    ('s_l2_c', 'gs-s-dram-4K', 417.6, '417.6', 'cycles per instruction'),
    ('s_sp_r', 'gs-s-scp-16K', 23.5, '23.5', 'G elements/s'),
    ('s_sp_e', 'gs-s-scp-16K', 690.5, '690.5', 'pJ per element'),
    ('s_sp_c', 'gs-s-scp-16K', 417.5, '417.5', 'cycles per instruction'),
    ('s_rs_r', 'gs-s-rscp-16K', 10.2, '10.2', 'G elements/s'),
    ('s_rs_e', 'gs-s-rscp-16K', 1983, '1,983', 'pJ per element'),
    ('s_rs_c', 'gs-s-rscp-16K', 958.3, '958.3', 'cycles per instruction'),
    ('s_dr_r', 'gs-s-dram-256K', 0.422, '0.422', 'G elements/s'),
    ('s_dr_e', 'gs-s-dram-256K', 23770, '23,770', 'pJ per element'),
    ('s_dr_c', 'gs-s-dram-256K', 24584, '24,584', 'cycles per instruction'),
    ('g_mh', 'gs-mh', 27.36, '27.36', 'G elements/s'),
    ('g_dram_line', 'gs-dram', 76.4, '76.4 GB/s', ''),
    # die geometry (inferred from a die plot; used to draw the die to scale)
    ('die_w', 'chip.die-dims', 25.7, '25.6-25.8 mm', ''),
    ('die_h', 'chip.die-dims', 22.2, '22.1-22.2 mm', ''),
    ('strip_mm', 'L09', 1.76, '1.76 mm', ''),
    ('grid_mm', 'L08', 22.2, '22.2 mm', ''),
    # the second version's flows (27 Sep): numbers from research facts that the new flows print
    ('peak_tf32', 'mm-peak', 9.83, '9.83 TFLOP/s', ''),
    ('tfma546', 'minion.tensorfma-546', 546, '546 cycles', ''),
    ('e_mac32z', 'e-tfma-fp32-zeros', 0.273, '0.273', 'pJ per multiply-add'),
    ('hot60', 'hot-cost', 60, '60 M/s', ''),
    ('hot031', 'hot-cost', 0.31, '0.31 cycles', ''),
    ('hot1919', 'hot-cost', 1919, '1,919 M/s', ''),
    ('hot32x', 'hot-cost', 32, '32x', '', '32×'),
    ('hot_nj', 'hot-energy', 19.8, '19.8 nJ', ''),
    ('hot_nj_s', 'hot-energy', 1.16, '1.16 nJ', ''),
    ('hot17x', 'hot-energy', 17, '17x', '', '17×'),
    ('lv_fln', 'sync.tree-levels', 71, '68-71 cycles', ''),
    ('lv_xbar', 'sync.tree-levels', 117, '117', ''),
    ('lv_mesh', 'sync.tree-levels', 234, '164-234', ''),
    ('ar32', 'sync-allreduce32', 444, '444 cycles', ''),
    ('ar_us', 'sync-allreduce1024', 2.3, '2.3 us', '', '2.3 µs'),
    ('chipbar_us', 'sync-chip-barrier', 8.3, 'about 8.3 us', '', 'about 8.3 µs'),
    # the broadcast flow (B, 28 Sep): the tree timed with 1 KB, the launch per shire, the pollers
    ('ar32_us', 'sync-allreduce32', 0.74, '0.74 us', '', '0.74 µs'),
    ('chipbar_us2', 'sync-chip-barrier', 8.3, '8.3 us', '', '8.3 µs'),
    ('bc_1k', 'bc.allreduce-1kb', max(med1k), AR1K_T, 'cycles'),
    ('bc_1k_us', 'bc.allreduce-1kb', float(AR1K_US), AR1K_US + ' µs', ''),
    ('bc_1k32', 'bc.allreduce-1kb', statistics.median(all32), AR32K_T + ' cycles', ''),
    ('bc_1k32_us', 'bc.allreduce-1kb', float(AR32K_US), AR32K_US + ' µs', ''),
    ('bc_l1', 'bc.launch-31', round(max(B1), 1), slash(B1), 'µs'),
    ('bc_l31', 'bc.launch-31', round(max(DL), 1), f'{min(DL):.1f}-{max(DL):.1f} µs', ''),
    ('bc_poll', 'bc.pollers', 100, '100%', ''),
    ('bc_512', 'bc.tensorbroadcast', 512, 'minion 512', ''),
]
N += [tuple(r) for r in V2['num']]
DASH = str.maketrans({'–': '-', '‑': '-', '−': '-', ' ': ' ', 'µ': 'u', 'μ': 'u'})
NUMS = re.compile(r'\d[\d,]*(?:\.\d+)?')


def rounds_to(src, disp):
    """True when every number in disp is the matching number of src rounded to disp's decimals."""
    a, b = NUMS.findall(src), NUMS.findall(disp)
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        dec = len(y.split('.')[1]) if '.' in y else 0
        if abs(float(x.replace(',', '')) - float(y.replace(',', ''))) > 0.5 * 10 ** -dec + 1e-9:
            return False
    return True


num = {}
for row in N:
    key, fid, v, t, u = row[:5]
    disp = row[5] if len(row) > 5 else None   # a rounding of t the page prints instead (27 Sep review)
    assert key not in num, key
    f = ALL[fid]
    s = f['statement'].translate(DASH)
    if t.translate(DASH) not in s and not (isinstance(f['value'], (int, float)) and abs(f['value'] - v) < 1e-9 and t == str(v)):
        raise SystemExit(f'{key}: "{t}" not in {fid}: {f["statement"]}')
    if disp and not rounds_to(t, disp):
        raise SystemExit(f'{key}: "{disp}" is not a rounding of "{t}"')
    shown = disp or t
    num[key] = {'v': v, 't': re.sub(r'(?<=\d)-(?=\d)', '–', shown), 'u': u, 'f': fid}
    if disp:
        num[key]['src_t'] = t

# ---- what each details panel lists (components at three zoom levels, then the flows)
COMP = {
    'chip': ['chip.cores-total', 'chip.minion-shires', 'chip.compute-array', 'chip.cm-shire-mask', 'chip.die-area',
             'chip.process', 'chip.die-dims', 'chip.sram-total', 'op-600', 'clock.minion-opps', 'mm-rate',
             'mm-board-w', 'mm-perw', 'power.idle', 'chip.die-revision', 'chip.advertised-range', 'die.handedness', 'fw.map-match'],
    'cshire': ['shire.composition', 'chip.compute-array', 'shire.partition-m0', 'shire.partition-measured',
               'mesh.single-attach', 'L11', 'chip.hop-pitch', 'sync-shire-barrier', 'L123', 'L121'],
    'master': ['fw.grey-cells', 'fw.map-match', 'chip.master-shire-id', 'chip.spare-shire-id', 'L26', 'L31', 'L32', 'chip.compute-array',
               'chip.cm-shire-mask', 'die.handedness'],
    'pcie': ['pcie.negotiated', 'pcie.h2d', 'pcie.d2h', 'pcie.staged', 'pcie.conc', 'pcie.write-l3', 'pcie.nhalf', 'fw.grey-cells', 'chip.pcie-shire',
             'L28', 'pcie.link', 'bw-pcie', 'addr.regions', 'L24', 'die.handedness', 'L25'],
    'io': ['chip.io-shire', 'L29', 'chip.maxions', 'chip.service-processor', 'volt.other', 'L24', 'L32', 'L25', 'fw.grey-cells', 'die.handedness'],
    'memshire': ['chip.memshires', 'L40', 'ms-fit-3cards', 'L41', 'L43', 'L42', 'ms2-forced', 'mesh.grid', 'L44', 'L46', 'L48', 'dram.memshire-select',
                 'dram.controller-policy', 'L47', 'dram.counters', 'L25', 'fw.memshires'],
    'dram': ['dram.channels', 'dram.capacity', 'dram.rate-datasheet', 'dram.rate-card', 'dram.peak-card', 'bw-dram',
             'lat-dram', 'lat-dram-typical', 'lat-dram-chip', 'dram.row-bits', 'lat-dram-rowconflict', 'lat-dram-refresh',
             'e-dram', 'e-dram-tload', 'dram.unmetered', 'dram.placeholder', 'L47', 'dram.pkg-pairing', 'L23'],
    'mesh': ['mesh.grid', 'mesh.logical-map', 'mesh.empty-cells', 'mesh.orientation', 'L34', 'mesh-hop-lat', 'L72',
             'mesh.shortest-paths', 'L104', 'chip.hop-pitch', 'mesh.clock', 'mesh.voltage', 'L102', 'L105',
             'mesh.1kb-knee', 'mesh-hop-ring', 'mesh-bit-mm-free', 'mesh-bit-mm-loaded', 'L91', 'mesh.no-counters', 'fw.map-match', 'die.handedness'],
    'host': ['pcie.negotiated', 'pcie.h2d', 'pcie.d2h', 'pcie.staged', 'pcie.small', 'pcie.poll', 'pcie.launch', 'pcie.conc',
             'pcie.link', 'bw-pcie', 'board.card', 'board.meters', 'ridge.levels'],
    # shire level
    'meshstop': ['mesh.single-attach', 'L103', 'mesh.port-width', 'L114', 'mesh-hop-lat', 'L91'],
    'banks': ['shire.cache-geometry', 'L111', 'shire.partition-m0', 'shire.other-modes', 'shire.bank-queues',
              'shire.sc-latency-spec', 'l2.decode', 'l3.bank', 'volt.sram', 'sram-idle'],
    'l2': ['l2.private', 'lat-l2', 'lat-rb', 'l2.read-buffer', 'bw-l2', 'shire.l2-bw-spec', 'e-l2', 'l2.decode', 'l2.latency'],
    'l3': ['l3.capacity', 'l3.home', 'l3.latency', 'lat-l3-hop', 'lat-l3-avg', 'L79', 'L80', 'bw-l3', 'e-l3', 'l3.bank',
           'l3.writearound', 'mem.global-atomic', 'sync.flag-memory', 'sc.l3-miss'],
    'scp': ['scp.size', 'lat-scp-own', 'bw-scp-own', 'e-scp-own-zeros', 'e-scp-own-rand', 'lat-scp-remote',
            'bw-scp-remote', 'e-scp-remote-zeros', 'e-scp-remote-rand', 'scp.format0', 'scp.format1', 'scp.offset0'],
    'uc': ['shire.composition', 'sync.flb', 'sync.fcc', 'sync-shire-barrier', 'sync-chip-barrier', 'ts-credit',
           'hot-cost', 'hot-edge', 'hot-energy'],
    'xbar': ['shire.crossbar', 'shire.neigh-link', 'L114', 'ts-rt-fln'],
    'neigh': ['neigh.composition', 'L115', 'neigh.fln-edges', 'L116', 'neigh.fln-latency-spec', 'bw-tsend-fln',
              'ts-e-pair', 'sync.tree-levels', 'sync-allreduce32', 'sync-allreduce1024', 'neigh.coop-tload', 'neigh.pmu',
              'neigh.ptw'],
    # minion level
    'minion': ['minion.isa', 'chip.harts', 'minion.vec-peak', 'clock.minion-opps', 'volt.minion', 'e-awake', 'e-nop', 'e-add', 'e-fadd',
               'minion.no-divide', 'minion.sleep-unused'],
    'hart': ['minion.isa', 'chip.harts', 'minion.tensor-hart0', 'minion.vpu-regs', 'lat-l1', 'l2.latency'],
    'vpu': ['minion.vpu', 'minion.vec-peak', 'minion.vpu-regs', 'minion.vpu-pipeline', 'minion.l1-port', 'e-fmadd-ps', 'e-fadd-ps',
            'e-fexp-ps', 'minion.vector-rate'],
    'tensor': ['minion.vec-peak', 'minion.vpu', 'mm-peak', 'mm-rate', 'minion.tensorfma-546', 'minion.tensor-shape', 'minion.tenb-tenc',
               'minion.tensor-hart0', 'e-tfma-fp32', 'e-tfma-fp16', 'e-tfma-int8', 'e-tfma-fp32-zeros', 'mm-perw',
               'minion.tensorload', 'minion.tensor-cache-path', 'minion.tensor-csrs'],
    'l1d': ['minion.l1d', 'minion.l1-modes', 'minion.l1-firmware', 'minion.miss-handlers', 'lat-l1', 'bw-l1', 'e-l1',
            'e-l1-cat', 'e-l1-fill', 'e-dram-writeback'],
    'l1scp': ['minion.l1-modes', 'minion.tensorload', 'minion.tensor-shape', 'minion.tensorfma-546', 'e-scp-tload'],
    'etlink': ['minion.etlink-width', 'shire.neigh-link', 'addr.load-path', 'minion.miss-handlers', 'shire.crossbar'],
    'fln': ['neigh.fln-edges', 'ts-rt-fln', 'neigh.fln-latency-spec', 'minion.msg-cost', 'bw-tsend-link',
            'minion.tensorsend', 'minion.one-ready-bit', 'minion.combine-free', 'sync-allreduce1024', 'sync.tree-levels'],
    # flows
    'flowA': ['addr.load-path', 'addr.load-model', 'L45', 'l2.decode', 'l3.home', 'dram.memshire-select', 'L43',
              'dram.row-bits', 'L50', 'lat-l1', 'lat-l2', 'l3.latency', 'dram.leg', 'lat-dram-typical', 'lat-dram',
              'L46', 'lat-dram-chip', 'e-l1', 'e-l2', 'e-l3', 'e-dram', 'mesh-hop-lat', 'L104', 'mesh.memshire-positions', 'sc.l3-miss'],
    'flowB': ['lat-l1', 'lat-rb', 'lat-l2', 'lat-scp-own', 'lat-scp-remote', 'lat-l3-hop', 'l3.latency', 'lat-l3-avg',
              'dram.leg', 'lat-dram-typical', 'lat-dram', 'bw-l1', 'bw-l2', 'bw-scp-own', 'bw-scp-remote', 'bw-l3',
              'bw-dram', 'e-l1', 'e-l2', 'e-scp-own-zeros', 'e-scp-own-rand', 'e-scp-remote-zeros',
              'e-scp-remote-rand', 'e-l3', 'e-dram', 'L104'],
    'flowC': ['ts-rt-mesh', 'L70', 'L71', 'L72', 'minion.tensorsend', 'mesh-hop-ring', 'L86', 'L87', 'bw-tsend-mesh',
              'bw-tsend-link', 'mesh.1kb-knee', 'minion.one-ready-bit', 'L104'],
    'flowD': ['relay-energy', 'relay-13x', 'relay-bw', 'relay.speedup', 'L93', 'L94', 'relay-watts', 'e-dram-vs-scp',
              'addr.load-path', 'minion.tensor-cache-path', 'l3.home', 'dram.memshire-select', 'L104'],
    'flowE': ['gs-g-dram-512B', 'gs-g-dram-4K', 'gs-g-scp-16K', 'gs-g-rscp-16K', 'gs-g-dram-256K', 'gs-s-dram-512B',
              'gs-s-dram-4K', 'gs-s-scp-16K', 'gs-s-rscp-16K', 'gs-s-dram-256K', 'gs-mh', 'gs-dram', 'gs-l1', 'gs-uc',
              'gs-add', 'gs-card', 'L104'],
    'flowF': ['pcie.negotiated', 'pcie.h2d', 'pcie.d2h', 'pcie.staged', 'pcie.nhalf', 'pcie.small', 'pcie.poll', 'pcie.launch',
              'pcie.conc', 'pcie.write-l3', 'l3.home', 'bw-pcie', 'chip.pcie-shire', 'addr.regions', 'addr.dram-region', 'dram.memshire-select',
              'fw.grey-cells', 'chip.master-shire-id', 'chip.cm-shire-mask', 'L104'],
    # the second version's flows (27 Sep): 7 the matmul's data flow, 8 data sets the watts, 9 the hot line, 0 the allreduce
    'flowG': ['minion.tensorload', 'tl.one', 'tl.all', 'minion.tensorfma-546', 'tfma.tenb', 'mm.reload', 'minion.tensor-hart0',
              'minion.vec-peak', 'mm-peak', 'mm-rate', 'neigh.coop-tload', 'minion.tensor-cache-path', 'mm.dram', 'e-scp-tload',
              'e-dram-tload', 'e-tfma-fp32', 'L104'],
    'flowH': ['mm.w-data', 'mm.w-3cards', 'e-tfma-fp32', 'e-tfma-fp32-zeros', 'heat.race', 'heat.fewer', 'heat.leak',
              'mm-board-w', 'power.idle', 'board.meters', 'mm-rate'],
    'flowI': ['hot.fair', 'hot-cost', 'hot.cliff', 'hot-edge', 'hot-energy', 'mem.global-atomic', 'L43', 'l3.home'],
    'flowJ': ['ar.tree', 'neigh.fln-edges', 'sync.tree-levels', 'sync-allreduce32', 'sync-allreduce1024', 'sync-shire-barrier',
              'sync-chip-barrier', 'sync.flb', 'sync.fcc', 'ts-rt-fln', 'L104'],
    # the broadcast (B, 28 Sep): the tree, the relay against DRAM, one line read by everyone, the launch's multicast
    'flowK': ['minion.vpu-regs', 'minion.tensor-hart0', 'bc.tensorbroadcast', 'ar.tree', 'neigh.fln-edges', 'sync.tree-levels',
              'sync-allreduce32', 'sync-allreduce1024', 'bc.allreduce-1kb', 'bc.half', 'ts-e-pair', 'relay-energy', 'relay-13x',
              'relay-bw', 'e-dram', 'bw-dram', 'l3.home', 'l3.latency', 'bc.one-request', 'e-l3', 'hot-cost', 'bc.pollers',
              'hot.cliff', 'mem.global-atomic', 'bc.esr-ipi', 'bc.launch-multicast', 'bc.launch-31', 'pcie.launch', 'pcie.poll',
              'sync-chip-barrier', 'L104'],
}
used = set(v['f'] for v in num.values())
for k, ids in COMP.items():
    for i in ids:
        if i not in ALL:
            raise SystemExit(f'{k}: no fact {i}')
    used.update(ids)
# facts the honest note and the text cite by id
NOTE = ['mesh.orientation', 'L33', 'L34', 'L32', 'L24', 'L42', 'L40', 'L104', 'mesh.xy-assumption', 'mesh.shortest-paths',
        'chip.die-dims', 'L114', 'chip.hop-pitch', 'addr.load-model', 'L37', 'chip.io-shire', 'L47', 'L23', 'dram.pkg-pairing',
        'ms-fit-3cards', 'ms2-forced', 'mesh.grid', 'fw.map-match', 'fw.grey-cells', 'fw.memshires', 'die.handedness',
        'sc.l3-miss', 'pcie.write-l3', 'L50', 'minion.tensor-cache-path', 'pcie.conc']
for i in NOTE:
    assert i in ALL, i
used.update(NOTE)

for a in ASKS:
    for i in a['facts']:
        assert i in ALL, (a['part'], i)
    used.update(a['facts'])
# ---- the deep zoom (30 Sep 2026, the owner's request: zoom out to the universe, in to the circuit components):
# the scale nodes, their facts (in.*, out.*, size.*), the map outlines, the image manifest, and the memory-levels
# facts and numbers that the tree cites and the drawings copied from that page print (research/deepzoom.py says how)
import sys
sys.path.insert(0, R)
import deepzoom  # noqa: E402
CKT = os.path.join(HERE, '..', '..', 'sources', 'circuitkit.js')
ckt = open(CKT).read() if os.path.exists(CKT) else ''
# the memory-levels numbers the copied drawings print (mlnt('…'), mlnf('…'), mln('…')) and the facts they cite by id
ML_NUM = sorted(set(re.findall(r"\b(?:nt|nf|n|K)\('([A-Za-z0-9_]+)'", ckt)))
ML_FIDS = sorted(set(m.group(0) for m in re.finditer(r"\b(?:l1|l2|l3|scp|dram|g):[a-z0-9][A-Za-z0-9_.\-]*[A-Za-z0-9]", ckt)))
DZ = deepzoom.build(ALL, ML_FIDS, ML_NUM)
used.update(DZ['used_chip'])
facts = {i: norm(ALL[i]) for i in sorted(used)}
for i, f in DZ['facts'].items():
    assert i not in facts, i
    facts[i] = f
# the page reads a fact's statement, kind, source, note, page link, cards and caveat: the other fields (kept in the
# research files) stay out of the page's data, as do empty ones (30 Sep: the page carries 700-odd facts now)
# (the chip's own facts also keep topic, value and unit: the memory levels' build_facts.py copies them for the facts it
# imports, chip:mesh.grid, L40 and the others; review of 1 Oct 2026. Build order: this file reads the memory levels'
# facts.json and that page's build reads this one; both are fixed points, see MIRROR.md)
KEEP = ('statement', 'kind', 'source', 'note', 'url', 'page', 'cards', 'cards_txt', 'card', 'caveat')
KEEP_CHIP = KEEP + ('topic', 'value', 'unit')
for i, f in list(facts.items()):
    dz = f.get('set') in ('deep zoom', 'memory-levels')
    g = {k: f[k] for k in (KEEP if dz else KEEP_CHIP) if f.get(k) not in (None, [], '')}
    if dz:
        g['dz'] = 1
    facts[i] = g
kinds = {}
for f in facts.values():
    kinds[f['kind']] = kinds.get(f['kind'], 0) + 1
out = {
    'meta': {'built_from': ['research/facts-arch.json', 'research/facts-layout.json', 'research/facts-numbers.json',
                            'research/facts-v2.json', 'research/layout.json', 'research/asks.json',
                            '../../sources/limits-of-observability.data.json (the hub rows the asks link to)'],
             'n_facts': len(facts), 'kinds': kinds, 'n_num': len(num), 'et_platform_head': '836a4ab'},
    'facts': facts, 'num': num, 'comp': COMP, 'layout': layout, 'asks': ASKS, 'rungs': RUNGS,
    'scales': DZ['scales'], 'geo': DZ['geo'], 'img': DZ['img'], 'mlnum': DZ['ml_num'], 'mladdr': DZ['ml_addr'], 'onum': DZ['onum'], 'outside': DZ['outside_meta'],
}
p = os.path.join(HERE, 'facts.json')
json.dump(out, open(p, 'w'), indent=1, ensure_ascii=False)
print('wrote', p, len(facts), 'facts', kinds, len(num), 'numbers')
