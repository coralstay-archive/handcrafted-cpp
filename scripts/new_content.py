#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/new_content.py
새로운 도서/교안 추가 시 표준 스키마를 만족하는 content_data 패키지 스캐폴드를 자동 생성합니다.

책이 추가될 때도 사람이 수동으로 규격을 고민할 필요 없이,
표준화된 필수 필드(section_dir, section_title, num, slug, title, page, concept, target_code)가
채워진 템플릿 모듈을 생성하고 즉시 validate_content_data.py로 기계적 검증을 수행합니다.

사용법:
  ./scripts/new_content.py --id content09 --title "Modern C++ Design Patterns" --chapters 3
  ./scripts/new_content.py --id rust_basics --title "Rust 프로그래밍 기초" --chapters 5
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DATA_DIR = REPO_ROOT / "content_data"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^0-9a-zA-Z_]+", "_", text)
    return text.strip("_")


def create_new_content(book_id: str, book_title: str, num_chapters: int) -> int:
    # book_id 정규화: content09 -> content09_data
    clean_id = slugify(book_id)
    if not clean_id.endswith("_data"):
        pkg_name = f"{clean_id}_data"
    else:
        pkg_name = clean_id

    target_dir = CONTENT_DATA_DIR / pkg_name
    if target_dir.exists():
        print(f"⚠️ 이미 존재하는 도서 패키지입니다: {target_dir}", file=sys.stderr)
        print("기존 데이터를 덮어쓰지 않고 검증만 수행합니다.\n")
        return subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "validate_content_data.py"), pkg_name]).returncode

    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. __init__.py 생성
    init_file = target_dir / "__init__.py"
    init_content = f"""# -*- coding: utf-8 -*-
\"\"\"
{pkg_name}
- 도서명: 《{book_title}》
- 스키마 검증기(scripts/validate_content_data.py) 표준 규격 패키지
\"\"\"
"""
    init_file.write_text(init_content, encoding="utf-8")

    # 2. 챕터별 모듈 생성
    for ch in range(1, num_chapters + 1):
        ch_slug = f"ch{ch:02d}"
        mod_file = target_dir / f"{ch_slug}_items.py"
        sec_dir = f"{ch:02d}_{ch_slug}"
        sec_title = f"{ch}장. {book_title} 핵심 실습"

        mod_content = f"""# -*- coding: utf-8 -*-
\"\"\"
{pkg_name}: {sec_title}
\"\"\"

ITEMS = [
    {{
        "section_dir": "{sec_dir}",
        "section_title": "{sec_title}",
        "num": "01",
        "slug": "sample_exercise_01",
        "title": "{ch}.1 첫 번째 실습 항목",
        "page": "p.{ch * 10}",
        "concept": \"\"\"- **동작 원리**: 본 항목의 핵심 메커니즘과 C++ 표준 라이브러리/시스템콜 동작 원리를 기술합니다.
- **복잡도 관점**: 시간 복잡도와 메모리 공간 복잡도 설계 근거를 설명합니다.\"\"\",
        "target_code": r\"\"\"#include <iostream>

int main() {{
    std::cout << "=== {ch}.1 {book_title} 실습 ===" << std::endl;
    return 0;
}}
\"\"\",
    }},
    {{
        "section_dir": "{sec_dir}",
        "section_title": "{sec_title}",
        "num": "02",
        "slug": "sample_exercise_02",
        "title": "{ch}.2 두 번째 심화 실습",
        "page": "p.{ch * 10 + 5}",
        "concept": \"\"\"- **심화 원리**: 예외 처리, 경계값 엣지 케이스 및 고성능 최적화 기법을 기술합니다.
- **테스트 기준**: GoogleTest 단위 검증 기준을 사전에 정의합니다.\"\"\",
        "target_code": r\"\"\"#include <iostream>
#include <vector>

int main() {{
    std::vector<int> data = {{1, 2, 3}};
    std::cout << "Size: " << data.size() << std::endl;
    return 0;
}}
\"\"\",
    }},
]
"""
        mod_file.write_text(mod_content, encoding="utf-8")

    print(f"✨ 새로운 도서 패키지 생성 완료: {target_dir}")
    print(f"   • 도서명: 《{book_title}》")
    print(f"   • 생성 챕터 수: {num_chapters}개 (ch01_items.py ~ ch{num_chapters:02d}_items.py)\n")

    # 3. 생성 직후 즉시 스키마 기계적 강제 검증 수행
    print("🔍 [검증] 생성된 도서 패키지 표준 스키마 즉시 기계 검증 실행...")
    validator = REPO_ROOT / "scripts" / "validate_content_data.py"
    return subprocess.run([sys.executable, str(validator), pkg_name]).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="새로운 도서/교안 추가 시 표준 스키마 템플릿 패키지를 자동 생성하고 검증합니다."
    )
    parser.add_argument("--id", required=True, help="도서 식별자 (예: content09, modern_cpp, rust_primer)")
    parser.add_argument("--title", required=True, help="도서 정식 한글/영문 제목 (예: 'Modern C++ Design Patterns')")
    parser.add_argument("--chapters", type=int, default=3, help="초기 생성할 챕터 모듈 개수 (기본값: 3)")
    args = parser.parse_args()

    return create_new_content(args.id, args.title, args.chapters)


if __name__ == "__main__":
    sys.exit(main())
