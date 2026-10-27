# V3-TR: the thirteen instructions that trap, and what they cost instead (E76, Q129)

*Pre-registered Tue 27 Oct 2026 (week 44), 14:2x–15:3x PDT, on aifoundry1 (build, source reading and dry run
only — no card was opened anywhere for this file). Frozen at the commit that adds it, before the first measured
pass on aifoundry3. Changes after that go in Amendments, dated, before the data they touch.*

## The question, and the answer the firmware already gives

Q128 §5 item 5, second half: **thirteen instructions trap in U-mode and have no energy figure.** The energy
manual lists them — `fdiv.s`, `fsqrt.s`, `fdiv.ps`, `fsqrt.ps`, `frsq.ps`, `fsin.ps`, `fdiv.pi`, `fdivu.pi`,
`frem.pi`, `fremu.pi`, `fcvt.l.s`, `fcvt.s.l`, `csrr cycle` — and records that they "trapped in U-mode in a
one-off check while the catalogue was written (the card and the log of that check were not kept)".

**Read before designing anything: there is no emulation path, so there is no per-instruction energy to measure.**
In the minion runtime (`device-minion-runtime`, Apache-2.0, installed on the lab boxes), M-mode's
`src/MachineMinion/src/trap_routine.c` handles exactly one illegal instruction — `csrrs` of `mhartid` — and
delegates every other one to S-mode. S-mode's `src/WorkerMinion/src/exception.c` `exception_handler` then, for a
U-mode exception: logs it, saves the execution context into the kernel's exception buffer, evicts the S-mode and
U-mode trace buffers to the L3, sends one `CM_TO_MM_MESSAGE_ID_KERNEL_EXCEPTION` per shire to the kernel worker,
and calls `return_from_kernel(0, KERNEL_RETURN_EXCEPTION)`. It never returns to `mepc + 4`. **One trapping
instruction ends that hart's kernel.** So the quantity "pJ per `fdiv.s` retired" does not exist on this
silicon, and an experiment that reports one would be reporting an artefact.

What does exist, and what this experiment delivers:

| strand | card? | what it gives |
|---|---|---|
| **S** — the firmware path | no | the above, with file and function names: the structural answer to §5 item 5 |
| **P** — the probe | yes, ~10 card-minutes | which of the thirteen trap, **with a log**, each beside a control of the same shape in the same build: the replication the manual asks for |
| **L** — the price | yes, ~5 card-minutes | an ordinary catalogue energy for any of the thirteen that turns out **not** to trap |
| **X** — the substitute | no | what the operations cost in practice: the instruction counts of the routines a C kernel really calls, priced from the catalogue |

## What the probe measures, and why its launches fail on purpose

`gen_tr.py` compiles all thirteen into the kernel behind `-DENERCAT_TR=ON` (modes 500+, so gen_ops.py's and
gen_df.py's numbering is untouched), each as eight ops of the catalogue's rotating-source shape, and seven
controls of the same shapes that are known to run (`fmul.s`, `fsgnj.s`, `fmul.ps`, `frcp.ps`, `fmv.x.w`,
`fmv.w.x`, `csrr 0xcc0`). Every probe item runs `--window 0 --seconds 0.001`: one launch, one block of 64 ops.

- a control does its 64 ops and returns: the host prints `"ok":true` with `ops` and `cycles`;
- a trapping mode dies on op 1: the host prints `"ok":false`, no ops, and exits 1.

**A failed launch is the measurement.** Nothing is reset, no driver is reloaded, nothing is retried beyond
runitems.py's own single retry. `trx_fdiv_ps` and `trx_fsqrt_ps` run the same two instructions through the
catalogue's own hand-written modes (`fdiv_ps`, `fsqrt_ps`, which already exist in every build), so the result is
attributed to the instruction and not to this kernel.

The probe also gives the **time** cost exactly: `wall_s` for a trapping launch against a control launch, which
is the one part of the cost a host clock resolves.

**The energy of one trap is below the board meter, and this registration says so in advance.** One trap per hart
per launch, one launch per process, a process is about a second: the counted cost (below) is tens of microjoules
over the chip, three to four orders of magnitude under what a 10 Hz board meter resolves in a one-second window.
No energy number will be quoted for the trap itself. The counted estimate is the answer, and it is labelled as a
count.

## Counted on aifoundry1, 27 Oct 2026, from /opt/et's own ELFs (`static_cost.py`)

Instructions on the path a U-mode illegal instruction takes (objdump of the installed firmware; local labels
folded into their function):

| where | symbol | instructions |
|---|---|---|
| MachineMinion (M-mode) | `trap_handler` + `trap_routine` | 22 + 56 |
| WorkerMinion (S-mode) | `trap_handler` + `exception_handler` | 6 + 465 |
| WorkerMinion | `Trace_Evict_CM_Buffer` + `Trace_Evict_UMode_Buffer` | 59 + 84 |
| WorkerMinion | `return_from_kernel` | 66 |
| **the path** | | **758** |

At the catalogue's 6–11 pJ per scalar instruction that is **4.5–8.3 nJ per trap per hart**, or **4.6–8.5 µJ for a
launch in which all 1,024 harts trap** — plus the trace evictions' memory traffic and one CM→MM message per
shire, which the count does not price. (MasterMinion's own `exception_handler`, 217 instructions, runs on the
management side; `syscall_handler` is the `ecall` path, not this one, and is listed in `static.json` for
contrast.)

**And the finding that matters most for anyone writing a kernel**: the toolchain's own libraries contain these
instructions.

| library routine | instructions | contains |
|---|---|---|
| `libgcc.a __divsf3` | 299 | **no trapping instruction**: a C `a / b` on floats is a software divide and is safe |
| `libgcc.a __divdf3` | 335 | no trapping instruction |
| `libgcc.a __fixunssfdi` | 12 | **`fcvt.l.s`** — a float to unsigned 64-bit conversion dies |
| `libm.a sqrtf` / `__ieee754_sqrtf` | 25 / 81 | **`fdiv.s`** — `sqrtf()` dies |
| `libm.a fmodf` / `__ieee754_fmodf` | 29 / 146 | **`fdiv.s`** — `fmodf()` dies |
| `libm.a sinf` / `__kernel_sinf` | 43 / 43 | no trapping instruction in these two symbols (the argument reduction `__ieee754_rem_pio2f`, 208, is clean too) |

So the shipped libm was built for a target whose `fdiv.s` works, and libgcc's soft-float divide was not: in a
U-mode kernel on this silicon **`a / b` is fine and costs about 299 instructions, while `sqrtf(x)` is fatal**.
This generalises 14-card-behaviour.md's "a `double` anywhere in a kernel traps" from the type to the library.

## Frozen predictions

| # | prediction |
|---|---|
| P1 | **All thirteen trap**: every `trp_` item of a trapping mode records `"ok":false` with zero ops, and every `trp_tr_ctl_*` control records `"ok":true` with 64 ops — 13 of 13 and 7 of 7 |
| P2 | `trx_fdiv_ps` and `trx_fsqrt_ps` behave exactly as `trp_tr_fdiv_ps` and `trp_tr_fsqrt_ps`: the result belongs to the instruction, not the kernel |
| P3 | **The trap costs time**: a trapping launch's `wall_s` exceeds its shape control's by **0.5–50 ms** (the handler path plus two trace evictions plus the CM→MM message, on 1,024 harts at 600 MHz) |
| P4 | **No lasting harm**: after every trapping launch the control items that follow in the same block still record `"ok":true`, `et-who` is clean, and the pass ends `ok`. A card that stops answering is a FAIL of this prediction and is reported as one |
| P5 | **No energy figure for a trap** will be quoted; the counted cost is **4.5–8.3 nJ per hart** (758 instructions at 6–11 pJ) |
| P6 | **The substitute prices**: an fp32 divide in a U-mode kernel costs 299 instructions ≈ **1.8–3.3 nJ**, i.e. **310–570 multiply-adds** at Q128's 5.783 pJ; a square root cannot be called from libm at all |

## Decision rules (registered)

1. **P1 is a count, not a mean**: each item's verdict is the modal `ok` over the passes, and any item whose
   verdict is not unanimous across passes is reported as unstable with its per-pass values.
2. **P3** is the median difference of `wall_s` over the passes, with the full range; the host clock, not the
   board meter, is the instrument, and the process-startup component is removed by differencing against the
   control launched in the same block under the same protocol.
3. **P4 is a stop rule, not only a prediction**: if a trapping launch is followed by a control that does not
   record `"ok":true`, the queue stops (`build/tr-STOP`), the claim stays open, and
   flush-util `notify.py --unblock` is used. **No card is reset, no driver is reloaded, no PCIe is
   retrained** — ever, in this experiment.
4. **The L strand runs only on what P1 clears**: a `trl_` item is launched only for a mode the probe found does
   not trap, named explicitly on the command line.
5. **Passes**: 2 probe passes (the verdict is a boolean; a third is run only if any item is unstable).
6. **What it changes.** §5 item 5's second half closes with a structural answer rather than thirteen energies:
   these instructions are not executed, so they have no energy; the trap that replaces them costs 758
   instructions on the handling hart and ends the kernel; and the operations themselves cost what their software
   substitutes cost, which is 310–570 MACs for a divide and "not available from libm" for a square root. None of
   this moves the 3.837 pJ unaccounted on the multiply-add; it removes an open item from the list and replaces
   it with numbers a kernel writer can use.

## How to run it

    # no card, anywhere:
    bash tools/claims-v3/tr/run_e76.sh build          # build/enercat-tr (-DENERCAT_TR=ON)
    bash tools/claims-v3/tr/run_e76.sh static         # the counts above, into build/tr-static/
    bash tools/claims-v3/tr/run_e76.sh setup          # modes, mnemonics in the kernel, .text hashes, dry run
    # on aifoundry1 the dry run needs a card named (lib.sh: two cards); V3_DRY=1 still opens nothing:
    V3_DEVICE=0 bash tools/claims-v3/tr/run_e76.sh setup

    # on aifoundry3, after E70 and E71:
    ssh aifoundry3
    cd ~/aifoundry
    bash tools/claims-v3/tr/run_e76.sh build          # the TR build must exist on THIS box
    bash tools/claims-v3/tr/run_e76.sh setup
    bash tools/claims-v3/tr/run_e76.sh probe 7610 2   # two probe passes; log build/e76-tr-probe.log
    # then, for whatever did not trap, e.g.:
    bash tools/claims-v3/tr/run_e76.sh price 7620 2 anchor_pi,trl_tr_ctl_frcp_ps

Data in `build/claims-v3/aifoundry3/tr/p<pass>/`; collect into
`docs/reports/data/2026-10-27-e76-trapped-instructions/` together with `build/tr-static/static.json`.

## Risks

- **The build.** `-DENERCAT_TR=ON` must be built on the box that runs it. It built clean on aifoundry1 on
  27 Oct (every one of the thirteen mnemonics assembles; the kernel carries 64 of each, `csrr 0xc00` appearing
  as `rdcycle`), and `gen_tr.py --skip <name>` drops a mode whose mnemonic a different assembler rejects
  **without renumbering the others**.
- **Repeatedly killing kernels.** This is a firmware path that lab work has hit many times by accident
  (14-card-behaviour.md's trap list was collected that way), and the firmware's own design is to report and
  return. P4 and rule 3 are the guard; the probe is 20 launches, not 20,000.
- **A trapping launch might leave the management queue or the trace buffers in a state the next launch trips
  over.** The controls interleaved in the shuffled order are the detector, and `block.sh` drains the management
  queue the way every V3 block does.
- **`--window 0`** relies on `RUN`'s do-while running the block once. If a control records zero ops, the window
  is the suspect and the item is re-registered at `--window 1000` in an amendment.
- **No card is opened on aifoundry1**: `build`, `static` and `setup` touch no device.

## Files

| file | what it is |
|---|---|
| `../../../workloads/enercat/gen_tr.py` | the kernel cases and the host table for the thirteen plus seven controls (modes 500+, `-DENERCAT_TR=ON`) |
| `make_tr.py` | the probe and price item lists for `runitems.py` |
| `static_cost.py` | the trap path's and the library routines' instruction counts, and which library routines contain a trapping instruction |
| `block.sh` | one pass as a `lib.sh` block: card lock, sampler, `timeout 10`, stop on another user |
| `queue_tr.sh` | passes back to back, detached, stopping on `build/tr-STOP` |
| `run_e76.sh` | `build` / `static` / `setup` / `probe` / `price` |
| `predictions.json` | P1–P6 and the decision rules, frozen with this commit |

## Amendments

*(none yet)*
