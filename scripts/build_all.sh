#!/usr/bin/env bash
# practice-01/02/03 아래 모든 main.cpp + test.cpp 가 컴파일되는지 한 번에 검증한다.
# (CMake 로 절/항목마다 독립된 실행파일 타겟 + GoogleTest 타겟을 구성해서 빌드한다.)
# 최초 실행시 GoogleTest 를 다운로드하므로 인터넷 연결이 필요하다.
set -euo pipefail
cd "$(dirname "$0")/.."

build_dir="cmake-build-practice"
cmake -S . -B "$build_dir" -DCMAKE_BUILD_TYPE=Debug
cmake --build "$build_dir" -j"$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)"
