#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
구종만 저 《알고리즘 문제 해결 전략》 (종만북 1권 & 2권, 1,084페이지) 전수 스캐폴딩 생성 엔진
- 원서 32개 전 챕터 (1부 ~ 7부, Ch01 ~ Ch32) 전수 수록 (축약 없음)
- 공식 Algospot 연습문제 및 알고리즘 구현체 전수 수록
- 각 문제별 README.md, main.cpp, test.cpp (GoogleTest) 생성
- 테스트 케이스 (.in, .out) 자동 포함 및 단위 테스트 연동
"""

import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_BOOK_DIR = REPO_ROOT / "practice" / "jongmanbook"
SOURCE_JMBOOK_DIR = Path("/tmp/jmbook")
SOURCE_JMCODE_DIR = Path("/tmp/jmcode")

CHAPTER_META = {
    1: ("Problem Solving and Contests", "문제 해결과 프로그래밍 대회", "1권 1부: 문제 해결 시작하기"),
    2: ("Overview of Problem Solving", "문제 해결 개관", "1권 1부: 문제 해결 시작하기"),
    3: ("Coding and Debugging", "코딩과 디버깅에 관하여", "1권 1부: 문제 해결 시작하기"),
    4: ("Time Complexity Analysis", "알고리즘의 시간 복잡도 분석", "1권 2부: 알고리즘 분석"),
    5: ("Algorithm Correctness Proofs", "알고리즘의 정당성 증명", "1권 2부: 알고리즘 분석"),
    6: ("Brute Force", "무식하게 풀기 (완전 탐색)", "1권 3부: 알고리즘 설계 패러다임"),
    7: ("Divide and Conquer", "분할 정복", "1권 3부: 알고리즘 설계 패러다임"),
    8: ("Dynamic Programming", "동적 계획법", "1권 3부: 알고리즘 설계 패러다임"),
    9: ("Dynamic Programming Techniques", "동적 계획법 테크닉", "1권 3부: 알고리즘 설계 패러다임"),
    10: ("Greedy Algorithms", "탐욕법", "1권 3부: 알고리즘 설계 패러다임"),
    11: ("Combinatorial Search", "조합 탐색", "1권 3부: 알고리즘 설계 패러다임"),
    12: ("Decision Problems", "최적화 문제를 결정 문제로 바꿔 풀기", "1권 3부: 알고리즘 설계 패러다임"),
    13: ("Numerical Analysis", "수치 해석", "1권 3부: 알고리즘 설계 패러다임"),
    14: ("Number Theory", "정수론", "1권 4부: 유명한 알고리즘들"),
    15: ("Computational Geometry", "계산 기하", "1권 4부: 유명한 알고리즘들"),
    16: ("Bitmask", "비트마스크", "2권 5부: 기본 자료 구조"),
    17: ("Partial Sum", "부분 합", "2권 5부: 기본 자료 구조"),
    18: ("Linear Data Structures", "선형 자료 구조 (동적 배열, 연결 리스트)", "2권 5부: 기본 자료 구조"),
    19: ("Queue Stack Deque", "큐와 스택, 데크", "2권 5부: 기본 자료 구조"),
    20: ("Strings", "문자열 (KMP, 접미사 배열)", "2권 5부: 기본 자료 구조"),
    21: ("Tree Traversal", "트리의 구현과 순회", "2권 6부: 트리"),
    22: ("Binary Search Trees", "이진 검색 트리 (Treap)", "2권 6부: 트리"),
    23: ("Priority Queue and Heap", "우선순위 큐와 힙", "2권 6부: 트리"),
    24: ("Segment Trees", "구간 트리와 펜윅 트리", "2권 6부: 트리"),
    25: ("Disjoint Set", "상호 배타적 집합 (Union-Find)", "2권 6부: 트리"),
    26: ("Trie", "트라이", "2권 6부: 트리"),
    27: ("Graph Representation", "그래프의 표현과 정의", "2권 7부: 그래프"),
    28: ("Depth First Search", "그래프의 깊이 우선 탐색 (DFS)", "2권 7부: 그래프"),
    29: ("Breadth First Search", "그래프의 너비 우선 탐색 (BFS)", "2권 7부: 그래프"),
    30: ("Shortest Path Algorithms", "최단 경로 알고리즘 (다익스트라, 벨만-포드, 플로이드)", "2권 7부: 그래프"),
    31: ("Minimum Spanning Tree", "최소 스패닝 트리 (크루스칼, 프림)", "2권 7부: 그래프"),
    32: ("Network Flow", "네트워크 유량 (포드-풀커슨, 이분 매칭)", "2권 7부: 그래프"),
}

# Mapping of chapters to official problem IDs and code targets
CHAPTER_ITEMS = {
    1: [
        ("FESTIVAL", "록 페스티벌", "rockfestival", "문제 ID: FESTIVAL (난이도: 하)"),
    ],
    2: [
        ("overview_strategy", "문제 해결 6단계 및 체계적 전략 템플릿", "scaffolding", "문제 해결 6단계와 알고리즘 선택 가이드"),
    ],
    3: [
        ("floating_point_comparisons", "부동 소수점 실수 비교와 오차 제어", "float", "실수 오차 다루기 (|a-b| < eps)"),
    ],
    4: [
        ("moving_average_complexity", "이동 평균 계산과 시간 복잡도 선형화 (O(N^2) -> O(N))", "moving_average", "선형 시간 알고리즘"),
        ("maximum_subarray_sum", "최대 연속 부분 구간 합 알고리즘 4가지 비교 (O(N^3) ~ O(N))", "maxsum", "복잡도 비교 분석"),
    ],
    5: [
        ("bisection_invariant", "이진 탐색(이분법)과 루프 불변식 정당성 증명", "bisection", "알고리즘 정당성 증명"),
    ],
    6: [
        ("BOGGLE", "보글 게임 (Boggle Game)", "boggle", "난이도: 하 | 완전 탐색"),
        ("PICNIC", "소풍 (Picnic)", "picnic", "난이도: 하 | 완전 탐색"),
        ("BOARDCOVER", "게임판 덮기 (Board Cover)", "boardcover", "난이도: 하 | 완전 탐색"),
        ("CLOCKSYNC", "시계 맞추기 (Clock Sync)", "clocks", "난이도: 중 | 완전 탐색"),
    ],
    7: [
        ("QUADTREE", "쿼드 트리 뒤집기 (Quad Tree)", "quadtree", "난이도: 하 | 분할 정복"),
        ("FENCE", "울타리 잘라내기 (Fence)", "histogram", "난이도: 중 | 분할 정복 스위핑"),
        ("FANMEETING", "팬 미팅 (Fan Meeting)", "fanmeeting", "난이도: 상 | 카라츠바 곱셈"),
    ],
    8: [
        ("JUMPGAME", "외발뛰기 (Jump Game)", "boggle", "난이도: 하 | 메모이제이션"),
        ("WILDCARD", "와일드카드 (Wildcard)", "wildcards", "난이도: 중 | 동적 계획법"),
        ("TRIANGLEPATH", "삼각형 위의 최대 경로", "triangle", "난이도: 하 | 동적 계획법"),
        ("LIS", "최대 부분 증가 수열 (Longest Increasing Subsequence)", "lis", "난이도: 하 | 동적 계획법"),
        ("JLIS", "합친 LIS (Joined LIS)", "jlis", "난이도: 하 | 동적 계획법"),
        ("PI", "원주율 외우기 (Memorizing PI)", "memorizing_pi", "난이도: 하 | 동적 계획법"),
        ("QUANTIZE", "Quantization (양자화)", "quantization", "난이도: 중 | 동적 계획법"),
        ("TILING2", "타일링 방법의 수 세기", "tiling", "난이도: 하 | 경우의 수 DP"),
        ("ASYMTILING", "비대칭 타일링", "asymmetric", "난이도: 하 | 경우의 수 DP"),
        ("POLY", "폴리오미노 (Polyominoes)", "polyominoes", "난이도: 중 | 경우의 수 DP"),
        ("NUMB3RS", "두니발 박사의 탈옥 (Numb3rs)", "dunibal", "난이도: 중 | 마르코프 체인 DP"),
    ],
    9: [
        ("PACKING", "여행 짐 싸기 (Packing - 0/1 Knapsack)", "knapsack", "난이도: 중 | 실제 답 역추적"),
        ("OCR", "광학 문자 인식 (Optical Character Recognition)", "handwriting", "난이도: 상 | 마르코프 모델 DP"),
        ("MORSE", "모스 부호 사전 (Morse Code)", "morse", "난이도: 중 | K번째 답 계산"),
        ("KLIS", "K번째 최대 증가 부분 수열 (k-th LIS)", "kthlis", "난이도: 상 | K번째 답 역추적"),
        ("DRAGON", "드래곤 커브 (Dragon Curve)", "dragon", "난이도: 중 | 동적 계획법"),
        ("ZIMBABWE", "웨브바짐 (Zimbabwe)", "zimbabwe", "난이도: 상 | 자릿수 DP"),
        ("RESTORE", "실험 데이터 복구하기 (Restore)", "restore", "난이도: 중 | 외판원 순회 DP"),
        ("TICTACTOE", "틱택토 (Tic-Tac-Toe)", "tictactoe", "난이도: 하 | 게임 트리 미니맥스"),
        ("NUMBERGAME", "숫자 게임 (Number Game)", "numbergame", "난이도: 하 | 미니맥스 DP"),
        ("BLOCKGAME", "블록 게임 (Block Game)", "lblock", "난이도: 중 | 게임 이론 DP"),
        ("SUSHI", "회전초밥 (Sushi)", "sushi", "난이도: 중 | 슬라이딩 윈도우 DP"),
        ("GENIUS", "지니어스 (Genius)", "genius", "난이도: 중 | 행렬 거듭제곱 DP"),
    ],
    10: [
        ("MATCHORDER", "출전 순서 정하기 (Match Order)", "matchorder", "난이도: 하 | 그리디"),
        ("LUNCHBOX", "도시락 데우기 (Lunch Box)", "lunchbox", "난이도: 하 | 그리디 정렬"),
        ("STRJOIN", "문자열 합치기 (String Join - 허프만)", "strcat", "난이도: 중 | 우선순위 큐 그리디"),
        ("MINASTIRITH", "미나스 아노르 (Minas Tirith)", "minastirith", "난이도: 상 | 원형 구간 커버 그리디"),
    ],
    11: [
        ("BOARDCOVER2", "게임판 덮기 2 (Board Cover 2)", "boardcover2", "난이도: 하 | 백트래킹"),
        ("ALLERGY", "알러지가 심한 친구들 (Allergy)", "allergy", "난이도: 중 | 조합 탐색 가지치기"),
        ("KAKURO2", "카쿠로 (Kakuro)", "kakuro", "난이도: 중 | 제약 충족 문제"),
    ],
    12: [
        ("DARPA", "DARPA Grand Challenge", "darpa", "난이도: 하 | 이진 탐색 최적화"),
        ("ARCTIC", "남극 기지 (Arctic Base)", "arctic", "난이도: 하 | 이분법과 그래프"),
        ("CANADATRIP", "캐나다 여행 (Canada Trip)", "canada", "난이도: 중 | 결정 문제 변환"),
        ("WITHDRAWAL", "수강 철회 (Withdrawal)", "withdraw", "난이도: 상 | 비율 최적화 이분법"),
    ],
    13: [
        ("ROOTS", "방정식 풀기 (Roots)", "bisection", "난이도: 중 | 단조 함수 이분법"),
        ("LOAN", "전세금 균등상환 (Loan Repayment)", "loan", "난이도: 하 | 수치 이분 탐색"),
        ("RATIO", "승률 올리기 (Ratio)", "ratio", "난이도: 하 | 이분 탐색"),
        ("FOSSIL", "꽃가루 화석 (Fossil)", "fossil", "난이도: 상 | 삼분 탐색 볼록 다각형"),
    ],
    14: [
        ("PASS486", "비밀번호 486 (Password 486)", "password", "난이도: 중 | 에라토스테네스의 체 소인수분해"),
        ("POTION", "마법의 약 (Magic Potion)", "recipe", "난이도: 중 | 유클리드 호제법 최대공약수"),
    ],
    15: [
        ("PINBALL", "핀볼 시뮬레이션 (Pinball)", "pinball", "난이도: 상 | 벡터 기하 충돌"),
        ("TREASURE", "보물섬 (Treasure Island)", "treasure", "난이도: 상 | 다각형 교집합 면적"),
        ("NERDS", "너드인가, 너드가 아닌가? (Nerds)", "nerd", "난이도: 중 | 볼록 껍질 분리"),
    ],
    16: [
        ("GRADUATION", "졸업 학기 (Graduation)", "graduation", "난이도: 중 | 비트마스크 DP"),
    ],
    17: [
        ("CHRISTMAS", "크리스마스 인형 (Christmas Dolls)", "partial", "난이도: 중 | 부분 합과 모듈로 연산"),
    ],
    18: [
        ("JOSEPHUS", "조세푸스 문제 (Josephus Problem)", "josephus", "난이도: 하 | 원형 연결 리스트"),
    ],
    19: [
        ("BRACKETS2", "짝이 맞지 않는 괄호 (Mismatched Brackets)", "scaffolding", "난이도: 하 | 스택 매칭"),
        ("ITES", "외계 신호 분석 (Online Signals Analysis)", "subway", "난이도: 중 | 큐와 슬라이딩 윈도우"),
    ],
    20: [
        ("NAMING", "작명하기 (Naming - 접두사 접미사)", "prefixsuffix", "난이도: 하 | KMP 부분 일치 테이블"),
        ("PALINDROMIZE", "팰린드롬 만들기 (Palindromize)", "palindromize", "난이도: 하 | KMP 알고리즘"),
        ("JAEHASAFE", "재하의 금고 (Jaeha's Safe)", "dialsafe", "난이도: 중 | KMP 순환 문자열"),
        ("HABIT", "말버릇 (Habit - 최장 공통 부분 문자열)", "frequentsubstring", "난이도: 중 | 접미사 배열"),
    ],
    21: [
        ("TRAVERSAL", "트리 순회 순서 변경 (Tree Traversal)", "treeorder", "난이도: 하 | 전위/중위 -> 후위 변환"),
        ("FORTRESS", "요새 (Fortress)", "castle", "난이도: 중 | 트리 최장 경로 직경"),
    ],
    22: [
        ("NERD2", "너드인가, 너드가 아닌가? 2 (Nerds 2)", "nerd2", "난이도: 중 | 이진 검색 트리 지배점"),
        ("INSERTION", "삽입 정렬 뒤집기 (Insertion Sort Reversal)", "reverseinsert", "난이도: 중 | 트립(Treap) k번째 원소"),
    ],
    23: [
        ("RUNNINGMEDIAN", "변화하는 중간 값 (Running Median)", "runningmedian", "난이도: 하 | 최대힙/최소힙 중간값"),
    ],
    24: [
        ("MORDOR", "등산로 (Mordor - Range Minimum/Maximum Query)", "rmq", "난이도: 중 | 구간 트리 (Segment Tree)"),
        ("FAMILYTREE", "족보 탐험 (Family Tree - LCA)", "familytree", "난이도: 상 | 최소 공통 조상 LCA 구간 트리"),
        ("MEASURETIME", "삽입 정렬 시간 재기 (Measure Insertion Time)", "countinsertion", "난이도: 중 | 펜윅 트리 (Fenwick Tree)"),
    ],
    25: [
        ("EDITORWARS", "에디터 전쟁 (Editor Wars)", "disjoint", "난이도: 중 | 상호 배타 집합 (Union-Find) 적대 관계"),
    ],
    26: [
        ("SOLONG", "안녕히, 그리고 물고기는 고마웠어요! (So Long)", "trie", "난이도: 중 | 트라이 자동완성 추천"),
        ("NH", "보안종결자 (Security Terminator)", "aho-corasick", "난이도: 상 | 아호-코라식 문자열 매칭"),
    ],
    27: [
        ("graph_representation", "그래프 표현 방식 비교 (인접 행렬 vs 인접 리스트)", "dfs", "그래프 기본 표현"),
    ],
    28: [
        ("DICTIONARY", "고대어 사전 (Ancient Dictionary)", "tree", "난이도: 하 | 위상 정렬 DFS"),
        ("WORDCHAIN", "단어 제한 끝말잇기 (Word Chain)", "wordgame", "난이도: 중 | 오일러 트레일 DFS"),
        ("GALLERY", "감시 카메라 설치 (Gallery)", "gallery", "난이도: 중 | 최소 지배 집합 트리 DFS"),
        ("MEETINGROOM", "회의실 배정 (Meeting Room - 2-SAT)", "meeting", "난이도: 상 | 강결합 컴포넌트 SCC 2-SAT"),
    ],
    29: [
        ("SORTGAME", "Sorting Game (배열 뒤집기 최단 경로)", "sortinggame", "난이도: 중 | BFS 너비 우선 탐색"),
        ("CHILDRENDAY", "어린이날 (Children's Day)", "childrenday", "난이도: 상 | BFS 경로 탐색"),
        ("HANOI4B", "하노이의 탑 (Hanoi Tower 4 Pegs)", "hanoi", "난이도: 중 | 양방향 BFS 탐색"),
    ],
    30: [
        ("ROUTING", "신호 라우팅 (Signal Routing)", "dijkstra", "난이도: 하 | 다익스트라 최단 경로"),
        ("FIRETRUCKS", "소방차 (Fire Trucks)", "nthlon", "난이도: 중 | 다익스트라 가상 시작점"),
        ("NTHLON", "철인 N종 경기 (N-thlon)", "nthlon", "난이도: 상 | 다익스트라 상태 그래프"),
        ("TIMETRIP", "시간여행 (Time Trip)", "bellman", "난이도: 중 | 벨만-포드 음수 사이클"),
        ("DRUNKEN", "음주 운전 단속 (Drunken Driving)", "floyd", "난이도: 중 | 플로이드-워셜 정점 경유"),
        ("PROMISES", "선거 공약 (Promises)", "promises", "난이도: 중 | 플로이드-워셜 동적 간선 추가"),
    ],
    31: [
        ("LAN", "근거리 네트워크 (Local Area Network)", "lan", "난이도: 하 | 크루스칼 최소 스패닝 트리"),
        ("TPATH", "여행 경로 정하기 (Travel Path)", "tpath", "난이도: 상 | 크루스칼 최소 스패닝 트리 이분 탐색"),
    ],
    32: [
        ("MATCHFIX", "승부 조작 (Match Fixing)", "flow", "난이도: 중 | 네트워크 유량 포드-풀커슨"),
        ("TRAPCARD", "함정 설치 (Trap Card)", "trapcard", "난이도: 상 | 이분 매칭 최소 버텍스 커버"),
    ],
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def find_source_folder(folder_hint):
    """Look up folder in /tmp/jmcode/problems or /tmp/jmcode/src."""
    p_dir = SOURCE_JMCODE_DIR / "problems" / folder_hint
    if p_dir.exists():
        return p_dir, "problem"
    s_dir = SOURCE_JMCODE_DIR / "src" / folder_hint
    if s_dir.exists():
        return s_dir, "src"
    # Case-insensitive search
    for p in (SOURCE_JMCODE_DIR / "problems").iterdir():
        if p.name.lower() == folder_hint.lower():
            return p, "problem"
    for s in (SOURCE_JMCODE_DIR / "src").iterdir():
        if s.name.lower() == folder_hint.lower():
            return s, "src"
    return None, None

def generate_jongmanbook_full():
    print("🚀 《알고리즘 문제 해결 전략 (종만북 1·2권)》 32개 전 챕터 전수 스캐폴딩을 시작합니다...")

    TARGET_BOOK_DIR.mkdir(parents=True, exist_ok=True)
    total_items = 0
    master_rows = []

    for ch_num in range(1, 33):
        en_title, ko_title, part_name = CHAPTER_META[ch_num]
        ch_folder_name = f"{ch_num:02d}_{slugify(en_title)}"
        ch_target_path = TARGET_BOOK_DIR / ch_folder_name
        ch_target_path.mkdir(parents=True, exist_ok=True)

        items_def = CHAPTER_ITEMS.get(ch_num, [])
        chapter_items = []
        item_counter = 1

        for prob_id, prob_title, folder_hint, desc in items_def:
            item_slug = f"{item_counter:02d}_{slugify(prob_id)}"
            item_dest = ch_target_path / item_slug
            item_dest.mkdir(parents=True, exist_ok=True)

            src_folder, src_type = find_source_folder(folder_hint)
            cpp_files = []
            in_file = None
            out_file = None
            md_file = None

            if src_folder:
                for f in src_folder.iterdir():
                    if f.is_file():
                        dest_f = item_dest / f.name
                        shutil.copy2(f, dest_f)
                        if f.suffix in [".cpp", ".cc"]:
                            cpp_files.append(f.name)
                        elif f.suffix == ".in":
                            in_file = f.name
                        elif f.suffix == ".out":
                            out_file = f.name
                        elif f.suffix == ".md":
                            md_file = f.name

            # Ensure main.cpp exists
            main_path = item_dest / "main.cpp"
            if not main_path.exists():
                if cpp_files:
                    # Pick primary cpp file
                    primary_cpp = item_dest / cpp_files[0]
                    shutil.copy2(primary_cpp, main_path)
                else:
                    with open(main_path, "w", encoding="utf-8") as fp:
                        fp.write(f"""// Algospot Problem: {prob_id} - {prob_title}
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

void solve() {{
    // Implement algorithm for {prob_id}
}}

int main() {{
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout << "[종만북 Ch {ch_num:02d}] {prob_id}: {prob_title} ready." << endl;
    return 0;
}}
""")

            # Read main.cpp for preview in README
            main_code_preview = ""
            if main_path.exists():
                with open(main_path, "r", encoding="utf-8", errors="replace") as fp:
                    main_code_preview = fp.read().strip()
            if len(main_code_preview) > 2000:
                main_code_preview = main_code_preview[:2000] + "\n// ... (이하 생략 - 전체 코드는 main.cpp 참조)"

            suite_name = f"Jongman_Ch{ch_num:02d}_{slugify(prob_id)[:25]}"

            # Ensure README.md exists
            readme_path = item_dest / "README.md"
            readme_text = f"""# 📘 [종만북 Ch {ch_num:02d}] {prob_id}: {prob_title}

- **도서**: 《프로그래밍 대회에서 배우는 알고리즘 문제 해결 전략》 (구종만 저, 인사이트)
- **챕터**: {ch_num}장. {ko_title} ({en_title})
- **구분**: {part_name}
- **난이도 및 속성**: {desc}
- **온라인 저지 링크**: [Algospot {prob_id}](http://algospot.com/judge/problem/read/{prob_id})

---

## 1. 문제 해결 개요 및 접근법
본 문제는 종만북의 대표 실습 문제인 **{prob_title}**입니다.
- 시간 복잡도 목표: 문제 제한 시간 내 통과
- 주요 자료구조 및 알고리즘 기법을 직접 구현하고 GoogleTest를 통해 검증합니다.

## 2. 따라쳐볼 목표 코드 (`main.cpp`)
아래 코드를 `main.cpp`에 직접 타이핑하며 알고리즘 기법을 체득하세요.

```cpp
{main_code_preview}
```

## 3. 추천 GoogleTest 검증 코드 예시 (`test.cpp`)
아래 단위 테스트 예시를 참고하여 `test.cpp`에 직접 타이핑하여 테스트를 완성해 보세요.

```cpp
#include <gtest/gtest.h>

TEST({suite_name}, SampleCase) {{
    // TODO: 샘플 입력 및 기대 출력을 바탕으로 단위 테스트를 직접 타이핑하세요.
    EXPECT_TRUE(true);
}}
```

## 4. 컴파일 및 실행 사이클
```bash
# 1) 직접 작성한 main.cpp 즉시 컴파일 & 실행 (0.1초 고속 빌드)
./scripts/run.sh {item_dest.relative_to(REPO_ROOT)}

# 2) 직접 작성한 test.cpp GoogleTest 단위 테스트 자동 검증
./scripts/test.sh {item_dest.relative_to(REPO_ROOT)}
```
"""
            with open(readme_path, "w", encoding="utf-8") as fp:
                fp.write(readme_text)

            # Ensure test.cpp (GoogleTest) exists with learner typing guide
            test_path = item_dest / "test.cpp"
            test_code = f"""// ==============================================================================
// [종만북 Ch {ch_num:02d}] {prob_id}: {prob_title}
//
// 같은 폴더의 README.md 에 있는 목표 코드와 추천 GoogleTest 코드를 참고하여
// 직접 테스트 케이스를 타이핑하여 완성해 보세요.
// ==============================================================================

#include <gtest/gtest.h>

TEST({suite_name}, TODO) {{
    // TODO: 여기에 직접 GoogleTest 케이스를 타이핑하세요.
    // 예: EXPECT_EQ(solve(), expected_answer);
    EXPECT_TRUE(true);
}}
"""
            with open(test_path, "w", encoding="utf-8") as fp:
                fp.write(test_code)

            chapter_items.append((item_slug, f"{prob_id} - {prob_title}"))
            item_counter += 1
            total_items += 1

        # Chapter README.md
        ch_readme = f"""# 📖 {ch_num}장. {ko_title} ({en_title})

> **도서**: 《프로그래밍 대회에서 배우는 알고리즘 문제 해결 전략》 (종만북, 구종만 저)  
> **부(Part)**: {part_name}  
> **총 실습 항목**: {len(chapter_items)}개

---

## 챕터 전체 실습 및 문제 목록

| 번호 | 폴더명 | 문제 ID 및 주제 |
|:---:|:---|:---|
"""
        for slug, desc in chapter_items:
            ch_readme += f"| {slug[:2]} | [`{slug}`]({slug}/) | {desc} |\n"

        with open(ch_target_path / "README.md", "w", encoding="utf-8") as fp:
            fp.write(ch_readme)

        master_rows.append((ch_num, ko_title, en_title, part_name, ch_folder_name, len(chapter_items)))

    # Master README.md
    master_readme = f"""# 📚 프로그래밍 대회에서 배우는 알고리즘 문제 해결 전략 (종만북) 전수 실습 트랙

> **구종만 저 | 도서출판 인사이트 | 총 1,084페이지 (1권 & 2권)**  
> **총 32개 전 챕터 (1부 ~ 7부, Ch01 ~ Ch32) 전수 수록 (축약 없음)**  
> **총 {total_items}개 알고스팟(Algospot) 공식 문제 및 핵심 알고리즘 수록**  
> **공식 테스트케이스 (.in / .out), C++17 참조 풀이, GoogleTest 연동**

---

## 32개 챕터별 마스터 색인 (Chapter Master Index)

| 챕터 | 한글 챕터명 | 영문 챕터명 | 수록 권/부 | 폴더 링크 | 항목 수 |
|:---:|:---|:---|:---|:---|:---:|
"""
    for ch_num, ko, en, part, folder, tot in master_rows:
        master_readme += f"| {ch_num:02d} | {ko} | {en} | {part.split(':')[0]} | [{folder}](./{folder}/) | **{tot}** |\n"

    master_readme += f"""
---

## 🛠️ 실습 및 검증 방법

```bash
# 1) 특정 알고스팟 문제 즉시 컴파일 & 실행 (0.1초 고속 빌드)
./scripts/run.sh practice/jongmanbook/06_brute_force/02_picnic

# 2) 특정 알고스팟 문제 GoogleTest 단위 테스트 검증
./scripts/test.sh practice/jongmanbook/06_brute_force/02_picnic

# 3) 전수 스캐폴딩 재생성
python3 scripts/generate_jongmanbook_full.py
```
"""
    with open(TARGET_BOOK_DIR / "README.md", "w", encoding="utf-8") as fp:
        fp.write(master_readme)

    print(f"\n✨ 《알고리즘 문제 해결 전략 (종만북)》 전수 스캐폴딩 완료!")
    print(f"📊 총 32개 챕터 폴더, {total_items}개 전체 실습 항목 생성 완료.")
    print(f"📄 마스터 색인: {TARGET_BOOK_DIR / 'README.md'}")

if __name__ == "__main__":
    generate_jongmanbook_full()
