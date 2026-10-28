# E76 — the thirteen instructions that trap in U-mode: the hardware check (Q129)

## Results

*Two probe passes, `p7610`–`p7611`, Wed 28 Oct 2026 11:39:47–11:47:28 PDT on aifoundry3 card 0, 600 MHz,
`--harts 1` (1,024 harts). **7.7 card-minutes.** Both passes `block.json` `"status":"ok"`; `et-who` clean
afterwards. Pre-registered Tue 27 Oct in `2be3f07e` / `547f4ae3`. Reduced with `reduce.sh`.*

**All thirteen trap, on silicon, with a log. 13 of 13 and 7 of 7:**

> ### every one of the thirteen ended the kernel: `"ok":false`, **0 ops**, host exit 1
> `fdiv.s` · `fsqrt.s` · `fdiv.ps` · `fsqrt.ps` · `frsq.ps` · `fsin.ps` · `fdiv.pi` · `fdivu.pi` ·
> `frem.pi` · `fremu.pi` · `fcvt.l.s` · `fcvt.s.l` · `csrr cycle`
>
> and every one of the seven same-shape controls returned: `"ok":true`, **65,536 ops** (64 per hart × 1,024
> harts) — `fmul.s`, `fsgnj.s`, `fmul.ps`, `frcp.ps`, `fmv.x.w`, `fmv.w.x`, `csrr 0xcc0`.
> Unanimous across both passes; nothing unstable.

This is the replication the energy manual asked for. Its own note said these thirteen "trapped in U-mode in a
one-off check while the catalogue was written (the card and the log of that check were not kept)". There is now a
log, a build, two passes, and a control of the same shape in the same build beside every one of them. Together
with the firmware reading (below, and unchanged by this run) it closes the second half of Q128 §5 item 5:
**these instructions have no per-instruction energy because they are never executed.**

### Scoring

| Rule | Reading | Registered | Verdict |
|---|---|---|---|
| **P1** all thirteen trap | **13/13** `ok:false` with 0 ops; **7/7** controls `ok:true` with 65,536 ops; modal verdict unanimous over both passes | 13 and 7 | **PASS** |
| **P2** build independence | `trx_fdiv_ps` and `trx_fsqrt_ps` — the catalogue's own hand-written modes, present in every build — behave exactly as `trp_tr_fdiv_ps` / `trp_tr_fsqrt_ps` | agree | **PASS** |
| **P3** the trap costs time | trap launches **1.0–1.2 ms** wall, controls **0.4–0.7 ms**; excess **median 0.45 ms**, range 0.10–0.70, n = 26 | 0.5–50 ms | **FAIL** — below the floor. The trap path is *cheaper* in wall time than registered |
| **P4** no lasting harm | **33 runs after a trapping launch** in the same block, **0** not `ok`; both passes end `ok`; the `anchor_pi` drift anchor after 13 kernel-killing launches still records its 10 launches; `et-who` clean | all ok | **PASS** |
| **P5** no energy figure | none quoted. The counted cost stands: 758 instructions ≈ **4.5–8.3 nJ per hart**, 4.6–8.5 µJ per 1,024-hart launch | a count, not a measurement | **as registered** |
| **P6** substitute price | static, unchanged by this run: an fp32 divide is 299 instructions of `libgcc.__divsf3` ≈ 1.8–3.3 nJ ≈ **310–570 multiply-adds**; a square root is not callable from libm at all | — | **as registered** |

**P3 is the one miss, and it is informative.** 0.45 ms of wall clock buys: M-mode's `trap_handler` +
`trap_routine` (78 instructions), S-mode's `trap_handler` + `exception_handler` (471), two trace-buffer evictions
to the L3 (143), `return_from_kernel` (66) — on 1,024 harts, plus one CM→MM message per shire and the host's
teardown of a failed launch. The registration put the floor at 0.5 ms on the assumption that the evictions'
memory traffic would dominate; measured, the whole thing fits in under half a millisecond. The counted energy
(P5) is unaffected: it is an instruction count, not a time.

**P4 matters more than it reads.** Thirteen launches per pass each killed the kernel on 1,024 harts, twice over,
and the card neither needed nor received anything: no reset, no driver reload, no PCIe retrain, no `kill -9`. The
control launched immediately after each trap in the shuffled order returned its full 65,536 ops every time. The
device recovers a killed kernel by itself, which is what makes this probe cheap and safe to repeat.

## Why this ran at all: the card-minute gate

The task's gate was "≤ ~15 card-minutes, and it must add a hardware check of the source finding". The harness's
own `runitems.py --list` priced one probe pass at **21.3 min** (it charges 50 s of approach per run), which would
have failed the gate — and the registration's own estimate, 42 card-minutes for two passes, came from that
number. The two queues that ran first on this card the same morning measured the real cost: E74 **695 s / 78 runs
= 8.9 s per run**, E75 **275 s / 32 runs = 8.6 s**. At 8.5 s a probe pass of 26 runs is **3.7 min**, so two
passes are **7.4 card-minutes** — and the probe took **7.7**. The gate was decided on the measured rate, with
the arithmetic recorded before the launch.

## The firmware path (strand S), unchanged by this run

There is no emulation path, so no per-instruction energy exists. M-mode's `trap_routine.c` emulates exactly one
illegal instruction (`csrrs` of `mhartid`) and delegates the rest; S-mode's `exception.c` `exception_handler`, for
a U-mode exception, saves the context, evicts the S-mode and U-mode trace buffers, sends one
`CM_TO_MM_MESSAGE_ID_KERNEL_EXCEPTION` per shire and calls `return_from_kernel(0, KERNEL_RETURN_EXCEPTION)`. It
never returns to `mepc + 4`. **The hardware now says the same thing**: 0 ops on every one of the thirteen, 65,536
on every control.

| where | symbol | instructions |
|---|---|---|
| MachineMinion (M-mode) | `trap_handler` + `trap_routine` | 22 + 56 |
| WorkerMinion (S-mode) | `trap_handler` + `exception_handler` | 6 + 465 |
| WorkerMinion | `Trace_Evict_CM_Buffer` + `Trace_Evict_UMode_Buffer` | 59 + 84 |
| WorkerMinion | `return_from_kernel` | 66 |
| **the path** | | **758** |

And the finding for anyone writing a kernel, also unchanged: `libgcc.a __divsf3` (299 instructions) contains no
trapping instruction, so a C `a / b` on floats is safe; `libm.a sqrtf` / `__ieee754_sqrtf` and `fmodf` /
`__ieee754_fmodf` contain `fdiv.s`, and `libgcc.a __fixunssfdi` contains `fcvt.l.s`, so **`sqrtf(x)` is fatal and
a float→unsigned-64 conversion is fatal**, while a divide costs about 310–570 multiply-adds.

## What ran, and what was registered

| | registered | happened |
|---|---|---|
| stages | `build`, `static`, `setup` (no card); `probe` 2 passes; `price` on whatever the probe cleared | `build` ran 27 Oct on this box; `setup` + dry run 28 Oct; **`probe 7610 2`** |
| the L strand (`trl_`) | "launched only for a mode the probe cleared, named explicitly" | **not run: the probe cleared nothing.** All thirteen trap, so there is no mode to price. The registered rule retires the strand rather than the strand failing |
| the `price` stage | an energy for a non-trapping member of the thirteen | **not run**, same reason. The seven controls are not members of the thirteen and already have catalogue prices |
| passes | 2, a third only if an item is unstable | 2; nothing unstable, so no third |
| energy of a trap | none to be quoted | none quoted |

## Departures, dated

- **D-T1 (28 Oct 2026) — the reducer was written on the day.** The registration named the four decision rules and
  left the reducer to the running agent; `tools/claims-v3/tr/reduce_tr.py` implements them and reads
  `runs.jsonl` / `marks.jsonl` only — no power at all, as predictions.json itself requires ("the board meter is
  3–4 orders of magnitude short").
- **D-T2 (28 Oct 2026) — the probe ran against a measured card-minute cost, not the harness's.** See the gate
  section: `--list`'s 21.3 min per pass is a ceiling that charges 50 s of approach per run; the measured cost on
  this card is 8.5 s.
- **D-T3 (28 Oct 2026) — "64 ops" in P1 is per hart.** The device record is chip-wide: a control reports 65,536 =
  64 × 1,024. Read as registered, with the factor named.
- **The `static` stage was not re-run on this box.** The counts above are the registration's, taken on aifoundry1
  from `/opt/et`'s own ELFs on 27 Oct; both boxes run `et_soc1 0.20.0`, `srcversion 47D26A305A0428B29FB7FC4`.
  Re-running `objdump` on the card host during a measurement would have split the passes (the campaign's rule
  after E67), and the probe's own result does not depend on the count.

## What it changes

1. **Q128 §5 item 5's second half closes** — structurally, not with thirteen energies. The question "what do the
   thirteen trapping instructions cost?" is now answered: *they are never executed, so they have no
   per-instruction energy*; the trap that replaces one costs 758 instructions on the handling hart
   (≈ 4.5–8.3 nJ counted) and **ends that hart's kernel**; and the operations cost what their software
   substitutes cost — 310–570 multiply-adds for a divide, and nothing for a square root because `sqrtf` cannot be
   called at all. It does **not** move the 3.837 pJ unaccounted on the multiply-add; it removes an open item and
   replaces it with numbers a kernel writer can use.
2. **`docs/findings/14-card-behaviour.md`'s traps list gets its replication**: thirteen for thirteen, on a named
   card, with a build hash, two passes and a log — and the generalisation from the type to the library ("a
   `double` anywhere in a kernel traps" becomes "libm's `sqrtf` traps and libgcc's `__divsf3` does not").
3. **The energy manual's §3.1 note** that the thirteen "have no energy" is now a measured statement rather than a
   recollection, and the card's recovery behaviour is on the record: a killed kernel needs no intervention.

## Files

| file | what it is |
|---|---|
| `passes/p7610`, `passes/p7611` | the two probe passes: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `configs.json`, `block.json`, `gen.sha256`, `text.sha256`, `manifest.txt`, `run.log` |
| `gen/manifest.json` | the item list (13 trapping modes, 7 controls, 2 catalogue modes, the drift anchor) |
| `tr.json` | the reduction: per-item verdicts, P1–P4 scored, the registration's counts carried through |
| `runs.csv` | one row per run: item, designed-to-trap, ok, ops, wall_s, host rc |
| `reduce.sh`, `queue.log` | the reduction command and the queue's own log |

Code: `tools/claims-v3/tr/` (`make_tr.py`, `static_cost.py`, `block.sh`, `queue_tr.sh`, `run_e76.sh`,
`predictions.json`, `reduce_tr.py`), stimulus `workloads/enercat/gen_tr.py` and `enercat_tr_modes.json`,
runner `tools/claims-v3/runitems.py`.

## Reproducing it

    bash tools/claims-v3/tr/run_e76.sh build        # build/enercat-tr, -DENERCAT_TR=ON. No card.
    bash tools/claims-v3/tr/run_e76.sh static       # the firmware and library counts. No card.
    bash tools/claims-v3/tr/run_e76.sh setup        # item list, mode list, hashes, dry run. No card.
    bash tools/claims-v3/tr/run_e76.sh probe 7610 2 # the two probe passes; log build/e76-tr-probe.log
    bash docs/reports/data/2026-10-28-e76-trapped-instructions/reduce.sh
