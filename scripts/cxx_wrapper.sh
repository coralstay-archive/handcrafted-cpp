#!/usr/bin/env bash
# 컴파일러 래퍼 스크립트 (CMake RULE_LAUNCH_COMPILE 및 scripts/run.sh 용)
# 소스 파일에 [[snippet]] / [[snippet(...)]] 또는 @snippet 태그가 있으면,
# 원본 파일은 그대로 보존한 채 컴파일러에게 넘기는 스트림에서만 동일 길이의 공백으로 치환하여
# 클래스/함수/템플릿 어디에 붙이든 줄 번호(Line)와 칸 번호(Column) 왜곡 없이 100% 컴파일되게 한다.

set -euo pipefail

# 1. 빠른 경로(Fast path): 인자 중 snippet 태그가 포함된 소스 파일이 있는지 확인
needs_filter=0
for arg in "$@"; do
  case "$arg" in
    *.cpp|*.cc|*.cxx|*.c)
      if [ -f "$arg" ] && grep -Eq '(\[\[\s*snippet|@snippet)' "$arg" 2>/dev/null; then
        needs_filter=1
        break
      fi
      ;;
  esac
done

# 태그가 없는 일반 파일(예: GoogleTest 등)은 오버헤드 없이 즉시 원본 명령 실행
if [ "$needs_filter" -eq 0 ]; then
  exec "$@"
fi

# 2. 태그가 포함된 파일이 있으면 임시 디렉토리에서 전처리 후 컴파일
tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

new_args=()
idx=0

for arg in "$@"; do
  case "$arg" in
    *.cpp|*.cc|*.cxx|*.c)
      if [ -f "$arg" ] && grep -Eq '(\[\[\s*snippet|@snippet)' "$arg" 2>/dev/null; then
        idx=$((idx + 1))
        src_dir="$(cd "$(dirname "$arg")" && pwd)"
        src_base="$(basename "$arg")"
        abs_src="$src_dir/$src_base"
        tmp_src="$tmp_dir/${idx}_${src_base}"

        # 원본 파일의 줄 번호/컬럼 번호/파일명을 디버거와 에러 메시지에서 100% 유지하기 위해
        # #line 1 "원본절대경로" 를 삽입하고, [[snippet(...)]] / @snippet(...) 을 동일 길이의 공백으로 치환
        python3 - "$abs_src" "$tmp_src" << 'PYEOF'
import re
import sys

src_path, dst_path = sys.argv[1], sys.argv[2]
with open(src_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

pattern = re.compile(
    r'(?:\[\[\s*snippet(?:\s*\((?:[^()\\]|\\.|"[^"]*"|\'[^\']*\')*\))?\s*\]\]'
    r'|@snippet(?:\s*\((?:[^()\\]|\\.|"[^"]*"|\'[^\']*\')*\))?)'
)
cleaned = pattern.sub(lambda m: re.sub(r'[^\n]', ' ', m.group(0)), content)

escaped_path = src_path.replace('\\', '\\\\').replace('"', '\\"')
with open(dst_path, 'w', encoding='utf-8') as f:
    f.write(f'#line 1 "{escaped_path}"\n')
    f.write(cleaned)
PYEOF

        # 원본 소스 폴더의 상대경로 #include "..." 가 정상 동작하도록 -I 추가
        new_args+=("-I$src_dir" "$tmp_src")
      else
        new_args+=("$arg")
      fi
      ;;
    *)
      new_args+=("$arg")
      ;;
  esac
done

"${new_args[@]}"
