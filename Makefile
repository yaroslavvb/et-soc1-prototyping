# Build and run ET-SoC-1 prototypes.  Everything here runs on Linux, so from
# the Mac prefix commands with scripts/vm, e.g.
#   scripts/vm make                      # build kernels + launchers
#   scripts/vm make run-hello            # run hello on the sysemu simulator
#   make run-hello DEVICE=silicon        # (on a lab machine with a card)

ET         ?= /opt/et
GP_SDK     := $(CURDIR)/external/et-platform/gp-sdk
BUILD      ?= $(CURDIR)/build
RUN_DIR    ?= $(BUILD)/run
ADDRESS    ?= 0x8006335000
JOBS       ?= $(shell nproc)
DEVICE     ?= sysemu
# Extra sys_emu flags for DEVICE=sysemu, e.g. SIM_PARAMS="-vpurf_check -mem_check"
SIM_PARAMS ?=

CMAKE_PATHS := -DCMAKE_PREFIX_PATH="$(ET);$(ET)/lib/cmake" \
               -DCMAKE_MODULE_PATH="$(ET)/lib/cmake;$(ET)/lib/cmake/cmake-modules"

.PHONY: all kernels launchers run-hello mmbench-check bench-power trace upstream-test upstream-hello sgemm run-sgemm clean

all: kernels launchers

$(BUILD)/kernels/CMakeCache.txt:
	cmake -S $(GP_SDK)/device -B $(BUILD)/kernels $(CMAKE_PATHS) \
	  -DCMAKE_TOOLCHAIN_FILE=$(ET)/lib/cmake/riscv64-ec-toolchain.cmake \
	  -DCMAKE_BUILD_TYPE=Release -DADDRESS:STRING=$(ADDRESS) -DBUILD_TESTS=OFF \
	  -DCUSTOM_KERNELS_SRC_DIR=$(CURDIR)/kernels -DCUSTOM_KERNELS_BIN_DIR=$(BUILD)/kernels/nekko

kernels: $(BUILD)/kernels/CMakeCache.txt
	cmake --build $(BUILD)/kernels -j$(JOBS)

$(BUILD)/launchers/CMakeCache.txt:
	cmake -S launchers -B $(BUILD)/launchers $(CMAKE_PATHS) -DCMAKE_BUILD_TYPE=Release

launchers: $(BUILD)/launchers/CMakeCache.txt
	cmake --build $(BUILD)/launchers -j$(JOBS)

# The launcher writes sys_emu UART logs and trace dumps to the current dir.
run-hello: all
	mkdir -p $(RUN_DIR)
	cd $(RUN_DIR) && $(BUILD)/launchers/hello_launcher \
	  --kernel_path=$(BUILD)/kernels/nekko/hello.elf --device_type=$(DEVICE) \
	  $(if $(SIM_PARAMS),--simulator_params="$(SIM_PARAMS)")

# Matmul throughput / energy benchmark (kernels/mmbench, launchers/mmbench); see docs/getting-started.md.
# On a lab machine, build it first with scripts/deploy-lab-gpsdk.sh <host>.
# mmbench-check: short exact-result runs of every mode, on one shire in sysemu (about 40 s each) or
# on all 32 shires of a card (each run holds the card well under 1 s; capped at 10 s).
MMBENCH_SHIRES ?= $(if $(filter silicon,$(DEVICE)),0xffffffff,0x1)
mmbench-check: all
	mkdir -p $(RUN_DIR)
	cd $(RUN_DIR) && for args in "-m fp32" "-m fp16" "-m int8" "-m fp32 -n 64 -i 2 -p"; do \
	  $(if $(filter silicon,$(DEVICE)),timeout 10) $(BUILD)/launchers/mmbench_launcher \
	    -k $(BUILD)/kernels/nekko/mmbench.elf -d $(DEVICE) -s $(MMBENCH_SHIRES) $$args || exit 1; done

# FLOP/s per watt on a lab card: idle baseline, then each workload with board power sampled
# (quit et-powertop first: the power logger needs the card's mgmt node). Results in $(BUILD)/mmbench-power.
bench-power: all
	python3 scripts/mmbench-power.py --launcher $(BUILD)/launchers/mmbench_launcher \
	  --kernel $(BUILD)/kernels/nekko/mmbench.elf --out $(BUILD)/mmbench-power
	python3 scripts/mmbench-report-data.py $(BUILD)/mmbench-power

# Standalone workload (et-testdrive style, no gp-sdk): see workloads/sgemm/README.md.
# On a lab machine: scripts/deploy-lab.sh aifoundry3 workloads/sgemm
sgemm:
	cmake -S workloads/sgemm -B $(BUILD)/sgemm -DCMAKE_PREFIX_PATH=$(ET) -Wno-dev > /dev/null
	cmake --build $(BUILD)/sgemm -j$(JOBS)

run-sgemm: sgemm
	mkdir -p $(BUILD)/sgemm/run
	cd $(BUILD)/sgemm/run && $(BUILD)/sgemm/host/sgemm_host --sysemu -n 128 --reps 1 $(if $(SIM_PARAMS),--sim-args "$(SIM_PARAMS)")

# Print et_printf() output from the last run's device trace dump.
trace:
	$(BUILD)/launchers/trace_dump $(RUN_DIR)/traceKernels_dev0_0.bin

# The hello world from et-platform's README / CI (on a card: make upstream-test DEVICE=silicon).
upstream-test:
	mkdir -p $(RUN_DIR)
	cd $(RUN_DIR) && $(ET)/bin/it_test_code_loading $(if $(filter silicon,$(DEVICE)),--mode=pcie)

# gp-sdk's own hello world (needs patches/et-platform-0002 to boot sysemu).
upstream-hello:
	mkdir -p $(RUN_DIR)
	cd $(RUN_DIR) && $(ET)/bin/hello_world_launcher --kernel_path=$(ET)/kernels/print.elf --device_type=$(DEVICE)
	$(BUILD)/launchers/trace_dump $(RUN_DIR)/traceKernels_dev0_0.bin

clean:
	rm -rf $(BUILD)
