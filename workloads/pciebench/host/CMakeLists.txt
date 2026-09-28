# Host program: the runtime API over the PCIe device layer only (no simulator: timing the link needs the card).
find_package(runtime REQUIRED)
find_package(deviceLayer REQUIRED)

set(KERNEL_ELF "${CMAKE_BINARY_DIR}/kernel/empty.elf")
configure_file(Constants.h.in ${CMAKE_CURRENT_BINARY_DIR}/Constants.h)

add_executable(pciebench_host main.cpp)
target_include_directories(pciebench_host PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_compile_features(pciebench_host PRIVATE cxx_std_17)
target_compile_options(pciebench_host PRIVATE -O2)
target_link_libraries(pciebench_host PRIVATE runtime::etrt deviceLayer::deviceLayer pthread)
