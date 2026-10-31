#!/usr/bin/env bash
# 프로젝트 내 컴파일·실행·테스트·스니펫 도구 사용법을 한눈에 출력한다.
set -euo pipefail

cat << 'EOF'
======================================================================
 🛠️  handcrafted-cpp 빠른 명령어 치트시트 (Cheat Sheet)
======================================================================

1. 단일 문제 빠른 컴파일 + 실행 (g++ -std=c++17/c++20/c++23 직접 호출, 0.1초 고속 빌드)
   ./scripts/run.sh practice/stone-lecture/01_문법_STL/01_기본/02_typedef
   ./scripts/run.sh practice/c-and-cpp/01_c_300/01_PART1_입문/001_C_프로그램_시작하기
   ./scripts/run.sh practice/c-and-cpp/08_prof_cpp/01_a_crash_course_in_c_and_the_standard_library/01_example_01_helloworld
   ./scripts/run.sh practice/jongmanbook/06_brute_force/02_picnic

2. 단일 문제 GoogleTest 빌드 + 실행 (Fast-path 0.1초 고속 검증)
   ./scripts/test.sh practice/stone-lecture/01_문법_STL/01_기본/02_typedef
   ./scripts/test.sh practice/c-and-cpp/08_prof_cpp/01_a_crash_course_in_c_and_the_standard_library/32_exercise_01_1
   ./scripts/test.sh practice/linux/01_tlpi_system_programming/04_file_i_o_the_universal_i_o_model/03_exercise_04_01
   ./scripts/test.sh practice/jongmanbook/06_brute_force/02_picnic
   ./scripts/test.sh practice/knuth/01_zeros_and_ones/03_bitwise_tricks

3. 실습 파일 위치 네비게이터 (어느 책, 몇 장, 몇 절, 몇 문단/페이지 실시간 색인)
   ./scripts/locate.sh practice/stone-lecture/01_문법_STL/03_타입과_타입변환/12_string_split_콤마/main.cpp
   ./scripts/locate.sh split                    # 키워드로 검색하여 위치 찾기
   ./scripts/locate.sh --tree                   # 전체 도서·장·절 목차 트리 출력

4. 오프라인 Linux man7 매뉴얼 뷰어 (man-pages 6.20 2,666개 전수 수록)
   ./scripts/man.sh epoll_create
   ./scripts/man.sh 2 open
   ./scripts/man.sh --list inotify

5. [[snippet]] 스니펫 검색, 추출, 사람 검증 및 블로그 발행 장치
   ./scripts/snippets.sh                  # 등록된 모든 스니펫 코드 전체 출력
   ./scripts/snippets.sh split            # 키워드(함수명/메모/경로)로 필터링 검색
   ./scripts/snippets.sh --list           # 코드 없이 요약 목록만 출력
   ./scripts/snippets.sh --status         # 사람 검증 상태 대시보드 (VERIFIED/PENDING/OUTDATED)
   ./scripts/snippets.sh --verify "split()" --reviewer "이름" --notes "검증메모"  # 사람 검증 승인 및 해시 박제
   ./scripts/snippets.sh --export         # tips/snippets.md 마크다운 대시보드 저장
   ./scripts/snippets.sh --export-blog    # tips/posts/ 에 GitHub Pages/Jekyll용 기술 블로그 포스트 발행

6. 리눅스 시스템 프로그래밍 & CLI 자동화 실행 (practice/linux/)
   ./scripts/linux_run.sh practice/linux/01_tlpi_system_programming/04_file_i_o_the_universal_i_o_model/01_listing_copy_c
   ./scripts/linux_run.sh practice/linux/02_cli_and_shell_automation/01_combine_commands/01_pipes_and_tee
   ./scripts/linux_run.sh --docker practice/linux/01_tlpi_system_programming/63_alternative_io_models/01_listing_63_01_epoll_input

7. 목차/트리구조 변경 시 마스터 일괄 동기화 (Sync Pipeline)
   ./scripts/sync_all.sh                        # 프론트매터 갱신 및 전체 목차 트리 무결성 검증

8. 전수 스캐폴딩 생성 엔진 (축약 없는 완전판 전수 복원)
   python3 scripts/generate_linux_tlpi_full.py      # TLPI 68개 전 챕터 (506제)
   python3 scripts/generate_linux_cli_full.py       # Linux CLI 24개 전 챕터 (46제)
   python3 scripts/generate_content_07_full.py      # Extreme C 23개 전 챕터 (114제)
   python3 scripts/generate_content_08_full.py      # Professional C++ 35개 전 챕터 (499제)
   python3 scripts/generate_jongmanbook_full.py     # 종만북 32개 전 챕터 (94제)
   python3 scripts/generate_knuth.py                # TAOCP Vol 4A 조합 알고리즘 (13제)

9. 말단 노드 파일 경로 프론트매터 자동 주석 삽입 엔진
   python3 scripts/apply_file_frontmatter.py        # practice/ 내 모든 파일에 @file/@path 주석 프론트매터 적용

10. 외부 라이브러리(libc++/POSIX 헤더/GoogleTest) 소스 내비게이션 인덱스 재생성
   python3 scripts/generate_external_libs_index.py   # → EXTERNAL_LIBRARIES.md
======================================================================
자세한 설명은 루트의 README.md 를 참고하세요.
EOF
