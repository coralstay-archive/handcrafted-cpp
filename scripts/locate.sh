#!/usr/bin/env bash
# 실습 파일의 도서명, 몇 장, 몇 절, 몇 문단/항목을 출력하는 네비게이터
#
# 사용법:
#   ./scripts/locate.sh practice/stone-lecture/01_문법_STL/03_타입과_타입변환/12_string_split_콤마/main.cpp
#   ./scripts/locate.sh split                    # 키워드로 검색하여 위치 찾기
#   ./scripts/locate.sh --tree                   # 전체 목차 트리 보기
set -euo pipefail
PYTHON_BIN="python3"
if [ -x /usr/bin/python3 ]; then
  PYTHON_BIN="/usr/bin/python3"
fi
exec "$PYTHON_BIN" "$(dirname "$0")/locate.py" "$@"
