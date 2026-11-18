# v31-trace's traced sys_emu runs (Q217)

These runs check the masked walk (`../walk/walk_v31.py`) against the simulator. They used sys_emu only, on aifoundry3, under THE
SIMULATOR's rule:

- only while no lane booked aifoundry3 and `queue_state.py aifoundry3 e213a` read QUEUE OVER, both read again just before each run;
- one run at a time, at nice 19, the host inside bubblewrap with no `/dev/et*` node and an empty `/run/lock`;
- `prlimit --as` 4 GB on the host and on the summarizer;
- a plain `timeout` (TERM only, never `-k`);
- no card device node opened.

## What sys_emu can show, and what it cannot

I read this from its sources (`/opt/et-platform/sw-sysemu` on aifoundry2: `sys_emu/sys_emu_parse_args.cpp`, `insns/tensors.cpp`,
`insn_util.h`, `mmu.cpp`, `emu_gio.h`, `sys_emu/testLog.cpp`, `sys_emu/checkers/mem_checker.*`) and checked it against the runs.

**It can show these, through its own logging options (`-l` for DEBUG and `-ls <shire>,<hart mask>` to pick harts; the log goes to
`sysemu.log` in the host's run folder, here a FIFO):**

- which harts run user-mode code and tensor operations, and the privilege mode of every instruction;
- every tensor operation a logged hart issues, in program order, from the TensorLoad, TensorStore and TensorFMA Start lines:
  - TensorLoad: address, rows, stride, scratchpad start line, TenB, coop flag, load id, mask, cmd, boffset;
  - the `tensor_coop` group value at a cooperative load, and the leader neighbourhood the simulator picks;
  - TensorStore: address, stride, rows, cols, regstart, srcinc, coop;
  - TensorFMA: every field;
- the 64-B lines each load actually read (one MEM512 line per row) and each store wrote (MEM128 lines), at physical addresses;
- the simulator's step (its emulated cycle) on every line. A step is one instruction per hart, not time (mm-timing).

**It cannot show these:**

- **which level serves a line (L1, L2, L3 or DRAM).** sys_emu has no cache hierarchy with capacity, latency or eviction. Its
  `-mem_check` directory tracks only coherence state (which shires and minions have touched a line), with no capacity limit except
  the L1's sets.
- any time or contention: no bandwidth, no queues, no mesh, no DRAM, no L3 home slice for a line.
- the card's order across shires, which latency drives. The simulator runs all harts in near lock step, so its interleaving is its
  own.
- the hardware's one read per cooperative group. sys_emu makes each member hart read the tile into its own scratchpad once the whole
  group has started. The walk's one-read-per-group (8 minions share A, 4 share B) is the hardware's rule, taken from the code's
  `tensor_coop` values, which the trace does show.

So the trace checks every input the walk's level model takes: who reads which tile, in which order, with which cooperation group, and
which shires share it. It cannot check the levels the model assigns.

## Files

| file | what |
|---|---|
| `plan.json`, `make_plan.py` | the runs and each run's `-ls` selections. Per active shire: hart 0 of minions 0, 9, 18, 27, 4, 13, 22 and 31 (every neighbourhood and every position, so every tile the shire reads) and hart 1 of all 32 minions; plus harts 0 and 1 of one shire outside the mask. The `-all` runs log all 64 harts of every active shire |
| `trace_run.py` | the runner (refusals, sandbox, FIFO, a reader thread) and the streaming summarizer; `summarize` mode reads a log file (desk tests) |
| `r_prep.sh`, `r_update.sh`, `r_trace.sh` | run on aifoundry3: prepare the folder (kit-e211's builds copied and checked against E211's `.text` pins), install a newer payload, run one trace |
| `a3_send.sh`, `a3_fetch.sh`, `wait_a3.sh`, `prep_payload.sh` | desk side: the booking, claim and queue checks before every ssh, copy back, the bounded wait, the payload |
| `check_v31.py` | THE CHECK: one run's summary against the walk, hart by hart and event by event |
| `make_fake_log.py` | synthetic logs in sys_emu's line formats, used for the desk tests (`../scripts/s02_trace_desk_tests.sh`: 9 of 9) |
| `runs/<name>/` | per run: `summary.json.gz` (per-hart event lists and line checks), `out.json` (the host's SPARSITY lines), `RUN.txt`, `sandbox-check.txt`, `err.log`, `check.json` |
