#!/bin/bash
# v31-trace (Q217), run ON aifoundry3: remove run t1's host stderr log (85 MB of per-poll INFO lines; its size, counts and first and last
# 40 lines are kept on the desk in traces/runs/t1-gemmL-2x4x16-0xf/err.excerpt.txt), by its literal path.
rm -f ~/claude/work/q217-v31-trace/runs/t1-gemmL-2x4x16-0xf/err.log
du -sh ~/claude/work/q217-v31-trace/runs/t1-gemmL-2x4x16-0xf
