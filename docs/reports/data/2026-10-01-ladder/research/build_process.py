#!/usr/bin/env python3
"""Write process.json: the facts about TSMC's 7 nm process (N7), the ET-SoC-1 and the electronics a beginner needs,
for the ladder's inward scales (chip diagram and memory levels, 1 Oct 2026).

Every fact: id, group, levels (which zoom scales it informs), statement, value, unit, kind, label, source, url,
quote (verbatim from the source, or the inputs for a derived fact), note (assumptions, derivation, caveats).

Kinds are the build's vocabulary (docs/reports/data/2026-09-27-chip-diagram/research/build_inside.py LABELS):
  spec      an Esperanto/ET document says so                 -> page label "documented"
  measured  measured on the lab's cards (this repository)    -> "measured"
  derived   arithmetic on sourced values                     -> "model"
  inferred  our reading or estimate; no source states it     -> "inference"
  outside   a published outside source (process, physics)    -> "outside source"
  generic   a textbook rule or circuit, not this chip        -> "outside source (generic)"
  unknown   an open question                                 -> "unknown"
Sources read 1 Oct 2026; the downloaded copies were kept in the session's work directory, not in the repository
(each fact cites its source by title and URL).
"""
import json, math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'process.json')
LABEL = {'spec': 'documented', 'measured': 'measured', 'derived': 'model', 'inferred': 'inference',
         'outside': 'outside source', 'generic': 'outside source (generic)', 'unknown': 'unknown'}

# ---- sources (short key -> citation, url) ----
S = {
 'hc33': ('D. Ditzel et al. (Esperanto), "Accelerating ML Recommendation with over a Thousand RISC-V/Tensor Processors '
          'on Esperanto\'s ET-SoC-1 Chip", Hot Chips 33 slides, 24 Aug 2021',
          'https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Esperanto.Dave_Ditzel.presentation.v1submitted.pdf'),
 'micro': ('D. Ditzel et al. (Esperanto), same title, IEEE Micro 42(3), May/June 2022, pp. 31-38 (hosted by Esperanto)',
           'https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf'),
 'wc-et': ('D. Schor, "A Look At The ET-SoC-1, Esperanto\'s Massively Multi-Core RISC-V Approach To AI", WikiChip Fuse, '
           '16 May 2021 (public 10 Jul 2021); read via the Internet Archive capture of 10 Jul 2021 (the site refuses connections)',
           'https://fuse.wikichip.org/news/4911/a-look-at-the-et-soc-1-esperantos-massively-multi-core-risc-v-approach-to-ai/'),
 'wc-n7': ('D. Schor, "TSMC 7nm HD and HP Cells, 2nd Gen 7nm, And The Snapdragon 855 DTCO", WikiChip Fuse, 16 Jun 2019 '
           '(VLSI 2019); read via the Internet Archive capture of 13 Nov 2019',
           'https://fuse.wikichip.org/news/2408/tsmc-7nm-hd-and-hp-cells-2nd-gen-7nm-and-the-snapdragon-855-dtco/'),
 'wc-7nm': ('WikiChip, "7 nm lithography process" (comparison table and TSMC section); read via the Internet Archive '
            'capture of 16 Jun 2025',
            'https://en.wikichip.org/wiki/7_nm_lithography_process'),
 'dj-iedm16': ('D. James (TechInsights/Chipworks), "IEDM 2016 - Setting the Stage for 7.5 nm", Solid State Technology '
               '"Real Chips" blog, 18 Jan 2017 (on S.-Y. Wu et al. (TSMC), "A 7nm CMOS platform technology featuring 4th '
               'generation FinFET transistors with a 0.027um2 high density 6-T SRAM cell for mobile SoC applications", '
               'IEDM 2016, paper 2.6)',
               'https://sst.semiconductor-digest.com/chipworks_real_chips_blog/2017/01/18/iedm-2016-setting-the-stage-for-75-nm/'),
 'ew-iedm16': ('D. Manners, "7nm processes at IEDM", Electronics Weekly, 20 Oct 2016 (republished by Design & Reuse), '
               'on the TSMC IEDM 2016 paper 2.6',
               'https://www.design-reuse.com/news/3017-7nm-processes-at-iedm/'),
 'dj-co': ('P. Singer with D. James (TechInsights), "Intel 4 Process Drops Cobalt Interconnect, Goes with Tried and '
           'Tested Copper with Cobalt Liner/Cap", Semiconductor Digest, 1 Oct 2022',
           'https://www.semiconductor-digest.com/intel-4-process-drops-cobalt-interconnect-goes-with-tried-and-tested-copper-with-cobalt-liner-cap/'),
 'siliconics': ('D. James (Siliconics), "A Quick Look at 14-nm and 10-nm", AVS Joint Users Group, July 2018 (JTG718-4)',
                'https://nccavs-usergroups.avs.org/wp-content/uploads/JTG2018/JTG718-4-James-Siliconics.pdf'),
 'wp-7nm': ('Wikipedia, "7 nm process", comparison table, column TSMC N7',
            'https://en.wikipedia.org/wiki/7_nm_process'),
 'semiwiki17': ('T. Dillinger, "Top 10 Updates from the TSMC Technology Symposium, Part II", SemiWiki, 23 Mar 2017',
                'https://semiwiki.com/semiconductor-manufacturers/tsmc/6676-top-10-updates-from-the-tsmc-technology-symposium-part-ii/'),
 'tsmc-n7': ('TSMC, "7nm Technology" (N7/N6 platform page)',
             'https://www.tsmc.com/english/dedicatedFoundry/technology/platform_DCE_N7_N6'),
 'angstro': ('SkyJuice, "The Truth of TSMC 5nm", Angstronomics, 2022',
             'https://www.angstronomics.com/p/the-truth-of-tsmc-5nm'),
 'hu1': ('C. Hu, Modern Semiconductor Devices for Integrated Circuits (Pearson 2010), ch. 1 (author\'s free chapter)',
         'https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch1-3.pdf'),
 'hu6': ('C. Hu, Modern Semiconductor Devices for Integrated Circuits (Pearson 2010), ch. 6 (author\'s free chapter)',
         'https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch6-1.pdf'),
 'hu7': ('C. Hu, Modern Semiconductor Devices for Integrated Circuits (Pearson 2010), ch. 7 (author\'s free chapter)',
         'https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch7.pdf'),
 'ioffe-band': ('Ioffe Institute, NSM Archive, "Band structure and carrier concentration of Silicon (Si)" (read via the '
                'mirror at www-f9.ijs.si; ioffe.ru served a self-signed certificate)',
                'https://www.ioffe.ru/SVA/NSM/Semicond/Si/bandstr.html'),
 'ioffe-basic': ('Ioffe Institute, NSM Archive, "Basic parameters of Silicon (Si)" (read via the mirror at www-f9.ijs.si)',
                 'https://www.ioffe.ru/SVA/NSM/Semicond/Si/basic.html'),
 'ioffe-elec': ('Ioffe Institute, NSM Archive, "Electrical properties of Silicon (Si)" (read via the mirror at www-f9.ijs.si)',
                'https://www.ioffe.ru/SVA/NSM/Semicond/Si/electric.html'),
 'nist-asil': ('NIST, CODATA 2022 recommended values, "lattice parameter of silicon"',
               'https://physics.nist.gov/cgi-bin/cuu/Value?asil'),
 'nist-e': ('NIST, CODATA 2022 recommended values, "elementary charge"', 'https://physics.nist.gov/cgi-bin/cuu/Value?e'),
 'nist-k': ('NIST, CODATA 2022 recommended values, "Boltzmann constant"', 'https://physics.nist.gov/cgi-bin/cuu/Value?k'),
 'nist-iso': ('NIST, "Atomic Weights and Isotopic Compositions for Silicon"',
              'https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Si'),
 'konig': ('K. Koenig et al., "Nuclear charge radii of silicon isotopes", arXiv:2309.02037, Table 1 (28Si from '
           'I. Angeli and K. P. Marinova, At. Data Nucl. Data Tables 99 (2013) 69-95)',
           'https://arxiv.org/abs/2309.02037'),
 'zhao': ('C. Zhao and J. Xiang, "Atomic Layer Deposition (ALD) of Metal Gates for CMOS", Applied Sciences 9 (2019) 2388',
          'https://doi.org/10.3390/app9112388'),
 'berkeley': ('X. Zhang, "Simulation-based Study of Super-steep Retrograde Doped Bulk FinFET Technology and 6T-SRAM '
              'Yield", UC Berkeley EECS Technical Report UCB/EECS-2016-3, 5 Jan 2016',
              'https://www2.eecs.berkeley.edu/Pubs/TechRpts/2016/EECS-2016-3.pdf'),
 'amat-sip': ('X. Li, A. Dube, Z. Ye, S. Sharma, Y. Kim, S. Chu (Applied Materials), "Selective Epitaxial Si:P Film for '
              'nMOSFET Application: High Phosphorous Concentration and High Tensile Strain", ECS/SMEQ joint meeting, '
              'Cancun, Oct 2014 (abstract)',
              'https://ecs.confex.com/ecs/226/webprogram/Paper40706.html'),
 'qc-pat': ('Qualcomm, US patent 9,564,518 B2, "Method and apparatus for source-drain junction formation in a FinFET with '
            'in-situ doping" (priority 24 Sep 2014)',
            'https://patents.google.com/patent/US9564518B2/en'),
 'ti-dram': ('J. Choe (TechInsights), "DRAM Scaling Trend and Beyond", TechInsights blog, June 2022',
             'https://www.techinsights.com/blog/dram-scaling-trend-and-beyond'),
 'wp-cu': ('Wikipedia, "Copper" (infobox)', 'https://en.wikipedia.org/wiki/Copper'),
}

def R(path):  # a repository source
    return ('repository: ' + path, None)

facts = []
def F(id, group, levels, statement, value, unit, kind, src, quote=None, note=None, url=None, repo_fact=None):
    assert kind in LABEL, kind
    if isinstance(src, str) and src in S:
        cit, u = S[src]
    elif isinstance(src, tuple):
        cit, u = src
    else:
        raise ValueError(src)
    facts.append({'id': id, 'group': group, 'levels': levels, 'statement': statement, 'value': value, 'unit': unit,
                  'kind': kind, 'label': LABEL[kind], 'source': cit, 'url': url or u, 'quote': quote, 'note': note,
                  'repo_fact': repo_fact})

# =====================================================================================================
# 1. The ET-SoC-1 (Esperanto's own statements, and the repository's measurements)
# =====================================================================================================
g = 'et-soc1'
F('et.process', g, ['die'], 'The ET-SoC-1 is made in TSMC 7 nm.', 7, 'nm (node name)', 'spec', 'micro',
  quote='"The Esperanto supercomputer on a chip has been fabricated in TSMC 7-nm technology and contains over 24 billion transistors." (p. 37)')
F('et.process-n7', g, ['die'], 'WikiChip names the process as TSMC N7 (the first-generation 7 nm, not N7+ with EUV); Esperanto\'s papers say only "TSMC 7 nm".',
  None, None, 'outside', 'wc-et',
  quote='"Physically, the chip is fabricated on TSMC\'s N7 process technology."',
  note='Whether the silicon is N7 or the IP-compatible N7P (same design rules) is not published.')
F('et.transistors', g, ['die'], 'Over 24 billion transistors.', 24e9, 'transistors (lower bound)', 'spec', 'micro',
  quote='"The ET-SoC-1 chip is implemented in TSMC 7-nm technology using over 24 billion transistors." (p. 31); Hot Chips 33 slide 20: "24 billion transistors"',
  note='WikiChip (May 2021, before Hot Chips) gave 23.8 billion: "packing 23.8 billion transistors".', repo_fact='chip:chip.process')
F('et.die-area', g, ['die'], 'Die area 570 mm².', 570, 'mm²', 'spec', 'micro',
  quote='"It has a die area of 570 mm2 and uses 89 mask layers." (p. 37); slide 20: "Die-area: 570 mm2"', repo_fact='chip:chip.die-area')
F('et.masks', g, ['die'], '89 mask layers: 89 photolithography steps define the wafer, from fins up to the top metal.', 89, 'mask layers', 'spec', 'micro',
  quote='"uses 89 mask layers" (p. 37)')
F('et.package', g, ['package'], 'The package is 45 x 45 mm, with 2,494 balls to the board and over 30,000 bumps to the die.', 30000, 'bumps (lower bound)', 'spec', 'hc33',
  quote='"Package: 45x45mm with 2494 balls to PCB, over 30,000 bumps to die" (slide 20)')
F('et.sram-bytes', g, ['die'], 'Over 160 million bytes of on-die SRAM (caches and scratchpads).', 160e6, 'bytes (lower bound)', 'spec', 'hc33',
  quote='"Over 160 million bytes of on-die SRAM used for caches and scratchpad memory" (slide 20)',
  note='The datasheet\'s 140 MB is the 35 shire caches alone (repository fact chip.sram-total). Adding the 1,088 minion L1s (4 KiB) and 136 neighbourhood I-caches (32 KiB) gives about 156 million bytes; the rest (Maxion L1s, tags, ECC, buffers) is not itemised anywhere (inference).')
F('et.cores', g, ['die'], '1,088 ET-Minion cores, 4 ET-Maxion cores and 1 service processor: 1,093 RISC-V cores.', 1093, 'cores', 'spec', 'hc33',
  quote='"1088 energy-efficient ET-Minion 64-bit RISC-V in-order cores each with a vector/tensor unit" / "4 high-performance ET-Maxion 64-bit RISC-V out-of-order cores" (slide 2); "1 RISC-V service processor" (slide 20)',
  repo_fact='chip:chip.cores-total')
F('et.range', g, ['die', 'minion'], 'Operating range: ET-Minions 300 MHz to 2 GHz (typical 500 MHz to 1.5 GHz expected); the cards here run 600-800 MHz.', None, None, 'spec', 'hc33',
  quote='"OPERATING RANGE: 300 MHz TO 2 GHz" (slide 7); "Typical operation 500 MHz to 1.5 GHz expected" (slide 20)',
  repo_fact='chip:chip.advertised-range')
F('et.power', g, ['die'], 'Typical power under 20 W, adjustable from 10 to 60+ W in software.', 20, 'W (typical, upper)', 'spec', 'hc33',
  quote='"Power typically < 20 watts, can be adjusted for 10 to 60+ watts under SW control" (slide 20)')
F('et.shire-supplies', g, ['shire'], 'Each minion shire has its own low-voltage supply inputs, so its voltage can be trimmed against threshold-voltage variation and for DVFS.', None, None, 'spec', 'hc33',
  quote='"Each Minion Shire has independent low voltage power supply inputs that can be finely adjusted to mitigate Vt variation effects and enable DVFS" (slide 20)')
F('et.nominal-075', g, ['finfet', 'die'], '0.75 V is "the nominal voltage in 7 nm" (Esperanto); TSMC\'s N7 core transistors are designed around it.', 0.75, 'V', 'spec', 'micro',
  quote='"Reducing the operating voltage to 0.75 V, the nominal voltage in 7 nm, would result in 164 W, still way too high." (p. 33)')
F('et.sweet-spot', g, ['minion', 'finfet'], 'Esperanto\'s chosen region: minions between 300 and 500 mV, near the best energy efficiency (0.3 V gave 20x the efficiency of the highest voltage in their model).', None, 'V', 'spec', 'micro',
  quote='"Esperanto\'s sweet spot for achieving best performance will usually be for operating our ET-Minions between 300 and 500 mV, that is, nearest the best energy efficiency points." (p. 33)',
  note='The voltage curve is modelled, with cores re-synthesised at each voltage (repository R6).')
F('et.lib-04', g, ['minion', 'gate'], 'The standard-cell libraries were re-characterised at 0.4 V for the timing tools; the pipeline has very few gates per stage to keep MHz up at low voltage.', 0.4, 'V', 'spec', 'micro',
  quote='"The core uses an in-order pipeline optimized to have very few gates per pipeline stage to improve megahertz when operated at low voltages. For timing and other CAD tools, we had libraries recharacterized at 0.4 V." (p. 33)')
F('et.one-plane', g, ['minion', 'l1'], 'The whole minion, its 4 KB L1 included, is on one low-voltage power plane.', None, None, 'spec', 'micro',
  quote='"To simplify physical design, the entire ET-Minion, including its 4-KB L1 caches, operates on a single low-voltage power plane." (p. 33)')
F('et.custom-sram', g, ['minion', 'l1'], 'Esperanto designed its own low-voltage memory cells instead of TSMC\'s standard SRAM for the minion: larger cells that work far below nominal voltage, around 400 mV. (The repository finds the minion L1 and register files are latch arrays.)', 0.4, 'V (order of)', 'outside', 'wc-et',
  quote='"Esperanto has gone further and designed its own custom SRAM instead of using TSMC\'s standard SRAM offering. The cells, while physically larger, can stably operate at considerably lower voltage - far below nominal. \'When I talk about low voltage operations, I really mean operating at much lower than nominal voltages. So, if nominal is 0.75 V or so, we are operating on the order of 400 mV,\' Swift said."',
  note='Art Swift (Esperanto CEO) quoted by WikiChip. Repository: the L1 is an LRAM latch array (memory-levels fact l1:l1.lram-model and research-inside.md).')
F('et.sram-nominal', g, ['l2', 'shire'], 'The shire\'s four 1 MB SRAM banks run near the process-nominal voltage, for density; the mesh has its own low-voltage domain.', None, None, 'spec', 'micro',
  quote='"These SRAM banks operate near the process-nominal supply voltage to allow higher density than the smaller caches within each core." / "Shires are connected to each other via an on-chip mesh interconnect operated on its own low-voltage domain." (p. 35)')
F('et.wires-slow', g, ['neighbourhood'], '7 nm wires are slow, so minions were grouped in eights (neighbourhoods) before wire length became a problem.', 8, 'minions per neighbourhood', 'spec', 'micro',
  quote='"Physical design plays an important role in chip architecture as 7-nm wires are relatively slow. We found it convenient to group eight ET-Minion cores together before wire length became a problem." (p. 34)')
F('et.cdyn-target', g, ['minion'], 'Esperanto\'s target: 10 mW per minion at 1 GHz and 0.425 V, i.e. 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 core).', 0.04, 'nF', 'spec', 'hc33',
  quote='"10mW ET-Minion core (~10W for 1K cores) 0.01 W 1 GHz 0.425v 0.04nF" (slide 5); "Power (Watts) = Cdynamic x Voltage2 x Frequency + Leakage"')
F('et.ops-per-ghz', g, ['minion', 'vpu'], 'Each minion peaks at 128 int8 operations per cycle (128 GOPS per GHz); 16 fp32 or 32 fp16 operations per cycle.', 128, 'int8 ops per cycle', 'spec', 'hc33',
  quote='"Each ET-Minion can deliver peak of 128 Int8 GOPS per GHz"; "16 32-bit single precision operations per cycle"; "32 16-bit half precision operations per cycle" (slide 7)')
F('et.tensor-512', g, ['minion', 'vpu'], 'A tensor instruction runs for up to 512 cycles while the integer pipeline sleeps.', 512, 'cycles (max)', 'spec', 'micro',
  quote='"Esperanto added new tensor instructions that utilize the full vector width every cycle and run for up to 512 cycles." / "During these long tensor instructions, the RISC-V integer pipeline is put to sleep" (pp. 33-34)')
F('et.trans-rom', g, ['vpu', 'lane'], 'The transcendental unit is ROM-based, trading area for low power.', None, None, 'outside', 'wc-et',
  quote='"The trans unit is ROM-based, favoring lower power over silicon."')
F('et.vt-area', g, ['minion'], 'In Esperanto\'s minion plot (drawn roughly to scale) the vector/tensor unit takes far more area than the integer pipeline.', None, None, 'spec', 'micro',
  quote='"you can see that the vector/tensor unit takes far more area than the integer pipeline" (p. 33, Figure 2)')
F('et.icache', g, ['neighbourhood'], 'Eight minions share one 32 KB instruction cache.', 32, 'KB', 'spec', 'hc33',
  quote='"Instruction Cache 32 KB shared" (slide 8)')
F('et.density', g, ['die'], 'Average density 24 billion / 570 mm² = 42 million transistors per mm², 46% of N7\'s densest logic (91.2 MTr/mm²): SRAM periphery, analog (PLLs, PHYs), I/O and wiring take the rest.',
  42.1, 'MTr/mm²', 'derived', ('arithmetic on et.transistors, et.die-area and n7.density-hd', S['wc-n7'][1]),
  quote='24e9 / 570 mm² = 42.1e6 per mm²; 42.1 / 91.2 = 0.46')
F('et.tr-per-minion', g, ['minion'], 'At most about 15 million transistors per minion: what is left after the shire caches\' bitcells (35 x 4 MiB x 6 transistors = 7.0 billion), shared over 1,088 minions; the true count is lower because the rest also holds the mesh, memory shires, PHYs, PCIe and Maxions.',
  15e6, 'transistors (upper bound)', 'inferred', ('arithmetic on et.transistors and chip.sram-total (repository)', None),
  quote='(24e9 - 35 x 4 x 2^20 x 8 x 6) / 1088 = 15.6e6',
  note='Assumes 6-transistor cells for the shire caches (the bitcell is not documented: memory-levels u.bitcell). No floorplan below the shire is published.')

# measured on the cards (the repository)
F('et.v-minion', g, ['minion', 'finfet'], 'Minion rail: 0.517 V at 600 MHz on die (0.568 V at 700, 0.618 V at 800); firmware limits 0.40-0.62 V.', 0.517, 'V', 'measured',
  R('docs/findings/16-dvfs-and-leakage.md:20; docs/findings/05-claims.md:26-27, 41'),
  quote='"Three operating points: 600 MHz at 0.517 V, 700 at 0.568, 800 at 0.618." (16-dvfs-and-leakage.md)',
  repo_fact='chip:volt.minion; ml:l1:l1.voltage')
F('et.v-sram', g, ['l2', 'sram'], 'SRAM rail (shire-cache arrays): 0.703-0.707 V on die; firmware limits 0.66-0.85 V.', 0.705, 'V', 'measured',
  R('chip facts volt.sram; memory-levels l2:l2.voltage.idle, l2:l2.voltage.limits'), repo_fact='chip:volt.sram')
F('et.v-noc', g, ['mesh'], 'Mesh rail: 0.485 V set point, 0.483-0.486 V on die.', 0.485, 'V', 'measured',
  R('chip facts mesh.voltage, L101'), repo_fact='chip:mesh.voltage')
F('et.v-other', g, ['memshire', 'dram'], 'Other rails on die: DDR (memory shires) 0.76-0.77 V, Maxion 0.58-0.59 V, I/O shire 0.75 V, PCIe shire 0.75 V. The DRAM\'s own two rails have set points only (no reading on die): 1.1 V (the card\'s "VDDQ", the LPDDR4X\'s VDD2 core supply) and 0.64 V (the card\'s VDDQLP, the LPDDR4X\'s I/O VDDQ).', None, 'V', 'measured',
  R('chip facts volt.other; memory levels dram.pwr.rails (the rails\' names)'), repo_fact='chip:volt.other',
  note='volt.other gives these two as set points (1,100 and 640 mV) read from the power controller, with no on-die value; the memory levels\' dram.pwr.rails names them: VDD_Q is the LPDDR4X\'s VDDQ/VDD2 core supply, VDD_QLP its I/O VDDQ.')
F('et.per-shire-v', g, ['shire'], 'Per-shire minion-rail voltage at idle: 513-522 mV across the 34 minion shires.', None, 'mV', 'measured',
  R('chip facts L123 (docs/findings/05-claims.md:41)'), repo_fact='chip:L123')
F('et.leakage', g, ['die', 'finfet'], 'Leakage on aifoundry2 at 80 °C: 20-29 W, 55-80% of an idle card and 31-45% of a 64 W random-data matmul; it rises 0.65 W per °C (fit: 23.3 W x exp((T-80)/36)).', 23.3, 'W at 80 °C (fit)', 'measured',
  R('docs/findings/16-dvfs-and-leakage.md (Kanter table row "Leakage is typically 5-30%"); docs/research/why-low-power.md "What this card measures"'),
  quote='"Fitted: 12.6 W fixed + 23.3 W x exp((T - 80)/36) of leakage" (why-low-power.md)')
F('et.leak-double', g, ['finfet'], 'By that fit, leakage doubles every 25 °C.', 25, '°C per doubling', 'derived',
  ('arithmetic on et.leakage: 36 °C x ln 2', None), quote='36 x 0.693 = 24.95 °C')
F('et.leak-per-tr', g, ['finfet'], 'Spread over 24 billion transistors, the 23 W of leakage fitted at 80 °C is about 1 nW each on average: roughly 1.4-1.9 nA, about 10 billion electrons a second per transistor (an average over every kind, threshold voltage and state, not what any one "off" transistor passes).', 1.0, 'nW per transistor', 'derived',
  ('arithmetic on et.leakage and et.transistors', None),
  quote='23.3 W / 24e9 = 0.97 nW; at 0.52-0.705 V that is 1.4-1.9 nA = 0.9e10-1.2e10 electrons/s',
  note='An average over every kind of transistor and rail: SRAM, logic, analog; the leakage is not split by rail.')
F('et.cdyn-measured', g, ['minion'], 'Measured switched capacitance per minion: 0.168 nF on random fp32 matmul (0.064 on ones, 0.012 on zeros), against the 0.04 nF target.', 0.168, 'nF', 'measured',
  R('docs/research/why-low-power.md "What this card measures"'),
  quote='"Cdynamic = P/(V^2 f): 0.012, 0.064 and 0.168 nF against the slide\'s 0.04 nF target"')
F('et.electrons-per-cycle', g, ['minion'], 'Each cycle of a minion on random fp32 matmul moves about 87 pC from the 0.517 V supply: 540 million electrons per minion per cycle (45 pJ).', 5.4e8, 'electrons per minion-cycle', 'derived',
  ('arithmetic on et.cdyn-measured and et.v-minion', None), quote='Q = C V = 0.168 nF x 0.517 V = 86.9 pC; / 1.602e-19 C = 5.4e8; E = C V^2 = 44.9 pJ')
F('et.flip-reg', g, ['lane', 'gate', 'latch'], 'Clocking one register bit in the tensor unit costs 3.18 fJ (fitted on aifoundry2): at 0.517 V that is an effective 11.9 fF charged, about 38,000 electrons from the supply.', 38000, 'electrons per register bit clocked', 'derived',
  R('docs/energy-manual/03-instructions.md "Where the tensor unit\'s energy goes: per flip" (ffclk 3.179 fJ)'),
  quote='C = E / V^2 = 3.179 fJ / 0.517^2 = 11.9 fF; Q = C V = 6.1 fC = 38,400 electrons',
  note='Treats each clocking event as one full charge from the supply (E = C V^2); the effective capacitance includes the clock wiring and buffers that drive the flip-flop, not only the flip-flop.')

# =====================================================================================================
# 2. TSMC N7, the process
# =====================================================================================================
g = 'n7'
F('n7.start', g, ['die'], 'TSMC started N7 volume production in April 2018; first products include the Apple A12, Kirin 980, Snapdragon 855 and AMD Zen 2.', 2018, 'year', 'outside', 'wc-n7',
  quote='"TSMC started mass production of their 7-nanometer node in April 2018. Since then we have seen a number of high-profile processors that make use of the technology including the Apple A12 and A12X, the Kirin 980, and soon Qualcomm\'s Snapdragon 855 and AMD Zen 2."')
F('n7.generation', g, ['finfet', 'gate'], 'N7 is TSMC\'s 4th-generation FinFET and 5th-generation high-k metal gate: gate-last, with two gate-oxide thicknesses (thin for core logic, thick for I/O).', 4, 'FinFET generation', 'outside', 'wc-n7',
  quote='"This is a fourth-generation FinFET, fifth-generation HKMG, gate-last, dual gate oxide process."',
  note='What the two oxides are used for (core vs I/O transistors) is the usual meaning of "dual gate oxide"; TSMC does not say (generic).')
F('n7.litho', g, ['die'], 'N7 is patterned with 193 nm immersion (DUV) light, no EUV: fins by self-aligned quadruple patterning, gates and M0-M4 by double patterning.', 193, 'nm (light wavelength)', 'outside', 'wc-n7',
  quote='"For the 7-nanometer process, deep ultraviolet (DUV) 193 nm ArF Immersion lithography continues to be used." Design rules: Fin 30 SAQP; Poly 57 SADP; M0-M4 40 SADP; M5-M9 76 Single.')
F('n7.vs-n16', g, ['die'], 'TSMC: N7 gives about 30% more speed, 55% less power or 3x the logic density of its 16 nm.', 3, 'x density vs N16', 'outside', 'tsmc-n7',
  quote='"delivers up to a 30% speed improvement, a 55% power saving, and a 3 times logic density improvement over 16nm (N16) technology"',
  note='The IEDM 2016 paper said 35-40% speed or >65% power and >3.3x routed gate density (ew-iedm16, dj-iedm16).')
F('n7.fin-pitch', g, ['finfet', 'fin', 'sram'], 'Fin pitch 30 nm (fins patterned by self-aligned quadruple patterning).', 30, 'nm', 'outside', 'wc-n7',
  quote='Transistor Profile table: "Fin Pitch | 36 nm | 30 nm | 0.83x" (10 nm, 7 nm); design rules "Fin | 30 | SAQP"',
  note='Also Wikipedia, "7 nm process" (TSMC N7 fin pitch 30 nm).')
F('n7.fin-width', g, ['fin', 'channel', 'crystal'], 'Fin width 6 nm (the same as TSMC 10 nm).', 6, 'nm', 'outside', 'wc-n7',
  quote='Transistor Profile table: "Fin Width | 6 nm | 6 nm | 1.00x"',
  note='Fins are tapered, wider at the base, with rounded tops (Siliconics on Intel 14 nm: "Vertical fins! But still rounded fin tops"; Intel 10 nm: "fin width 5-15 nm, ~7 nm at half height"); WikiChip does not say at what height its 6 nm is measured.')
F('n7.fin-height', g, ['fin', 'channel'], 'Fin height 52 nm (42 nm at TSMC 10 nm): taller fins carry more current per footprint.', 52, 'nm', 'outside', 'wc-n7',
  quote='Transistor Profile table: "Fin Height | 42 nm | 52 nm | 1.24x"; "Continuing to scale the fin width gives you a narrower channel while increasing the height to maintain a good effective width is done in order to improve the short channel characteristics and subthreshold slope"',
  note='The height of fin standing above the isolation oxide, as these tables quote it (not stated explicitly).')
F('n7.weff', g, ['fin', 'finfet'], 'One fin gives about 110 nm of channel width: the gate wraps both 52 nm sides and the 6 nm top. N7 has over twice N16\'s effective width.', 110, 'nm per fin', 'derived',
  ('C. Hu, ch. 7 (the rule) with n7.fin-height and n7.fin-width', S['hu7'][1]),
  quote='Hu: "The channel width, W, is the sum of twice the fin height and the width of the fin." 2 x 52 + 6 = 110 nm. WikiChip: "Compared to N16, N7 has over twice the effective channel width."')
F('n7.cpp', g, ['finfet', 'gate', 'cell'], 'Contacted gate pitch 57 nm in the dense cells (64 nm in the 7.5-track high-performance cells).', 57, 'nm', 'outside', 'wc-n7',
  quote='"For the transistor, the gate pitch has been further scaled down to 57 nm, however, the interconnect pitch halted at the 40 nm point in order to keep patterning at the SADP point." Flavors table: Gate Pitch 57 nm (low power) / 64 nm (high performance)',
  note='WikiChip: "while at IEDM TSMC reported slightly more aggressive pitches, the numbers shown in this article are the actual pitches used in their standard cells"; the IEDM paper does not state it: Dick James reports Scotten Jones\'s guess of 54 nm, the same as Intel 10 nm.')
F('n7.leff', g, ['gate', 'channel'], 'Effective gate length about 16.5 nm: the length of channel the gate controls, between source and drain.', 16.5, 'nm', 'outside', 'dj-iedm16',
  quote='"fifth-generation HKMG gate-last, dual gate oxide process ... effective gate length (leff) centered around 16.5 nm"',
  note='The physical (drawn) gate length is not published; comparable: TSMC 10 nm minimum Lg ~25 nm, Intel 10 nm 18 nm (Siliconics).')
F('n7.ss', g, ['finfet', 'channel'], 'Subthreshold swing about 65 mV per decade: below threshold, each 65 mV less on the gate cuts the current tenfold (the room-temperature limit is 60).', 65, 'mV/decade', 'outside', 'dj-iedm16',
  quote='"Sub-threshold swing has been pushed down to ~65mV/decade, and DIBL is ~40 mV/V"')
F('n7.dibl', g, ['finfet'], 'Drain-induced barrier lowering about 40 mV/V: raising the drain voltage by 1 V lowers the threshold by about 40 mV.', 40, 'mV/V', 'outside', 'dj-iedm16',
  quote='"DIBL is ~40 mV/V"')
F('n7.vt-options', g, ['finfet', 'gate'], 'Four threshold-voltage options spanning about 200 mV, set by different gate metals (faster but leakier, or slower and tighter).', 4, 'Vt options', 'outside', 'dj-iedm16',
  quote='"four device Vt options with a range of ~200 mV"; WikiChip: "Different multi-Vt devices were developed for this process with a Vt range of around 200 mV."',
  note='The absolute threshold voltages are not published (unknown); which options the ET-SoC-1 uses is not published either.')
F('n7.vt-abs', g, ['finfet'], 'N7\'s absolute threshold voltages are not published. Running at 0.4-0.52 V and libraries characterised at 0.4 V imply the minion\'s transistors switch with a few hundred millivolts or less of threshold: near-threshold operation.', None, 'V', 'unknown',
  ('open question; the inputs are et.lib-04, et.sweet-spot, et.v-minion', None))
F('n7.mmp', g, ['wire', 'cell'], 'Metal pitch 40 nm for M0 to M4 (so the finest wires are about 20 nm wide), 76 nm for M5 to M9, 124 nm for M10, 720 nm for M11-M12.', 40, 'nm (M0-M4 pitch)', 'outside', 'wc-n7',
  quote='Design rules: "M0 | 40 | SADP", "M1-M4 | 40 | SADP | 1x", "M5-M9 | 76 | Single | 1.9x", "M10 | 124 | Single | 3.1x", "M11, M12 | 720 | Single | 18x"',
  note='The IEDM paper as Dick James read it: "1x metal pitch is 40 nm for M0 to M4, and M5 - M9 are 1.9x (76 nm)". Line width ~half the pitch is the usual layout (generic).')
F('n7.metal-layers', g, ['wire', 'die'], 'The interconnect is a stack of about a dozen copper layers in low-k insulator: TSMC\'s paper says 12 layers; WikiChip\'s design rules list M0-M12. How many the ET-SoC-1 uses is not published.', 12, 'metal layers (paper)', 'outside', 'dj-iedm16',
  quote='"193 nm immersion lithography, dual raised source/drain epi, a novel contact technique, and a 12-layer copper/low-k interconnect stack"',
  note='GlobalFoundries\' 7 nm (IEDM 2017): "up to 17 metal layers" (siliconics).')
F('n7.contacts-co', g, ['finfet', 'wire'], 'Contacts to source and drain are cobalt: TSMC replaced tungsten with cobalt fill in the trench contacts, halving their resistance.', 50, '% resistance reduction', 'outside', 'wc-n7',
  quote='"Like Intel, TSMC introduced cobalt fill at the trench contact, replacing the tungsten contact. This has the effect of reducing the resistance at that area by 50%."; Dick James (2022): "both TSMC and Samsung have cobalt contacts in their 7- and 5-nm products."',
  note='WikiChip shows MSS Corp\'s element map of the Apple A12 (N7) with cobalt contacts.')
F('n7.cu-co-liner', g, ['wire'], 'The finest copper wires have a cobalt liner and cap (TSMC since 16FF\'s M1-M3, every generation since, including N5): the cobalt keeps copper atoms from migrating.', None, None, 'outside', 'dj-co',
  quote='"When we looked at the Apple A9 the following year, in TSMC\'s 16FF process, the M1 - M3 layers had Co liners and caps" / "And in fact, it has been used in the minimum pitch metals every generation since then, including the N5"',
  note='"keeps copper atoms from migrating" paraphrases the electromigration benefit the article attributes to cobalt (Intel: "improved electromigration (EM) 5 - 10x").')
F('n7.cells', g, ['cell', 'gate'], 'Standard cells are 240 nm tall (high density, 6 tracks, 8 fin pitches, 57 nm gate pitch) or 300 nm (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate pitch); a 360 nm 9-track variant also exists.', 240, 'nm (HD cell height)', 'outside', 'wc-n7',
  quote='"TSMC 7-nanometer comes in two variations - low power and high performance. Those cells are 240 nm and 300 nm tall respectively." Flavors: "240 nm 8-fin x 30 nm" / "300 nm 10-fin x 30 nm"; Tracks 6 T / 7.5 T',
  note='Which library the ET-SoC-1 uses is not published; the RTL names cell families HDBULT08 and HDBULT11 (memory-levels fact l1:l1.icg-cells, an open question l1:l1.u-library).')
F('n7.two-fin', g, ['cell', 'finfet'], 'In the 240 nm dense cell each transistor typically has 2 fins (Angstronomics\' "2-fin" N7 cell).', 2, 'fins per transistor (HD logic)', 'outside', 'angstro',
  quote='N7 2-fin descriptor "H240g57" (H240 = 240nm cell height, g57 = 57nm contacted gate pitch)',
  note='8 fin pitches per cell: about 2 active fins for the PMOS row and 2 for the NMOS row, the rest under the power rails and the gap (generic layout).')
F('n7.density-hd', g, ['cell', 'die'], 'Densest logic: about 91.2 million transistors per mm² (high-performance cells about 65).', 91.2, 'MTr/mm²', 'outside', 'wc-n7',
  quote='"The dense cells come at around 91.2 MTr/mm² while the less dense, high-performance cells, are calculated at around 65 MTr/mm²."')
F('n7.sram-hd', g, ['sram', 'l2'], 'High-density 6-transistor SRAM bitcell: 0.027 µm² (TSMC\'s IEDM 2016 headline).', 0.027, 'µm²', 'outside', 'wc-n7',
  quote='"Here, the 7-nanometer high-density SRAM bitcell is 0.027 µm², making it the second-densest cell reported to date. On the current FinFET processes, the bitcells are largely fin-quantized."',
  note='WikiChip\'s 7 nm table leaves TSMC\'s high-performance (high-current) cell blank: not published.')
F('n7.sram-dims', g, ['sram'], 'A 0.027 µm² cell fits 2 gate pitches by 8 fin pitches: about 114 x 240 nm, one fin per transistor in the densest cell.', 0.0274, 'µm² (2 x 57 nm x 8 x 30 nm)', 'inferred',
  ('arithmetic on n7.cpp and n7.fin-pitch', None), quote='0.114 µm x 0.240 µm = 0.0274 µm²',
  note='A layout reading, not a published drawing. The one-fin-per-transistor (1:1:1) arrangement is the usual high-density cell (generic). Which bitcell the ET-SoC-1\'s macros use is not documented (memory-levels u.bitcell).')
F('n7.sram-vmin', g, ['sram'], 'TSMC\'s 256 Mbit N7 SRAM test chip read and wrote down to 0.5 V.', 0.5, 'V', 'outside', 'ew-iedm16',
  quote='"a fully functional, low-voltage 256Mb SRAM test chip with full read/write functionality down to 0.5V, and the smallest SRAM cells ever reported (0.027um2)"',
  note='The ET-SoC-1 runs its shire-cache arrays at 0.705 V (et.v-sram).')
F('n7.features', g, ['finfet'], 'TSMC\'s list of what makes N7: an optimised fin width and profile, raised source/drain epitaxy that strains the channel, a novel contact process, and copper/low-k wiring.', None, None, 'outside', 'ew-iedm16',
  quote='"an advanced patterning technique used with 193nm immersion lithography, an optimized fin width and profile, a raised source/drain epitaxial process that strains the transistor channel and reduces parasitics, a novel contact process, and a copper/low-k interconnect scheme featuring different metal pitches and stacks."')
F('n7.hpc', g, ['cell'], 'TSMC\'s symposium: N7 gives +33% performance at the same leakage as N16FFC, or 58% less leakage at the same drive.', 33, '% performance at iso-Ioff', 'outside', 'semiwiki17',
  quote='"N7 will provide a +33% performance boost at the same I_off compared to N16FFC, or a -58% I_off leakage reduction at the same I_on."')

# comparable 7/10 nm processes (cross-sections are published for these; TSMC N7's teardowns are paywalled)
g = 'comparable'
F('cmp.gf7', g, ['finfet', 'fin'], 'GlobalFoundries\' 7 nm (IEDM 2017): fin pitch 30 nm, gate pitch 56 nm, metal pitch 40 nm, four work-function metals for each of N and P; active fin about 41 nm tall and 6 nm wide; cobalt contacts; up to 17 metal layers.', 41, 'nm (active fin height)', 'outside', 'siliconics',
  quote='"IEDM 2017 paper states FP 30 nm, CGP 56 nm, MMP 40 nm, quad-WF NFETs & PFETs"; "Active fin height ~41 nm, width ~6 nm, gate width ~ 88 nm"; "Co contacts, up to 17 metal layers" (slide 25)')
F('cmp.intel10', g, ['fin', 'gate'], 'Intel 10 nm: fin height 46-53 nm, fin width 5-15 nm from top to bottom (about 7 nm at half height); punch-through stopper by solid-source diffusion; 4-6 work-function metals; cobalt M0 and M1.', 7, 'nm (width at half height)', 'outside', 'siliconics',
  quote='"Fin height up from 34 to 42 to 53 nm, (IEDM17 46 nm) fin width 5 - 15 nm, ~7 nm at half height." / "Solid-source diffusion punch-stopper used again" / "Gate stack looks similar, 5th generation HKMG but 4 - 6 WFs" / "Cobalt M0 & M1 (with Ru?), Co cap on M2 - M5" (slides 12-13)')
F('cmp.tsmc10', g, ['fin'], 'TSMC 10 nm (Apple A11): fin pitch about 33 nm, fin width about 6 nm, gate height about 44 nm; fins visibly tapered.', 44, 'nm', 'outside', 'siliconics',
  quote='"SAQP minimum fin pitch ~33 nm, fin width ~6 nm, functional gate height ~44 nm, gate width ~95 nm" (slide 18); "Fin taper" (slide 17 label)')

# =====================================================================================================
# 3. The gate stack, dopants and the crystal
# =====================================================================================================
g = 'gate'
F('gate.hfo2', g, ['gate'], 'The gate insulator is hafnium oxide (HfO2, relative permittivity ~24, six times SiO2\'s 3.9) on a thin SiO2 interfacial layer: as good as 1 nm of SiO2 electrically, but a much thicker barrier, so the electrons that tunnel through it are several orders of magnitude fewer.', 24, 'relative permittivity', 'generic', 'hu7',
  quote='"HfO2 has a relative dielectric constant (k) of ~24, six times larger than that of SiO2. A 6 nm thick HfO2 film is equivalent to 1 nm thick SiO2 ... the HfO2 film presents a much thicker (albeit lower) tunneling barrier to the electrons and holes. The consequence is that the leakage current through HfO2 is several orders of magnitude smaller than that through SiO2 ... These problems are minimized by inserting a thin SiO2 interfacial layer between the silicon substrate and the high-k dielectric."',
  note='TSMC does not publish N7\'s stack or its thicknesses.')
F('gate.eot', g, ['gate'], 'Equivalent oxide thickness under 1 nm is typical of FinFETs of this generation (0.7 nm in a 15 nm-gate research FinFET); N7\'s is not published.', 0.7, 'nm (comparable, simulated)', 'outside', 'berkeley',
  quote='Table 1.1, nominal FinFET design: "Lgate (nm) 15", "EOT (nm) 0.7", "HSi (nm) 40", "WSi (nm) 8"',
  note='A simulation study\'s parameters, not a TSMC figure.')
F('gate.metals', g, ['gate'], 'Gate metals: since the first high-k gates (45 nm), the n-type gate uses TiAl and the p-type TiN on HfO2, deposited into the trench left by a removed dummy polysilicon gate and filled with W or Al; their work functions (about 4.1 and 4.85 eV) set the threshold.', None, None, 'generic', 'zhao',
  quote='"In the 45 nm node, the first generation of the high-k/metal gate technology for mass production, dual metal/single high-k stack was used. The metal gate for nMOS was TiAl, and that for pMOS was TiN, integrated with HfO2 dielectric by a gate last process ... To fill the gap, a conductive metal such as Al or W was deposited." / "The PVD TiAl and PVD TiN in gate stacks with HfO2 show EWF around 4.1 eV and 4.85 eV."',
  note='Industry practice, not a TSMC N7 disclosure; multi-Vt options come from different work-function metal stacks (four per polarity in GF 7 nm, cmp.gf7).')
F('gate.undoped-vt', g, ['gate', 'channel'], 'In a FinFET with an undoped channel the threshold voltage is set mainly by the gate metal\'s work function, not by dopants in the channel.', None, None, 'generic', 'zhao',
  quote='"The relation between Vt and the work function of the gate electrode for FinFETs with undoped channel is different to that for the planar MOSFETs. For planar devices, there are plenty of charges to form inversion. For undoped FinFETs, much less charges are available."')
F('gate.cap-fin', g, ['gate', 'finfet'], 'One fin\'s gate is a capacitor of roughly 60-90 aF (0.06-0.09 fF): 110 nm of wrapped width by 16.5 nm of length at an equivalent oxide of 0.7-1 nm.', 0.075, 'fF (order of)', 'inferred',
  ('arithmetic on n7.weff, n7.leff and gate.eot', None),
  quote='C = 3.9 x 8.854e-12 F/m / EOT x (110 nm x 16.5 nm) = 63 aF at 1 nm, 90 aF at 0.7 nm',
  note='Oxide capacitance only; the real gate also has overlap and fringe capacitance to the contacts (adds), and quantum effects that thin the inversion charge (subtracts).')

g = 'dope'
F('dope.channel', g, ['channel'], 'The channel inside the fin is left undoped or lightly doped: the gate surrounds it on three sides, so there is no need for heavy doping.', None, None, 'generic', 'hu7',
  quote='"There is no need for heavy doping in the channel to reduce Wdep. This leads to low vertical field and less impurity scattering; as a result the mobility is higher"')
F('dope.levels', g, ['channel', 'fin'], 'Fin doping in bulk FinFETs: about 1e18 cm^-3 with a conventional implant, about 1e16 with a super-steep retrograde profile; a punch-through stopper of 2.5-5e18 at the base of the fin blocks leakage under the channel.', 1e18, 'cm^-3 (conventional fin)', 'outside', 'berkeley',
  quote='"If a bulk-silicon wafer is used as the substrate, heavy doping is needed at the base of the fins to suppress off-state leakage current (Ioff). However, a conventional doping process results in dopants within the fin (channel region), on the order of 1 x 10^18 cm^-3." Table 1.1: Nfin 1e18 (control) / 1e16 (SSR); Nfin,peak 2.5e18 / 5e18; NSD 2e20',
  note='TCAD study values; TSMC\'s profile is not published. Intel 10 nm uses a solid-source diffusion punch-stopper (cmp.intel10).')
F('dope.n-sd', g, ['finfet'], 'NMOS source and drain: phosphorus-doped silicon grown epitaxially, up to 1.75e21 P atoms per cm³ (about 3% of the atoms), of which only about 1.3e20 are electrically active.', 1.75e21, 'cm^-3', 'outside', 'amat-sip',
  quote='"total [P] by SIMS in HS Si:P epitaxial film is 1.75E+21 at/cc (~ 3 at.% in silicon)"; "only ~1.3E+20 at/cc phosphorous atoms are electrically active"',
  note='Applied Materials\' research film (2014), representative of FinFET Si:P source/drain epitaxy; TSMC\'s values are not published.')
F('dope.p-sd', g, ['finfet'], 'PMOS source and drain: boron-doped silicon-germanium, with boron of the order of 1e20 per cm³ (a patent\'s range runs from below 1e20 to above 2e20); the larger germanium atoms squeeze the channel, which speeds holes.', 2e20, 'cm^-3 (order of)', 'outside', 'qc-pat',
  quote='"one example range of boron concentration that may be used in forming a SiGeB epi layer ... may span from, for example, less than 1E20 at/cm3 and may encompass, for example, greater than 2E20 at/cm3."',
  note='A patent range, not a product measurement. The strain statement is generic: TSMC calls its epitaxy one "that strains the transistor channel" (n7.features).')
F('dope.donor-acceptor', g, ['crystal', 'channel'], 'Dopants work by valence: phosphorus or arsenic (5 outer electrons) gives one free electron (a donor); boron (3) leaves a hole (an acceptor). Freeing the extra electron takes only about 50 meV, about twice kT at room temperature, so dopants are almost all ionised.', 0.05, 'eV (ionisation energy)', 'generic', 'hu1',
  quote='"group V elements such as As ... bring five valence electrons with each atom. While four electrons are shared with the neighboring Si atoms, the fifth electron may escape to become a mobile electron, leaving behind a positive As ion." / "it takes the donor ionization energy (about 50 meV) to free the extra electron"')
F('dope.count-channel', g, ['channel'], 'A channel 6 x 16.5 x 52 nm holds about 257,000 silicon atoms but only 0.05 to 5 dopant atoms (at 1e16 to 1e18 per cm³): often none. That is why random dopant fluctuation would wreck such a device if it relied on channel doping.', 257000, 'Si atoms in the channel', 'derived',
  ('arithmetic on n7.fin-width, n7.leff, n7.fin-height, si.density and dope.levels', None),
  quote='V = 6 x 16.5 x 52 = 5,148 nm³ = 5.15e-18 cm³; x 5.0e22 = 2.57e5 Si atoms; x 1e16 = 0.05, x 1e17 = 0.5, x 1e18 = 5.1 dopant atoms',
  note='Uses Leff for the length; the drawn gate is a little longer.')
F('dope.count-sd', g, ['finfet'], 'At 1.75e21 per cm³ the source and drain hold 1.75 phosphorus atoms per cubic nanometre, one atom in 29; only about one of every thirteen of them (1.3e20 per cm³) is electrically active and gives its electron.', 1.75, 'P atoms per nm³', 'derived',
  ('arithmetic on dope.n-sd and si.density', None), quote='1.75e21 cm^-3 x 1e-21 cm³/nm³ = 1.75 /nm³; / 49.9 Si per nm³ = 3.5% (1 in 28.5); 1.3e20 / 1.75e21 = 7.4% (1 in 13.5)')

g = 'silicon'
F('si.lattice', g, ['crystal'], 'Silicon is a diamond-cubic crystal with a 0.5431 nm cube; every atom bonds to four neighbours 0.235 nm away.', 0.5431, 'nm', 'outside', 'nist-asil',
  quote='"5.431 020 511(89) x 10^-10 m" (CODATA 2022); Hu ch. 1: "each and every silicon atom has four other silicon atoms as its nearest neighbor atoms"',
  note='Bond length a x sqrt(3)/4 = 0.2352 nm (derived).')
F('si.density', g, ['crystal', 'channel'], '5 x 10^22 silicon atoms per cm³: 50 per cubic nanometre.', 5e22, 'atoms/cm³', 'outside', 'ioffe-basic',
  quote='"Number of atoms in 1 cm3: 5*10^22"; "Lattice constant: 5.431 A"; "Dielectric constant: 11.7"; "Crystal structure: Diamond"',
  note='8 / a³ = 49.94 per nm³ (derived).')
F('si.planes-width', g, ['crystal', 'fin'], 'Across a 6 nm fin there are about 31 planes of atoms (11 unit cells); along a 16.5 nm channel about 86 planes (30 unit cells); up a 52 nm fin about 383 planes (96 unit cells).', 31, 'atomic planes across the fin', 'derived',
  ('arithmetic on si.lattice, n7.fin-width, n7.leff, n7.fin-height', None),
  quote='(220) planes a/sqrt(8) = 0.192 nm apart: 6/0.192 = 31, 16.5/0.192 = 86; (400) planes a/4 = 0.136 nm apart: 52/0.136 = 383',
  note='Assumes the usual orientation: a (100) wafer, the channel along <110>, so fin sidewalls are (110) planes (an assumption; TSMC does not say).')
F('si.bandgap', g, ['crystal', 'finfet'], 'Silicon\'s band gap is 1.12 eV at room temperature (1.11 eV at the card\'s 80 °C): an electron needs that much energy to leave a bond and conduct.', 1.12, 'eV', 'outside', 'ioffe-band',
  quote='"Energy gap 1.12 eV"; "Eg = 1.17 - 4.73*10^-4*T^2/(T+636) (eV)"; Hu ch. 1: "This band gap is 1.12 eV for Si."',
  note='At 353 K the formula gives 1.110 eV (derived).')
F('si.ni', g, ['crystal', 'channel'], 'Pure silicon has only about 1e10 free electrons per cm³ at room temperature (about 4e11 at 80 °C): in one 5,148 nm³ channel that is 0.00000005 electrons. Every carrier that conducts comes from the gate\'s field and the doped source and drain.', 1e10, 'cm^-3', 'outside', 'ioffe-band',
  quote='"Intrinsic carrier concentration 1*10^10 cm-3"; Hu: "ni at room temperature is roughly 10^10 cm^-3 for Si"',
  note='At 80 °C: ni x (T/300)^1.5 x exp(-Eg/2kT ratio) = about 42x, 4e11 cm^-3 (derived); the count in a channel: 1e10 x 5.15e-18 = 5e-8.')
F('si.mobility', g, ['channel'], 'In pure silicon electrons move about 3 times more easily than holes (mobility up to 1,400 vs 450 cm²/V·s); electrons saturate at about 8e6 cm/s, so crossing a 16.5 nm channel takes about 0.2 ps.', 1400, 'cm²/V·s (electrons, upper bound)', 'outside', 'ioffe-elec',
  quote='"Mobility electrons <=1400 cm2 V-1s-1"; "Mobility holes <=450 cm2 V-1s-1"; Hu ch. 6: "It is known that vsat is 8 x 10^6 cm/s for electrons and 6 x 10^6 cm/s for holes."',
  note='Transit time 16.5e-7 cm / 8e6 cm/s = 0.21 ps (derived), against a 1.67 ns cycle at 600 MHz.')
F('si.atom', g, ['atom'], 'A silicon atom: 14 protons and 14 electrons, 4 of them valence electrons shared in bonds; 92.2% of silicon is silicon-28 (14 neutrons), 4.7% Si-29, 3.1% Si-30.', 0.92223, 'fraction 28Si', 'outside', 'nist-iso',
  quote='"28Si 0.922 23(19)", "29Si 0.046 85(8)", "30Si 0.030 92(11)"; Hu ch. 1: "Silicon is a group IV element in the periodic table and has four valence electrons."')
F('si.nucleus', g, ['nucleus'], 'The silicon-28 nucleus has a charge radius of 3.12 fm (3.12 x 10^-15 m): about 8.1 fm across, some 29,000 times narrower than the 0.235 nm an atom takes in the crystal.', 3.1224, 'fm', 'outside', 'konig',
  quote='28Si charge radius "3.1224 (24)" fm (Table 1, from Angeli and Marinova 2013)',
  note='A uniform sphere with that rms radius has radius sqrt(5/3) x 3.1224 = 4.03 fm, 8.06 fm across; 0.2352 nm / 8.06 fm = 29,200 (derived).')

# =====================================================================================================
# 4. Electronics: how a FinFET switches, charges, electrons
# =====================================================================================================
g = 'electronics'
F('el.switch', g, ['finfet'], 'A MOSFET is a voltage-controlled switch: the gate voltage decides whether current flows between source and drain. Above threshold the gate\'s field pulls a thin layer of electrons (the inversion layer) to the fin\'s surfaces, connecting source to drain.', None, None, 'generic', 'hu6',
  quote='"At the most basic level, a MOSFET may be thought of as an on-off switch ... The gate voltage determines whether a current flows between the drain and source or not." / "When Vg is equal to Vdd ... an inversion layer is present"')
F('el.off-not-off', g, ['finfet'], '"Off" is not totally off: below the threshold the current falls only tenfold per 60 mV x eta (65 mV in N7). This subthreshold current is the leakage.', 60, 'mV/decade (room-temperature limit)', 'generic', 'hu7',
  quote='"At room temperature, the function exp(qVgs/kT) changes by 10 for every 60 mV change in Vgs, therefore exp(qVgs/ηkT) changes by 10 for every η x 60 mV ... η x 60 mV is called the subthreshold swing" (section 7.2 "Subthreshold Current - \'Off\' Is Not Totally \'Off\'")')
F('el.ss-80c', g, ['finfet'], 'The swing scales with absolute temperature: the 59.5 mV/decade limit at 300 K is 70 mV at the card\'s 80 °C, and N7\'s 65 becomes about 77, one reason leakage climbs when the chip is hot.', 77, 'mV/decade at 80 °C', 'derived',
  ('C. Hu eq. 7.2.6 (S proportional to T) with n7.ss and NIST k, e', S['hu7'][1]),
  quote='kT/q x ln 10 = 59.5 mV at 300 K, 70.1 mV at 353 K; 65 x 353/300 = 76.5 mV',
  note='Leakage also rises because the threshold voltage drops with temperature (generic); the measured total doubles every 25 °C (et.leak-double).')
F('el.finfet-why', g, ['finfet', 'fin'], 'Why fins: a thin body with gates on several sides leaves no leakage path far from a gate, so the gate holds the channel shut better and transistors can be shorter, leak less and drive more.', None, None, 'generic', 'hu7',
  quote='"very thin so that no leakage path is far from one of the gates ... For these reasons, a multigate MOSFET can have shorter Lg, lower Ioff, and larger Ion than a single-gate MOSFET." / "A tall FinFET has the advantage of providing a large W and therefore large Ion while occupying a small footprint."')
F('el.dynamic', g, ['gate', 'minion'], 'Every switching cycle moves a charge C x Vdd from the supply into a node and dumps it to ground: dynamic power = k C Vdd² f. Halving the voltage quarters the energy per switch, which is why lowering the voltage saves so much.', None, None, 'generic', 'hu6',
  quote='"In each switching cycle, a charge CVdd is transferred from the power supply to the load, C. ... P_dynamic = Vdd x average current = kCVdd^2 f ... Power consumption can be reduced by lowering Vdd and by minimizing all capacitances"')
F('el.kt', g, ['crystal', 'finfet'], 'Thermal energy kT is 25.9 meV at room temperature (30.4 meV at 80 °C): the band gap is about 43 kT, so thermal agitation alone frees almost no electrons; the dopants\' 50 meV is only 2 kT, so they are all ionised.', 25.85, 'meV at 300 K', 'derived',
  ('NIST k and e (CODATA 2022)', S['nist-k'][1]), quote='k = 1.380649e-23 J/K, e = 1.602176634e-19 C: kT/e = 25.85 mV (300 K), 30.43 mV (353 K); 1.12 / 0.02585 = 43')
F('el.electron', g, ['all'], 'The charge of one electron is 1.602176634 x 10^-19 C (exact by definition), so 1 fC is 6,242 electrons.', 1.602176634e-19, 'C', 'outside', 'nist-e',
  quote='"1.602 176 634 x 10^-19 C (exact)"')
F('el.channel-electrons', g, ['channel', 'finfet'], 'When a single fin is on at the minion\'s 0.517 V, its channel holds only about 85-120 electrons (with an assumed 0.3 V threshold); at N7\'s nominal 0.75 V, about 180-250.', 100, 'electrons (order of)', 'inferred',
  ('arithmetic on gate.cap-fin, et.v-minion and an assumed threshold', None),
  quote='Q = C_gate x (Vgs - Vt): 63-90 aF x 0.217 V = 13.6-19.5 aC = 85-122 electrons; x 0.45 V = 176-253',
  note='Vt of 0.3 V is an assumption (n7.vt-abs is unknown); the count is a gate-oxide-capacitor estimate, ignoring quantum and fringe effects.')
F('el.sram-node', g, ['sram', 'l2', 'cell6t'], 'A 6T SRAM bit is held as a voltage on two tiny nodes. Each node is roughly 0.1-0.3 fF (the gates of the other inverter\'s two 1-fin transistors plus three drains and a few tens of nanometres of wire); at the 0.705 V SRAM rail that is about 440-1,300 electrons, roughly a thousand.', 900, 'electrons per storage node (order of)', 'inferred',
  ('arithmetic on gate.cap-fin, n7.sram-dims, et.v-sram', None),
  quote='Q = C V: 0.1 fF x 0.705 V = 0.07 fC = 440 e; 0.2 fF = 880 e; 0.3 fF = 1,320 e',
  note='No source publishes an N7 storage-node capacitance; the range is built from two fin gates (~0.13-0.18 fF) plus drain and wire capacitance. The cross-coupled inverters keep restoring it, so it needs no refresh (memory-levels l2:l2.seq.no-refresh.01). In the minion\'s latch arrays at 0.517 V the same capacitance holds about 320-970 electrons.')
F('el.dram-cell', g, ['dram', 'cell1t1c'], 'A DRAM bit is charge on one capacitor: modern cells (2019-2022 generations) are under 10 fF, heading to 6-7. At about 1-1.1 V that is roughly 45,000-70,000 electrons for a full cell; the sense amplifier sees half of that against the half-voltage bitline.', 60000, 'electrons (order of)', 'inferred',
  ('arithmetic on TechInsights\' cell capacitance and the LPDDR4X array voltage (assumed about VDD2 = 1.1 V)', S['ti-dram'][1]),
  quote='TechInsights: "D1z and D1a cell capacitances are now lower than 10 fF/cell". Q = 7-10 fF x 1.0-1.1 V = 7-11 fC = 44,000-69,000 electrons',
  note='The card\'s LPDDR4X die (Micron) and its generation are not known (memory-levels dram.org.part); the array voltage is an assumption. A DRAM cell holds about 50 times more electrons than an SRAM node, because it has no circuit to restore it and must survive 32 ms between refreshes.')
F('el.dram-leak', g, ['dram', 'cell1t1c'], 'To lose no more than a tenth of 60,000 electrons in a 32 ms refresh window a DRAM cell may leak only about 190,000 electrons a second: 30 femtoamps, about 50,000 times less than the average transistor\'s leakage on this chip.', 3e-14, 'A (budget)', 'inferred',
  ('arithmetic on el.dram-cell, the JEDEC LPDDR4 32 ms refresh window (memory-levels dram:gen.refresh) and et.leak-per-tr', None),
  quote='6,000 e / 0.032 s = 1.9e5 e/s = 3.0e-14 A; vs 1.4-1.9 nA per transistor: 1.4e-9 / 3.0e-14 = 47,000',
  note='The tenth is an illustrative margin, not a JEDEC figure.')
F('el.bus-bit', g, ['wire', 'lane'], 'Toggling one operand-word bit outside the tensor unit costs 15.5 fJ: an effective 58 fF of wire and drivers at 0.517 V, about 190,000 electrons; wires, not transistors, hold most of the switched charge.', 58, 'fF effective', 'derived',
  R('docs/energy-manual/03-instructions.md (bus 15.539 fJ)'), quote='C = 15.539 fJ / 0.517² = 58 fF; Q = 30 fC = 188,000 electrons',
  note='Same E = C V^2 convention as et.flip-reg; a toggle that only discharges draws nothing from the supply, so this is an upper bound on C.')

g = 'wire'
F('wire.cu', g, ['wire'], 'Copper is face-centred cubic, 0.3615 nm cube, resistivity 16.78 nΩ·m in bulk: a 20 nm-wide M0-M4 wire is about 78 copper atoms across, thin enough that surface scattering raises its resistance well above bulk.', 0.3615, 'nm (Cu lattice)', 'outside', 'wp-cu',
  quote='"a = 361.50 pm (at 20 °C)"; "16.78 nΩ·m (at 20 °C)"',
  note='78 atoms: 20 nm / (0.3615/sqrt 2 = 0.256 nm nearest-neighbour distance) (derived); the size-effect remark is generic.')

# ---- checks and write ----
ids = [f['id'] for f in facts]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
for f in facts:
    assert f['statement'] and f['source'], f['id']
    if f['kind'] in ('outside', 'generic', 'spec'):
        assert f['url'] and f['quote'], f['id']
    if f['kind'] in ('derived', 'inferred'):
        assert f['quote'], f['id']
kinds = {}
for f in facts:
    kinds[f['kind']] = kinds.get(f['kind'], 0) + 1
out = {'meta': {'title': 'TSMC N7, the ET-SoC-1 and the electronics: facts for the ladder\'s inward scales',
                'written': '2026-10-01', 'by': 'build_process.py (worktree branch ladder; research only, no card access)',
                'n_facts': len(facts), 'kinds': kinds, 'labels': LABEL,
                'sources': {k: {'citation': v[0], 'url': v[1]} for k, v in S.items()},
                'local_copies': 'kept in the work directory of the session that read them (HC33 slides, Hu chapters, IRDS MM, WikiChip archive captures, Berkeley report, ALD review); not committed',
                'note': 'Quotes are verbatim from the source as read (PDF text extraction or the page); for derived and inferred facts the quote field holds the arithmetic.'},
       'facts': facts}
json.dump(out, open(OUT, 'w'), indent=1, ensure_ascii=False)
print('wrote', OUT, len(facts), 'facts', kinds)
