# PREREG (amended): OH (E53), the effect of overheating on the ET-SoC-1

## Amendment 2, frozen 2026-09-28 11:06 PDT

It replaces PREREG.md SHA-256 `067a32b41014fdc65d0880008d090d022075b812c63e360d8dc831c4222ad22e`. The registered predictions and decision rules (prereg.json `items`) are unchanged (checked by prereg.py). OH block directories that existed on the hosts when it was frozen: {"aifoundry3": ["p201.aborted-a1", "p201.aborted-a2", "p901"], "aifoundry1": ["p201.aborted-a1", "p201.aborted-a2", "p901"]}.

**Why.** The OH-2 blocks re-run under amendment 1 (started 10:39 PDT) were stopped by hand (SIGTERM, STOP file) at
10:59 PDT. aifoundry3 had finished B0-B3 (117 checked launches, all correct) and was heating to B4; card 1 had
finished B0-B2 (81, all correct) and was heating to B3. Neither card reaches the upper targets under the frozen heater
at the chain duty (2 s launches, <= 150 s chains, 15 s gaps): card 1 with ALL24 above 75 C (its board-power rule)
plateaued at a mean of 75-76 C for 9 min (board 71 W), aifoundry3 at 82 C (B4 target 83). With the registered
holds each checked launch in such a band would first heat for the full 150 s, so B3 and B4 would have taken 1.5-3 h
per card. Both attempts were finalised like the first (status aborted) and set aside as `p201.aborted-a2`; their
checked launches are reported beside the verdicts (amendment 1's rule).

**Changes (code and three parameters; no prediction, decision rule, cap, kernel, band edge or schedule changes).**
1. `params-oh.json`: `band_heat_s` 300 (a band's first heating, was a fixed 600 s in `block.sh`), `hold_heat_s` 30
   (the heating before a checked launch, was a fixed 150 s), B4's heating target 82 C (was 83, above aifoundry3's
   plateau; the band stays 82-84 C).
2. `block.sh`: a band whose first heating does not reach its target (`HEAT_WHY` time or soft) is held one degree below
   the highest mean that heating reached (`PLATEAU`), and later bands keep that hold. `ohlib.sh`: `oh_heat_to` records
   the highest mean it saw (`HEAT_MAX`).
Every checked launch's band is still its measured mean (the hottest mean from 0.3 s before to 0.3 s after it), as
registered, so OH2-b's "hot" set is whatever reached 80-85 C; a card that never reaches 80 C has no OH2-b hot set
(INSUFFICIENT) and says so. The dry runs of these changes (V3_DRY, both hosts, and card 1 with a low simulated rest so
the plateau path runs) passed before this freeze. OH-2 is re-run from B0 as p201 under this amendment.

---

# PREREG (amended): OH (E53), the effect of overheating on the ET-SoC-1

## Amendment 1, frozen 2026-09-28 10:39 PDT

It replaces PREREG.md SHA-256 `8d620b64dc60239a104c59e3d9bd8c42cf1b4adb9e482460499dedc836f36661`. The registered predictions and decision rules (prereg.json `items`) are unchanged (checked by prereg.py). OH block directories that existed on the hosts when it was frozen: {"aifoundry3": ["p201.aborted-a1", "p901"], "aifoundry1": ["p201.aborted-a1", "p901"]}.

**Why.** The two OH-2 blocks started at 10:13 PDT (p201 on aifoundry3 and on aifoundry1 card 1) were stopped by hand
(SIGTERM to `block.sh`, STOP file for the queues) at 10:33 PDT, 20 min in, in their B2 band. Cause: a bug in
`oh_heat_to`. The watcher stops each heater launch as soon as a sample reads the mean at the heating target; the loop
then re-read the mean after the process had ended, found it one whole degree lower, and launched again, so the die was
held at the target until the time cap (B2 on aifoundry3: 600 s and 81 launches, then 150 s and 82 launches for one hold;
every mark says `"why":"time"` at a mean of 73 for the target 74). No measurement was biased by it (every checked
launch ran at its measured temperature, and all 96 checked so far were correct: aifoundry3 B0 27, B1 27, B2 15; card 1
B0 27, B1 27), but holding B3 and B4 would have taken hours, and OH-1's preheat would have held 62 C for 140 s and
pushed each condition out of its 150 s chain.

**Changes (code only; no prediction, band, cap, kernel, schedule or rule changes).**
1. `ohlib.py` watcher: a sticky `tgt_hit` field (the 15th of the state line): 1 once any sample read the mean at or
   above the current heating target, reset by the next `target` line. `ohlib.sh` `oh_heat_to`: the target counts as
   reached when the mean reads it or `tgt_hit` is 1 (and it waits 0.15 s after writing a new target so the watcher
   reads it first).
2. `reduce.py --all`: a block whose `block.json` says `"status":"aborted"` enters no verdict; its checked launches are
   reported beside the verdicts (`oh2-aborted.json`).

**The stopped blocks** were finalised by hand the same way `oh_gzip_all` does (telemetry gzipped, process outputs in
`k.tar.gz`, the op lists removed), given a `block.json` with `"status":"aborted"` and set aside as
`p201.aborted-a1` on each card. OH-2 is re-run from B0 as p201 under this amendment; its B0 waits (up to 600 s, as
registered) for the die to rest after the stopped attempt. The dry runs of the fix (V3_DRY) passed on both hosts before
this freeze.

---

# PREREG: OH (E53), the effect of overheating on the ET-SoC-1

Frozen 2026-09-28 10:11 PDT, before any OH-1 or OH-2 block on any card. 

The owner's request (28 Sep 2026, ~09:00 PDT; recorded as Q61 when the findings are updated): comprehensive outside
research on throttling and overheating, validated on the ET-SoC-1 where relevant, on one page called "The effect of
overheating". This pre-registration covers the card work only (the plan's §2: OH-1, OH-2, OH-3); the page, its sources
and the analyses of existing data are separate. Code: `tools/claims-v3/oh/` (README.md there). Every number below is a
prediction or a rule fixed now; the reducer (`reduce.py`, locked) computes the verdicts. A failed prediction is reported
as failed.

## Cards, rules and what is not changed

- **aifoundry3** (1.3.1, pinned at 600 MHz) and **aifoundry1 card 1** (1.2.0, 600 MHz in every sample since 25 Sep).
  Nothing on aifoundry2 (its Master Minion is hung since 28 Sep 02:50 PDT) and **nothing on aifoundry1 card 0**:
  every entry point refuses it; while card 1 runs, a read-only 1 Hz guard sampler on card 0 (no lock, no launch; as
  E52) must read <= 85 C to start and stops card 1's work above 90 C or when 10 s stale.
- Before every block: `others_present` (other logins on aifoundry3; on aifoundry1 other device holders, as lib.sh's
  amendment A3), no device process of anyone else, no CI runner, the card lock for the whole block; the same checks
  between every two launches. Every device process <= 10 s (`timeout 10`). Chains of back-to-back launches <= 150 s,
  then >= 15 s with no launch while the sampler runs.
- **Temperature**: the watcher reads the 10 Hz sampler; the mean **or** the hottest sensor >= 88 C, or the board >= 82 W
  for two samples, stops the heater at once (its stop file), ends the block (fail) and the session (STOP file). Soft
  caps (a sensor >= 86 C, the mean >= 85 C, the board >= 78 W for two samples) stop heater launches until the reading
  is 1 C / 2 W below the cap. The OH-2 hot band is a mean of 82-84 C (heating stops at 83).
- **No global state change**: no TDP, threshold, clock, voltage, firmware, trace-level or SP log-level command. The one
  write is the sampler's statistics reset (`ettelem sample --reset-ms 1000`, which clears the SP's min/max statistics
  and sends the PMIC its statistics reset; E52 used it on both cards), without which no windowed hottest sensor
  exists; each block first records the standing statistics read-only (`stats-before.jsonl.gz`).
- Data: `build/claims-v3/<card>/oh/p<pass>/`, collected into `docs/reports/data/2026-09-28-overheating/raw/`.

## OH-1: the hottest sensor under the most concentrated load

**Claim it settles** (page §2): on this chip the hottest sensor leads the 34-sensor mean by only 1-4 C, so the
governor's `mean > 65` acts like "hottest sensor above about 68 C" for the loads tested. The untested case is one
shire at full occupancy, the most concentrated load the heater can make.

**Design.** Conditions: IDLE (sampler only); ONE-C = S14 (grid row 3, column c3; mask 0x00004000; 32 minions);
ONE-NE = S28 (row 1, c6, next to the I/O corner; 0x10000000); B4C = S13 S14 S21 S22 (0x00606000; 128 minions;
E51's B4C@32). Shire positions from `tools/claims-v3/hp/placements.json` (an inferred die frame). A run: its own 10 Hz
sampler with `--reset-ms 1000` and the watcher; ALL24 2 s bursts to a mean of 62 C (stopped at the target); then 60 s of
the condition (back-to-back `sparsity_host --test fma --type fp32 --pattern none --values randn --shires <mask>
--per-shire 32 --seconds <= 4 --seed 1`, or 60 s idle), the preheat and the condition in one chain of <= 150 s; then 15 s
idle. Analysis windows: every successful 1 s reset window from 10 s after the condition starts to its end (for a load,
wholly inside a launch's kernel span). dhot = the window's highest sensor minus its highest mean (whole degrees).
A block = the four conditions in a row of the 4 x 4 Williams square (params-oh.json): rows 1-3 on aifoundry3 (passes
101-103), rows 1-2 on card 1 (101-102), each after that card's OH-2 block.

**Physics and data behind the predictions.** A shire at full heater occupancy switches about 0.9 W (INT16@32 is about
14 W over 16 shires, E52 development); E52's 4-shire blocks (about 3.5 W) moved dhot by 0 to +1 over idle; one shire
heats itself less than a 2 x 2 block does (less mutual heating) while the mean barely moves. The chip's power density
is low (at most about 0.10 W/mm2 on the metered rails at 86.9 W).

- **OH1-a**: every 1 s analysis window (10 s after the condition starts to its end), every condition, both cards: hottest sensor minus mean <= +4 C. FAIL if any window >= +5.
- **OH1-b**: per block, median dhot of ONE-C <= that of B4C. PASS in >= 2 of 3 blocks on aifoundry3 and 2 of 2 on card 1; otherwise FAIL.
- **OH1-c**: per card, pooled over its blocks: |median dhot(condition) - median dhot(IDLE)| <= 1 C, for ONE-C, ONE-NE and B4C separately.
- Descriptive (no verdict): the hottest sensor in every window whose mean reads 64-66 C (the governor's decision point),
  per card; the I/O-shire sensor beside the mean.

## OH-2: known-answer kernels from rest to a mean of 82-84 C

**Claims it settles** (page §3, §4): no wrong result at any temperature tested; at a fixed clock the chip does the same
work per cycle; the gap against die temperature; the DRAM refresh stays at 1x when hot. aifoundry3 had no checked launch
above 80 C and 4 at 70-80; card 1's hottest checked launch was at 83 C; the relay (DRAM and mesh data paths, exact
element checks) never ran above 66 C on any card.

**Design.** Bands of the die mean: B0 rest (aifoundry3 <= 58 C, card 1 <= 63 C; up to 10 min wait), B1 65-69, B2 72-76,
B3 78-81, B4 82-84. The heater (ALL32 2 s launches; ALL24 on card 1 above 75 C for its board power) takes the die to the
band's target (67, 74, 80, 83) and holds it: before each checked launch, heat to the target if the mean is below the
band, wait (<= 60 s) if above. Batteries (`battery.txt`, 9 kernels, each its own process, cyclically rotated): 3 in B0-B2,
4 in B3-B4; the memprobe refresh programs once in B4 (`gen_ops.py refresh --name refresh_jit --n 19000 --jitter 3000
--start 0x1000 --seed 101`, then the locked `--n 24000 --start 0x1000`). Then the cooling tail: 6 min of sampler only,
with one battery when the mean first reads <= 65 C (at the end if never). Each launch's temperature is the hottest mean
from 0.3 s before to 0.3 s after it. A launch with rc != 0 and no result line is void and run once more (aifoundry3's
1-in-100 host crash); voids are counted, never called wrong.

**Follow-up if a kernel fails** (the page's "stops hot, works cool" test): the failing kernel is repeated 3 times at the
same band, and once more in the cooling tail at <= 65 C. A failure that repeats hot and vanishes cool is a parametric
failure shown on this chip; the block records it and the session stops for the owner.

**Physics behind the predictions.** At 600 MHz the minion rail (about 500 mV on card 1, 525 mV on aifoundry3) sits at
the simulated 7 nm temperature-inversion crossover, so heat should neither eat setup margin in the minions nor move the
PLL clock; the SRAM rail (750 / 700 mV) and the wires slow slightly with heat, but aifoundry2 already computed correctly
to 97 C (checked) with its SRAM at 705 mV; the DRAM packages are cooler than the die (their temperature is not
measured), so 1x refresh should hold at a die <= 88 C.

- **OH2-a**: 0 wrong results, 0 tensor-error CSRs and 0 not-ok among all checked launches in every band on both cards. With N checked launches in a band and 0 failures the page quotes the 95 % upper bound 3/N per launch.
- **OH2-b**: for each kernel metric (fma cycles per op and gemv cycles per layer per sweep point; mmbench and relay cycles_max): |median over launches whose die mean read 80-85 C / median over the rest band B0 - 1| <= 0.1 % -> PASS; otherwise, if the hot median lies inside the rest band's [min, max] -> PASS (within noise); otherwise FAIL.
- **OH2-c**: the heater's implied clock (cycles / host wall time of its 0.5 s launches), median per 5 C band of the die mean, lies in 0.5994-0.5995 GHz in every band.
- **OH2-d**: 1 s windows inside a heater (ALL32/ALL24) launch: max dhot <= +4 in every band (60-70, 70-80, 80-85); median(80-85) - median(60-70) is 0 or +1 C.
- **OH2-e**: memprobe's refresh period (the jittered series, computed as V3's MEM-P5) at the hot band = 2,325.4 +- 0.1 minion cycles on both cards.

## OH-3: the idle law, from the idle stretches of OH-1 and OH-2 (no extra card time)

- **OH3-a**: idle samples (>= 5 s after any launch, 600 MHz) of the OH blocks: the median board power per whole degree (>= 20 samples) between 60 and 84 C is within +-1.5 W of the card's E44 law (aifoundry3 15.45 + 21.89 e^((T-80)/30); card 1 18.45 + 30.50 e^((T-80)/30)).
- **OH3-b**: refitting P_fix + A e^((T-80)/T_L) on E44's T_L grid to those bins gives a doubling interval T_L ln 2 of 17-25 C.
Card 1's W_idle drift since 26 Sep is a known risk: a FAIL there is reported, not explained away.

## Not run, and the prediction registered now

- **Transistor speed against temperature from the process detectors.** The PD oscillator select is
  `MEASUREMENT_DISABLED`, the read functions have no caller and the blocks are reachable only by the service processor:
  it needs an SP BL2 build that selects an internal delay chain, keeps the 31-cycle gate, samples the 34 PDs with each
  temperature pass and exposes the counts (a DM command or a trace line), flashed by the lab admin. *Prediction*: if the
  PDs run on the minion rail (about 0.50-0.525 V), the count changes by less than +-2 % between 55 and 85 C (at the
  crossover), and is more likely to rise (hot is faster) than to fall; on a rail >= 0.70 V the count falls, by less
  than 5 % over that range. Which rail the PDs sit on is undocumented. This is an ask for the hub.
- A DLL delay-estimation sweep (M-mode code, neighbourhood resets), a clock or voltage shmoo (admin settings), the
  power-limit hypothesis for the ~120 C stop (board power near the 88 W input), and a DRAM retention hold at a hot die
  (device buffers do not outlive a 10 s process; the DRAM temperature is not measurable): not within the rules.

## Departures from the plan (fixed here, before any data)

1. OH-1's condition uses launches of <= 4 s (the plan said 2 s) so fewer 1 s windows straddle a gap between processes;
   the preheat bursts stay 2 s ALL24. The condition is 60 s of wall time, not a count of launches.
2. OH-2 holds each band with a heating target inside it (67, 74, 80, 83 C) instead of one heater launch after each
   checked launch, which could push the die out of the band; the watcher stops each heater launch at the target.
3. OH2-b has a second, noise-aware level (PASS within noise) for kernels whose launch-to-launch spread exceeds 0.1 %
   (relay and mmbench cycle counts vary by up to 0.3 % between identical launches in earlier data).
4. The card-1 W_idle proxy of E52 is not used as a stop: the die temperature changes by design here, and idle power
   follows it. The direct card-0 guard stays.
5. The relay kernels run 64 stages (the plan said 4), about 90 ms, so each checked launch moves 2 GB through the path.
6. The smoke (901) runs after this freeze and before any OH-1/OH-2 block. If a kernel reports "unchecked" there, it is
   replaced and this PREREG is re-frozen with --replace-unused (recorded), before any OH-1/OH-2 block.

## The lock

(The lock block of this version is replaced by the amendment's lock below; this version's full text, with its own lock, is `PREREG-before-amendment-1.md`, SHA-256 8d620b64dc60239a104c59e3d9bd8c42cf1b4adb9e482460499dedc836f36661.)

## The lock (amendment 1)

(The lock block of this version is replaced by the amendment's lock below; this version's full text, with its own lock, is `PREREG-before-amendment-2.md`, SHA-256 067a32b41014fdc65d0880008d090d022075b812c63e360d8dc831c4222ad22e.)

## The lock (amendment 2)

<!-- lock-begin -->
```json
{
 "binaries": {
  "aifoundry1-c1": {
   "ettelem": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325",
   "heater": "1641d27764478465cc054ca24c38b678bbe8616c3cc1bce9f47a93ee389d2bf6",
   "heater_kernel": "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24",
   "memprobe": "0b1e4bc024bce33aa8909341f2a6323c66523ce5affbdd04ce7e78ec68af876d",
   "memprobe_kernel": "55c6dbab43929eb00e0422f73bb2bbc0f24cb891b2c2632125d211e790b0ff20",
   "mmbench": "a071fcef900bc3f3e59a609a369884ca0ce6b35eeb24195d8a119e89861ebf76",
   "mmbench_kernel": "5b2b25a98440543848dbac9ec1b4ef5e3209c9994fcf3ba5e68741836367b0d3",
   "onchip": "c281c327de81bfe55cbed4c1a5e5ff9864d57a4585a954bc49ff7e020e4b295f",
   "onchip_kernel": "b4630d14c9628928407bae59b280cfd79d9e2148b0aa5568492aeab892c27bb3"
  },
  "aifoundry3": {
   "ettelem": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",
   "heater": "20e760c20e9b99c789ef96f1e4e950d51f534410275bfb933c2aaf96d1090fd0",
   "heater_kernel": "d521e43248d00b4da455ada7020741f39b8940e52bbbce05380beccedcd17d19",
   "memprobe": "35762434ae2434532935a0a230dd22faf0348ce8aafef83dc22fbe52f3f41380",
   "memprobe_kernel": "180eb2acb032f955002f1eb64927d0f4876f714eec05bdfb91d675d2bb1408a0",
   "mmbench": "8ba18ee8759e6631c7c8a329df22fd6b6dfbb92aea09b05a86d4cd898e402f76",
   "mmbench_kernel": "3c91a87faa2406c2e4bacb9a65c57329695761b08e35560d705ceb2f35fc63cb",
   "onchip": "ea8d8282a9747711a3f5ba2c4a17444076c8f69c448c84c1c7474ebb7b279bd7",
   "onchip_kernel": "f8da0d8bf3ceb4140e09ac9ca5517d947e73baf4f981637c4af551806f9b6499"
  }
 },
 "files": {
  "tools/claims-v3/lib.sh": "033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa",
  "tools/claims-v3/oh/battery.txt": "f18c415cceb530cf3b26c468b42e21149fb812734322e117d5bfe811232da9d7",
  "tools/claims-v3/oh/block.sh": "9909206ab2a40dbff211622d4f688982b6808720f21edd80f5227a7fe5210a32",
  "tools/claims-v3/oh/ohlib.py": "12628e24d2416d48779c19f4ab85f6a6f975fd622017f0b049d890932aa5b35c",
  "tools/claims-v3/oh/ohlib.sh": "49282a84be0bc2fe8c7e60b22cd53d26c583a48dabb4b5e7593e21228df0732f",
  "tools/claims-v3/oh/params-oh.json": "3087a44b68c9be2b7792b01a9ec5796a41bb6a09043ddec691173b55ff1fae38",
  "tools/claims-v3/oh/prereg/prereg.json": "4b13e7dec36ba46a5ea92607d42e96266edc3df7fea67f24d2ee70a80fe8a973",
  "tools/claims-v3/oh/reduce.py": "915c9a13d2bc81fcbb222231d23d9c50fb75b4fc3dd55172241c5ac7969e9a6f",
  "tools/claims-v3/oh/run_queue.sh": "7d427103080f0613d84bae4fb26a46f7307f0cfbae5ac6e7e5735ed2b6bee1ff",
  "tools/claims-v3/oh/schedule-aifoundry1-c1.txt": "165c235fde7200edf7ea24b339bf9d3ec13833a70efe1e0ce8785c2c63b279d9",
  "tools/claims-v3/oh/schedule-aifoundry3.txt": "20731e7297d402804dbd9c8760d0d0cdae5a1937658d02710699c7ede94bab6a",
  "tools/claims-v3/queue.sh": "4b63600429614c2379ce6e63e0cfc4fe518e8069bfa3a01b594b663facd924e9",
  "workloads/memprobe/gen_ops.py": "379e1522c16f5cc9884263c83e29d63084989fdbe996d6a80db35e3502ac89b3"
 }
}
```
<!-- lock-end -->
