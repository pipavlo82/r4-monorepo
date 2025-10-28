cmake_minimum_required(VERSION 3.10)
project(re4ctor_core LANGUAGES C)

# Стандарти
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Release)

# Опції
option(ENABLE_RDRAND "Enable Intel RDRAND fallback" ON)
option(ENABLE_FIPS "Build in FIPS mode" OFF)

# Джерела — вручну (без GLOB_RECURSIVE)
set(SOURCES
    src/main.c
    entropy/entropy.c
    drbg/hmac_drbg.c
)

# Заголовки
include_directories(
    include
    entropy
    drbg
)

# Бінарники
add_executable(re4_dump ${SOURCES})
add_executable(re4_tests
    tests/test_drbg.c
    entropy/entropy.c
    drbg/hmac_drbg.c
)

# Оптимізація
target_compile_options(re4_dump PRIVATE -O3 -march=native -mtune=native)
target_compile_options(re4_tests PRIVATE -O3 -march=native -mtune=native)

# RDRAND
if(ENABLE_RDRAND)
    target_compile_definitions(re4_dump PRIVATE USE_RDRAND)
    target_compile_definitions(re4_tests PRIVATE USE_RDRAND)
endif()

# FIPS
if(ENABLE_FIPS)
    target_compile_definitions(re4_dump PRIVATE FIPS_MODE)
    target_compile_definitions(re4_tests PRIVATE FIPS_MODE)
endif()

# Лінки
find_library(MATH_LIBRARY m)
if(MATH_LIBRARY)
    target_link_libraries(re4_dump ${MATH_LIBRARY})
    target_link_libraries(re4_tests ${MATH_LIBRARY})
endif()

# Тести
enable_testing()
add_test(NAME re4_tests COMMAND re4_tests)
