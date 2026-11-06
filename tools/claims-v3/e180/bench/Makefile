# E180's bench: core-et's whole minion_top (front end, integer pipe, dcache, vector unit) running the energy catalogue's
# vector-add loop on both harts, under Verilator 5.052 (the mini's Homebrew build, the version rtl-sim/fma_toggle_v2 uses).
#   make CORE_ET=<core-et at b38a1a3> V2=<rtl-sim/fma_toggle_v2> VERILATOR=/opt/homebrew/bin/verilator
# -fno-dfg is rtl-sim/fma_toggle_v2's fix (its README: Verilator 5.052's DFG pass miscompiles core-et's casez muxes).
# ff_acct.sv, macros_acct.vh and acct.cpp are rtl-sim/fma_toggle_v2's, used unchanged (register accounting, coverage reset).
CORE_ET   ?= ../../../../external/core-et
V2        ?= ../../../../rtl-sim/fma_toggle_v2
VERILATOR ?= verilator
JOBS      ?= 4
R := $(CORE_ET)/rtl
M := $(R)/shire/minion
VP := $(M)/vpu
VFLAGS := -Wno-fatal -Wno-lint -Wno-style -fno-dfg --top-module tb -j $(JOBS) \
  +define+ET_SIMULATION +define+ET_NO_TESTEND_MONITOR \
  +incdir+. +incdir+$(V2) +incdir+$(R)/inc +incdir+$(R) +incdir+$(CORE_ET) +incdir+$(M)/intpipe/csr \
  -y $(M) -y $(M)/dcache -y $(M)/frontend -y $(M)/intpipe -y $(M)/intpipe/csr \
  -y $(VP) -y $(VP)/txfma_7s -y $(VP)/tima -y $(VP)/trans_unit \
  -y $(R)/libs/macros -y $(R)/libs/rf_latches -y $(R)/libs/compressors -y $(R)/libs/floating_point -y $(R)/libs/fixed_point \
  -y $(R)/libs/registers -y $(R)/libs/arbiters -y $(R)/libs/mems_and_fifos -y $(R)/libs/counters -y $(R)/libs/ecc \
  -y $(R)/libs/bridges -y $(R)/libs/pll

all: obj_min/Vtb

obj_min/Vtb: tb_minion_e180.sv prelude_e180.sv $(V2)/ff_acct.sv $(V2)/macros_acct.vh $(V2)/acct.cpp
	$(VERILATOR) --binary --timing --coverage-toggle --coverage-max-width 4096 --Mdir obj_min $(VFLAGS) \
	  $(V2)/ff_acct.sv prelude_e180.sv tb_minion_e180.sv $(V2)/acct.cpp

clean:
	rm -rf obj_min
