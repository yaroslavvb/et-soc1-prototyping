# Q133(a): rtl-sim/fma_toggle_v2's whole vpu_top with tima_top (the int8 multiply-add, 16 per VPU) replaced by a gate-level
# netlist from the open flow (tools/open-flow/tima/). Everything else is that bench's own files, unchanged: tb_vpu.sv,
# ff_acct.sv, acct.cpp, macros_acct.vh, settle_count.cpp, accum.c, run_kinds.py, train_maps.py, fcheck_vpu.py. See README.md.
#
#   make BUILD=<dir> CORE_ET=../../external/core-et rtl                      # the control: the RTL bench as Q132(b) built it
#   make BUILD=<dir> CORE_ET=... NETDIR=<dir of tima_<arm>_staged.v and asap7_cells.v> ARM=booth_tree gate
#   make BUILD=<dir> tools                                                   # accum and settle_count
#
# Build products go to $(BUILD), never into this directory. On the Intel: VERILATOR=$HOME/.local/micromamba/envs/verilator/bin/verilator
# CXXOVERRIDE=/usr/bin/clang++ (Verilator 5.052, the version Q132(b) used), and at most 6 jobs.
CORE_ET   ?= ../../external/core-et
VERILATOR ?= verilator
BUILD     ?= build
NETDIR    ?= $(BUILD)/net
ARM       ?= booth_tree
JOBS      ?= 6
RTL       := $(CORE_ET)/rtl
V         := $(RTL)/shire/minion/vpu
V2        := ../fma_toggle_v2
CXXOVERRIDE ?=
MKFLAGS := $(if $(CXXOVERRIDE),-MAKEFLAGS CXX=$(CXXOVERRIDE) -MAKEFLAGS LINK=$(CXXOVERRIDE),)

# -fno-dfg: Q132(b)'s fix for Verilator 5.052's data-flow-graph miscompile of core-et's casez blocks (txfma_f3.v:160-170).
VOPT := -fno-dfg

VCOMMON := -Wno-fatal -Wno-lint -Wno-style --top-module tb -j $(JOBS) $(MKFLAGS) $(VOPT) \
	  +define+ET_SIMULATION +incdir+$(V2) +incdir+$(RTL)/inc +incdir+$(RTL) +incdir+$(CORE_ET) \
	  -y $(V) -y $(V)/txfma_7s -y $(V)/tima -y $(V)/trans_unit \
	  -y $(RTL)/libs/macros -y $(RTL)/libs/rf_latches -y $(RTL)/libs/compressors \
	  -y $(RTL)/libs/floating_point -y $(RTL)/libs/fixed_point

VTRACE := --binary --timing --coverage-toggle --coverage-max-width 4096 \
	  --trace --trace-depth 99 --trace-max-width 4096 --trace-max-array 4096

.PHONY: rtl gate tools
rtl: $(BUILD)/obj_rtl/Vtb
gate: $(BUILD)/obj_$(ARM)/Vtb
tools: $(BUILD)/accum $(BUILD)/settle_count

# the control: fma_toggle_v2's obj_vpu/Vtb target, flag for flag
$(BUILD)/obj_rtl/Vtb: $(V2)/tb_vpu.sv $(V2)/ff_acct.sv $(V2)/macros_acct.vh $(V2)/acct.cpp
	$(VERILATOR) $(VTRACE) --Mdir $(BUILD)/obj_rtl $(VCOMMON) $(V2)/ff_acct.sv $(V2)/tb_vpu.sv $(V2)/acct.cpp

# the same, with the gate-level tima_top listed first: a module defined in a listed file is never looked up in -y
$(BUILD)/obj_$(ARM)/Vtb: $(V2)/tb_vpu.sv $(V2)/ff_acct.sv $(V2)/macros_acct.vh $(V2)/acct.cpp $(NETDIR)/tima_$(ARM)_staged.v $(NETDIR)/asap7_cells.v
	$(VERILATOR) $(VTRACE) --Mdir $(BUILD)/obj_$(ARM) $(VCOMMON) $(NETDIR)/asap7_cells.v $(NETDIR)/tima_$(ARM)_staged.v \
	  $(V2)/ff_acct.sv $(V2)/tb_vpu.sv $(V2)/acct.cpp

# the float unit at gate level: txfma_top (8 per VPU) replaced by FNET, a netlist from tools/open-flow/tima/synth_txfma_flat.sh
# rewritten by netlist_stages.py --generic; tima_top stays RTL. For counting fp32 and fp16 on the same footing as the int8 netlists.
FNET ?= txfma_flat
.PHONY: gatef
gatef: $(BUILD)/obj_f_$(FNET)/Vtb
$(BUILD)/obj_f_$(FNET)/Vtb: $(V2)/tb_vpu.sv $(V2)/ff_acct.sv $(V2)/macros_acct.vh $(V2)/acct.cpp $(NETDIR)/$(FNET)_staged.v $(NETDIR)/asap7_cells.v
	$(VERILATOR) $(VTRACE) --Mdir $(BUILD)/obj_f_$(FNET) $(VCOMMON) $(NETDIR)/asap7_cells.v $(NETDIR)/$(FNET)_staged.v \
	  $(V2)/ff_acct.sv $(V2)/tb_vpu.sv $(V2)/acct.cpp

$(BUILD)/accum: $(V2)/accum.c
	mkdir -p $(BUILD) && $(CC) -O2 -ffp-contract=off -o $@ $< -lm

$(BUILD)/settle_count: $(V2)/settle_count.cpp
	mkdir -p $(BUILD) && $(CXX) -O2 -std=c++17 -o $@ $<
