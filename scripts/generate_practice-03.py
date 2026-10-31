#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_알고리즘 문제해설.pdf 의 주차별 추천문제 목록을 풀이 연습용 디렉토리로 생성한다.
PDF 자체에는 문제 지문/입출력 예시가 없고 문제번호와 해설코드 링크만 있으므로,
각 main.cpp 스텁에는 문제번호(acmicpc.net 참고링크 포함)만 적어두고 문제 지문/예제 입출력은
그 링크에서 직접 확인한 뒤 손으로 풀이를 타이핑하는 방식이다.
(교안에 따르면 원 채점 사이트는 서비스가 종료되었으므로, 정답 검증은 사이트 제출이 아니라
직접 작성하는 test.cpp 의 GoogleTest 로 한다.)
각 항목마다 main.cpp(풀이용) 와 test.cpp(GoogleTest 작성용)를 만든다.
이미 존재하는 main.cpp/test.cpp 는 건드리지 않는다 (사용자가 작성한 내용 보존).
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "practice", "stone-lecture", "03_실전_문제풀이")

# (주차 디렉토리, 주차 제목, [(레이블, 문제번호, 참고메모 또는 None), ...])
WEEKS = [
    ("01_1주차_문자열_누적합_구현", "1주차 문자열, 누적합, 구현", [
        ("A", "2309", None),
        ("B", "10808", None),
        ("C", "2979", None),
        ("D", "10988", None),
        ("E", "1159", None),
        ("F", "11655", None),
        ("G", "9996", None),
        ("H", "2559", None),
        ("I", "1620", None),
        ("J", "9375", None),
        ("K", "1213", None),
        ("L", "1940", None),
        ("M", "3986", None),
        ("N", "1629", None),
        ("O", "4375", None),
    ]),
    ("02_2주차_그래프이론_DFS_BFS", "2주차 그래프이론, DFS, BFS", [
        ("A", "2178", None),
        ("B", "1012", None),
        ("C", "2468", None),
        ("D", "2583", None),
        ("E", "1992", None),
        ("F", "2828", None),
        ("G", "2910", None),
        ("H", "4659", None),
        ("I", "2870", None),
        ("J", "10709", None),
        ("K", "3474", "n이하의 5의 개수는 2의 개수보다 항상 작다는 점을 활용"),
        ("L", "2852", None),
        ("M", "1436", None),
        ("N", "9012", None),
        ("O", "4949", None),
        ("P", "14502", None),
        ("Q", "2636", None),
        ("R", "1068", None),
        ("S", "1325", None),
        ("T", "17298", None),
    ]),
    ("03_3주차_완전탐색_백트래킹", "3주차 완전탐색, 백트래킹", [
        ("A", "15686", None),
        ("B", "2589", None),
        ("C", "16234", None),
        ("D", "4179", None),
        ("E", "12869", None),
        ("F", "16637", None),
        ("G", "12851", None),
        ("H", "13913", None),
        ("I", "17071", None),
        ("J", "14497", None),
        ("K", "3197", None),
        ("L", "1987", None),
        ("M", "2529", None),
        ("N", "9934", None),
        ("O", "15684", None),
        ("P", "14620", None),
        ("Q", "1189", None),
    ]),
    ("04_4주차_비트마스킹", "4주차 비트마스킹", [
        ("A", "19942", None),
        ("B", "1285", None),
        ("C", "17471", None),
        ("D", "1987", None),
        ("E", "14890", None),
        ("F", "1062", None),
        ("G", "1094", None),
        ("H", "2234", None),
        ("I", "11723", None),
        ("J", "14391", None),
        ("K", "13244", None),
        ("L", "5430", None),
        ("M", "14405", None),
        ("N", "15353", None),
        ("O", "15926", None),
        ("P", "3015", None),
    ]),
    ("05_5주차_그리디_라인스위핑_투포인터", "5주차 그리디, 라인스위핑, 투포인터", [
        ("A", "2109", None),
        ("B", "9935", None),
        ("C", "1781", None),
        ("D", "14469", None),
        ("E", "1931", None),
        ("F", "1202", None),
        ("G", "1644", None),
        ("H", "13144", None),
        ("I", "3273", None),
        ("J", "1700", None),
        ("K", "17144", None),
        ("L", "14889", None),
        ("M", "12100", "struct를 이용하지 않은 풀이도 가능"),
        ("N", "3190", None),
        ("O", "17406", None),
        ("P", "15662", "비트마스킹을 이용한 풀이도 가능"),
        ("Q", "1911", None),
        ("R", "17825", None),
        ("S", "14888", None),
        ("T", "17143", None),
        ("U", "15685", None),
        ("V", "2632", None),
        ("W", "1912", None),
        ("X", "15683", None),
        ("Y", "17822", None),
        ("Z", "2170", None),
    ]),
    ("06_6주차_이분탐색과_LIS", "6주차 이분탐색과 LIS", [
        ("A", "2792", None),
        ("B", "2343", None),
        ("C", "6236", None),
        ("D", "7795", None),
        ("E", "1269", None),
        ("F", "16434", None),
        ("G", "1072", None),
        ("H", "2776", None),
        ("I", "14627", None),
        ("J", "1561", None),
        ("K", "14003", None),
        ("L", "2670", None),
        ("M", "11053", None),
        ("N", "14002", None),
        ("O", "2565", None),
    ]),
    ("07_7주차_DP", "7주차 DP", [
        ("A", "2098", None),
        ("B", "17070", None),
        ("C", "1103", None),
        ("D", "2240", None),
        ("E", "4811", None),
        ("F", "12852", None),
        ("G", "2294", None),
        ("H", "2293", None),
        ("I", "4781", None),
        ("J", "12865", "재귀함수를 이용한 풀이도 가능"),
        ("K", "1513", None),
        ("L", "1535", None),
        ("M", "16235", None),
        ("N", "17136", None),
        ("O", "17837", None),
        ("P", "14867", None),
        ("Q", "1344", None),
        ("R", "10942", None),
        ("S", "1509", None),
        ("T", "5557", None),
        ("U", "1450", None),
        ("V", "14863", "반복문 DP를 이용한 풀이도 가능"),
        ("W", "2342", None),
        ("X", "1480", None),
        ("Y", "3687", None),
    ]),
    ("08_8주차_펜윅트리_최단거리", "8주차 펜윅트리, 최단거리", [
        ("A", "2618", None),
        ("B", "1315", None),
        ("C", "17258", None),
        ("D", "5419", None),
        ("E", "2302", None),
        ("F", "1514", None),
        ("G", "17623", None),
        ("H", "17297", None),
        ("I", "1280", None),
        ("J", "3653", None),
        ("K", "2042", None),
        ("L", "11658", None),
        ("M", "1486", None),
        ("N", "5719", None),
        ("O", "16118", None),
        ("P", "1219", None),
        ("Q", "1613", None),
        ("R", "1238", None),
        ("S", "9370", None),
        ("T", "17612", None),
        ("U", "4485", None),
        ("V", "5373", None),
        ("W", "14864", None),
        ("X", "15972", None),
        ("Y", "17616", None),
        ("Z", "17611", None),
    ]),
]


def make_stub(week_title: str, label: str, boj_num: str, note: str) -> str:
    note_line = f"\n// 참고: {note}" if note else ""
    return f"""// {week_title} - {label}
// 문제번호 {boj_num} (참고링크: https://www.acmicpc.net/problem/{boj_num})
// 문제 지문과 예제 입출력은 위 링크에서 확인한 뒤, 아래에 직접 풀이를 작성해보세요.{note_line}
// 실행 테스트: ./scripts/run.sh practice-03/{{주차폴더}}/{{이 폴더}} 로 컴파일 후
//              문제의 예제 입력값을 직접 타이핑해서 결과를 눈으로 비교하세요.
// 정답 검증: test.cpp 에 GoogleTest 로 예제 입출력 기반 테스트를 직접 작성하세요.

#include <bits/stdc++.h>
using namespace std;

int main() {{

    return 0;
}}
"""


def sanitize_test_name(slug: str) -> str:
    name = re.sub(r"[^0-9A-Za-z_]", "_", slug)
    if not name or name[0].isdigit():
        name = "T_" + name
    return name


def make_test_stub(week_title: str, label: str, boj_num: str, note: str) -> str:
    suite = sanitize_test_name(f"{label}_{boj_num}")
    note_line = f"\n// 참고: {note}" if note else ""
    return f"""// {week_title} - {label}
// 문제번호 {boj_num} (참고링크: https://www.acmicpc.net/problem/{boj_num}){note_line}
//
// 여기에 GoogleTest 테스트를 직접 작성하세요.
// 문제 페이지의 예제 입력/출력을 기반으로 테스트 케이스를 만드세요.
// main.cpp 는 자체 main() 을 갖고 있어 그대로 include 하면 충돌하니,
// 검증하고 싶은 로직은 함수로 분리해서 여기서 다시 선언/정의하거나
// 이 파일에서 필요한 로직만 옮겨와 테스트하세요.

#include <gtest/gtest.h>

TEST({suite}, TODO) {{
    // TODO: 문제의 예제 입출력을 기반으로 테스트 케이스를 작성하세요.
}}
"""


def main():
    created = 0
    skipped = 0
    test_created = 0
    test_skipped = 0
    for week_dir, week_title, items in WEEKS:
        week_path = os.path.join(ROOT, week_dir)
        os.makedirs(week_path, exist_ok=True)

        index_lines = [f"# {week_title}", ""]
        for i, (label, boj_num, note) in enumerate(items, start=1):
            item_dir = f"{i:02d}_{label}_{boj_num}"
            item_path = os.path.join(week_path, item_dir)
            os.makedirs(item_path, exist_ok=True)
            main_cpp = os.path.join(item_path, "main.cpp")
            if os.path.exists(main_cpp):
                skipped += 1
            else:
                with open(main_cpp, "w", encoding="utf-8") as f:
                    f.write(make_stub(week_title, label, boj_num, note))
                created += 1

            test_cpp = os.path.join(item_path, "test.cpp")
            if os.path.exists(test_cpp):
                test_skipped += 1
            else:
                with open(test_cpp, "w", encoding="utf-8") as f:
                    f.write(make_test_stub(week_title, label, boj_num, note))
                test_created += 1

            note_suffix = f" ({note})" if note else ""
            index_lines.append(
                f"- `{item_dir}/main.cpp` — 문제번호 {boj_num}: "
                f"https://www.acmicpc.net/problem/{boj_num}{note_suffix}"
            )

        with open(os.path.join(week_path, "README.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines) + "\n")

    print(f"main.cpp created: {created}, skipped: {skipped}")
    print(f"test.cpp created: {test_created}, skipped: {test_skipped}")


if __name__ == "__main__":
    main()
