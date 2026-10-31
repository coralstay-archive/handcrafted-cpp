#!/usr/bin/env bash
# ==============================================================================
# handcrafted-cpp Linux Track Runner
# 리눅스 시스템 프로그래밍(C/C++17) 및 셸 자동화 스크립트를 빌드/실행한다.
#
# 사용법:
#   ./scripts/linux_run.sh practice/linux/01_tlpi_system_programming/01_file_io/01_copy_file_lowlevel
#   ./scripts/linux_run.sh practice/linux/02_cli_and_shell_automation/01_pipeline_and_filters/01_pipes_stdin_stdout
#   ./scripts/linux_run.sh --docker <경로>   # Docker Linux 컨테이너 환경에서 강제 실행
# ==============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

use_docker=false
if [ "${1:-}" = "--docker" ]; then
  use_docker=true
  shift
fi

if [ "$#" -lt 1 ]; then
  echo "사용법: $0 [--docker] <폴더경로 또는 파일경로> [실행시 넘길 인자...]" >&2
  exit 1
fi

target="$1"
shift || true

# practice/ 접두사 보정
if [ ! -e "$target" ] && [ -e "practice/$target" ]; then
  target="practice/$target"
fi

if [ -d "$target" ]; then
  if [ -f "$target/main.cpp" ]; then
    src="$target/main.cpp"
    mode="cpp"
  elif [ -f "$target/script.sh" ]; then
    src="$target/script.sh"
    mode="sh"
  else
    echo "실행 가능한 main.cpp 또는 script.sh 가 없습니다: $target" >&2
    exit 1
  fi
else
  src="$target"
  if [[ "$src" == *.sh ]]; then
    mode="sh"
  else
    mode="cpp"
  fi
fi

# 1. Shell Script 실행 모드
if [ "$mode" = "sh" ]; then
  echo "=== [Bash Script Execution] $src ==="
  bash "$src" "$@"
  exit 0
fi

# 2. C++17 시스템 프로그래밍 실행 모드
# Docker 강제 실행 요청이거나 리눅스 전용 헤더(<sys/epoll.h> 등)가 감지되고 Docker 데몬이 실행 중인 경우
need_linux_kernel=false
if grep -qE "sys/epoll\.h|sys/inotify\.h|sys/eventfd\.h|sys/timerfd\.h|sys/signalfd\.h" "$src" 2>/dev/null; then
  need_linux_kernel=true
fi

if [ "$use_docker" = true ] || [ "$need_linux_kernel" = true ]; then
  if docker info >/dev/null 2>&1; then
    echo "=== [Docker Linux Container Run] $src ==="
    docker run --rm -v "$(pwd):/workspace" -w /workspace gcc:12 bash -c \
      "g++ -std=c++17 -O2 -Wall -Wextra -pthread '$src' -o /tmp/linux_app && /tmp/linux_app $*"
    exit 0
  elif [ "$use_docker" = true ]; then
    echo "[오류] Docker 데몬이 실행 중이지 않습니다. Docker Desktop을 실행하거나 일반 모드로 실행하세요." >&2
    exit 1
  else
    echo "[안내] 리눅스 전용 커널 API가 포함되어 있으나 호스트 macOS 호환 모드로 컴파일합니다 (Docker 실행 시 순정 리눅스 커널 위에서 동작)."
  fi
fi

# 호스트 macOS 네이티브 빌드 & 실행
out_dir="$(mktemp -d)"
out="$out_dir/a.out"
trap 'rm -rf "$out_dir"' EXIT

echo "=== [Native Host Run (-std=c++17)] $src ==="
./scripts/cxx_wrapper.sh g++ -std=c++17 -O1 -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -pthread "$src" -o "$out"
"$out" "$@"
