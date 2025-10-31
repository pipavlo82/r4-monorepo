cmake_minimum_required(VERSION 3.15)
project(re4ctor_core LANGUAGES C)

# ---- Standards & policies ----------------------------------------------------
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)  # PIE/PIC by default on modern toolchains

# Default to Release if not specified
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# ---- Options -----------------------------------------------------------------
option(ENABLE_RDRAND "Enable Intel RDRAND fallback" ON)
option(ENABLE_FIPS   "Build in FIPS mode"           OFF)
option(ENABLE_ASAN   "Enable AddressSanitizer in Debug" OFF)
option(ENABLE_UBSAN  "Enable UndefinedBehaviorSanitizer in Debug" OFF)
option(ENABLE_LTO    "Enable Link-Time Optimization in Release/RelWithDebInfo" ON)
option(BUILD_TESTING "Build tests" ON)

# ---- Sources -----------------------------------------------------------------
# Створюємо бібліотеку r4core і потім лінкуємо дві утиліти
add_library(r4core STATIC
    src/main_dummy.c           # порожній/заглушка, якщо потрібно lib без main (можеш прибрати, якщо не треба)
    entropy/entropy.c
    drbg/hmac_drbg.c
)

# Інтерфейсні заголовки для публічного використання
target_include_directories(r4core
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/entropy
    ${CMAKE_CURRENT_SOURCE_DIR}/drbg
)

# ---- Compile options / warnings ----------------------------------------------
if(MSVC)
  target_compile_options(r4core PRIVATE /W4 /permissive-)
else()
  target_compile_options(r4core PRIVATE
    -Wall -Wextra -Wpedantic -Wshadow -Wformat=2 -fno-common
  )
  # Безпекові флаги (де підтримуються)
  target_compile_options(r4core PRIVATE -fstack-protector-strong -D_FORTIFY_SOURCE=2)
  target_link_options(r4core PRIVATE -Wl,-z,relro,-z,now)
endif()

# Оптимізації за профілями
if(CMAKE_BUILD_TYPE MATCHES "Release|RelWithDebInfo")
  if(NOT MSVC)
    target_compile_options(r4core PRIVATE -O3 -mtune=native)
    # LTO
    if(ENABLE_LTO)
      include(CheckIPOSupported)
      check_ipo_supported(RESULT ipo_ok OUTPUT ipo_msg)
      if(ipo_ok)
        set_target_properties(r4core PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
      endif()
    endif()
  endif()
else() # Debug
  if(ENABLE_ASAN AND NOT MSVC)
    target_compile_options(r4core PRIVATE -fsanitize=address -fno-omit-frame-pointer)
    target_link_options(r4core    PRIVATE -fsanitize=address)
  endif()
  if(ENABLE_UBSAN AND NOT MSVC)
    target_compile_options(r4core PRIVATE -fsanitize=undefined)
    target_link_options(r4core    PRIVATE -fsanitize=undefined)
  endif()
endif()

# ---- Feature macros (RDRAND / FIPS) ------------------------------------------
if(ENABLE_FIPS)
  target_compile_definitions(r4core PUBLIC FIPS_MODE)
endif()

# Перевірка підтримки RDRAND: додаємо макрос лише якщо і опція увімкнена, і компілятор знає інструкцію
if(ENABLE_RDRAND AND NOT MSVC)
  include(CheckCSourceCompiles)
  set(CODE_RDRAND "
    #include <immintrin.h>
    int main(){ unsigned int s; _rdrand32_step(&s); return 0; }
  ")
  check_c_source_compiles("${CODE_RDRAND}" HAVE_RDRAND)
  if(HAVE_RDRAND)
    target_compile_definitions(r4core PUBLIC USE_RDRAND)
  else()
    message(STATUS "RDRAND not supported by compiler/CPU: disabling USE_RDRAND")
  endif()
elseif(ENABLE_RDRAND AND MSVC)
  # MSVC: спробуємо ввімкнути, якщо є immintrin.h (зазвичай так)
  target_compile_definitions(r4core PUBLIC USE_RDRAND)
endif()

# ---- Libs / math --------------------------------------------------------------
# m потрібна не всюди, але перевіримо
find_library(MATH_LIBRARY m)
if(MATH_LIBRARY)
  target_link_libraries(r4core PUBLIC ${MATH_LIBRARY})
endif()

# ---- Executables --------------------------------------------------------------
# re4_dump — основний бінарник
add_executable(re4_dump src/main.c)
target_link_libraries(re4_dump PRIVATE r4core)

# re4_tests — юніт-тести для DRBG/entropy
add_executable(re4_tests
  tests/test_drbg.c
)
target_link_libraries(re4_tests PRIVATE r4core)
if(NOT MSVC)
  target_compile_options(re4_dump  PRIVATE -O3 -mtune=native)
  target_compile_options(re4_tests PRIVATE -O3 -mtune=native)
endif()

# ---- Testing ------------------------------------------------------------------
include(CTest)
if(BUILD_TESTING)
  enable_testing()
  add_test(NAME re4_tests COMMAND re4_tests)
endif()

# ---- Install rules ------------------------------------------------------------
include(GNUInstallDirs)

install(TARGETS r4core re4_dump
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

# ---- Packaging config (optional; зручно для find_package) --------------------
# Можеш пізніше додати export targets / Config.cmake, якщо плануєш інсталювати як SDK
