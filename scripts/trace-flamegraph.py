#!/usr/bin/env python3
"""Device flame graph from a kernel's profile regions.

Input: the JSON lines traceprof_host writes (one per et_trace_user_profile_event: hart, cycle, insts,
region, start, func, name). Begin/end events are paired per hart into a stack of regions; each frame's
self time is its span minus its children's. Output: folded stacks (Brendan Gregg's format, one
"a;b;c value" line per stack) and a standalone SVG flame graph.

    trace-flamegraph.py events.jsonl --svg flame.svg [--folded out.folded] [--metric cycles|insts]
                        [--harts 0,2,4] [--per-hart]

Cycles come from hpmcounter3. On aifoundry2's card that counter reads 128 short when its low 7 bits are
0-10 (the carry into bit 7 lands late), so stamps are corrected the same way workloads/memprobe does.
Retired instructions (hpmcounter4/5) are summed over the 8 minions of a neighbourhood by the hardware,
so --metric insts only means something when one hart per neighbourhood runs.
"""
import argparse
import collections
import html
import json


def fixcyc(v):
    return v + 128 if (v & 0x7F) < 11 else v


def fold(events, metric, per_hart):
    """{stack tuple: self value} summed over harts (or keyed with the hart as the root frame)."""
    by_hart = collections.defaultdict(list)
    for e in events:
        by_hart[e["hart"]].append(e)
    folded = collections.Counter()
    problems = 0
    for hart, evs in sorted(by_hart.items()):
        stack = []  # [name, start value, children total]
        for e in evs:
            v = fixcyc(e["cycle"]) if metric == "cycles" else e["insts"]
            name = e["name"] or f"region{e['region']}"
            if e["start"]:
                stack.append([name, v, 0])
                continue
            if not stack or stack[-1][0] != name:
                problems += 1
                continue
            _, v0, children = stack.pop()
            span = v - v0
            path = tuple(([f"hart {hart}"] if per_hart else []) + [s[0] for s in stack] + [name])
            folded[path] += max(0, span - children)
            if stack:
                stack[-1][2] += span
        problems += len(stack)
    return folded, problems


PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#4a3aa7", "#008300", "#e34948"]


def svg(folded, metric, title):
    total = sum(folded.values())
    tree = {}
    for path, v in folded.items():
        node = tree
        for name in path:
            node = node.setdefault(name, {"_v": 0, "_c": {}})
            node["_v"] += v
            node = node["_c"]
    depth = max(len(p) for p in folded)
    W, row, pad, top = 1200, 22, 10, 46
    H = top + (depth + 1) * row + 30
    colors = {}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="system-ui,sans-serif" font-size="12">',
           "<style>text{fill:#0b0b0b}.bg{fill:#fcfcfb}.t{font-size:15px;font-weight:600}.s{fill:#52514e}"
           "@media(prefers-color-scheme:dark){.bg{fill:#1a1a19}.t,.s{fill:#fff}}</style>",
           f'<rect class="bg" width="{W}" height="{H}"/>',
           f'<text class="t" x="{pad}" y="22">{html.escape(title)}</text>',
           f'<text class="s" x="{pad}" y="38">{total:,} {metric} in all; width is time summed over harts; hover for numbers</text>']

    def draw(children, x, level, parent_w):
        for name, node in sorted(children.items(), key=lambda kv: -kv[1]["_v"]):
            w = node["_v"] / total * (W - 2 * pad)
            if w >= 0.5:
                y = H - 30 - (level + 1) * row
                c = colors.setdefault(name, PALETTE[len(colors) % len(PALETTE)])
                pct = 100 * node["_v"] / total
                out.append(f'<g><title>{html.escape(name)}: {node["_v"]:,} {metric} ({pct:.1f}%)</title>'
                           f'<rect x="{x:.1f}" y="{y}" width="{max(w - 1, 0.5):.1f}" height="{row - 2}" rx="3" fill="{c}"/>')
                if w > 60:
                    label = f"{name} {pct:.0f}%"
                    out.append(f'<text x="{x + 5:.1f}" y="{y + 14}" style="fill:#0b0b0b">{html.escape(label[:int(w / 7)])}</text>')
                out.append("</g>")
            draw(node["_c"], x, level + 1, w)
            x += w

    draw(tree, pad, 0, W - 2 * pad)
    out.append("</svg>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("events")
    ap.add_argument("--svg")
    ap.add_argument("--folded")
    ap.add_argument("--metric", choices=["cycles", "insts"], default="cycles")
    ap.add_argument("--harts", help="comma-separated hart ids to keep")
    ap.add_argument("--per-hart", action="store_true", help="one root frame per hart instead of summing harts")
    ap.add_argument("--title", default="Device flame graph")
    args = ap.parse_args()
    events = [json.loads(l) for l in open(args.events)]
    if args.harts:
        keep = {int(h) for h in args.harts.split(",")}
        events = [e for e in events if e["hart"] in keep]
    folded, problems = fold(events, args.metric, args.per_hart)
    if problems:
        print(f"warning: {problems} unmatched begin/end events (a hart's trace buffer wrapped?)")
    lines = [f"{';'.join(p)} {v}" for p, v in sorted(folded.items())]
    if args.folded:
        open(args.folded, "w").write("\n".join(lines) + "\n")
    if args.svg:
        open(args.svg, "w").write(svg(folded, args.metric, args.title))
    harts = len({e["hart"] for e in events})
    print(f"{len(events)} events from {harts} harts, {len(folded)} stacks")
    for p, v in sorted(folded.items(), key=lambda kv: -kv[1]):
        print(f"  {v / harts:12,.0f} {args.metric}/hart  {';'.join(p)}")


if __name__ == "__main__":
    main()
