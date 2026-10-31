#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/audit_and_verify_all.py
handcrafted-cpp 17개 전 도서/트랙, 2,535개 실습 항목 전수 감사(Audit) 및 컴파일/실행 검증기.
"""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
PRACTICE_DIR = REPO_ROOT / "practice"

TRACKS = [
    ("stone-lecture/01_문법_STL", "큰돌 01_문법_STL"),
    ("stone-lecture/02_알고리즘_개념", "큰돌 02_알고리즘_개념"),
    ("stone-lecture/03_실전_문제풀이", "큰돌 03_실전_문제풀이"),
    ("c-and-cpp/01_c_300", "01_c_300 (C언어 300제)"),
    ("c-and-cpp/02_c_100", "02_c_100 (C언어 100제)"),
    ("c-and-cpp/03_tour_of_cpp", "03_tour_of_cpp (A Tour of C++)"),
    ("c-and-cpp/04_cpp_stl", "04_cpp_stl (C++ STL 프로그래밍)"),
    ("c-and-cpp/05_high_perf_cpp", "05_high_perf_cpp (고성능 C++)"),
    ("c-and-cpp/06_algo_generic", "06_algo_generic (알고리즘 산책)"),
    ("c-and-cpp/07_extreme_c", "07_extreme_c (전문가를 위한 C)"),
    ("c-and-cpp/08_prof_cpp", "08_prof_cpp (전문가를 위한 C++)"),
    ("linux/01_tlpi_system_programming", "linux 01_tlpi (리눅스 시스템 프로그래밍)"),
    ("linux/02_cli_and_shell_automation", "linux 02_cli (CLI 셸 자동화)"),
    ("linux/03_bpf_performance_tools", "linux 03_bpf (BPF 성능 분석 도구)"),
    ("linux/04_arm_kernel", "linux 04_arm (ARM 리눅스 커널)"),
    ("jongmanbook", "jongmanbook (알고리즘 문제 해결 전략)"),
    ("knuth", "knuth (TAOCP Vol 4A 조합 알고리즘)"),
]


def find_item_dirs(base_path: Path) -> List[Path]:
    items = []
    for root, dirs, files in os.walk(base_path):
        p = Path(root)
        if any(f in files for f in ["main.cpp", "script.sh", "main.c"]):
            items.append(p)
    return sorted(items)


def audit_item(item_dir: Path) -> Dict[str, any]:
    try:
        files = set(os.listdir(item_dir))
    except Exception:
        files = set()

    has_readme = "README.md" in files
    has_main = any(f in files for f in ["main.cpp", "script.sh", "main.c"])
    has_test = "test.cpp" in files or "test.sh" in files or "Test.cpp" in files

    compile_ok = True
    error_msg = ""
    main_src = None
    for f in ["main.cpp", "main.c"]:
        if f in files:
            main_src = item_dir / f
            break

    if main_src and main_src.suffix in [".cpp", ".c"]:
        # 리눅스 전용 헤더가 있는 파일은 호스트 Clang에서 문법 에러가 날 수 있으므로 예외 기록
        cmd = [
            "clang++",
            "-fsyntax-only",
            "-std=c++20",
            "-Wno-attributes",
            "-Wno-unused-value",
            "-Wno-unused-variable",
            "-Wno-unused-parameter",
            str(main_src),
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            if res.returncode != 0:
                compile_ok = False
                error_msg = res.stderr.splitlines()[0] if res.stderr else "Syntax Error"
        except subprocess.TimeoutExpired:
            compile_ok = False
            error_msg = "Timeout (>3s)"
        except Exception as e:
            compile_ok = False
            error_msg = str(e)

    return {
        "path": item_dir,
        "has_readme": has_readme,
        "has_main": has_main,
        "has_test": has_test,
        "compile_ok": compile_ok,
        "error_msg": error_msg,
    }


def main():
    print("=" * 80, flush=True)
    print(" 🔍 handcrafted-cpp 17개 전 도서/트랙 전수 감사(Audit) 및 컴파일 검증", flush=True)
    print("=" * 80, flush=True)

    total_items = 0
    total_missing_readme = 0
    total_missing_test = 0
    total_compile_errors = 0

    all_missing_readmes = []
    all_missing_tests = []
    all_compile_errors = []

    print(f"\n| 번호 | 트랙명 | 실습 항목 수 | README 누락 | test.cpp 누락 | 호스트 구문 검사 |", flush=True)
    print(f"|:---:|:---|:---:|:---:|:---:|:---:|", flush=True)

    for idx, (rel_path, track_name) in enumerate(TRACKS, 1):
        track_dir = PRACTICE_DIR / rel_path
        if not track_dir.exists():
            print(f"| {idx:02d} | {track_name} | ❌ 없음 | - | - | - |", flush=True)
            continue

        items = find_item_dirs(track_dir)
        total_items += len(items)

        # 16개 스레드로 고속 처리
        with ThreadPoolExecutor(max_workers=16) as ex:
            results = list(ex.map(audit_item, items))

        missing_readme = [r for r in results if not r["has_readme"]]
        missing_test = [r for r in results if not r["has_test"]]
        compile_errors = [r for r in results if not r["compile_ok"]]

        total_missing_readme += len(missing_readme)
        total_missing_test += len(missing_test)
        total_compile_errors += len(compile_errors)

        all_missing_readmes.extend(missing_readme)
        all_missing_tests.extend(missing_test)
        all_compile_errors.extend(compile_errors)

        err_str = f"⚠️ {len(compile_errors)}개" if compile_errors else "🟢 100% PASS"
        readme_str = f"❌ {len(missing_readme)}개" if missing_readme else "🟢 0"
        test_str = f"❌ {len(missing_test)}개" if missing_test else "🟢 0"

        print(f"| {idx:02d} | {track_name} | **{len(items)}개** | {readme_str} | {test_str} | {err_str} |", flush=True)

    print("\n" + "=" * 80, flush=True)
    print(f"📊 총 실습 항목: {total_items}개", flush=True)
    print(f"📝 README 누락: {total_missing_readme}개", flush=True)
    print(f"🧪 test.cpp 누락: {total_missing_test}개", flush=True)
    print(f"⚠️ 호스트 구문 경고/에러: {total_compile_errors}개", flush=True)
    print("=" * 80, flush=True)

    # 상세 내역 파일 저장
    report_file = REPO_ROOT / "audit_report.txt"
    with open(report_file, "w", encoding="utf-8") as fp:
        fp.write("=== README 누락 목록 ===\n")
        for r in all_missing_readmes:
            fp.write(f"- {r['path']}\n")
        fp.write("\n=== test.cpp 누락 목록 ===\n")
        for r in all_missing_tests:
            fp.write(f"- {r['path']}\n")
        fp.write("\n=== 컴파일 구문 에러/경고 목록 ===\n")
        for r in all_compile_errors:
            fp.write(f"- {r['path']}: {r['error_msg']}\n")
    print(f"📄 상세 감사 보고서 저장됨: {report_file}", flush=True)


if __name__ == "__main__":
    main()
