#!/usr/bin/env bash
# ==============================================================================
# man7 Linux 공식 매뉴얼 페이지 오프라인 뷰어 (man7.org / Linux man-pages 6.20)
#
# 사용법:
#   ./scripts/man.sh <함수명/시스템콜> [섹션번호]
#   ./scripts/man.sh epoll_create
#   ./scripts/man.sh read 2
#   ./scripts/man.sh pthread_create
#   ./scripts/man.sh --list <키워드>
# ==============================================================================

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAN_DIR="$REPO_ROOT/docs/linux/01_tlpi_system_programming/man-pages/man"
if [ ! -d "$MAN_DIR" ]; then
    MAN_DIR="$REPO_ROOT/docs/linux/man-pages/man"
fi

if [ ! -d "$MAN_DIR" ]; then
    echo "❌ Error: man-pages directory not found at '$MAN_DIR'."
    exit 1
fi

if [ "$#" -lt 1 ]; then
    echo "사용법: $0 <시스템콜/함수명> [섹션번호 (예: 2, 3, 7)]"
    echo "예시:"
    echo "  $0 epoll_create        # epoll_create(2) 시스템콜 매뉴얼 열람"
    echo "  $0 read 2              # read(2) 시스템콜 열람"
    echo "  $0 pthread_create      # pthread_create(3) 함수 매뉴얼 열람"
    echo "  $0 --list socket       # socket 관련 전체 매뉴얼 목록 검색"
    exit 1
fi

if [ "$1" == "--list" ] || [ "$1" == "-l" ]; then
    if [ -z "${2:-}" ]; then
        echo "❌ 검색할 키워드를 입력하세요. 예: $0 --list epoll"
        exit 1
    fi
    KEYWORD="$2"
    echo "🔍 '$KEYWORD' 매뉴얼 검색 결과:"
    find "$MAN_DIR" -type f -name "*${KEYWORD}*.[1-8]*" | sort | while read -r page; do
        sec="$(basename "$(dirname "$page")")"
        base="$(basename "$page")"
        echo "  - $base ($sec): $page"
    done
    exit 0
fi

TARGET="$1"
SECTION="${2:-}"

MATCH=""
if [ -n "$SECTION" ]; then
    # 특정 섹션 지정 검색
    MATCH=$(find "$MAN_DIR/man${SECTION}"* -type f \( -name "${TARGET}.${SECTION}*" -o -name "${TARGET}.${SECTION}" \) 2>/dev/null | head -n 1 || true)
fi

if [ -z "$MATCH" ]; then
    # 우선순위: man2(시스템콜) -> man3(라이브러리) -> man7(개요) -> 기타
    for s in 2 3 7 1 4 5 8; do
        MATCH=$(find "$MAN_DIR/man${s}"* -type f \( -name "${TARGET}.${s}*" -o -name "${TARGET}.${s}" \) 2>/dev/null | head -n 1 || true)
        if [ -n "$MATCH" ]; then break; fi
    done
fi

if [ -z "$MATCH" ]; then
    # 와일드카드 부분 일치 검색
    MATCH=$(find "$MAN_DIR" -type f -name "*${TARGET}*.[1-8]*" 2>/dev/null | head -n 1 || true)
fi

if [ -z "$MATCH" ] || [ ! -f "$MATCH" ]; then
    echo "❌ '$TARGET'에 대한 man7 매뉴얼 페이지를 찾을 수 없습니다."
    echo "💡 목록 검색: $0 --list $TARGET"
    exit 1
fi

echo "📖 열람 중: $(basename "$MATCH") [man7.org Linux man-pages 6.20]"
echo "───────────────────────────────────────────────────────────────"

if command -v mandoc >/dev/null 2>&1; then
    mandoc "$MATCH" | (command -v less >/dev/null 2>&1 && less -R || cat)
else
    cat "$MATCH"
fi
