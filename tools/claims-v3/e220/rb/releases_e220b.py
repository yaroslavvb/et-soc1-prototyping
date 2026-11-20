#!/usr/bin/env python3
"""E220 ARM B (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): THE RELEASE RECORDS IN THE REST RULE'S FORM, AND THEIR GUARD - E216's
copy-and-guard route for E212's release record (ready-e216's FINDING 1, Thu 19 Nov 2026: the round's W/out/orch/e212-releases.txt holds lines
naming 'aifoundry2 card 0' that E216's rest rule cannot read - E212's a2c0-S3 NOT RUN, the S3 re-run's CLAIM, and its RELEASE with no
'YYYY-MM-DD HH:MM:SS PST' day - so the rule printed REST UNREADABLE and step 7 would have stopped the day; ready-e216 routed around it with a copy
in the rule's form, scripts/make_releases_e216.py, and a guard, scripts/rel_guard_e216.sh) made a kit tool for every release record of the round.
The rest rule (rb/rest_rule_e220b.py, E216's unchanged) reads a release line only when it names 'aifoundry2 card 0', does not start with '#',
and carries its post's day ('YYYY-MM-DD HH:MM:SS PST') and its 'ended [cleanly] HH:MM:SS'. This tool writes, for each record W/out/orch/*releases*.txt,
a copy in which every line the rule would read stays as it is, every other line too, but for the lines naming 'aifoundry2 card 0':

  - a line the rule reads (not '#', its day and its end): kept as it is;
  - a '#' line (E221's record writes every line '#<post>') that carries a day and an end ('ended [cleanly] [at] HH:MM:SS'): kept as a comment and
    followed by ONE line in the rule's form with that line's own facts (its first word the record's name and the post, its day, 'ended HH:MM:SS'),
    so that the rule counts the session it records;
  - a line with an end but no day (E212's S3 re-run RELEASE, '16:25 #11.14.1 (16:23:38) RELEASE ... ended cleanly at 16:23:09'): kept as a comment and
    followed by the rule-form line E216's copy wrote for it - ONLY for that line, known by its sha256 (E216's c086b9eb copy; any other such line:
    UNCLASSIFIED);
  - (fix-e220, Fri 20 Nov 2026, before any E220 datum: verify-e220's F2 and the orchestrator's answer 2 in W/out/orch/e220-answers.txt) A SESSION
    END SAID WITHOUT ITS TIME - a line with the word RELEASE, released or ended but no 'ended [cleanly] [at] HH:MM:SS' (E221's release form:
    '#15.9.1 2026-11-20 10:55:47 PST: RELEASE aifoundry2 card 0: E221 a2c0-S1 ended (runner rc 0, ...)') - is NEVER a comment, whatever other
    words it holds: with its post's day and time ('YYYY-MM-DD HH:MM:SS PST') it is kept as a comment and followed by ONE line in the rule's form
    whose 'ended HH:MM:SS' is THE POST'S OWN TIME (at or after the session's true end, so the 40-minute rest the rule then requires from it is
    never shorter than the truth); with no day it is UNCLASSIFIED (exit 16: a person reads it). Checked before the no-end words below, so that a
    release line holding one of them (such as "is the lab's") is never read as a line with no session end;
  - a line with no session end - a CLAIM, a proposal, a session NOT RUN, an answer naming the card - (no 'ended' time, none of the words RELEASE,
    released or ended, and one of the words CLAIM, proposal, NOT RUN, names it, yes to, left to, is the lab's, offered): kept as a comment (the
    rule never reads it), and listed;
  - anything else naming 'aifoundry2 card 0': UNCLASSIFIED: the tool refuses (exit 16) and writes nothing: a person reads the line.

    /usr/bin/python3 -I -B tools/claims-v3/e220/rb/releases_e220b.py make <W/out/orch> <OUT dir>
        writes <OUT>/<record> for each record and <OUT>/MANIFEST-releases-e220b.json (each record's sha256, the sha256 of its lines naming
        aifoundry2, the copy's sha256, every converted and commented line); prints the RB_RELEASES value (the copies joined by ':') and
        "RELEASES-E220B: MADE <n> records (<k> lines naming aifoundry2 card 0: <r> read as they are, <e> session ends added in the rule's form
        (<p> of them at the post's own time), <c> comments: no session end)"; exit 0, 16 unclassified, 10 a usage error or an existing OUT
    /usr/bin/python3 -I -B tools/claims-v3/e220/rb/releases_e220b.py guard <W/out/orch> <OUT dir>
        THE GUARD (rows B, 7 and 9 of the card-lane brief): the round's records are still exactly the ones the copies were made from (the same
        files, each one's lines naming aifoundry2 at the sha256 the manifest holds) and every copy at its sha256: "REL-GUARD-E220B: AS READ ..."
        (exit 0), else "REL-GUARD-E220B: CHANGED: ...: do not go on (no step 7); make the copies again (the card lane's row B)" (exit 1)
Reads only the round's records; writes only OUT. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import os
import re
import sys

CARD = "aifoundry2 card 0"
REL_DAY = re.compile(r"\b(\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST\b")
REL_END = re.compile(r"\bended (?:cleanly )?(\d\d:\d\d:\d\d)\b")
END_ANY = re.compile(r"\bended (?:cleanly )?(?:at )?(\d\d:\d\d:\d\d)\b")
NO_END = ("CLAIM", "proposal", "NOT RUN", "names it", "yes to", "left to", "is the lab's", "offered", "the lab's freeze")
# fix-e220 (verify-e220's F2): a session's end said without its time ('RELEASE ... E221 a2c0-S1 ended (runner rc 0, ...)'): never a comment
SESSION_END_WORD = re.compile(r"\bRELEASE\b|\breleased\b|\bended\b")
# E212's S3 re-run RELEASE line (W/out/orch/e212-releases.txt line 14) and the rule-form line E216's copy (ready-e216's c086b9eb) added for it
E212_S3R_LINE_SHA = None            # filled from the line's own text below (the line as ready-e216 read it)
E212_S3R_HEAD = "16:25 #11.14.1 (16:23:38) RELEASE: aifoundry2 card 0 released at 16:24 PST: E212's S3 re-run ended cleanly at 16:23:09"
E212_S3R_ADD = ("a2c0-S3r aifoundry2 card 0 #11.14.1 2026-11-18 16:23:38 PST (released 16:24; session ended cleanly 16:23:09; 55 of 55 runs, "
                "23.0 card-minutes, runner rc 0, no stop: E212's S3 re-run, the round's line 14 above in the rest rule's form, written by ready-e216) "
                "~/claude/work/ee-1117-mmsweep2/sessions/1795046404-a2c0-S3/ (on aifoundry2)\n")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def card_lines(text):
    return [ln for ln in text.splitlines(keepends=True) if CARD in ln or "aifoundry2" in ln]


def classify(name, ln):
    """(kind, added line or None): kind 'read' | 'added' | 'added_post' (fix-e220: the end is the post's own time) | 'comment' | 'unclassified'
    for a line naming aifoundry2 card 0"""
    body = ln.lstrip()
    if not body.startswith("#") and REL_DAY.search(ln) and REL_END.search(ln):
        return "read", None
    if ln.startswith(E212_S3R_HEAD):
        return "added", E212_S3R_ADD
    m, e = REL_DAY.search(ln), END_ANY.search(ln)
    if body.startswith("#") and m and e:
        post = body.split()[0].lstrip("#") or "post"
        return "added", (f"{name.replace('-releases.txt', '')}-{post} {CARD} #{post} {m.group(1)} {m.group(2)} PST (session ended {e.group(1)}: "
                         f"the line above of {name} in the rest rule's form, written by releases_e220b.py)\n")
    if not e and SESSION_END_WORD.search(ln):
        # fix-e220 (verify-e220's F2): a session end with no 'ended HH:MM:SS': its post's own time is the end (never a comment); no day: refused
        if not m:
            return "unclassified", None
        post = body.split()[0].lstrip("#").rstrip(":") or "post"
        return "added_post", (f"{name.replace('-releases.txt', '')}-{post} {CARD} #{post} {m.group(1)} {m.group(2)} PST (session ended "
                              f"{m.group(2)}: THE POST'S OWN TIME, taken as the session's end because the line above of {name} gives no "
                              f"'ended HH:MM:SS' (fix-e220; the true end is at or before it, so the rest counted from it is never shorter); "
                              f"the line in the rest rule's form, written by releases_e220b.py)\n")
    if not END_ANY.search(ln) and any(w in ln for w in NO_END):
        return "comment", None
    return "unclassified", None


def make(orch, out):
    if os.path.exists(out):
        print(f"releases_e220b: {out} exists: nothing written (a new folder for each copy)")
        return 10
    recs = sorted(glob.glob(os.path.join(orch, "*releases*.txt")))
    if not recs:
        print(f"releases_e220b: no release record under {orch}")
        return 10
    man = {"what": "the round's release records in E220 arm B's rest rule's form (rb/releases_e220b.py make)", "orch": orch, "records": {}}
    copies, bad = {}, []
    n_k = n_r = n_e = n_c = n_p = 0
    for p in recs:
        name = os.path.basename(p)
        raw = open(p, "rb").read()
        text = raw.decode("utf-8")
        outl = [f"# releases_e220b.py (E220 arm B's kit): a copy of {name} (sha256 {sha(raw)}) in the rest rule's form; every line kept in order,\n",
                "# the lines naming aifoundry2 card 0 that the rule cannot read as comments, each session end they record added in the rule's form.\n"]
        conv = []
        for ln in text.splitlines(keepends=True):
            if CARD not in ln:
                outl.append(ln)
                continue
            n_k += 1
            kind, add = classify(name, ln)
            if kind == "read":
                n_r += 1
                outl.append(ln)
            elif kind in ("added", "added_post"):
                n_e += 1
                outl.append(ln if ln.lstrip().startswith("#") else "# " + ln)
                outl.append(add)
                if kind == "added_post":
                    n_p += 1
                    conv.append({"line": ln.strip()[:200], "added": add.strip(), "end_is_the_post_time": True})
                else:
                    conv.append({"line": ln.strip()[:200], "added": add.strip()})
            elif kind == "comment":
                n_c += 1
                outl.append(ln if ln.lstrip().startswith("#") else "# " + ln)
                conv.append({"line": ln.strip()[:200], "comment": "no session end (a claim, a proposal, a session not run or an answer)"})
            else:
                bad.append(f"{name}: {ln.strip()[:160]}")
        body = "".join(outl)
        copies[name] = body
        man["records"][name] = {"sha256": sha(raw), "aifoundry2_lines_sha256": sha("".join(card_lines(text)).encode()),
                                "copy_sha256": sha(body.encode()), "lines": len(text.splitlines()), "converted": conv}
    if bad:
        print("RELEASES-E220B: UNCLASSIFIED line(s) naming aifoundry2 card 0 (nothing written; a person reads them): " + " | ".join(bad))
        return 16
    os.makedirs(out)
    for name, body in copies.items():
        open(os.path.join(out, name), "x", encoding="utf-8").write(body)
    man["n_records"] = len(copies)
    json.dump(man, open(os.path.join(out, "MANIFEST-releases-e220b.json"), "x"), indent=1, sort_keys=True)
    print("RB_RELEASES=" + ":".join(os.path.join(out, n) for n in sorted(copies)))
    print(f"RELEASES-E220B: MADE {len(copies)} records ({n_k} lines naming {CARD}: {n_r} read as they are, {n_e} session ends added in the rule's "
          f"form ({n_p} of them at the post's own time), {n_c} comments: no session end)")
    return 0


def guard(orch, out):
    mp = os.path.join(out, "MANIFEST-releases-e220b.json")
    try:
        man = json.load(open(mp))
    except (OSError, ValueError):
        print(f"REL-GUARD-E220B: CHANGED: no manifest {mp}: do not go on (no step 7); make the copies again (the card lane's row B)")
        return 1
    bad = []
    now = sorted(os.path.basename(p) for p in glob.glob(os.path.join(orch, "*releases*.txt")))
    if now != sorted(man["records"]):
        bad.append(f"the records under {orch} are {now}, not the {sorted(man['records'])} the copies were made from")
    for name, r in man["records"].items():
        p = os.path.join(orch, name)
        if not os.path.exists(p):
            continue
        a2 = sha("".join(card_lines(open(p, encoding="utf-8").read())).encode())
        if a2 != r["aifoundry2_lines_sha256"]:
            bad.append(f"{name}: its lines naming aifoundry2 changed (sha256 {a2[:12]}, the copy's {r['aifoundry2_lines_sha256'][:12]})")
        c = os.path.join(out, name)
        if not os.path.exists(c) or sha(open(c, "rb").read()) != r["copy_sha256"]:
            bad.append(f"the copy of {name} is not at its sha256")
    if bad:
        print("REL-GUARD-E220B: CHANGED: " + "; ".join(bad) + ": do not go on (no step 7); make the copies again (the card lane's row B)")
        return 1
    print(f"REL-GUARD-E220B: AS READ ({len(man['records'])} records; the round's records hold what the copies were made from)")
    return 0


def main(a):
    if len(a) == 3 and a[0] == "make":
        return make(os.path.abspath(a[1]), os.path.abspath(a[2]))
    if len(a) == 3 and a[0] == "guard":
        return guard(os.path.abspath(a[1]), os.path.abspath(a[2]))
    print(__doc__)
    return 10


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
