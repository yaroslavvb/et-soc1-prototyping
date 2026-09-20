# pmcsel: test for the counter-configure syscall

`patches/0003-pmc-configure-syscall-353f20e.patch` adds a U-mode syscall to the minion firmware that lets a kernel
choose what `hpmcounter4-8`, the shire-cache monitors and the memory-shire monitors count (they are M-mode only
otherwise). This workload checks it. It needs no card: the simulator loads firmware ELFs directly.

```bash
# build the firmware with the patch applied (see patches/README.md), then:
cmake -S workloads/pmcsel -B build/pmcsel -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/pmcsel -j4
build/pmcsel/host/pmcsel_host --sysemu                                   # stock firmware: rc -1, hpm6_delta 0
build/pmcsel/host/pmcsel_host --sysemu --fw-dir $PWD/build/fw-build      # patched: rc 0, hpm6 counts instructions
```

Measured in `sys_emu` on 2026-09-20: stock firmware returns -1 for every call and `hpmcounter6` stays 0; the patched
firmware returns 0, refuses `mhpmevent3` (the cycle counter must stay a cycle counter), and `hpmcounter6` counts 80,006
retired instructions against `hpmcounter4`'s 80,007. `sys_emu` models only the cycle and retired-instruction events,
so other events can only be checked on a card running the patched firmware.
