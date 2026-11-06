# Kit v4's one-kernel-per-burst option: a burst as one kernel, with no gap inside it (Q145(b), MAP step 1)

*Fri 6 Nov 2026 (week 45), about 03:00 PST, on the Intel, desk only. New files only: no v3 driver (E171-E175's kits, the k6 and kg
runbooks, `run_hpl.py`) is edited. The desk test's T4 checks every file in the three governed kits' harness lists against its listed
hash. This is the option that section 46 item 5 of the round's brief made kit v4's default: "Kit v4 runs each burst as one kernel by
default (E100's N arm: no gaps, so no idle-reset falls)." The counted dip term (`tools/claims-v3/dipterm/`) is scored on sessions
that keep the gaps.*

## Builds on

1. **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 02:10 PST. Public rows read: P01, P02, H08, H24, H26, H28, L22.
   The ids are opaque pointers into a private inventory.
2. **Used:**
   - **E100's N arm** ([`2026-11-01-e100-idle-reset/`](../../../docs/reports/data/2026-11-01-e100-idle-reset/README.md),
     `f9fe3f57`; its registration [`../e100/README.md`](../e100/README.md), `5e12c4bd`). Its form
     `--seconds 0 --iters 10000000 --budget 7.5` ran one kernel of 4.2 s at 800 MHz on aifoundry2: 0 falls in 126 heartbeats inside
     its 50 kernels.
     - **The check against an earlier measurement of the same thing:** its committed launch records hold one SPARSITY line in each
       of its 50 work processes: launch −1, iters 10,000,000, wall 3.98-4.28 s, the whole kernel at 0.742-0.800 GHz. The dry pass
       below writes that same shape.
   - **The host's one-launch path** (`workloads/sparsity/host/main.cpp` at `27dce7f0`). `repeatFor` (lines 560-580) runs only the
     first launch when `--seconds` is 0 or less. Each launch waits at most 6 s on silicon, then aborts the stream (lines 237-246).
   - **The C-logging host keeps that loop.** `tools/claims-v3/ccheck/patch_host_ccheck.py` (`abe6b0f2`) patches the launch's body and
     leaves `repeatFor` as it is (its replacement pairs at lines 118-130). `--iters` passes through `sparsity_ccheck.sh` unchanged.
   - **`run_hpl.py`** (sha256 `68493295…`, `1a899d8f`) as every v3 kit imports it: `spawn_kernel`, the watcher's stop (it touches the
     stop file, and the host checks that file between launches), and the `--dry` toy card. The q142s watcher fix
     (`../hpl/watcher_q142s.py`) is installed as each v3 kit installs it.
   - **The registered reduction** (`../kspeed/reduce_kspeed.py` `burst_extra`, `BURST_FROM_S` 1.5 s; `../hpl/reduce_hpl.py`
     `run_metrics`). This tells what changes when no launch starts 1.5 s in.
   - **The dip term's climb** (`../dipterm/dipterm.py` `CLIMB_S`, aifoundry2's c7 0.12 s and c8 0.31 s). It gives the kernel's wall
     time at the cap after the first heartbeat inside it.
3. **Not used:**
   - **The toy card's clock** as a measurement. `run_hpl.py --dry`'s toy climbs to 800 MHz at once and writes fp32-shaped launch
     records, so the dry pass shows the records' shape, not a clock or a rate.
   - **A host with a longer launch timeout.** That is a host change, outside this option.
   - **Two kernels per burst.** One gap opens about 0.3% of bursts to a fall, so it is not the default asked for.
4. **Tiers:** public only. Every piece is the lab's committed data or public code at a pinned commit.
5. **Readiness:** this is an option, not a kit. Section 5 lists what a kit that uses it still needs before a card.

## 1. What the option does

[`onekernel.py`](onekernel.py) is all of it:
- **`iters_for(type)`** sizes one kernel to end in 5.5 s at 600 MHz, 0.5 s under the host's 6 s launch timeout, even if the clock
  never leaves the boot point:
  - fp32 and fp16: **6,043,956 iterations** (3.30 G cycles at 546 a op);
  - int8: **10,377,358** (318 a op).

  At the cap, after the climb from the first heartbeat inside the kernel, the kernel lasts **4.30-4.43 s** (desk test T1).
- **`command(cmd, type)`** turns a v3 burst command into one kernel: `--seconds 6` becomes `--seconds 0 --iters N`. Every other flag
  stays: `--budget`, `--stop-file`, `--kernel`, `--values`. It refuses a command that already names `--iters`, lacks
  `--stop-file`, or was sized for another type.
- **`install(H)`** patches the imported `run_hpl` module in memory, after checking that it is the committed file.
  - A work launch (spawn_kernel with no override) runs as one kernel. A heater or gate launch goes to the original method
    unchanged.
  - Under `--dry` it simulates the one kernel on the toy card and writes one SPARSITY line.
  - [`run_hpl_onekernel.py`](run_hpl_onekernel.py) is `run_hpl.py`'s own `main()` with the watcher fix and this install, and it
    records both in `<RUNDIR>/onekernel.json`.
- **`burst_extra_v4(m, procs, B)`** is the registered `burst_extra`, unchanged, with the one-kernel fields beside it (section 3).

## 2. What it changes in the launch records (the dry pass, [`drypass-onekernel.txt`](drypass-onekernel.txt))

The same three bursts (fp32 zeros, int8 zeros, fp16 randn; one 6 s process each) ran under `run_hpl.py --dry`, first in the v3 form,
then with the option:

| | v3 form | one kernel per burst |
|---|---|---|
| SPARSITY lines per work process | 13 on the toy (17-18 on a card: E173-E175's records) | **1** (launch −1, iters N) |
| gaps inside the process / inside the burst window | 12 / 10 | **0 / 0** |
| the process | 6.59-6.61 s | 4.15-4.79 s (4.30-4.43 s at the cap on a card, T1) |
| the window's sampler readings | 47-48 | 25-32 |
| the dip term's eligible gaps (DT-N's exposure) | 29 | **0** (band [0, 0]) |

- **The C log** holds one C record per burst instead of 17-18. The desk check of C simulates N iterations for that one launch: 7-11
  times as many as a v3 launch's, the same in all.
- **The DMA rule** (E160's, in E173.md: the session runs only if 6.57 s + 17 δ ≤ 7.2 s) counts one δ, not 17.
- **The stop file** is read only between launches (main.cpp `repeatFor`), so a one-kernel burst cannot be ended early (section 5).

## 3. What it changes in the reduction

- **`burst_mhz` and `burst_w` keep their form:** the sampler's means from 1.5 s after the process start to its end. The window is
  about 2.95 s at the cap instead of about 4.95 s.
- **`burst_rate` and `burst_ghz_kernel` read None.** They count only launches that start 1.5 s in (`reduce_kspeed.burst_extra`).
  The one kernel starts about 0.15 s after the process (E173-E175's records), so none qualifies (dry pass T7). `burst_extra_v4` adds
  beside them:
  - `v4_burst_rate_from_clock`: minions × ops a op / cycles a op × `burst_mhz`;
  - `v4_whole_kernel_ghz`: the kernel's own cycles over its wall, the climb included;
  - `v4_launches_in_window` and `v4_gaps_in_window`.

  (On the toy, int8's v3 `burst_rate` reads 49.2 against 84.4 from the clock. The toy writes 546 cycles a op for every type; on a
  card the two agree.)
- **Predictions made for a 6 s burst are for a different burst.** That covers the governed clock's dither over 1.5-6.5 s, the burst
  die rise and the frozen M10 and M9 burst predictions. A kit that uses the option recomputes them for the one-kernel length (the
  predictor's `t_end`) before its freeze. The 4.5 s heat laws apply as they are.
- **The accumulator grows 7-11 times further in one kernel than in one v3 launch.** If the result path's switching depends on C's
  magnitude, a kind's power can shift a little. An A/B check is owed before kinds are scored on one-kernel bursts: one kernel
  against v3 launches, on the zeros and random anchors, in one session.

## 4. What it does to the dips

There is no gap inside a burst. So no heartbeat lands between two kernels, and no climb is late: the first heartbeat after the launch
lies inside the kernel unless it falls in its first 0.7 ms. On a one-kernel session the dip term's DT-N reads exposure 0 and band
[0, 0]. Any fall inside a kernel refutes the chain (DT-K, E100's D2 form). The term and its blind test are for sessions that keep the
gaps (`../dipterm/REGISTRATION.md` section 6).

## 5. Before a card uses it

- **A safety stop now waits for the kernel's end.**
  - The watcher touches the stop file, and the host reads it only between launches. `run_hpl` never signals a device process.
  - So a stop's response time grows from one v3 launch (about 0.5 s) to one kernel (up to 5.5 s).
  - A kit using the option must register an admission margin that covers a whole kernel under each stop: aifoundry2's 85 W on
    three samples, card 0's 65.9 W one-sample stop, and far from its 75 W PMIC alarm.
  - It must also re-run its stop-path tests with one-kernel bursts. STOPTEST-BOARD's "the launch ending within 3 s of the trip"
    cannot hold for a 4.3 s kernel, so its line becomes the kernel's own length plus 1 s.
- **Device commands.** The option adds no device command. A one-kernel burst runs the same host binary with `--seconds 0 --iters N`,
  the same commands as a v3 burst's first launch. dmcmd_audit GO is still required on the kit's new file set.
- **The rest:** its own registration, the recomputed predictions (section 3), the A/B check, a dry pass on the box, a readiness critic,
  fresh Tailscale approvals and his go. Nothing in this directory touches a card.

## Files

| file | what |
|---|---|
| [`onekernel.py`](onekernel.py) | the sizing, the command, the install into `run_hpl`, `burst_extra_v4` |
| [`run_hpl_onekernel.py`](run_hpl_onekernel.py) | `run_hpl.py`'s own main with the watcher fix and the option installed |
| [`protocol-onekernel-dry.json`](protocol-onekernel-dry.json) | the dry pass's three bursts (built-in kinds, no tile file) |
| [`selftest_onekernel.py`](selftest_onekernel.py) | the desk test: T1-T5 (sizing, command, refusal, v3 untouched, the dip term); `--dry` T6-T8 |
| [`selftest-onekernel.txt`](selftest-onekernel.txt) | its unit output |
| [`drypass_onekernel.sh`](drypass_onekernel.sh) | the dry pass: v3 form and one-kernel form on the toy card, then T6-T8 |
| [`drypass-onekernel.txt`](drypass-onekernel.txt) | its output (scratch paths as `<scratch>`) |
| [`SHA256SUMS`](SHA256SUMS) | the hash list of the files above |

SPDX-License-Identifier: Apache-2.0
