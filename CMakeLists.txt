cmake_minimum_required(VERSION 3.16)
project(KApiDox NONE)

find_package(Python3 COMPONENTS Interpreter)

if(WIN32)
    # Needs native path and extra escaping of spaces
    file(TO_NATIVE_PATH "${CMAKE_BINARY_DIR}" BINARY_DIR)
else()
    set(BINARY_DIR ${CMAKE_BINARY_DIR})
endif()

add_custom_target(build ALL
    COMMAND ${Python3_EXECUTABLE} setup.py build --build-base ${BINARY_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )

# DESTDIR may be set at install time (eg: `make DESTDIR=/tmp/package install`)
# so we need to check for it when the install code is run and pass the appropriate
# argument to distutils.
#
# Note that if(\$ENV{DESTDIR}) always fails, regardless of the value of the DESTDIR
# environment variable, hence the STREQUAL test.
# See https://public.kitware.com/Bug/view.php?id=14737
install(CODE
    "set(_root_arg)
     if (NOT \$ENV{DESTDIR} STREQUAL \"\")
         file(TO_NATIVE_PATH \$ENV{DESTDIR} DESTDIR)
         set(_root_arg --root \"\${DESTDIR}\")
     endif()
    file(TO_NATIVE_PATH ${CMAKE_INSTALL_PREFIX} INSTALL_PREFIX)
     execute_process(
        COMMAND ${Python3_EXECUTABLE} setup.py install --prefix \"\${INSTALL_PREFIX}\" \${_root_arg}
        WORKING_DIRECTORY \"${CMAKE_SOURCE_DIR}\"
        )"
    )
