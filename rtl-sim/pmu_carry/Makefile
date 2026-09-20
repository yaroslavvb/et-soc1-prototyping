# Simulates the original PMU counter RTL to show the late carry into bit 7 (see README.md).
#   make CORE_ET=../../external/core-et [TRACE=1]
CORE_ET   ?= ../../external/core-et
VERILATOR ?= $(HOME)/.local/verilator/bin/verilator
RTL := $(CORE_ET)/rtl

run: obj_dir/Vtb
	./obj_dir/Vtb $(if $(TRACE),+trace)

obj_dir/Vtb: tb.sv
	$(VERILATOR) --binary --timing --trace -Wno-fatal -Wno-lint -Wno-style --top-module tb \
	  +define+ET_SIMULATION +incdir+$(RTL)/inc +incdir+$(RTL) +incdir+$(CORE_ET) \
	  tb.sv $(RTL)/shire/neigh/neigh_pmu.v $(RTL)/libs/rf_latches/et_clk_gate.v

clean:
	rm -rf obj_dir pmu.vcd
