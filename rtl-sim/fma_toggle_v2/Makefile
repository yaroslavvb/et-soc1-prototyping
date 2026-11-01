# The real vector unit of the ET-SoC-1's open RTL, as a Verilator bench that returns correct multiply-adds. See README.md.
#   make CORE_ET=../../external/core-et                      # obj_vpu/Vtb, obj_unit/Vtb, accum, settle_count
#   make check                                               # the functional check, about a minute on 10 cores
# On a Mac with conda-forge's verilator, pass VERILATOR=<its path> CXXOVERRIDE=/usr/bin/clang++ as in ../fma_toggle/README.md.
CORE_ET   ?= ../../external/core-et
VERILATOR ?= verilator
RTL       := $(CORE_ET)/rtl
V         := $(RTL)/shire/minion/vpu
CXXOVERRIDE ?=
MKFLAGS := $(if $(CXXOVERRIDE),-MAKEFLAGS CXX=$(CXXOVERRIDE) -MAKEFLAGS LINK=$(CXXOVERRIDE),)
PY ?= python3

# -fno-dfg IS THE FIX. Verilator 5.052's data-flow-graph pass miscompiles core-et's casez blocks with a wildcard arm and part-select
# targets, among them the mux in front of the alignment shifter (txfma_f3.v:160-170): with the pass on, the shifter's input reads 0,
# and a multiply-add returns only its larger operand. verilator_dfg_reproducer.sv shows it in 20 lines.
VOPT := -fno-dfg

VCOMMON := -Wno-fatal -Wno-lint -Wno-style --top-module tb -j 10 $(MKFLAGS) $(VOPT) \
	  +define+ET_SIMULATION +incdir+. +incdir+$(RTL)/inc +incdir+$(RTL) +incdir+$(CORE_ET) \
	  -y $(V) -y $(V)/txfma_7s -y $(V)/tima -y $(V)/trans_unit \
	  -y $(RTL)/libs/macros -y $(RTL)/libs/rf_latches -y $(RTL)/libs/compressors \
	  -y $(RTL)/libs/floating_point -y $(RTL)/libs/fixed_point

all: obj_vpu/Vtb obj_unit/Vtb accum settle_count

# vpu_top whole, with toggle coverage, the register accounting and VCD tracing, which stays off unless +dump is given.
obj_vpu/Vtb: tb_vpu.sv ff_acct.sv macros_acct.vh acct.cpp
	$(VERILATOR) --binary --timing --coverage-toggle --coverage-max-width 4096 \
	  --trace --trace-depth 99 --trace-max-width 4096 --trace-max-array 4096 \
	  --Mdir obj_vpu $(VCOMMON) ff_acct.sv tb_vpu.sv acct.cpp

# one txfma_top, for the operand corners
obj_unit/Vtb: tb_unit.sv
	$(VERILATOR) --binary --timing --Mdir obj_unit $(VCOMMON) -y $(RTL)/libs/registers tb_unit.sv

accum: accum.c
	$(CC) -O2 -ffp-contract=off -o accum accum.c -lm

settle_count: settle_count.cpp
	$(CXX) -O2 -std=c++17 -o settle_count settle_count.cpp

check: all
	./fcheck_all.sh

clean:
	rm -rf obj_vpu obj_unit accum settle_count *.dat

# diagnostics: the flip count of the chip diagram's fact tfma.flip.stages, and use_prev_sigs on and off, each in both builds
obj_flip/Vtb: tb_flip.sv
	$(VERILATOR) --binary --timing --trace --trace-depth 99 --trace-max-width 4096 --Mdir obj_flip $(VCOMMON) -y $(RTL)/libs/registers tb_flip.sv
obj_prev/Vtb: tb_prev.sv
	$(VERILATOR) --binary --timing --Mdir obj_prev $(VCOMMON) -y $(RTL)/libs/registers tb_prev.sv
