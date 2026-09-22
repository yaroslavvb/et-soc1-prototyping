cmake_minimum_required(VERSION 3.16)
project(etcfg C)
add_executable(etcfg etcfg.c)
target_include_directories(etcfg PRIVATE /opt/et/include)
