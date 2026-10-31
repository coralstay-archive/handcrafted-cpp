#!/usr/bin/env bash
# 항목 하나의 GoogleTest(test.cpp)를 빌드하고 실행한다.
# 처음 실행할 때는 CMake 구성 + GoogleTest 다운로드/빌드가 필요해 다소 걸릴 수 있다.
# (이후에는 해당 target 만 다시 빌드하므로 빠르다.)
#
# 사용법:
#   ./scripts/test.sh practice/stone-lecture/01_문법_STL/01_기본/02_typedef
#   ./scripts/test.sh practice/c-and-cpp/08_prof_cpp/01_a_crash_course_in_c_and_the_standard_library/01_example_01_helloworld
set -euo pipefail
cd "$(dirname "$0")/.."

if [ "$#" -lt 1 ]; then
  echo "사용법: $0 <항목폴더경로>  (예: practice/stone-lecture/01_문법_STL/01_기본/02_typedef)" >&2
  exit 1
fi

item_dir="${1%/}"
item_dir="${item_dir#./}"
item_dir="${item_dir#practice/}"
shift || true

root_dir="$(echo "$item_dir" | cut -d/ -f1)"

case "$root_dir" in
  stone-lecture)
    sub_lec="$(echo "$item_dir" | cut -d/ -f2)"
    lec_num="$(echo "$sub_lec" | grep -oE '^[0-9]+' || true)"
    prefix="stone_lec${lec_num}"
    section_dir="$(echo "$item_dir" | cut -d/ -f3)"
    leaf_dir="$(echo "$item_dir" | cut -d/ -f4)"
    ;;
  c-and-cpp)
    book_dir="$(echo "$item_dir" | cut -d/ -f2)"
    book_num="$(echo "$book_dir" | grep -oE '^[0-9]+' || true)"
    prefix="book${book_num}"
    section_dir="$(echo "$item_dir" | cut -d/ -f3)"
    leaf_dir="$(echo "$item_dir" | cut -d/ -f4)"
    ;;
  linux)
    track_dir="$(echo "$item_dir" | cut -d/ -f2)"
    track_num="$(echo "$track_dir" | grep -oE '^[0-9]+' || true)"
    if [ "$track_num" = "01" ]; then
      prefix="linux_tlpi"
    elif [ "$track_num" = "02" ]; then
      prefix="linux_cli"
    else
      prefix="linux${track_num}"
    fi
    section_dir="$(echo "$item_dir" | cut -d/ -f3)"
    leaf_dir="$(echo "$item_dir" | cut -d/ -f4)"
    ;;
  jongmanbook)
    prefix="jongman"
    section_dir="$(echo "$item_dir" | cut -d/ -f2)"
    leaf_dir="$(echo "$item_dir" | cut -d/ -f3)"
    ;;
  knuth)
    prefix="knuth"
    section_dir="$(echo "$item_dir" | cut -d/ -f2)"
    leaf_dir="$(echo "$item_dir" | cut -d/ -f3)"
    ;;
  *)
    echo "알 수 없는 폴더입니다: $root_dir (stone-lecture, c-and-cpp, linux, jongmanbook 또는 knuth 이어야 함)" >&2
    exit 1
    ;;
esac

section_num="$(echo "$section_dir" | grep -oE '^[0-9]+' || true)"
item_num="$(echo "$leaf_dir" | grep -oE '^[0-9]+' || true)"

if [ -z "$section_num" ] || [ -z "$item_num" ]; then
  echo "폴더 구조에서 번호를 읽을 수 없습니다: $item_dir" >&2
  exit 1
fi

target="${prefix}_${section_num}_${item_num}_test"
build_dir="cmake-build-practice"

# Fast-path: GoogleTest 가 이미 빌드되어 있다면 단일 테스트를 0.2초 내로 직접 초고속 빌드 및 실행
test_file="practice/$item_dir/test.cpp"
if [ ! -f "$test_file" ] && [ -f "$item_dir/test.cpp" ]; then
  test_file="$item_dir/test.cpp"
fi

if [ ! -f "$test_file" ]; then
  echo "test.cpp 파일을 찾을 수 없습니다: $item_dir" >&2
  exit 1
fi

if [ -f "$test_file" ] && [ -f "$build_dir/lib/libgtest_main.a" ]; then
  item_folder="$(dirname "$test_file")"
  cxx_std="${CXX_STD:-c++20}"
  if grep -qE "(<print>|std::println)" "$test_file" 2>/dev/null; then
    cxx_std="c++23"
  fi
  helpers=()
  for f in "$item_folder"/*.cpp "$item_folder"/*.c; do
    [ -f "$f" ] || continue
    base="$(basename "$f")"
    if [ "$base" != "main.cpp" ] && [ "$base" != "test.cpp" ] && [ "$base" != "main.c" ]; then
      if ! grep -Eq 'int\s+main\s*\(' "$f" 2>/dev/null; then
        helpers+=("-x" "c++" "$f")
      fi
    fi
  done

  out_dir="$(mktemp -d)"
  out="$out_dir/test_bin"
  script_dir="$(cd "$(dirname "$0")" && pwd)"
  if "$script_dir/cxx_wrapper.sh" clang++ -std="$cxx_std" -Wno-attributes -Wno-character-conversion \
     -I "$build_dir/_deps/googletest-src/googletest/include" \
     -I "$item_folder" \
     "$test_file" ${helpers[@]+"${helpers[@]}"} \
     -x none "$build_dir/lib/libgtest_main.a" "$build_dir/lib/libgtest.a" -lpthread -o "$out" 2>/dev/null; then
    (cd "$item_folder" && "$out" "$@")
    rm -rf "$out_dir"
    exit 0
  fi
  rm -rf "$out_dir"
fi

if [ ! -d "$build_dir" ]; then
  echo "처음 실행이라 CMake 구성 + GoogleTest 다운로드를 먼저 합니다..." >&2
  cmake -S . -B "$build_dir" -DCMAKE_BUILD_TYPE=Debug
fi

if ! cmake --build "$build_dir" --target "$target" -j"$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)"; then
  echo "타겟 구성을 갱신하기 위해 CMake 를 재실행합니다..." >&2
  cmake -S . -B "$build_dir" -DCMAKE_BUILD_TYPE=Debug
  cmake --build "$build_dir" --target "$target" -j"$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)"
fi
"$build_dir/bin/$target" "$@"
