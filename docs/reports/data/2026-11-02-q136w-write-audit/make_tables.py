#!/usr/bin/env python3
"""Q136(w): the Markdown tables of this directory's README, from the audit table and the inventory.

    python3 docs/reports/data/2026-11-02-q136w-write-audit/make_tables.py > docs/reports/data/2026-11-02-q136w-write-audit/tables.md

Reads tools/claims-v3/dmcmd_table.json (every command at et-platform 836a4ab, classified from source), inventory.json
(dmcmd_audit.py run over every tracked code file under tools/, scripts/ and workloads/, scanned-files.txt) and
inventory-docs.json (the same over the code kept with the records under docs/, docs-scanned-files.txt). Stdlib only.
Corrected after verification, Mon 2 Nov 2026: the forms of SET_STATS_RUN_CONTROL, sections E and F."""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
T = json.loads((REPO / "tools/claims-v3/dmcmd_table.json").read_text())
INV = json.loads((HERE / "inventory.json").read_text())
DOCS = json.loads((HERE / "inventory-docs.json").read_text())

sites = collections.defaultdict(list)
for r in INV["records"]:
    if r["line"]:  # line 0 = a reviewed source taken from the table, not a send site
        sites[r["command"]].append(r)


def where(cmd, k=4):
    files = collections.Counter(r["file"] for r in sites.get(cmd, []))
    shown = [f"`{f}`" + (f" ×{n}" if n > 1 else "") for f, n in files.most_common(k)]
    more = len(files) - k
    return ", ".join(shown) + (f" and {more} more" if more > 0 else "") if files else "none"


print("## A. Every command the lab's code can send, classified from et-platform `836a4ab` (BL2 0.22.0)\n")
print("Handler paths are under `device-bootloaders/src/ServiceProcessorBL2/`. *Sites* counts the lines in this repository's "
      "tracked code that can send the command (inventory.json); *where* names the files with the most.\n")
print("| Id | Command | Class | PMIC | Handler at `836a4ab` | Side effects | Sites | Where |")
print("|---|---|---|---|---|---|---|---|")
forms_of = collections.defaultdict(list)
for f, c in T.get("forms", {}).items():
    forms_of[c["of"]].append(f)
lab = {n: c for n, c in T["commands"].items() if c.get("lab_sends") or sites.get(n) or
       any(sites.get(f) for f in forms_of[n])}
for n, c in sorted(lab.items(), key=lambda kv: (kv[1]["class"] != "WRITE", kv[1]["class"], kv[1]["id"])):
    pm = c.get("pmic", "none") + (f" ({c['pmic_reads']} register reads)" if c.get("pmic_reads") else "")
    se = "; ".join(c.get("side_effects", [])) or "-"
    nsites = len(sites.get(n, [])) + sum(len(sites.get(f, [])) for f in forms_of[n])
    wh = where(n) if sites.get(n) else "; ".join(f"`{f}`: {where(f)}" for f in forms_of[n] if sites.get(f)) or "none"
    print(f"| {c['id']} | `{n}` | **{c['class']}** | {pm} | {c['handler']} | {se} | {nsites} | {wh} |")
for n, c in T["pseudo"].items():
    if sites.get(n):
        print(f"| - | `{n}` (no DM command) | **{c['class']}** | {c.get('pmic', 'none')} | {c['what']} | - | "
              f"{len(sites[n])} | {where(n)} |")

print("\n## A2. The forms of `SET_STATS_RUN_CONTROL` (62): only `STATS_RESET` is the ruled statistics reset\n")
print("| Form | Type, control | Sent by | What it writes | PMIC | Sites | Where |")
print("|---|---|---|---|---|---|---|")
for f, c in T.get("forms", {}).items():
    print(f"| `{f}` | {c['type']}, {c['control']} | {c['sent_by']} | {c['what']} | {c['pmic']} | {len(sites.get(f, []))} | "
          f"{where(f)} |")
print(f"| `SET_STATS_RUN_CONTROL` (form not visible) | - | the command's name in code, -o 62, a raw client's 62 | never allowed | - | "
      f"{len(sites.get('SET_STATS_RUN_CONTROL', []))} | {where('SET_STATS_RUN_CONTROL')} |")

print("\n## B. The ettelem variants: what each subcommand sends\n")
print("| Variant (source) | Subcommand | Sends | Source lines | Note |")
print("|---|---|---|---|---|")
for v, info in T["tools"]["variants"].items():
    print(f"| `{v}` | *build directories* | {', '.join('`' + b + '`' for b in info['build_dirs'])} | | "
          f"{info.get('build_dirs_note', '')} |")
    for sub, sc in info["subcommands"].items():
        sends = ", ".join(f"`{x}`" for x in sc["sends"]) or "nothing"
        if sc.get("reset_sends"):
            sends += (f"; with {' or '.join('`' + o + '`' for o in sc['reset_options'])}: "
                      + ", ".join(f"`{x}`" for x in sc["reset_sends"]))
        print(f"| `{v}` (`{info['source']}`) | `{sub}` | {sends} | {sc.get('lines', '')} | {sc.get('note', '')} |")

print("\n## C. Every write site in the lab's code\n")
print("| Command | Class | Site | Detail |")
print("|---|---|---|---|")
for n in sorted(sites):
    e = T["commands"].get(n) or T.get("forms", {}).get(n) or T["pseudo"].get(n) or {}
    if e.get("class") not in ("WRITE", "UNCLASSIFIED", "UNSUPPORTED") or n in ("VARIANT_UNRESOLVED",
                                                                            "UNREVIEWED_VARIANT", "UNKNOWN_SUBCOMMAND"):
        continue
    for r in sorted(sites[n], key=lambda r: (r["file"], r["line"])):
        print(f"| `{n}` | {e.get('class')} | `{r['file']}:{r['line']}` | {r['tool']}{'; ' + r['detail'] if r['detail'] else ''} |")

print("\n## D. Reads with a side effect that blocks a launch\n")
print("| Site | Command | Tag | Detail |")
print("|---|---|---|---|")
for r in sorted(INV["records"], key=lambda r: (r["file"], r["line"])):
    if r["tags"] and r["line"]:
        print(f"| `{r['file']}:{r['line']}` | `{r['command']}` | {', '.join(r['tags'])} | {r['detail']} |")

print("\n## E. ettelem calls whose build the checker cannot see, and wrappers a person reads\n")
print("A binary chosen at run time (a protocol's or a host config's path, an environment variable) is `VARIANT_UNRESOLVED`, "
      "NO-GO until the runner names its source with `--variant-source` (the source's sha256 must equal a reviewed "
      "variant's); a line that forwards its arguments (`\"$@\"`, `*args`) or takes the command from a variable is a "
      "`WRAPPER` for a person to read, and its calls in the same file are classified through it.\n")
print("| Site | Tag | Detail |")
print("|---|---|---|")
for r in sorted(INV["records"], key=lambda r: (r["file"], r["line"])):
    if r["line"] and r["command"] in ("VARIANT_UNRESOLVED", "UNREVIEWED_VARIANT", "UNKNOWN_SUBCOMMAND", "WRAPPER"):
        print(f"| `{r['file']}:{r['line']}` | `{r['command']}` | {r['tool']}; {r['detail']} |")

print("\n## F. Code kept with the records under docs/ (copies of what ran, page tools, desk scripts)\n")
print(f"`dmcmd_audit.py` over the {len(DOCS['files'])} tracked code files under `docs/` (docs-scanned-files.txt, inventory-docs.json). "
      "These are records, not runners: a run's generated scripts as they ran, a page's example tools, and desk scripts "
      "that name commands in strings. *Sends* marks the files that run something.\n")
print("| File | Commands | Sends |")
print("|---|---|---|")
dfiles = collections.defaultdict(set)
for r in DOCS["records"]:
    dfiles[r["file"]].add(r["command"])
names_only = {"docs/reports/data/2026-09-30-without-heatsink/lowclock_calc.py",
              "docs/reports/data/2026-10-31-e85-camera-kinds/corrections-check.py",
              "docs/reports/data/2026-11-01-e113-a-side-saturation/corrections-check.py",
              "docs/reports/data/2026-11-01-e114-card0-replicates/corrections-check.py",
              "docs/reports/data/2026-10-31-e83-kinds-speed-rest/corrections-check.py",
              "docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/corrections-check.py",
              "docs/reports/sources/dvfs-leakage.script.js", "docs/reports/sources/power-temperature.script.js"}
for f in sorted(dfiles):
    sends = "no: names the commands in strings (read by hand)" if f in names_only else "yes"
    print(f"| `{f}` | {', '.join('`' + c + '`' for c in sorted(dfiles[f]))} | {sends} |")
lab_cmds = {r["command"] for r in INV["records"]}
extra = sorted({c for f in dfiles if f not in names_only for c in dfiles[f]} - lab_cmds)
print(f"\n*The files that send use no command outside those the lab's runners send{': ' + ', '.join(extra) if extra else ''}.*")

counts = collections.Counter(c["class"] for c in T["commands"].values())
print(f"\n*Table: {len(T['commands'])} commands ({', '.join(f'{k} {v}' for k, v in sorted(counts.items()))}); "
      f"inventory: {len(INV['files'])} files scanned, {len({r['file'] for r in INV['records']})} with a send site, "
      f"{len(INV['records'])} records ({sum(1 for r in INV['records'] if r['line'])} at a line, the rest from reviewed "
      f"sources taken from the table); docs/: {len(DOCS['files'])} files, {len(dfiles)} with a record.*")
