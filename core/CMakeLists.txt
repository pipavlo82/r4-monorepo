cmake_minimum_required(VERSION 3.16)
project(re4ctor_core C)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

include(GNUInstallDirs)

# ---------- Статична бібліотека ----------
add_library(re4ctor_core STATIC
  src/core/re4ctor_core.c
)
target_include_directories(re4ctor_core
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

# ---------- Утиліта re4_dump ----------
add_executable(re4_dump
  src/core/re4_dump.c
  src/drbg/drbg.c
  src/entropy/entropy.c
  src/health/health.c
  src/sp800_90b/estimator.c
)
target_link_libraries(re4_dump PRIVATE re4ctor_core m)

# Увімкнути RDRAND/RDSEED лише на Linux x86_64 (не на macOS)
if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64")
  set_source_files_properties(src/entropy/entropy.c
    PROPERTIES COMPILE_FLAGS "-mrdrnd -mrdseed")
endif()

# ---------- Тести ----------
enable_testing()
add_executable(re4_tests
  tests/basic.c
  src/drbg/drbg.c
  src/entropy/entropy.c
  src/health/health.c
  src/sp800_90b/estimator.c
)
target_link_libraries(re4_tests PRIVATE re4ctor_core m)
add_test(NAME basic COMMAND re4_tests)

# ---------- Інсталяція та CMake package ----------
install(TARGETS re4ctor_core
  EXPORT re4ctor_coreTargets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(TARGETS re4_dump
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(EXPORT re4ctor_coreTargets
  NAMESPACE re4::
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/re4ctor_core
)

include(CMakePackageConfigHelpers)
write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/re4ctor_coreConfigVersion.cmake"
  VERSION 0.1.0
  COMPATIBILITY SameMajorVersion
)
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/re4ctor_coreConfig.cmake"
"include(\"${CMAKE_CURRENT_LIST_DIR}/re4ctor_coreTargets.cmake\")\n"
)
install(FILES
  "${CMAKE_CURRENT_BINARY_DIR}/re4ctor_coreConfig.cmake"
  "${CMAKE_CURRENT_BINARY_DIR}/re4ctor_coreConfigVersion.cmake"
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/re4ctor_core
)
