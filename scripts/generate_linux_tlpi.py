#!/usr/bin/env python3
"""Generator for Linux Track 01: TLPI System Programming (The Linux Programming Interface)
-> stone/linux/01_tlpi_system_programming/
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = REPO_ROOT / "stone" / "linux" / "01_tlpi_system_programming"

import _init_paths


def load_all_items():
    from linux_data import (
        tlpi_01_file_io,
        tlpi_02_proc_threads,
        tlpi_03_memory,
        tlpi_04_signals,
        tlpi_05_ipc,
        tlpi_06_sockets,
        tlpi_07_events,
    )
    items = []
    for mod in (
        tlpi_01_file_io,
        tlpi_02_proc_threads,
        tlpi_03_memory,
        tlpi_04_signals,
        tlpi_05_ipc,
        tlpi_06_sockets,
        tlpi_07_events,
    ):
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

> **도서**: The Linux Programming Interface (리눅스 API의 모든 것)  
> **장/절**: {chapter}  
> **컴파일 표준**: C++17 / POSIX (`-std=c++17 -pthread`)

---

## 1. 핵심 시스템 콜 및 원리

{concept}

---

## 2. 따라쳐볼 목표 코드 (`main.cpp` 완성본)

아래 코드를 `main.cpp`에 직접 타이핑하며 리눅스/유닉스 커널 시스템 콜 인터페이스와 에러 처리, 리소스 관리 원리를 체득해 보세요.

```cpp
{target_code}
```

### 예상 실행 출력

```text
{expected_output}
```

---

## 3. GoogleTest 검증 가이드 (`test.cpp` 예시)

`main.cpp` 실습을 마친 뒤, `test.cpp`에서 시스템 콜 동작과 반환값, 버퍼 무결성을 단위 테스트로 검증해 보세요.

```cpp
{test_guide}
```
"""


def render_main_skeleton(item: dict) -> str:
    num = item["num"]
    title = item["title"]
    chapter = item["chapter"]
    steps = item.get("steps", [
        "필요한 시스템 헤더(<unistd.h>, <fcntl.h>, <sys/types.h> 등)를 포함하세요.",
        "README.md의 시스템 콜 사용법을 참고하여 함수와 에러 처리 로직을 구현하세요.",
        "main()에서 시나리오를 실행하고 리소스(FD, 버퍼)를 안전하게 해제하세요.",
    ])
    expected_output = item["expected_output"].strip()

    step_lines = "\n".join(f"    // Step {i+1}: {s}" for i, s in enumerate(steps))
    exp_lines = "\n".join(f"//   {line}" for line in expected_output.splitlines())

    return f"""// ============================================================================
// [TLPI 리눅스 시스템 프로그래밍] {num}. {title}
// 장/절: {chapter}
// 컴파일 표준: C++17 (-std=c++17 -pthread)
// ============================================================================
// [따라치기 가이드]
// README.md에 수록된 목표 코드를 직접 타이핑하며 시스템 콜 동작을 체득하세요.
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
    test_suite = f"LinuxTLPI_{num}_{slug.title().replace('_', '')}"

    return f"""#include <gtest/gtest.h>

// [{num}] {title}
// README.md의 '3. GoogleTest 검증 가이드'를 참고하여 시스템 콜 테스트를 작성하세요.

TEST({test_suite}, BasicSyscallVerification) {{
    // TODO: 시스템 콜 호출 및 반환값/errno를 EXPECT_NE / EXPECT_EQ 로 검증하세요.
    SUCCEED();
}}
"""


def verify_items(items: list[dict]) -> bool:
    print(f"[검증] 총 {len(items)}개 TLPI 시스템 프로그래밍 target_code를 g++ -std=c++17로 컴파일 테스트합니다...")
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
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    updated_readme = 0

    sections: dict[str, list[dict]] = {}
    for item in items:
        sec = item["section_dir"]
        sections.setdefault(sec, []).append(item)
        item_dir = BASE_DIR / sec / f"{item['num']}_{item['slug']}"
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
        "# 01. TLPI 리눅스 시스템 프로그래밍 (The Linux Programming Interface)",
        "",
        "> 원본 도서: `docs/linux/TLPI-1.pdf` & `TLPI-2.pdf` (Michael Kerrisk 저, 전 64장 완역 실습)",
        "> 컴파일 표준: **C++17 / POSIX (`-std=c++17 -pthread`)**",
        "",
        "## 실행 및 테스트 방법",
        "",
        "```bash",
        "# 1. 네이티브 호스트에서 즉시 컴파일 & 실행",
        "./scripts/run.sh stone/linux/01_tlpi_system_programming/01_file_io/01_copy_file_lowlevel",
        "",
        "# 2. Docker 순정 리눅스 컨테이너 환경에서 실행",
        "./scripts/linux_run.sh stone/linux/01_tlpi_system_programming/01_file_io/01_copy_file_lowlevel",
        "",
        "# 3. GoogleTest 단위 테스트 실행",
        "./scripts/test.sh stone/linux/01_tlpi_system_programming/01_file_io/01_copy_file_lowlevel",
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

    (BASE_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[완료] TLPI 총 {len(items)}개 항목 생성 완료 (README 갱신: {updated_readme}, 스켈레톤 생성: {created})")


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
