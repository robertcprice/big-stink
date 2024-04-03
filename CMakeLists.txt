cmake_minimum_required(VERSION 3.17)
project(big_stink C)

set(CMAKE_C_STANDARD 11)

add_executable(big_stink
        tools/hornets.c
        tools/thumper.c)
