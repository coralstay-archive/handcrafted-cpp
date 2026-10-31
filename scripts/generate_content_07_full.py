#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전문가를 위한 C (Extreme C, Kamran Amini 저) 전수 스캐폴딩 생성 엔진
- 원서 23개 전 챕터 (Part I ~ Part IV, Ch01 ~ Ch23)
- 공식 PacktPublishing Extreme-C 저장소 전수 예제 및 프로젝트 포함
- Ch13, Ch14 이론 챕터에 대한 시뮬레이션 코드 포함
- 각 항목별 README.md, main.cpp, test.cpp (GoogleTest) 전수 생성
"""

import os
import re
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_BOOK_DIR = os.path.join(REPO_ROOT, "practice", "c-and-cpp", "07_extreme_c")
SOURCE_EXTREMEC_DIR = "/tmp/extremec"

CHAPTER_META = {
    1: ("Essential Features", "필수 요소 - 전처리기 매크로 포인터 함수 포인터 구조체", "Part I: Essential C"),
    2: ("Compilation and Linking", "컴파일과 링킹 - 전처리 컴파일 어셈블리 링크 단계별 분해", "Part I: Essential C"),
    3: ("Object Files", "목적 파일 - ELF 심볼 테이블 재배치 섹션 구조", "Part I: Essential C"),
    4: ("Process Memory Structure", "프로세스 메모리 구조 - 코드 데이터 BSS 힙 스택 매핑", "Part II: Memory Management"),
    5: ("Stack and Heap", "스택과 힙 - 스택 프레임 동적 메모리 할당 메모리 누수 방지", "Part II: Memory Management"),
    6: ("OOP and Encapsulation", "OOP와 캡슐화 - 불투명 포인터를 활용한 C 객체지향 캡슐화", "Part III: OOP in C"),
    7: ("Composition and Aggregation", "합성과 집합 - C 구조체 기반 Has-A 관계 설계", "Part III: OOP in C"),
    8: ("Inheritance and Polymorphism", "상속과 다형성 - 함수 포인터 테이블(VTable)과 타입 캐스팅 상속", "Part III: OOP in C"),
    9: ("Abstraction and OOP in C++", "추상화와 C++의 OOP - C와 C++ 객체 모델 및 가상 함수 비교", "Part III: OOP in C"),
    10: ("Unix History and Architecture", "유닉스 역사와 아키텍처 - POSIX 표준 파일 디스크립터", "Part IV: System & Network"),
    11: ("System Calls and Kernel", "시스템 호출과 커널 - 사용자 모드 대 커널 모드 전환 및 syscall", "Part IV: System & Network"),
    12: ("The Most Recent C", "최신 C 표준 - C11/C18 제네릭 선택자 정적 단언 가변 길이 배열", "Part I: Essential C"),
    13: ("Concurrency Concepts", "동시성 개념 - 시분할 인터리빙 스케줄러와 경쟁 상태", "Part V: Concurrency"),
    14: ("Synchronization Concepts", "동기화 개념 - 임계 영역 데드락 방지 상호 배제 원리", "Part V: Concurrency"),
    15: ("Thread Execution", "스레드 실행 - POSIX pthread 생성 결합 분리 및 인자 전달", "Part V: Concurrency"),
    16: ("Thread Synchronization", "스레드 동기화 - Mutex 세마포어 배리어 조건 변수", "Part V: Concurrency"),
    17: ("Process Execution", "프로세스 실행 - fork exec waitpid 좀비 프로세스 방지", "Part VI: Multiprocessing"),
    18: ("Process Synchronization", "프로세스 동기화 - POSIX 명명된 세마포어와 공유 메모리", "Part VI: Multiprocessing"),
    19: ("Single Host IPC and Sockets", "단일 호스트 IPC - 파이프 FIFO 유닉스 도메인 소켓", "Part VI: Multiprocessing"),
    20: ("Socket Programming", "소켓 프로그래밍 - TCP/IP 클라이언트 서버 통신 및 계산기 서비스", "Part VI: Multiprocessing"),
    21: ("Integration with Other Languages", "이기종 언어 연동 - C와 C++ Go Python Java JNI FFI", "Part VII: Integration & Quality"),
    22: ("Unit Testing and Debugging", "단위 테스트와 디버깅 - GoogleTest CMocka 모의 객체 단위 테스트", "Part VII: Integration & Quality"),
    23: ("Build Systems", "빌드 시스템 - Make 및 CMake를 활용한 프로덕션 빌드 자동화", "Part VII: Integration & Quality"),
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def get_first_comment(filepath):
    """Extract descriptive comment from file header."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for _ in range(15):
                line = f.readline()
                if not line:
                    break
                line = line.strip()
                if "Description:" in line:
                    return line.split("Description:", 1)[1].strip()
                if line.startswith("//") and len(line) > 5 and not "File name" in line:
                    return line.lstrip("/ ").strip()
                if line.startswith("/*") and len(line) > 5 and not "File name" in line:
                    return line.lstrip("/* ").strip()
    except Exception:
        pass
    return ""

def process_item(dest_dir, item_title, ch_num, source_files, extra_desc=""):
    os.makedirs(dest_dir, exist_ok=True)
    cpp_files = []
    c_files = []
    h_files = []
    other_files = []

    for src_path in source_files:
        fname = os.path.basename(src_path)
        dest_path = os.path.join(dest_dir, fname)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dest_path)
            if fname.endswith(".cpp"):
                cpp_files.append(fname)
            elif fname.endswith(".c"):
                c_files.append(fname)
            elif fname.endswith((".h", ".hpp")):
                h_files.append(fname)
            else:
                other_files.append(fname)
        elif os.path.isdir(src_path):
            sub_dest = os.path.join(dest_dir, fname)
            if os.path.exists(sub_dest):
                shutil.rmtree(sub_dest)
            shutil.copytree(src_path, sub_dest)
            other_files.append(fname)

    # Ensure main.cpp exists
    main_target = os.path.join(dest_dir, "main.cpp")
    if not os.path.exists(main_target):
        # Look for a main in c or cpp files
        main_c = None
        for f in c_files + cpp_files:
            p = os.path.join(dest_dir, f)
            with open(p, "r", encoding="utf-8", errors="replace") as fp:
                txt = fp.read()
                if "int main" in txt or "main(" in txt:
                    main_c = f
                    break
        if main_c:
            shutil.copy2(os.path.join(dest_dir, main_c), main_target)
        else:
            with open(main_target, "w", encoding="utf-8") as fp:
                fp.write(f"""// Entry point for Extreme C: {item_title}
#include <iostream>
int main() {{
    std::cout << "[Extreme C Ch {ch_num:02d}] {item_title} loaded successfully." << std::endl;
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

    test_slug = slugify(item_title)[:30]
    suite_name = f"ExtremeC_Ch{ch_num:02d}_{test_slug}"

    # Create README.md
    readme_text = f"""# 📘 [Extreme C Ch {ch_num:02d}] {item_title}

- **도서**: 전문가를 위한 C (Extreme C, Kamran Amini 저)
- **챕터**: {ch_num}장. {CHAPTER_META.get(ch_num, ('', ''))[0]} ({CHAPTER_META.get(ch_num, ('', ''))[1]})
- **분류**: 본문 공식 예제 (Official Listing)
- **컴파일 표준**: C11 / C++17 (`-std=c++17`)

---

## 1. 개요 및 학습 내용
{extra_desc or f'본 예제는 Extreme C 원서의 **{item_title}** 공식 코드입니다.'}

## 2. 따라쳐볼 목표 코드 (`main.cpp`)
아래 코드를 `main.cpp`에 직접 타이핑하며 C 언어 아키텍처 및 시스템 프로그래밍 기법을 체득하세요.

```c
{main_code_preview}
```

## 3. 추천 GoogleTest 검증 코드 예시 (`test.cpp`)
아래 단위 테스트 예시를 참고하여 `test.cpp`에 직접 타이핑하여 테스트를 완성해 보세요.

```cpp
#include <gtest/gtest.h>

TEST({suite_name}, TestSample) {{
    // TODO: C 구조체 및 함수 동작을 검증하는 테스트를 직접 타이핑하세요.
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

    # Create test.cpp (GoogleTest)
    test_text = f"""// ==============================================================================
// [Extreme C Ch {ch_num:02d}] {item_title}
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

def generate_content_07_full():
    print("🚀 《전문가를 위한 C (Extreme C)》 23개 전 챕터 전수 스캐폴딩을 시작합니다...")

    # Remove existing old folders
    if os.path.exists(TARGET_BOOK_DIR):
        for entry in os.listdir(TARGET_BOOK_DIR):
            ep = os.path.join(TARGET_BOOK_DIR, entry)
            if os.path.isdir(ep) and entry.startswith(("0", "1", "2")):
                shutil.rmtree(ep)

    os.makedirs(TARGET_BOOK_DIR, exist_ok=True)

    # Also load content07_data items if available for rich concepts
    sys.path.insert(0, os.path.join(REPO_ROOT, "content_data"))
    sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
    data_items_by_ch = {}
    try:
        from content07_data.part1_3 import ITEMS as P1_ITEMS
        from content07_data.part4_7 import ITEMS as P2_ITEMS
        for it in (P1_ITEMS + P2_ITEMS):
            sec_num = int(it["section_dir"].split("_")[0])
            data_items_by_ch.setdefault(sec_num, []).append(it)
    except Exception as e:
        print(f"  (참고: content07_data 로드 중: {e})")

    total_items_generated = 0
    master_index_rows = []

    for ch_num in range(1, 24):
        en_title, ko_title, part_name = CHAPTER_META[ch_num]
        ch_folder_name = f"{ch_num:02d}_{slugify(en_title)}"
        ch_target_path = os.path.join(TARGET_BOOK_DIR, ch_folder_name)
        os.makedirs(ch_target_path, exist_ok=True)

        # Discover official files from SOURCE_EXTREMEC_DIR
        ch_str = f"ch{ch_num:02d}"
        found_src_dir = None
        for d in os.listdir(SOURCE_EXTREMEC_DIR):
            if d.startswith(ch_str) or d.startswith(f"ch{ch_num}-"):
                found_src_dir = os.path.join(SOURCE_EXTREMEC_DIR, d)
                break

        grouped_examples = {}
        if found_src_dir and os.path.isdir(found_src_dir):
            for fname in sorted(os.listdir(found_src_dir)):
                fpath = os.path.join(found_src_dir, fname)
                if fname.startswith(".") or fname == "CMakeLists.txt":
                    continue
                if os.path.isdir(fpath):
                    grouped_examples[fname] = [fpath]
                elif fname.endswith((".c", ".h", ".cpp")):
                    m = re.search(r"chapter\d+_(\d+)", fname)
                    if m:
                        ex_key = f"example_{int(m.group(1)):02d}"
                    else:
                        m2 = re.search(r"ex(\d+)_(\d+)", fname)
                        if m2:
                            ex_key = f"example_{int(m2.group(2)):02d}"
                        else:
                            name_no_ext = os.path.splitext(fname)[0]
                            ex_key = f"example_{name_no_ext}"
                    grouped_examples.setdefault(ex_key, []).append(fpath)

        chapter_items = []
        item_counter = 1

        if grouped_examples:
            # Process discovered official examples
            for ex_key in sorted(grouped_examples.keys()):
                files = grouped_examples[ex_key]
                first_f = files[0]
                desc = get_first_comment(first_f) if os.path.isfile(first_f) else ""
                
                # Make clean title
                clean_title = ex_key.replace("example_", "Example ")
                if desc:
                    item_display_name = f"{clean_title} - {desc}"
                else:
                    item_display_name = clean_title

                item_slug = f"{item_counter:02d}_{slugify(clean_title)}"
                item_dest = os.path.join(ch_target_path, item_slug)
                process_item(item_dest, item_display_name, ch_num, files, desc)
                chapter_items.append((item_slug, item_display_name))
                item_counter += 1
                total_items_generated += 1
        else:
            # Chapters with theoretical concepts or simulations (like Ch13, Ch14)
            sim_items = data_items_by_ch.get(ch_num, [])
            if sim_items:
                for it in sim_items:
                    item_title = it["title"]
                    item_slug = f"{item_counter:02d}_{it['slug']}"
                    item_dest = os.path.join(ch_target_path, item_slug)
                    os.makedirs(item_dest, exist_ok=True)

                    main_code = it["target_code"]
                    with open(os.path.join(item_dest, "main.cpp"), "w", encoding="utf-8") as fp:
                        fp.write(main_code)

                    test_code = it.get("test_code", "")
                    if not test_code:
                        test_code = f"""#include <gtest/gtest.h>
TEST(ExtremeC_Ch{ch_num:02d}_{it['slug'][:25]}, Basic) {{
    EXPECT_TRUE(true);
}}
"""
                    with open(os.path.join(item_dest, "test.cpp"), "w", encoding="utf-8") as fp:
                        fp.write(test_code)

                    readme_text = f"""# 📘 [Extreme C Ch {ch_num:02d}] {item_title}

- **도서**: 전문가를 위한 C (Extreme C, Kamran Amini 저)
- **챕터**: {ch_num}장. {en_title} ({ko_title})
- **페이지**: {it.get('page', '')}

---

## 1. 핵심 개념
{it.get('concept', '')}

## 2. 컴파일 및 실행 방법
```bash
./scripts/run.sh {item_dest}
./scripts/test.sh {item_dest}
```
"""
                    with open(os.path.join(item_dest, "README.md"), "w", encoding="utf-8") as fp:
                        fp.write(readme_text)

                    chapter_items.append((item_slug, item_title))
                    item_counter += 1
                    total_items_generated += 1

        # Chapter README.md
        ch_readme = f"""# 📖 {ch_num}장. {en_title} ({ko_title})

> **전문가를 위한 C (Extreme C, Kamran Amini 저)**  
> **부(Part)**: {part_name}  
> **총 실습 항목**: {len(chapter_items)}개

---

## 챕터 전체 실습 목록

| 번호 | 폴더명 | 주제 및 설명 |
|:---:|:---|:---|
"""
        for slug, desc in chapter_items:
            ch_readme += f"| {slug[:2]} | [`{slug}`]({slug}/) | {desc} |\n"

        with open(os.path.join(ch_target_path, "README.md"), "w", encoding="utf-8") as fp:
            fp.write(ch_readme)

        master_index_rows.append((ch_num, en_title, ko_title, part_name, ch_folder_name, len(chapter_items)))

    # Master README.md in practice/c-and-cpp/07_extreme_c
    master_readme = f"""# 📚 전문가를 위한 C (Extreme C) 전수 실습 트랙

> **Kamran Amini 저 | C11/C18 & C++17 표준 | 시스템 프로그래밍 & 소프트웨어 아키텍처**  
> **총 23개 전 챕터 (Part I ~ Part VII, Ch01 ~ Ch23) 전수 수록**  
> **총 {total_items_generated}개 실습 항목 (공식 PacktPublishing 전수 예제 + 시뮬레이션)**

---

## 23개 챕터별 마스터 색인 (Chapter Master Index)

| 챕터 | 영문 챕터명 | 한글 핵심 주제 | 구분 | 폴더 링크 | 전체 항목 |
|:---:|:---|:---|:---|:---|:---:|
"""
    for ch_num, en, ko, part, folder, tot in master_index_rows:
        master_readme += f"| {ch_num:02d} | {en} | {ko.split('-')[0].strip()} | {part.split(':')[0]} | [{folder}](./{folder}/) | **{tot}** |\n"

    master_readme += f"""
---

## 🛠️ 실습 및 검증 방법

```bash
# 1) 특정 항목 즉시 컴파일 & 실행 (0.1초 고속 빌드)
./scripts/run.sh practice/c-and-cpp/07_extreme_c/01_essential_features/01_example_01

# 2) 특정 항목 GoogleTest 단위 테스트 검증
./scripts/test.sh practice/c-and-cpp/07_extreme_c/01_essential_features/01_example_01

# 3) 전수 스캐폴딩 재생성
python3 scripts/generate_content_07_full.py
```
"""
    with open(os.path.join(TARGET_BOOK_DIR, "README.md"), "w", encoding="utf-8") as fp:
        fp.write(master_readme)

    print(f"\n✨ 《전문가를 위한 C (Extreme C)》 전수 스캐폴딩 완료!")
    print(f"📊 총 23개 챕터 폴더, {total_items_generated}개 전체 실습 항목 생성 완료.")
    print(f"📄 마스터 색인: {os.path.join(TARGET_BOOK_DIR, 'README.md')}")

if __name__ == "__main__":
    generate_content_07_full()
