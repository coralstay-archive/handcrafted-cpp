#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/apply_file_frontmatter.py
모든 practice/ 하위 말단 노드 파일(C/C++, Shell, Python, Markdown)의 상단 주석에
고유 식별자(@file), 전체 상대 경로(@path), 참고 도서명(@book)을
명확히 기록하는 표준화 프론트매터를 일괄 생성/갱신합니다.

기존 프론트매터를 모두 감지하여 깔끔히 제거한 뒤 최신 표준으로 재작성하며,
'교안을 옆에 두고~' 문구를 '《10주완성 C++ 코딩테스트》(큰돌 저)를 참고하여~' 로
참고 도서명을 정확히 명시하도록 일괄 보정합니다.
"""

import os
import re
import sys
from pathlib import Path
from typing import Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
PRACTICE_DIR = (REPO_ROOT / "practice").resolve()

EXT_CPP = {".cpp", ".c", ".cc", ".h", ".hpp", ".cppm"}
EXT_SH = {".sh"}
EXT_PY = {".py"}
EXT_MD = {".md"}

BOOK_TITLES = {
    "stone-lecture": "《10주완성 C++ 코딩테스트》(큰돌 저)",
    "01_c_300": "《초보자를 위한 C 언어 300제》(김용성 저, 정보문화사)",
    "02_c_100": "《실무자를 위한 C 언어 100제》(김용성 저, 정보문화사)",
    "03_tour_of_cpp": "《A Tour of C++ 3rd Edition》(Bjarne Stroustrup 저, Addison-Wesley)",
    "04_cpp_stl": "《뇌를 자극하는 C++ STL 프로그래밍》(최흥배 저, 한빛미디어)",
    "05_high_perf_cpp": "《고성능을 위한 C++ (C++ High Performance 2nd Ed)》(Björn Andrist & Viktor Sehr 저, Packt)",
    "06_algo_generic": "《알고리즘 산책: 수학에서 제네릭 프로그래밍까지》(Alexander Stepanov & Daniel Rose 저, 길벗)",
    "07_extreme_c": "《전문가를 위한 C (Extreme C)》(Kamran Amini 저, 길벗 / Packt)",
    "08_prof_cpp": "《전문가를 위한 C++ (Professional C++ 6th Edition)》(Marc Gregoire 저, 제이펍 / Wiley)",
    "01_tlpi_system_programming": "《리눅스 프로그래밍 인터페이스 (The Linux Programming Interface) 1·2권》(Michael Kerrisk 저, 길벗 / No Starch)",
    "02_cli_and_shell_automation": "《Efficient Linux at the Command Line & Adventures with the Linux Command Line》(Daniel J. Barrett & William Shotts 저)",
    "jongmanbook": "《프로그래밍 대회에서 배우는 알고리즘 문제 해결 전략 (종만북 1·2권)》(구종만 저, 인사이트)",
    "knuth": "《The Art of Computer Programming Vol 4A: Combinatorial Algorithms》(Donald E. Knuth 저, Addison-Wesley)",
}


def get_book_title(rel_path: Path) -> str:
    """practice 기준 상대 경로에서 참고 도서명을 정확히 반환합니다."""
    parts = rel_path.parts
    if not parts:
        return "C/C++ & Linux Engineering Curriculum"
    root_seg = parts[0]
    if root_seg == "stone-lecture":
        return BOOK_TITLES["stone-lecture"]
    elif root_seg == "c-and-cpp" and len(parts) > 1:
        return BOOK_TITLES.get(parts[1], "C/C++ 도서 실습 트랙")
    elif root_seg == "linux" and len(parts) > 1:
        return BOOK_TITLES.get(parts[1], "Linux 시스템 & CLI 실습 트랙")
    elif root_seg == "jongmanbook":
        return BOOK_TITLES["jongmanbook"]
    elif root_seg == "knuth":
        return BOOK_TITLES["knuth"]
    return "C/C++ & Linux Engineering Curriculum"


def make_file_id(rel_path: Path) -> str:
    """
    rel_path: practice 기준 상대 경로 (예: stone-lecture/01_문법_STL/01_기본/03_define/main.cpp)
    반환값: stone-lecture-01_문법_STL_01_기본_03_define_main.cpp
    """
    parts = list(rel_path.parts)
    if len(parts) >= 2:
        return f"{parts[0]}-" + "_".join(parts[1:])
    return rel_path.name


def strip_existing_banner(content: str, ext: str) -> Tuple[str, str]:
    """기존 프론트매터 배너를 제거하고 (shebang, body) 튜플을 반환합니다."""
    shebang = ""
    body = content
    if ext in (EXT_SH | EXT_PY) and content.startswith("#!"):
        lines = content.split("\n", 1)
        shebang = lines[0]
        body = lines[1] if len(lines) > 1 else ""

    if ext in EXT_CPP:
        pattern = re.compile(r"^\s*// =+\s*\n(?:\s*// @[^\n]*\n)+\s*// =+\s*\n\n?", re.MULTILINE)
    elif ext in (EXT_SH | EXT_PY):
        pattern = re.compile(r"^\s*# =+\s*\n(?:\s*# @[^\n]*\n)+\s*# =+\s*\n\n?", re.MULTILINE)
    elif ext in EXT_MD:
        pattern = re.compile(r"^\s*<!--\s*\n=+\s*\n(?:@[^\n]*\n)+=+\s*\n-->\s*\n\n?", re.MULTILINE)
    else:
        return shebang, body

    body = pattern.sub("", body, count=1)
    return shebang, body


def process_file(file_path: Path) -> bool:
    ext = file_path.suffix.lower()
    if ext not in (EXT_CPP | EXT_SH | EXT_PY | EXT_MD):
        return False

    abs_file = file_path.resolve()
    try:
        content = abs_file.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[WARN] Failed to read {abs_file}: {e}", file=sys.stderr)
        return False

    original_content = content
    rel_path = abs_file.relative_to(PRACTICE_DIR)
    file_id = make_file_id(rel_path)
    repo_path = f"practice/{rel_path.as_posix()}"
    book_title = get_book_title(rel_path)

    # 1. '교안을 옆에 두고~' 문구를 도서명 명시 문구로 일괄 치환
    if "교안을 옆에 두고 아래 내용을 직접 타이핑해서 완성해보세요." in content:
        content = content.replace(
            "// 교안을 옆에 두고 아래 내용을 직접 타이핑해서 완성해보세요.",
            f"// {book_title}를 참고하여 아래 내용을 직접 타이핑해서 완성해보세요."
        )

    shebang, body = strip_existing_banner(content, ext)

    new_content = ""
    if ext in EXT_CPP:
        banner = (
            "// ==============================================================================\n"
            f"// @file: {file_id}\n"
            f"// @path: {repo_path}\n"
            f"// @book: {book_title}\n"
            "// ==============================================================================\n"
        )
        new_content = banner + ("\n" if not body.startswith("\n") and body else "") + body

    elif ext in (EXT_SH | EXT_PY):
        banner = (
            "# ==============================================================================\n"
            f"# @file: {file_id}\n"
            f"# @path: {repo_path}\n"
            f"# @book: {book_title}\n"
            "# ==============================================================================\n"
        )
        clean_body = body.lstrip("\n")
        if shebang:
            new_content = f"{shebang}\n{banner}\n{clean_body}"
        else:
            new_content = f"{banner}\n{clean_body}"

    elif ext in EXT_MD:
        banner = (
            "<!--\n"
            "==============================================================================\n"
            f"@file: {file_id}\n"
            f"@path: {repo_path}\n"
            f"@book: {book_title}\n"
            "==============================================================================\n"
            "-->\n"
        )
        new_content = banner + ("\n" if not body.startswith("\n") and body else "") + body

    if new_content != original_content:
        prev_mode = abs_file.stat().st_mode & 0o777
        if not (prev_mode & 0o200):
            abs_file.chmod(0o644)
        abs_file.write_text(new_content, encoding="utf-8")
        abs_file.chmod(prev_mode)
        return True
    return False


def main():
    if not PRACTICE_DIR.exists():
        print(f"Error: {PRACTICE_DIR} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"🔄 모든 기존 프론트매터를 정규화하고 정확한 도서명(@book)을 반영합니다...")
    print(f"🔍 대상 경로: {PRACTICE_DIR}")
    total_scanned = 0
    total_updated = 0

    EXCLUDE_DIRS = {".git", ".skeleton", "assets", "build", "CMakeFiles", "googletest"}
    for root, dirs, files in os.walk(PRACTICE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in EXCLUDE_DIRS]
        for f in sorted(files):
            fp = Path(root) / f
            total_scanned += 1
            if process_file(fp):
                total_updated += 1

    print(f"✨ 프론트매터 및 참고 도서명 재작성 완료!")
    print(f"📊 스캔 파일 수: {total_scanned}개")
    print(f"📝 업데이트 파일 수: {total_updated}개")


if __name__ == "__main__":
    main()
