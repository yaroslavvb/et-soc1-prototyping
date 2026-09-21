# ettelem: telemetry client on the management library (see ettelem.cpp).
#   cmake -S tools/ettelem -B build/ettelem -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/ettelem
cmake_minimum_required(VERSION 3.17)
project(ettelem LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_PREFIX_PATH}/lib/cmake")
find_package(deviceLayer REQUIRED)
find_package(deviceManagement REQUIRED)
add_executable(ettelem ettelem.cpp)
target_compile_features(ettelem PRIVATE cxx_std_17)
target_link_libraries(ettelem PRIVATE deviceLayer::deviceLayer deviceManagement::DM dl)
