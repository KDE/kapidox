cmake_minimum_required(VERSION 3.16)
project(KApiDox NONE)

include(FindUnixCommands)

if(WIN32)
    # Needs native path and extra escaping of spaces
    file(TO_NATIVE_PATH "${CMAKE_BINARY_DIR}" BINARY_DIR)
else()
    set(BINARY_DIR ${CMAKE_BINARY_DIR})
endif()

add_custom_target(build ALL
    COMMAND ${BASH} bootstrap-devenv.sh
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
)

