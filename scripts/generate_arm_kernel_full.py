#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_arm_kernel_full.py
《코드로 알아보는 ARM 리눅스 커널》 (강진우 저, 제이펍)
ARM64 리눅스 커널 내부구조 전수 실습 트랙 스캐폴딩 생성 엔진

타깃 위치: practice/linux/04_arm_kernel/
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_DIR = REPO_ROOT / "practice" / "linux" / "04_arm_kernel"

import _init_paths

from arm_kernel_data import (
    ch01_02_arch_boot,
    ch03_04_paging_memory,
    ch05_06_tasks_sched,
    ch07_09_smp_irq_timers,
)

MODULES = [
    ch01_02_arch_boot,
    ch03_04_paging_memory,
    ch05_06_tasks_sched,
    ch07_09_smp_irq_timers,
]

BOOK_TITLE = "《코드로 알아보는 ARM 리눅스 커널》(강진우 저, 제이펍)"


def generate_arm_kernel_scaffolding():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    total_items = 0

    chapter_summary = {}

    for mod in MODULES:
        for item in mod.ITEMS:
            sec_dir = item["section_dir"]
            sec_title = item["section_title"]
            num = item["num"]
            slug = item["slug"]
            title = item["title"]
            page = item.get("page", "")
            concept = item.get("concept", "").strip()
            target_code = item["target_code"].strip()

            item_folder_name = f"{num}_{slug}"
            item_path = TARGET_DIR / sec_dir / item_folder_name
            item_path.mkdir(parents=True, exist_ok=True)

            rel_path_str = f"practice/linux/04_arm_kernel/{sec_dir}/{item_folder_name}"

            if sec_dir not in chapter_summary:
                chapter_summary[sec_dir] = {"title": sec_title, "items": []}
            chapter_summary[sec_dir]["items"].append((num, slug, title, page))

            # 1. README.md 생성
            readme_content = f"""<!--
==============================================================================
@file: linux-04_arm_kernel_{sec_dir}_{item_folder_name}_README.md
@path: {rel_path_str}/README.md
@book: {BOOK_TITLE}
==============================================================================
-->

# 🛡️ [ARM Kernel Ch {sec_dir[:2]}] {title}

> **도서**: {BOOK_TITLE}  
> **단원**: {sec_title} ({page})  
> **컴파일 표준**: C++17 / ARM64 Linux Kernel Subsystem (`-std=c++17 -pthread`)

---

## 1. 핵심 아키텍처 및 커널 메커니즘
{concept}

## 2. 따라 칠 완성 구현 코드 (`main.cpp`)
```cpp
{target_code}
```

## 3. 추천 GoogleTest 단위 검증 코드 예시 (`test.cpp`)
```cpp
#include <gtest/gtest.h>

TEST(ARMKernel_{slug}, Verification) {{
    // TODO: ARM 커널 내부 자료구조 및 알고리즘 검증 테스트를 직접 작성하세요.
    EXPECT_TRUE(true);
}}
```

## 4. 컴파일 및 실행 사이클
```bash
# 1) 직접 작성한 main.cpp 즉시 컴파일 & 콘솔 출력 확인 (0.1초 고속 빌드)
./scripts/run.sh {rel_path_str}

# 2) 직접 작성한 test.cpp GoogleTest 자동 검증
./scripts/test.sh {rel_path_str}
```
"""
            readme_file = item_path / "README.md"
            if not readme_file.exists():
                readme_file.write_text(readme_content, encoding="utf-8")

            # 2. main.cpp 생성
            main_file = item_path / "main.cpp"
            if not main_file.exists():
                main_file.write_text(target_code + "\n", encoding="utf-8")

            # 3. test.cpp 생성
            test_content = f"""// ==============================================================================
// @file: linux-04_arm_kernel_{sec_dir}_{item_folder_name}_test.cpp
// @path: {rel_path_str}/test.cpp
// @book: {BOOK_TITLE}
// ==============================================================================

#include <gtest/gtest.h>

TEST(ARMKernel_{slug}, BasicVerification) {{
    // TODO: 여기에 직접 GoogleTest 케이스를 타이핑하여 완성하세요.
    EXPECT_TRUE(true);
}}
"""
            test_file = item_path / "test.cpp"
            if not test_file.exists():
                test_file.write_text(test_content, encoding="utf-8")

            total_items += 1

    # 4. Master README.md 생성
    master_readme = f"""# 🛡️ 《코드로 알아보는 ARM 리눅스 커널》 전수 실습 트랙

> **강진우 저 | 제이펍 | 총 938페이지**  
> **총 9개 핵심 챕터 전수 인제스천 완료**  
> **총 {total_items}개 핵심 ARM64 아키텍처, 부팅, 메모리, 스케줄링 실습 항목 수록**

---

## 챕터별 실습 마스터 색인 (Chapter Master Index)

| 챕터 | 폴더명 | 단원 제목 | 실습 항목 수 |
|:---:|:---|:---|:---:|
"""
    for sec_dir, data in chapter_summary.items():
        master_readme += f"| {sec_dir[:2]} | [`{sec_dir}`](./{sec_dir}/) | {data['title']} | **{len(data['items'])}** |\n"

    master_readme += f"""
---

## 🛠️ 실습 및 검증 방법

```bash
# 1) 특정 실습 항목 즉시 컴파일 & 실행 (0.1초 고속 빌드)
./scripts/run.sh practice/linux/04_arm_kernel/01_armv8_arch/01_armv8_registers_pstate

# 2) 특정 실습 항목 GoogleTest 단위 테스트 검증
./scripts/test.sh practice/linux/04_arm_kernel/01_armv8_arch/01_armv8_registers_pstate
```
"""
    (TARGET_DIR / "README.md").write_text(master_readme, encoding="utf-8")
    print(f"✨ 《코드로 알아보는 ARM 리눅스 커널》 전수 스캐폴딩 완료! (총 {total_items}개 항목 생성)")


if __name__ == "__main__":
    generate_arm_kernel_scaffolding()
