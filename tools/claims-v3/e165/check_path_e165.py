#!/usr/bin/env python3
"""E165 (Q141(g)), amendment A2-5: the scorer's whole code path, pinned, and checked at collection before any score. Standard library only;
no device, no ssh; it reads committed files and writes nothing (--self-test writes one temporary directory and removes it).

    python3 -B tools/claims-v3/e165/check_path_e165.py              # from the top of the tree: exit 0 if every check passes, else 1
    python3 -B tools/claims-v3/e165/check_path_e165.py --self-test  # the pins refuse a changed byte (a temporary copy of the pinned files)

Why. score_e165.main() checks e165_common.FROZEN only (pool 7's predictions and manifests, m9_a2.json, predict_m9_a2.py). The primary's call
reads more: predict_m9_a2 imports make_predictions_e119 (E83's dither, `dither`), which imports kspeed/e83/predict_e83.py (`Rel._d`, `NQ`),
hpl/surface_hpl.py and hpl/surface_hpl_t.py, and reads four committed data files as it loads; the reduction imports hpl/reduce_hpl.py (with
hpl/sptrace_full.py and dv2/sptrace_events.py) and kspeed/reduce_kspeed.py, and collect() reads kspeed/predictions.json. None of them was
checked when a score is made (the verifier of Q141(g), its fault 5). This is the check, run by collect_e165_bounded.sh before it collects:

  1. e165_common.check_frozen(ccheck=True): the registration's 10 pins (3ef06839);
  2. PRIMARY_PATH: the 8 files the primary's call reads beyond FROZEN, each at its pin here AND at its own entry in
     ../kinds/blind7/provenance-blind7.json (the bytes Q140(x) froze pool 7's predictions with, 75802201);
  3. REDUCTION and E165_OWN: the reduction's 5 files, and E165's own score_e165.py, e165_common.py, make_predictions_e165.py and
     predictions-e165.json, each at its pin here (the bytes of the registration's and the scorer's commits, 3ef06839 and a5c56d17;
     the reduction's are E160's, unchanged since 23 Sep-31 Oct);
  4. the closure is whole: under an audit hook on file opens, importing score_e165 and calling the primary on every pool tile, with a
     session read (one zeros-anchor burst at 752 MHz among them, which burst() drops) and with none, opens no file of the tree and loads no
     module of the tree outside 1-3 (compiled-bytecode caches aside);
  5. the frozen-block recheck (make_predictions_e165's, here without writing): burst() with no session read reproduces every field of
     M9.a2_q140l in predictions-blind7-aifoundry2.json on all 61 tiles (1,586 fields, 0 differ).

SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PROV_REL = "tools/claims-v3/kinds/blind7/provenance-blind7.json"
PRIMARY_PATH = {  # read by the primary's call beyond e165_common.FROZEN (each also pinned in provenance-blind7.json, 75802201)
    "tools/claims-v3/e119/make_predictions_e119.py": "8f9b7fe440a632bddbab411a2b054aa87880b64c12b685efd612e211ca8e96e0",
    "tools/claims-v3/kspeed/e83/predict_e83.py": "f82efac5c0107a30808ede5bbd6f2f479c77fac5a6ea8f22e820ec2749783cd4",
    "tools/claims-v3/hpl/surface_hpl.py": "cf2b63e2b9bf9b53b2aa0a6b415578d4464f5cf3c4ca689985f75b7006e23550",
    "tools/claims-v3/hpl/surface_hpl_t.py": "772da3bc732eb8443bd41d1d8c222c16bdd8aeecb44c2eaae51128e013602248",
    "tools/claims-v3/kinds/predictions-e101.json": "bf2646e9889a0a3dc7883abb2f31c456f40c5c0a93a5d6db5d868710fa9c5652",
    "docs/reports/data/2026-11-01-e107-gemm-placement/e107.json": "87b190f364ceb2eee796d00b78e6fda49775be59c1b40cc87da0b6f6c79f6a86",
    "docs/reports/data/2026-11-01-e107-gemm-placement/scored.json": "fd9d43e2764da8a604dc7fd4ed919897d81ac0fc57af4693b0f8edb31b4f7811",
    "docs/reports/data/2026-11-01-e105-gemm-layout/results-speed.json": "e817d98062ce7fc8cdd27befa3bbe904bc44ce1d0cd635eaba8a6b3cc61188d2",
}
REDUCTION = {  # E160's reduction, imported unchanged by score_e165.py (E80's metrics)
    "tools/claims-v3/hpl/reduce_hpl.py": "e49b6c1b39d742043a73447f7b4f67c677bd9b73c9902664261113c5c241ed00",
    "tools/claims-v3/hpl/sptrace_full.py": "58dd8b04860bee003cbf924db412764fe8561d8ec11770b14fe13b465e6fda59",
    "tools/claims-v3/dv2/sptrace_events.py": "8cbb7df0d6e32494945ad5a8d761b9b02c4b6ad3efa1d087b0c7091a71178834",
    "tools/claims-v3/kspeed/reduce_kspeed.py": "10fee8c153a2af4550e0ae40cda521683ab8245413a7af6f9649f381af71eca2",
    "tools/claims-v3/kspeed/predictions.json": "69a62b31607a02a481a8ea23ba716d42fae5822343cb372f7fa706e6ba00762c",
}
E165_OWN = {  # the registration (3ef06839) and the scorer (a5c56d17), as committed
    "tools/claims-v3/e165/score_e165.py": "03bfd40b728bad2a40a8e3559f16ac4b7e817929729c2090d9f029b4b41fd74c",
    "tools/claims-v3/e165/e165_common.py": "b6c021c122b3c8c934510893b56cbcefadaee736c8997b4648460a728005824b",
    "tools/claims-v3/e165/make_predictions_e165.py": "6dc500881ca80565e23308b3f665c50401880229e77493dd804c0d7a2b2ea415",
    "tools/claims-v3/e165/predictions-e165.json": "7235109379f9a8f6af5057a205ea5b41c18049045706801ee46b8325380555a2",
}
SELF_REL = "tools/claims-v3/e165/check_path_e165.py"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_pins(root, frozen, ccheck_frozen):
    """the differences of checks 1-3 under `root` (a list of lines; empty = every pin holds)"""
    bad = []
    for rel, want in {**frozen, **ccheck_frozen}.items():
        p = os.path.join(root, rel)
        got = sha256_file(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"1 {rel}: sha256 {got}, registered {want}")
    pp = os.path.join(root, PROV_REL)
    prov = {f["path"]: f["sha256"] for f in json.load(open(pp))["files"]} if os.path.isfile(pp) else {}
    for rel, want in PRIMARY_PATH.items():
        p = os.path.join(root, rel)
        got = sha256_file(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"2 {rel}: sha256 {got}, pinned {want}")
        if prov.get(rel) != want:
            bad.append(f"2 {rel}: provenance-blind7.json has {prov.get(rel)}, pinned {want}")
    for tag, group in (("3", REDUCTION), ("3", E165_OWN)):
        for rel, want in group.items():
            p = os.path.join(root, rel)
            got = sha256_file(p) if os.path.isfile(p) else None
            if got != want:
                bad.append(f"{tag} {rel}: sha256 {got}, pinned {want}")
    return bad


def main():
    seen, tracing = [], [True]

    def hook(ev, args):
        if tracing[0] and ev == "open" and args and isinstance(args[0], (str, bytes)):
            ap = os.path.normpath(os.path.join(os.getcwd(), os.fsdecode(args[0])))
            if ap.startswith(ROOT + os.sep) and ap not in seen:
                seen.append(ap)

    # 4 (traced first): import the scorer and call the primary on every pool tile, with a session read and with none
    sys.addaudithook(hook)
    sys.path.insert(0, HERE)
    import e165_common as C  # noqa: E402
    import score_e165 as S  # noqa: E402,F401
    P = json.load(open(os.path.join(ROOT, C.PRED_REL)))
    anchors = {t: [{"burst_w": 34.6, "burst_mhz": 800.0, "die_start": 54}, {"burst_w": 32.4, "burst_mhz": 752.0, "die_start": 55}]
               for t in ("fp32", "fp16", "int8")}
    for name, rec in sorted(P["tiles"].items()):
        lo, hi = rec["M9"]["D600_a3_95"]
        C.primary(rec["M9"]["D600_a3_footing_w"], rec["type"], anchors, [53, 55], (hi - lo) / 2.0)
        C.primary(rec["M9"]["D600_a3_footing_w"], rec["type"], None, None, (hi - lo) / 2.0)
    tracing[0] = False

    print(f"E165 code-path check (amendment A2-5): check_path_e165.py sha256 {sha256_file(os.path.abspath(__file__))}; python {sys.version.split()[0]}")
    bad = check_pins(ROOT, C.FROZEN, C.CCHECK_FROZEN)
    n1 = len(C.FROZEN) + len(C.CCHECK_FROZEN)
    print(f"  1. the registration's pins (e165_common FROZEN + CCHECK_FROZEN): {n1} files, {sum(1 for b in bad if b.startswith('1 '))} differ")
    print(f"  2. the primary's path beyond FROZEN, at the pins and at provenance-blind7.json: {len(PRIMARY_PATH)} files, "
          f"{sum(1 for b in bad if b.startswith('2 '))} differ")
    print(f"  3. the reduction and E165's own files: {len(REDUCTION) + len(E165_OWN)} files, {sum(1 for b in bad if b.startswith('3 '))} differ")
    files = {os.path.relpath(p, ROOT) for p in seen if os.sep + "__pycache__" + os.sep not in p}
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f and os.path.abspath(f).startswith(ROOT + os.sep):
            files.add(os.path.relpath(os.path.abspath(f), ROOT))
    pinned = set(C.FROZEN) | set(C.CCHECK_FROZEN) | set(PRIMARY_PATH) | set(REDUCTION) | set(E165_OWN) | {SELF_REL}
    stray = sorted(files - pinned)
    for s in stray:
        bad.append(f"4 {s}: read or loaded on the score's path, not pinned")
    print(f"  4. the closure: {len(files)} files of the tree read or loaded by score_e165 and the primary on {len(P['tiles'])} tiles x 2; "
          f"{len(stray)} outside the pins")

    # 5. the frozen-block recheck, as make_predictions_e165.main() does it (d_band_hw = half of M9.D600_a3_95), without writing
    A2 = C.m9a2()
    nt = nf = 0
    differ = []
    for name in sorted(P["tiles"]):
        rec = P["tiles"][name]
        q = rec["M9"]["a2_q140l"]
        lo, hi = rec["M9"]["D600_a3_95"]
        again = A2.burst(rec["M9"]["D600_a3_footing_w"], rec["type"], anchors=None, die_starts=None, D_band_hw=(hi - lo) / 2.0)
        for k, v in q.items():
            nf += 1
            if again.get(k) != v:
                differ.append(f"{name}.{k}: {again.get(k)!r} vs frozen {v!r}")
        nt += 1
    for d in differ:
        bad.append(f"5 {d}")
    print(f"  5. the frozen-block recheck: burst() with no session read reproduces M9.a2_q140l on {nt} tiles, {nf} fields, {len(differ)} differ")
    for b in bad:
        print("   DIFFERS", b)
    print("CHECK-PATH:", "PASS (every file on the score's path is the registered bytes)" if not bad else f"FAIL ({len(bad)} differ): do not score")
    return 0 if not bad else 1


def self_test():
    """the pins refuse a changed byte: a temporary copy of every pinned file, one byte of make_predictions_e119.py changed"""
    sys.path.insert(0, HERE)
    import e165_common as C  # noqa: E402
    rels = list(C.FROZEN) + list(C.CCHECK_FROZEN) + list(PRIMARY_PATH) + list(REDUCTION) + list(E165_OWN) + [PROV_REL]
    fails = []
    with tempfile.TemporaryDirectory(prefix="e165-pathcheck-") as td:
        for rel in rels:
            os.makedirs(os.path.dirname(os.path.join(td, rel)), exist_ok=True)
            shutil.copyfile(os.path.join(ROOT, rel), os.path.join(td, rel))
        b0 = check_pins(td, C.FROZEN, C.CCHECK_FROZEN)
        print(("ok   " if not b0 else "FAIL ") + f"the copy of the {len(rels)} pinned files passes checks 1-3 ({len(b0)} differ)")
        fails += b0
        tgt = os.path.join(td, "tools/claims-v3/e119/make_predictions_e119.py")
        with open(tgt, "r+b") as f:
            f.seek(-2, os.SEEK_END)
            c = f.read(1)
            f.seek(-2, os.SEEK_END)
            f.write(b"#" if c != b"#" else b" ")
        b1 = check_pins(td, C.FROZEN, C.CCHECK_FROZEN)
        want = [x for x in b1 if "make_predictions_e119.py" in x]
        good = len(b1) == 1 and len(want) == 1
        print(("ok   " if good else "FAIL ") + f"one byte of make_predictions_e119.py changed: refused at exactly that file ({len(b1)} lines: "
              + "; ".join(x[:110] for x in b1) + ")")
        if not good:
            fails.append("changed byte not refused as expected")
        os.remove(os.path.join(td, PROV_REL))
        b2 = check_pins(td, C.FROZEN, C.CCHECK_FROZEN)
        good = sum(1 for x in b2 if "provenance-blind7.json has None" in x) == len(PRIMARY_PATH)
        print(("ok   " if good else "FAIL ") + f"provenance-blind7.json missing: all {len(PRIMARY_PATH)} primary-path files refused on the cross-check")
        if not good:
            fails.append("missing provenance not refused")
    print("CHECK-PATH SELF-TEST:", "ALL PASS" if not fails else f"{len(fails)} FAIL")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv[1:] else main())
