# traceprof: a device flame graph

A kernel wraps its phases in profile regions (`et_trace_user_profile_event`), the host launches it with user
tracing on and decodes the trace buffer, and `scripts/trace-flamegraph.py` turns the events into folded stacks and
an SVG flame graph in minion cycles.

```bash
cmake -S workloads/traceprof -B build/traceprof -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/traceprof -j4
cd build/traceprof-data
timeout 10 ../traceprof/host/traceprof_host --shires 0x1 --reps 4 --out events.jsonl     # 512 events in 2.6 ms of kernel time (1.57 M cycles)
python3 ../../scripts/trace-flamegraph.py events.jsonl --svg flame.svg --folded flame.folded \
    --title "traceprof on aifoundry2: 32 harts of shire 0, cycles"
```

The committed run is in `docs/reports/data/2026-09-20-traceprof-aifoundry2/`; the second command, run on its
`events.jsonl`, reproduces its `flame.svg` and `flame.folded` byte for byte.

Things to know:
- Each hart gets 4 KB of trace buffer, about 85 profile events; a full buffer wraps silently, and the converter
  reports unmatched begin/end events when that happens.
- Every event carries a cycle stamp (`hpmcounter3`, corrected for the late bit-7 carry) and a retired-instruction
  count. The instruction counters are summed over the 8 minions of a neighbourhood by the hardware.
- The string pointers in the events are device addresses. The runtime copies the whole ELF file to the load
  address, so pointer minus load address is an offset into the ELF file; the host resolves names that way.
- The minion has no 64-bit integer-to-float conversion: `fcvt.s.lu` traps with cause 30. Use 32-bit counters in
  floating-point loops.
