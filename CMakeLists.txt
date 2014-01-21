project(kapidox NONE)
cmake_minimum_required(VERSION 2.8)

find_package(PythonInterp REQUIRED)

add_custom_target(build ALL
    COMMAND ${PYTHON_EXECUTABLE} setup.py build --build-base ${CMAKE_BINARY_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )

install(CODE
    "execute_process(
        COMMAND ${PYTHON_EXECUTABLE} setup.py install --prefix ${CMAKE_INSTALL_PREFIX}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        )"
    )
