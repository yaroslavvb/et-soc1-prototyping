# Switching activity of the fused multiply-add unit for one data pattern (see README.md).
#   make CORE_ET=../../external/core-et                      # obj_dir/Vtb, the coverage counter
#   make trace CORE_ET=../../external/core-et                # obj_dir_trace/Vtrace, the settled counter's tracer
#   make settle_count                                        # the VCD counter
# On macOS, conda-forge's verilator hardcodes a C++ compiler it does not ship on PATH; pass
#   VERILATOR=$HOME/.local/micromamba/envs/verilator/bin/verilator CXXOVERRIDE=/usr/bin/clang++
CORE_ET   ?= ../../external/core-et
VERILATOR ?= $(HOME)/.local/verilator/bin/verilator
RTL := $(CORE_ET)/rtl
LAT ?= 7
CXXOVERRIDE ?=
MKFLAGS := $(if $(CXXOVERRIDE),-MAKEFLAGS CXX=$(CXXOVERRIDE) -MAKEFLAGS LINK=$(CXXOVERRIDE),)

VCOMMON := -Wno-fatal -Wno-lint -Wno-style --top-module tb -j 4 $(MKFLAGS) \
	  +define+ET_SIMULATION +define+FMA_TB_LATENCY=$(LAT) \
	  +incdir+$(RTL)/inc +incdir+$(RTL) +incdir+$(CORE_ET) \
	  -y $(RTL)/shire/minion/vpu/txfma_7s -y $(RTL)/libs/rf_latches -y $(RTL)/libs/compressors \
	  -y $(RTL)/libs/floating_point -y $(RTL)/libs/fixed_point

obj_dir/Vtb: tb.sv ff_acct.sv acct.cpp
	$(VERILATOR) --binary --timing --coverage-toggle --coverage-max-width 4096 $(VCOMMON) \
	  ff_acct.sv tb.sv acct.cpp

# The same stimulus with VCD tracing compiled in, and the toggle coverage still on, so one run yields
# both counts on exactly the same stream. Tracing stays off at run time unless +dump=<file> is given.
trace: obj_dir_trace/Vtrace
obj_dir_trace/Vtrace: tb.sv ff_acct.sv acct.cpp
	$(VERILATOR) --binary --timing --coverage-toggle --coverage-max-width 4096 \
	  --trace --trace-depth 99 --trace-max-width 4096 --trace-max-array 4096 \
	  --Mdir obj_dir_trace -o Vtrace $(VCOMMON) ff_acct.sv tb.sv acct.cpp

settle_count: settle_count.cpp
	$(CXX) -O2 -std=c++17 -o settle_count settle_count.cpp

clean:
	rm -rf obj_dir obj_dir_trace settle_count *.dat
