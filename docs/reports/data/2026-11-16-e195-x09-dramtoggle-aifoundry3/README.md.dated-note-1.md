# E195's data README, dated note 1 (Mon 16 Nov 2026; after the data verifier): the C2 and C3 failures touch R8, R8b, R9 and R10; the rails' measured volts, the write-price label (C6 NO DATA) and no zero-filled term; six nits answered (post hoc)

*Written on aifoundry2 from about 02:35 PST on Mon 16 Nov 2026 (week 47) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e195d` of Q191, after this directory's data verifier `verify-e195d` (holds with fixes: two minor findings and six
nits, none of them a fault in a datum or a verdict; with its own reducer, written from E195.md sections 7-9 and importing nothing from
the kit, it matched the registered reduction's output on all 1,811 numbers it compared, within 1e-9 relative with the same three-decimal
t table). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `97e144c3`, 01:59:34 PST Mon 16 Nov 2026) stay as committed. **No number, rule, verdict or check reading changes, nothing is scored,
and no forecast number is here** (the model session scores its sealed forecast privately). **Every figure below is post hoc to the data
commit.** Where the figures come from: (a) the registered reducer
[`reduce_x09.py`](../../../../tools/claims-v3/e195/proposal/src/reduce_x09.py) (sha256 `999232f2...`) and the kit's checker
[`check_e195.py`](../../../../tools/claims-v3/e195/check_e195.py) `leftover` (`ef4be633...`), run by the README's section 6 commands on
the committed main passes p910-p916 (`--warmup 910`, never `--forecast`): this lane re-ran both from the repository's tree at `99bc9a38`
and got the same bytes as step 13's outputs of 01:59:52-01:59:53 PST, which the reduction's dated note is to commit (their sha256 in
section 5); (b) the session's committed log, `session/session.log`; (c) desk checks of the registered code, by line number at
`999232f2`; (d) one reading of verify-e195d's own. Interpreter: `/usr/bin/python3` 3.12.3 with numpy 1.26.4 on aifoundry2, for step 13 and for this
lane's re-run. Labels: **registered** ([`E195.md`](../../../../tools/claims-v3/e195/E195.md), the kit), **measured** (the session's
records, and the registered reducer's and checker's outputs from them), **desk check of code**, **post hoc** (desk arithmetic after the
data, deciding nothing), **REPORTED** (verify-e195d's, not re-run here).*

## 1. The C2 and C3 failures touch R8, R8b, R9 and R10 (verify-e195d's finding 1, minor)

The reducer's checks line (measured): "checks: FAIL: C2_polls_per_slot_paced, C3_late_slots_paced (C1-C6 (a FAIL names what it
touches; the data stand, read with it))". E195.md 9 (registered): "A FAIL does not remove data; the verdicts it touches are read with
it." The card lane's own report named R8 and R8b only; **the two failures also touch R9 and R10**, with all three "any line" figures and
the `wrh.scp - wrh.nst` figure.

**The two checks, arm by arm** (measured; the reducer's `checks` and `rates`; a failing value in bold):

| paced arm | what it is | C2: polls a slot over its family's zeros arm (pass: within 2 %) | C3: late slots (pass: at most 1 %) | rate (a second) |
|---|---|---|---|---|
| `rdh.z` | read, zeros | 1 (the reference) | **0.667** | 5.976e8 lines |
| `rdh.u4` | read, every byte 0x0F | **0.958** | **0.680** | 5.976e8 lines |
| `rdh.rnd` | read, random lines | 1.016 | **0.671** | 5.977e8 lines |
| `rdh.l1` | control: the same loop on one L1 line, no memory traffic | **14.448** | 0.000006 | 5.977e8 accesses |
| `wrh.z` | write, zeros | 1 (the reference) | **0.745** | 5.975e8 lines |
| `wrh.u4` | write, every byte 0x0F | 1.000 | **0.745** | 5.976e8 lines |
| `wrh.rnd` | write, random lines | 1.001 | **0.745** | 5.974e8 lines |
| `wrh.scp` | control: the same store into the minion's own on-chip memory | **4.914** | 0 | 7.470e7 stores |
| `wrh.nst` | control: the same loop, storing nothing | **4.796** | 0 | 7.470e7 stores |

The six paced memory arms kept the slot rate: 5.974e8-5.977e8 lines a second, 99.6 % of the designed 6.00e8 (E195.md 2), each within
0.5 % of its zeros arm (C4 PASS). But they were late in 66.7-74.5 % of their slots, while the three controls were almost never late and
polled 4.8 to 14.4 times as often a slot as their family's zeros arm (post hoc reading of the measured values). E195.md 2 meant the paced
zeros arms, against their controls, to "give the zero line at a rate where every core polls the clock in all arms"; in this session the
memory arms mostly did not poll.

**Which verdicts read the paced arms** (desk check of code, `reduce_x09.py` at `999232f2`). The paced arms enter only the contrasts
`RH.u4`, `RH.rnd`, `RH.zl`, `WH.u4`, `WH.rnd`, `WH.zl`, `WH.zl_nst` and `WH.scp` (lines 119-126). Those feed the rate tests of R8 and R8b
(lines 549-552 and 717-737), R9's zero line and R10's bracket and `wrh.scp - wrh.nst` (lines 520-532 and 739-745), and the three "any
line" sums built on those zero lines (lines 527-532). The controls belong to their family by the manifest (`rdh.l1` to `rdh`;
`wrh.scp` and `wrh.nst` to `wrh`; none has a designed memory line), so C2 reads them against `rdh.z` and `wrh.z`. Every other rule
(R0-R7, R11, R12) and both floors are built from the flat arms alone (`x9_rd_*`, `x9_wr_*`), whose checks C1, C4 and C5 PASS.

| the reducer's word | contrast | its arms' failing checks | the reducer's figure (measured; mean [95 % interval], 6 passes) |
|---|---|---|---|
| R8 `rd.rnd`: UNRESOLVED (late slots 0.671) | `rdh.rnd - rdh.z` | C3 on both | paced / flat pJ a line 1.023 [1.008, 1.039] |
| R8 `wr.rnd`: UNRESOLVED (late slots 0.745) | `wrh.rnd - wrh.z` | C3 on both | 1.058 [1.023, 1.092] |
| R8b `rd.u4`: UNRESOLVED (late slots 0.680) | `rdh.u4 - rdh.z` | C2 and C3 on `rdh.u4`; C3 on `rdh.z` | 1.041 [0.956, 1.125] |
| R8b `wr.u4`: UNRESOLVED (late slots 0.745) | `wrh.u4 - wrh.z` | C3 on both | 1.189 [1.087, 1.291] |
| R9: REPORTED | `rdh.z - rdh.l1` | C3 on `rdh.z`; C2 on `rdh.l1` | zero line 3906 pJ [3836, 3976]; any line 3947 pJ [3781, 4113] |
| R10: REPORTED, one end of the bracket | `wrh.z - wrh.scp` | C3 on `wrh.z`; C2 on `wrh.scp` | zero line 4285 pJ [4221, 4349]; any line 4450 pJ [4367, 4534] |
| R10: REPORTED, the other end | `wrh.z - wrh.nst` | C3 on `wrh.z`; C2 on `wrh.nst` | zero line 4890 pJ [4783, 4996]; any line 5055 pJ [4956, 5154] |
| R10: REPORTED, the store itself | `wrh.scp - wrh.nst` | C2 on both (4.914 and 4.796: 2.5 % apart) | 604 pJ a line [506, 703] |

**How each reads with them** (no verdict changes):

- **R8 and R8b stay UNRESOLVED, and the late slots decide it, not the intervals.** Both readings: on its band alone (post hoc arithmetic
  on the reducer's own intervals), `rd.rnd`'s and `wr.rnd`'s intervals lie inside R8's PER LINE band of 0.9-1.1 and `rd.u4`'s inside
  R8b's 0.8-1.2, while `wr.u4`'s straddles 1.2. The registered rule decides: R8's row carries the clause in its own words ("a leg whose
  paced arm has more than 1 % late slots is UNRESOLVED", E195.md 8), R8b's row reads "the same for 0x0F lines", and the registered
  reducer, run unchanged (E195.md 7), applies the clause to both rows (lines 717-737). Nothing is re-read: all four legs stay UNRESOLVED.
- **R9 and R10 (reported, never scored) carry the poll loops beside the memory.** Each zero line is a paced memory arm that was late in
  two thirds to three quarters of its slots, less a control that was almost never late and polled 4.8 to 14.4 times as often a slot. The
  difference therefore holds the poll loops' difference as well as the memory's, in a share this design cannot split. The three "any
  line" figures carry the same (the floor added to each comes from flat arms). `wrh.scp - wrh.nst` is two controls whose polls a slot
  differ by 2.5 %, beyond C2's 2 %.
- **E195.md 15 foresaw one cause, not this one.** It reads: "if C2 fails on `wrh.nst`, `wrh.z - wrh.nst` and `wrh.scp - wrh.nst` carry a
  poll-rate difference, and `wrh.z - wrh.scp` (one loop) does not", about a difference from the two loops' addresses mod 32. C2 does fail
  on `wrh.nst`, so those two carry it. But C2 also fails on `wrh.scp` (4.914) and C3 on `wrh.z` (0.745), so `wrh.z - wrh.scp` is touched
  as well, through the late slots. Both readings: that sentence alone would leave the `wrh.scp` end of the bracket clean; E195.md 9
  decides ("the verdicts it touches are read with it"), and C2's failure names `wrh.scp`, so both ends of R10's bracket are read with C2
  and C3. R10 is reported, so no verdict changes.

## 2. The rails' measured volts, the write-price label and no zero-filled term (verify-e195d's finding 2, minor)

- **The rails' volts.** E195.md 7 (registered): the reducer turns a rail's energy into electrons at fixed reference volts, and the data
  README reports the measured volts beside them; the README put off every price (its section 1), so they are here. Measured, by the
  kit checker's `leftover` (the mean over p910-p916 of each pass's mean of `sp.<rail>_mv[0]`): **minion 0.5219 V, SRAM 0.6980 V, mesh
  (NoC) 0.4838 V**, beside the reducer's fixed **0.522, 0.698 and 0.484 V**. The passes' means agree to the fourth decimal (minion
  0.5219 V and SRAM 0.6980 V in every pass; mesh 0.4837-0.4838 V). The fixed volts sit 0.13, 0.00 and 0.24 mV above the measured means,
  so a rail's electrons a line at the fixed volts read at most 0.05 % below what the measured volts would give (post hoc arithmetic: mesh
  0.050 %, minion 0.024 %, SRAM 0).
- **The write-price label.** E195.md 9's C6 and E195.md 15 (registered; the README's Departures 8): every `x9_` item ran `--no-ms`, so
  C6 reads **NO DATA**, and **every write price in the reduction is labelled as assuming that a full-line store reaches memory once,
  unread.** That covers each `wr.` price (the high pin, the toggle, the one, the 64- and 256-bit paths, the channel step, the zero-line
  bracket, both written "any line" figures, the write floor and the write closure), `wrh.scp - wrh.nst`, and every ratio and rule read
  from a write price (R1b-R7, the write legs of R8 and R8b, R10, and R11's write closure).
- **No zero-filled term.** E195.md 7 (registered): in a pass where the one, pin or toggle price is missing, the reducer takes that term as
  zero in that pass's floor and random closure; the kit's checker lists every such pass, and the data README names those passes beside
  the floor and "any line". The checker read, for each of p911-p916 in each direction, "the floor's and the random closure's terms all
  present", and in all "**0 pass-direction(s) with a zero-filled term of 12**". **No pass is named:** the read floor (41 pJ [-93, 176]),
  the write floor (165 pJ [137, 193]), the three "any line" figures (section 1) and both closures are computed with every term present in
  every headline pass. This matches the reducer's gates (measured): 231 runs, 0 failing a gate.
- **The interpreter** (E195.md 7): step 13 ran the reducer and the checker as `/usr/bin/python3 -I -B`, Python 3.12.3 with numpy 1.26.4,
  at the desk on aifoundry2 (01:59:52-01:59:53 PST Mon 16 Nov 2026); this lane's re-run, the same.

## 3. The six nits

1. **Card-minutes to the last card command: 38.18** (post hoc arithmetic of the log's whole-second times). The README's 38.22 (its title
   and lines 11, 68, 78 and 124) runs from the first card command (01:12:47) to the `session end` line (01:51:00). The last card commands
   were the closing config read and the closing `et-who`, both logged at 01:50:58 (`session/session.log`; `session/session-end.time` also
   reads 01:50:58): 38.18 card-minutes to them, and 41.83 from step 7's read (01:09:08) against the stated 41.87 (lines 69 and 80). Every
   reading is under the cap of 45; the README's is the larger, by 2 s.
2. **R12's two knife edges** (measured; R12 is reported only; E110's classes, E195.md 8: moves needs a mean at or below -0.30 mV and an
   interval below 0, still an interval inside +-0.30 mV). `W.c44x` (the channel step against `u4`): the DDR die reading moved **-0.325 mV
   [-0.6515, +0.0015]**: its mean is past -0.30 mV, but the interval's top end sits 0.0015 mV above zero, so it reads unresolved, not
   moves. `W.h256x` (the 256-bit path against `u4`): **-0.2991 mV [-0.6132, +0.0150]**, 0.0009 mV short of the mean that moves needs, its
   interval also reaching above zero. Both "unresolved" readings sit at the edge of moves; neither comes near still.
3. **The leakage slope's reading** (desk check of code; one REPORTED reading). E195.md 7 words the `auto` slope as "the median
   within-run slope of the runs that warm by 1 °C or more". The registered code (`leak_slope`, lines 280-288) takes a run when the range
   of its die readings is at least 1 °C (`np.ptp(T) >= 1`), which with whole-degree readings counts a run whose readings step between two
   adjacent degrees: **53 runs, 0.0367 W/°C**. Both readings: verify-e195d's post hoc literal reading (a run that rises by 1 °C or more)
   takes 6 runs and 0.0753 W/°C, and no verdict differs (REPORTED). The registered code decides (E195.md 7: run unchanged); the reducer's
   own sensitivity arms (0.2936 and 0.3803 W/°C, and unfiltered) differ on nothing (measured).
4. **The data commit's message.** The README (line 161) says the round's public-text scans read the commit message; they read it as the
   card lane wrote it. The round's commit helper then appended its two standard trailer lines (a session reference and the co-author
   line), which every lab commit of the round has carried since Q177;
   [E188's data note 1](../2026-11-15-e188-one-number-r4-aifoundry3/README.md.dated-note-1.md), section 1, is the same case. A round
   convention, for the orchestrator to decide; nothing in E195 changes. This note's commit carries the same two lines.
5. **The README's numbered sections run 1, 2, 4, 5, 6:** there is no section 3, and nothing is missing from the text (cosmetic; the README
   stays as committed).
6. **A lesson for later kits** (post hoc arithmetic of `session/session.log`). E195.md 11's estimate (a pass with its 15 s gap 5.09
   minutes, the smoke and the config reads about 2: 8 x 5.09 + 2 = 42.7 minutes) put p917's start at about the 37.6th minute (2 + 7 x
   5.09), 0.4 minutes inside the 38-minute rule. As run, T0 to the smoke gate's pass took 2.07 minutes (01:12:46-01:14:50) and each pass
   with its 15 s gap took 5.16 minutes on average (01:14:50 to 01:50:57 for seven), so p917 came due 38.18 minutes after T0 and did not
   start. p917 was marginal from the registration: a kit should leave its last planned start more room inside its n-th-minute rule than
   its estimate's error (here 0.55 minutes: 0.07 at the start and 0.49 over seven passes), or say beforehand that the last pass may fall.

## 4. What stays

`README.md` and `SHA256SUMS` stay as committed in `97e144c3`, and no committed data file changed. Every verdict and check word stands as
the registered reducer prints it (R8 and R8b UNRESOLVED; R9 to R12 reported; C2 and C3 FAIL; C6 NO DATA; the rest as printed); the
reduction's dated note is to publish them all. Nothing is scored here, and no forecast number is in this note.

## 5. Files

| path | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS`, so the line numbers above refer to their committed bytes |

The four outputs this note quotes, as step 13 wrote them and as this lane's re-run reproduced them byte for byte; the reduction's dated
note is to commit them:

| output | sha256 |
|---|---|
| the reducer's JSON (`x09-e195.json`) | `325395a9da5027f689a7c4fc67842bc786156de67500ac87fdc591898506c11b` |
| its printed lines (`x09-e195.txt`) | `1a6b2b216b9944b1808f79b9cb7f2200fee0e84c07d746aab76192614c173ef2` |
| the checker's JSON (`leftover-e195.json`) | `2bbedbc89f9df31006fcdfed14e392a9bb68b01f2caa7e18ad4f471dfee975ac` |
| its printed lines (`leftover-e195.txt`) | `eee0f2292ce85c0501368530085cfb4ba5cb3605da9450351ef33fc380f85cee` |

SPDX-License-Identifier: Apache-2.0
