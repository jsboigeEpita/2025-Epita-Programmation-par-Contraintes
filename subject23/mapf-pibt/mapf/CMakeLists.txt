cmake_minimum_required(VERSION 3.16)
project(lib-mapf)
add_library(lib-mapf SHARED)
if( CPU STREQUAL "M1" )
    message("Configuring grid-pathfinding for M1 Mac.")
    target_compile_options(lib-mapf PUBLIC 
        -std=c++20 -O0 -g -Wall -Wl,--out-implib,libshared_lib.a -mtune=native -mcpu=apple-m1)
else()
    target_compile_options(lib-mapf PUBLIC 
        -std=c++20 -O0 -g -Wall -Wl,--out-implib,libshared_lib.a -mtune=native -march=native)
endif()
target_include_directories(lib-mapf INTERFACE ./include)

add_subdirectory(../third_party/grid-pathfinding/graph ./graph)
add_subdirectory(src)
target_link_libraries(lib-mapf lib-graph)
