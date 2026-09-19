# Device kernels.  This directory is not a standalone CMake project: it is
# pulled into the gp-sdk device build via
#   -DCUSTOM_KERNELS_SRC_DIR=<this dir> -DCUSTOM_KERNELS_BIN_DIR=<build dir>
# (see external/et-platform/gp-sdk/device/CMakeLists.txt and the top-level
# Makefile), which provides add_etsoc_riscv_executable() and etsoc_crt0.
#
# add_etsoc_riscv_executable(foo.elf ...) also produces foo.elf_dbg, relinked
# at the predicted load address, for use with gdb.

function(add_kernel NAME)
  add_etsoc_riscv_executable(${NAME}.elf ${ARGN})
  target_link_libraries(${NAME}.elf PRIVATE etsoc_crt0)
  target_include_directories(${NAME}.elf PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
endfunction()

add_kernel(hello hello/hello.cc)
add_kernel(mmbench mmbench/mmbench.cc)
