# E131: E95's thirty real tiles on aifoundry1 card 1, scored (600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 7, "More real tensors"** (Q134 left it: "E95's thirty tiles are still not scored on a second card"), and Q134's final critic, its item 9 ("E95's pass on aifoundry1 card 1, with four or five passes and a set-aside rule written first").*

*Mon 2 Nov 2026 (week 45), Q136, lane `a1c1-e131-real-tiles`. Pre-registered in `959f635e` (committed 11:12:52 PST, pushed by 11:12:55, before the
claim and the first device access): [`tools/claims-v3/e131/E131.md`](../../../../tools/claims-v3/e131/E131.md), frozen numbers in
`predictions-e131.json`. No amendment. aifoundry1 card 1 (`V3_DEVICE=1`, its own lock) at 600 MHz, 498.6 mV mean; `ettelem config` read at the
session's start (11:14:01 PST: TDP 65 W, threshold 65 °C, `low_power`, 600 MHz, 500 mV) and end (11:55:12: 65 W, 65 °C, `managed_power`, 600 MHz,
499 mV), and at both ends of every block, always 65 / 65 / 600; **nothing was set, and no WRITE was sent** (§ Device commands sent). The day's
one card post in #community-lab, message 1566837317765963987, gained this card's clause at 11:13:54 PST and lost it at 11:55:49: **41.2 card-minutes
of device access (11:14:01–11:55:12, T0 + 2,471 s) of the registered 45**, 41.9 minutes claim to release.*

**What ran.** One session, E95's 53-run pass unchanged (Q132(r)'s thirty real2 tiles, three of E86's tiles, E78's six anchors three times, the
tie twice), E78's runner and reduction and E95's card code byte for byte, on four passes (13110–13113) after the smoke (13101). **D** is a tile's
board power over its own format's all-zeros level, **S** over idle, **whole board** the window's leakage-corrected power; **r** is D over the
same pass's random kind of that format (`fp32.randn`, `fp16.randn`, `int8.full`). The primary reduction removes card 1's launch-gap meter dips
and corrects leakage at E82's frozen 0.2414 W/°C. Intervals are 95% over kept passes, t(0.975, 3) × SE = 3.182 × SE; a difference is paired
within the pass. The numbers below come from [`scored.json`](scored.json) and [`results.md`](results.md) (the registered scorer's output) and
[`readme-numbers.txt`](readme-numbers.txt) (derived, every one printed by [`readme-numbers.py`](readme-numbers.py)).

## Results

**All four passes kept (212 of 212 runs), so the primary reading S1 carries every verdict and the set-aside rule restored nothing. Of E95's 13
frozen claims, 10 PASS, 1 FAILS (C1) and 2 read INCONCLUSIVE (C5, C7): verdict for verdict what E95's registered dips-removed arm read on
aifoundry3. All three cross-card rules PASS: the ranks agree (ρ 1.000, 1.000, 0.984), the tiles share E82's card scale (median 1.0238), and
33 of 33 tiles' ratios to random agree within their bands. The session tie to E82's card-1 cells passes in all four cells.**

| claim | says | PASS if (card-1 view) | E131 on card 1 | verdict | E95 on aifoundry3: dips-removed arm / registered primary |
|---|---|---|---|---|---|
| **C1** | no-zero fp32, fp16 within 2% of random in every model | every cell's r interval inside [0.98, 1.02] | gpt2/fp32 0.9830 ± 0.0052 INCONCLUSIVE; **gpt2/fp16 0.9563 ± 0.0094 FAIL**; bert/fp32 0.9898 ± 0.0080 PASS; bert/fp16 0.9918 ± 0.0146 INCONCLUSIVE; vit/fp32 0.9974 ± 0.0144 PASS; vit/fp16 0.9817 ± 0.0107 INCONCLUSIVE | **FAIL** | FAIL / FAIL |
| **C2** | they sit below random on average | each format's upper bound < 1 | fp32 0.9883 ± 0.0076; fp16 0.9766 ± 0.0026 | **PASS** | PASS / INCONCLUSIVE |
| **C3a** | a ReLU tile's D follows its live share | all 7 inside the gate-law interval | 7 of 7 | **PASS** | PASS / PASS |
| **C3b** | D's slope on live share ÷ L | in [0.85, 1.25] | fp32 0.949, fp16 0.937 | **PASS** | PASS / PASS |
| **C4** | a window costs more in fp16 than fp32 | r(fp16) − r(fp32) lower bound > 0, all three | VGG fc2 +0.1455 ± 0.0099; ResNet l3c1 +0.0640 ± 0.0050; T5 l0 down +0.0864 ± 0.0117 | **PASS** | PASS / PASS |
| **C5** | int8 ReLU tiles follow bits more than live share | (a) nearer than (c) on both | ResNet 4.310 ± 0.179 W, nearer (a) (3.521 / 5.732); VGG 3.896 ± 0.167 W, nearer (c) (2.634 / 4.694) | **INCONCLUSIVE** | INCONCLUSIVE / INCONCLUSIVE |
| **C6** | p99.9 clip − max-abs on GPT-2's layer 11 | lower bound ≥ 1.9473 W | +2.949 ± 0.193 W | **PASS** | PASS / PASS |
| **C7** | E86's window ranks committed < per-token < p99.9, p99.99 beside | lower bounds > 0, p99.99 inside ±0.3895 W | p99.99 −0.009 ± 0.326 W; per-token −0.012 ± 0.092 W; p99.9 +0.135 ± 0.383 W | **INCONCLUSIVE** | INCONCLUSIVE / UNDER-RESOLVED |
| **C8** | asymmetric activations show the gate nothing | lower bound > 0.4868 W | +0.677 ± 0.123 W | **PASS** | PASS / PASS |
| **C9** | −0.0 passes the gate (ViT layer 11, 64% −0.0 words) | D's lower bound > 11.5619 W | D 19.726 ± 0.225 W (r 0.8232 ± 0.0116): the gate does not take −0.0 | **PASS** | PASS / PASS |
| **C10** | bf16-grid weights cost clearly less (T5 layer 0) | r's upper bound < 0.97 | r 0.8898 ± 0.0115 | **PASS** | PASS / PASS |
| **C11** | an fp16 forward pass costs what rounding costs | paired interval inside ±0.4839 W | −0.120 ± 0.223 W | **PASS** | PASS / PASS |
| **C12** | the (a) intervals hold | ≥ 20 of 25 tier-1 tiles inside | 23 of 25 (tier 2 apart, 4 of 5) | **PASS** | PASS / PASS |

| cross-card rule | threshold | E131 | verdict |
|---|---|---|---|
| **E131-X1** rank within each format, card 1 against aifoundry3 | ρ ≥ 0.90 in each | fp32 1.000 (12 of 12), fp16 1.000 (11 of 11), int8 0.984 (13 of 13) | **PASS** |
| **E131-X4** the tiles share E82's card scale | median D(aifoundry3) / D(card 1) over the 24 eligible tiles inside [1.0008, 1.0608] | **1.0238** (IQR 1.0224–1.0279; fp32 1.0231, fp16 1.0243, int8 1.0332) | **PASS** |
| **E131-X5** each tile's r replicates | ≥ 80% of tiles within 0.03 (fp32, fp16) or 0.06 (int8) | **33 of 33** | **PASS** |

Sources: `scored.json` › `claims`, `cross_card.carrying`, `set_aside`, `e95_verdicts_beside`; `readme-numbers.txt` § B and § C. Every verdict is the
same at the frozen thresholds unscaled (`claims.<C>.at_frozen_thresholds_unscaled_labelled`). The pairing is E131's primary (dips removed,
0.2414 W/°C) against E95's registered dips-removed arm (dips removed, its own `auto` slope 0.299 W/°C, five passes).

**1. On a second card, every one of the 33 tiles costs the same share of random data as on aifoundry3.** Over each format's zeros level, the
difference r(card 1) − r(aifoundry3) has medians **−0.0024 (fp32), −0.0027 (fp16) and −0.0006 (int8)** and is at most **0.0102, 0.0091 and
0.0181** in size, a third or less of X5's bands (0.03, 0.03, 0.06); card 1's own 95% half-widths on r have medians ±0.0080, ±0.0075 and ±0.0242
(`readme-numbers.txt` § C). So the per-tile ratios that E112(b)'s two passes could only describe are now a registered replicate. The ranks agree
exactly in fp32 and fp16 (ρ = 1.000) and nearly in int8 (0.984).

**2. The claims replicate, including the one that fails.** C1 fails on card 1 for the reason it failed on aifoundry3: **GPT-2's fp16 attention
tile (layer 9, queries × keys) costs 0.9563 ± 0.0094 of random fp16, against 0.9562 ± 0.0060 there**, its whole interval below the 0.98 line.
Three more cells read INCONCLUSIVE because card 1's intervals are wider (GPT-2 fp32 0.9830 ± 0.0052, BERT fp16 0.9918 ± 0.0146, ViT fp16
0.9817 ± 0.0107), and the other two PASS (`readme-numbers.txt` § B). So on both cards, real fp32 and fp16 operands with full mantissas and no exact
or negative zero cost 95.6–99.7% of random data over the format's zeros level, within 2% everywhere but in GPT-2's attention tiles (fp32 0.973,
fp16 0.956–0.970; `results.md`, Every tile). The other findings carry across:
- a ReLU tile's power follows its live share, at a slope of 0.949 (fp32) and 0.937 (fp16) of random's cost, against 0.955 and 0.929 on aifoundry3
  (C3b);
- the same zeros cost more in fp16 than in fp32, by +0.06 to +0.15 of random (C4);
- an int8 calibration is a lever: on GPT-2's layer 11, clipping at p99.9 instead of max-abs costs +2.95 ± 0.19 W, against +3.13 ± 0.14 W there
  (C6);
- ViT's layer-11 tile, 64% of whose words are −0.0, reads 19.73 ± 0.22 W, as if the gate never saw a zero (C9);
- T5's bf16-grid weights cost 0.890 ± 0.012 of random in fp32 (C10).

C5 stays INCONCLUSIVE on both cards: the int8 ResNet tile sits nearer the bits predictor (a) and the VGG tile nearer the gate law (c), on both
cards (D 4.310 and 3.896 W here, 4.356 and 3.884 W there). C7 stays INCONCLUSIVE: the GPT-2 layer-6 calibrations sit within ±0.4 W of the committed
one, with intervals of ±0.09–0.38 W.

**3. The card scale is E82's.** D(aifoundry3) / D(card 1) has a median of 1.0238 over the 24 eligible tiles (IQR 1.0224–1.0279). The rows
outside that run from 0.884 (fp32's T5 down-projection, 1.8 W) to 1.066 (int8's ViT −0.0 tile, 2.7 W), both low-power tiles. That is near E82's
1.031 over 32 synthetic kinds, measured, like this pairing, with each card at its own slope. At card 1's own fitted slope (the `auto` arm, 0.40
W/°C) the median is 1.0442, E112(b)'s post-hoc 1.0432 again; at 0.545 W/°C it is 1.0641, past the band's top (1.0608): X4 is the one cross-card
verdict that moves at an arm (`readme-numbers.txt` § C, E; the arms' medians from `e131-auto.json` and `e131-leak0.545.json` against
`dips-arm/e95-nodips.json`).

**4. The leakage slope, again.** Fitted per session (`auto`), card 1's slope came out **0.4008 W/°C** (E112(b) 0.417, E91 0.422), against E82's
0.2414 that the primary uses. The fitted slope would lower fp32 random's D by 0.51 W, fp16 random's by 0.42 W and int8 `full`'s by 0.19 W
(`readme-numbers.txt` § E). It changes no claim's verdict and no cross-card verdict (`at_arms.auto`). With the slope frozen, the session tie to
E82's card-1 cells (E82's own slope) passes with room: `fp32.randn` 23.963 ± 0.131 W against 23.987 (−0.024), `fp16.randn` +0.025, `anchor_pi`
+0.059, `int8.full` +0.022 W (bands ±0.50 and ±0.25 W; § F). With no leakage correction at all (the 0 arm), two passes are set aside by
zeros-line departures (−0.253 and −0.403 W), so that arm keeps two and scores nothing.

**5. Beside E112(b)'s two kept passes of the same pass on this card** (1 Nov; reported, never a verdict): each tile's r differs by at most 0.0091
(fp32), 0.0093 (fp16) and 0.0337 (int8), with medians −0.0014, +0.0021 and −0.0036, and D at like slopes (E131's `auto` arm against E112(b)'s
`auto`) by −0.18 to +0.20 W (`readme-numbers.txt` § D). The card read the same tiles the same way on two days.

**6. Arms and checks (reported).** Three claims move at one arm each, none at the registered primary: C5 reads PASS at 0.545 W/°C; C8 and C11 read
INCONCLUSIVE with the meter dips kept (`scored.json` › `claims.<C>.at_arms`). E78-R5's checks hold: idle consistency 0.082 W (≤ 0.15), rail lag
re-fit 1.00 s (in [0.80, 1.15]), duty 0.9957–0.9964, carry-over 0.0046 W/W, standard error 0.0007 (n 208; ≤ 0.01). The smoke (13101): 7 of 7 runs
ok, cycles per op 546 / 546 / 318, 0.5992–0.5995 GHz, its gate PASS. Cycles per op 546 / 546 / 318 in every pass; 30–34 dip samples removed per
pass.

**7. The stops were never approached.** The session's highest board reading was **60.58 W** and its hottest minion-shire reading **65 °C** (PMIC
field 62 °C), against the registered stops of 68 W and 72 °C and the firmware's PMIC alarm at 75 W / 75 °C
([`telemetry-max-e131.txt`](telemetry-max-e131.txt)).

## Device commands sent

Every command the session sent to card 1, classified from the source of its running build, **et-platform `836a4ab` (BL2 0.22.0)**. E128's
version-matched reading, run unchanged for E131, is byte-identical to E128's ([`desk/dmcmd-e131.txt`](desk/dmcmd-e131.txt)). Q136(w)'s checker over
every file the session ran read **GO with no WRITE allowed**, on the Intel before the registration
([`desk/dmcmd-audit-e131.txt`](desk/dmcmd-audit-e131.txt)) and on the box before the first device access ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt),
`session.log`: "dmcmd_audit preflight rc=0").

| # | sent by | command (id) | class (BL2 0.22.0 source, `device-bootloaders/src/ServiceProcessorBL2/`) |
|---|---|---|---|
| 1 | `ettelem config`: the session's 2 reads, each block's 2 (10 in all) | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25) | READ: `thermal_power_monitor.c:339` → `thermal_pwr_mgmt.c:613`, a copy from SP RAM |
| 2 | `ettelem config` | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` (21) | READ: `:438` → `:665`, a copy from SP RAM |
| 3 | `ettelem config` | `DM_CMD_GET_MODULE_POWER_STATE` (23) | READ: `:48` → `:551`, a copy from SP RAM |
| 4 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_FREQUENCIES` (53) | READ: `performance.c:41` → `perf_mgmt.c:276`, PLL registers and a strap read, an SP RAM copy |
| 5 | `ettelem config`, `ettelem sample` | `DM_CMD_GET_ASIC_VOLTAGE` (32) | READ: PVT voltage monitors and two PMIC voltage-register reads over I2C (allowed by the owner's rule of 2 November 2026) |
| 6 | `ettelem sample`: each block's 10 Hz sampler and `lib.sh`'s 1 s die reads | `DM_CMD_GET_MODULE_POWER` (33) | READ: `:142` → `:984`, a copy from SP RAM |
| 7 | `ettelem sample` | `DM_CMD_GET_SP_STATS` (60) | READ: a RAM copy of the SP's statistics, no reset |
| 8 | `ettelem sample` | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | READ: PVT temperature sensors, an SP RAM copy |
| 9 | `ettelem sample` | `DM_CMD_GET_MODULE_VOLTAGE` (31) | READ: nine PMIC voltage-register reads over I2C (allowed) |
| — | `sparsity_host` (the workload and the heater) | the Master Minion's device-ops: DMA writes and reads of device DRAM, kernel launches, an abort on a 6 s overrun | the workload, not a device-management command |
| — | `et-lab-manifest`, `et-holders`, `et-who` | sysfs and `fuser` reads | open no device node |

READ: the handler writes only its response, its log line and the SP's RAM copy of the value it read (an I2C read puts the register's address on
the bus through the SP's own I2C controller; only a failed read soft-resets that controller). **No WRITE was sent.** Every telemetry call went
through `tools/claims-v3/e128/ettelem_guard.sh` (`config`, `sample --seconds --every-ms`; anything else refused before the device opens), and
`lib.sh`'s drain (the vendor tool) was replaced by a refusal; the logs show neither a refusal nor a drain. **Not sent:** the statistics reset
(`DM_CMD_SET_STATS_RUN_CONTROL`, 62; no `--reset-ms`), the SP log level (67), `sptrace`, `dev_mngt_service`, the firmware-revisions query (14),
any residency read, any governor, TDP, threshold, clock or voltage set, any reset. The checker's one finding, `lib.sh:154`'s forwarded sampler
arguments, is waived on its line: `block_e131.sh`'s one `start_sampler` call passes the file and the duration only.

## Registered against what happened

| | registered (E131.md) | what happened |
|---|---|---|
| pre-registration | committed and pushed before the claim | `959f635e`, 11:12:52 / pushed by 11:12:55; claim 11:13:54 |
| desk | self-test A–E PASS; the port reproduces E112(b)'s reduction | [`selftest.txt`](../../../../tools/claims-v3/e131/selftest.txt): every check PASS; 240 per-pass values equal to E112(b)'s committed reduction, max difference 0 |
| box, before the claim | `check_e131.py` with the binaries, the preflight GO, `bash -n`, a stub queue, `V3_DRY=1` of the smoke and pass 13110 | 11:11:44 with the final files ([`logs/box-setup-2.txt`](logs/box-setup-2.txt)): HARNESS OK (23 files), GO, syntax ok, the stub queue ran five 1 s stubs; dry smoke 7 launches, dry pass 55 (30 on real2 tiles, 3 on E86's), cap 72 °C, `ET_DEVICES=1`, two config reads, no drain, no reset ([`logs/box-dry-2.txt`](logs/box-dry-2.txt)) |
| before the claim | `et-who` clean on card 1; no clause holds a card on aifoundry1 | "No process holds an ET-SoC-1 device node or card lock"; the post held only aifoundry2 |
| session | check, preflight, `et-who`, the opening config read, the smoke and its gate, the queue, the closing read, `et-who` | 11:14:01 HARNESS OK, GO, card free, config 65 / 65 / 600 / 500 mV; smoke 11:14:03–11:14:46, gate PASS; queue 11:14:46–11:55:12; closing read 11:55:12, card free ([`logs/session.log`](logs/session.log)) |
| passes | 13110–13113, then 13114 if it fits (T0 + 2,640 s, projected by the longest pass) | 652, 620, 547 and 567 s, every one rc 0; 13114 refused at T0 + 2,471 s (projected 652 s, end T0 + 3,123 s) ([`logs/queue.out`](logs/queue.out)) |
| kept passes, the set-aside rule | S1 carries with ≥ 3 | S1 kept **4 of 4**; S2 and S3 restored nothing |
| verdicts | C1–C12, X1, X4, X5 | 10 PASS, 1 FAIL, 2 INCONCLUSIVE; X1, X4, X5 PASS |
| stops | board ≥ 68 W, a shire ≥ 72 °C | maxima 60.58 W, 65 °C; no stop fired |
| budget | ≤ 45 card-minutes, first device access to last | 41.2 (2,471 s); claim to release 41.9 |

## Departures

- **None from the registered procedure.** Every pass ran in the registered order under the registered rule; no pass was started, stopped or chosen
  by hand; nothing was reduced or read for a verdict before the session ended.
- **The first pass ran slow.** It began from a 50 °C die (the card had idled since E129's release at 10:38) and took 652 s, against E112(b)'s
  491–502 s from a warm die; its runs needed 1.25 heats each against 0.85–1.06 later (`readme-numbers.txt` § A). Because the queue projects every
  later pass by the longest one, the fifth pass would have had to end by T0 + 2,640 s and was refused, as the registration expected ("four passes
  are expected").
- **The box setup ran twice.** The first run (11:08, [`logs/box-setup-1.txt`](logs/box-setup-1.txt)) found `preflight_e131.sh`'s hash different
  from the freeze, because the file list had been narrowed after the first freeze (the checker had read the freeze script's list of unsent
  commands as sends); the freeze was re-made and the second run (11:11) read HARNESS OK. Its dry blocks were skipped as already done, so they were
  re-run with `V3_FORCE=1` (`logs/box-dry-2.txt`). All of this came before the commit and the claim.
- **Beyond the registration, labelled:** before E131's data existed, the collector was run once on E112(b)'s published passes as stand-ins, in the
  lane's scratch, to test it (it reproduced self-test D; nothing committed). After the session, the collector was run twice on the same raw copy:
  first from the lane's scratch, then from a repo-relative root (`build/e131-raw`), so that the reductions name their input directories without a
  home path; the committed files are the second run's, with the same verdicts. `readme-numbers.py` and `telemetry-max-e131.txt` are derived after
  the scoring and decide nothing.
- The raw passes and the box's logs keep the box's own paths, as every raw directory here does.

## What it changes for the blog material and the hub

- **Item 7, "another card":** answered for E95's thirty tiles. On a second card, under a rule written before the data, every tile's cost relative
  to random data agrees with aifoundry3's to within 0.010 (fp32), 0.009 (fp16) and 0.018 (int8); the ranks agree; the card scale is E82's 1.024;
  and the claims read verdict for verdict as E95's dips-removed arm did. Item 7's remaining open parts are the other ones it lists: real int8 beyond
  GPT-2's tiles, an int8 calibration's effect on the clock, no-zero tiles sustained, and these tiles' heat below 12 W.
- **The blog's real-tensors sentence** can now cite two cards: real fp32 and fp16 operands with full mantissas and no exact or negative zero cost
  95.6–99.7% of random data over the format's zeros level, within 2% of random except in GPT-2's attention tiles (layer 9's fp16 tile 0.956 on both
  cards), and that one failure is a property of the tile, not of a card.
- **For the instrument record** (14-card-behaviour.md, the bullet "A session's automatic leakage slope wanders, so register one"): card 1's `auto`
  slope came out 0.4008 W/°C this session, its fourth reading near 0.40–0.42 since 31 Oct, against E82's 0.2414; frozen at E82's, the session tie
  sits 0.02–0.06 W from E82's cells (bands ±0.25 and ±0.50 W) and no pass was set aside.
- **For the runbook:** with the hot anchors kept in the pass (unlike E129's cut pass), a cool die costs mostly the first pass (652 s, then 620, 547
  and 567 s). Five of E95's passes fit 45 card-minutes only at about 511 s a pass, so on this card a fifth needs a warm start or a longer budget;
  after the fourth only 169 s were left, whatever the projection.

## Files

- Reductions and scores (the registered `collect_e131.sh`): `e131.json` (primary), `runs.csv`, `reduce.txt`, `reduce.log`; `e131-relaxed.json`
  (the set-aside rule's reduction, with `runs-relaxed.csv`, `reduce-relaxed.*`); the arms `e131-auto.json`, `e131-dipskept.json`,
  `e131-leak{0.1994,0.3803,0,0.545}.json` with their `runs-*.csv` and `reduce-*`; `scored.json` and `results.md` (every claim, every reading, every
  arm, the cross-card rows, E95's verdicts beside, the comparison with E112(b), the session tie, the checks); `score.log`; `code.sha256`.
- Raw data: `aifoundry1-c1/e131/p13110/` … `p13113/` (each block's runs, marks, plan, telemetry, configs, manifest, run log, binaries' sha256,
  tiles) and `aifoundry1-c1/e131-smoke-p13101/`; `logs/` (the session log, the queue's log, the session's two config reads with their times, the
  box's preflight, the binaries' sha256, the dry runs, the box setup, the launch).
- Derived, after the scoring: [`readme-numbers.py`](readme-numbers.py) / [`.txt`](readme-numbers.txt), [`telemetry-max-e131.txt`](telemetry-max-e131.txt).
- Desk, before the registration: `desk/history-card1.py` / `.txt` (how often E78's gates fire on card 1), `desk/telemetry-max-e112b.py` / `.txt`
  (the stops' margin), `desk/dmcmd-e131.txt` (the commands at `836a4ab`), `desk/dmcmd-audit-e131.txt` (the checker).
