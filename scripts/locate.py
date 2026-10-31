#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/locate.py
실습 파일의 정확한 도서명, 몇 장, 몇 절, 몇 문단(항목/스텝), 페이지 번호를
동적으로 파싱하여 터미널에 구조화된 카드 형태로 출력하는 위치 색인 네비게이터.

사용법:
  ./scripts/locate.sh practice/stone-lecture/01_문법_STL/03_타입과_타입변환/12_string_split_콤마/main.cpp
  ./scripts/locate.sh split                    # 키워드로 검색하여 위치 찾기
  ./scripts/locate.sh --tree stone-lecture     # 특정 도서 목차 트리 보기
  ./scripts/locate.sh --json <경로>            # JSON 형식 출력
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
PRACTICE_DIR = REPO_ROOT / "practice"

TRACK_TITLES = {
    "stone-lecture": "큰돌 C++ 알고리즘 강의 교안",
    "01_c_300": "초보자를 위한 C언어 300제",
    "02_c_100": "실무자를 위한 C언어 100제",
    "03_tour_of_cpp": "A Tour of C++ 3rd Edition (Bjarne Stroustrup)",
    "04_cpp_stl": "C++ STL 프로그래밍",
    "05_high_perf_cpp": "고성능을 위한 C++ (High Performance C++)",
    "06_algo_generic": "알고리즘 산책: 수학에서 제네릭 프로그래밍까지 (Alexander Stepanov)",
    "07_extreme_c": "전문가를 위한 C (Extreme C, Kamran Amini)",
    "08_prof_cpp": "전문가를 위한 C++ 6th Edition (Marc Gregoire)",
    "01_tlpi_system_programming": "The Linux Programming Interface (TLPI, Michael Kerrisk)",
    "02_cli_and_shell_automation": "Linux CLI & Shell Script Automation (Barrett & Shotts)",
    "03_bpf_performance_tools": "BPF 성능 분석 도구 (BPF Performance Tools, Brendan Gregg)",
    "04_arm_kernel": "코드로 알아보는 ARM 리눅스 커널 (강진우 저, 제이펍)",
    "jongmanbook": "알고리즘 문제 해결 전략 (종만북 1·2권, 구종만)",
    "knuth": "The Art of Computer Programming Vol 4A: Combinatorial Algorithms (Donald E. Knuth)",
}


def clean_frontmatter(text: str) -> str:
    """프론트매터 주석 블록을 건너뛰고 실제 본문 텍스트를 반환합니다."""
    # HTML 주석 프론트매터 제거
    text = re.sub(r"^\s*<!--\s*\n=+\s*\n@file:[^\n]*\n@path:[^\n]*\n=+\s*\n-->\s*\n?", "", text, flags=re.MULTILINE)
    # C++ 주석 프론트매터 제거
    text = re.sub(r"^\s*// =+\s*\n\s*// @file:[^\n]*\n\s*// @path:[^\n]*\n\s*// =+\s*\n?", "", text, flags=re.MULTILINE)
    # Bash/Python 주석 프론트매터 제거
    text = re.sub(r"^\s*# =+\s*\n\s*# @file:[^\n]*\n\s*# @path:[^\n]*\n\s*# =+\s*\n?", "", text, flags=re.MULTILINE)
    return text.strip()


def parse_item_info(target_path: Path) -> Dict[str, Any]:
    """주어진 파일 또는 디렉터리 경로의 장, 절, 문단, 페이지, 스니펫 정보를 파싱합니다."""
    abs_target = target_path.resolve()
    if abs_target.is_file():
        item_dir = abs_target.parent
        active_file = abs_target
    else:
        item_dir = abs_target
        active_file = item_dir / "main.cpp"
        if not active_file.exists():
            for cand in item_dir.glob("*.cpp"):
                active_file = cand
                break
        if not active_file.exists():
            active_file = item_dir / "README.md"

    # practice/ 기준 상대 경로 분해
    abs_practice = PRACTICE_DIR.resolve()
    try:
        rel = item_dir.relative_to(abs_practice)
        parts = rel.parts
    except ValueError:
        rel = item_dir
        parts = rel.parts

    track_key = ""
    book_title = "알 수 없는 트랙"
    chapter_str = "-"
    section_str = "-"
    item_str = "-"
    page_str = ""
    snippet_str = ""
    summary_str = ""

    # 1. 트랙 판별 및 계층 매핑
    if len(parts) >= 1:
        root_seg = parts[0]
        if root_seg == "stone-lecture":
            track_key = "stone-lecture"
            book_title = TRACK_TITLES["stone-lecture"]
            sub_part = parts[1] if len(parts) > 1 else ""
            sec_folder = parts[2] if len(parts) > 2 else ""
            item_folder = parts[3] if len(parts) > 3 else ""

            # sub_part: 01_문법_STL
            part_num = re.search(r"^\d+", sub_part).group() if re.search(r"^\d+", sub_part) else "1"
            chapter_str = f"Part {int(part_num)} ({sub_part.split('_', 1)[-1]})"

            # sec_folder: 03_타입과_타입변환
            sec_num = re.search(r"^\d+", sec_folder).group() if re.search(r"^\d+", sec_folder) else "1"
            section_str = f"{int(sec_num)}장/절 ({sec_folder.split('_', 1)[-1]})"

            # item_folder: 12_string_split_콤마
            it_num = re.search(r"^\d+", item_folder).group() if re.search(r"^\d+", item_folder) else "1"
            item_str = f"{int(it_num)}번째 문단/항목 ({item_folder.split('_', 1)[-1]})"

        elif root_seg == "c-and-cpp":
            book_code = parts[1] if len(parts) > 1 else ""
            track_key = book_code
            book_title = TRACK_TITLES.get(book_code, f"C/C++ 도서 ({book_code})")
            ch_folder = parts[2] if len(parts) > 2 else ""
            item_folder = parts[3] if len(parts) > 3 else ""

            ch_num = re.search(r"^\d+", ch_folder).group() if re.search(r"^\d+", ch_folder) else "1"
            chapter_str = f"{int(ch_num)}장 ({ch_folder.split('_', 1)[-1]})"

            it_num = re.search(r"^\d+", item_folder).group() if re.search(r"^\d+", item_folder) else "1"
            item_str = f"{int(it_num)}번째 문단/예제 ({item_folder.split('_', 1)[-1]})"
            section_str = f"{int(ch_num)}장 세부 실습"

        elif root_seg == "linux":
            linux_track = parts[1] if len(parts) > 1 else ""
            track_key = linux_track
            book_title = TRACK_TITLES.get(linux_track, f"Linux 트랙 ({linux_track})")
            ch_folder = parts[2] if len(parts) > 2 else ""
            item_folder = parts[3] if len(parts) > 3 else ""

            ch_num = re.search(r"^\d+", ch_folder).group() if re.search(r"^\d+", ch_folder) else "1"
            chapter_str = f"{int(ch_num)}장 ({ch_folder.split('_', 1)[-1]})"

            it_num = re.search(r"^\d+", item_folder).group() if re.search(r"^\d+", item_folder) else "1"
            item_str = f"{int(it_num)}번째 항목/리스팅 ({item_folder.split('_', 1)[-1]})"
            section_str = f"{int(ch_num)}장 시스템 프로그래밍"

        elif root_seg == "jongmanbook":
            track_key = "jongmanbook"
            book_title = TRACK_TITLES["jongmanbook"]
            ch_folder = parts[1] if len(parts) > 1 else ""
            item_folder = parts[2] if len(parts) > 2 else ""

            ch_num = re.search(r"^\d+", ch_folder).group() if re.search(r"^\d+", ch_folder) else "1"
            chapter_str = f"{int(ch_num)}장 ({ch_folder.split('_', 1)[-1]})"

            it_num = re.search(r"^\d+", item_folder).group() if re.search(r"^\d+", item_folder) else "1"
            item_str = f"{int(it_num)}번째 알고스팟 문제 ({item_folder.split('_', 1)[-1]})"
            section_str = f"{int(ch_num)}장 알고리즘 전략"

        elif root_seg == "knuth":
            track_key = "knuth"
            book_title = TRACK_TITLES["knuth"]
            ch_folder = parts[1] if len(parts) > 1 else ""
            item_folder = parts[2] if len(parts) > 2 else ""

            if "01_zeros" in ch_folder:
                chapter_str = "Chapter 7.1 (Zeros and Ones)"
            elif "02_generating" in ch_folder:
                chapter_str = "Chapter 7.2 (Generating All Possibilities)"
            else:
                chapter_str = ch_folder

            section_str = ch_folder.split('_', 1)[-1]
            it_num = re.search(r"^\d+", item_folder).group() if re.search(r"^\d+", item_folder) else "1"
            item_str = f"{int(it_num)}번째 알고리즘 ({item_folder.split('_', 1)[-1]})"

    # 2. 본문 텍스트 (README.md 또는 main.cpp) 분석을 통한 정밀 보정
    readme_path = item_dir / "README.md"
    main_path = item_dir / "main.cpp"

    sample_text = ""
    if readme_path.exists():
        raw = readme_path.read_text(encoding="utf-8", errors="ignore")
        sample_text = clean_frontmatter(raw)
    elif main_path.exists():
        raw = main_path.read_text(encoding="utf-8", errors="ignore")
        sample_text = clean_frontmatter(raw)

    if sample_text:
        # 페이지 번호 매칭: (p.49), (p. 49), p.38
        p_match = re.search(r"\(p\.?\s*(\d+)\)|페이지\s*:\s*(\d+)|p\.(\d+)", sample_text)
        if p_match:
            pg = p_match.group(1) or p_match.group(2) or p_match.group(3)
            page_str = f"p.{pg}"

        # 교안 절 번호 매칭: // 1.4 타입과 타입 변환
        sec_match = re.search(r"//\s*(\d+\.\d+)\s+([^\n]+)", sample_text)
        if sec_match:
            section_str = f"{sec_match.group(1)}절 ({sec_match.group(2).strip()})"

        # 도서 챕터 타이틀 매칭: 1장. A Crash Course...
        ch_match = re.search(r"-\s*\*\*챕터\*\*:\s*([^\n]+)", sample_text)
        if ch_match:
            chapter_str = ch_match.group(1).strip()

        # 리스팅 번호 매칭: (Listing 4-1)
        listing_match = re.search(r"Listing\s+([0-9\-]+)", sample_text, re.IGNORECASE)
        if listing_match:
            item_str += f" [Listing {listing_match.group(1)}]"

        # 연습문제 번호 매칭: Exercise 1-1
        exercise_match = re.search(r"Exercise\s+([0-9\-_]+)", sample_text, re.IGNORECASE)
        if exercise_match:
            item_str += f" [Exercise {exercise_match.group(1)}]"

        # 첫 번째 설명 라인
        for line in sample_text.splitlines():
            sline = line.strip()
            if sline.startswith(("#", "-", ">", "//", "/*", "*", "<!--")) or not sline:
                continue
            summary_str = sline[:80] + ("..." if len(sline) > 80 else "")
            break

    # 3. [[snippet]] 태그 검사
    if main_path.exists():
        main_raw = main_path.read_text(encoding="utf-8", errors="ignore")
        snip_match = re.search(r'\[\[snippet(?:\("([^"]+)"\))?\]\]\s*([^\n{;]+)', main_raw)
        if snip_match:
            desc = snip_match.group(1) or ""
            sym = snip_match.group(2).strip()
            snippet_str = f"{sym} ({desc})" if desc else sym

    run_cmd = f"./scripts/run.sh practice/{rel.as_posix()}"
    test_cmd = f"./scripts/test.sh practice/{rel.as_posix()}"

    return {
        "track_key": track_key,
        "book_title": book_title,
        "chapter": chapter_str,
        "section": section_str,
        "paragraph": item_str,
        "page": page_str,
        "snippet": snippet_str,
        "summary": summary_str,
        "rel_path": f"practice/{rel.as_posix()}",
        "run_cmd": run_cmd,
        "test_cmd": test_cmd,
    }


def format_card(info: Dict[str, Any]) -> str:
    lines = [
        "==============================================================================",
        f" 📍 [위치 색인 결과] {info['rel_path']}",
        "==============================================================================",
        f" • 도서 / 트랙 : {info['book_title']}",
        f" • 장 (Chapter) : {info['chapter']}",
        f" • 절 (Section) : {info['section']}",
        f" • 문단 / 항목  : {info['paragraph']}" + (f"  [원서 {info['page']}]" if info['page'] else ""),
    ]
    if info["snippet"]:
        lines.append(f" • 핵심 스니펫  : {info['snippet']}")
    if info["summary"]:
        lines.append(f" • 핵심 요약    : {info['summary']}")
    lines.append("------------------------------------------------------------------------------")
    lines.append(f" • 실행 명령어  : {info['run_cmd']}")
    lines.append(f" • 테스트 명령  : {info['test_cmd']}")
    lines.append("==============================================================================")
    return "\n".join(lines)


def search_items(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """키워드로 practice 하위 항목을 검색합니다."""
    query_lower = query.lower()
    matches = []

    for root, dirs, files in os.walk(PRACTICE_DIR):
        if "main.cpp" in files or "README.md" in files:
            p = Path(root)
            # 폴더명이나 경로에 검색어 포함 여부 확인
            if query_lower in p.as_posix().lower():
                matches.append(parse_item_info(p))
                if len(matches) >= limit:
                    break
                continue

            # 파일 내용 검색
            for fn in ("main.cpp", "README.md"):
                fp = p / fn
                if fp.exists():
                    try:
                        c = fp.read_text(encoding="utf-8", errors="ignore")
                        if query_lower in c.lower():
                            matches.append(parse_item_info(p))
                            break
                    except Exception:
                        pass
            if len(matches) >= limit:
                break

    return matches


def print_tree(track_filter: Optional[str] = None):
    """지정된 트랙 또는 전체 목차 트리를 출력합니다."""
    print("==============================================================================")
    print(" 📚 handcrafted-cpp 전체 도서·장·절 마스터 목차 트리 (Master Table of Contents)")
    print("==============================================================================")

    tracks = [p for p in PRACTICE_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")]
    for tr in sorted(tracks):
        if track_filter and track_filter.lower() not in tr.name.lower():
            continue
        print(f"\n📁 [{tr.name}] {TRACK_TITLES.get(tr.name, '')}")
        for ch in sorted(tr.iterdir()):
            if not ch.is_dir() or ch.name.startswith("."):
                continue
            item_count = sum(1 for _ in ch.rglob("main.cpp"))
            print(f"  └── 📖 {ch.name} ({item_count}개 실습 항목)")
    print("==============================================================================")


def main():
    parser = argparse.ArgumentParser(description="실습 파일의 도서명, 몇 장, 몇 절, 몇 문단/항목을 출력하는 네비게이터")
    parser.add_argument("target", nargs="?", help="조회할 파일/폴더 경로 또는 검색 키워드")
    parser.add_argument("--tree", nargs="?", const="ALL", help="목차 트리 출력 (옵션: 특정 트랙명)")
    parser.add_argument("--json", action="store_true", help="결과를 JSON 형식으로 출력")
    args = parser.parse_args()

    if args.tree:
        flt = None if args.tree == "ALL" else args.tree
        print_tree(flt)
        return

    if not args.target:
        parser.print_help()
        sys.exit(1)

    target_path = Path(args.target)
    # 직접 파일/디렉터리 경로로 존재하는 경우
    if target_path.exists() or (REPO_ROOT / target_path).exists():
        real_path = target_path if target_path.exists() else (REPO_ROOT / target_path)
        info = parse_item_info(real_path)
        if args.json:
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            print(format_card(info))
        return

    # 경로가 아니면 키워드 검색 수행
    print(f"🔍 키워드 '{args.target}' 로 실습 항목을 검색합니다...\n")
    results = search_items(args.target)
    if not results:
        print(f"일치하는 실습 항목을 찾을 수 없습니다: {args.target}")
        sys.exit(1)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for i, info in enumerate(results, 1):
            print(f"[{i}/{len(results)}]")
            print(format_card(info))
            print()


if __name__ == "__main__":
    main()
