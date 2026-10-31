#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07_extreme_c (전문가를 위한 C - Extreme C) 실습 스캐폴드 및 해설(README.md) 생성기.
"""
import argparse
import importlib
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict

import _init_paths

ROOT = os.path.join(os.path.dirname(__file__), "..", "stone", "c-and-cpp", "07_extreme_c")

PART_MODULES = [
    "content07_data.part1_3",
    "content07_data.part4_7",
]


def load_all_items():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    all_items = []
    for mod_name in PART_MODULES:
        try:
            mod = importlib.import_module(mod_name)
            items = getattr(mod, "ITEMS", [])
            all_items.extend(items)
        except ModuleNotFoundError:
            pass
    return all_items


def sanitize_test_name(slug: str, num: str) -> str:
    name = re.sub(r"[^0-9A-Za-z_]", "_", slug)
    name = re.sub(r"_+", "_", name).strip("_")
    return f"Book07_{num}_{name}" if name else f"Book07_{num}"


def make_readme(item: dict) -> str:
    title = item["title"]
    page = item["page"]
    section_title = item["section_title"]
    concept = item["concept"].strip()
    target_code = item["target_code"].strip()
    expected_output = item.get("expected_output", "").strip()
    test_code = item.get("test_code", "").strip()

    out_section = ""
    if expected_output:
        out_section = f"\n## 예상 실행 결과\n```text\n{expected_output}\n```\n"

    test_section = ""
    if test_code:
        test_section = f"\n## 추천 GoogleTest 검증 코드 (`test.cpp`)\n```cpp\n{test_code}\n```\n"

    return f"""# {title} ({page})

> **장(Chapter)**: {section_title}

## 핵심 개념 & 원리
{concept}

## 따라 칠 목표 코드 (`main.cpp`)
```cpp
{target_code}
```
{out_section}{test_section}"""


def make_main_stub(item: dict) -> str:
    section_title = item["section_title"]
    title = item["title"]
    page = item["page"]
    steps = item.get("steps", [])
    expected_output = item.get("expected_output", "").strip()

    io_comment = ""
    if expected_output:
        io_lines = "\n".join(f"// {line}" for line in expected_output.splitlines())
        io_comment = f"//\n// --- 예상 실행 결과 ---\n{io_lines}\n"

    step_lines = "\n".join(f"    // {s}" for s in steps) if steps else "    // README.md 의 목표 코드를 보며 직접 타이핑해 보세요."

    return f"""// [{section_title}]
// {title} ({page})
// 같은 폴더의 README.md 에 있는 개념 해설과 목표 코드를 보며 직접 타이핑해서 완성해 보세요.
{io_comment}
#include <bits/stdc++.h>
using namespace std;

int main() {{
{step_lines}

    return 0;
}}
"""


def make_test_stub(item: dict) -> str:
    section_title = item["section_title"]
    title = item["title"]
    page = item["page"]
    suite = sanitize_test_name(item["slug"], item["num"])

    return f"""// [{section_title}]
// {title} ({page})
//
// 같은 폴더의 README.md 에 있는 추천 GoogleTest 검증 코드를 참고하여
// 직접 테스트 케이스를 작성해 보세요.

#include <gtest/gtest.h>

TEST({suite}, TODO) {{
    // TODO: 검증하고 싶은 함수/로직을 선언하고 테스트 케이스를 작성하세요.
}}
"""


def verify_items(items: list) -> bool:
    print(f"Verifying {len(items)} items with g++ -std=c++17...")
    failed = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for idx, item in enumerate(items):
            num = item["num"]
            slug = item["slug"]
            sec = item["section_dir"]
            src_path = os.path.join(tmpdir, f"item_{idx}_{num}.cpp")
            out_path = os.path.join(tmpdir, f"item_{idx}_{num}.out")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(item["target_code"])

            res = subprocess.run(
                ["g++", "-std=c++17", "-O1", "-Wall", "-Wno-attributes", "-Wno-unused-variable", "-Wno-unused-but-set-variable", "-pthread", src_path, "-o", out_path],
                capture_output=True,
                text=True,
            )
            if res.returncode != 0:
                failed.append((sec, num, slug, res.stderr))
                print(f"[FAIL] {sec}/{num}_{slug}:\n{res.stderr}", file=sys.stderr)

    if failed:
        print(f"\nVerification FAILED: {len(failed)}/{len(items)} items had compile errors.", file=sys.stderr)
        return False
    print(f"Verification PASSED: All {len(items)} items compiled cleanly with g++ -std=c++17!")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Compile-check all target_code snippets with g++ -std=c++17")
    parser.add_argument("--force", action="store_true", help="Overwrite existing main.cpp and test.cpp stubs")
    args = parser.parse_args()

    items = load_all_items()
    if not items:
        print("No items loaded yet.")
        return

    if args.verify:
        ok = verify_items(items)
        if not ok:
            sys.exit(1)

    os.makedirs(ROOT, exist_ok=True)
    by_section = defaultdict(list)
    for item in items:
        by_section[(item["section_dir"], item["section_title"])].append(item)

    main_created = 0
    main_skipped = 0
    test_created = 0
    test_skipped = 0
    readme_written = 0

    book_index_lines = [
        "# 07. 전문가를 위한 C (Extreme C — C++17 클론 타이핑 실습장)",
        "",
        "Kamran Amini의 『전문가를 위한 C (Extreme C)』 전 7부 23장 모든 절과 심화 C 기법(매크로, 빌드 파이프라인, 메모리 구조, C 기반 OOP, 유닉스/커널, POSIX 동시성, IPC/소켓, 타 언어 통합, 테스팅)을 하나도 빠짐없이 C++17 호환 실행 예제로 구성했습니다.",
        "",
        "## 장(Chapter) 목록",
        "",
    ]

    for (sec_dir, sec_title), sec_items in sorted(by_section.items(), key=lambda x: x[0][0]):
        sec_path = os.path.join(ROOT, sec_dir)
        os.makedirs(sec_path, exist_ok=True)
        book_index_lines.append(f"- [`{sec_dir}/`](./{sec_dir}/README.md) — {sec_title} ({len(sec_items)}개 항목)")

        sec_index_lines = [f"# {sec_title}", ""]
        for item in sorted(sec_items, key=lambda x: x["num"]):
            item_dir = f"{item['num']}_{item['slug']}"
            item_path = os.path.join(sec_path, item_dir)
            os.makedirs(item_path, exist_ok=True)

            readme_path = os.path.join(item_path, "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(make_readme(item))
            readme_written += 1

            main_cpp = os.path.join(item_path, "main.cpp")
            if os.path.exists(main_cpp) and not args.force:
                main_skipped += 1
            else:
                with open(main_cpp, "w", encoding="utf-8") as f:
                    f.write(make_main_stub(item))
                main_created += 1

            test_cpp = os.path.join(item_path, "test.cpp")
            if os.path.exists(test_cpp) and not args.force:
                test_skipped += 1
            else:
                with open(test_cpp, "w", encoding="utf-8") as f:
                    f.write(make_test_stub(item))
                test_created += 1

            sec_index_lines.append(f"- [`{item_dir}/`](./{item_dir}/README.md) — {item['title']} ({item['page']})")

        with open(os.path.join(sec_path, "README.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(sec_index_lines) + "\n")

    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(book_index_lines) + "\n")

    print(f"Book 07 generated: {readme_written} READMEs, main.cpp (created={main_created}, skipped={main_skipped}), test.cpp (created={test_created}, skipped={test_skipped})")


if __name__ == "__main__":
    main()
