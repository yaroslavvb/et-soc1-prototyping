#!/usr/bin/env python3
"""E202's collection at the desk (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): step 11's desk half, after the
copy-back (E189's collect_e189.py form, with E196's gate-stop record and login scrub).

    /usr/bin/python3 -B tools/claims-v3/e202/collect_e202.py COPY DATA --box-home PATH --box-login LOGIN
        COPY  the session's directory as rsync copied it from the box (RB_OUT/e202-raw/T<T0>/)
        DATA  docs/reports/data/<day>-e202-mnist-int8-aifoundry3 for a session that ran a burst, or
              docs/reports/gate-stops/<day>-e202-mnist-int8-T<T0>-aifoundry3 for one that ran none (new; refused if it exists)

  1. COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but MANIFEST.sha256
     itself and runner.rc (the one file the wrapper writes after it); else exit 3, nothing written;
  2. THE KIND: queue.json's bursts_ran > 0 is data (docs/reports/data/), 0 is a gate stop's record (docs/reports/gate-stops/: no data,
     never a failed forecast; step 2 reads every docs/reports/data/*e202* path as an E202 datum, so a gate stop never lands there);
  3. DATA in E202.md 7.1's form: smoke/<arm>/ (host-raw.json = the host's own --out file, labels.bin, smoke.json, stdout.txt, host.err),
     bursts/<config>/b<k>/ (host-raw.json, host.json, burst.json, run.json, telemetry.jsonl.gz, stdout.txt, host.err, and energy.json),
     session/ (everything else: session.log, the config reads, stop-path.json, queue.json, the whole telemetry, runner.out, runner.rc,
     MANIFEST.sha256, the box's dry-pass-free record);
  4. each burst reduced by workloads/sparseparity/tools/energy_reduce.py, UNCHANGED (its own process, numpy), into its energy.json
     (energy.txt its printed lines); the one field it writes with the reducing machine's path, "dir", set to the burst's repository path;
  5. THE SCRUB: the box's home path becomes "~" and our own box login "<login>" in every text and .gz file; then no file may hold
     /home/ or the login (the desk-path gate, nopath_q142s.py, runs after this, from step 11);
  6. session-facts-e202.json (the scored stage, each arm's R, the bursts run and set aside, the stop, the peaks of board power and
     minshire[0] over the session's telemetry, the clock's samples, the config reads, the closing read's word, and since fix-e202 the
     runner's exit status (runner.rc) and its crash, if any: verify-e202's finding 2) and SHA256SUMS. A session the runner crashed in with
     no burst is collected as a record under docs/reports/gate-stops/ (no data) and named a crash's record, never a gate stop's.
The scorer is NOT run here: s24_score_e202.sh runs score_e202.py on the committed DATA, after the data commit. Exit 0 collected, 3 a
gate, 2 usage. RB_DESKTEST=1 with --data-outside lets a desk test write DATA in its scratch (never on the card day).
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
REDUCER = os.path.join(REPO, "workloads/sparseparity/tools/energy_reduce.py")
TEXT = (".json", ".txt", ".log", ".err", ".out", ".rc", ".sha256", ".jsonl")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def copy_back_exact(copy):
    man = os.path.join(copy, "MANIFEST.sha256")
    if not os.path.exists(man):
        return ["no MANIFEST.sha256"]
    want = {}
    for ln in open(man):
        if ln.strip():
            h, p = ln.rstrip("\n").split("  ", 1)
            want[p] = h
    have = set()
    for dp, dn, fn in os.walk(copy):
        for n in fn:
            have.add(os.path.relpath(os.path.join(dp, n), copy))
    bad = [f"missing {p}" for p in want if p not in have]
    bad += [f"differs {p}" for p in want if p in have and sha(os.path.join(copy, p)) != want[p]]
    bad += [f"not in the manifest: {p}" for p in sorted(have - set(want) - {"MANIFEST.sha256", "runner.rc"})]
    return bad


def scrub_file(p, home, login_re):
    """The box's home -> "~", then our login (a whole word only, never inside another word or a hash) -> "<login>"."""
    def fix(b):
        return login_re.sub(b"<login>", b.replace(home, b"~"))
    raw = open(p, "rb").read()
    if p.endswith(".gz"):
        data = gzip.decompress(raw)
        new = fix(data)
        if new != data:
            with open(p, "wb") as f:
                f.write(gzip.compress(new, compresslevel=9, mtime=0))
        return new
    if p.endswith(TEXT) or os.path.basename(p) in ("runner.rc",):
        new = fix(raw)
        if new != raw:
            open(p, "wb").write(new)
        return new
    return raw


def runner_rc(dabs):
    """session_e202.sh's runner.rc (written after the runner exits, outside its manifest): an int, or None if absent or unreadable."""
    try:
        t = open(os.path.join(dabs, "session", "runner.rc")).read().strip()
        return int(t) if t.lstrip("-").isdigit() else None
    except OSError:
        return None


def facts(dabs):
    q = json.load(open(os.path.join(dabs, "session", "queue.json")))
    tel = os.path.join(dabs, "session", "telemetry.jsonl.gz")
    n = n600 = 0
    peak_w = peak_c = None
    if os.path.exists(tel):
        for ln in gzip.open(tel, "rt"):
            if not ln.startswith("{"):
                continue
            try:
                s = json.loads(ln)
            except ValueError:
                continue
            n += 1
            if (s.get("mhz") or {}).get("minion") == 600:
                n600 += 1
            bw = s.get("board_w")
            c = ((s.get("temp_c") or {}).get("minshire") or [None])[0]
            if isinstance(bw, (int, float)):
                peak_w = bw if peak_w is None else max(peak_w, bw)
            if isinstance(c, (int, float)):
                peak_c = c if peak_c is None else max(peak_c, c)

    def cfg(name):
        try:
            return json.load(open(os.path.join(dabs, "session", f"config-{name}.json")))
        except (OSError, ValueError):
            return None
    return {"what": "E202's session facts (collect_e202.py): measured, from the session's own files", "t0": q.get("t0"),
            "scored_stage": q.get("scored_stage"), "smoke_gate": q.get("smoke_gate"), "R": q.get("R"),
            "smoke": {a: {k: v.get(k) for k in ("core_status", "logits_status", "status", "rc", "accuracy", "R")}
                      for a, v in (q.get("smoke") or {}).items()},
            "bursts_ran": q.get("bursts_ran"), "bursts": q.get("bursts"), "set_aside": q.get("set_aside"), "stop": q.get("stop"),
            "off_clock": q.get("off_clock"), "telemetry_samples": n, "samples_at_600_mhz": n600, "peak_board_w": peak_w,
            "peak_minshire0_c": peak_c, "config_start": cfg("start"), "config_end": cfg("end"),
            "closing_config": q.get("closing_config"), "t_first_ms": q.get("t_first_ms"), "t_close_ms": q.get("t_close_ms"),
            "crash": q.get("crash"), "runner_rc": runner_rc(dabs), "R_registered_rule": q.get("R_registered_rule"),
            "card_minutes_first_command_to_close": round((q["t_close_ms"] - q["t_first_ms"]) / 60000.0, 2)
            if q.get("t_first_ms") and q.get("t_close_ms") else None}


def main(argv):
    if len(argv) < 6 or argv[2] != "--box-home" or argv[4] != "--box-login":
        print(__doc__)
        return 2
    copy, data, box_home, login = os.path.abspath(argv[0]), argv[1], argv[3].rstrip("/"), argv[5]
    if not box_home.startswith("/") or len(box_home) < 6 or not login or "/" in login or len(login) < 2:
        print(f"COLLECT-REFUSED: the box's home path {box_home!r} or login is not usable")
        return 2
    dabs = os.path.join(REPO, data) if not os.path.isabs(data) else data
    rel = os.path.relpath(dabs, REPO)
    base = REPO
    if os.environ.get("RB_DESKTEST") == "1" and "--data-outside" in argv:     # a desk test only: a data folder in its scratch
        rel, base = os.path.basename(dabs), os.path.dirname(dabs)
    bad = copy_back_exact(copy)
    if bad:
        print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
        return 3
    print("COPY-BACK EXACT: every file of the box's MANIFEST.sha256 at its sha256, nothing else but runner.rc")
    try:
        q = json.load(open(os.path.join(copy, "queue.json")))
    except (OSError, ValueError):
        print("COLLECT-REFUSED: the session has no readable queue.json")
        return 3
    gate = not q.get("bursts_ran")
    crash = q.get("crash")
    want = "gate-stops" if gate else "data"
    if base == REPO and not rel.startswith(f"docs/reports/{want}/"):
        print(f"COLLECT-REFUSED: a session that ran {'no' if gate else 'a'} burst is collected under docs/reports/{want}/, not {rel}")
        return 2
    if "e202" not in rel:
        print(f"COLLECT-REFUSED: {rel} is not an E202 directory")
        return 2
    if os.path.exists(dabs):
        print(f"COLLECT-REFUSED: {rel} exists already (never merge into an earlier copy)")
        return 3
    os.makedirs(os.path.join(dabs, "session"))
    for top in ("smoke", "bursts"):
        if os.path.isdir(os.path.join(copy, top)):
            shutil.copytree(os.path.join(copy, top), os.path.join(dabs, top))
    for n in sorted(os.listdir(copy)):
        if n in ("smoke", "bursts"):
            continue
        s = os.path.join(copy, n)
        (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, os.path.join(dabs, "session", n))
    nb, nbad = 0, []
    bdir = os.path.join(dabs, "bursts")
    for cfg in sorted(os.listdir(bdir)) if os.path.isdir(bdir) else []:
        for k in sorted(os.listdir(os.path.join(bdir, cfg))):
            d = os.path.join(bdir, cfg, k)
            r = subprocess.run([sys.executable, "-B", REDUCER, d], capture_output=True, text=True, timeout=600)
            ej = os.path.join(d, "energy.json")
            if r.returncode not in (0, 1) or not os.path.exists(ej):
                nbad.append(f"{cfg}/{k}: the reducer rc {r.returncode}")
                continue
            with open(os.path.join(d, "energy.txt"), "w") as f:
                f.write(r.stdout)
            en = json.load(open(ej))
            en["dir"] = os.path.relpath(d, base)
            with open(ej, "w") as f:
                json.dump(en, f, indent=1)
            nb += 1
            print(f"reduced {cfg}/{k}: ok {en.get('ok')}, J over idle a launch {(en.get('board') or {}).get('j_per_solve')}, "
                  f"hard {en.get('hard')}")
    login_re = re.compile(rb"(?<![A-Za-z0-9_])" + re.escape(login.encode()) + rb"(?![A-Za-z0-9_])")
    left = []
    for dp, dn, fn in os.walk(dabs):
        for n in fn:
            p = os.path.join(dp, n)
            body = scrub_file(p, box_home.encode(), login_re)
            if b"/home/" in body or login_re.search(body):
                left.append(os.path.relpath(p, dabs))
    if left:
        print("SCRUB FAILED: a /home/ path or the login is left in " + ", ".join(left[:10]))
        return 3
    with open(os.path.join(dabs, "session-facts-e202.json"), "w") as f:
        json.dump(facts(dabs), f, indent=1)
    rows = []
    for dp, dn, fn in os.walk(dabs):
        dn.sort()
        for n in sorted(fn):
            p = os.path.join(dp, n)
            r2 = os.path.relpath(p, dabs)
            if r2 != "SHA256SUMS":
                rows.append(f"{sha(p)}  {r2}")
    with open(os.path.join(dabs, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(rows, key=lambda x: x[66:])) + "\n")
    if nbad:
        print("REDUCER FAILED: " + "; ".join(nbad))
        return 3
    ctype = str(crash).split(":")[0][:60] if crash else ""           # the crash's type only: its message can hold a box path
    kind = ("a crash's record (the runner crashed, no burst ran: " + ctype + "; session/queue.json holds it)" if gate and crash else
            "a gate stop record (no burst ran)" if gate else str(nb) + " bursts reduced" + ("; the runner crashed after them: " +
                                                                                      ctype if crash else ""))
    print(f"COLLECTED {rel}: {kind}; {len(rows)} files in SHA256SUMS; the scrub clean (no /home/ path, no login)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
