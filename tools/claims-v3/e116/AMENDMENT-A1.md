# E116 amendment A1: one more measured pass after the queue, inside the registered 40 card-minutes

*Written Sun 1 Nov 2026, ~17:02 PST, during pass 11611, before any power data were read. Committed and pushed before the
pass it adds can start. The registration (`README.md`, `predictions-e116.json`, commit `8bac6da5`) is not edited.*

**What I had seen when I wrote it:** the session log (the opening config read, the read-back's last line, "smoke rc=0",
the smoke gate's line "PASS items 6 bad [] MHz [599, 600]", the queue's start), the queue log (p11610 rc=0 after 6 min,
p11611 started 16:59:19), p11610's `block.json` (status ok, die 51 → 58 °C) and its count of runs (36). No power value,
no telemetry, no reduction.

**Why.** The registration gave the queue `E88_BUDGET_MIN = min(34, 38 − minutes since the session started)` and expected
"about five passes", from E88's 6-minute passes on card 1. On aifoundry3 the first pass took 409 s (16:52:21–16:59:09),
so the queue's rule (start a pass only if the elapsed time plus the longest pass fits the budget) stops after four
passes, about 37 s short of a fifth. Four kept passes is the registered minimum, so one pass set aside by E78's gates
(E88 lost one of six, E104 one of three, E82 two of seven) would leave S, W, H, P and T unscored.

**The change.** After the session's own closing config read, `extra_e116.sh` runs **one** more measured pass with
`block_e88.sh` unchanged (the next pass number after the queue's last, 11614 if the queue ran 11610–11613), then a
closing `ettelem config` (read only, under the lock, `timeout 10`, to `build/e116/config-a1-end.json`) and et-who. It runs
only if all of these hold, checked just before it starts:
- fewer than five passes ended with status ok (if the queue fitted a fifth, it does nothing);
- the projected end, now + the longest pass so far + 30 s, is at most the session's start + 39 minutes, so the whole
  session stays inside the registered **40 card-minutes**; and before 18:55 PST;
- no `build/claims-v3/STOP` or `build/rpath-STOP` file exists.

The pass, if it runs, is reduced and scored like the others: `collect_e116.sh` already reduces every `p116[1-9][0-9]` pass
whose `block.json` says ok, and no pass is chosen after the fact. Nothing else changes: the rules, the bands, the
expectations, the arms, the minimum of four passes and the reduction stay as registered. No knob is written, no
`--reset-ms`, no PMIC command.
