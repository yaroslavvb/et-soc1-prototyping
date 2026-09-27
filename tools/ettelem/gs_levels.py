"""E48's gathers and scatters arranged by memory level: one list that every page renders from (the energy manual's
sections 3.1, 4.3, 4.4 and 6 through render_catalogue.py and render_energy_manual.py, the hub's events through
sync_hub_data.py, the memory-hierarchy page through workloads/memhier/analyze.py, the influence page through
make_analysis.py), so the rows and their labels are the same everywhere.

A configuration's name is tools/claims-v3/gs's: gs/<set>/<op>/<table>/<pattern>/<data>/h<harts>/m<mask>/n<minions>,
every field always present; the values are manual.json gs.configs[<name>] (build_energy_manual.py gs_block()).
"random" is random lines within 4 KB tiles (manual.json gs.random), never uniform random addresses.
"""


def cfg(op, table, pattern="rand", data="random", harts=2, mask="ff", minions="1024", s="E"):
    return f"gs/{s}/{op}/{table}/{pattern}/{data}/h{harts}/m{mask}/n{minions}"


# (key, label, the table per hart, the contiguous row it is set against, {column: (op, table)})
# columns: gather (fgw.ps through the L1), gather_lg (fgwl.ps to the shire's L2 or fgwg.ps to the home, skipping the
# L1), scatter (fscw.ps), scatter_lg (fscwl.ps / fscwg.ps), load (scalar flw on the same 64 offsets), store (fsw),
# block (fg32w.ps: one 32 B block per instruction, lanes permuted), upd (gather + fadd.ps + scatter, per update).
# stream: the energy manual's contiguous path for the same level, (source, key): "cat" a catalogue entry per byte
# (flw.ps per instruction / 32), "lv" reruns.json levels_pj_per_byte, "lvc" levels_by_contents_pj_per_byte random.
LEVELS = [
    ("l1", "L1", "512 B per hart (the hart's whole L1)", ("cat", "flw.ps/random/h2"),
     {"gather": ("fgw.ps", "dram-512B"), "scatter": ("fscw.ps", "dram-512B"), "load": ("flw", "dram-512B"),
      "store": ("fsw", "dram-512B"), "block": ("fg32w.ps", "dram-512B"), "upd": ("upd", "dram-512B")}),
    ("l2", "L2", "4 KB per hart, 256 KB per shire (half the L2)", ("lv", "l2"),
     {"gather": ("fgw.ps", "dram-4K"), "gather_lg": ("fgwl.ps", "dram-4K"), "scatter": ("fscw.ps", "dram-4K"),
      "scatter_lg": ("fscwl.ps", "dram-4K"), "load": ("flw", "dram-4K"), "store": ("fsw", "dram-4K"),
      "block": ("fg32w.ps", "dram-4K"), "upd": ("upd", "dram-4K")}),
    ("scp", "own scratchpad", "16 KB per hart of the shire's own scratchpad", ("lvc", "scp-local"),
     {"gather": ("fgw.ps", "scp-16K"), "gather_lg": ("fgwl.ps", "scp-16K"), "scatter": ("fscw.ps", "scp-16K"),
      "scatter_lg": ("fscwl.ps", "scp-16K"), "load": ("flw", "scp-16K"), "store": ("fsw", "scp-16K"),
      "block": ("fg32w.ps", "scp-16K"), "upd": ("upd", "scp-16K")}),
    ("mix", "L2 and L3", "16 KB per hart, 1 MB per shire (32 MB in all)", None,
     {"gather": ("fgw.ps", "dram-16K"), "scatter": ("fscw.ps", "dram-16K")}),
    ("l3", "L3", "4 KB per hart, read past the L1 and L2 at the line's home slice", ("lv", "l3"),
     {"gather_lg": ("fgwg.ps", "dram-4K"), "scatter_lg": ("fscwg.ps", "dram-4K")}),
    ("rscp", "remote scratchpad", "16 KB per hart of a scratchpad 2 mesh hops away", ("lvc", "scp-remote"),
     {"gather": ("fgw.ps", "rscp-16K"), "gather_lg": ("fgwg.ps", "rscp-16K"), "scatter": ("fscw.ps", "rscp-16K"),
      "scatter_lg": ("fscwg.ps", "rscp-16K")}),
    ("edge", "L3 and DRAM", "64 KB per hart (128 MB in all)", None,
     {"gather": ("fgw.ps", "dram-64K")}),
    ("dram", "DRAM", "256 KB per hart (512 MB in all)", ("cat", "tload/dram/random"),
     {"gather": ("fgw.ps", "dram-256K"), "gather_lg": ("fgwg.ps", "dram-256K"), "scatter": ("fscw.ps", "dram-256K"),
      "scatter_lg": ("fscwg.ps", "dram-256K"), "load": ("flw", "dram-256K"), "block": ("fg32w.ps", "dram-256K"),
      "upd": ("upd", "dram-256K")}),
]
COLUMNS = [("gather", "gather `fgw.ps`"), ("gather_lg", "gather past the L1 (`fgwl.ps` to the L2, `fgwg.ps` to the home)"),
           ("scatter", "scatter `fscw.ps`"), ("scatter_lg", "scatter past the L1 (`fscwl.ps`, `fscwg.ps`)"),
           ("load", "scalar `flw`, same offsets"), ("store", "scalar `fsw`, same offsets")]

# The L1 rows of section 3.1: (op, table, pattern, label). Per instruction and per element; zeros where they ran.
L1_ROWS = [("fgw.ps", "dram-512B", "rand", "gather, 32-bit"), ("fgh.ps", "dram-512B", "rand", "gather, 16-bit"),
           ("fgb.ps", "dram-512B", "rand", "gather, 8-bit"), ("fscw.ps", "dram-512B", "rand", "scatter, 32-bit"),
           ("fsch.ps", "dram-512B", "rand", "scatter, 16-bit"), ("fscb.ps", "dram-512B", "rand", "scatter, 8-bit"),
           ("fg32w.ps", "dram-512B", "rand", "32 B-block gather, 32-bit"), ("fg32b.ps", "dram-512B", "rand", "32 B-block gather, 8-bit"),
           ("fsc32w.ps", "dram-512B", "rand", "32 B-block scatter, 32-bit"),
           ("famoaddl.pi", "dram-512B", "bcast", "packed atomic add at the L2, every lane on the hart's own word"),
           ("famoaddg.pi", "dram-512B", "bcast", "packed atomic add at the home L3, every lane on the hart's own word")]

# Scatter-add and atomics (section 6, the influence page): (op, table, pattern, data, label)
UPDATES = [("upd", "dram-512B", "rand", "random", "gather + `fadd.ps` + scatter, private table in the L1 (512 B per hart)"),
           ("upd", "dram-4K", "rand", "random", "gather + `fadd.ps` + scatter, private table in the L2 (4 KB per hart)"),
           ("upd", "scp-16K", "rand", "random", "gather + `fadd.ps` + scatter, private table in the own scratchpad (16 KB per hart)"),
           ("upd", "dram-256K", "rand", "random", "gather + `fadd.ps` + scatter, private table in DRAM (256 KB per hart)"),
           ("famoaddl.pi", "shire-256K", "rand", "zeros", "packed atomic add `famoaddl.pi`, a 256 KB table shared by the shire (at its L2)"),
           ("amoaddl.w", "shire-256K", "rand", "zeros", "scalar atomic add `amoaddl.w`, the same shire tables"),
           ("famoaddg.pi", "chip-8M", "rand", "zeros", "packed atomic add `famoaddg.pi`, one 8 MB table for the chip (at the home L3 slices)"),
           ("amoaddg.w", "chip-8M", "rand", "zeros", "scalar atomic add `amoaddg.w`, the same chip table"),
           ("famoaddl.pi", "dram-512B", "bcast", "zeros", "`famoaddl.pi`, every lane on the hart's own word"),
           ("famoaddg.pi", "dram-512B", "bcast", "zeros", "`famoaddg.pi`, every lane on the hart's own word")]

# The L2 pattern sweep of section 4.3 (lines per instruction: unit 0.5, s2 1, s4 2, s16 8, line 1, rand 8, bcast 1)
PATTERNS = [("unit", "unit stride"), ("s2", "stride 2 words"), ("s4", "stride 4 words"), ("line", "8 words of one line, permuted"),
            ("bcast", "every lane one word"), ("s16", "one word per line, lines in order"), ("rand", "one word per line, lines random")]
