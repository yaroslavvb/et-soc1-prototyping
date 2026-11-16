"""E194's firmware read on aifoundry2 card 0 (Sun 15 Nov 2026, Q187): parse the read's raw output and compare it, field by field, with
E69's read of record (Tue 27 Oct 2026 13:56:26 PDT), as the lab repo states it in two places that must agree:
  tools/claims-v3/knob/CHANGE-RECORD.md, the "Firmware identities, read fresh 13:56:26 PDT" item (lines 67-69), and
  docs/reports/data/2026-10-27-e69-governor-knob/README.md, "This card's firmware build" (lines 209-210).
E69's raw output was never committed (its README's dated note of 1 Nov 2026), so those two lines are the record.
Reads only. Writes nothing: prints the comparison (text, then one JSON line starting 'JSON '). Exit 0 if every field is EQUAL, 1 if any
field is DIFFERENT, 2 if the read or the record cannot be parsed.
Usage, from the lab repo's top:
  python3 -I docs/reports/data/2026-11-15-e194-fwread-aifoundry2/compare_fwread.py docs/reports/data/2026-11-15-e194-fwread-aifoundry2"""
import json
import re
import sys

FIELDS = [  # (the tool's own label, the short name used here)
    ("Firmware release revision", "release"),
    ("BL1 Firmware versions", "BL1"),
    ("BL2 Firmware versions", "BL2"),
    ("PMIC Firmware versions", "PMIC"),
    ("Master Minion Firmware versions", "Master Minion"),
    ("Worker Minion versions", "Worker Minion"),
    ("Machine Minion versions", "Machine Minion"),
]
CR = "tools/claims-v3/knob/CHANGE-RECORD.md"
RM = "docs/reports/data/2026-10-27-e69-governor-knob/README.md"


def die(msg):
    print("PARSE-FAILED: " + msg)
    sys.exit(2)


def read_this(d):
    raw = open(d + "/fwread.stdout", encoding="utf-8").read() + open(d + "/fwread.stderr", encoding="utf-8").read()
    text = re.sub(r"\x1b\[[0-9;]*m", "", raw)  # the tool's terminal colour codes
    n_cmd = len(re.findall(r"command: DM_CMD_GET_MODULE_FIRMWARE_REVISIONS code 14$", text, re.M))
    n_ok = len(re.findall(r"Service request succeeded$", text, re.M))
    vals, stamps = {}, {}
    for label, short in FIELDS:
        m = re.findall(r"^(\S+ \S+ \d+)\t.*\]: " + re.escape(label) + r": Major: (\d+) Minor: (\d+) Revision: (\d+)$", text, re.M)
        if len(m) != 1:
            die(f"this read: {len(m)} lines for '{label}' (want 1)")
        stamps[short] = m[0][0]
        vals[short] = ".".join(m[0][1:])
    return vals, stamps, n_cmd, n_ok


def lines(path, a, b):
    with open(path, encoding="utf-8") as f:
        ls = f.read().split("\n")
    return " ".join(x.strip() for x in ls[a - 1:b])


def read_e69(top):
    cr = lines(top + "/" + CR, 67, 69)
    m = re.search(r"Firmware identities, read fresh 13:56:26 PDT\*\* \(`DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`\): release \*\*(\d+\.\d+\.\d+)\*\*; "
                  r"BL1 \*\*(\d+\.\d+\.\d+)\*\*; BL2 \*\*(\d+\.\d+\.\d+)\*\*; PMIC \*\*(\d+\.\d+\.\d+)\*\*; Master / Worker / Machine Minion "
                  r"\*\*(\d+\.\d+\.\d+)\*\*", cr)
    if not m:
        die(CR + " lines 67-69 do not read as E69's firmware identities")
    a = {"release": m[1], "BL1": m[2], "BL2": m[3], "PMIC": m[4], "Master Minion": m[5], "Worker Minion": m[5], "Machine Minion": m[5]}
    rm = lines(top + "/" + RM, 209, 210)
    m = re.search(r"`DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`, read fresh at 13:56:26 PDT, reports release \*\*(\d+\.\d+\.\d+)\*\*, "
                  r"BL1 and BL2 \*\*(\d+\.\d+\.\d+)\*\*, PMIC (\d+\.\d+\.\d+), minions \*\*(\d+\.\d+\.\d+)\*\*", rm)
    if not m:
        die(RM + " lines 209-210 do not read as E69's firmware build")
    b = {"release": m[1], "BL1": m[2], "BL2": m[2], "PMIC": m[3], "Master Minion": m[4], "Worker Minion": m[4], "Machine Minion": m[4]}
    if a != b:
        die(f"E69's two statements disagree: {a} vs {b}")
    return a, cr, rm


def main():
    if len(sys.argv) != 2:
        die("usage: compare_fwread.py <this read's data directory, from the repo top>")
    d = sys.argv[1].rstrip("/")
    this, stamps, n_cmd, n_ok = read_this(d)
    e69, cr, rm = read_e69(".")
    rows, diff = [], []
    for _, short in FIELDS:
        v = "EQUAL" if this[short] == e69[short] else "DIFFERENT"
        rows.append({"field": short, "e69_2026_10_27": e69[short], "this_read_2026_11_15": this[short], "verdict": v})
        if v != "EQUAL":
            diff.append(short)
    print("E69's read of record (Tue 27 Oct 2026 13:56:26 PDT), from " + CR + " lines 67-69 and " + RM + " lines 209-210 (they agree)")
    print("this read (Sun 15 Nov 2026, aifoundry2 card 0): 'command: ... code 14' lines %d, 'Service request succeeded' lines %d" % (n_cmd, n_ok))
    print()
    print("%-15s %-24s %-24s %s" % ("field", "E69, 27 Oct 13:56:26 PDT", "this read, 15 Nov PST", "verdict"))
    for r in rows:
        print("%-15s %-24s %-24s %s" % (r["field"], r["e69_2026_10_27"], r["this_read_2026_11_15"], r["verdict"]))
    verdict = "EQUAL" if not diff and n_cmd == 1 and n_ok == 1 else ("DIFFERENT" if diff else "NOT READ")
    print()
    print("VERDICT: " + verdict + ("" if not diff else " (fields: " + ", ".join(diff) + ")"))
    print("JSON " + json.dumps({"verdict": verdict, "different_fields": diff, "rows": rows, "tool_stamps": stamps,
                                "command_lines": n_cmd, "succeeded_lines": n_ok,
                                "e69_sources": {CR: "lines 67-69", RM: "lines 209-210"}}, sort_keys=True))
    sys.exit(0 if verdict == "EQUAL" else 1)


main()
