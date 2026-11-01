# ettelem-e118: tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp in E118's no-PMIC-read profile (see ettelem.cpp's header).
# Build into its own directory, never into build/ettelem, build/ettelem-dv2 or build/ettelem-e84:
#   cmake -S tools/claims-v3/e118/ettelem-e118 -B build/ettelem-e118 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/ettelem-e118 -j4
cmake_minimum_required(VERSION 3.17)
project(ettelem_e118 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
find_package(deviceLayer REQUIRED)
find_package(deviceManagement REQUIRED)
add_executable(ettelem ettelem.cpp)
target_compile_features(ettelem PRIVATE cxx_std_17)
target_link_libraries(ettelem PRIVATE deviceLayer::deviceLayer deviceManagement::DM dl)
