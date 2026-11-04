# Dated note on E166's kit README `README.md` (Wed 4 Nov 2026, week 45, before any E166 data)

Written beside the README and not inside it, desk only, before any E166 data, claim or launch. [`README.md`](README.md) stays as committed
in `c75bc460`. This note adds one box step and the parent self-test, after [`E166.md.dated-note-2.md`](E166.md.dated-note-2.md).

## A box step for a later try (E166.md's "A later try", after G0 stopped a session)

**Before a later session on aifoundry3**, in `~/aifoundry`, move the earlier session's smoke aside (a file move, no device):

```bash
mv build/claims-v3/aifoundry3/e166-smoke/p16601 build/claims-v3/aifoundry3/e166-smoke/p16601.try1
```

Without it, `lib.sh`'s `block_begin` finds the earlier smoke's `block.json` "ok" and exits "already done", and `session_e166.sh` reads the
old smoke gate as GO. The five stop tests would then not run again that session. The gated measured pass (block status "gate") needs
nothing: `block_e166.sh` moves a non-ok pass directory aside by itself. Collect every attempt's directory. The scorer scores the first
measured pass whose R0 passes G0 (E166.md § G0), and each attempt's `start_gate` mark is reported.

## The parent self-test (before any E166 data)

`/usr/bin/python3 tools/claims-v3/e166/selftest_parent_e166.py` (about 15 s; [`logs/selftest-parent-e154.txt`](logs/selftest-parent-e154.txt),
`.json`) runs two things:
- **E154's registered scorer, unchanged,** on E154's committed pass 15420. It gives back `scored.json` byte for byte, with its eleven
  registered verdicts, all PASS.
- **`score_e166.py --self-test`, unchanged.** It passes and equals `logs/selftest-e166-kit.json` byte for byte.

Run it on the Intel before the claim, beside `score_e166.py --self-test`. [`frozen-e166-fix.sha256`](frozen-e166-fix.sha256) pins this fix
pass's files. Nothing in `frozen-e166.sha256`, the 30 files the box checks, changes.

## Smaller points

- The § Stops figure: the hottest frozen in-launch peak under G0 is **67.33 °C** (K_S at a 51.5 °C room), not 67.24 °C. The conclusion
  stands (the dated note 2).
- SL's stated 5.0% false-positive rate is the registered seven-hold pool's. It reads 8.1% on E154's five holds and 10.3% on the four whose
  slope window matches SL's 300 s (the dated note 2). The thresholds stay.
