# Switching activity of the fused multiply-add unit for one data pattern (see README.md).
#   make CORE_ET=../../external/core-et
CORE_ET   ?= ../../external/core-et
VERILATOR ?= $(HOME)/.local/verilator/bin/verilator
RTL := $(CORE_ET)/rtl
LAT ?= 7

obj_dir/Vtb: tb.sv ff_acct.sv acct.cpp
	$(VERILATOR) --binary --timing --coverage-toggle --coverage-max-width 4096 -Wno-fatal -Wno-lint -Wno-style \
	  --top-module tb -j 4 +define+ET_SIMULATION +define+FMA_TB_LATENCY=$(LAT) \
	  +incdir+$(RTL)/inc +incdir+$(RTL) +incdir+$(CORE_ET) \
	  -y $(RTL)/shire/minion/vpu/txfma_7s -y $(RTL)/libs/rf_latches -y $(RTL)/libs/compressors \
	  -y $(RTL)/libs/floating_point -y $(RTL)/libs/fixed_point \
	  ff_acct.sv tb.sv acct.cpp

clean:
	rm -rf obj_dir *.dat
