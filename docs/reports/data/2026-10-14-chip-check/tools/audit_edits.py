#!/usr/bin/env python3
"""audit_edits.py : the ten new errors the five auditors found in the rebuilt chip diagram (14 Oct 2026, evening),
each an exact replacement that must match once, in the file that generates the text. See audit/new-errors.md."""
R = '/home/yaroslavvb/claude/et-soc1-prototyping/'
CD = R + 'docs/reports/data/2026-09-27-chip-diagram/'
MD = R + 'docs/reports/data/2026-09-28-memory-levels/'
LD = R + 'docs/reports/data/2026-10-01-ladder/'
SRC = R + 'docs/reports/sources/'
NOC_OLD = ("the firmware's generated register header does define address- and command-filtered transaction counters with "
           "latency counters in every NoC bridge (noc_esr.h: *_m_am_cntr0/1 with ccmd0/1, caddr and latnum0/1; *_s_as_cntr)")
NOC_NEW = ("the firmware's generated register header does define transaction counters in every NoC bridge: two address- "
           "and command-filtered counters in each master bridge (*_m_am_cntr0/1 with ccmd0/1 and caddr, beside registers "
           "named latnum0/1 whose use it does not give) and one command-filtered counter in each slave bridge (*_s_as_cntr)")
E = [
    # 1 (a4) the process file named by its path, not "beside this file"
    (LD + 'research/build_particles.py', '"process": "process.json beside this file: ',
     '"process": "docs/reports/data/2026-10-01-ladder/research/process.json: '),
    # 2 (a2) the relay is the next stage reading the last one's scratchpad: a remote load, not a remote store
    (SRC + 'memory-levels.script.js',
     "led: [[null, null], [null, null], [null, null]], tot: () => ({c: `${n('scp_hop12')} per hop`, e: `${n('scp_relay')}`}), ask: {c: 'ask-cache-latency'},\n  cap: () => `Writing another shire's scratchpad: the relay hands data to the next shire for ${n('scp_relay')} (DRAM / next / own).`,",
     "led: [[null, null], [null, null], [null, null]], tot: () => ({c: `${n('scp_hop12')} per hop`}), ask: {c: 'ask-cache-latency'},\n  cap: () => `Writing another shire's scratchpad: a plain write leaves from the data queue, a TensorStore write-around once its line is full (not timed here; the relay reads its input, see Remote load).`,"),
    (SRC + 'memory-levels.script.js',
     "cap: () => `Another shire's scratchpad: ${n('scp_remote')}; from shire ${IS().req} to shire ${IS().shire}, ${hopsC(SHC[IS().req], SHC[IS().shire])} hops.`,",
     "cap: () => `Another shire's scratchpad: ${n('scp_remote')}; from shire ${IS().req} to shire ${IS().shire}, ${hopsC(SHC[IS().req], SHC[IS().shire])} hops; the relay's next stage reads its input this way, ${n('scp_relay')} per byte moved (DRAM / next / own).`,"),
    (SRC + 'memory-levels.script.js',
     "what: `A pipeline that hands each stage's output to the next shire's scratchpad instead of DRAM:",
     "what: `A pipeline whose next stage reads each stage's output from the producing shire's scratchpad instead of going through DRAM:"),
    (MD + 'research/build_facts_scp.py',
     '"Handing each stage\'s output to the next shire\'s scratchpad instead of DRAM: ',
     '"Having the next shire read each stage\'s output from the producing shire\'s scratchpad instead of going through DRAM: '),
    (MD + 'research/build_facts_scp.py', 'CLM + ":464, :428; " + EMR', 'CLM + ":490, :451; " + EMR'),
    (MD + 'research/build_facts_scp.py',
     'measured="99.84 + 12.00 cycles per hop at 600 MHz (112-220 cycles over 1-10 hops); 0.96 TB/s chip-wide at 2.1 hops; 5.10 / 11.8 pJ/B at 2.1 hops, +0.67 / 1.80 pJ/B per hop",',
     'measured="99.84 + 12.00 cycles per hop at 600 MHz (112-220 cycles over 1-10 hops); 0.96 TB/s chip-wide at 2.1 hops; 5.10 / 11.8 pJ/B at 2.1 hops, +0.67 / 1.80 pJ/B per hop; the relay\'s next stage reads the previous shire\'s scratchpad this way: 592.5 GB/s for 8.92 pJ per byte moved, against 116.2 through DRAM",'),
    (MD + 'research/build_facts_scp.py',
     '  measured="the relay hands data to the next shire at 592.5 GB/s for 8.92 pJ/B moved (write + read), against 116.2 through DRAM",',
     '  measured=None,'),
    # 3 (a2) the 2 GB channel geometry is the 32 GB cards'
    (MD + 'research/build_facts_dram.py',
     '"Each channel is one rank of 8 banks x 131,072 rows x 2 KB pages (1,024 columns of 16 bits): 8 x 131,072 x 2 KB = "\n  "2 GB, matching the capacity.',
     '"On the 32 GB cards (aifoundry2, aifoundry3) each channel is one rank of 8 banks x 131,072 rows x 2 KB pages (1,024 "\n  "columns of 16 bits): 8 x 131,072 x 2 KB = 2 GB, matching their capacity (aifoundry1 card 1\'s 1 GB channels are a "\n  "smaller die)."'
     ' "'),
    # 4 (a5) the summary slide's legend fits its box at 23 px labels
    (SRC + 'chip-diagram.script.js', 'lx += 22 + (tw || 110) + 26;', 'lx += 22 + (tw || 110) + 12;'),
    # 5 (a5) the summary's relay item: per byte moved, as everywhere else
    (SRC + 'chip-diagram.script.js',
     "(4) The relay: ${n('rl_e_next')} pJ/B to the next shire against",
     "(4) The relay: ${n('rl_e_next')} pJ per byte moved (each write and each read counted) to the next shire against"),
    # 6 (a5) "its mirror" read as the silicon's
    (SRC + 'chip-diagram.script.js',
     'the published die plot is not its mirror, it keeps the PCIe and I/O cells',
     "the published die plot is not this view's mirror: it keeps the PCIe and I/O cells"),
    # 8 (a1) the NoC bridges' counters, as the header defines them
    (CD + 'research/facts-arch.json', NOC_OLD, NOC_NEW),
    (CD + 'research/build_facts_arch.py', NOC_OLD, NOC_NEW),
    # 9 (a3) E57: the map held in 14 of 15 conditions; the PA[17] pair was the fifteenth
    (MD + 'research/build_facts_dram.py',
     '"aifoundry2, E57 (29 Sep, R33a) also read two lines that differ only in PA[17], a column bit in this map, as a "\n       "row conflict, in 14 of 15 conditions, which the lab has not explained:',
     '"aifoundry2, E57 (29 Sep, R33a) matched this map in 14 of 15 conditions; in the fifteenth, two lines that differ "\n       "only in PA[17], a column bit in this map, read as a row conflict (48 trials), which the lab has not explained:'),
    # 10 (a3) the density evidence is the firmware's code 6 and the driver's 32 GB, not a read MR8
    (MD + 'build_facts.py',
     '"external/et-platform/device-bootloaders/src/ServiceProcessorBL2/utils/mem_controller_utils.c:941, 990-999 "\n                  "(MR8 0x18: x16, code 6); ET values from dram.ctl.*",',
     '"external/et-platform/device-bootloaders/src/ServiceProcessorBL2/utils/mem_controller_utils.c:993-999 and "\n                  "include/mem_controller.h:137 (MR8 density code 6, the firmware\'s 32 GB setting, which the driver reports on "\n                  "aifoundry2 and aifoundry3: dram.org.capacity); ET values from dram.ctl.*",'),
]
# check every edit first (several edit one file, in order), then write: a failure leaves nothing half applied
texts = {}
for path, old, new in E:
    s = texts.get(path) or open(path).read()
    n = s.count(old)
    if n != 1: raise SystemExit(f'{path}: found {n} times: {old[:90]!r}')
    texts[path] = s.replace(old, new)
for path, s in texts.items():
    open(path, 'w').write(s)
    print('edited', path.replace(R, ''))
