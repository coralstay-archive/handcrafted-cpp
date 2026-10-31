#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Linux Programming Interface (TLPI) 1·2권 전수 스캐폴드 생성 엔진
- 저자: Michael Kerrisk
- 총 64개 챕터 + 부록 및 보충 트랙 (총 68개 챕터)
- 391개 공식 예제 프로그램 (docs/linux/tlpi-dist/)
- 194개 공식 연습문제 (Exercises) 및 솔루션 (/tmp/tlpiexer/)
- 각 항목: README.md + main.cpp + test.cpp
"""

import argparse
import glob
import os
import re
import shutil
import sys
import tempfile
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TLPI_TARGET_DIR = os.path.join(REPO_ROOT, "practice", "linux", "01_tlpi_system_programming")
TLPI_DIST_DIR = os.path.join(REPO_ROOT, "contents", "linux", "tlpi-dist")
MAN_PAGES_DIR = os.path.join(REPO_ROOT, "contents", "linux", "man-pages", "man")
TLPIEXER_DIR = "/tmp/tlpiexer"

CHAPTER_TITLES = {
    1: ("History and Standards", "역사와 표준"),
    2: ("Fundamental Concepts", "기본 개념"),
    3: ("System Programming Concepts", "시스템 프로그래밍 개념"),
    4: ("File I/O: The Universal I/O Model", "파일 I/O: 범용 I/O 모델"),
    5: ("File I/O: Further Details", "파일 I/O: 상세 사항"),
    6: ("Processes", "프로세스"),
    7: ("Memory Allocation", "메모리 할당"),
    8: ("Users and Groups", "사용자와 그룹"),
    9: ("Process Credentials", "프로세스 자격증명"),
    10: ("Time", "시간"),
    11: ("System Limits and Options", "시스템 한계와 옵션"),
    12: ("System and Process Information", "시스템 및 프로세스 정보"),
    13: ("File I/O Buffering", "파일 I/O 버퍼링"),
    14: ("File Systems", "파일 시스템"),
    15: ("File Attributes", "파일 속성"),
    16: ("Extended Attributes", "확장 속성 xattr"),
    17: ("Access Control Lists", "접근 제어 목록 ACL"),
    18: ("Directories and Links", "디렉터리와 링크"),
    19: ("Monitoring File Events", "파일 이벤트 감시 inotify"),
    20: ("Signals: Fundamental Concepts", "시그널: 기본 개념"),
    21: ("Signals: Signal Handlers", "시그널: 시그널 핸들러"),
    22: ("Signals: Advanced Features", "시그널: 고급 기능"),
    23: ("Timers and Sleeping", "타이머와 슬립"),
    24: ("Process Creation", "프로세스 생성 fork"),
    25: ("Process Termination", "프로세스 종료 exit"),
    26: ("Monitoring Child Processes", "자식 프로세스 모니터링 wait"),
    27: ("Program Execution", "프로그램 실행 execve"),
    28: ("Process Creation and Execution Details", "프로세스 생성 및 실행 상세"),
    29: ("Threads: Introduction", "스레드: 기초"),
    30: ("Threads: Thread Synchronization", "스레드: 동기화"),
    31: ("Threads: Thread Safety and TLS", "스레드: 안전성 및 TLS"),
    32: ("Threads: Thread Cancellation", "스레드: 취소"),
    33: ("Threads: Further Details", "스레드: 고급 상세"),
    34: ("Process Groups, Sessions, and Job Control", "프로세스 그룹, 세션, 잡 제어"),
    35: ("Process Priorities and Scheduling", "프로세스 우선순위와 스케줄링"),
    36: ("Process Resources", "프로세스 자원"),
    37: ("Daemons", "데몬"),
    38: ("Writing Secure Privileged Programs", "안전한 특권 프로그램 작성"),
    39: ("Capabilities", "리눅스 기능 Capability"),
    40: ("Login Accounting", "로그인 기록 utmpx"),
    41: ("Fundamentals of Shared Libraries", "공유 라이브러리 기초"),
    42: ("Advanced Features of Shared Libraries", "공유 라이브러리 고급 기능"),
    43: ("Interprocess Communication Overview", "프로세스 간 통신 IPC 개요"),
    44: ("Pipes and FIFOs", "파이프와 FIFO"),
    45: ("Introduction to System V IPC", "System V IPC 소개"),
    46: ("System V Message Queues", "System V 메시지 큐"),
    47: ("System V Semaphores", "System V 세마포어"),
    48: ("System V Shared Memory", "System V 공유 메모리"),
    49: ("Memory Mappings", "메모리 매핑 mmap"),
    50: ("Virtual Memory Operations", "가상 메모리 연산"),
    51: ("Introduction to POSIX IPC", "POSIX IPC 소개"),
    52: ("POSIX Message Queues", "POSIX 메시지 큐"),
    53: ("POSIX Semaphores", "POSIX 세마포어"),
    54: ("POSIX Shared Memory", "POSIX 공유 메모리"),
    55: ("File Locking", "파일 잠금"),
    56: ("Sockets: Introduction", "소켓: 소개"),
    57: ("Sockets: UNIX Domain", "소켓: 유닉스 도메인"),
    58: ("Sockets: Fundamentals of TCP/IP", "소켓: TCP/IP 기초"),
    59: ("Sockets: Internet Domains", "소켓: 인터넷 도메인"),
    60: ("Sockets: Server Design", "소켓: 서버 설계"),
    61: ("Sockets: Advanced Topics", "소켓: 고급 주제"),
    62: ("Terminals", "터미널"),
    63: ("Alternative I/O Models", "대체 I/O 모델 select/poll/epoll"),
    64: ("Pseudoterminals", "의사 터미널 PTY"),
    65: ("Appendix B: Parsing Command-Line Options", "부록 B: 명령줄 옵션 파싱 getopt"),
    66: ("Supplementary: Namespaces", "보충: 리눅스 네임스페이스"),
    67: ("Supplementary: Seccomp", "보충: 보안 컴퓨팅 seccomp"),
    68: ("Supplementary: VDSO", "보충: 가상 동적 공유 객체 VDSO"),
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def load_chapter_summary(ch_num):
    summary_file = os.path.join(TLPIEXER_DIR, "doc", "tlpi-summary", f"chapter-{ch_num:02d}.txt")
    if os.path.exists(summary_file):
        with open(summary_file, "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    return ""

def load_official_listings():
    listings_by_ch = {}
    html_file = "/tmp/tlpi_all_files_by_chapter.html"
    if not os.path.exists(html_file):
        return listings_by_ch
    
    with open(html_file, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    blocks = re.findall(r'<h2 id=\"ch(\d+)\">Chapter\s+\d+:\s+([^<]+)</h2>\s+<p class=\"top\">.*?<ul>(.*?)</ul>', html, re.DOTALL)
    for ch_str, ch_title, ul in blocks:
        ch = int(ch_str)
        items = re.findall(r'<li><a href=\"dist/([^\"]+)\">([^<]+)</a>(?:\s*\(([^)]+)\))?</li>', ul)
        listings_by_ch[ch] = items
    return listings_by_ch

def load_exercises():
    exercises_by_ch = {}
    imp_files = sorted(glob.glob(os.path.join(TLPIEXER_DIR, "src", "imp", "*.c")))
    for path in imp_files:
        base = os.path.basename(path)
        if base == "run.c":
            continue
        m = re.match(r'^(\d+)', base)
        if m:
            ch = int(m.group(1))
            exercises_by_ch.setdefault(ch, []).append(path)
    return exercises_by_ch

def parse_exercise_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    req_match = re.search(r'REQUIREMENT\s*\n\s*\n(.*?)\n\s*SOLUTION', content, re.DOTALL)
    req = req_match.group(1).strip() if req_match else "원서 연습문제를 읽고 요구사항을 충족하는 C++ 프로그램을 작성하세요."
    
    sol_match = re.search(r'SOLUTION\s*\n\s*\n(.*?)\n\s*USAGE', content, re.DOTALL)
    sol = sol_match.group(1).strip() if sol_match else "시스템 콜 인터페이스를 활용하여 요구사항을 단계별로 구현합니다."
    
    code_match = re.search(r'\*/\s*\n(.*)', content, re.DOTALL)
    code = code_match.group(1).strip() if code_match else content
    
    return req, sol, code

def find_man_links(code_text):
    syscalls = ["open", "creat", "read", "write", "close", "lseek", "dup", "dup2", "fcntl", "ioctl",
                 "stat", "lstat", "fstat", "chmod", "chown", "unlink", "link", "symlink", "readlink",
                 "mmap", "munmap", "mprotect", "fork", "vfork", "clone", "execve", "waitpid", "waitid",
                 "pipe", "pipe2", "mkfifo", "socket", "bind", "listen", "accept", "connect", "send", "recv",
                 "epoll_create", "epoll_create1", "epoll_ctl", "epoll_wait", "select", "poll", "signalfd",
                 "timerfd_create", "eventfd", "pthread_create", "pthread_join", "pthread_mutex_lock"]
    found = []
    for sc in syscalls:
        if re.search(r'\b' + sc + r'\s*\(', code_text):
            found.append(sc)
    return found[:5]

def generate_all():
    print("🚀 TLPI 1·2권 전수 스캐폴딩(391개 공식 예제 + 194개 연습문제) 생성을 시작합니다...")
    os.makedirs(TLPI_TARGET_DIR, exist_ok=True)
    
    listings_by_ch = load_official_listings()
    exercises_by_ch = load_exercises()
    
    # Supplementary listings mapping
    supp_dirs = {
        65: ("getopt", "t_getopt.c"),
        66: ("namespaces", "*.c"),
        67: ("seccomp", "*.c"),
        68: ("vdso", "gettimeofday.c")
    }
    
    total_generated = 0
    chapter_index_data = []

    for ch_num in range(1, 69):
        if ch_num not in CHAPTER_TITLES:
            continue
        en_title, ko_title = CHAPTER_TITLES[ch_num]
        ch_slug = slugify(en_title)
        ch_dir_name = f"{ch_num:02d}_{ch_slug}"
        ch_dir_path = os.path.join(TLPI_TARGET_DIR, ch_dir_name)
        os.makedirs(ch_dir_path, exist_ok=True)
        
        ch_summary = load_chapter_summary(ch_num)
        ch_listings = listings_by_ch.get(ch_num, [])
        ch_exercises = exercises_by_ch.get(ch_num, [])
        
        # Add supplementary
        if ch_num in supp_dirs:
            s_dir, s_pattern = supp_dirs[ch_num]
            s_files = glob.glob(os.path.join(TLPI_DIST_DIR, s_dir, s_pattern))
            for sf in s_files:
                base = os.path.basename(sf)
                rel = f"{s_dir}/{base}"
                ch_listings.append((rel, rel, f"Supplementary: {s_dir}"))
        
        item_counter = 1
        chapter_items = []
        
        # 1. Generate Listings
        for rel_path, display_name, *desc in ch_listings:
            clean_name = os.path.splitext(os.path.basename(rel_path))[0]
            item_slug = f"{item_counter:02d}_listing_{slugify(clean_name)}"
            item_path = os.path.join(ch_dir_path, item_slug)
            os.makedirs(item_path, exist_ok=True)
            
            src_file = os.path.join(TLPI_DIST_DIR, rel_path)
            orig_code = ""
            if os.path.exists(src_file):
                with open(src_file, "r", encoding="utf-8", errors="replace") as f:
                    orig_code = f.read()
            else:
                orig_code = f"// Source: {rel_path}\n#include <iostream>\n\nint main() {{ std::cout << \"TLPI {rel_path}\" << std::endl; return 0; }}\n"
            
            man_links = find_man_links(orig_code)
            man_text = ", ".join([f"`{m}(2)`" for m in man_links]) if man_links else "`시스템 콜`"
            desc_text = desc[0] if desc else "원서 공식 본문 예제 프로그램"
            
            # Write README.md
            suite_name = f"TLPI_Ch{ch_num:02d}_{slugify(clean_name)}"
            readme_content = f"""# 🐧 [TLPI Ch {ch_num:02d}] {clean_name} ({desc_text})

- **챕터**: {ch_num}장. {en_title} ({ko_title})
- **원본 소스**: `{rel_path}`
- **관련 man7 매뉴얼**: {man_text} (터미널 조회: `./scripts/man.sh {man_links[0] if man_links else 'intro'}`)

## 1. 예제 개요 및 개념
본 예제는 TLPI 원서 본문에서 다루는 `{clean_name}` 공식 실습 코드입니다.
리눅스 커널 시스템 콜과 POSIX C 라이브러리의 동작 원리를 검증하고 테스트합니다.

## 2. 주요 단계별 구현 (Step Guide)
- **Step 1**: 필요한 시스템 헤더(`<fcntl.h>`, `<unistd.h>`, `<sys/stat.h>` 등)를 인클루드합니다.
- **Step 2**: 명령줄 인자(argc, argv)를 검증하고 파일/디스크립터 리소스를 엽니다.
- **Step 3**: 핵심 시스템 콜을 수행하고 반환값 및 에러(`errno`)를 검사합니다.
- **Step 4**: 할당된 자원을 닫고(`close`) 안전하게 프로그램을 종료합니다.

## 3. 추천 GoogleTest 검증 코드 예시 (`test.cpp`)
아래 예시를 참고하여 `test.cpp`에 직접 단위 테스트를 타이핑하여 작성해 보세요.

```cpp
#include <gtest/gtest.h>

TEST({suite_name}, TestSample) {{
    // TODO: 시스템 콜 반환값 및 에러 처리를 검증하는 테스트를 직접 타이핑하세요.
    EXPECT_TRUE(true);
}}
```

## 4. 컴파일 및 실행 사이클
```bash
# 1) 직접 작성한 main.cpp 즉시 컴파일 & 실행 (0.1초 고속 빌드)
./scripts/run.sh {item_path}

# 2) 직접 작성한 test.cpp GoogleTest 단위 테스트 자동 검증
./scripts/test.sh {item_path}
```
"""
            with open(os.path.join(item_path, "README.md"), "w", encoding="utf-8") as f:
                f.write(readme_content)
                
            # Write main.cpp
            main_cpp = f"""// ==============================================================================
// [TLPI Ch {ch_num:02d}] {clean_name}
// 원서 예제: {rel_path} ({desc_text})
// 같은 폴더의 README.md 에 있는 개념 해설과 단계별 가이드를 보며 직접 타이핑해 보세요.
// ==============================================================================

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <iostream>

// 간이 에러 진단 헬퍼
static void errExit(const char *msg) {{
    std::perror(msg);
    std::exit(EXIT_FAILURE);
}}

int main(int argc, char *argv[]) {{
    // Step 1: 환경 설정 및 실행 알림
    std::cout << "[TLPI Ch {ch_num:02d}] Running listing: {clean_name}" << std::endl;

    // Step 2: 핵심 시스템 콜 데모 실행 (원서 {rel_path} 참조하여 직접 작성)

    return 0;
}}
"""
            with open(os.path.join(item_path, "main.cpp"), "w", encoding="utf-8") as f:
                f.write(main_cpp)
                
            # Write test.cpp
            test_cpp = f"""// ==============================================================================
// [TLPI Ch {ch_num:02d}] {clean_name}
//
// 같은 폴더의 README.md 에 있는 목표 코드와 추천 GoogleTest 코드를 참고하여
// 직접 테스트 케이스를 타이핑하여 완성해 보세요.
// ==============================================================================

#include <gtest/gtest.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

TEST({suite_name}, TODO) {{
    // TODO: 여기에 직접 GoogleTest 케이스를 타이핑하세요.
    EXPECT_TRUE(true);
}}
"""
            with open(os.path.join(item_path, "test.cpp"), "w", encoding="utf-8") as f:
                f.write(test_cpp)
                
            chapter_items.append((item_slug, f"Listing: {clean_name}", desc_text))
            item_counter += 1
            total_generated += 1

        # 2. Generate Exercises
        for ex_file in ch_exercises:
            ex_base = os.path.splitext(os.path.basename(ex_file))[0]
            ex_req, ex_sol, ex_code = parse_exercise_file(ex_file)
            
            item_slug = f"{item_counter:02d}_exercise_{slugify(ex_base)}"
            item_path = os.path.join(ch_dir_path, item_slug)
            os.makedirs(item_path, exist_ok=True)
            
            man_links = find_man_links(ex_code)
            man_text = ", ".join([f"`{m}(2)`" for m in man_links]) if man_links else "`시스템 콜`"
            
            # Write README.md
            ex_suite_name = f"TLPI_Ch{ch_num:02d}_Exercise_{slugify(ex_base)}"
            readme_content = f"""# 📝 [TLPI Ch {ch_num:02d} Exercise {ex_base}] 실전 프로그래밍 과제

- **챕터**: {ch_num}장. {en_title} ({ko_title})
- **과제 번호**: Exercise {ex_base}
- **관련 man7 매뉴얼**: {man_text} (터미널 조회: `./scripts/man.sh {man_links[0] if man_links else 'intro'}`)

## 1. 문제 요구사항 (Requirement from Book)
```text
{ex_req}
```

## 2. 해결 방안 및 설계 (Solution Architecture)
```text
{ex_sol}
```

## 3. 단계별 실습 가이드 (Step-by-Step Implementation)
- **Step 1**: 요구되는 시스템 헤더를 포함하고 인자 처리(`argc`, `argv`)를 작성합니다.
- **Step 2**: 시스템 콜 에러 조건(`-1`)에 대해 철저한 방어 코드를 작성합니다.
- **Step 3**: `README.md`의 요구사항을 통과하는 알고리즘 및 I/O 파이프라인을 완성합니다.
- **Step 4**: `test.cpp`의 GoogleTest 단위 테스트를 직접 타이핑하여 정답 여부를 검증합니다.

## 4. 추천 GoogleTest 검증 코드 예시 (`test.cpp`)
아래 예시를 참고하여 `test.cpp`에 직접 단위 테스트를 타이핑하여 작성해 보세요.

```cpp
#include <gtest/gtest.h>

TEST({ex_suite_name}, VerifyRequirement) {{
    // TODO: 연습문제 요구조건 및 반환값을 검증하는 테스트를 직접 타이핑하세요.
    EXPECT_TRUE(true);
}}
```

## 5. 컴파일 및 테스트 실행 사이클
```bash
# 1) 직접 작성한 main.cpp 실행
./scripts/run.sh {item_path}

# 2) 직접 작성한 test.cpp GoogleTest 자동 채점 검증
./scripts/test.sh {item_path}
```
"""
            with open(os.path.join(item_path, "README.md"), "w", encoding="utf-8") as f:
                f.write(readme_content)
                
            # Write main.cpp
            main_cpp = f"""// ==============================================================================
// [TLPI Ch {ch_num:02d} Exercise {ex_base}]
// 실전 연습문제 구현 스켈레톤
// 같은 폴더의 README.md 에 있는 요구사항과 설계 가이드를 보며 직접 타이핑해 보세요.
// ==============================================================================

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <iostream>

static void errExit(const char *msg) {{
    std::perror(msg);
    std::exit(EXIT_FAILURE);
}}

int main(int argc, char *argv[]) {{
    // Step 1: 문제 요구사항 확인 (README.md 참조)
    std::cout << "[TLPI Ch {ch_num:02d} Exercise {ex_base}] Solution Running..." << std::endl;

    // Step 2: 여기에 시스템 콜 기반 해결 코드를 직접 작성하세요.

    return 0;
}}
"""
            with open(os.path.join(item_path, "main.cpp"), "w", encoding="utf-8") as f:
                f.write(main_cpp)
                
            # Write test.cpp
            test_cpp = f"""// ==============================================================================
// [TLPI Ch {ch_num:02d} Exercise {ex_base}]
//
// 같은 폴더의 README.md 에 있는 목표 코드와 추천 GoogleTest 코드를 참고하여
// 직접 테스트 케이스를 타이핑하여 완성해 보세요.
// ==============================================================================

#include <gtest/gtest.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

TEST({ex_suite_name}, TODO) {{
    // TODO: 여기에 직접 GoogleTest 케이스를 타이핑하세요.
    EXPECT_TRUE(true);
}}
"""
            with open(os.path.join(item_path, "test.cpp"), "w", encoding="utf-8") as f:
                f.write(test_cpp)
                
            chapter_items.append((item_slug, f"Exercise {ex_base}", ex_req.splitlines()[0] if ex_req else ""))
            item_counter += 1
            total_generated += 1

        # Write Chapter README.md
        ch_readme = f"""# 📖 {ch_num}장. {en_title} ({ko_title})

> **The Linux Programming Interface (Michael Kerrisk)**  
> **총 실습 항목: {len(chapter_items)}개 (공식 예제 {len(ch_listings)}개 + 연습문제 {len(ch_exercises)}개)**

---

## 1. 챕터 개요 및 요약 (Overview & Summary)

```text
{ch_summary if ch_summary else en_title + ' - 리눅스 시스템 프로그래밍 핵심 개념'}
```

---

## 2. 챕터 전체 실습 및 연습문제 목록

| 번호 | 폴더명 | 분류 | 설명 |
|:---:|:---|:---:|:---|
"""
        for it_slug, it_type, it_desc in chapter_items:
            ch_readme += f"| {it_slug[:2]} | [`{it_slug}`]({it_slug}/) | {it_type} | {it_desc[:60]} |\n"
            
        with open(os.path.join(ch_dir_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(ch_readme)
            
        chapter_index_data.append((ch_num, en_title, ko_title, ch_dir_name, len(chapter_items), len(ch_listings), len(ch_exercises)))

    # Master README.md in practice/linux/01_tlpi_system_programming
    master_readme = """# 🐧 The Linux Programming Interface (TLPI) 1·2권 전수 실습 트랙

> **Michael Kerrisk 저 | 총 64개 전 챕터 + 부록 및 보충 트랙 (총 68개)**  
> **총 391개 공식 예제 프로그램 + 194개 공식 연습문제 (Exercises) 전수 수록**

---

## 📚 챕터별 실습 트랙 마스터 색인

| 챕터 | 영문 챕터명 | 한글 주제 | 폴더 링크 | 전체 항목 | 공식 예제 | 연습문제 |
|:---:|:---|:---|:---|:---:|:---:|:---:|
"""
    for ch_num, en, ko, folder, total, n_list, n_ex in chapter_index_data:
        master_readme += f"| {ch_num:02d} | {en} | {ko} | [{folder}](./{folder}/) | **{total}** | {n_list} | {n_ex} |\n"

    master_readme += f"""
---

## 🛠️ 실습 및 검증 방법

```bash
# 1) man7 공식 매뉴얼 터미널 열람
./scripts/man.sh epoll_create
./scripts/man.sh read 2

# 2) 특정 항목 즉시 컴파일 & 실행
./scripts/run.sh practice/linux/01_tlpi_system_programming/04_file_io_universal_i_o_model/01_listing_copy

# 3) 특정 항목 GoogleTest 단위 테스트 검증
./scripts/test.sh practice/linux/01_tlpi_system_programming/04_file_io_universal_i_o_model/01_listing_copy
```
"""
    with open(os.path.join(TLPI_TARGET_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(master_readme)
        
    print(f"\n✨ TLPI 전수 스캐폴딩 완료!")
    print(f"📊 총 68개 챕터, {total_generated}개 전체 실습 항목 생성 완료.")
    print(f"📄 마스터 색인: {os.path.join(TLPI_TARGET_DIR, 'README.md')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate full TLPI scaffolding")
    parser.add_argument("--force", action="store_true", help="Force overwrite")
    args = parser.parse_args()
    generate_all()
