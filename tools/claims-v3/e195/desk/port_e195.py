#!/usr/bin/env python3
"""E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): the two ports of the session's chain, made from their
sources by EXACT REPLACEMENTS, each applied exactly once, and nothing else (E191's kit note 2's way for its runner v2):

  tools/claims-v3/runitems.py                        -> tools/claims-v3/e195/runitems_e195.py   (4 replacements)
  tools/claims-v3/e195/proposal/src/block_x09.sh     -> tools/claims-v3/e195/block_e195.sh      (9 replacements)

    python3 -I -B port_e195.py --make     write both ports from their sources (the kit's own step)
    python3 -I -B port_e195.py --check    re-make both in memory: each equal byte for byte to the committed port: PORT CHECK PASS
    python3 -I -B port_e195.py --diff     print each replacement (old, then new)

The generator refuses (exit 3) if a source is not at the sha256 below or an "old" text does not occur exactly once. Why each change is
made is in KIT.md section 1; in short:
  runitems_e195.py: the host's record read from a source no runtime print can split (CONTEXT section 116; E195.md section 4): the one
    runtime line the lab has ever seen on a host's standard output, "Opening device <n>" with its newline (E191 kit note 2's
    RUNTIME_LINE; aifoundry1's runtime prints it when ET_DEVICES is set), is removed wherever it fell, before the lines are read; every
    other byte is read as runitems.py reads it (an unknown text inside a record still fails the parse and ends the pass: never a wrong
    datum); a dropped line is logged in run.log; no record changes.
  block_e195.sh: block_x09.sh beside the registered source (proposal/src) instead of at tools/claims-v3/x09/; lib_e195.sh sourced after
    lib_x09.sh (no SIGKILL of a sampler: E195.md section 10); runitems_e195.py in place of runitems.py (the preflight, the listing, the
    run, code.sha256); code.sha256 also names the kit's own *_e195.* files; and the signal path keeps the card lock until no device
    process of ours runs (E195.md section 10), never killing one.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E = "tools/claims-v3/e195"

RUNITEMS_SRC = ("tools/claims-v3/runitems.py", "8293b5a0fbf72b68cb2d1ded35fa520711f0bd404246ac36874d8922cb137735")
BLOCK_SRC = (E + "/proposal/src/block_x09.sh", "494f262480e14b6b2cafc2624a8dcd718335ef3919e58fd373996324c4759245")

R_RUNITEMS = [
    ('"""A manifest-driven runner for version-3 blocks whose items need their own device-tool arguments.\n',
     '"""E195\'s kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): tools/claims-v3/runitems.py with four exact\n'
     'replacements, each applied once (desk/port_e195.py), and nothing else: THE HOST\'S RECORD READ FROM A SOURCE NO RUNTIME PRINT CAN\n'
     'SPLIT (CONTEXT section 116\'s lesson; E195.md section 4\'s record-reading rule). The one runtime line the lab has ever seen on a\n'
     'host\'s standard output, the exact text "Opening device <n>" with its newline (E191\'s kit note 2, RUNTIME_LINE: aifoundry1\'s\n'
     'runtime prints it when ET_DEVICES is set), is removed wherever it fell (at a line\'s start or inside a record line) before the\n'
     'lines are read; a JSON line holds no raw newline, so the removal never cuts into the host\'s own text. Every other byte is read\n'
     'exactly as runitems.py reads it: an unknown text inside a record still fails the parse and ends the pass (never a wrong datum).\n'
     'A dropped line is logged in run.log (one line naming the item and the text); no record, mark or exit code changes.\n'
     '\n'
     'runitems.py\'s docstring follows, unchanged:\n'
     '\n'
     'A manifest-driven runner for version-3 blocks whose items need their own device-tool arguments.\n'),
    ("import random\nimport subprocess\n",
     "import random\nimport re\nimport subprocess\n"),
    ("def others_on_card(dev_n):\n",
     'RUNTIME_LINE = re.compile(r"Opening device [0-9]+\\n")   # E195 kit: aifoundry1\'s runtime line (E191 kit note 2)\n'
     "\n"
     "\n"
     "def drop_runtime(text):\n"
     '    """E195 kit: the host\'s stdout with every runtime line removed, wherever it fell, and the lines removed."""\n'
     "    return RUNTIME_LINE.sub(\"\", text), RUNTIME_LINE.findall(text)\n"
     "\n"
     "\n"
     "def others_on_card(dev_n):\n"),
    ("                n = 0\n                for line in r.stdout.splitlines():\n",
     "                n = 0\n"
     "                kept, dropped = drop_runtime(r.stdout or \"\")   # E195 kit: the record read whole\n"
     "                if dropped:\n"
     "                    say(f\"block {blk} {it['name']}: {len(dropped)} runtime line(s) dropped from the host's stdout: \"\n"
     "                        + \"; \".join(sorted(set(d.strip() for d in dropped))))\n"
     "                for line in kept.splitlines():\n"),
]

R_BLOCK = [
    ("#!/usr/bin/env bash\n",
     "#!/usr/bin/env bash\n"
     "# E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): one pass of E195 (one lib.sh block), the registered\n"
     "# proposal/src/block_x09.sh PORTED by nine exact replacements, each applied once (desk/port_e195.py), and nothing else:\n"
     "#   1. this header;  2. X9, the registered source beside this file (proposal/src);\n"
     "#   3. lib_x09.sh sourced from X9, and lib_e195.sh right after it: no SIGKILL of a sampler that ignores SIGTERM (it is left to end at\n"
     "#      its own --seconds bound, the session stops), no second sampler beside a stuck one, no management read beside it (E195.md 10);\n"
     "#   4. the preflight's file check names runitems_e195.py (runitems.py with the record read whole: E195.md section 4);\n"
     "#   5. the build hint names X9;  6. the listing runs runitems_e195.py;\n"
     "#   7. code.sha256 names runitems_e195.py, the registered source at proposal/src and the kit's own *_e195.* files;\n"
     "#   8. a signal to the block writes this pass's STOP and the session's stop file and lets runitems and its device process end by\n"
     "#      themselves (lib_e195.sh's x9k_on_signal: at most 180 s; the registered SIGTERM to runitems would end a running host by SIGPIPE),\n"
     "#      then keeps the card lock until no device process of ours runs, never killing one (E195.md section 10);  9. the run: runitems_e195.\n"
     "# The approach, the anchor, the shuffle, the records and the stops are runitems.py's, the sampler and the lock lib.sh's, unchanged.\n"
     "# Run only by session_e195.sh (or by hand: X9_ROOT=<E195's root> [V3_DRY=1] bash tools/claims-v3/e195/block_e195.sh <pass> [items]).\n"
     "# block_x09.sh's words follow (its paths are the ones it had at tools/claims-v3/x09/):\n"),
    ('HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)\n',
     'HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)\n'
     'X9=$HERE/proposal/src      # E195 kit: the registered source, byte for byte, beside this port\n'),
    ('. "$HERE/lib_x09.sh"       # ETTELEM = the guard, no drain; X9_ROOT = V3_ROOT; USER = this login; others_present\n',
     '. "$X9/lib_x09.sh"         # ETTELEM = the guard, no drain; X9_ROOT = V3_ROOT; USER = this login; others_present\n'
     '. "$HERE/lib_e195.sh"      # E195 kit: no SIGKILL of a sampler, no second sampler, no management read beside a stuck one\n'),
    ("for f in tools/claims-v3/runitems.py tools/claims-v3/text_hash.sh; do",
     "for f in tools/claims-v3/e195/runitems_e195.py tools/claims-v3/text_hash.sh; do"),
    ('[ -x "$HOST" ] || pf+=("missing $HOST (cmake -S $HERE -B build/x09mem -DCMAKE_PREFIX_PATH=/opt/et)")',
     '[ -x "$HOST" ] || pf+=("missing $HOST (cmake -S $X9 -B build/x09mem -DCMAKE_PREFIX_PATH=/opt/et)")'),
    ("LIST=$(python3 tools/claims-v3/runitems.py /dev/null",
     "LIST=$(python3 tools/claims-v3/e195/runitems_e195.py /dev/null"),
    ('{ sha256sum tools/claims-v3/lib.sh tools/claims-v3/runitems.py tools/claims-v3/text_hash.sh "$ETTELEM" \\\n'
     '    "$HERE"/*.* "$HERE"/host/* "$HERE"/kernel/* "$GEN/manifest.json" "$GEN/counts.json" \\\n',
     '{ sha256sum tools/claims-v3/lib.sh tools/claims-v3/e195/runitems_e195.py tools/claims-v3/text_hash.sh "$ETTELEM" \\\n'
     '    "$X9"/*.* "$X9"/host/* "$X9"/kernel/* "$HERE"/*_e195.* "$GEN/manifest.json" "$GEN/counts.json" \\\n'),
    ('on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }\n',
     'on_signal() { x9k_on_signal; }   # E195 kit (lib_e195.sh): the stop files first; runitems and its device process end by themselves\n'),
]
R_BLOCK.append(('python3 tools/claims-v3/runitems.py "$OUT" --root "$V3_ROOT"',
                'python3 tools/claims-v3/e195/runitems_e195.py "$OUT" --root "$V3_ROOT"'))   # 9, in the file's order

PORTS = [(RUNITEMS_SRC, E + "/runitems_e195.py", R_RUNITEMS), (BLOCK_SRC, E + "/block_e195.sh", R_BLOCK)]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def make(src, reps):
    path, want = src
    with open(os.path.join(REPO, path), "rb") as f:
        b = f.read()
    if sha(b) != want:
        raise SystemExit(f"PORT REFUSED: {path} is {sha(b)}, not the source {want}")
    t = b.decode()
    for i, (old, new) in enumerate(reps, 1):
        n = t.count(old)
        if n != 1:
            raise SystemExit(f"PORT REFUSED: {path} replacement {i}: the old text occurs {n} times, not once: {old[:80]!r}")
        t = t.replace(old, new, 1)
    return t.encode()


def main(argv):
    if argv not in (["--make"], ["--check"], ["--diff"]):
        print(__doc__)
        return 2
    bad = 0
    for src, dst, reps in PORTS:
        out = make(src, reps)
        q = os.path.join(REPO, dst)
        if argv == ["--make"]:
            with open(q, "wb") as f:
                f.write(out)
            os.chmod(q, 0o644)
            print(f"written {dst}: {len(reps)} replacements on {src[0]} ({len(out)} B, sha256 {sha(out)})")
        elif argv == ["--diff"]:
            print(f"== {dst} from {src[0]} (sha256 {src[1]}): {len(reps)} replacements")
            for i, (old, new) in enumerate(reps, 1):
                print(f"-- {i} old:\n{old}-- {i} new:\n{new}")
        else:
            have = open(q, "rb").read() if os.path.exists(q) else b""
            ok = have == out
            bad += not ok
            print(f"{'SAME' if ok else 'DIFFERS'} {dst}: {len(reps)} exact replacements on {src[0]} (sha256 {sha(out)})")
    if argv == ["--check"]:
        print("PORT CHECK " + ("PASS: both ports are their sources with the listed replacements, byte for byte" if not bad else "FAIL"))
        return 3 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
