#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전문가를 위한 C++ (Professional C++, Marc Gregoire, 1,496페이지) 전수 스캐폴딩 생성 엔진
- 원서 34개 전 챕터 (Part I ~ Part V, Ch00 ~ Ch34)
- 345개 공식 예제 프로그램 (Official Examples from Wiley/Marc Gregoire)
- 154개 공식 연습문제 (Official Exercises with Solutions)
- 총 499개 전수 실습 항목 생성 (README.md + main.cpp + test.cpp)
"""

import argparse
import glob
import os
import re
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_BOOK_DIR = os.path.join(REPO_ROOT, "practice", "c-and-cpp", "08_prof_cpp")
SOURCE_PROCPP_DIR = "/tmp/procpp"

CHAPTER_META = {
    0: ("Preface and Introduction", "서문 및 개요", "Part I: Introduction"),
    1: ("A Crash Course in C++ and the Standard Library", "C++와 표준 라이브러리 초단기 속성 코스", "Part I: Introduction"),
    2: ("Working with Strings and String Views", "스트링과 스트링 뷰 다루기", "Part I: Introduction"),
    3: ("Coding with Style", "코딩 스타일", "Part I: Introduction"),
    4: ("Designing Professional C++ Programs", "전문가다운 C++ 프로그램 디자인", "Part II: Software Design"),
    5: ("Designing with Objects", "객체지향 디자인", "Part II: Software Design"),
    6: ("Designing for Reuse", "재사용을 고려한 디자인", "Part II: Software Design"),
    7: ("Memory Management", "메모리 관리", "Part III: Coding the Professional Way"),
    8: ("Gaining Proficiency with Classes and Objects", "클래스와 객체 숙달하기", "Part III: Coding the Professional Way"),
    9: ("Mastering Classes and Objects", "클래스와 객체 마스터하기", "Part III: Coding the Professional Way"),
    10: ("Discovering Inheritance Techniques", "상속 기법 발견하기", "Part III: Coding the Professional Way"),
    11: ("C++ Quirks, Oddities, and Incidentals", "C++의 독특한 특성과 주의점", "Part III: Coding the Professional Way"),
    12: ("Writing Generic Code with Templates", "템플릿을 활용한 제네릭 코드 작성", "Part III: Coding the Professional Way"),
    13: ("Demystifying C++ I/O", "C++ I/O 파헤치기", "Part III: Coding the Professional Way"),
    14: ("Handling Errors", "에러 처리 및 예외", "Part III: Coding the Professional Way"),
    15: ("Overloading C++ Operators", "C++ 연산자 오버로딩", "Part III: Coding the Professional Way"),
    16: ("Overview of the C++ Standard Library", "C++ 표준 라이브러리 개요", "Part III: Coding the Professional Way"),
    17: ("Understanding Iterators and the Ranges Library", "반복자와 Ranges 라이브러리", "Part III: Coding the Professional Way"),
    18: ("Standard Library Containers", "표준 라이브러리 컨테이너", "Part III: Coding the Professional Way"),
    19: ("Function Pointers, Function Objects, and Lambdas", "함수 포인터, 함수 객체, 람다 표현식", "Part III: Coding the Professional Way"),
    20: ("Mastering Standard Library Algorithms", "표준 라이브러리 알고리즘 마스터", "Part III: Coding the Professional Way"),
    21: ("String Localization and Regular Expressions", "스트링 로컬라이제이션과 정규 표현식", "Part III: Coding the Professional Way"),
    22: ("Date and Time Utilities", "날짜와 시간 유틸리티 chrono", "Part III: Coding the Professional Way"),
    23: ("Random Number Facilities", "난수 생성 기능", "Part III: Coding the Professional Way"),
    24: ("Additional Library Utilities", "추가 라이브러리 유틸리티 (optional, variant, any)", "Part III: Coding the Professional Way"),
    25: ("Customizing and Extending the Standard Library", "표준 라이브러리 커스터마이징 및 확장", "Part IV: Advanced Features"),
    26: ("Advanced Templates", "고급 템플릿 메타프로그래밍", "Part IV: Advanced Features"),
    27: ("Multithreaded Programming with C++", "C++ 멀티스레드 프로그래밍", "Part IV: Advanced Features"),
    28: ("Maximizing Software Engineering Methods", "소프트웨어 공학 기법 극대화", "Part V: Robust Software"),
    29: ("Writing Efficient C++", "효율적인 C++ 코드 작성과 최적화", "Part V: Robust Software"),
    30: ("Becoming Adept at Testing", "테스트 기법 숙달하기", "Part V: Robust Software"),
    31: ("Conquering Debugging", "디버깅 정복하기", "Part V: Robust Software"),
    32: ("Incorporating Design Techniques and Frameworks", "디자인 기법과 프레임워크 적용", "Part V: Robust Software"),
    33: ("Applying Design Patterns", "디자인 패턴 적용", "Part V: Robust Software"),
    34: ("Developing Cross-Platform and Cross-Language Apps", "크로스 플랫폼 및 이기종 언어 연동", "Part V: Robust Software"),
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def get_chapter_num(ch_str):
    m = re.search(r'\d+', ch_str)
    return int(m.group(0)) if m else 0

def process_item_sources(src_dir, dest_dir, item_title, ch_num, is_exercise=False):
    os.makedirs(dest_dir, exist_ok=True)
    
    # 1. Copy all source files
    cpp_files = []
    h_files = []
    other_files = []
    
    for fname in sorted(os.listdir(src_dir)):
        src_path = os.path.join(src_dir, fname)
        if os.path.isfile(src_path):
            dest_path = os.path.join(dest_dir, fname)
            shutil.copy2(src_path, dest_path)
            if fname.endswith(".cpp"):
                cpp_files.append(fname)
            elif fname.endswith((".h", ".hpp")):
                h_files.append(fname)
            else:
                other_files.append(fname)
                
    # 2. Ensure main.cpp exists
    main_target = os.path.join(dest_dir, "main.cpp")
    if "main.cpp" not in cpp_files:
        if cpp_files:
            # Check if any cpp file has 'main('
            main_cand = None
            for f in cpp_files:
                p = os.path.join(dest_dir, f)
                with open(p, "r", encoding="utf-8", errors="replace") as fp:
                    content = fp.read()
                    if "int main" in content or "main(" in content:
                        main_cand = f
                        break
            if main_cand:
                # Copy/rename main_cand to main.cpp or create driver
                shutil.copy2(os.path.join(dest_dir, main_cand), main_target)
            else:
                # Combine or create driver calling functions
                primary = cpp_files[0]
                with open(main_target, "w", encoding="utf-8") as fp:
                    fp.write(f"""// Auto-generated main driver for {item_title}
#include <iostream>
int main() {{
    std::cout << "[Professional C++ Ch {ch_num:02d}] {item_title} loaded successfully." << std::endl;
    return 0;
}}
""")
        else:
            # No cpp files (e.g. text or header only)
            with open(main_target, "w", encoding="utf-8") as fp:
                fp.write(f"""// Auto-generated main driver for {item_title}
#include <iostream>
int main() {{
    std::cout << "[Professional C++ Ch {ch_num:02d}] {item_title} loaded successfully." << std::endl;
    return 0;
}}
""")

    # Read main.cpp for preview in README
    main_code_preview = ""
    if os.path.exists(main_target):
        with open(main_target, "r", encoding="utf-8", errors="replace") as fp:
            main_code_preview = fp.read().strip()
    if len(main_code_preview) > 2000:
        main_code_preview = main_code_preview[:2000] + "\n// ... (이하 생략 - 전체 코드는 소스 파일 참조)"

    suite_name = f"ProCpp_Ch{ch_num:02d}_{slugify(item_title)}"

    # 3. Create README.md
    item_type_str = "연습문제 (Exercise)" if is_exercise else "본문 공식 예제 (Listing)"
    readme_text = f"""# 📘 [Professional C++ Ch {ch_num:02d}] {item_title}

- **도서**: 전문가를 위한 C++ (Professional C++, Marc Gregoire 저)
- **챕터**: {ch_num}장. {CHAPTER_META.get(ch_num, ('', ''))[0]} ({CHAPTER_META.get(ch_num, ('', ''))[1]})
- **분류**: {item_type_str}
- **컴파일 표준**: C++17 / C++20 (`-std=c++17`)

---

## 1. 개요 및 학습 목표
본 예제는 《전문가를 위한 C++》 원서의 **{item_title}** 공식 코드입니다.
모던 C++의 핵심 문법, 표준 라이브러리(STL), 메모리 안전성 및 객체지향/제네릭 설계 기법을 직접 실습합니다.

## 2. 따라쳐볼 목표 코드 (`main.cpp`)
아래 코드를 `main.cpp`에 직접 타이핑하며 모던 C++ 문법과 설계 기법을 체득하세요.

```cpp
{main_code_preview}
```

## 3. 추천 GoogleTest 검증 코드 예시 (`test.cpp`)
아래 예시를 참고하여 `test.cpp`에 직접 타이핑하여 단위 테스트를 완성해 보세요.

```cpp
#include <gtest/gtest.h>

TEST({suite_name}, TestSample) {{
    // TODO: 목표 코드의 핵심 함수 및 객체 상태를 직접 검증해 보세요.
    EXPECT_TRUE(true);
}}
```

## 4. 컴파일 및 실행 사이클
```bash
# 1) 직접 작성한 main.cpp 즉시 컴파일 & 실행 (0.1초 고속 빌드)
./scripts/run.sh {dest_dir}

# 2) 직접 작성한 test.cpp GoogleTest 단위 테스트 자동 검증
./scripts/test.sh {dest_dir}
```
"""
    with open(os.path.join(dest_dir, "README.md"), "w", encoding="utf-8") as fp:
        fp.write(readme_text)

    # 4. Create test.cpp (GoogleTest)
    test_text = f"""// ==============================================================================
// [Professional C++ Ch {ch_num:02d}] {item_title}
//
// 같은 폴더의 README.md 에 있는 목표 코드와 추천 GoogleTest 코드를 참고하여
// 직접 테스트 케이스를 타이핑하여 완성해 보세요.
// ==============================================================================

#include <gtest/gtest.h>

TEST({suite_name}, TODO) {{
    // TODO: 여기에 직접 GoogleTest 케이스를 타이핑하세요.
    // 예: EXPECT_EQ(actual, expected);
    EXPECT_TRUE(true);
}}
"""
    with open(os.path.join(dest_dir, "test.cpp"), "w", encoding="utf-8") as fp:
        fp.write(test_text)

def generate_content_08_full():
    print("🚀 《전문가를 위한 C++》 (1,496페이지) 34개 전 챕터 전수 스캐폴딩을 시작합니다...")
    
    # 1. Remove old collapsed 8 directories in TARGET_BOOK_DIR
    if os.path.exists(TARGET_BOOK_DIR):
        for entry in os.listdir(TARGET_BOOK_DIR):
            ep = os.path.join(TARGET_BOOK_DIR, entry)
            if os.path.isdir(ep) and entry.startswith("0") and "_part" in entry:
                print(f"  - 기존 축약 폴더 제거: {entry}")
                shutil.rmtree(ep)

    os.makedirs(TARGET_BOOK_DIR, exist_ok=True)
    
    examples_base = os.path.join(SOURCE_PROCPP_DIR, "Examples - No Modules")
    exercises_base = os.path.join(SOURCE_PROCPP_DIR, "Exercises - No Modules")
    
    all_chapters = sorted(set(list(CHAPTER_META.keys())))
    total_items_generated = 0
    master_index_rows = []

    for ch_num in all_chapters:
        en_title, ko_title, part_name = CHAPTER_META[ch_num]
        ch_folder_name = f"{ch_num:02d}_{slugify(en_title)}"
        ch_target_path = os.path.join(TARGET_BOOK_DIR, ch_folder_name)
        os.makedirs(ch_target_path, exist_ok=True)
        
        ch_str = f"Ch{ch_num:02d}"
        ex_dir = os.path.join(examples_base, ch_str)
        exer_dir = os.path.join(exercises_base, ch_str)
        
        # Discover examples
        ex_folders = []
        if os.path.exists(ex_dir):
            for d in sorted(os.listdir(ex_dir)):
                dp = os.path.join(ex_dir, d)
                if os.path.isdir(dp):
                    ex_folders.append((d, dp))
                    
        # Discover exercises
        exer_folders = []
        if os.path.exists(exer_dir):
            for d in sorted(os.listdir(exer_dir)):
                dp = os.path.join(exer_dir, d)
                if os.path.isdir(dp):
                    exer_folders.append((d, dp))

        item_counter = 1
        chapter_item_rows = []
        
        # 1. Process Examples
        for folder_name, src_path in ex_folders:
            item_slug = f"{item_counter:02d}_example_{slugify(folder_name)}"
            item_dest = os.path.join(ch_target_path, item_slug)
            process_item_sources(src_path, item_dest, folder_name, ch_num, is_exercise=False)
            chapter_item_rows.append((item_slug, "공식 예제", folder_name))
            item_counter += 1
            total_items_generated += 1

        # 2. Process Exercises
        for folder_name, src_path in exer_folders:
            item_slug = f"{item_counter:02d}_exercise_{slugify(folder_name)}"
            item_dest = os.path.join(ch_target_path, item_slug)
            process_item_sources(src_path, item_dest, f"Exercise {folder_name}", ch_num, is_exercise=True)
            chapter_item_rows.append((item_slug, "연습문제", f"Exercise {folder_name}"))
            item_counter += 1
            total_items_generated += 1

        # Chapter README.md
        ch_readme = f"""# 📖 {ch_num}장. {en_title} ({ko_title})

> **전문가를 위한 C++ (Professional C++, Marc Gregoire 저)**  
> **부(Part)**: {part_name}  
> **총 실습 항목**: {len(chapter_item_rows)}개 (공식 예제 {len(ex_folders)}개 + 연습문제 {len(exer_folders)}개)

---

## 챕터 전체 실습 및 연습문제 목록

| 번호 | 폴더명 | 분류 | 실습 내용 |
|:---:|:---|:---:|:---|
"""
        for slug, it_type, desc in chapter_item_rows:
            ch_readme += f"| {slug[:2]} | [`{slug}`]({slug}/) | {it_type} | {desc} |\n"

        with open(os.path.join(ch_target_path, "README.md"), "w", encoding="utf-8") as fp:
            fp.write(ch_readme)

        master_index_rows.append((ch_num, en_title, ko_title, part_name, ch_folder_name, len(chapter_item_rows), len(ex_folders), len(exer_folders)))

    # Master README.md in practice/c-and-cpp/08_prof_cpp
    master_readme = f"""# 📚 전문가를 위한 C++ (Professional C++) 전수 실습 트랙

> **Marc Gregoire 저 | 총 1,496페이지 | C++17 / C++20 표준**  
> **총 34개 전 챕터 (Part I ~ Part V, Ch00 ~ Ch34) 전수 수록**  
> **총 {total_items_generated}개 실습 항목 (345개 공식 예제 + 154개 공식 연습문제)**

---

## 34개 챕터별 마스터 색인 (Chapter Master Index)

| 챕터 | 영문 챕터명 | 한글 주제 | 구분 | 폴더 링크 | 전체 항목 | 공식 예제 | 연습문제 |
|:---:|:---|:---|:---|:---|:---:|:---:|:---:|
"""
    for ch_num, en, ko, part, folder, tot, n_ex, n_exer in master_index_rows:
        master_readme += f"| {ch_num:02d} | {en} | {ko} | {part.split(':')[0]} | [{folder}](./{folder}/) | **{tot}** | {n_ex} | {n_exer} |\n"

    master_readme += f"""
---

## 🛠️ 실습 및 검증 방법

```bash
# 1) 특정 항목 즉시 컴파일 & 실행 (0.1초 고속 빌드)
./scripts/run.sh practice/c-and-cpp/08_prof_cpp/01_a_crash_course_in_c_and_the_standard_library/01_example_01_helloworld

# 2) 특정 항목 GoogleTest 단위 테스트 검증
./scripts/test.sh practice/c-and-cpp/08_prof_cpp/01_a_crash_course_in_c_and_the_standard_library/01_example_01_helloworld

# 3) 전수 스캐폴딩 재생성
python3 scripts/generate_content_08_full.py
```
"""
    with open(os.path.join(TARGET_BOOK_DIR, "README.md"), "w", encoding="utf-8") as fp:
        fp.write(master_readme)

    print(f"\n✨ 《전문가를 위한 C++》 전수 스캐폴딩 완료!")
    print(f"📊 총 35개 챕터 폴더, {total_items_generated}개 전체 실습 항목 생성 완료.")
    print(f"📄 마스터 색인: {os.path.join(TARGET_BOOK_DIR, 'README.md')}")

if __name__ == "__main__":
    generate_content_08_full()
