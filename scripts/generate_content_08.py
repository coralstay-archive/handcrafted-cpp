#!/usr/bin/env python3
"""Generator for Book 08: 전문가를 위한 C++ (Professional C++ 4th Edition, C++17) -> stone/c-and-cpp/08_prof_cpp/"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_DIR = REPO_ROOT / "stone" / "c-and-cpp" / "08_prof_cpp"

import _init_paths


def load_all_items():
    from content08_data import part1_2, part3_a, part3_b, part4_5
    items = []
    for mod in (part1_2, part3_a, part3_b, part4_5):
        items.extend(mod.ITEMS)
    return items


def render_readme(item: dict) -> str:
    num = item["num"]
    title = item["title"]
    chapter = item["chapter"]
    concept = item["concept"]
    target_code = item["target_code"].strip()
    expected_output = item["expected_output"].strip()
    test_guide = item["test_guide"].strip()

    return f"""# [{num}] {title}

> **도서**: 전문가를 위한 C++ (Professional C++ 4th Edition)  
> **장/절**: {chapter}  
> **컴파일 표준**: C++17 (`-std=c++17`)

---

## 1. 핵심 개념 및 원리

{concept}

---

## 2. 따라쳐볼 목표 코드 (`main.cpp` 완성본)

아래 코드를 `main.cpp`에 직접 타이핑하며 엔터프라이즈급 C++17 소프트웨어 설계와 구현 기법을 체득해 보세요.

```cpp
{target_code}
```

### 예상 실행 출력

```text
{expected_output}
```

---

## 3. GoogleTest 검증 가이드 (`test.cpp` 예시)

`main.cpp` 실습을 마친 뒤, `test.cpp`에서 핵심 클래스/함수/템플릿을 단위 테스트로 검증해 보세요.

```cpp
{test_guide}
```
"""


def render_main_skeleton(item: dict) -> str:
    num = item["num"]
    title = item["title"]
    chapter = item["chapter"]
    steps = item.get("steps", [
        "필요한 표준 헤더를 포함하고 네임스페이스/타입을 선언하세요.",
        "README.md의 목표 코드를 참고하여 클래스, 템플릿, 알고리즘을 구현하세요.",
        "main()에서 시나리오를 실행하고 결과를 표준 출력으로 확인하세요.",
    ])
    expected_output = item["expected_output"].strip()

    step_lines = "\n".join(f"    // Step {i+1}: {s}" for i, s in enumerate(steps))
    exp_lines = "\n".join(f"//   {line}" for line in expected_output.splitlines())

    return f"""// ============================================================================
// [전문가를 위한 C++] {num}. {title}
// 장/절: {chapter}
// 컴파일 표준: C++17 (-std=c++17)
// ============================================================================
// [따라치기 가이드]
// README.md에 수록된 목표 코드를 직접 타이핑하며 C++17 엔터프라이즈 기법을 익히세요.
//
// 예상 출력:
{exp_lines}
// ============================================================================

#include <iostream>

int main() {{
{step_lines}

    return 0;
}}
"""


def render_test_skeleton(item: dict) -> str:
    num = item["num"]
    slug = item["slug"]
    title = item["title"]
    test_suite = f"Book08_{num.replace('-', '_')}_{slug.title().replace('_', '')}"

    return f"""#include <gtest/gtest.h>

// [{num}] {title}
// README.md의 '3. GoogleTest 검증 가이드'를 참고하여 테스트를 작성하세요.

TEST({test_suite}, BasicVerification) {{
    // TODO: 핵심 클래스/함수/템플릿을 호출하고 EXPECT_EQ / EXPECT_TRUE로 검증하세요.
    SUCCEED();
}}
"""


def verify_items(items: list[dict]) -> bool:
    print(f"[검증] 총 {len(items)}개 예제의 target_code를 g++ -std=c++17로 컴파일 테스트합니다...")
    ok_count = 0
    fail_count = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        for item in items:
            num = item["num"]
            src_path = os.path.join(tmpdir, f"item_{num}.cpp")
            bin_path = os.path.join(tmpdir, f"item_{num}.bin")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(item["target_code"].strip() + "\n")
            res = subprocess.run(
                ["g++", "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wno-unused-parameter", "-Wno-unused-variable", "-pthread", src_path, "-o", bin_path],
                capture_output=True,
                text=True,
            )
            if res.returncode != 0:
                print(f"  [실패] {num} ({item['title']}):\n{res.stderr}")
                fail_count += 1
            else:
                ok_count += 1
    print(f"[검증 결과] 성공: {ok_count}/{len(items)}, 실패: {fail_count}")
    return fail_count == 0


def generate_files(items: list[dict], force: bool = False):
    BOOK_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    updated_readme = 0

    sections: dict[str, list[dict]] = {}
    for item in items:
        sec = item["section_dir"]
        sections.setdefault(sec, []).append(item)
        item_dir = BOOK_DIR / sec / f"{item['num']}_{item['slug']}"
        item_dir.mkdir(parents=True, exist_ok=True)

        readme_path = item_dir / "README.md"
        main_path = item_dir / "main.cpp"
        test_path = item_dir / "test.cpp"

        readme_path.write_text(render_readme(item), encoding="utf-8")
        updated_readme += 1

        if force or not main_path.exists():
            main_path.write_text(render_main_skeleton(item), encoding="utf-8")
            created += 1
        if force or not test_path.exists():
            test_path.write_text(render_test_skeleton(item), encoding="utf-8")

    lines = [
        "# 08. 전문가를 위한 C++ (Professional C++ 4th Edition, C++17)",
        "",
        "> 원본 도서: `docs/C-and-Cpp/전문가를-위한-C++.pdf` (전 30장 + 부록 완역 실습)",
        "> 컴파일 표준: **C++17 (`-std=c++17`)**",
        "",
        "## 실행 및 테스트 방법",
        "",
        "```bash",
        "# 예제 실행 (예: 01_part1_crash_course_and_style/001_cpp17_crash_course_basics)",
        "./scripts/run.sh c-and-cpp/08_prof_cpp/01_part1_crash_course_and_style/001_cpp17_crash_course_basics",
        "",
        "# GoogleTest 실행",
        "./scripts/test.sh c-and-cpp/08_prof_cpp/01_part1_crash_course_and_style/001_cpp17_crash_course_basics",
        "```",
        "",
        "## 전체 목차",
        "",
    ]
    for sec in sorted(sections.keys()):
        lines.append(f"### `{sec}`")
        for it in sections[sec]:
            rel = f"{sec}/{it['num']}_{it['slug']}"
            lines.append(f"- [{it['num']}. {it['title']}](./{rel}/README.md) (`{it['chapter']}`)")
        lines.append("")

    (BOOK_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[완료] 총 {len(items)}개 항목 생성 완료 (README 갱신: {updated_readme}, 스켈레톤 생성: {created})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Compile all target_code with g++ -std=c++17")
    parser.add_argument("--force", action="store_true", help="Overwrite existing main.cpp and test.cpp")
    args = parser.parse_args()

    items = load_all_items()
    if args.verify:
        if not verify_items(items):
            sys.exit(1)
    generate_files(items, force=args.force)


if __name__ == "__main__":
    main()
