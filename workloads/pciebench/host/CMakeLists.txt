# Host program: the runtime API over the PCIe device layer only (no simulator: timing the link needs the card).
find_package(runtime REQUIRED)
find_package(deviceLayer REQUIRED)

set(KERNEL_ELF "${CMAKE_BINARY_DIR}/kernel/empty.elf")
set(TOUCH_ELF "${CMAKE_BINARY_DIR}/kernel/touch.elf")
# The sources' sha256, compiled into the binary (Constants.h: SRC_SHA256), so a pass can tell a stale build from its
# tree's code. A change to any of them re-runs the configure, so the hashes never lag the code they describe.
set(PCIEBENCH_SRC main.cpp ../touch_args.h ../kernel/touch.c)
file(SHA256 ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp PCIEBENCH_MAIN_SHA256)
file(SHA256 ${CMAKE_CURRENT_SOURCE_DIR}/../touch_args.h PCIEBENCH_ARGS_SHA256)
file(SHA256 ${CMAKE_CURRENT_SOURCE_DIR}/../kernel/touch.c PCIEBENCH_TOUCH_SHA256)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${PCIEBENCH_SRC})
configure_file(Constants.h.in ${CMAKE_CURRENT_BINARY_DIR}/Constants.h)

add_executable(pciebench_host main.cpp)
target_include_directories(pciebench_host PRIVATE ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/..)
target_compile_features(pciebench_host PRIVATE cxx_std_17)
target_compile_options(pciebench_host PRIVATE -O2)
target_link_libraries(pciebench_host PRIVATE runtime::etrt deviceLayer::deviceLayer pthread)
