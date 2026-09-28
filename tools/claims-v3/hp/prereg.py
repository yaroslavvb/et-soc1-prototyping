#!/usr/bin/env python3
"""Heat placement (HP, DESIGN2 §3.5, §6.3): the pre-registration files and their lock.

    prereg.py --a2 [--replace-unused]
                                   freeze aifoundry2's same-day session: copy hplib.sh, hplib.py, sptrace_events.py and
                                   placements.json into a2/, then write a2/PREREG-A2.md (with the lock: the sha256 of
                                   every file in a2/, of ../lib.sh and of the binaries a2/block.sh runs),
                                   a2/prereg-a2.json and a2/PREREG-A2.sha256. Run it BEFORE the session; a2/block.sh
                                   refuses to run if any hash differs. It refuses once any a2 data exist
                                   (build/claims-v3/aifoundry2/hp/a2/p*), and refuses to replace an existing PREREG-A2
                                   unless --replace-unused (allowed only while no a2 data exist; the new file records
                                   the hash it replaces).
    prereg.py --val --registration registration.json --v0 v0.json --bin-c1 bin-c1.json
              [--probe-a3 probe.json] [--probe-c1 probe.json] [--replace-unused]
                                   after P3 (reduce.py --p3) and V0 (hplib.py v0final --write v0.json on card 1's data):
                                   write prereg/prereg.json, params/params-val-aifoundry1-c1.json, then prereg/PREREG.md
                                   (with the lock: the sha256 of prereg.json, params-val, the code, the helpers and card
                                   1's binaries from bin-c1.json, written on aifoundry1 by
                                   `V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/hp/block.sh --binhash`) and
                                   prereg/PREREG.sha256. block.sh (validation passes 9xxx) and reduce.py --val refuse on
                                   any mismatch. It refuses once PREREG.md exists (unless --replace-unused while no
                                   validation data exist) or any validation block exists, here or on aifoundry1
                                   (listed over ssh, or --card1-listing FILE; refused if it cannot be listed), and
                                   refuses if aifoundry1 already holds a PREREG (unless --replace-unused). It prints
                                   PREREG.md's sha256: record it outside the tree; validation blocks need it as
                                   HP_PREREG_SHA256. --out-dir and --params-dir work only under V3_DRY=1 (dry tests).
    prereg.py --check <prereg.json | a2/prereg-a2.json>   exit 0 if PREREG.md and every locked file are unchanged

The validation lock (DESIGN2 §6.3): PREREG.md's sha256 is in PREREG.sha256; PREREG.md carries the sha256 of
prereg.json, params-val-aifoundry1-c1.json, hp/block.sh, hp/hplib.sh, hp/hplib.py, hp/probe.sh, hp/reduce.py,
hp/sptrace_events.py, hp/placements.json, hp/ettelem-hp/ettelem.cpp, ../lib.sh, ../queue.sh,
tools/ettelem/flip_thermal_model.py and tools/ettelem/ettelem.cpp, and of card 1's heater, heater kernel, sampler and
ettelem-hp binaries. params-val no longer carries PREREG.md's sha256 (it is hashed inside PREREG.md, which would be
circular); prereg.py prints PREREG.md's sha256, which is the value to record.
"""
import argparse
import datetime
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import hplib as H  # noqa: E402

REL = lambda p: os.path.relpath(p, ROOT)
A2 = os.path.join(HERE, "a2")
A2_FROZEN = ["hplib.sh", "hplib.py", "sptrace_events.py", "placements.json"]
A2_OWN = {"PREREG-A2.md", "prereg-a2.json", "PREREG-A2.sha256"}
VAL_CODE = ["block.sh", "hplib.sh", "hplib.py", "probe.sh", "reduce.py", "sptrace_events.py", "placements.json",
            "ettelem-hp/ettelem.cpp", "run_queue.sh"]
# card 1's validation directories and deployed PREREG live on aifoundry1 (~/nekko), not where prereg.py usually runs
CARD1_HOST, CARD1_TREE = "aifoundry1", "nekko"
CARD1_LIST_CMD = ("cd ~/%s && ls -d build/claims-v3/aifoundry1-c1/hp/p9[0-9][0-9][0-9]* "
                  "build/claims-v3/aifoundry1-c1/hp-smoke/p9[0-9][0-9][0-9]* 2>/dev/null; "
                  "sha256sum tools/claims-v3/hp/prereg/PREREG.md tools/claims-v3/hp/params/params-val-aifoundry1-c1.json "
                  "2>/dev/null; true" % CARD1_TREE)
# README departure 37 (27 Sep 2026, decided before any validation data); reduce.py applies it (POWER_WAIVED)
POWER_WAIVER_S = ("Tier S POWER is WAIVED for every pair with INT16@32 (PLACE-tS, PLACE-kappa-S, CONC's INT16@32-UNI32@16): "
                  "sw_W is the median over t0 + 1 s .. t0 + t66 (DESIGN2 §5.5, unchanged) and INT16@32 crosses 66 C in "
                  "< 1 s from S_S (R1c: 0.86-0.97 s), so its window is empty and POWER cannot be computed (it would be "
                  "INSUFFICIENT by construction, card 1 heating faster). The verdicts list these pairs as \"waived: no "
                  "window in Tier S; see Tier L\". Equal power for the INT/PER/UNI placements rests on the Tier L check: "
                  "development R1c L16 sw_W INT16@32 13.96, PER16@32 13.87, UNI32@16 13.83 W, every pair within "
                  "+-0.5 W; on card 1 PLACE-t's POWER EQUIV (PER16@32-INT16@32, L16) is tested when PLACE-t is "
                  "registered, and the verdicts report the waived pairs' L16 values. WORK is not waived; the other "
                  "Tier S pairs (CONC's PER16@32-UNI32@16, MAP's B4NE-B4SW) keep POWER EQUIV.")
VAL_HELPERS = [os.path.join(HERE, "..", "lib.sh"), os.path.join(HERE, "..", "queue.sh"),
               os.path.join(ROOT, "tools", "ettelem", "flip_thermal_model.py"), os.path.join(ROOT, "tools", "ettelem", "ettelem.cpp")]
BIN_ROLES = ("heater", "heater_kernel", "ettelem", "ettelem_hp")


def refuse(msg):
    sys.exit("prereg.py refused: %s" % msg)


def check_bins(bins, where):
    if not isinstance(bins, dict) or set(bins) != set(BIN_ROLES):
        refuse("%s must list the binaries %s (block.sh --binhash)" % (where, ", ".join(BIN_ROLES)))
    missing = [r for r, e in bins.items() if not (e or {}).get("sha256")]
    if missing and not H.dry():
        refuse("%s: no sha256 for %s (the binary is missing where --binhash ran)" % (where, ", ".join(missing)))


def a2_data(extra=()):
    """Every a2 attempt directory on this host (build/claims-v3/aifoundry2, plus any --a2-data directory)."""
    import glob
    out = []
    for d in [os.path.join(ROOT, "build", "claims-v3", "aifoundry2")] + list(extra or []):
        out += glob.glob(os.path.join(d, "hp", "a2", "p*"))
    return sorted(out)


def a2(a):
    data = a2_data(a.a2_data)
    if data:
        refuse("a2 data exist (%s): PREREG-A2 is frozen for good (DESIGN2 §3.5: nothing in hp/a2/ changes after the "
               "session starts)" % ", ".join(REL(d) for d in data))
    replaced = None
    if os.path.exists(os.path.join(A2, "PREREG-A2.md")):
        if not a.replace_unused:
            refuse("a2/PREREG-A2.md exists: an unused freeze is replaced only with --replace-unused (no a2 data exist)")
        replaced = H.sha256(os.path.join(A2, "PREREG-A2.md"))
    for f in A2_FROZEN:                    # the frozen copies first: --binhash below runs a2/block.sh with them
        shutil.copy2(os.path.join(HERE, f), os.path.join(A2, f))
    # the binaries a2/block.sh would run on this host, resolved by a2/block.sh itself (V3_DRY: no device access)
    import subprocess
    r = subprocess.run(["bash", os.path.join(A2, "block.sh"), "--binhash"], cwd=ROOT, capture_output=True, text=True,
                       env=dict(os.environ, V3_DRY="1"))
    try:
        bins = json.loads(r.stdout)
    except Exception:
        refuse("a2/block.sh --binhash failed: %s %s" % (r.stdout[-300:], r.stderr[-300:]))
    check_bins(bins, "a2/block.sh --binhash")
    files = sorted(f for f in os.listdir(A2) if os.path.isfile(os.path.join(A2, f)) and f not in A2_OWN
                   and not f.endswith(".pyc"))
    hashes = {REL(os.path.join(A2, f)): H.sha256(os.path.join(A2, f)) for f in files}
    hashes[REL(os.path.join(HERE, "..", "lib.sh"))] = H.sha256(os.path.join(HERE, "..", "lib.sh"))
    P = json.load(open(os.path.join(A2, "params-a2.json")))
    now = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    br = P["branches"]
    tA, tB = P["trigA"], P["trigB"]
    md = f"""# PREREG-A2: aifoundry2's same-day clock-step session (heat placement, DESIGN2 §3.4-3.5)

Written {now}, before the session, by `tools/claims-v3/hp/prereg.py --a2`. The session may run only on
**{P['date']}** (owner decision O3, 27 Sep 2026: aifoundry2's part is tried today from whatever temperature it rests
at; nothing carries over to another day). `a2/block.sh` refuses to run if any file below differs from its hash, or
this file from `PREREG-A2.sha256`.

These items take their predictions from the firmware source, not from development: the governor compares the integer
mean of the 34 truncated minion-shire sensors against `> 65` (TPM:656-679; `firmware.md` §2, §5). aifoundry3 cannot
develop them (its clock is pinned at 600 MHz and its trace is predicted latched), so freezing them before development
is not premature.

## The session

1. Gate: `et-who`, `who`, the process scan (no other user, no foreign device process, no `Runner.Worker`, no queue of
   ours), the card lock held from here to the end.
2. R0 probe (DESIGN2 §3.2): one 1 s die reading gives the rest reading **R**; `sptrace` p0; one 2 s `UNI32@4` launch
   (128 minions) with no sampler; `sptrace` p1 at once; `ettelem config`. Class: ALIVE (power lines and an "event
   received" line after them), STUCK (power lines only), SILENT (no governor line; at R >= 66 the governor sits in
   its thermal loop). Prediction: **SILENT (LOOP) if R >= 66, ALIVE if R <= 65**.
3. Smoke: the sampler, one {P['smoke_launch_s']} s `UNI32@4` launch, `sptrace`, `reduce_a2.py --check-pass`.
4. Branch on R:

| R | Class | What runs | Outcome |
|---|---|---|---|
| <= {br['COOL']['rest_max']} | COOL | up to {br['COOL']['blocks']} A2 blocks from S_A2 = {br['COOL']['S_A2']} (the {br['COOL']['S_A2'] + 1} -> {br['COOL']['S_A2']} falling edge) | TRIG-A, TRIG-B (if ALIVE) tested |
| {br['COOL-']['rest_max']} | COOL- | the same from S_A2 = {br['COOL-']['S_A2']} | tested; t_down shorter |
| {br['COOL-']['rest_max'] + 1}-{br['MARGINAL']['rest_max']} | MARGINAL | {br['MARGINAL']['blocks']} A2 block from S_A2 = {br['MARGINAL']['S_A2']} | tested; None likely |
| >= {br['MARGINAL']['rest_max'] + 1} | WARM | one documentation run: a {P['launch_s']} s `UNI32@4` launch with the sampler (expected 600 MHz throughout, mean >= 66); then stop | **TRIG-A, TRIG-B, H12: NOT OBSERVABLE** -> INSUFFICIENT, reason "rest R C >= 66: the governor sits in its thermal loop at the 600 MHz bottom point (TPM:2316-2360; firmware.md:189-194), so no clock step can be provoked" |

   After a WARM first reading, up to {P['recheck_max']} more 1 s readings are allowed today (`a2/block.sh 2..4`), each
   after the gate, each >= {P['recheck_gap_s'] // 3600} h after the previous, the last before {P['recheck_last_local_hour']}:00 local time. The
   session (probe, smoke, branch) runs at the first reading <= 65.
5. An A2 block: one warm-up run from rest (a {P['launch_s']} s `{P['warmup_run']}` launch, discarded); then the 8 runs
   ({', '.join(P['runs'])}) in a seeded shuffle (seed {P['seed_base']} + block). Each run, inside its own 10 Hz `--reset-ms 1000`
   sampler: if the mean reads below S_A2 + 1, light lifts ({P['launch_s']} s `{P['warmup_run']}` launches, at most {P['warmup_max']}, discarded) until
   it does (DESIGN2's single warm-up run, applied per run: a 128-minion run's heat is transient, so after its 10 s tail
   a cool die has already fallen below the edge and could give the next run no falling edge); the falling
   S_A2+1 -> S_A2 edge (cap {P['edge_cap_s']} s, else void); one {P['launch_s']} s launch under `hold10`; {P['idle_after_s']} s more of sampling (the exit
   event); then, if TRIG-B is registered, `sptrace`. A second block runs only if the first block's last run reached its
   edge within {P['edge_cap_s']} s. The session stops launching at {P['session_cap_s'] // 60} min of card time.
6. End: the log level restored (if set), `block_end`.

Safety (every run): the watcher stops the heater and the session at a mean or high >= 90 C; a run ends after 2
samples at mean >= 80, high >= 85 or board >= 73 W; the block aborts if the watcher dies or its state goes stale. No
TDP, threshold, clock, reset, firmware or driver change; the only SP state change is the log level (WARNING, the boot
default), and only when the probe is ALIVE (owner O2) and the level found at the session start is known (INFO or
DEBUG; it is kept in `build/claims-v3/aifoundry2/hp/sp-level.json`). An unknown level (a failed or empty dump) sets
nothing and TRIG-B is not tested; a level found at WARNING or lower is left as found. WARNING is recorded as pending
before the set command, restored at the end and checked with a dump; a set left pending (an abort) is restored before
the next attempt's probe.

The session card-time cap ({P['session_cap_s'] // 60} min) holds for whole runs: a run starts only if its worst case (the lifts, the
{P['edge_cap_s']} s edge cap, the launch and its tail) fits in the time left. An aborted attempt (exit 1, or exit 3: someone else
on the card) writes `a2.json` with branch ABORTED; its data are never used, and a re-check (2-4) may follow (an ABORTED
attempt is no reading for the 2 h gap). The bypass variables `HP_A2_ANY_DAY`, `HP_A2_NO_GAP`, `HP_A2_IN_QUEUE` and
`HP_PARAMS_DIR` are refused unless `V3_DRY=1`; the caps are hplib.py's fixed defaults (no params file is read).

Outcome precedence (README departure 18, fixed before any data): a CI wholly inside +-band fails a SIGN or NONZERO
item even when it also excludes 0.

## Items

**TRIG-A (the clock test), prediction from source: H1 holds.** Per measured run (not a warm-up, the edge reached,
not void: heater rc, safety stop, sampler gap > 1 s), from the samples after t0 (the heater's own `t_start_ms`):
`t_up` the first sample at 800 MHz; `t_hi` the first sample at 800 MHz whose windowed high reads >= 66; `t_m` the
first sample whose mean reads >= 66; `t_down` the first **one-point** down-step 800 -> 700 MHz (a single 800 -> 600
change is an idle or boot reset and is excluded).
- Separating: (a) `t_m - t_hi` >= {tA['sep_tm_minus_thi_s']} s; or (b) a rise under a hot max: the high already reads >= {tA['rise_under_hot_high_c']} at `t_up`
  and the clock holds 800 MHz for >= {tA['rise_hold_s']} s.
- Fits H1: (a) `t_down` in [`t_m` - {-tA['fit_lo_s']}, `t_m` + {tA['fit_hi_s']}] s, or (b). Fits H1': (a) `t_down` in [`t_hi` - {-tA['fit_lo_s']}, `t_hi` + {tA['fit_hi_s']}] s.
- **Holds** if >= {tA['holds_min_sep_runs']} separating runs over >= {tA['holds_min_blocks']} blocks, >= {int(100 * tA['holds_frac_h1'])}% fit H1 and <= {tA['holds_max_h1p']} fits H1'.
  **Fails** if >= {int(100 * tA['fails_frac_h1p'])}% fit H1'. **None** otherwise, including not observable.
- The limit is stated: one day, one room.

**TRIG-B (the trace test), registered only if the probe is ALIVE (or ALIVE_CANDIDATE).** At WARNING. A dump counts
only if the newest entry of the previous dump reappears in it. The SP tick rate and offset are fitted by least
squares from the power lines against the heater's kernel starts and process ends; a residual above
{tB['tick_resid_max_ms']} ms voids the session's TRIG-B. Per thermal event E, with m(E) the host means and h(E) the highs within
+-{tB['window_s']} s: discriminating if max h >= max m + {tB['disc_c']}; H1-consistent: a down event printing T >= 66 within +-{tB['tol_c']} of
some m, or an idle event printing T <= 65 within +-{tB['tol_c']} of some m with max m >= 65; H1'-consistent: T >= max m + {tB['disc_c']}.
First-event test per re-armed run (the high <= 65 in the 3 samples before t0): H1 puts the first down event in
[t_m - {-tB['first_event_lo_s']}, t_m + {tB['first_event_hi_s']}] s, H1' in [t_hi - {-tB['first_event_lo_s']}, t_hi + {tB['first_event_hi_s']}] s; a test counts for H1' only if it fits
H1' and not H1. **Holds** if >= {tB['holds_min_disc']} discriminating events, >= {int(100 * tB['holds_frac_h1'])}% H1-consistent, <= {tB['holds_max_h1p']} H1'-consistent and no
first-event test for H1'; **fails** if >= {int(100 * tB['fails_frac_h1p'])}% of the discriminating events are H1'-consistent or >= {tB['fails_first_event_h1p']} first-event
tests fit H1'; **None** otherwise and on a SILENT card. An ALIVE_CANDIDATE whose first thermal down event has no idle
event after it is reclassified STUCK (None).

**H12 (DVFS-PLACE), exploratory, reported:** per block ln(min(t_down PER16@8, {P['C_down_s']}) / min(t_down INT16@8, {P['C_down_s']})), each
placement the mean of its runs' ln min(t_down, {P['C_down_s']}), with its range. With at most 2 blocks it is not a test.

**Outcome words:** V3's (`card_verdicts`) over the one registered card, aifoundry2: PASS, FAIL, INSUFFICIENT (None,
including NOT OBSERVABLE). "Not registered" when the probe is not ALIVE.

## Parameters

```json
{json.dumps(P, indent=1)}
```

## Files and binaries (sha256)

| File | sha256 |
|---|---|
""" + "".join("| `%s` | `%s` |\n" % (k, v) for k, v in sorted(hashes.items())) + """
| Binary (role) | Path | sha256 |
|---|---|---|
""" + "".join("| %s | `%s` | `%s` |\n" % (r, e["path"], e["sha256"]) for r, e in sorted(bins.items())) + (
        "\nThis freeze replaces an unused earlier one (PREREG-A2.md sha256 `%s`); no a2 data existed.\n" % replaced
        if replaced else "") + """
## The lock (machine-readable; a2/block.sh checks every entry)

""" + H.lock_block({"card": "aifoundry2", "files": hashes, "binaries": bins})
    open(os.path.join(A2, "PREREG-A2.md"), "w").write(md)
    mdh = H.sha256(os.path.join(A2, "PREREG-A2.md"))
    json.dump({"written": now, "date": P["date"], "sha256": hashes, "binaries": bins, "replaces": replaced,
               "md": {"path": REL(os.path.join(A2, "PREREG-A2.md")), "sha256": mdh}},
              open(os.path.join(A2, "prereg-a2.json"), "w"), indent=1)
    open(os.path.join(A2, "PREREG-A2.sha256"), "w").write("%s  PREREG-A2.md\n" % mdh)
    print("wrote a2/PREREG-A2.md (sha256 %s), a2/prereg-a2.json (%d files, %d binaries), a2/PREREG-A2.sha256%s" % (
        mdh, len(hashes), len(bins), "; replaces the unused %s" % replaced if replaced else ""))


def val_data(extra=()):
    """Validation block directories on this host (build/claims-v3/aifoundry1-c1, plus any --val-data directory)."""
    import glob
    out = []
    for d in [os.path.join(ROOT, "build", "claims-v3", "aifoundry1-c1")] + list(extra or []):
        out += glob.glob(os.path.join(d, "hp", "p9[0-9][0-9][0-9]*")) + glob.glob(os.path.join(d, "hp-smoke", "p9[0-9][0-9][0-9]*"))
    return sorted(out)


def card1_listing(a):
    """(validation dirs, {path: sha256} of the PREREG files) on card 1's host (review low, 27 Sep: the local check sees
    only this host's build/claims-v3/aifoundry1-c1, and prereg.py normally runs elsewhere). From --card1-listing FILE
    (the output of CARD1_LIST_CMD run on aifoundry1), from this host if it is aifoundry1, else fetched with ssh; outside
    V3_DRY a listing that cannot be had refuses the freeze. Under V3_DRY without --card1-listing: none."""
    import socket
    import subprocess
    if a.card1_listing:
        txt = open(a.card1_listing).read()
    elif socket.gethostname() == CARD1_HOST:
        return [], {}                    # val_data() already looks at this tree's build/claims-v3/aifoundry1-c1
    elif H.dry():
        return [], {}
    else:
        try:
            r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", CARD1_HOST, CARD1_LIST_CMD],
                               capture_output=True, text=True, timeout=60)
        except Exception as e:
            r = None
            err = str(e)
        if r is None or r.returncode != 0:
            refuse("cannot list card 1's validation directories on %s (%s): run on %s\n    %s\n  and pass its output "
                   "with --card1-listing FILE" % (CARD1_HOST, (r.stderr.strip()[-200:] if r is not None else err),
                                                   CARD1_HOST, CARD1_LIST_CMD))
        txt = r.stdout
    dirs, shas = [], {}
    for line in txt.splitlines():
        f = line.split()
        if len(f) == 2 and len(f[0]) == 64:
            shas[f[1]] = f[0]
        elif len(f) == 1 and "/p9" in f[0]:
            dirs.append(f[0])
    return dirs, shas


def val(a):
    if (a.out_dir or a.params_dir) and not H.dry():
        refuse("--out-dir and --params-dir work only under V3_DRY=1 (dry tests); the real PREREG goes to hp/prereg/")
    c1_dirs, c1_shas = card1_listing(a)
    if c1_dirs:
        refuse("validation data exist on %s (%s): PREREG is frozen for good (DESIGN2 §6.4)" % (
            CARD1_HOST, ", ".join(c1_dirs[:5])))
    reg = json.load(open(a.registration))
    reg = reg.get("registration", reg)
    out_dir = a.out_dir or os.path.join(HERE, "prereg")
    params_dir = a.params_dir or os.path.join(HERE, "params")
    mdp = os.path.join(out_dir, "PREREG.md")
    pvp = os.path.join(params_dir, "params-val-aifoundry1-c1.json")
    data = val_data(a.val_data)
    if data:
        refuse("validation data exist (%s): PREREG is frozen for good (DESIGN2 §6.4)" % ", ".join(REL(d) for d in data[:5]))
    replaced = None
    if c1_shas and not a.replace_unused:
        refuse("%s already has a PREREG (%s): no re-freeze (an unused freeze is replaced only with --replace-unused "
               "while no validation data exist)" % (CARD1_HOST, ", ".join("%s %s" % (k, v[:12]) for k, v in sorted(c1_shas.items()))))
    if os.path.exists(mdp) or os.path.exists(pvp):
        if not a.replace_unused:
            refuse("%s or %s exists: no re-freeze (an unused freeze is replaced only with --replace-unused while no "
                   "validation data exist; the blocks on aifoundry1 also refuse a PREREG other than the one their "
                   "earlier validation blocks ran under)" % (REL(mdp), REL(pvp)))
        replaced = H.sha256(mdp) if os.path.exists(mdp) else None
    # V0 (DESIGN2 §6.1): card 1's own edges, required (review F6)
    # S_L8 is required only while the registration keeps L8 or G8 (README departure 36: after D-L8 drops both, the
    # S_L8 series never runs on card 1 and the frozen S_L8 is unused)
    types_kept = reg.get("types_kept", [])
    need8 = H.l8_kept(types_kept)
    v0 = H.load_json(a.v0) if a.v0 else None
    if not v0 or not v0.get("complete") or v0.get("S_L") is None or (need8 and v0.get("S_L8") is None):
        refuse("--v0 v0.json with card 1's settled S_L%s is required (hplib.py v0final --data "
               "build/claims-v3/aifoundry1-c1 --card aifoundry1-c1 --write v0.json, after the V0 blocks; the "
               "registration keeps %s)" % (" and S_L8" if need8 else "", types_kept))
    for k in (("S_L", "S_L8") if need8 else ("S_L",)):
        lo, hi = H.VAL_RANGES[k]
        if not lo <= v0[k] <= hi:
            refuse("V0 %s = %s outside validation's range %s-%s" % (k, v0[k], lo, hi))
    bins = H.load_json(a.bin_c1) if a.bin_c1 else None
    check_bins(bins, "--bin-c1 (V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/hp/block.sh --binhash on aifoundry1)")
    os.makedirs(out_dir, exist_ok=True)
    probes = {}
    for k, p in (("aifoundry3", a.probe_a3), ("aifoundry1-c1", a.probe_c1)):
        probes[k] = (H.load_json(p) or {}).get("class") if p else None
    trigb = probes.get("aifoundry1-c1") in ("ALIVE", "ALIVE_CANDIDATE")
    P3 = H.resolve_params("r3", "aifoundry3")
    frozen = {k: P3[k] for k in ("S_L", "S_L8", "S_S", "target_S", "target_L_over", "target_L8_over", "chain_cap_s",
                                 "C_L", "kappa_gate", "void_tauc_lo", "void_tauc_hi", "void_widle_range_w")}
    frozen["S_L"] = v0["S_L"]                                       # card 1's V0 edges (§6.1)
    if need8:
        frozen["S_L8"] = v0["S_L8"]
    # else: L8 and G8 dropped, no validation block runs at S_L8; it keeps aifoundry3's frozen R3 value (unused)
    frozen["types"] = types_kept
    frozen["n_val"] = reg.get("n_val", {})
    items = reg.get("items", {})
    regd = {k: v for k, v in items.items() if v.get("registered")}
    waiver = ("TRIG-A on card 1 is WAIVED: DESIGN2 §3.4 registers it only if card 1's probe is ALIVE and its smoke shows "
              "the clock leaving 600 MHz below 65 C; this implementation has no card-1 clock-step protocol (its "
              "validation runs void any sample off 600 MHz), so TRIG-A is not tested on card 1 whatever the probe says "
              "(card 1's probe: %s)." % probes.get("aifoundry1-c1"))
    S_L8_NOTE = ("L8 and G8 are kept: S_L8 is card 1's settled V0 edge." if need8 else
                 "L8 and G8 were dropped (types kept: %s; by D-L8 in development, DESIGN2 §5.3, or by P3): card 1 "
                 "runs no S_L8 V0 series and no L8 or G8 validation block; the frozen S_L8 (aifoundry3's R3 value) is "
                 "unused (README departure 36)." % ", ".join(types_kept))
    now = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    # 1. prereg.json and params-val (no PREREG.md hash inside either: PREREG.md hashes them)
    pjp = os.path.join(out_dir, "prereg.json")
    json.dump({"written": now, "items": items, "beta": reg.get("beta"), "primary": reg.get("primary"),
               "trigb_registered": trigb, "probes": probes, "frozen": frozen, "v0": v0,
               "trig_a_card1": {"registered": False, "waiver": waiver},
               "power_waiver_tier_s": POWER_WAIVER_S, "s_l8_note": S_L8_NOTE,
               "outcome_precedence": "a CI wholly inside +-band fails SIGN and NONZERO even if it excludes 0",
               "cv": reg.get("cv"), "d_s": reg.get("D-S"), "notes": reg.get("notes")},
              open(pjp, "w"), indent=1, default=lambda x: None)
    pv = dict(frozen)
    pv.pop("n_val", None)
    pv.update({"trigb_registered": trigb, "beta": reg.get("beta"),
               "_what": "frozen by prereg.py --val %s: every value equals prereg.json's frozen; PREREG.md hashes this "
                        "file; block.sh refuses a validation pass on any mismatch" % now})
    json.dump(pv, open(pvp, "w"), indent=1)
    # 2. the lock
    files = {REL(os.path.join(HERE, f)): H.sha256(os.path.join(HERE, f)) for f in VAL_CODE}
    for f in VAL_HELPERS:
        files[REL(f)] = H.sha256(f)
    files[REL(pjp)] = H.sha256(pjp)
    files[REL(pvp)] = H.sha256(pvp)
    lock = {"card": "aifoundry1-c1", "prereg_json": REL(pjp), "params_val": REL(pvp), "files": files, "binaries": bins}
    rows = []
    for k, v in items.items():
        if v.get("registered"):
            wv = v.get("power_waived_pairs") or []
            rows.append("| %s | %s | %s | %.4g | %s | n_val %s; POWER and WORK EQUIV on %s%s |" % (
                k, v["type"], v["prediction"], v["band"], v.get("primary"), frozen["n_val"].get(v["type"]),
                ", ".join(v.get("power_work_pairs") or []),
                "; POWER waived on %s (no window in Tier S; see Tier L)" % ", ".join(wv) if wv else ""))
        else:
            rows.append("| %s | %s | reported, not tested | %.4g | | %s |" % (k, v["type"], v.get("band", float("nan")),
                                                                              v.get("reason", "")))
    md = f"""# PREREG: heat placement, validation on aifoundry1 card 1 (DESIGN2 §6)

Written {now} by `tools/claims-v3/hp/prereg.py --val` from the development registration (P3, `reduce.py --p3`) and
card 1's V0 calibration. Once the first validation block starts, code, parameters and this item list stay as hashed
(DESIGN2 §6.4). This file's sha256 is in `PREREG.sha256`; the lock at the end holds the sha256 of `prereg.json` (every
item, prediction, band, beta, primary and n_val), of `params-val-aifoundry1-c1.json`, of the code and helpers, and of
card 1's binaries. `block.sh` refuses a validation block and `reduce.py --val` refuses to reduce on any mismatch, and
on aifoundry1 a validation block also refuses a PREREG other than the one earlier validation blocks ran under.

- Probe classes: aifoundry3 {probes.get('aifoundry3')}, aifoundry1-c1 {probes.get('aifoundry1-c1')}; TRIG-B registered on card 1: {trigb}.
- {waiver}
- Family size: {len(regd)} registered items at 99% (plus POWER and WORK EQUIV on every pair of a registered item,
  CONC, MAP and LIN included). Under a global null each SIGN item holds falsely with probability 0.005; no Bonferroni
  correction (V3 practice).
- Outcome precedence (README departure 18, fixed before any data): a 99% CI lying wholly inside +-band FAILS a SIGN or
  NONZERO item even when it also excludes 0 (the effect is shown negligible).
- Each type uses its first n_val usable validation blocks in pass order (void or incomplete blocks are replaced by
  later ones, §4.4); later blocks are listed as extra and never used; fewer than n_val usable blocks gives
  INSUFFICIENT. A block is used only if every registered pair in it is complete.
- {POWER_WAIVER_S}
- {S_L8_NOTE}
- kappa gate {frozen.get('kappa_gate')} (as designed; decided 27 Sep 2026 before any validation data): an item whose
  development runs never passed it is listed below as reported, not tested.
- beta = {reg.get('beta')}; the primary contrast per time item as listed (L or L_adj, chosen by P3).
- CV ratio for card 1 (§2.4): {json.dumps(reg.get('cv'), default=lambda x: None)}.
- Only signs transfer between cards, never magnitudes.

| Item | Block type | Prediction | Band | Primary | n / reason |
|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## Frozen parameters (card 1)

{"S_L and S_L8 are card 1's V0 edges" if need8 else "S_L is card 1's V0 edge (S_L8: L8 and G8 dropped, unused)"} ({json.dumps({k: v0.get(k) for k in ('S_L', 'S_L8', 'L8_offset')})}); the rest are
aifoundry3's frozen R3 values.

```json
{json.dumps(frozen, indent=1)}
```

## Development values (aifoundry3, REPORTED)

```json
{json.dumps({k: v.get('dev_ci99') for k, v in items.items()}, indent=1, default=lambda x: None)}
```

## Files and binaries (sha256)

| File | sha256 |
|---|---|
""" + "".join("| `%s` | `%s` |\n" % (k, v) for k, v in sorted(files.items())) + """
| Binary (role, card 1) | Path | sha256 |
|---|---|---|
""" + "".join("| %s | `%s` | `%s` |\n" % (r, e["path"], e["sha256"]) for r, e in sorted(bins.items())) + (
        "\nThis freeze replaces an unused earlier one (PREREG.md sha256 `%s`); no validation data existed.\n" % replaced
        if replaced else "") + """
## The lock (machine-readable; block.sh and reduce.py --val check every entry)

""" + H.lock_block(lock)
    open(mdp, "w").write(md)
    mdh = H.sha256(mdp)
    open(os.path.join(out_dir, "PREREG.sha256"), "w").write("%s  PREREG.md\n" % mdh)
    print("wrote %s (sha256 %s), prereg.json, PREREG.sha256 and %s%s" % (REL(mdp), mdh, REL(pvp),
                                                                    "; replaces the unused %s" % replaced if replaced else ""))
    print("RECORD this sha256 outside the tree now (commit PREREG.md and note the sha256 in docs/findings/03-experiments.md): "
          "every validation block refuses to run unless started with HP_PREREG_SHA256=%s (README 'The lock')" % mdh)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--a2", action="store_true")
    ap.add_argument("--val", action="store_true")
    ap.add_argument("--check")
    ap.add_argument("--registration")
    ap.add_argument("--probe-a3")
    ap.add_argument("--probe-c1")
    ap.add_argument("--v0")
    ap.add_argument("--bin-c1")
    ap.add_argument("--replace-unused", action="store_true")
    ap.add_argument("--val-data", action="append", help="another card-1 data dir to check for validation blocks")
    ap.add_argument("--card1-listing", help="the output of prereg.CARD1_LIST_CMD run on aifoundry1 (else fetched by ssh)")
    ap.add_argument("--a2-data", action="append", help="another aifoundry2 data dir to check for a2 attempts")
    ap.add_argument("--out-dir")
    ap.add_argument("--params-dir")
    a = ap.parse_args()
    if a.a2:
        return a2(a)
    if a.check:
        # the file part of a lock (the binaries are checked where they run: block.sh, a2/block.sh, reduce.py --val)
        if os.path.basename(a.check) == "prereg-a2.json":
            ok, why = H.a2lock(a.check, None, need_bins=False)
        else:
            d = os.path.dirname(os.path.abspath(a.check))
            ok, why, _ = H.md_and_sha(os.path.join(d, "PREREG.md"), os.path.join(d, "PREREG.sha256"))
            if ok:
                lock = H.parse_lock(os.path.join(d, "PREREG.md"))
                bad = H.check_lock_files(lock, None, need_bins=False)
                if lock.get("prereg_json") != REL(a.check):
                    bad.append("%s is not the prereg.json PREREG.md locks" % REL(a.check))
                ok, why = not bad, "; ".join(bad) or "PREREG.md and all %d locked files match" % len(lock.get("files") or {})
        print(why)
        sys.exit(0 if ok else 1)
    if a.val:
        if not a.registration:
            ap.error("--val needs --registration")
        return val(a)
    ap.print_help()


if __name__ == "__main__":
    main()
