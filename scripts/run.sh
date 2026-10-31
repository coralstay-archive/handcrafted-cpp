#!/usr/bin/env bash
# 연습 파일(main.cpp) 하나를 빠르게 컴파일 + 실행한다. (CMake 재구성 없이 즉시 실행)
# GoogleTest(test.cpp)를 빌드/실행하려면 scripts/test.sh 를 쓰세요.
#
# 사용법:
#   ./scripts/run.sh practice/stone-lecture/01_문법_STL/01_기본/01_예제로_이해하는_Cpp
#   ./scripts/run.sh practice/c-and-cpp/08_prof_cpp/01_a_crash_course_in_c_and_the_standard_library/01_example_01_helloworld
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "사용법: $0 <폴더경로 또는 main.cpp 경로> [실행시 넘길 인자...]" >&2
  exit 1
fi

target="$1"
shift

# practice/ 접두사를 생략하고 입력해도 자동으로 찾도록 보정
if [ ! -e "$target" ] && [ -e "practice/$target" ]; then
  target="practice/$target"
fi

if [ -d "$target" ]; then
  src="$target/main.cpp"
  # Also compile any helper .cpp/.c files in the folder (excluding test.cpp and files with main)
  helpers=()
  for f in "$target"/*.cpp "$target"/*.c; do
    [ -f "$f" ] || continue
    base="$(basename "$f")"
    if [ "$base" != "main.cpp" ] && [ "$base" != "test.cpp" ] && [ "$base" != "main.c" ]; then
      if ! grep -Eq 'int\s+main\s*\(' "$f" 2>/dev/null; then
        helpers+=("-x" "c++" "$f")
      fi
    fi
  done
  sources=("$src" ${helpers[@]+"${helpers[@]}"})
else
  src="$target"
  sources=("$target")
fi

if [ ! -f "$src" ]; then
  echo "파일을 찾을 수 없습니다: $src" >&2
  exit 1
fi

cxx_std="${CXX_STD:-c++20}"
if grep -qE "(<print>|std::println)" "$src" 2>/dev/null; then
  cxx_std="c++23"
fi

out_dir="$(mktemp -d)"
out="$out_dir/a.out"

script_dir="$(cd "$(dirname "$0")" && pwd)"
"$script_dir/cxx_wrapper.sh" g++ -std="$cxx_std" -O2 -Wall -Wno-attributes "${sources[@]}" -o "$out"

if [ -d "$target" ]; then
  (cd "$target" && "$out" "$@")
else
  (cd "$(dirname "$target")" && "$out" "$@")
fi
