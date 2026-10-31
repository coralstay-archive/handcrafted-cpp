#!/usr/bin/env bash
# ==============================================================================
# handcrafted-cpp Master TOC & Scaffold Sync Pipeline
# 목차 트리구조나 메타데이터 변경 시 전수 스캐폴드, 프론트매터, 색인을 일괄 갱신한다.
# ==============================================================================
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=============================================================================="
echo " 🔄 handcrafted-cpp 목차 및 트리구조 동기화 파이프라인 (Master Sync)"
echo "=============================================================================="

PYTHON_BIN="python3"
if [ -x /usr/bin/python3 ]; then
  PYTHON_BIN="/usr/bin/python3"
fi

# 1. 모든 말단 파일의 @file / @path 주석 프론트매터 동기화
echo -e "\n[Step 1/2] 말단 노드 파일 주석 프론트매터 동기화..."
"$PYTHON_BIN" scripts/apply_file_frontmatter.py

# 2. 동적 목차 트리 출력 및 무결성 검증
echo -e "\n[Step 2/2] 동적 목차 트리 무결성 검증..."
"$PYTHON_BIN" scripts/locate.py --tree

echo -e "\n✨ 목차 및 트리구조 동기화가 성공적으로 완료되었습니다!"
