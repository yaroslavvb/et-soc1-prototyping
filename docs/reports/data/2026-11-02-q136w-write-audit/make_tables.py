#!/usr/bin/env python3
"""Q136(w): the Markdown tables of this directory's README, from the audit table and the inventory.

    python3 docs/reports/data/2026-11-02-q136w-write-audit/make_tables.py > docs/reports/data/2026-11-02-q136w-write-audit/tables.md

Reads tools/claims-v3/dmcmd_table.json (every command at et-platform 836a4ab, classified from source) and inventory.json
(dmcmd_audit.py run over every tracked code file under tools/, scripts/ and workloads/, scanned-files.txt). Stdlib only."""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
T = json.loads((REPO / "tools/claims-v3/dmcmd_table.json").read_text())
INV = json.loads((HERE / "inventory.json").read_text())

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
lab = {n: c for n, c in T["commands"].items() if c.get("lab_sends") or sites.get(n)}
for n, c in sorted(lab.items(), key=lambda kv: (kv[1]["class"] != "WRITE", kv[1]["class"], kv[1]["id"])):
    pm = c.get("pmic", "none") + (f" ({c['pmic_reads']} register reads)" if c.get("pmic_reads") else "")
    se = "; ".join(c.get("side_effects", [])) or "-"
    print(f"| {c['id']} | `{n}` | **{c['class']}** | {pm} | {c['handler']} | {se} | {len(sites.get(n, []))} | {where(n)} |")
for n, c in T["pseudo"].items():
    if sites.get(n):
        print(f"| - | `{n}` (no DM command) | **{c['class']}** | {c.get('pmic', 'none')} | {c['what']} | - | "
              f"{len(sites[n])} | {where(n)} |")

print("\n## B. The ettelem variants: what each subcommand sends\n")
print("| Variant (source) | Subcommand | Sends | Source lines | Note |")
print("|---|---|---|---|---|")
for v, info in T["tools"]["variants"].items():
    for sub, sc in info["subcommands"].items():
        sends = ", ".join(f"`{x}`" for x in sc["sends"]) or "nothing"
        if sc.get("reset_sends"):
            sends += f"; with {' or '.join('`' + o + '`' for o in sc['reset_options'])}: `SET_STATS_RUN_CONTROL`"
        print(f"| `{v}` (`{info['source']}`) | `{sub}` | {sends} | {sc.get('lines', '')} | {sc.get('note', '')} |")

print("\n## C. Every write site in the lab's code\n")
print("| Command | Class | Site | Detail |")
print("|---|---|---|---|")
for n in sorted(sites):
    e = T["commands"].get(n) or T["pseudo"].get(n) or {}
    if e.get("class") not in ("WRITE", "UNCLASSIFIED", "UNSUPPORTED"):
        continue
    for r in sorted(sites[n], key=lambda r: (r["file"], r["line"])):
        print(f"| `{n}` | {e.get('class')} | `{r['file']}:{r['line']}` | {r['tool']}{'; ' + r['detail'] if r['detail'] else ''} |")

print("\n## D. Reads with a side effect that blocks a launch\n")
print("| Site | Command | Tag | Detail |")
print("|---|---|---|---|")
for r in sorted(INV["records"], key=lambda r: (r["file"], r["line"])):
    if r["tags"] and r["line"]:
        print(f"| `{r['file']}:{r['line']}` | `{r['command']}` | {', '.join(r['tags'])} | {r['detail']} |")

counts = collections.Counter(c["class"] for c in T["commands"].values())
print(f"\n*Table: {len(T['commands'])} commands ({', '.join(f'{k} {v}' for k, v in sorted(counts.items()))}); "
      f"inventory: {len(INV['files'])} files scanned, {len({r['file'] for r in INV['records']})} with a send site, "
      f"{len(INV['records'])} records.*")
