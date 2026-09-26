# enercat workload: memory-hierarchy probes (device kernel + host program), one command to build both.
#   cmake -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build
#   ./build/host/enercat_host --sysemu      # simulator
#   ./build/host/enercat_host               # ET-SoC-1 card (/dev/et0_*)
# Structure adapted from https://github.com/marty1885/et-testdrive (Apache-2.0).
cmake_minimum_required(VERSION 3.17)
project(enercat VERSION 0.1.0)

include(ExternalProject)

# -DENERCAT_GS=ON adds the gather/scatter modes (V3-GS) to kernel and host; build it in its own directory
# (build/enercat_gs) so the catalogue's binaries (build/enercat, build/enercat_v2) are never rebuilt with it.
option(ENERCAT_GS "compile the gather/scatter modes (400+)" OFF)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules")

set(KERNEL_BINARY_DIR ${CMAKE_BINARY_DIR}/kernel)
ExternalProject_Add(enercat_kernel
    SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/kernel
    BINARY_DIR ${KERNEL_BINARY_DIR}
    CMAKE_ARGS
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_PREFIX_PATH}/lib/cmake/riscv64-ec-toolchain.cmake
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_MODULE_PATH=${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules
        -DCMAKE_BUILD_TYPE=Release
        -DCMAKE_INSTALL_LIBDIR=lib
        -DENERCAT_GS=${ENERCAT_GS}
    INSTALL_COMMAND ""
    BUILD_ALWAYS TRUE
    BUILD_BYPRODUCTS ${KERNEL_BINARY_DIR}/enercat.elf
)

add_subdirectory(host)
add_dependencies(enercat_host enercat_kernel)
