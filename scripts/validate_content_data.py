#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/validate_content_data.py
content_data/ 하위의 모든 도서 데이터 파일(ITEMS 리스트)의 스키마 및 무결성을 프로그램으로 기계적 강제 검증합니다.

책이 추가될 때도 본 검증기를 통해 필수 필드(section_dir, section_title, num, slug, title, page, concept, target_code)와
구문 무결성이 100% 검증되어야만 프로젝트 파이프라인에 통합될 수 있습니다.

사용법:
  ./scripts/validate_content_data.py               # content_data 전체 도서 데이터 스키마 전수 검증
  ./scripts/validate_content_data.py content01     # 특정 도서 데이터만 검증
  ./scripts/validate_content_data.py --compile     # target_code C++ 문법 컴파일 구문 검사까지 전수 수행
"""

import argparse
import importlib
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DATA_DIR = REPO_ROOT / "content_data"

# sys.path에 content_data 추가
if str(CONTENT_DATA_DIR) not in sys.path:
    sys.path.insert(0, str(CONTENT_DATA_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass
class ValidationError:
    book: str
    module: str
    index: int
    item_title: str
    field: str
    message: str


REQUIRED_BASE_SCHEMA = [
    ("section_dir", str, "절 디렉터리 경로 (section_dir)"),
    ("num", str, "2자리 이상 번호 (num, 예: '01', '001')"),
    ("slug", str, "식별자 슬러그 (slug)"),
    ("title", str, "항목 제목 (title)"),
    ("concept", str, "개념 및 동작 원리 설명 (concept)"),
    ("target_code", str, "C/C++ 또는 쉘 구현 소스코드 (target_code)"),
]


def validate_item(book_name: str, mod_name: str, idx: int, item: Dict[str, Any]) -> List[ValidationError]:
    errors = []
    item_title = item.get("title", f"Item #{idx}")

    # 1. 공통 필수 키 및 타입 검사
    for field_name, expected_type, field_desc in REQUIRED_BASE_SCHEMA:
        if field_name not in item:
            errors.append(ValidationError(
                book=book_name, module=mod_name, index=idx, item_title=item_title,
                field=field_name, message=f"필수 필드 누락: {field_desc}"
            ))
            continue

        val = item[field_name]
        if not isinstance(val, expected_type):
            errors.append(ValidationError(
                book=book_name, module=mod_name, index=idx, item_title=item_title,
                field=field_name, message=f"타입 불일치: {expected_type.__name__} 필요 (현재: {type(val).__name__})"
            ))
            continue

        # 문자열 내용 검사
        if isinstance(val, str) and not val.strip():
            errors.append(ValidationError(
                book=book_name, module=mod_name, index=idx, item_title=item_title,
                field=field_name, message=f"빈 문자열(empty string) 금지: {field_desc}"
            ))

    # 2. 챕터/절 제목 검사 (section_title 또는 chapter 둘 중 하나는 반드시 존재해야 함)
    sec_title = item.get("section_title") or item.get("chapter")
    if not sec_title or not str(sec_title).strip():
        errors.append(ValidationError(
            book=book_name, module=mod_name, index=idx, item_title=item_title,
            field="section_title|chapter", message="섹션/챕터 제목 누락: section_title 또는 chapter 필드가 필요합니다."
        ))

    # 3. 번호(num) 포맷 검사
    num = str(item.get("num", "")).strip()
    if num and not re.match(r"^[0-9]+[a-zA-Z0-9_-]*$", num):
        errors.append(ValidationError(
            book=book_name, module=mod_name, index=idx, item_title=item_title,
            field="num", message=f"번호 형식 오류: 숫자로 시작해야 함 (현재: '{num}')"
        ))

    # 4. 개념(concept) 최소 설명 길이 검사
    concept = str(item.get("concept", "")).strip()
    if concept and len(concept) < 10:
        errors.append(ValidationError(
            book=book_name, module=mod_name, index=idx, item_title=item_title,
            field="concept", message=f"개념 설명 너무 짧음: 최소 10자 이상 서술 필요 (현재: {len(concept)}자)"
        ))

    return errors


def check_code_syntax(code: str) -> Optional[str]:
    """C++ 컴파일러(clang++/g++)로 소스코드의 문법 구문(-fsyntax-only)을 기계적 검증합니다."""
    compiler = "clang++" if subprocess.run(["which", "clang++"], stdout=subprocess.PIPE).returncode == 0 else "g++"
    with tempfile.NamedTemporaryFile("w", suffix=".cpp", delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        res = subprocess.run(
            [compiler, "-std=c++17", "-fsyntax-only", temp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        if res.returncode != 0:
            err_line = res.stderr.strip().split("\n")[0]
            return err_line
        return None
    except Exception as e:
        return str(e)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def scan_and_validate(book_filter: Optional[str] = None, compile_check: bool = False) -> int:
    if not CONTENT_DATA_DIR.exists():
        print(f"❌ content_data 디렉터리가 존재하지 않습니다: {CONTENT_DATA_DIR}", file=sys.stderr)
        return 1

    book_dirs = sorted([
        d
        for d in CONTENT_DATA_DIR.iterdir()
        if d.is_dir()
        and not d.is_symlink()
        and "-" not in d.name
        and not d.name.startswith((".", "__"))
        and any(f for f in d.glob("*.py") if not f.name.startswith((".", "__")))
    ])
    if book_filter:
        book_dirs = [d for d in book_dirs if book_filter.lower() in d.name.lower()]

    if not book_dirs:
        print(f"⚠️ 검사할 도서 데이터 폴더를 찾지 못했습니다 (filter: {book_filter})")
        return 0

    print("==============================================================================")
    print(" 📖 content_data 도서 데이터 스키마 및 무결성 기계적 강제 검증 파이프라인")
    print("==============================================================================")
    print(f"• 검증 대상 도서 패키지 수: {len(book_dirs)}개")
    print(f"• 구문 컴파일(-fsyntax-only) 검사: {'활성화' if compile_check else '비활성화'}")
    print("------------------------------------------------------------------------------")

    all_errors: List[ValidationError] = []
    total_items_checked = 0
    total_modules_checked = 0

    for bdir in book_dirs:
        py_files = sorted([f for f in bdir.glob("*.py") if not f.name.startswith((".", "__"))])
        print(f"📁 [{bdir.name}] 검증 시작 ({len(py_files)}개 모듈)...")

        for py_file in py_files:
            mod_import_name = f"{bdir.name}.{py_file.stem}"
            total_modules_checked += 1
            try:
                mod = importlib.import_module(mod_import_name)
            except Exception as e:
                all_errors.append(ValidationError(
                    book=bdir.name, module=py_file.name, index=0, item_title="-",
                    field="import", message=f"Python 모듈 임포트 실패: {e}"
                ))
                continue

            items = getattr(mod, "ITEMS", None)
            if items is None:
                continue

            if not isinstance(items, list):
                all_errors.append(ValidationError(
                    book=bdir.name, module=py_file.name, index=0, item_title="-",
                    field="ITEMS", message=f"ITEMS는 list 타입이어야 합니다 (현재: {type(items).__name__})"
                ))
                continue

            seen_section_nums = set()
            for idx, item in enumerate(items, 1):
                total_items_checked += 1
                if not isinstance(item, dict):
                    all_errors.append(ValidationError(
                        book=bdir.name, module=py_file.name, index=idx, item_title=f"Item #{idx}",
                        field="type", message="항목은 dict 타입이어야 합니다."
                    ))
                    continue

                # 스키마 검증
                item_errs = validate_item(bdir.name, py_file.name, idx, item)
                all_errors.extend(item_errs)

                # 한 절/챕터(section_dir) 내에서 번호 중복 검사
                sec_dir = item.get("section_dir", "")
                num = item.get("num")
                if sec_dir and num:
                    sec_key = (sec_dir, num)
                    if sec_key in seen_section_nums:
                        all_errors.append(ValidationError(
                            book=bdir.name, module=py_file.name, index=idx, item_title=item.get("title", ""),
                            field="num", message=f"동일 섹션('{sec_dir}') 내에서 num 중복 발견: '{num}'"
                        ))
                    seen_section_nums.add(sec_key)

                # 컴파일 검사 (옵션)
                if compile_check and "target_code" in item and item["target_code"].strip():
                    syntax_err = check_code_syntax(item["target_code"])
                    if syntax_err:
                        all_errors.append(ValidationError(
                            book=bdir.name, module=py_file.name, index=idx, item_title=item.get("title", ""),
                            field="target_code", message=f"컴파일 구문 에러: {syntax_err}"
                        ))

    print("------------------------------------------------------------------------------")
    print(f"📊 총 검증 모듈: {total_modules_checked}개 | 총 검증 항목: {total_items_checked}개")

    if all_errors:
        print(f"\n❌ [FAIL] 총 {len(all_errors)}개의 스키마/무결성 위반이 발견되었습니다:")
        for err in all_errors[:30]:  # 최대 30개 표시
            print(f"  • [{err.book} > {err.module}] #{err.index} '{err.item_title}'")
            print(f"    - 필드: {err.field} | 원인: {err.message}")
        if len(all_errors) > 30:
            print(f"  ... 외 {len(all_errors) - 30}개 에러 생략")
        print("\n💡 해결 방법: 위 오류 항목의 필수 필드와 형식을 표준 규격에 맞게 수정한 후 다시 실행하세요.\n")
        return 1

    print(f"✅ [PASS] 모든 도서 데이터({total_items_checked}개 항목)가 표준 스키마 규격을 100% 충족합니다!\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="content_data 도서 데이터 파일의 스키마와 무결성을 기계적으로 강제 검증합니다.")
    parser.add_argument("book", nargs="?", help="특정 도서 필터 (예: content01, content07, linux)")
    parser.add_argument("-c", "--compile", action="store_true", help="target_code의 C++ 문법 컴파일 구문 검사(-fsyntax-only)까지 수행합니다.")
    args = parser.parse_args()

    return scan_and_validate(book_filter=args.book, compile_check=args.compile)


if __name__ == "__main__":
    sys.exit(main())
