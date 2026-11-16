# x14: request 1113-x14-zeroshare. The lab repo's sparsity kernel (kernel/, unchanged) and a card-only host for it
# (host/, the lab's sparsity host trimmed to the fp32 TensorFMA loop). One command builds both:
#   cmake -S . -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build -j4
# Structure as in the public lab repo's workloads/sparsity (itself adapted from github.com/marty1885/et-testdrive,
# Apache-2.0).
cmake_minimum_required(VERSION 3.17)
project(x14 VERSION 0.1.0)

include(ExternalProject)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules")

set(KERNEL_BINARY_DIR ${CMAKE_BINARY_DIR}/kernel)
ExternalProject_Add(x14_kernel
    SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/kernel
    BINARY_DIR ${KERNEL_BINARY_DIR}
    CMAKE_ARGS
        -DCMAKE_TOOLCHAIN_FILE=${CMAKE_PREFIX_PATH}/lib/cmake/riscv64-ec-toolchain.cmake
        -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}
        -DCMAKE_MODULE_PATH=${CMAKE_PREFIX_PATH}/lib/cmake/cmake-modules
        -DCMAKE_BUILD_TYPE=Release
        -DCMAKE_INSTALL_LIBDIR=lib
    INSTALL_COMMAND ""
    BUILD_ALWAYS TRUE
    BUILD_BYPRODUCTS ${KERNEL_BINARY_DIR}/sparsity.elf
)

add_subdirectory(host)
add_dependencies(x14_host x14_kernel)
