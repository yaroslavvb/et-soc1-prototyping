#!/usr/bin/env python3
"""Facts for the chip diagram's second version (27 September 2026), read from the repository's data files.

    python3 docs/reports/data/2026-09-27-chip-diagram/research/build_facts_v2.py   # writes facts-v2.json beside it

Every number in a statement below is formatted here from a data file's field; nothing is typed in by hand except the
card order and the line numbers cited in the sources. The output has two lists:
  facts  the facts, in the research files' format (id, component, topic, statement, value, unit, source, kind, card,
         page, url, note)
  num    rows for build_facts.py's table of printed numbers: [key, fact id, value, text, unit]; the text is the one
         formatted into that fact's statement, and build_facts.py checks again that it occurs there

The groups: the PCIe link and the launch path, timed on three cards on 27 September (docs/reports/data/2026-09-27-pcie);
the firmware's shire map against the measured one (research/firmware_map.json); the tensor unit's data flow and the
matmul benchmark (claims-v3 lat.json, mmb.json); the same matmul on different data, its watts and its heat
(horace3.json, abla.json, long.json, model.json); the hot line's fairness and cliff (hotline.json); the allreduce tree
as the benchmark kernel builds it (workloads/nocbench/kernel/nocbench.c); and the shire cache's L3 miss path (the
CORE-ET Shire Cache Specification).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
DATA = os.path.join(REPO, 'docs', 'reports', 'data')
J = lambda p: json.load(open(os.path.join(DATA, p)))
CARDS = ['aifoundry2', 'aifoundry3', 'aifoundry1-c1']
CARDS_TXT = 'aifoundry2, aifoundry3, aifoundry1-c1'
SLASH = 'aifoundry2 / aifoundry3 / aifoundry1-c1'
PCIE_URL = 'https://spacesheep.dev/@yaroslavvb/et-soc1-pcie-link'
PCIE_PAGE = 'Over the PCIe link'
HOT_URL = 'https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line'
HOT_PAGE = 'One hot line stops a shire'
MM_URL = 'https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency'
MM_PAGE = 'Matmul efficiency'
HOR_URL = 'https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment'
HOR_PAGE = 'The Horace experiment'
OC_URL = 'https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication'
OC_PAGE = 'On-chip communication'

FACTS, NUM = [], []


def fmt(v, dp):
    s = f'{v:,.{dp}f}'
    return s


def rng(vals, dp, sep='-'):
    lo, hi = fmt(min(vals), dp), fmt(max(vals), dp)
    return lo if lo == hi else lo + sep + hi


def per(vals, dp):
    return ' / '.join(fmt(v, dp) for v in vals)


def fact(fid, comp, topic, kind, statement, value, unit, source, card, page=None, url=None, note=None):
    FACTS.append({'id': fid, 'component': comp, 'topic': topic, 'kind': kind, 'statement': statement, 'value': value,
                  'unit': unit, 'source': source, 'card': card, 'page': page, 'url': url, 'note': note})


def num(key, fid, v, t, u=''):
    st = next(f['statement'] for f in FACTS if f['id'] == fid)
    assert t in st, (key, t, st)
    NUM.append([key, fid, v, t, u])


def item(d, name):
    items = d['items'] if isinstance(d, dict) else d
    return next(i for i in items if i['item'] == name)


# ======================= the PCIe link and the launch path (27 September, three cards) =======================
P = J('2026-09-27-pcie/pcie.json')
PF = 'docs/reports/data/2026-09-27-pcie/pcie.json'
BIG = 268435456
link = P['meta']['link_gbs']
speeds = {P['hosts'][c]['link_speed'] for c in CARDS}
widths = {P['hosts'][c]['link_width'] for c in CARDS}
assert speeds == {'16.0 GT/s PCIe'} and widths == {8}, (speeds, widths)
fact('pcie.negotiated', 'pcie', 'interconnect', 'measured',
     f'The link trained at 16.0 GT/s x8 on all three cards in every run (sysfs current_link_speed and '
     f'current_link_width): PCIe Gen4 x8, {link:.2f} GB/s per direction after 128b/130b coding.',
     16.0, 'GT/s', f'{PF}: hosts.<card>.link_speed, .link_width; meta.link_gbs; docs/reports/data/2026-09-27-pcie/hosts.txt',
     CARDS_TXT, PCIE_PAGE, PCIE_URL)
num('pcie_neg', 'pcie.negotiated', 16.0, '16.0 GT/s x8')
num('pcie_link', 'pcie.negotiated', round(link, 2), f'{link:.2f} GB/s')


def bw_at(c, d, kind, size=BIG):
    return next(e for e in P['bw'][c][d][kind] if e['bytes'] == size)['gbs']


def ci(v, dp=2):
    m = v['mean'] if 'mean' in v else v['point']
    return f'{m:.{dp}f} [{v["lo"]:.{dp}f}, {v["hi"]:.{dp}f}]'


h2d = [bw_at(c, 'h2d', 'dma') for c in CARDS]
d2h = [bw_at(c, 'd2h', 'dma') for c in CARDS]
h2d_pct = [100 * v['mean'] / link for v in h2d]
d2h_pct = [100 * v['mean'] / link for v in d2h]
fact('pcie.h2d', 'pcie', 'bandwidth', 'measured',
     'Host to device, DMA only (the runtime\'s host-side copy replaced by a no-op, the analogue of pinned memory), 256 MB '
     'per copy: ' + ', '.join(f'{ci(v)} GB/s on {c}' for v, c in zip(h2d, CARDS)) +
     f' (mean of 5 runs [99% interval]): {rng([v["mean"] for v in h2d], 2)} GB/s, '
     f'{rng(h2d_pct, 0)}% of the link\'s {link:.2f} GB/s.',
     round(h2d[0]['mean'], 2), 'GB/s (aifoundry2)', f'{PF}: bw.<card>.h2d.dma[bytes=268435456].gbs (mean, lo, hi)',
     CARDS_TXT, PCIE_PAGE, PCIE_URL)
num('pcie_h2d', 'pcie.h2d', round(max(v['mean'] for v in h2d), 2), rng([v['mean'] for v in h2d], 2), 'GB/s')
num('pcie_h2d_pct', 'pcie.h2d', round(max(h2d_pct)), rng(h2d_pct, 0) + '%')
d2h_peak = [max(P['bw'][c]['d2h']['dma'], key=lambda e: e['gbs']['mean']) for c in CARDS]
fact('pcie.d2h', 'pcie', 'bandwidth', 'measured',
     'Device to host, DMA only, 256 MB per copy: ' + ', '.join(f'{ci(v)} GB/s on {c}' for v, c in zip(d2h, CARDS)) +
     f': {rng([v["mean"] for v in d2h], 2)} GB/s, {rng(d2h_pct, 0)}% of the link figure, slower than host to device. '
     'The fastest device-to-host size is ' + ', '.join(f'{e["bytes"] >> 20} MB on {c} ({e["gbs"]["mean"]:.2f} GB/s)'
                                                        for e, c in zip(d2h_peak, CARDS)) + '.',
     round(d2h[0]['mean'], 2), 'GB/s (aifoundry2)', f'{PF}: bw.<card>.d2h.dma[bytes=268435456].gbs; the size of the '
     'largest bw.<card>.d2h.dma[].gbs.mean', CARDS_TXT, PCIE_PAGE, PCIE_URL)
num('pcie_d2h', 'pcie.d2h', round(max(v['mean'] for v in d2h), 2), rng([v['mean'] for v in d2h], 2), 'GB/s')
num('pcie_d2h_pct', 'pcie.d2h', round(max(d2h_pct)), rng(d2h_pct, 0) + '%')

sh = [bw_at(c, 'h2d', 'staged')['mean'] for c in CARDS]
sd = [bw_at(c, 'd2h', 'staged')['mean'] for c in CARDS]
mc = [next(e for e in P['hostcopy'][c] if e['bytes'] == BIG)['gbs']['mean'] for c in CARDS]
serial = []
for i in range(3):
    for s, d in ((sh[i], h2d[i]['mean']), (sd[i], d2h[i]['mean'])):
        serial.append(100 * s / (1 / (1 / d + 1 / mc[i])))
# aifoundry3's staged rate against each other host's, host to device (its host memcpy is the slowest)
slow = [sh[1] / sh[0], sh[1] / sh[2]]
fact('pcie.staged', 'pcie', 'bandwidth', 'measured',
     'The path a program takes, the runtime\'s staged copy (a host memcpy into a CMA bounce buffer, then the DMA), '
     f'256 MB: host to device {per(sh, 2)} GB/s ({rng(sh, 2)}), device to host {per(sd, 2)} GB/s ({SLASH}). The hosts\' own memcpy '
     f'runs at {per(mc, 1)} GB/s, and each staged rate is {rng(serial, 0)}% of 1/(1/DMA + 1/memcpy): the runtime copies '
     'and then transfers, one after the other, so a slow host memcpy (aifoundry3\'s) cuts the staged rate on the same '
     f'link to {rng(slow, 2)} of the other hosts\' (host to device).',
     round(sh[0], 2), 'GB/s (aifoundry2, host to device)',
     f'{PF}: bw.<card>.<h2d|d2h>.staged[bytes=268435456].gbs.mean, hostcopy.<card>[bytes=268435456].gbs.mean; '
     'the ratio computed here', CARDS_TXT, PCIE_PAGE, PCIE_URL)
num('pcie_stg_h', 'pcie.staged', round(sh[0], 2), per(sh, 2), 'GB/s')
num('pcie_stg_rng', 'pcie.staged', round(max(sh), 2), rng(sh, 2), 'GB/s')
num('pcie_memcpy', 'pcie.staged', round(mc[0], 1), per(mc, 1), 'GB/s')

nh = [2 ** P['n_half_log2'][c]['h2d_dma']['mean'] / 2 ** 20 for c in CARDS]
fact('pcie.nhalf', 'pcie', 'bandwidth', 'measured',
     f'A DMA-only host-to-device copy reaches half its 256 MB rate at {per(nh, 1)} MB per copy ({SLASH}; '
     'n½, from the mean over five runs of log2 of the size): smaller copies are dominated by the per-command time.',
     round(nh[0], 1), 'MB (aifoundry2)', f'{PF}: n_half_log2.<card>.h2d_dma.mean (log2 bytes)', CARDS_TXT, PCIE_PAGE, PCIE_URL)
num('pcie_nhalf', 'pcie.nhalf', round(nh[0], 1), per(nh, 1), 'MB')

sp = [sum(v['mean_us']['mean'] for v in P['lat'][c]['sporadic'].values()) / len(P['lat'][c]['sporadic']) for c in CARDS]
pipe = [P['lat'][c]['pipelined_us_per_copy']['h2d_staged']['mean'] for c in CARDS]
idle = [P['lat'][c]['idle_wait_us']['mean'] for c in CARDS]
fact('pcie.small', 'pcie', 'latency', 'measured',
     f'A 4 KB copy issued after a random 0-1 ms gap takes {per(sp, 0)} µs on average ({rng(sp, 0)} µs; {SLASH}; the mean over the four '
     f'copy variants), while 200 queued 4 KB copies take {per(pipe, 0)} µs each (host to device, staged) and a wait on '
     f'an idle stream {per(idle, 1)} µs. The time of a lone small copy is the runtime\'s response polling, not the link.',
     round(sp[0]), 'µs (aifoundry2)', f'{PF}: lat.<card>.sporadic.<variant>.mean_us.mean (averaged over the four), '
     'lat.<card>.pipelined_us_per_copy.h2d_staged.mean, lat.<card>.idle_wait_us.mean', CARDS_TXT, PCIE_PAGE, PCIE_URL)
num('pcie_4k_rng', 'pcie.small', round(max(sp)), rng(sp, 0) + ' µs')
num('pcie_4k', 'pcie.small', round(max(sp)), per(sp, 0))
num('pcie_q', 'pcie.small', round(max(pipe)), per(pipe, 0))

fact('pcie.poll', 'host', 'latency', 'spec',
     'The runtime\'s response thread polls the device\'s completion queue, sleeping 50 µs between polls while commands '
     'are in flight and 500 µs when none are.', 50, 'µs',
     'external/et-platform/esperanto-tools-libs/src/ResponseReceiver.cpp:21-22 (kResponsePollingIntervalWithEventsOnFly '
     '= 50us, kResponsePollingIntervalNoEventsOnFly = 500us), :62-63', None, PCIE_PAGE, PCIE_URL,
     'aifoundry3 runs a patched libetrt.so and aifoundry1 a fork build, so their constants may differ (PREREG.md).')
num('poll50', 'pcie.poll', 50, '50 µs')
num('poll500', 'pcie.poll', 500, '500 µs')

one = [P['launch'][c]['single_us']['32']['mean'] for c in CARDS]
one1 = [P['launch'][c]['single_us']['1']['mean'] for c in CARDS]
b32 = [P['launch'][c]['b2b_us']['32']['mean'] for c in CARDS]
b1 = [P['launch'][c]['b2b_us']['1']['mean'] for c in CARDS]
p9b = next(p for p in P['predictions'] if p['id'] == 'P9b')['per_card']
wait = [p9b[c]['value']['mean'] for c in CARDS]
fact('pcie.launch', 'host', 'latency', 'measured',
     f'An empty kernel on all 32 compute shires, launched and waited for: {per(one, 0)} µs ({rng(one, 0)} µs) from launch to completion '
     f'({SLASH}); 100 launches queued back to back: {per(b32, 1)} µs each ({rng(b32, 1)} µs) on 32 shires and {per(b1, 1)} on one shire. '
     f'The card\'s own cost is the queued figure: a lone launch waited for adds {per(wait, 0)} µs ({rng(wait, 0)} µs, each run\'s '
     f'difference), most of the runtime\'s 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same '
     f'{per(one1, 0)} µs.',
     round(one[0]), 'µs (aifoundry2)', f'{PF}: launch.<card>.single_us."32".mean, launch.<card>.b2b_us."32".mean, '
     '.b2b_us."1".mean, .single_us."1".mean; predictions[id=P9b].per_card.<card>.value.mean (launch to completion minus '
     'back-to-back, per run)', CARDS_TXT, PCIE_PAGE, PCIE_URL)
num('pcie_launch', 'pcie.launch', round(max(one)), per(one, 0))
num('pcie_launch_rng', 'pcie.launch', round(max(one)), rng(one, 0) + ' µs')
num('pcie_b2b_rng', 'pcie.launch', round(max(b32), 1), rng(b32, 1) + ' µs')
num('pcie_b2b', 'pcie.launch', round(b32[0], 1), per(b32, 1))
num('pcie_wait_rng', 'pcie.launch', round(max(wait)), rng(wait, 0) + ' µs')

one_s = [P['conc'][c]['dma']['h2d']['agg_gbs']['mean'] for c in CARDS]
ser = [P['conc'][c]['dma']['h2d/ser']['agg_gbs']['mean'] for c in CARDS]
two = [P['conc'][c]['dma']['2xh2d']['agg_gbs']['mean'] for c in CARDS]
dup = [P['conc'][c]['dma']['h2d+d2h/ser']['agg_gbs']['mean'] for c in CARDS]
fact('pcie.conc', 'pcie', 'bandwidth', 'measured',
     f'Two host-to-device commands in flight on one stream move {per(one_s, 2)} GB/s ({SLASH}), half the '
     f'{per(ser, 2)} GB/s of one command at a time (two streams: {per(two, 2)} GB/s in total); both directions at '
     f'once, one command each at a time, move {per(dup, 2)} GB/s together (2 × 64 MB per stream, DMA only).',
     round(dup[0], 2), 'GB/s (aifoundry2, both directions)', f'{PF}: conc.<card>.dma.h2d.agg_gbs.mean (no barrier: '
     'both commands of the stream in flight), ."h2d/ser" (a barrier on every copy), ."2xh2d", ."h2d+d2h/ser"',
     CARDS_TXT, PCIE_PAGE, PCIE_URL)
num('pcie_two', 'pcie.conc', round(one_s[0], 2), per(one_s, 2), 'GB/s')
num('pcie_ser', 'pcie.conc', round(ser[0], 2), per(ser, 2), 'GB/s')
num('pcie_dup', 'pcie.conc', round(dup[0], 2), per(dup, 2), 'GB/s')

# ======================= the firmware's shire map against the measured one =======================
FW = json.load(open(os.path.join(HERE, 'firmware_map.json')))
FWF = 'docs/reports/data/2026-09-27-chip-diagram/research/firmware_map.json'
A, W = FW['comment_map_after_remap'], FW['comment_map_as_written']
assert A['best_symmetry'] == {'swap_axes': False, 'flip_first': False, 'flip_second': False, 'shires_at_same_cell': 32}
fact('fw.map-match', 'mesh', 'placement', 'derived',
     f'Renamed as the boot firmware renames the shires (NOC_Remap_Shires with its \'No displacement\' table, used when '
     f'no shire is fused off), the firmware\'s \'default Shire Virtual ID Map, based on the NOC spec\' matches the '
     f'measured map: {A["pair_distances_equal"]} of {A["pairs"]} pair distances and '
     f'{A["best_symmetry"]["shires_at_same_cell"]} of 32 cells, with no rotation or mirror. As written, before the '
     f'renaming, only {W["pair_distances_equal"]} of {W["pairs"]} pair distances agree (fact L37).',
     A['pair_distances_equal'], 'pair distances',
     f'{FWF}: comment_map_after_remap.pair_distances_equal, .best_symmetry, comment_map_as_written; firmware_map.py '
     'beside it; external/et-platform/device-bootloaders/src/ServiceProcessorBL2/include/noc_reconfigure.h:76-82, '
     '398-405; ServiceProcessorBL2/common/main.c:275-286', None)
num('fw_pairs', 'fw.map-match', A['pair_distances_equal'], f'{A["pair_distances_equal"]} of {A["pairs"]}')
g = FW['grey_cells']
assert g['(0, 3)']['kernel_shire_id'] == 32 and g['(5, 3)']['kernel_shire_id'] == 33
assert g['(0, 4)']['bridge_map_entry'] == 'pcie0' and g['(0, 5)']['bridge_map_entry'] == 'io0'
fact('fw.grey-cells', 'master', 'placement', 'spec',
     'In the firmware\'s maps the four cells that hold no compute shire are: logical (0, 3), shire 32, the master; '
     '(5, 3), shire 33, the spare; (0, 4), the PCIe shire (\'pcie0\' in the bridge map); and (0, 5), the I/O shire '
     '(\'io0\'). On this die view that puts the master in the north cell and the spare in the south one, with PCIe '
     'then I/O east of the master.', None, None,
     f'{FWF}: grey_cells; external/et-platform/device-bootloaders/src/ServiceProcessorBL2/include/noc_reconfigure.h:'
     '76-90', None, note='To confirm on the cards: time a counter read on shire 32 from each compute shire '
                         '(the hub\'s rung exp-mesh-stops).')
ms = FW['memshires']
assert ms['agree'] == 8
# the fit places 7 memory shires on its own; memory shire 2 is its tie-break (layout.json), forced once the 7 are in place
LAYOUT = json.load(open(os.path.join(HERE, 'layout.json')))
assert [m['id'] for m in LAYOUT['memshires'] if m.get('tie_break')] == [2]
fact('fw.memshires', 'memory shire', 'placement', 'spec',
     'The firmware\'s map puts memory shires mc0-mc3 at logical rows 1-4 on the west (y = -1) and mc4-mc7 at rows '
     '1-4 on the east (y = 6): the DRAM-latency fit\'s places for the 7 memory shires the fit places on its own, '
     'provided the firmware\'s mcN is the memory shire that PA[8:6] = N selects. With those 7 in place, memory shire 2 '
     'has one cell left in the firmware\'s map as in the fit (fact ms2-forced): the map confirms the frame, not memory '
     'shire 2\'s place independently.', 7, 'memory shires agreeing independently',
     f'{FWF}: memshires.firmware_rows, .fit_positions, .agree; noc_reconfigure.h:76-82; '
     'docs/reports/data/2026-09-27-chip-diagram/research/layout.json memshires[].tie_break', None,
     note='Timing a counter read on each memory shire from every compute shire (the hub\'s rung exp-mesh-stops) would '
          'place memory shire 2 directly.')
fact('die.handedness', 'chip', 'placement', 'inferred',
     'The die view follows the firmware\'s NoC-spec drawing and the Programmer\'s Reference Manual\'s Fig. 1-3: '
     'memory shires 0-3 on the west, PCIe then I/O at the east end of the top row. The published die plot draws '
     'I/O then PCIe, its mirror image; no document in the open drop says which handedness the silicon has.', None, None,
     f'{FWF}; fact L24 (PRM Fig. 1-3 against the die plot)', None)

# ======================= the L3 miss path (the reply of a DRAM load) =======================
fact('sc.l3-miss', 'l3', 'path', 'spec',
     'An L3 read from another shire enters the home shire\'s cache through its L3 slave port and moves down the '
     'pipeline as L3_Read and L3_Fill: a miss goes out the to_sys mesh port to memory, the data comes back as the L3 '
     'fill, and the home answers the requester. The order memory shire, L3 home, requester is the specification\'s; '
     'which way each leg turns on the mesh is not documented.', None, None,
     'external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf, pdf p.55 (§3.2.2 \'L3 REQ_Read\': \'They are '
     'received from the L3_slave and move down the pipeline as L3_Read and L3_Fill. Misses and victims are directed '
     'to the to_sys mesh port.\', Figure 14)', None)

# ======================= the tensor unit's data flow (claims-v3, three cards) =======================
LAT = J('2026-09-25-claims-v3/results/lat.json')
LF = 'docs/reports/data/2026-09-25-claims-v3/results/lat.json'
s2 = item(LAT, 'LAT-S2')
pm = {c: s2['per_card'][c]['pass_means'] for c in CARDS}
l216 = [pm[c]['l216']['mean'] for c in CARDS]
scp16 = [pm[c]['scp16']['mean'] for c in CARDS]
l24 = [pm[c]['l24']['mean'] for c in CARDS]
warm = [p['dram16'] for c in CARDS for p in s2['per_card'][c]['passes'] if p.get('kept', True) and p['pass'] > 1]
cold = [p['dram16'] for c in CARDS for p in s2['per_card'][c]['passes'] if p['pass'] == 1]
fact('tl.one', 'l1scp', 'latency', 'measured',
     f'One minion\'s TensorLoad of 16 lines (1 KB) into its L1 scratchpad: {rng(l216, 1)} cycles from the L2 and '
     f'{rng(scp16, 1)} from the own scratchpad, on all three cards; 4 lines from the L2 take {rng(l24, 1)} cycles. From DRAM, '
     f'16 lines take {rng(warm, 0)} cycles on passes 2 and 3 and {rng(cold, 0)} on the first pass.',
     round(l216[0], 1), 'cycles', f'{LF}: [item=LAT-S2].per_card.<card>.pass_means.l216, .scp16, .l24 (mean); '
     '.passes[].dram16', CARDS_TXT, HOR_PAGE, HOR_URL)
num('tl_l2', 'tl.one', round(l216[0], 1), rng(l216, 1), 'cycles')
num('tl_dram', 'tl.one', round(max(warm)), rng(warm, 0), 'cycles')
s3 = item(LAT, 'LAT-S3')
all_l2 = [s3['per_card'][c]['pass_means']['l2_n200000']['mean'] for c in CARDS]
all_dr = [s3['per_card'][c]['pass_means']['dram_all16']['mean'] for c in CARDS]
fact('tl.all', 'l1scp', 'bandwidth', 'measured',
     f'All 1,024 minions tensor-loading at once: {rng(all_l2, 1)} cycles per 16-line load from the L2, and '
     f'{rng(all_dr, 0)} cycles from DRAM ({SLASH}: {per(all_dr, 0)}), where the memory shires set the pace.',
     round(all_l2[0], 1), 'cycles', f'{LF}: [item=LAT-S3].per_card.<card>.pass_means.l2_n200000, .dram_all16 (mean)',
     CARDS_TXT, HOR_PAGE, HOR_URL)
num('tl_all_l2', 'tl.all', round(all_l2[0], 1), rng(all_l2, 1), 'cycles')
num('tl_all_dr', 'tl.all', round(max(all_dr)), rng(all_dr, 0), 'cycles')
s1 = item(LAT, 'LAT-S1')
tenb = [x for c in CARDS for p in s1['per_card'][c]['passes'] for x in p['529.1']]
fact('tfma.tenb', 'tensor', 'latency', 'measured',
     f'A 16×16×16 fp32 TensorFMA with B streamed through TenB instead of held in the L1 scratchpad: {rng(tenb, 2)} '
     'cycles on all three cards (A in the L1 scratchpad).', round(min(tenb), 2), 'cycles',
     f'{LF}: [item=LAT-S1].per_card.<card>.passes[]."529.1" (each pass\'s interval)', CARDS_TXT, HOR_PAGE, HOR_URL)
num('tfma_tenb', 'tfma.tenb', round(min(tenb), 2), rng(tenb, 2), 'cycles')
MMB = J('2026-09-25-claims-v3/results/mmb.json')
MF = 'docs/reports/data/2026-09-25-claims-v3/results/mmb.json'
ma = item(MMB, 'MMB-a')
op = [x for c in CARDS for x in ma['per_card'][c]['fp32-tensor-L2']['cycles_per_op_mean_based']]
dr_op = [x for c in CARDS for x in ma['per_card'][c]['fp32-tensor-DRAM']['cycles_per_op_mean_based']]
dr_tf = [x for c in CARDS for x in ma['per_card'][c]['fp32-tensor-DRAM']['info_tflops_range']]
fact('mm.reload', 'tensor', 'compute', 'derived',
     f'The matmul benchmark loads a new A (16 lines from the shire\'s L2 into one of two L1-scratchpad buffers) and '
     f'streams B through TenB before every TensorFMA, issuing the next op\'s loads while the current FMA runs, and it '
     f'takes {rng(op, 3)} cycles per op on all three cards: no more than the TensorFMA alone with B through TenB '
     f'({rng(tenb, 2)} cycles), so the next A\'s load of about 160 cycles is hidden behind the FMA.',
     round(op[0], 3), 'cycles per op', f'{MF}: [item=MMB-a].per_card.<card>."fp32-tensor-L2".cycles_per_op_mean_based; '
     f'{LF}: [item=LAT-S1] "529.1"; kernels/mmbench/mmbench.cc:3-9, 78-86', CARDS_TXT, MM_PAGE, MM_URL,
     'A version that waits for each load before its FMA was never run; 160 + 529 cycles for it would be a derived '
     'figure, not a measured one.')
num('mm_op', 'mm.reload', round(op[0], 3), rng(op, 3), 'cycles per op')
fact('mm.dram', 'tensor', 'compute', 'measured',
     f'The same benchmark with 64 private tiles per minion, so that every load comes from DRAM: {rng(dr_op, 0)} cycles '
     f'per op and {rng(dr_tf, 3)} TFLOP/s on the three cards, about 30 times slower than with the tiles in the L2.',
     round(dr_tf[0], 3), 'TFLOP/s', f'{MF}: [item=MMB-a].per_card.<card>."fp32-tensor-DRAM".cycles_per_op_mean_based, '
     '.info_tflops_range; tools/claims-v3/mmb/mmbench_power_v3.py:65', CARDS_TXT, MM_PAGE, MM_URL)
assert 25 < 9.51 / max(dr_tf) < 35
num('mm_dram_op', 'mm.dram', round(max(dr_op)), rng(dr_op, 0), 'cycles per op')
num('mm_dram_tf', 'mm.dram', round(max(dr_tf), 3), rng(dr_tf, 3), 'TFLOP/s')

# ======================= the same matmul on different data: watts and heat =======================
H3 = J('2026-09-21-horace-aifoundry2/horace3.json')
HF = 'docs/reports/data/2026-09-21-horace-aifoundry2/horace3.json'
pat = {p: H3['patterns'][p] for p in ('zeros', 'ones', 'randn')}
tf = [pat[p]['tflops'] for p in pat]
pb = [pat[p]['p_before'] for p in pat]
st = [pat[p]['start_temp'] for p in pat]
fact('mm.w-data', 'board', 'power', 'derived',
     f'The Horace runs of the fp32 matmul, {rng(tf, 2)} TFLOP/s on every data set (timed from the host over the whole '
     f'run, its launches included), launched at {rng(st, 1)} °C on aifoundry2: {pat["zeros"]["p80"]:.2f} W on zeros, '
     f'{pat["ones"]["p80"]:.2f} W on ones and {pat["randn"]["p80"]:.2f} W on random data, the board\'s power at the '
     f'launch temperature: its reading in seconds 1-3 of the run ({pat["zeros"]["p_early"]:.2f}, '
     f'{pat["ones"]["p_early"]:.2f} and {pat["randn"]["p_early"]:.2f} W) less the leakage that the run\'s own heating '
     f'had added by then, at the fitted leakage slope. Idle before each run: {rng(pb, 1)} W.',
     round(pat['randn']['p80'], 2), 'W at the launch temperature (random data)',
     f'{HF}: patterns.<zeros|ones|randn>.p80, .p_early, .p_before, .tflops, .start_temp; '
     'tools/ettelem/analyze_horace_strict.py:105-116 (tflops over t_start of the first launch to t_end of the last), '
     ':141 and :275 (p80 = p_early - leak x (t_early - launch temperature))', 'aifoundry2', HOR_PAGE, HOR_URL,
     'Leakage-corrected, not a raw board reading: the raw mean board power over the random-data runs was '
     f'{pat["randn"]["p_mean"]:.2f} W.')
num('w_zeros', 'mm.w-data', round(pat['zeros']['p80'], 2), f'{pat["zeros"]["p80"]:.2f}', 'W')
num('w_ones', 'mm.w-data', round(pat['ones']['p80'], 2), f'{pat["ones"]["p80"]:.2f}', 'W')
num('w_randn', 'mm.w-data', round(pat['randn']['p80'], 2), f'{pat["randn"]["p80"]:.2f}', 'W')
num('w_idle', 'mm.w-data', round(pb[0], 1), rng(pb, 1), 'W')
num('w_tflops', 'mm.w-data', round(tf[0], 2), rng(tf, 2), 'TFLOP/s')
AB = J('2026-09-25-claims-v3/results/abla.json')
AF = 'docs/reports/data/2026-09-25-claims-v3/results/abla.json'
t8 = item(AB, 'ABL-T8')
ones_d, rand_d = [], []
for c in CARDS:
    pc = t8['per_card'][c]
    subs = pc['subtests'] if 'subtests' in pc else pc['vs_aifoundry2_values']['subtests']
    for s in subs:
        (ones_d if 'ones' in s['test'] else rand_d).append(s['ci'])
out = t8['all_cards']['per_card']
assert out['aifoundry2'] == 'PASS' and out['aifoundry3'] == 'PASS' and out['aifoundry1-c1'] == 'REPORTED'
fact('mm.w-3cards', 'board', 'power', 'measured',
     'The same matmul on the three cards (ABL-T8, watts above zeros at the board): ones ' +
     ', '.join(f'{ci(v)}' for v in ones_d) + ' W and random data ' + ', '.join(f'{ci(v)}' for v in rand_d) +
     f' W ({SLASH}; 99% intervals): ones cost {rng([v["point"] for v in ones_d], 1)} W more than zeros and random '
     f'data {rng([v["point"] for v in rand_d], 1)} W more. The registered test passed on aifoundry2 and aifoundry3; '
     'aifoundry1-c1 is reported against aifoundry2\'s registered values.',
     round(rand_d[0]['point'], 2), 'W (aifoundry2, random - zeros)',
     f'{AF}: [item=ABL-T8].per_card.<card>.subtests[].ci (point, lo, hi); aifoundry1-c1: '
     '.per_card.aifoundry1-c1.vs_aifoundry2_values.subtests[]; .all_cards.per_card (outcomes)', CARDS_TXT, HOR_PAGE, HOR_URL)
for c, v in zip(('a2', 'a3', 'a1'), ones_d):
    num(f'w_od_{c}', 'mm.w-3cards', round(v['point'], 2), f'{v["point"]:.2f}', 'W')
for c, v in zip(('a2', 'a3', 'a1'), rand_d):
    num(f'w_rd_{c}', 'mm.w-3cards', round(v['point'], 2), f'{v["point"]:.2f}', 'W')
num('w_ones_d', 'mm.w-3cards', round(ones_d[0]['point'], 1), rng([v['point'] for v in ones_d], 1), 'W')
num('w_rand_d', 'mm.w-3cards', round(rand_d[0]['point'], 1), rng([v['point'] for v in rand_d], 1), 'W')
LG = J('2026-09-21-horace-aifoundry2/long.json')
LGF = 'docs/reports/data/2026-09-21-horace-aifoundry2/long.json'


def race(values, minions):
    return [r for r in LG['runs'] if r['values'] == values and r['minions'] == minions]


def durs(rs, reason):
    return [r['dur'] for r in rs if r['reason'] == reason]


rn, on, zr = race('randn', 1024), race('ones', 1024), race('zeros', 1024)
assert all(r['reason'] == 'cap' for r in rn + on) and all(r['reason'] == 'time' for r in zr)
starts = [r['t_before'] for r in rn + on + zr]
fact('heat.race', 'board', 'thermal', 'measured',
     f'From a launch at {rng(starts, 1)} °C to the firmware\'s 90 °C cap on aifoundry2, the same matmul on all 1,024 '
     f'minions: random data {rng(durs(rn, "cap"), 1)} s ({len(rn)} runs), ones {rng(durs(on, "cap"), 1)} s '
     f'({len(on)} runs); zeros never reached the cap in {rng(durs(zr, "time"), 0)} s ({len(zr)} runs).',
     round(min(durs(rn, 'cap')), 1), 's (random data)', f'{LGF}: runs[] with minions = 1024 and values = randn, ones, '
     'zeros: .dur, .reason (cap: reached 90 °C; time: the run ended first), .t_before', 'aifoundry2', HOR_PAGE, HOR_URL,
     'One card: the three-card version (E47) was registered and not run.')
num('race_rand', 'heat.race', round(min(durs(rn, 'cap')), 1), rng(durs(rn, 'cap'), 1), 's')
num('race_ones', 'heat.race', round(min(durs(on, 'cap')), 1), rng(durs(on, 'cap'), 1), 's')
num('race_zero', 'heat.race', round(min(durs(zr, 'time'))), rng(durs(zr, 'time'), 0), 's')
fewer = []
for m in (768, 512, 384, 256, 128):
    rs = race('randn', m)
    cap, tm = durs(rs, 'cap'), durs(rs, 'time')
    fewer.append((m, cap, tm))
parts = []
for m, cap, tm in fewer:
    parts.append(f'{m} minions {rng(cap, 1)} s' if cap else f'{m} never ({rng(tm, 0)} s)')
fact('heat.fewer', 'board', 'thermal', 'measured',
     'Random data on fewer minions, the same launch and cap on aifoundry2: ' + ', '.join(parts) + '.',
     None, 's', f'{LGF}: runs[] with values = randn and minions = 768, 512, 384, 256, 128: .dur, .reason',
     'aifoundry2', HOR_PAGE, HOR_URL)
for m, cap, tm in fewer:
    num(f'race_{m}', 'heat.fewer', round(min(cap or tm), 1), rng(cap, 1) if cap else 'never')
MD = J('2026-09-21-horace-aifoundry2/model.json')
lam = MD['power']['lambda_at_80']
fact('heat.leak', 'board', 'thermal', 'derived',
     f'At 80 °C the card\'s idle power rises {lam:.2f} W per °C (the fitted leakage law\'s slope, aifoundry2): a '
     'hotter die leaks more, which heats it further.', round(lam, 2), 'W/°C',
     'docs/reports/data/2026-09-21-horace-aifoundry2/model.json: power.lambda_at_80', 'aifoundry2', HOR_PAGE, HOR_URL)
num('leak80', 'heat.leak', round(lam, 2), f'{lam:.2f} W per °C')

# ======================= the hot line: fairness and the cliff (three cards) =======================
HL = J('2026-09-22-hotline-aifoundry2/hotline.json')
HLF = 'docs/reports/data/2026-09-22-hotline-aifoundry2/hotline.json'
fair = [next(f for f in HL['fairness'] if f['card'] == c and f['per_shire'] == 32 and f['home'] == '0') for c in CARDS]
fact('hot.fair', 'uc', 'sync', 'measured',
     'All 32 shires hammering one global atomic homed in shire 0 (32 minions each): every shire gets an even share, '
     f'the host shire {per([f["host_share"] for f in fair], 3)} of it ({rng([f["host_share"] for f in fair], 3)}) and the lowest '
     f'{per([f["min_share"] for f in fair], 3)} ({rng([f["min_share"] for f in fair], 3)}; {SLASH}), at {rng([f["cycles_per_op"] for f in fair], 2)} cycles '
     'per atomic.', round(fair[0]['host_share'], 3), 'of an even share',
     f'{HLF}: fairness[card=<card>, home="0", per_shire=32].host_share, .min_share, .cycles_per_op', CARDS_TXT,
     HOT_PAGE, HOT_URL)
num('hot_host', 'hot.fair', round(fair[0]['host_share'], 3), per([f['host_share'] for f in fair], 3))
num('hot_host_rng', 'hot.fair', round(fair[0]['host_share'], 3), rng([f['host_share'] for f in fair], 3))
num('hot_min_rng', 'hot.fair', round(fair[0]['min_share'], 3), rng([f['min_share'] for f in fair], 3))
num('hot_min', 'hot.fair', round(fair[0]['min_share'], 3), per([f['min_share'] for f in fair], 3))
LH = item(LAT, 'LAT-H')
edge = {c: [p['host_over_aloneN'] for p in LH['per_card'][c]['sub']['P2_edge']['passes'] if p.get('kept', True)] for c in CARDS}
f21 = [100 * sum(p['21'] for p in edge[c]) / len(edge[c]) for c in CARDS]
all21 = [100 * p['21'] for c in CARDS for p in edge[c]]
all22 = [100 * p[k] for c in CARDS for p in edge[c] for k in ('22', '23', '24')]
rtt = HL['context']['remote_atomic_latency_by_card']
fact('hot.cliff', 'uc', 'sync', 'measured',
     'The host shire\'s minions read their own scratchpad while the same number of minions in one other shire hammer '
     f'one scratchpad word in the host shire: with 21 of each the host keeps {per(f21, 1)}% of its rate alone ({SLASH}, '
     f'mean of {len(edge[CARDS[0]])} passes; {rng(all21, 1)}% over every pass), and with 22, 23 or 24 it stops: '
     f'{rng(all22, 2)}% on every card. An uncontended remote atomic takes {per([rtt[c] for c in CARDS], 1)} cycles '
     'round trip.',
     round(f21[0], 1), '% of the rate alone (21 requesters, aifoundry2)',
     f'{LF}: [item=LAT-H].per_card.<card>.sub.P2_edge.passes[].host_over_aloneN (keys 21-24); '
     f'{HLF}: context.remote_atomic_latency_by_card', CARDS_TXT, HOT_PAGE, HOT_URL)
num('hot21', 'hot.cliff', round(f21[0], 1), per(f21, 1), '%')
num('hot21r', 'hot.cliff', round(max(all21), 1), rng(all21, 1) + '%')
num('hot22', 'hot.cliff', round(max(all22), 2), rng(all22, 2) + '%')

# ======================= the allreduce tree, as the benchmark builds it =======================
fact('ar.tree', 'neigh', 'sync', 'spec',
     'The allreduce benchmark\'s tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial '
     'sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same '
     'tree (TensorBroadcast). Levels 0-2 join a neighbourhood\'s 8 minions along the fast network\'s edges, levels 3-4 '
     'its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.', 10, 'levels',
     'workloads/nocbench/kernel/nocbench.c:279-288 (tree: TensorReduce for levels 0..top, TensorBroadcast back), '
     ':516-521 (\'Minion m receives at levels below ctz(m) and sends at ctz(m); the root (m = 0) receives at every '
     'level\'); fact neigh.fln-edges for the tree edges', None, OC_PAGE, OC_URL)

out = {'about': __doc__.strip().split('\n')[0], 'facts': FACTS, 'num': NUM}
p = os.path.join(HERE, 'facts-v2.json')
json.dump(out, open(p, 'w'), indent=1, ensure_ascii=False)
print('wrote', p, len(FACTS), 'facts', len(NUM), 'numbers')
