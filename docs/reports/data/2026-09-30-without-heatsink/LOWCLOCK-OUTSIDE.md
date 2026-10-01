# Outside research: a slower, cooler ET-SoC-1 and imaging where the work runs

> Repository copy (30 September 2026, after review): the outside research behind the page's sources [44]-[53], with
> their verbatim quotes, copied from the working notes `~/claude/work/lowclock/outside.md` so that the repository holds
> them. The text below is unchanged except that absolute paths are written from `~`. The local PDF copies it mentions
> are not in the repository; each source is cited with its URL. Section 7's draft numbers (`outside_calc.py`) are not
> used on the page: the page's diffusion lengths and DIBL-only factor come from `imaging_calc.py` and
> `lowclock_calc.py`.


Notes for the update of "Feasibility of running the ET-SoC-1 without its heatsink"
(https://spacesheep.dev/@yaroslavvb/et-soc1-without-heatsink), after the owner's question of
30 September 2026, ~15:45 PDT: how low can the clock go (100 MHz? 10 MHz?), what is the envelope,
and can a card run about ten times slower with no heatsink so a thermal camera sees where the
computation sits.

Read 30 September 2026. Web only; no card, host or /dev/et* node was touched. Local copies of every
PDF read are in `~/claude/work/lowclock/outside_src/` (with `pdftotext` output next
to each). Quotes are verbatim from the source unless marked "read off a chart" or "search-result
snippet". Sources are numbered O1–O41 here; where the published page already cites the same
source, its number there is given as "page [n]".

Labels used below, as the set uses them: **outside** (a cited source says it), **measured** (the
repo's own record), **model**, **inference** (my reasoning from the cited facts; not measured).
Section 7 lists the few numbers I derived; they come from a DRAFT script
(`~/claude/work/lowclock/outside_calc.py`, printout `outside_calc.out`) that must be
moved into `docs/reports/data/2026-09-30-without-heatsink/` before the page quotes any of them.

---

## 0. What the sources establish (short version for the page)

1. **Lowering the clock alone does not remove the power that makes a bare card run away.**
   P = C·f·V² + P_static (O15). Esperanto's own measured idle breakdown (O3, slide 14, read off the
   chart) is 20.0 W for the card with 5.8 W on the minion rail, 1.6 W NoC, 1.7 W SRAM; Esperanto
   states the chip "can be adjusted for 10 to 60 watts under SW control" (O3 slide 6; O1 says
   "10 to 60+"). The vendor's own floor for the chip is therefore about 10 W, not ~0. The
   runaway criterion θ·dP/dT < 1 depends on dP/dT, i.e. on leakage and temperature, which the
   clock does not change at fixed voltage (inference; SET_FREQUENCY does not change voltage per the
   repo's review-governor.md). A comparable 567 mm² many-core (Intel SCC, 45 nm) "dissipates
   between 25 W and 125 W" across its whole DVFS range (O17).
2. **The lever that cuts leakage is voltage and, more strongly, temperature — not frequency.**
   At TSMC N7, DIBL is ~40 mV/V and subthreshold swing ~65 mV/decade (O11), so subthreshold
   current falls only weakly with supply (inference, section 7E: ~0.85x from 0.517 V to 0.40 V,
   ~0.65x in power once V·I is counted). Leakage rises exponentially with temperature (O18, O19).
   Claremont (Intel, 32 nm) measured leakage rising from 3% of power at 1.1 V to 50% at 0.38 V,
   and energy per cycle rising 25% from 5 °C to 60 °C at low voltage (O16).
3. **How low can the clock go, physically.** Static CMOS "has no minimum clock rate—the clock can
   be paused indefinitely" (O10). The floor is the clock generator: PLL VCOs have a minimum
   frequency and reach low outputs only through post-dividers or by bypassing to the reference
   clock (O8: SiFive FU540, VCO 2.4–4.8 GHz, outputs 20–2400 MHz, boots running "directly from
   hfclk" at 33.33 MHz; O9: Zynq UltraScale+, VCO 1.5–3.0 GHz). Esperanto clocks ET-SoC-1 with
   Movellus all-digital PLLs (O4); Movellus's N7 HPDPLL brief lists outputs of 4 MHz – 6 GHz with
   a 1–256 divider (O5). Whether a given frequency is reachable on the card is a firmware-table
   question (section 5: the repo's LVDPLL table stops at 300 MHz, the step-clock HPDPLL table goes
   down to 100 MHz; nothing at 10 MHz). Esperanto's published ET-Minion "OPERATING RANGE: 300 MHz
   TO 2 GHz" (O1 slide 7) matches the LVDPLL table's floor.
4. **Seeing the arrangement of computation does not need a slow clock; it needs a modulated
   workload and lock-in thermography.** In lock-in thermography "permanently existing heat
   sources in the device, which are not affected by the trigger signal, do not appear in the
   lock-in thermogram" and "certain activities in a logic device can be switched on or off,
   synchronized to the lock-in correlation" (O20). It detects "local heat sources ... of a few µW
   corresponding to a local temperature modulation of a few µK" (O20); noise falls as
   1/√(measurement time) (O21). Fraunhofer and AISEC used exactly this — firmware toggling a
   function periodically — to locate hard blocks "at the die level on a modern SoC" (O22). The
   static leakage background, which dominates at low clock, drops out of the image; the
   modulated part can stay small enough (a few % of power, duty-cycled) to be thermally benign.
5. **Spatial resolution in lock-in is set by the thermal diffusion length μ = √(α/(πf))** (O24),
   not by the steady-state spreading length the page uses (15–31 mm). In silicon μ is about
   5–5.6 mm at 1 Hz, 1.6–1.8 mm at 10 Hz; in copper 6.0 and 1.9 mm (draft, section 7A). The
   shire footprint is about 3.2 × 3.7 mm. So lock-in at ≳5–10 Hz separates shires on a bare or
   delidded die; through the ~1 mm copper lid the thermal wave is attenuated by roughly e^(−d/μ)
   and blurred by ~μ (inference). The camera caps the lock-in frequency at f_frame/4 without
   undersampling (O20): 15 Hz at 60 Hz, 2.15 Hz for a <9 Hz export-grade camera (O30).
6. **Camera numbers.** A current 8–14 µm microbolometer core (FLIR Boson+) specifies NETD ≤20 mK
   (Industrial) / ≤30 mK (Professional) at f/1.0, 60 Hz, thermal time constant "Nominally 8 ms"
   (O28). Export-compliant cameras run at <9 Hz (O30). Cooled MWIR InSb cameras reach ≤20–25 mK
   and 480 Hz windowed (O31), and see through silicon (O33: "Silicon has a fairly uniform 55%
   transmittance from 1.5µm to 6µm").
7. **Heat-free alternatives for an activity map:** hot-carrier photon emission from switching
   transistors (O37) and laser voltage imaging, which "allows mapping frequencies through the
   backside of integrated circuit" (O38) — both need backside access to the die (failure-analysis
   lab tools). On-die sensors: the 34 shire sensors already give a shire-level map; spectral
   methods reconstruct a full thermal map "using a minimal number of thermal sensors" (O35).

---

## 1. Esperanto's own published low-voltage / low-power figures

### O1. Hot Chips 33 slides (page [3])
D. Ditzel et al., "Accelerating ML Recommendation with over a Thousand RISC-V/Tensor Processors on
Esperanto's ET-SoC-1 Chip", 2021 IEEE Hot Chips 33 Symposium, pp. 1–23, 22 Aug 2021,
doi:10.1109/HCS52781.2021.9566904. Slides:
https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Esperanto.Dave_Ditzel.presentation.v1submitted.pdf
(local: `outside_src/hc33.pdf`, `hc33.txt`, slide images `hc33p-06.png`, `hc33p-09.png`).

- Slide 5 (the 10 mW-per-core target; a design target, not a measurement):
  "Power (Watts) = Cdynamic x Voltage2 x Frequency + Leakage"; "10mW ET-Minion core (~10W for 1K
  cores) 0.01 W 1 GHz 0.425v 0.04nF". Label: outside (design target).
- Slide 6 (read off the chart): efficiency of the 1K ET-Minions vs "Operating voltage" from 0.2 to
  0.9 V; peak at about 0.30–0.33 V labelled "8.5 W / 6 chips"; "20 W / 6 chips" at about 0.4 V
  ("Esperanto's sweet-spot for best performance"); 118 W, 164 W and 275 W single-chip points at
  about 0.65, 0.75 and 0.9 V; the curve starts at about 0.24 V and falls steeply below the peak.
  Footnote [6]: "this was a design study and does not represent any specific silicon results or
  design, each point on the curve is a differently synthesized design". Label: outside (model).
  Relevance: the fall of efficiency below ~0.3 V is the leakage-dominated regime of O14.
- Slide 7: "In-order pipeline with low gates/stage to improve MHz at low voltages";
  "OPERATING RANGE: 300 MHz TO 2 GHz" (ET-Minion). Slide 19 (ET-Maxion): "OPERATING RANGE: 500 MHz
  to 2 GHz". Label: outside.
- Slide 9 (read off the diagram): in a minion shire the four 8-core neighbourhoods and the mesh
  stop are labelled "Low Voltage"; the 4x4 crossbar and the four 1 MB SRAM banks "Nominal
  Voltage". Label: outside.
- Slide 20: "Typical operation 500 MHz to 1.5 GHz expected"; "Power typically < 20 watts, can be
  adjusted for 10 to 60+ watts under SW control"; "Each Minion Shire has independent low voltage
  power supply inputs that can be finely adjusted to mitigate Vt variation effects and enable
  DVFS"; "Status: Silicon currently undergoing bring-up and characterization". Label: outside.
  Caveat (in-repo, section 5): on the lab's PCIe dev card all minion shires share one 3-phase
  regulator output, so per-shire voltage is not available there.

### O2. IEEE Micro 2022 (page [4])
D. R. Ditzel and the Esperanto team, "Accelerating ML Recommendation With Over 1,000
RISC-V/Tensor Processors on Esperanto's ET-SoC-1 Chip", IEEE Micro 42(3):31–38, May/June 2022,
doi:10.1109/MM.2022.3140674 (CC BY 4.0). https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf
(local `outside_src/micro.pdf`).

- "In this experiment, we model the cores as being resynthesized for each particular voltage
  point" (the Fig. 1 curve is a model).
- "Reducing the operating voltage to 0.75 V, the nominal voltage in 7 nm, would result in 164 W,
  still way too high."
- "If we operate at the best energy-efficiency point (0.3 V), each chip will consume only 8.5 W"
- "if we operate around 0.4 V, one chip would take about 20 W"
- "Esperanto's sweet spot for achieving best performance will usually be for operating our
  ET-Minions between 300 and 500 mV, that is, nearest the best energy efficiency points."
- "For timing and other CAD tools, we had libraries recharacterized at 0.4 V."
- "the entire ET-Minion, including its 4-KB L1 caches, operates on a single low-voltage power
  plane."
- "These SRAM banks operate near the process-nominal supply voltage to allow higher density than
  the smaller caches within each core."
- "Shires are connected to each other via an on-chip mesh interconnect operated on its own
  low-voltage domain."
- "Maximum chip power can be set with a software API, but for recommendation tasks, we expect a
  typical operating point will be under 20 W."
- "All the Esperanto performance numbers presented at Hot Chips were projections based on
  gate-level simulations of the entire chip on a large Synopsys Zebu hardware emulation system."
Label: outside (the voltage/power pairs are modelled, per the paper's own words).
Comparison with the record (measured, docs/findings/16): the lab cards run 600 MHz at 0.517 V,
700 at 0.568, 800 at 0.618 — i.e. real silicon at 600 MHz sits above the paper's 0.3–0.5 V band.

### O3. RISC-V Summit 2022 slides — the only measured Esperanto power breakdown found
D. Ditzel, "Real World Results using Thousands of RISC-V Cores for AI and Beyond", RISC-V Summit,
San Jose, 13 Dec 2022. Event page:
https://riscvsummit2022.sched.com/event/1CD6t/real-world-results-using-thousands-of-risc-v-cores-for-ai-and-beyond-dave-ditzel-esperanto-technologies-inc ;
slides: https://hosted-files.sched.co/riscvsummit2022/f3/Esperanto%20Ditzel%20-%20Thousands%20of%20RISC-V%20Cores%20for%20AI%20and%20Beyond%20for%20RISC-V%20Summit2022.pdf
(local `outside_src/rvs2022.pdf`, slide images `rvs-14.png`, `rvs-15.png`). Not cited on the page yet.

- Slide 6: "Typical operation 500 MHz to 1 GHz" (ET-Minion); "Power typically ~20 watts, can be
  adjusted for 10 to 60 watts under SW control"; "Status: Shipping to customers".
- Slide 11 (server): "600-800 MHz typical ET-Minion speed"; "ET-SoC-1 power consumption 10W to 40W
  (workload and MHz dependent)".
- Slide 12: "84 Int8 TeraOps per card @600MHz".
- Slide 14, "PCIe Card Power typically under 40 Watts", bar chart (values printed on the bars,
  read off the image): IDLE — card 20.0 W, "RISC-V ET-Minion Processors" 5.8 W, "Network-on-Chip"
  1.6 W, "160MB of on-die SRAM" 1.7 W. Loaded examples: RESNET50-FP16 card 36.8 W with minion
  14.6 W; DLRM-RMC1-FP16 card 21.7 W with minion 6.3 W. The slide does not state the minion clock
  for these bars. Label: outside (measured by Esperanto).
- Slide 15: "Power will vary depending on benchmark and operating conditions, but here is
  recently measured data." "ET-SoC-1 power about 13.5 to 16 watts"; "A thousand 600 MHz ET-Minion
  RISC-V processors: 6 watts"; "128 MB of on-die SRAM for caches: 2.8 watts"; "44 Network-on-Chip
  connecting compute shires: 1.8 watts"; "Total PCIe card power under 30 watts for DLRM". Between
  runs the plotted SoC trace sits at about 12 W and the card at about 19 W (read off the plot,
  approximate). Label: outside (measured by Esperanto).
Use: Esperanto's own idle minion rail (5.8 W) is most of the minion rail's loaded power on the
lighter DLRM runs (6.3–6.5 W): the part a lower clock can remove is small next to what stays.
Compare the record: aifoundry1 card 0 idles at 17.97 W at 300 MHz (card0_guard.out, measured).

### O4. Movellus press release: Esperanto's clock generators
"Esperanto Technologies Adopts Movellus Maestro AI, Intelligent Clock Networks for Its ET-SoC-1
Chip", San Jose, 4 May 2021, via Design & Reuse:
https://us.design-reuse.com/news/49909/esperanto-movellus-maestro-ai-intelligent-clock-networks.html
Art Swift (CEO): "The Maestro AI intelligent clocking solution was essential in enabling us to
achieve breakthrough power efficiency." Maestro is described as "an all-digital, fully
synthesizable clocking solution". No PLL ranges given. Label: outside. Consistent with the
firmware's `dvfs_movellus_lvdpll_modes_config.h` / `__MOVELLUS_HPDPLL_MODES_CONFIG_H__` names
(section 5).

### Not found
No ISSCC or VLSI-Symposium paper on ET-SoC-1 silicon (searched). No published minion-rail
voltage floor or measured V–f curve from Esperanto; the 0.3–0.5 V figures are modelled (O2). The
repo's datasheet (external/et-man, "ET Preliminary Datasheet Rev 1.0") leaves "Recommended
Operating Conditions" and "Package Thermal Information" as "will be included in a future release".

---

## 2. How power scales with f, V and T at 7 nm

### O11. TSMC N7 device figures (IEDM 2016), via a TechInsights/Chipworks summary
Primary: S.-Y. Wu et al., "A 7nm CMOS platform technology featuring 4th generation FinFET
transistors with a 0.027um² high density 6-T SRAM cell for mobile SoC applications", IEDM 2016,
pp. 2.6.1–2.6.4, doi:10.1109/IEDM.2016.7838333 (not read; paywalled). Read: Chipworks "Real Chips"
blog, "IEDM 2016 – Setting the Stage for 7/5 nm", Solid State Technology / Semiconductor Digest,
18 Jan 2017: https://sst.semiconductor-digest.com/chipworks_real_chips_blog/2017/01/18/iedm-2016-setting-the-stage-for-75-nm/
- "Sub-threshold swing has been pushed down to ~65mV/decade, and DIBL is ~40 mV/V."
- "the effective gate length (leff) centered around 16.5 nm"; "There are four device Vt options
  with a range of ~200 mV."
(The blog's "0.27 µm2" SRAM cell is a typo for the paper's 0.027 µm².) Label: outside (secondary).

### O12. TSMC N7 SRAM functional to 0.5 V
Electronics Weekly, "7nm processes at IEDM" (Dec 2016):
https://www.electronicsweekly.com/news/business/7nm-processes-iedm-2016-10/
- "a fully functional, low-voltage 256Mb SRAM test chip with full read/write functionality down
  to 0.5V". Label: outside (secondary, TSMC's IEDM claim).

### O13. TSMC 7 nm SRAM with write assist (ISSCC 2017)
J. Chang et al., "A 7nm 256Mb SRAM in high-k metal-gate FinFET technology with write-assist
circuitry for low-VMIN applications", ISSCC 2017, paper 12.1, doi:10.1109/ISSCC.2017.7870333
(abstract via OpenAlex). "Such variation degrades SRAM performance and its minimum operating
voltage"; "all transistors (PU, PG, PD) in this bitcell have to be sized as single fin". The
abstract gives no VMIN number. Label: outside.
No open source found giving an N7 SRAM data-retention voltage; the GLOBALFOUNDRIES 22 nm study
(Dong et al., ISQED 2019, https://isqed.org/English/Archives/2019/Technical_Sessions/64.html)
shows retention voltage is set by extrinsic defects ("data retention voltage is especially
sensitive to gate oxide shorts") but gives no mV value in its abstract.

### O14. Near-threshold computing: why energy per operation rises again at low voltage
R. G. Dreslinski, M. Wieckowski, D. Blaauw, D. Sylvester, T. Mudge, "Near-Threshold Computing:
Reclaiming Moore's Law Through Energy Efficient Integrated Circuits", Proc. IEEE 98(2):253–266,
Feb 2010, doi:10.1109/JPROC.2009.2034764. Copy read:
https://courses.grainger.illinois.edu/CS534/fa2021/reading_list/5a.pdf
- "In subthreshold (Vdd < Vth), circuit delay increases exponentially with Vdd, causing leakage
  energy (the product of leakage current, Vdd, and delay) to increase in a near-exponential
  fashion. This rise in leakage energy eventually dominates any reduction in switching energy,
  creating an energy minimum"
- "Zhai's work showed that SRAMs, commonly used for caches, have a higher energy optimal
  operating voltage (Vmin) than processors, by approximately 100 mV"
- "the lower bound on Vdd in commercial applications is typically set to 70% of the nominal Vdd
  due to concerns about robustness and performance loss"
Label: outside. Use: at fixed voltage a slower clock stretches each cycle, so leakage energy per
operation grows as 1/f while leakage power stays put (inference from the quoted mechanism).

### O15. DVFS: frequency reduces only the dynamic term
E. Le Sueur and G. Heiser, "Dynamic Voltage and Frequency Scaling: The Laws of Diminishing
Returns", USENIX HotPower '10, Vancouver, 2010.
https://www.trustworthy.systems/publications/nicta_full_text/4158.pdf
- "P = Cf V² + Pstatic"
- "The small feature sizes result in leakage power reaching or exceeding dynamic power"
- "Smaller transistors have a lower threshold voltage and, because sub-threshold leakage grows
  exponentially, more current is lost into the transistor substrate."
Label: outside.

### O16. Claremont (Intel, 32 nm): a measured processor from 1.1 V down to 0.38 V
G. Ruhl, S. Dighe, S. Jain, S. Khare, S. Yada, et al., "An IA-32 Processor with a Wide Voltage
Operating Range in 32nm CMOS", Hot Chips 24, 2012:
https://old.hotchips.org/wp-content/uploads/hc_archives/hc24/HC24-6-Tech-Scalability/HC24.29.625-IA-23-Wide-Ruhl-Intel_2012_NTV_iA.pdf
(local `outside_src/claremont_hc24.pdf`).
- "Wide Dynamic Range 1.1V/741MHz/445mW to 380mV/10MHz/1.5mW"
- "Leakage power scales from 3% @1.1V to 50% @ 0.38V"
- Chart axes: "Logic Vcc/ Memory Vcc (V)" — memory held at 0.65 V while logic goes to 0.38 V
  (the SRAM floor sits above the logic floor, as O14 says).
- "4.5X Energy reduction from Vmax: 135pJ/cycle at 450mV"
- "25% increase from 5C to 60C" (energy per cycle, typical skew, near 0.45 V)
- Test note: "Most peripherals fail below 15Mhz" (their 18-year-old motherboard's peripherals).
Label: outside (measured by Intel). Use: an existence proof that a processor can run at 10 MHz —
but only by dropping voltage with frequency; at fixed voltage the leakage share would be larger
still (inference).

### O17. Intel SCC: a 567 mm² mesh many-core's floor
J. Howard et al., "A 48-Core IA-32 message-passing processor with DVFS in 45nm CMOS", ISSCC 2010,
doi:10.1109/ISSCC.2010.5434077 (abstract via OpenAlex): "A 567 mm² processor on 45 nm CMOS
integrates 48 IA-32 cores ... Fine-grain power management takes advantage of 8 voltage and 28
frequency islands to allow independent DVFS of cores and mesh. As performance scales, the
processor dissipates between 25 W and 125 W." Label: outside. (A search-result summary of
Howard's talk attributes the 25 W point to 0.7 V, 125 MHz cores, 250 MHz mesh at 50 °C; not
verified — do not use.)

### O18. Leakage vs temperature, 7 nm FinFET model
H. Sultan, S. Varshney, S. R. Sarangi, "Is Leakage Power a Linear Function of Temperature?",
arXiv:1809.03147 (2018): https://arxiv.org/abs/1809.03147
- "Subthreshold leakage power dominates the total leakage power and is also very strongly
  dependent on temperature."
- They simulate "a 7 nm multifin device using predictive models" and fit linear models over the
  "standard operating range of real ICs (40°C to 80°C)". Label: outside (simulation). Use:
  supports the page's local linear dP/dT (+0.207 W/°C measured) over a limited range, and the
  exponential law beyond it.

### O19. Temperature effect inversion in FinFETs
S. Nazar Shahsavani, A. Shafaei, S. Nazarian, M. Pedram, "A Thermally-Aware Energy Minimization
Methodology for Global Interconnects", DATE 2017:
https://past.date-conference.com/proceedings-archive/2017/pdf/0483.pdf
- "As a result of the Temperature Effect Inversion (TEI) in FinFET-based designs, gate delays
  decrease with the increase of temperature."
- "super exponential increase in leakage power due to a positive feedback between temperature
  and leakage current". Label: outside (14 nm models). Use: at low voltage a hot die is not
  slower (timing is not the risk of running bare; leakage and runaway are).

---

## 3. Imaging the pattern of computation

### O20. Lock-in thermography of ICs (page [29]; new quotes)
O. Breitenstein, C. Schmidt, F. Altmann, D. Karg, "Thermal Failure Analysis by IR Lock-in
Thermography", in Microelectronics Failure Analysis Desk Reference, 6th ed., ASM International,
2011, pp. 330 ff.: https://www-old.mpi-halle.mpg.de/mpi/publi/pdf/10496_11.pdf
- "this technique allows the detection of local heat sources at the surface of a few µW
  corresponding to a local temperature modulation of a few µK."
- "Due to its dynamic nature, lateral heat diffusion (blurring) is considerably reduced in LIT
  compared to steady-state techniques, depending on the chosen lock-in frequency."
- "since we need at least 4 frames per lock-in period, the maximum possible lock-in frequency is
  flock-in = ffr/4, which is 25 Hz for a typical frame rate of 100 Hz." ("undersampling" allows
  "lock-in frequencies in the kHz-range".)
- "the magnitude of the LIT signal always reduces with increasing lock-in frequency"
- "For a point-like heat source lying at the surface of a device, the surface temperature
  modulation field at a small lateral distance r from the source reduces with 1/r, independent of
  the thermal diffusion length"
- "In this arrangement permanently existing heat sources in the device, which are not affected by
  the trigger signal, do not appear in the lock-in thermogram. Only heat sources affected by the
  trigger signal are detected here." ... "In a similar way certain activities in a logic device
  can be switched on or off, synchronized to the lock-in correlation, which would allow an easy
  functional in-circuit test of complex logical devices based on lock-in thermography."
- "thermal waves penetrate even optically opaque materials like mould compounds. Due to the
  damping of thermal waves, using a lock-in frequency of 1 to 25 Hz allows the observation of hot
  spots through 100-400 µm package material"
- "midwave IR cameras working in the 3-5 µm range show a better spatial resolution than longwave
  cameras working at 8-12 µm."
Label: outside.

### O21. Lock-in noise vs averaging time
S. Huth, O. Breitenstein, A. Huber, D. Dantz, U. Lambert, F. Altmann, "Lock-In IR-Thermography – A
Novel Tool for Material and Device Characterization", Solid State Phenomena 82–84:741–746 (2002;
Crossref date Nov 2001), doi:10.4028/www.scientific.net/ssp.82-84.741. Copy:
https://www-old.mpi-halle.mpg.de/mpi/publi/pdf/540_02.pdf
- "The achieved temperature resolution is 35 µK (effective value) after 16 min measurement time
  and further reduces with 1/(measurement time)^1/2."
- An earlier system reached "a noise level of 0.02 mK after an acquisition time of 1000 s".
Label: outside (cooled-detector systems; a microbolometer will be noisier per frame).

### O22. Firmware-modulated lock-in localisation on a modern SoC
M. Kögel, S. Brand, C. Große, F. Altmann, B. Selmke, K. Zinnecker, R. Hesselbarth, N. Jacob
Kabakci, "Lock-in Thermography for the Localization of Security Hard Blocks on SoC Devices",
ISTFA 2023, pp. 352–359, doi:10.31399/asm.cp.istfa2023p0352 (abstract:
https://dl.asminternational.org/istfa/proceedings-abstract/ISTFA2023/84741/352/28617).
- "We use a synchronous signal to periodically activate security-related functions in the
  firmware, which causes periodic temperature changes in the activated die areas that we detect
  and localize via an infra-red camera. Using this method, we demonstrate the precise detection
  and localization of security-related hard blocks at the die level on a modern SoC."
The abstract does not say which SoC, whether it was opened, or the camera. Label: outside.

### O23. Fraunhofer IISB lock-in service sheet
"Non-Destructive Localization of Electric Active Defects: Lock-In-Thermography", Fraunhofer IISB:
https://www.iisb.fraunhofer.de/content/dam/iisb2014/en/Documents/Research-Areas/Packaging_and_Reliability/Lock-In-Thermography_FraunhoferIISB_1V4_WWW.pdf
- "High sensitivity for hot spot detection with a heat dissipation in the μW range"
- "Lock-In-Frequency (typical: 1 Hz to 25 Hz)"; advantages "Differential measurement principle",
  "Best suited for different emission coefficients of the device surface materials".
Label: outside (vendor/lab sheet).

### O24. Thermal diffusion length
J. Y. Bae et al., "3D Defect Localization on Exothermic Faults within Multi-Layered Structures
Using Lock-In Thermography: An Experimental and Numerical Approach", Sensors 17(10):2331 (2017),
doi:10.3390/s17102331, https://pmc.ncbi.nlm.nih.gov/articles/PMC5677311
- "μ = √(2α/ω) = √(α/πf_lock-in)" for "a semi-infinite homogeneous material". Label: outside.

### O25. Surface temperature amplitude under modulated heating (formula not read at source)
A. Salazar, "Energy propagation of thermal waves", Eur. J. Phys. 27:1349–1355 (2006),
doi:10.1088/0143-0807/27/6/009 (PDF host refused connections). Search-result snippet of that
paper: T_ac(x,t) = (I₀/2ε√ω) e^(−x/μ) cos(x/μ − ωt + π/4), ε the effusivity. Label: outside,
unverified; used only in the draft section 7C, which should be replaced by the page model's own
thermal calculation.

### O26, O27. Window and die materials (page [27], [26])
Crystran, silicon: https://www.crystran.com/optical-materials/silicon-si/ — "Transmission Range:
1.2 to 15 μm and 30 to >100 μm"; "Thermal Conductivity: 163 W m-1 K-1 @ 273 K"; "Specific Heat
Capacity: 703 J Kg-1 K-1"; "Density: 2.33 g/cc"; "Optical Silicon is generally lightly doped (15
to 40 ohm cm) for best transmission above 10 microns"; CZ silicon "contains some oxygen which
causes an absorption band at 9 microns".
Crystran, sapphire: https://www.crystran.com/optical-materials/sapphire-al2o3 — "0.17 to 5.5 μm";
"27.21 W m-1 K-1 @ 300 K". Label: outside. Use: a silicon window conducts ~6x better than
sapphire and passes the 3–5 µm band; neither passes cleanly the 8–14 µm band of the lab camera
(sapphire stops at 5.5 µm; silicon absorbs at 9 µm and 11–16 µm, page [28]).

### O28. FLIR Boson+ datasheet (LWIR microbolometer core)
Teledyne FLIR, "Boson+ Product Datasheet", Rev 114, Table 1 and §11.1:
https://www.acalbfi.com/nl/file/16133/Boson-Plus-Product-Datasheet-Rev-114.pdf
- "Pixel size 12 µm"; "Spectral range Longwave infrared, nominally 8 µm to 14 µm";
  "Effective frame rate User selectable from 60, 30, 20, 15, 12, 10, 8.6, and 4.3 Hz";
  "Thermal time constant Nominally 8 ms"; "Thermal sensitivity Industrial: ≤ 20 mK /
  Professional: ≤ 30 mK".
- "NEDT values shown are acceptance-test limits representing the lensless configuration with an
  f/1.0 aperture installed. With a lens installed, test limits are scaled by (f/#)²" ...
  measured "imaging a 30°C background". Label: outside.

### O29. FLIR Boson (non-plus) grades — search-result snippet only
Search results for flir.com/products/boson (the page returned 403 to the fetcher): "Industrial:
≤40 mK, Professional: ≤50 mK, Consumer: ≤60 mK", 60 Hz baseline. Label: outside, unverified.

### O30. FLIR Lepton (export-grade microbolometer)
FLIR, "Lepton Data Brief" (Lepton 2.x, 80×60): https://cdn.sparkfun.com/datasheets/Sensors/Infrared/FLIR_Lepton_Data_Brief.pdf
- "Spectral range Longwave infrared, 8 μm to 14 μm"; "Pixel size 17 μm"; "Effective frame rate
  8.6 Hz (exportable)"; "Thermal sensitivity <50 mK (0.050° C)"; "Export compliant frame rate
  (< 9 Hz)". Label: outside. Use: a <9 Hz camera limits conventional lock-in to ~2 Hz, where
  silicon's μ is ~3.5–4 mm, about one shire (draft 7A/7B).

### O31. FLIR A6700 MWIR (cooled InSb)
https://www.flir.com/products/a6700-mwir/ — "FLIR indium antimonide (InSb)"; "A6700 MWIR, A6702
MWIR: 1.0 – 5.0 µm / A6701 MWIR, A6703 MWIR: 3.0 – 5.0 µm"; "≤25 mK typical" / "≤20 mK typical";
"640 × 512"; "15 µm"; full-window frame rate "Programmable; 0.0015 Hz to 60 Hz", up to 480 fps
windowed. Label: outside.

### O32. LWIR microscope camera
Optris, "Microthermography: research on next-generation MEMS and microprocessors":
https://optris.com/application/electronics/microthermography-research-on-next-generation-mems-and-microprocessors/
- PI 640i with microscope optics, "8-14µm", "8 µm" IFOV, field of view 5.4 mm × 4.0 mm, "32 Hz
  in standard mode or 125 Hz in high-speed subframe mode". Label: outside (vendor application
  note). Use: optics are not the limit at a 3.7 mm shire pitch; heat spreading is.

### O33. MWIR through silicon (Renau group)
E. K. Ardestani, F.-J. Mesa-Martínez, J. Renau, "Cooling Solutions for Processor Infrared
Thermography", 26th IEEE SEMI-THERM Symposium, 2010: https://masc.soe.ucsc.edu/docs/semitherm10.pdf
- "IR camera operates on the 3 − 5µm wavelength (MWIR), a range of light where silicon is
  partially transparent. Silicon has a fairly uniform 55% transmittance from 1.5µm to 6µm. As a
  result, the IR camera can measure the temperature through the chip under test."
- "Our setup has a resolution of 1024x1024 pixels with sampling rates of over 100Hz."
Label: outside (same group as page [14], [41]).

### O34. IBM: power maps from IR images, per workload and frequency (page [39])
H. F. Hamann, A. Weger, J. A. Lacey, Z. Hu, P. Bose, E. Cohen, J. Wakil, "Hotspot-limited
microprocessors: Direct temperature and power distribution measurements", IEEE JSSC 42(1):56–64,
2007, doi:10.1109/JSSC.2006.885064. Abstract (via Stony Brook research portal): "An experimental
technique is presented, which allows for spatially-resolved imaging of microprocessor power
(SIMP). In a first step this method utilizes infrared (IR) thermal imaging, while the processor
is effectively cooled using an IR-transparent heat sink." A search-result summary adds that they
measured the PowerPC970MP's temperature and power fields "as a function of workload and
frequency" (not verified in the paper). Label: outside.

### O35. Full thermal maps from few on-die sensors
R. Cochran, S. Reda, "Spectral techniques for high-resolution thermal characterization with
limited sensor data", DAC 2009, doi:10.1145/1629911.1630037 (abstract via OpenAlex): "We utilize
Nyquist-Shannon sampling theory to devise methods that can almost fully reconstruct the thermal
status of an integrated circuit during runtime using a minimal number of thermal sensors ... We
develop an extensive experimental setup and demonstrate the effectiveness of our methods by
thermally characterizing a 16-core processor." Label: outside. Use: ET-SoC-1 already has one
sensor per shire (34), i.e. the shire grid is sampled; the owner's "arrangement of the
computation" at shire granularity is available without a camera (the heat-placement study).

### O36. LWIR imaging of an FPGA die
H. Amrouch, T. Ebi, J. Schneider, S. Parameswaran, J. Henkel, "Analyzing the thermal hotspots in
FPGA-based embedded systems", FPL 2013, doi:10.1109/FPL.2013.6645567: "Our experimental setup
employs a thermal camera that captures the infrared emissions from the silicon wafer of an FPGA
die". Label: outside (camera band and die preparation not in the abstract; same KIT group as
page [8], whose camera is the 8–14 µm PYROVIEW 380L, page [16]).

### O37. Photon emission from switching transistors (activity without heat)
J. A. Kash, J. C. Tsang, "Optical imaging of picosecond switching in CMOS circuits", CLEO 1997
(IBM Research): https://research.ibm.com/publications/optical-imaging-of-picosecond-switching-in-cmos-circuits
- "Hot electron light emission is used to measure the propagation of signals through the
  individual gates in fully functional CMOS circuits." Later work (Tsang, Kash, IBM J. Res. Dev.
  44(4), 2000, "Picosecond imaging circuit analysis", not read) images through the chip's back.
Label: outside. Needs a thinned backside and a near-IR photon-counting camera (failure-analysis
lab equipment); the signal is per switching event, so it works at any clock (inference).

### O38. Laser voltage imaging
G. Celi, S. Dudit, T. Parrassin, P. Perdu, A. Reverdy, D. Lewis, M. Vallet, "Thermal Frequency
Imaging: A New Application of Laser Voltage Imaging Applied on 40nm Technology", ISTFA 2011,
pp. 18–23, doi:10.31399/asm.cp.istfa2011p0018: "The Laser Voltage Imaging (LVI) technique,
introduced in 2009, allows mapping frequencies through the backside of integrated circuit."
Label: outside.

### O39. Lock-in with a phone-attachment microbolometer
N. Samadi, D. Thapa, M. Salimi, A. Parkhimchyk, N. Tabatabaei, "Low-Cost Active Thermography using
Cellphone Infrared Cameras: from Early Detection of Dental Caries to Quantification of THC in
Oral Fluid", Sci. Rep. 10:7857 (2020), doi:10.1038/s41598-020-64796-6 (abstract via Europe PMC):
"A software development kit (SDK) is developed that controls camera attributes through a simple
USB interface and acquires camera frames at a constant frame rate up to 33 fps." ... "Our
results suggest achievement of reliable performance in the low-cost platform, comparable to
those of costly and bulky research-grade systems". Label: outside (non-electronic samples).

---

## 4. PLL minimum frequencies and reference-clock bypass

### O5. Movellus HPDPLL product brief (TSMC 7 nm)
https://anysilicon.com/wp-content/uploads/2020/06/Movellus-HPDPLL-Product-Brief3.pdf
- "Input Frequency 32kHz – 100MHz"; "Output Frequency 4MHz - 6GHz"; "Divider Range 1-256";
  "Lock Time 500 ref clk cycles"; "Wide operating voltages available for DVFS (e.g. 0.58V to
  0.93V in N7)"; "Portable to any process and available in TSMC 7nm"; "Integer or fractional
  division". Label: outside (generic product brief; not ET-SoC-1's configuration).

### O6. Movellus LVDPLL, GF12LP datasheet
https://anysilicon.com/wp-content/uploads/2020/06/Movellus-LVDPLL-GF12LP-Datasheet-4.pdf
- "Input Frequency 26MHz – 100MHz"; "Output Frequency 5.9MHz – 3GHz"; "Output Divider Range
  1 – 255"; "Frequency Lock 100 refclk cycles"; "VDD 0.8V". Label: outside (a 12 nm instance of
  the same product line the ET-SoC-1 firmware names; the N7 instance's limits are not public).

### O7. Movellus ULPDPLL / LPDPLL briefs
https://anysilicon.com/wp-content/uploads/2020/06/Movellus-ULPDPLL-Product-Brief3.pdf ,
https://anysilicon.com/wp-content/uploads/2020/06/Movellus-LPDPLL-Product-Brief3.pdf
- ULPDPLL "Output Frequency 0.1kHz - 150MHz*"; LPDPLL "Output Frequency 100kHz - 1GHz*". Label:
  outside. Use: the same vendor's digital PLLs reach far below 100 MHz; the ceiling on low
  frequencies is the instance and its mode tables, not the architecture (inference).

### O8. SiFive FU540-C000 (a RISC-V SoC): VCO range, output range, boot from the reference
SiFive, "FU540-C000 Manual", v1p0, 2018, ch. 7: https://pdos.csail.mit.edu/6.1810/2021/readings/FU540-C000-v1.0.pdf
- "On power-on, the default PRCI register settings start the harts running directly from
  hfclk." (33.33 MHz)
- "The minimum supported post-divide frequency is 7 MHz"; "The valid PLL VCO range is 2400 MHz
  to 4800 MHz."; "The maximum value of DIVQ is 6, and the valid output range is 20 to 2400 MHz."
- "A glitch-free clock mux (GLCM) switches the driver of coreclk between hfclk and COREPLL at
  runtime, under control of the PRCI control register coreclksel."
Label: outside.

### O9. AMD Zynq UltraScale+ PS PLLs
AMD DS925, "PS Clocks": https://docs.amd.com/r/en-US/ds925-zynq-ultrascale-plus/PS-Clocks —
"PS_REF_CLK frequency | 27 | – | 60 | MHz"; "PLL maximum VCO frequency | 3000 ... MHz"; "PLL minimum
VCO frequency | 1500 ... MHz". Register reference UG1087 (VPLL_CTRL) has a BYPASS bit selecting
the source clock (search-result snippet; page body not retrieved). Label: outside.

### O10. Static logic has no minimum clock
Wikipedia, "Dynamic logic (digital electronics)":
https://en.wikipedia.org/wiki/Dynamic_logic_(digital_electronics) — "Static logic has no minimum
clock rate—the clock can be paused indefinitely." Dynamic logic "requires a minimum clock rate
fast enough that the output state of each dynamic gate is used or refreshed before the charge in
the output capacitance leaks out". Label: outside (tertiary; a textbook citation would be better).
Caveat (inference): other clocked blocks still impose floors — DRAM refresh, PCIe link timers,
firmware timeouts and watchdogs — so "the core logic is static" does not mean the card
tolerates any clock.

---

## 5. In-repo pointers found while researching (NOT outside sources — for the firmware/record agents to verify)

- `external/et-platform/etsoc-hal/include/hwinc/lvdpll_modes_config.h`
  (`__MOVELLUS_LVDPLL_MODES_CONFIG_H__`): minion LVDPLL modes from 100, 24 and 40 MHz inputs;
  outputs 300 MHz to 1400 MHz in 25 MHz steps. Nothing below 300 MHz — consistent with O1's
  "300 MHz TO 2 GHz".
- `.../hwinc/hpdpll_modes_config.h` (`__MOVELLUS_HPDPLL_MODES_CONFIG_H__`, "From commit 568d7c4..."):
  HPDPLL modes with outputs from 100 MHz (then 125, 150, 166, 175, 200, ...) up to 4000 MHz.
  Lowest entry: 100 MHz. No 10 MHz entry.
- `device-bootloaders/src/ServiceProcessorBL2/services/thermal_power_monitor.c` lines ~876–905:
  SET_FREQUENCY carries `use_step_clock`; for the minion PLL with `use_step_clock` it looks the
  frequency up in the HPDPLL table (`pwr_svc_find_hpdpll_mode`), otherwise in the LVDPLL table.
- `.../ServiceProcessorBL2/driver/minion_configuration.c`: the per-shire clock mux has
  `SELECT_REF_CLOCK` (used while configuring DLLs), `SELECT_STEP_CLOCK` (SP PLL 4, the HPDPLL,
  "Minion Shire PLL using Step Clock") and `SELECT_PLL_CLOCK_0` (the shire's LVDPLL). So 100 MHz
  is in a firmware table (via the step clock); the reference clock is a mux input; 10 MHz would
  need a mode the tables do not contain ("the mode must exist", review-governor.md).
- `external/et-man/txt/ET Preliminary Datasheet Rev 1.0.txt` §5.1.1: external clocks
  "clk_100_in: a 100 MHz external oscillator", "osc_24_in: a 24 Mhz external clock oscillator",
  "clk_ext_in: This clock is for a test clock. Leave unconnected."
- `external/et-man/txt/ET-PCIe-Dev-Card-V3.txt`: "The Minion and NOC use the same Texas
  Instruments TPSM831D31 voltage regulator module ... the NOC is connected to a single phase
  output with a maximum of 40A and the Minion connects to a 3-phase output with a maximum of
  120A." SRAM: "Linear Technologies LTM4680 PMBus voltage regulator module with a maximum of 60A."
  (One minion regulator for all shires: O1's per-shire supply inputs are tied together on this
  card.)

### O40. TI TPSM831D31 (the minion + NoC regulator)
https://www.ti.com/product/TPSM831D31 — "8V-14V input, 120A + 40A dual output PMBus module with
AVS and monitoring"; "Output voltage range: 0.25 V to 1.52 V"; "Programmable in 5-mV steps";
"Dual output: 120 A (3-phase) + 40 A (1-phase)". Label: outside. Use: the regulator is not what
limits a lower minion voltage; the chip, its SRAM and the firmware are (inference).

### O41. ADI LTM4680 (the SRAM regulator) — search-result snippet only
"Dual 30A or Single 60A step-down µModule DC/DC regulator with an output voltage range of 0.5V
to 3.3V" (search result; analog.com timed out). Label: outside, unverified.

---

## 6. What this means for the owner's question (inference, for the page's writer)

- 100 MHz is at least named in a firmware table (the step clock); 10 MHz is not in any table and
  would need new PLL settings. Neither changes the minion voltage, so neither removes the idle
  floor (leakage + NoC + SRAM + I/O + board), which Esperanto measured at 20 W for the card at idle
  (O3 slide 14; the SoC trace sits near 12 W between runs, read off slide 15's plot) and the
  record at 17.97 W for aifoundry1 card 0 at 300 MHz. The bare-package runaway condition is about
  dP/dT·θ, which a lower clock at the same voltage barely moves. So "10x slower, bare" is not
  10x safer; the page's model should re-run its Monte Carlo with the dynamic term scaled by f and
  the leakage law unchanged to show this with numbers.
- What does move the floor is voltage (weakly, via DIBL at N7) and temperature (strongly). Both
  are outside "clock only" and one of them (voltage writes) has a known hazard in the repo
  (tools/claims-v3/nv/).
- The owner's goal — seeing where computation runs — is better served by lock-in: keep a safe
  cooling path, toggle a workload on chosen shires at 1–15 Hz, and correlate camera frames with
  the toggle. The static background disappears from the lock-in image. Where to look from:
  (a) the back of the board under the package with the heatsink on (thick, spreading path —
  page [15] reports reduced efficiency of through-PCB paths; resolution poorer), (b) the lid
  (needs the heatsink off or windowed; ~1 mm copper), (c) a delidded die under an IR window
  (page option 5). The lab camera's frame rate sets the maximum lock-in frequency (f_frame/4).
- A camera-free version of the same experiment already exists: toggle shires and read the 34
  shire sensors (the heat-placement study) — the "arrangement of computation" at shire
  granularity.

## 7. Draft numbers (DRAFT script, not committed; see header)

`~/claude/work/lowclock/outside_calc.py` -> `outside_calc.out`:
- A. μ in silicon (k 130–163 W/mK, ρc 2330·703): 7.1–8.0 mm at 0.5 Hz; 5.0–5.6 at 1 Hz; 3.6–4.0 at
  2 Hz; 2.3–2.5 at 5 Hz; 1.6–1.8 at 10 Hz; 1.0–1.1 at 25 Hz. Copper (k 390, ρc 8960·385): 8.5,
  6.0, 4.2, 2.7, 1.9, 1.2 mm. Shire footprint 3.20 × 3.70 mm.
- B. Maximum conventional lock-in frequency f_frame/4: 15 Hz at 60 Hz, 7.5 at 30 Hz, 2.15 at
  8.6 Hz. An 8 ms bolometer keeps 0.97 of the amplitude at 5 Hz, 0.89 at 10 Hz, 0.62 at 25 Hz.
- C. 1-D amplitude over a shire for an on/off modulated power per shire (ignores the die
  thickness, lid and substrate; overstates once μ nears the shire size, i.e. below ~5 Hz):
  10 mW gives about 5.9 mK at 5 Hz, 4.2 mK at 10 Hz, 2.6 mK at 25 Hz; 1 mW about 0.59, 0.42 and
  0.26 mK. (The script also prints 2 Hz, where μ ≈ the shire size and the 1-D value is too high.)
- D. Lock-in noise with σ ≈ NETD·√(2/N) (inference): a 60 Hz, 30 mK camera reaches ~0.7 mK in 1
  min and ~0.2 mK in 10 min; an 8.6 Hz, 50 mK camera ~3 mK in 1 min and ~1 mK in 10 min (at f/1;
  a real lens scales NETD by (f/#)², O28).
- E. DIBL-only leakage change (40 mV/V, 65 mV/dec): 0.517 -> 0.45 V: current x0.91, power x0.79;
  0.517 -> 0.40 V: x0.85, x0.66; 0.75 -> 0.517 V: x0.72, x0.50. The record's measured leakage laws
  (findings/16) should replace this wherever they exist.
Reading C against D (inference): a shire-level modulation of ~10 mW (about 1% of one shire's
share of the 27.2 W switching power of the record's random-normal matmul on 1,024 minions,
12-heat-management.md, at that run's clock) is detectable on a bare die within minutes with a
60 Hz microbolometer; through the lid and TIM it will be several times weaker and blurrier.

## 8. Caveats and gaps

- Esperanto's voltage–power curve (O1 slide 6, O2 Fig. 1) is a design study; only O3 is
  measured, and O3 does not give voltages or the idle clock.
- No public ET-SoC-1 minion voltage floor, SRAM retention voltage or N7 retention figure was found.
- O11 is a secondary summary of TSMC's IEDM paper; O12 is a trade-press summary.
- O25, O29, O41, the UG1087 bypass detail (O9) and the Hamann "frequency" detail (O34) come from
  search-result snippets and are marked unverified.
- The lock-in estimates in section 7 are 1-D and ignore the lid, TIM, die thickness, the
  substrate's share of the heat and emissivity (the metal package's ~0.01, page [8]); the page's
  model should compute them properly before any number is quoted.
