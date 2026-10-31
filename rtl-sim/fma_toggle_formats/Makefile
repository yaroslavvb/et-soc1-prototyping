# Switching activity of the tensor multiply-add units per NUMBER FORMAT (see README.md).
#   make CORE_ET=../../external/core-et
# On macOS, conda-forge's verilator hardcodes a C++ compiler it does not ship on PATH; pass
#   VERILATOR=$HOME/.local/micromamba/envs/verilator/bin/verilator CXXOVERRIDE=/usr/bin/clang++
CORE_ET   ?= ../../external/core-et
VERILATOR ?= $(HOME)/.local/verilator/bin/verilator
RTL := $(CORE_ET)/rtl
LAT ?= 7
AROVERRIDE  ?= /usr/bin/ar
CXXOVERRIDE ?=
MKFLAGS := $(if $(CXXOVERRIDE),-MAKEFLAGS CXX=$(CXXOVERRIDE) -MAKEFLAGS LINK=$(CXXOVERRIDE) -MAKEFLAGS AR=$(AROVERRIDE),)

VCOMMON := -Wno-fatal -Wno-lint -Wno-style --top-module tb -j 4 $(MKFLAGS) \
	  +define+ET_SIMULATION +define+FMA_TB_LATENCY=$(LAT) \
	  +incdir+$(RTL)/inc +incdir+$(RTL) +incdir+$(CORE_ET) \
	  -y $(RTL)/shire/minion/vpu/txfma_7s -y $(RTL)/shire/minion/vpu/tima \
	  -y $(RTL)/libs/rf_latches -y $(RTL)/libs/compressors \
	  -y $(RTL)/libs/floating_point -y $(RTL)/libs/fixed_point

obj_dir/Vtb: tb_fmt.sv ff_acct.sv acct.cpp
	$(VERILATOR) --binary --timing --coverage-toggle --coverage-max-width 4096 $(VCOMMON) \
	  ff_acct.sv tb_fmt.sv acct.cpp

clean:
	rm -rf obj_dir *.dat
