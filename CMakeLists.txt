cmake_minimum_required(VERSION 4.3)
project(handcrafted-cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# C++17 [[snippet]] / [[snippet("설명")]] 어트리뷰트 사용 시 알 수 없는 어트리뷰트 경고 비활성화
add_compile_options(-Wno-attributes)

# 혹시 @snippet 문법을 사용하더라도 투명하게 컴파일되도록 래퍼 스크립트 연결
set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE "${CMAKE_SOURCE_DIR}/scripts/cxx_wrapper.sh")

add_executable(handcrafted-cpp main.cpp)

# ---- GoogleTest (한 번만 받아서 모든 항목의 test.cpp 가 공유해서 링크한다) ----
include(FetchContent)
if(EXISTS "${CMAKE_SOURCE_DIR}/.opensource/googletest/CMakeLists.txt")
    FetchContent_Declare(
        googletest
        SOURCE_DIR "${CMAKE_SOURCE_DIR}/.opensource/googletest"
    )
else()
    FetchContent_Declare(
        googletest
        URL https://github.com/google/googletest/archive/refs/tags/v1.15.2.zip
    )
endif()
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)
enable_testing()

# practice/stone-lecture (01_문법_STL, 02_알고리즘_개념, 03_실전_문제풀이) 타이핑·풀이 연습용 스캐폴드.
# <dir_name>/<NN_절>/<NN_항목>/main.cpp 파일마다 독립된 실행파일 타겟을 만들고,
# 같은 폴더에 test.cpp 가 있으면 GoogleTest 실행파일 타겟(<target>_test)도 만들어 ctest 에 등록한다.
# 폴더명에 한글이 섞여 있어 CMake 타겟명으로 쓸 수 없으므로,
# 절/항목 폴더명 앞의 숫자만 뽑아 "<prefix>_<절번호>_<항목번호>" 형태로 타겟명을 만든다.
function(stonecpp_add_practice_dir dir_name target_prefix)
    file(GLOB_RECURSE main_sources CONFIGURE_DEPENDS ${dir_name}/*/*/main.cpp)
    foreach(main_src ${main_sources})
        file(RELATIVE_PATH rel_path ${CMAKE_SOURCE_DIR}/${dir_name} ${main_src})
        get_filename_component(rel_dir ${rel_path} DIRECTORY)
        string(REPLACE "/" ";" parts ${rel_dir})
        list(GET parts 0 section_dir)
        list(GET parts 1 item_dir)
        string(REGEX MATCH "^[0-9]+" section_num ${section_dir})
        string(REGEX MATCH "^[0-9]+" item_num ${item_dir})
        set(target_name "${target_prefix}_${section_num}_${item_num}")
        add_executable(${target_name} ${main_src})

        set(test_src "${CMAKE_SOURCE_DIR}/${dir_name}/${rel_dir}/test.cpp")
        if(EXISTS ${test_src})
            set(test_target "${target_name}_test")
            add_executable(${test_target} ${test_src})
            target_link_libraries(${test_target} PRIVATE gtest_main)
            add_test(NAME ${test_target} COMMAND ${test_target})
        endif()
    endforeach()
endfunction()

stonecpp_add_practice_dir(practice/stone-lecture/01_문법_STL stone_lec01)
stonecpp_add_practice_dir(practice/stone-lecture/02_알고리즘_개념 stone_lec02)
stonecpp_add_practice_dir(practice/stone-lecture/03_실전_문제풀이 stone_lec03)

# C-and-Cpp 8권 실습장 (practice/c-and-cpp/<권>/<장>/<항목>)
# 특정 책만 CMake 타겟으로 로드하고 싶다면 -DACTIVE_BOOK=01_c_300 처럼 지정 가능 (기본값: ALL)
set(ACTIVE_BOOK "ALL" CACHE STRING "Load all books or a specific book folder under practice/c-and-cpp")

function(stonecpp_add_book_if_exists book_folder target_prefix)
    if(ACTIVE_BOOK STREQUAL "ALL" OR ACTIVE_BOOK STREQUAL "${book_folder}" OR "${book_folder}" MATCHES "^${ACTIVE_BOOK}")
        if(EXISTS "${CMAKE_SOURCE_DIR}/practice/c-and-cpp/${book_folder}")
            stonecpp_add_practice_dir("practice/c-and-cpp/${book_folder}" "${target_prefix}")
        endif()
    endif()
endfunction()

stonecpp_add_book_if_exists(01_c_300 book01)
stonecpp_add_book_if_exists(02_c_100 book02)
stonecpp_add_book_if_exists(03_tour_of_cpp book03)
stonecpp_add_book_if_exists(04_cpp_stl book04)
stonecpp_add_book_if_exists(05_high_perf_cpp book05)
stonecpp_add_book_if_exists(06_algo_generic book06)
stonecpp_add_book_if_exists(07_extreme_c book07)
stonecpp_add_book_if_exists(08_prof_cpp book08)

# Linux System Programming Track (practice/linux/01_tlpi_system_programming)
if(EXISTS "${CMAKE_SOURCE_DIR}/practice/linux/01_tlpi_system_programming")
    stonecpp_add_practice_dir("practice/linux/01_tlpi_system_programming" "linux_tlpi")
endif()

# Linux CLI Track (practice/linux/02_cli_and_shell_automation)
if(EXISTS "${CMAKE_SOURCE_DIR}/practice/linux/02_cli_and_shell_automation")
    stonecpp_add_practice_dir("practice/linux/02_cli_and_shell_automation" "linux_cli")
endif()

# Jongmanbook Algorithm Track (practice/jongmanbook)
if(EXISTS "${CMAKE_SOURCE_DIR}/practice/jongmanbook")
    stonecpp_add_practice_dir("practice/jongmanbook" "jongman")
endif()

# Knuth TAOCP Track (practice/knuth)
if(EXISTS "${CMAKE_SOURCE_DIR}/practice/knuth")
    stonecpp_add_practice_dir("practice/knuth" "knuth")
endif()
