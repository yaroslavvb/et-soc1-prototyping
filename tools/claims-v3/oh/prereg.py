#!/usr/bin/env python3
"""OH (E53): freeze the pre-registration. Writes prereg/PREREG.md (the design, the registered predictions and decision
rules, and a lock block with the sha256 of every file the blocks and the reducer use and of each card's binaries),
prereg/prereg.json (the items) and prereg/PREREG.sha256, and prints PREREG.md's sha256: record it outside the tree
(RESULTS, the data README, 03-experiments.md) and pass it to run_queue.sh as OH_PREREG_SHA256.

  python3 tools/claims-v3/oh/prereg.py --bins-a3 F --bins-c1 F [--replace-unused]

--bins-a3 / --bins-c1: the output of `bash tools/claims-v3/oh/block.sh --binhash` on each host (V3_DEVICE=1 on
aifoundry1). Refuses if a PREREG exists (unless --replace-unused, which records the hash it replaces) or if any
non-smoke OH block exists on either host (listed over ssh: ls only) or here.
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ohlib  # noqa: E402

ROOT = ohlib.ROOT
LOCKED = ["tools/claims-v3/oh/block.sh", "tools/claims-v3/oh/ohlib.sh", "tools/claims-v3/oh/ohlib.py",
          "tools/claims-v3/oh/reduce.py", "tools/claims-v3/oh/params-oh.json", "tools/claims-v3/oh/battery.txt",
          "tools/claims-v3/oh/run_queue.sh", "tools/claims-v3/oh/schedule-aifoundry3.txt",
          "tools/claims-v3/oh/schedule-aifoundry1-c1.txt", "tools/claims-v3/lib.sh", "tools/claims-v3/queue.sh",
          "workloads/memprobe/gen_ops.py"]
LIST_CMD = "ls -d ~/nekko/build/claims-v3/{aifoundry3,aifoundry1-c1}/oh/p[12]* 2>/dev/null; true"

ITEMS = {
    "OH1-a": "every 1 s analysis window (10 s after the condition starts to its end), every condition, both cards: hottest sensor minus mean <= +4 C. FAIL if any window >= +5.",
    "OH1-b": "per block, median dhot of ONE-C <= that of B4C. PASS in >= 2 of 3 blocks on aifoundry3 and 2 of 2 on card 1; otherwise FAIL.",
    "OH1-c": "per card, pooled over its blocks: |median dhot(condition) - median dhot(IDLE)| <= 1 C, for ONE-C, ONE-NE and B4C separately.",
    "OH2-a": "0 wrong results, 0 tensor-error CSRs and 0 not-ok among all checked launches in every band on both cards. With N checked launches in a band and 0 failures the page quotes the 95 % upper bound 3/N per launch.",
    "OH2-b": "for each kernel metric (fma cycles per op and gemv cycles per layer per sweep point; mmbench and relay cycles_max): |median over launches whose die mean read 80-85 C / median over the rest band B0 - 1| <= 0.1 % -> PASS; otherwise, if the hot median lies inside the rest band's [min, max] -> PASS (within noise); otherwise FAIL.",
    "OH2-c": "the heater's implied clock (cycles / host wall time of its 0.5 s launches), median per 5 C band of the die mean, lies in 0.5994-0.5995 GHz in every band.",
    "OH2-d": "1 s windows inside a heater (ALL32/ALL24) launch: max dhot <= +4 in every band (60-70, 70-80, 80-85); median(80-85) - median(60-70) is 0 or +1 C.",
    "OH2-e": "memprobe's refresh period (the jittered series, computed as V3's MEM-P5) at the hot band = 2,325.4 +- 0.1 minion cycles on both cards.",
    "OH3-a": "idle samples (>= 5 s after any launch, 600 MHz) of the OH blocks: the median board power per whole degree (>= 20 samples) between 60 and 84 C is within +-1.5 W of the card's E44 law (aifoundry3 15.45 + 21.89 e^((T-80)/30); card 1 18.45 + 30.50 e^((T-80)/30)).",
    "OH3-b": "refitting P_fix + A e^((T-80)/T_L) on E44's T_L grid to those bins gives a doubling interval T_L ln 2 of 17-25 C.",
}

TEXT = r"""# PREREG: OH (E53), the effect of overheating on the ET-SoC-1

Frozen %(when)s, before any OH-1 or OH-2 block on any card. %(replaces)s

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

- **OH1-a**: %(OH1-a)s
- **OH1-b**: %(OH1-b)s
- **OH1-c**: %(OH1-c)s
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

- **OH2-a**: %(OH2-a)s
- **OH2-b**: %(OH2-b)s
- **OH2-c**: %(OH2-c)s
- **OH2-d**: %(OH2-d)s
- **OH2-e**: %(OH2-e)s

## OH-3: the idle law, from the idle stretches of OH-1 and OH-2 (no extra card time)

- **OH3-a**: %(OH3-a)s
- **OH3-b**: %(OH3-b)s
Card 1's W_idle drift since 26 Sep is a known risk: a FAIL there is reported, not explained away.

## Not run, and the prediction registered now

- **Transistor speed against temperature from the process detectors.** The PD oscillator select is
  `MEASUREMENT_DISABLED`, the read functions have no caller and the blocks are reachable only by the service processor:
  it needs an SP BL2 build that selects an internal delay chain, keeps the 31-cycle gate, samples the 34 PDs with each
  temperature pass and exposes the counts (a DM command or a trace line), flashed by the lab admin. *Prediction*: if the
  PDs run on the minion rail (about 0.50-0.525 V), the count changes by less than +-2 %% between 55 and 85 C (at the
  crossover), and is more likely to rise (hot is faster) than to fall; on a rail >= 0.70 V the count falls, by less
  than 5 %% over that range. Which rail the PDs sit on is undocumented. This is an ask for the hub.
- A DLL delay-estimation sweep (M-mode code, neighbourhood resets), a clock or voltage shmoo (admin settings), the
  power-limit hypothesis for the ~120 C stop (board power near the 88 W input), and a DRAM retention hold at a hot die
  (device buffers do not outlive a 10 s process; the DRAM temperature is not measurable): not within the rules.

## Departures from the plan (fixed here, before any data)

1. OH-1's condition uses launches of <= 4 s (the plan said 2 s) so fewer 1 s windows straddle a gap between processes;
   the preheat bursts stay 2 s ALL24. The condition is 60 s of wall time, not a count of launches.
2. OH-2 holds each band with a heating target inside it (67, 74, 80, 83 C) instead of one heater launch after each
   checked launch, which could push the die out of the band; the watcher stops each heater launch at the target.
3. OH2-b has a second, noise-aware level (PASS within noise) for kernels whose launch-to-launch spread exceeds 0.1 %%
   (relay and mmbench cycle counts vary by up to 0.3 %% between identical launches in earlier data).
4. The card-1 W_idle proxy of E52 is not used as a stop: the die temperature changes by design here, and idle power
   follows it. The direct card-0 guard stays.
5. The relay kernels run 64 stages (the plan said 4), about 90 ms, so each checked launch moves 2 GB through the path.
6. The smoke (901) runs after this freeze and before any OH-1/OH-2 block. If a kernel reports "unchecked" there, it is
   replaced and this PREREG is re-frozen with --replace-unused (recorded), before any OH-1/OH-2 block.

## The lock

%(lock)s
"""


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def listing():
    out = {}
    for host in ("aifoundry3", "aifoundry1"):
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", host,
                            "ls -d ~/nekko/build/claims-v3/{aifoundry3,aifoundry1-c1}/oh/p* 2>/dev/null; true"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            sys.exit("prereg.py: cannot list %s: %s" % (host, r.stderr.strip()))
        out[host] = [os.path.basename(x) for x in r.stdout.split()]
    return out


def amend(a):
    """An amendment after OH blocks exist: the registered items (ITEMS) must be unchanged; the new PREREG.md carries the
    amendment text, the replaced PREREG.md's sha256, the blocks that exist, the original text (its lock block replaced
    by a note) and a new lock over the current files and binaries."""
    d = os.path.join(HERE, "prereg")
    md = os.path.join(d, "PREREG.md")
    old = open(md).read()
    old_sha = sha(md)
    rec = open(os.path.join(d, "PREREG.sha256")).read().split()[0]
    if rec != old_sha:
        sys.exit("prereg.py: PREREG.md does not match PREREG.sha256: refusing to amend")
    pj_old = json.load(open(os.path.join(d, "prereg.json")))
    if pj_old.get("items") != ITEMS:
        sys.exit("prereg.py: the registered items differ from the frozen ones: an amendment may not change a prediction")
    n = 1 + old.count("## Amendment ")
    keep = os.path.join(d, "PREREG-before-amendment-%d.md" % n)
    open(keep, "w").write(old)
    bins = {}
    for card, f in (("aifoundry3", a.bins_a3), ("aifoundry1-c1", a.bins_c1)):
        b = json.load(open(f))
        bins[card] = {k: v["sha256"] for k, v in b.items()}
    files = {f: sha(os.path.join(ROOT, f)) for f in LOCKED}
    pj = os.path.join(d, "prereg.json")
    json.dump({"items": ITEMS, "files": files, "binaries": bins, "params": ohlib.params(),
               "amendments": pj_old.get("amendments", []) + [{"n": n, "replaces": old_sha}]},
              open(pj, "w"), indent=1, sort_keys=True)
    lock = {"files": dict(files, **{"tools/claims-v3/oh/prereg/prereg.json": sha(pj)}), "binaries": bins}
    lock_md = "%s\n```json\n%s\n```\n%s\n" % (ohlib.LOCK_BEGIN, json.dumps(lock, indent=1, sort_keys=True), ohlib.LOCK_END)
    body = old.split(ohlib.LOCK_BEGIN)[0].rstrip() + "\n\n(The lock block of this version is replaced by the amendment's lock below; this version's full text, with its own lock, is `%s`, SHA-256 %s.)\n" % (os.path.basename(keep), old_sha)
    when = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    ls = listing() if not a.no_ssh else {}
    head = ("# PREREG (amended): OH (E53), the effect of overheating on the ET-SoC-1\n\n"
            "## Amendment %d, frozen %s\n\nIt replaces PREREG.md SHA-256 `%s`. The registered predictions and decision rules "
            "(prereg.json `items`) are unchanged (checked by prereg.py). OH block directories that existed on the hosts when it was "
            "frozen: %s.\n\n%s\n\n---\n\n" % (n, when, old_sha, json.dumps(ls), open(a.amend).read().strip()))
    txt = head + body + "\n## The lock (amendment %d)\n\n%s" % (n, lock_md)
    open(md, "w").write(txt)
    h = sha(md)
    open(os.path.join(d, "PREREG.sha256"), "w").write("%s  PREREG.md\n" % h)
    print(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bins-a3", required=True)
    ap.add_argument("--bins-c1", required=True)
    ap.add_argument("--replace-unused", action="store_true")
    ap.add_argument("--no-ssh", action="store_true", help="skip the hosts' listing (dry tests only)")
    ap.add_argument("--amend", help="a markdown file: an amendment after OH blocks exist (predictions unchanged)")
    a = ap.parse_args()
    if a.amend:
        return amend(a)
    d = os.path.join(HERE, "prereg")
    os.makedirs(d, exist_ok=True)
    md = os.path.join(d, "PREREG.md")
    replaces = ""
    if os.path.exists(md):
        if not a.replace_unused:
            sys.exit("prereg.py: a PREREG exists (%s); --replace-unused only if no OH-1/OH-2 block ran under it" % sha(md)[:12])
        replaces = "It replaces an unused freeze, PREREG.md sha256 %s (no OH-1 or OH-2 block ran under it)." % sha(md)
    local = [p for p in glob.glob(os.path.join(ROOT, "build", "claims-v3", "*", "oh", "p[12]*"))]
    if local:
        sys.exit("prereg.py: OH blocks exist here: %s" % local)
    if not a.no_ssh:
        for host in ("aifoundry3", "aifoundry1"):
            r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", host, LIST_CMD],
                               capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                sys.exit("prereg.py: cannot list %s: %s" % (host, r.stderr.strip()))
            if r.stdout.strip():
                sys.exit("prereg.py: OH blocks exist on %s:\n%s" % (host, r.stdout))
    bins = {}
    for card, f in (("aifoundry3", a.bins_a3), ("aifoundry1-c1", a.bins_c1)):
        b = json.load(open(f))
        missing = [k for k, v in b.items() if not v.get("sha256")]
        if missing:
            sys.exit("prereg.py: %s: binaries missing: %s" % (card, missing))
        bins[card] = {k: v["sha256"] for k, v in b.items()}
    files = {f: sha(os.path.join(ROOT, f)) for f in LOCKED}
    pj = os.path.join(d, "prereg.json")
    json.dump({"items": ITEMS, "files": files, "binaries": bins, "params": ohlib.params()}, open(pj, "w"), indent=1, sort_keys=True)
    lock = {"files": dict(files, **{"tools/claims-v3/oh/prereg/prereg.json": sha(pj)}), "binaries": bins}
    lock_md = "%s\n```json\n%s\n```\n%s\n" % (ohlib.LOCK_BEGIN, json.dumps(lock, indent=1, sort_keys=True), ohlib.LOCK_END)
    when = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    txt = TEXT % dict(ITEMS, when=when, replaces=replaces, lock=lock_md)
    open(md, "w").write(txt)
    h = sha(md)
    open(os.path.join(d, "PREREG.sha256"), "w").write("%s  PREREG.md\n" % h)
    print(h)


if __name__ == "__main__":
    main()
