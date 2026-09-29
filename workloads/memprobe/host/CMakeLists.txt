# Host program.  Links both device layers; --sysemu picks the simulator at run time.
find_package(runtime REQUIRED)
find_package(deviceLayer REQUIRED)
find_package(sw-sysemu REQUIRED)
find_package(EsperantoBootLoader REQUIRED)
find_package(EsperantoDeviceMinionRuntime REQUIRED)

# Firmware that the simulator has to boot (a real card boots its own from flash).
get_property(BOOTROM_TRAMPOLINE_TO_BL2_ELF TARGET EsperantoBootLoader::BootromTrampolineToBL2.elf PROPERTY LOCATION)
get_property(BL2_ELF TARGET EsperantoBootLoader::ServiceProcessorBL2_fast-boot.elf PROPERTY LOCATION)
get_property(MASTER_MINION_ELF TARGET EsperantoDeviceMinionRuntime::MasterMinion.elf PROPERTY LOCATION)
get_property(MACHINE_MINION_ELF TARGET EsperantoDeviceMinionRuntime::MachineMinion.elf PROPERTY LOCATION)
get_property(WORKER_MINION_ELF TARGET EsperantoDeviceMinionRuntime::WorkerMinion.elf PROPERTY LOCATION)
set(SYSEMU_INSTALL_DIR "${CMAKE_PREFIX_PATH}/bin/")
set(KERNEL_ELF "${CMAKE_BINARY_DIR}/kernel/memprobe.elf")
configure_file(Constants.h.in ${CMAKE_CURRENT_BINARY_DIR}/Constants.h)

add_executable(memprobe_host main.cpp)
target_include_directories(memprobe_host PRIVATE ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_compile_features(memprobe_host PRIVATE cxx_std_17)
target_compile_options(memprobe_host PRIVATE -O2)
target_link_libraries(memprobe_host PRIVATE runtime::etrt deviceLayer::deviceLayer sw-sysemu::sw-sysemu)
# -DMEMPROBE_EXT=ON: the MP_EXT modes (--tloop, the TensorLoad ops); off, the host is unchanged.
# The binary carries "memp2-src:<sha256 main.cpp>:<sha256 memprobe_args.h>" (tools/claims-v3/memp2 refuses a stale
# build); a change to either file re-runs the configure step, so the tag follows the sources.
if(MEMPROBE_EXT)
  file(SHA256 ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp MP2_MAIN_SHA)
  file(SHA256 ${CMAKE_CURRENT_SOURCE_DIR}/../memprobe_args.h MP2_ARGS_SHA)
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
               ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp ${CMAKE_CURRENT_SOURCE_DIR}/../memprobe_args.h)
  target_compile_definitions(memprobe_host PRIVATE MP_EXT=1 MP2_SRC_TAG="memp2-src:${MP2_MAIN_SHA}:${MP2_ARGS_SHA}")
endif()
