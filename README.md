# handcrafted-cpp — 소프트웨어 장인정신 기반 C/C++·리눅스·알고리즘 전수 타이핑 연습장

> *"AI가 코드를 쏟아내는 시대일수록, 한 글자씩 정성껏 손으로 빚고(Handcrafted) 0.1초 만에 검증하는 장인정신(Craftsmanship)이 진짜 차이를 만듭니다."*  
> *(참조 철학: 《소프트웨어 장인정신》, 《Code Complete 2》, 《실용주의 프로그래머》)*  
>
> 🚀 초심자를 위한 완벽 실습 가이드 (5단계 사이클 & CLion 디버깅): [PRACTICE_GUIDE.md](PRACTICE_GUIDE.md)  
> 🏗️ 프로젝트 아키텍처 및 디렉터리 트리 상세 설계서: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)  
> 🔍 C++17 표준 헤더 / libc++ / POSIX 3,686개 심볼 소스라인 색인: [EXTERNAL_LIBRARIES.md](EXTERNAL_LIBRARIES.md)  
> 📖 GoogleTest & GoogleMock 공식 오프라인 가이드: [docs/googletest/](docs/googletest/)  
> 🐧 Linux man7.org 공식 매뉴얼 2,666개 오프라인 뷰어: `./scripts/man.sh`

본 저장소는 C/C++ 기초 문법부터 모던 C++20/C++23, 리눅스 시스템 프로그래밍, CLI 자동화, 대회용 알고리즘(종만북), 도널드 크누스 조합 알고리즘(TAOCP), BPF 성능 분석, ARM 리눅스 커널까지 총 17개 트랙, 2,535개의 방대한 실습 항목을 단 1개의 축약도 없이(Zero Abbreviation) 전수 수록한 엔지니어링 연습장입니다.

각 실습 항목 폴더는 표준화된 자기완비형(Self-contained) 3-파일 구조로 설계되었습니다:
- `README.md`: 원서 챕터/페이지, 핵심 개념, 알고리즘 및 시스템콜 해설, 컴파일/실행 가이드
- `main.cpp`: 학습자가 타이핑하고 즉시 실행할 수 있는 메인 소스 코드
- `test.cpp`: GoogleTest 기반 자동 채점 및 단위 검증 테스트 코드
- `(*.in, *.out)`: [종만북/알고리즘 트랙] 공식 입력 테스트케이스 및 예상 정답 데이터

---

## 📊 전체 트랙 및 실습 규모 (총 2,535개 항목)

| 대분류 | 트랙 / 도서명 | 원본 및 표준 | 챕터 / 섹션 | 실습 항목 수 | 특징 및 주요 내용 |
|:---|:---|:---|:---:|:---:|:---|
| 큰돌 강의 1: 문법/STL | `practice/stone-lecture/01_문법_STL/` | 큰돌 C++ 알고리즘 교안 | 14개 섹션 | 182개 | 기초 문법, STL 필수 컨테이너(vector, map, set), 문자열 처리 |
| 큰돌 강의 2: 알고리즘 | `practice/stone-lecture/02_알고리즘_개념/` | 알고리즘 개념 교안 | 22개 섹션 | 67개 | 시간복잡도, 재귀, 정렬, 투 포인터, 그리디, 이진 탐색, LCS |
| 큰돌 강의 3: 문제풀이 | `practice/stone-lecture/03_실전_문제풀이/` | 8주차 실전 문제해설 | 8개 섹션 | 160개 | 누적합, 완전탐색, BFS/DFS, 백트래킹, 비트마스킹, DP, 펜윅트리 |
| C/C++ 도서 1 | `practice/c-and-cpp/01_c_300/` | 초보자를 위한 C언어 300제 | 6개 챕터 | 315개 | C 기초 문법 300제 전수 + 실무 부록 15개 |
| C/C++ 도서 2 | `practice/c-and-cpp/02_c_100/` | 실무자를 위한 C언어 100제 | 5개 챕터 | 100개 | 실무 포인터, 동적 메모리, 파일 I/O 100제 전 문항 |
| C/C++ 도서 3 | `practice/c-and-cpp/03_tour_of_cpp/` | A Tour of C++ 3rd Ed (Bjarne Stroustrup) | 16개 챕터 | 113개 | C++ 창시자의 모던 C++20 전반 투어 전 절 |
| C/C++ 도서 4 | `practice/c-and-cpp/04_cpp_stl/` | C++ STL 프로그래밍 | 10개 챕터 | 100개 | STL 컨테이너, 반복자, 함수 객체, 알고리즘 전 레시피 |
| C/C++ 도서 5 | `practice/c-and-cpp/05_high_perf_cpp/` | 고성능을 위한 C++ | 11개 챕터 | 80개 | 캐시 친화적 자료구조, 이동 시맨틱, 무비용 추상화, 동시성 |
| C/C++ 도서 6 | `practice/c-and-cpp/06_algo_generic/` | 알고리즘 산책: 수학에서 제네릭까지 | 15개 챕터 | 104개 | 알렉산더 스테파노프의 제네릭 프로그래밍 수학적 원리 전 장 |
| C/C++ 도서 7 | `practice/c-and-cpp/07_extreme_c/` | 전문가를 위한 C (Extreme C) | 23개 전 챕터 | 114개 | C OOP 캡슐화/상속/다형성, POSIX IPC, 동시성, 네트워크 스택 |
| C/C++ 도서 8 | `practice/c-and-cpp/08_prof_cpp/` | 전문가를 위한 C++ 6th Ed (Marc Gregoire) | 35개 전 챕터 | 499개 | Wiley 공식 345개 예제 + 154개 공식 연습문제 (C++20/C++23) |
| 리눅스 시스템 | `practice/linux/01_tlpi_system_programming/` | The Linux Programming Interface (TLPI) | 68개 전 챕터 | 506개 | 312개 공식 예제 + 194개 연습문제 전수 (syscall, epoll, IPC) |
| 리눅스 자동화 | `practice/linux/02_cli_and_shell_automation/` | Efficient Linux & Adventures with Linux CLI | 24개 전 챕터 | 46개 | 파이프라인, AWK, xargs, tput, dialog, tmux, SQLite3 CLI |
| 리눅스 BPF/eBPF | `practice/linux/03_bpf_performance_tools/` | BPF 성능 분석 도구 (Brendan Gregg) | 18개 전 챕터 | 26개 | eBPF, BCC, bpftrace, CPU/메모리/네트워크/보안 커널 트레이싱 |
| ARM 커널 심층 | `practice/linux/04_arm_kernel/` | 코드로 알아보는 ARM 리눅스 커널 (강진우) | 9개 핵심 챕터 | 16개 | ARMv8 아키텍처, 부팅(head.S), 4레벨 페이징, 버디/SLUB, CFS |
| 알고리즘 대회 | `practice/jongmanbook/` | 알고리즘 문제 해결 전략 (종만북 1·2권) | 32개 전 챕터 | 94개 | 구종만 저자 공식 100개 Algospot 문제 + 입출력 테스트베드 |
| 조합 알고리즘 | `practice/knuth/` | The Art of Computer Programming Vol 4A (도널드 크누스) | 2개 전 챕터 | 13개 | 조합 알고리즘(비트 트릭, 순열/조합/분할 전수 생성) 원전 구현체 |
| 합계 | 17개 통합 트랙 | C11 / C++17 / C++20 / C++23 / POSIX | 318개 챕터 | 2,535개 | 축약 없는 완전판 전수 수록 (Zero Abbreviation) |

---

## ⚡ 초고속 빌드 및 테스트 파이프라인

본 저장소는 2,535개의 타깃 환경에서도 단 0.1초 만에 실행 및 테스트가 가능하도록 이원화된 Fast-path 파이프라인을 지원합니다.

### 1. 단일 항목 초고속 컴파일 및 실행 (`./scripts/run.sh`)
CMake 전체 메이크파일 생성 없이 `clang++ / g++`로 현재 항목의 `main.cpp`(및 필요한 헬퍼 C/C++ 파일)만 즉시 빌드하여 실행합니다. C++20/C++23(`<print>`, `std::println`) 문법을 자동 감지합니다.
```bash
# 큰돌 강의 예제 실행
./scripts/run.sh practice/stone-lecture/01_문법_STL/01_기본/02_typedef

# 전문가를 위한 C++ 6th Ed 예제 실행 (C++23 std::println 지원)
./scripts/run.sh practice/c-and-cpp/08_prof_cpp/01_a_crash_course_in_c_and_the_standard_library/01_example_01_helloworld

# 종만북 소풍(PICNIC) 공식 문제 실행 (공식 입력 파일 파이프 전달)
./scripts/run.sh practice/jongmanbook/06_brute_force/02_picnic < practice/jongmanbook/06_brute_force/02_picnic/picnic.in
```

### 2. 단일 항목 GoogleTest 0.1초 Fast-path 검증 (`./scripts/test.sh`)
수천 개 타깃으로 인한 CMake 지연을 완전히 제거하기 위해, 사전에 빌드된 GoogleTest 정적 라이브러리(`libgtest_main.a`)를 직접 링크하여 0.1~0.2초 내로 단위 테스트 결과를 즉시 출력합니다.
```bash
# 큰돌 강의 예제 GoogleTest 단위 검증
./scripts/test.sh practice/stone-lecture/01_문법_STL/01_기본/02_typedef

# C++ 도서 연습문제 GoogleTest 단위 검증
./scripts/test.sh practice/c-and-cpp/08_prof_cpp/01_a_crash_course_in_c_and_the_standard_library/32_exercise_01_1

# 리눅스 시스템 프로그래밍 (TLPI) 연습문제 자동 검증
./scripts/test.sh practice/linux/01_tlpi_system_programming/04_file_i_o_the_universal_i_o_model/03_exercise_04_01

# 종만북 알고리즘 문제 GoogleTest 검증
./scripts/test.sh practice/jongmanbook/06_brute_force/02_picnic
```

### 3. 오프라인 Linux man7 매뉴얼 뷰어 (`./scripts/man.sh`)
인터넷 연결이 없는 환경에서도 `docs/linux/01_tlpi_system_programming/man-pages/`에 수록된 2,666개의 공식 man-pages를 터미널에서 즉시 조회할 수 있습니다.
```bash
./scripts/man.sh epoll_create        # epoll_create(2) 시스템콜 열람
./scripts/man.sh 2 open              # Section 2 open 시스템콜 열람
./scripts/man.sh --list inotify      # inotify 관련 매뉴얼 검색
```

---

## 📌 `[[snippet]]` 코드 스니펫 추출 및 자동 색인

기억하고 싶은 함수, 클래스, 구조체 정의 위에 C++17 표준 어트리뷰트인 `[[snippet]]` 또는 `[[snippet("설명")]]`을 붙이면, 컴파일 에러 없이 그대로 동작하며 나중에 원하는 스니펫만 통째로 추출하여 마크다운 노트로 내보낼 수 있습니다.

```cpp
[[snippet("문자열을 delimiter 기준으로 쪼개는 함수")]]
vector<string> split(const string& input, string delimiter) {
    vector<string> result;
    // ...
    return result;
}

struct [[snippet("유니온 파인드 기본 구현")]] DisjointSet {
    // ...
};
```

```bash
./scripts/snippets.sh                  # 전체 스니펫 코드 터미널 출력
./scripts/snippets.sh split            # 키워드로 필터링 검색
./scripts/snippets.sh --list           # 요약 목록만 보기
./scripts/snippets.sh --status         # 사람 검증 상태 대시보드 조회
./scripts/snippets.sh --verify "split()" --reviewer "이름"  # 사람 검증 승인 및 해시 기록
./scripts/snippets.sh --export         # tips/snippets.md 도서 출처 포함 대시보드 저장
./scripts/snippets.sh --export-blog    # tips/posts/ 에 GitHub Pages 기술 블로그 포스트 개별 발행
```

---

## 🛠️ 스크립트 도구 모음

| 스크립트 | 용도 및 기능 |
|:---|:---|
| `scripts/run.sh <경로>` | `main.cpp` 초고속 직접 컴파일 및 실행 (C++17/20/23 자동 감지, 0.1초 고속 빌드) |
| `scripts/test.sh <경로>` | 사전 빌드된 GoogleTest 라이브러리를 직접 링크하는 0.1초 Fast-path 단위 테스트 러너 |
| `scripts/man.sh <명령어>` | Linux man-pages 6.20 2,666개 공식 매뉴얼 오프라인 터미널 뷰어 |
| `scripts/linux_run.sh <경로>` | 리눅스 트랙 전용 통합 실행기 (macOS 호스트 실행 및 `--docker` 순정 리눅스 컨테이너 빌드) |
| `scripts/snippets.sh` | `[[snippet]]` 태그 함수 검색, 사람 단위검증 승인, 도서 출처 자동 인용 및 기술 블로그 포스트 발행 |
| `scripts/locate.sh <경로/검색어>` | 실습 파일 위치 네비게이터 (어느 책, 몇 장, 몇 절, 몇 문단/페이지 실시간 색인) |
| `scripts/sync_all.sh` | 목차/트리구조 변경 시 프론트매터 및 트리 일괄 동기화 마스터 파이프라인 |
| `scripts/cxx_wrapper.sh` | 컴파일 시 `@snippet` 및 어트리뷰트 문법을 안전하게 가로채는 컴파일러 인터셉터 |
| `scripts/help.sh` | 프로젝트 내 주요 명령어 치트시트 출력 |
| `scripts/generate_linux_tlpi_full.py` | TLPI 68개 전 챕터 (506개: 312예제 + 194연습문제) 전수 생성기 |
| `scripts/generate_linux_cli_full.py` | 리눅스 CLI 24개 전 챕터 (46개 항목) 전수 생성기 |
| `scripts/generate_content_07_full.py` | Extreme C 23개 전 챕터 (114개 항목) 전수 생성기 |
| `scripts/generate_content_08_full.py` | Professional C++ 35개 전 챕터 (499개 항목) 전수 생성기 |
| `scripts/generate_jongmanbook_full.py` | 종만북 32개 전 챕터 (94개 항목) 전수 생성기 |
| `scripts/generate_knuth.py` | TAOCP Vol 4A 조합 알고리즘 2개 전 챕터 (13개 항목) 전수 생성기 |
| `scripts/generate_external_libs_index.py` | libc++/POSIX 헤더/GoogleTest 소스 위치 3,686개 전수 색인 (`EXTERNAL_LIBRARIES.md`) |
| `scripts/apply_file_frontmatter.py` | 모든 말단 노드 파일 상단에 `@file` 및 `@path` 주석 프론트매터 자동 주입 도구 |

---

## 📖 라이선스 및 저작권 안내
본 프로젝트에서 직접 작성한 코드와 문서(스캐폴딩 생성기 `scripts/`, 실행 도구, 색인 엔진)는 [GNU AGPL-3.0-only](./LICENSE)를 따릅니다(2026-10-31 MIT에서 변경).

교안·도서 원문(PDF)과, 그것을 바탕으로 만든 실습 디렉터리 `practice/` 전체(도서 예제 코드, 실습 스켈레톤, 입력 데이터, 벤더 라이브러리 사본 포함)는 저작권자 소유이거나 도서에 의존하므로 `.gitignore`로 Git 추적에서 제외합니다. 로컬에서 `scripts/` 생성기로 다시 만들 수 있습니다(원본 도서 자료 필요).
