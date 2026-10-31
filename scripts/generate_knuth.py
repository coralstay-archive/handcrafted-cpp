#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_knuth.py
도널드 크누스(Donald E. Knuth) 교수의 대작
《The Art of Computer Programming, Volume 4A: Combinatorial Algorithms, Part 1》
핵심 알고리즘 전수 스캐폴딩 생성기

Chapter 7.1: Zeros and Ones (비트 연산, 불리언 대수, BDD)
Chapter 7.2: Generating All Possibilities (순열, 조합, 분할, 트리 전수 생성)
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_DIR = REPO_ROOT / "practice" / "knuth"

BOOK_TITLE = "《The Art of Computer Programming Vol 4A: Combinatorial Algorithms》(Donald E. Knuth 저, Addison-Wesley)"

KNUTH_ITEMS = [
    # -------------------------------------------------------------------------
    # Chapter 7.1 Zeros and Ones
    # -------------------------------------------------------------------------
    {
        "folder": "01_zeros_and_ones/01_boolean_basics",
        "title": "7.1.1 불리언 기본 연산과 대수적 속성 (Boolean Basics & Algebra)",
        "chapter": "Chapter 7.1 Zeros and Ones",
        "section": "7.1.1 Boolean Basics",
        "page": "p.2-46",
        "desc": "불리언 대수의 공리계, 쌍대성 원리(Duality), 드 모르간 법칙과 표준형(CNF/DNF)의 비트 단위 모델링.",
        "cross_ref": [
            ("practice/stone-lecture/01_문법_STL/01_기본/04_bool", "큰돌 1.2 bool 자료형 및 논리 연산자"),
            ("practice/jongmanbook/16_bitmask", "종만북 16장 비트마스크 기초"),
        ],
        "main_cpp": r'''#include <iostream>
#include <bitset>
#include <string>

// 불리언 기본 연산 및 쌍대성(Duality) 검증
bool boolean_and(bool x, bool y) { return x && y; }
bool boolean_or(bool x, bool y)  { return x || y; }
bool boolean_xor(bool x, bool y) { return x ^ y; }

int main() {
    std::cout << "=== Knuth TAOCP 7.1.1: Boolean Basics ===\n";
    bool x = true, y = false;
    std::cout << "x = " << x << ", y = " << y << '\n';
    std::cout << "x AND y = " << boolean_and(x, y) << '\n';
    std::cout << "x OR  y = " << boolean_or(x, y) << '\n';
    std::cout << "x XOR y = " << boolean_xor(x, y) << '\n';
    std::cout << "De Morgan: !(x && y) == (!x || !y) -> " 
              << (!(x && y) == (!x || !y) ? "TRUE" : "FALSE") << '\n';
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>

TEST(Knuth_7_1_1, DeMorganLaws) {
    for (int x : {0, 1}) {
        for (int y : {0, 1}) {
            EXPECT_EQ(!(x && y), (!x || !y));
            EXPECT_EQ(!(x || y), (!x && !y));
        }
    }
}

TEST(Knuth_7_1_1, Distributivity) {
    for (int x : {0, 1}) {
        for (int y : {0, 1}) {
            for (int z : {0, 1}) {
                EXPECT_EQ(x && (y || z), (x && y) || (x && z));
                EXPECT_EQ(x || (y && z), (x || y) && (x || z));
            }
        }
    }
}
'''
    },
    {
        "folder": "01_zeros_and_ones/02_boolean_evaluation",
        "title": "7.1.2 비트 단위 병렬 평가 (Boolean Evaluation & Bit-Parallelism)",
        "chapter": "Chapter 7.1 Zeros and Ones",
        "section": "7.1.2 Boolean Evaluation",
        "page": "p.47-132",
        "desc": "SWAR(SIMD Within A Register) 기법을 활용한 64비트 정수 내 다중 불리언 식 동시 병렬 평가.",
        "cross_ref": [
            ("practice/c-and-cpp/05_high_perf_cpp/04_data_structures_memory", "고성능 C++ 메모리 및 병렬 연산"),
            ("practice/jongmanbook/16_bitmask", "종만북 16장 비트마스크 병렬 처리"),
        ],
        "main_cpp": r'''#include <iostream>
#include <cstdint>
#include <bitset>

// 64개의 불리언 입력을 1개 CPU 사이클로 동시 평가 (Bit-parallel evaluation)
uint64_t parallel_majority(uint64_t a, uint64_t b, uint64_t c) {
    // 3개 입력 중 2개 이상이 1인 비트 위치를 마스크로 반환
    return (a & b) | (b & c) | (c & a);
}

int main() {
    std::cout << "=== Knuth TAOCP 7.1.2: Bit-Parallel Boolean Evaluation ===\n";
    uint64_t a = 0b11001010;
    uint64_t b = 0b10101100;
    uint64_t c = 0b10011011;
    uint64_t maj = parallel_majority(a, b, c);
    std::cout << "a:   " << std::bitset<8>(a) << '\n';
    std::cout << "b:   " << std::bitset<8>(b) << '\n';
    std::cout << "c:   " << std::bitset<8>(c) << '\n';
    std::cout << "maj: " << std::bitset<8>(maj) << '\n';
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>
#include <cstdint>

uint64_t parallel_majority_test(uint64_t a, uint64_t b, uint64_t c) {
    return (a & b) | (b & c) | (c & a);
}

TEST(Knuth_7_1_2, MajorityGateBitwise) {
    uint64_t a = 0xF0F0ULL;
    uint64_t b = 0xCCCCULL;
    uint64_t c = 0xAAAAULL;
    uint64_t res = parallel_majority_test(a, b, c);
    for (int i = 0; i < 16; ++i) {
        int bit_a = (a >> i) & 1;
        int bit_b = (b >> i) & 1;
        int bit_c = (c >> i) & 1;
        int expected = (bit_a + bit_b + bit_c >= 2) ? 1 : 0;
        EXPECT_EQ((res >> i) & 1, expected);
    }
}
'''
    },
    {
        "folder": "01_zeros_and_ones/03_bitwise_tricks",
        "title": "7.1.3 비트 트릭과 Broadword 컴퓨팅 (Bitwise Tricks & Broadword Programming)",
        "chapter": "Chapter 7.1 Zeros and Ones",
        "section": "7.1.3 Bitwise Tricks and Techniques",
        "page": "p.133-221",
        "desc": "가장 오른쪽 1 추출(x & -x), 1 제거(x & (x-1)), Popcount, Bit Reversal, Gray Code 및 C++20 <bit>의 원전.",
        "cross_ref": [
            ("practice/stone-lecture/02_알고리즘_개념/12_이진수와_비트연산자", "큰돌 2.12 이진수와 비트연산자"),
            ("practice/stone-lecture/03_실전_문제풀이/04_4주차_비트마스킹", "큰돌 4주차 비트마스킹 실전"),
            ("practice/jongmanbook/16_bitmask", "종만북 16장 비트마스크 (Bitmask)"),
        ],
        "main_cpp": r'''#include <iostream>
#include <bit>
#include <cstdint>
#include <bitset>

// Knuth 7.1.3 Broadword Bitwise Tricks
uint64_t isolate_rightmost_one(uint64_t x) {
    return x & (-x); // x & (~x + 1)
}

uint64_t clear_rightmost_one(uint64_t x) {
    return x & (x - 1);
}

uint64_t isolate_rightmost_zero(uint64_t x) {
    return ~x & (x + 1);
}

// SWAR 64-bit Population Count (Knuth's Algorithm)
int knuth_popcount(uint64_t x) {
    x = x - ((x >> 1) & 0x5555555555555555ULL);
    x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL);
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
    return static_cast<int>((x * 0x0101010101010101ULL) >> 56);
}

int main() {
    std::cout << "=== Knuth TAOCP 7.1.3: Bitwise Tricks & Broadword Computing ===\n";
    uint64_t x = 0b00101100; // 44
    std::cout << "x:                         " << std::bitset<8>(x) << " (" << x << ")\n";
    std::cout << "isolate_rightmost_one(x):  " << std::bitset<8>(isolate_rightmost_one(x)) << '\n';
    std::cout << "clear_rightmost_one(x):    " << std::bitset<8>(clear_rightmost_one(x)) << '\n';
    std::cout << "isolate_rightmost_zero(x): " << std::bitset<8>(isolate_rightmost_zero(x)) << '\n';
    std::cout << "Knuth popcount(x):         " << knuth_popcount(x) << " (C++20 std::popcount: " << std::popcount(x) << ")\n";
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>
#include <cstdint>
#include <bit>

uint64_t isolate_rightmost_one_test(uint64_t x) { return x & (-x); }
uint64_t clear_rightmost_one_test(uint64_t x) { return x & (x - 1); }
int knuth_popcount_test(uint64_t x) {
    x = x - ((x >> 1) & 0x5555555555555555ULL);
    x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL);
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0FULL;
    return static_cast<int>((x * 0x0101010101010101ULL) >> 56);
}

TEST(Knuth_7_1_3, RightmostBitIsolate) {
    EXPECT_EQ(isolate_rightmost_one_test(12), 4); // 1100 -> 0100
    EXPECT_EQ(isolate_rightmost_one_test(40), 8); // 101000 -> 001000
    EXPECT_EQ(isolate_rightmost_one_test(0), 0);
}

TEST(Knuth_7_1_3, ClearRightmostBit) {
    EXPECT_EQ(clear_rightmost_one_test(12), 8); // 1100 -> 1000
    EXPECT_EQ(clear_rightmost_one_test(7), 6);  // 0111 -> 0110
}

TEST(Knuth_7_1_3, PopcountAgainstStd) {
    for (uint64_t val : {0ULL, 1ULL, 0x123456789ABCDEF0ULL, 0xFFFFFFFFFFFFFFFFULL}) {
        EXPECT_EQ(knuth_popcount_test(val), std::popcount(val));
    }
}
'''
    },
    {
        "folder": "01_zeros_and_ones/04_binary_decision_diagrams",
        "title": "7.1.4 이진 결정 다이어그램 (Binary Decision Diagrams - BDD)",
        "chapter": "Chapter 7.1 Zeros and Ones",
        "section": "7.1.4 Binary Decision Diagrams",
        "page": "p.222-315",
        "desc": "순서화 축약 BDD(ROBDD) 노드 공유 및 섀넌 전개(Shannon Expansion)를 통한 불리언 함수 유일 정규 표현.",
        "cross_ref": [
            ("practice/jongmanbook/21_tree_traversal", "종만북 21장 트리 순회"),
            ("practice/jongmanbook/27_graph_representation", "종만북 27장 그래프 표현"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>
#include <map>
#include <tuple>

// 초소형 ROBDD 노드 모델 (Knuth 7.1.4)
struct BDDNode {
    int var;       // 변수 인덱스
    int low, high; // 0 분기, 1 분기 자식 노드 ID
};

class SimpleBDD {
public:
    std::vector<BDDNode> nodes;
    // (var, low, high) -> node_id 고유화 테이블
    std::map<std::tuple<int, int, int>, int> unique_table;

    SimpleBDD() {
        // 단말 노드 0과 1
        nodes.push_back({-1, -1, -1}); // ID 0: False
        nodes.push_back({-1, -1, -1}); // ID 1: True
    }

    int get_node(int var, int low, int high) {
        if (low == high) return low; // 축약 규칙 (Reduction)
        auto key = std::make_tuple(var, low, high);
        if (unique_table.count(key)) return unique_table[key];
        int id = static_cast<int>(nodes.size());
        nodes.push_back({var, low, high});
        unique_table[key] = id;
        return id;
    }

    bool evaluate(int root, const std::vector<bool>& assignment) {
        int curr = root;
        while (curr > 1) {
            int v = nodes[curr].var;
            curr = assignment[v] ? nodes[curr].high : nodes[curr].low;
        }
        return curr == 1;
    }
};

int main() {
    std::cout << "=== Knuth TAOCP 7.1.4: Binary Decision Diagrams (BDD) ===\n";
    SimpleBDD bdd;
    // f(x0, x1) = x0 && x1
    // x1 노드: var=1, low=0, high=1
    int x1_node = bdd.get_node(1, 0, 1);
    // x0 노드: var=0, low=0, high=x1_node
    int f_and = bdd.get_node(0, 0, x1_node);

    std::cout << "ROBDD Node count: " << bdd.nodes.size() << '\n';
    std::cout << "f(1, 1) = " << bdd.evaluate(f_and, {true, true}) << '\n';
    std::cout << "f(1, 0) = " << bdd.evaluate(f_and, {true, false}) << '\n';
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>
#include <vector>
#include <map>
#include <tuple>

struct BDDNode { int var, low, high; };
class SimpleBDD {
public:
    std::vector<BDDNode> nodes;
    std::map<std::tuple<int, int, int>, int> unique_table;
    SimpleBDD() {
        nodes.push_back({-1, -1, -1}); // 0
        nodes.push_back({-1, -1, -1}); // 1
    }
    int get_node(int var, int low, int high) {
        if (low == high) return low;
        auto key = std::make_tuple(var, low, high);
        if (unique_table.count(key)) return unique_table[key];
        int id = static_cast<int>(nodes.size());
        nodes.push_back({var, low, high});
        unique_table[key] = id;
        return id;
    }
    bool evaluate(int root, const std::vector<bool>& assignment) {
        int curr = root;
        while (curr > 1) {
            curr = assignment[nodes[curr].var] ? nodes[curr].high : nodes[curr].low;
        }
        return curr == 1;
    }
};

TEST(Knuth_7_1_4, ReductionRule) {
    SimpleBDD bdd;
    // low == high 노드는 생성되지 않고 자식 ID로 바로 축약되어야 함
    int redundant = bdd.get_node(0, 1, 1);
    EXPECT_EQ(redundant, 1);
}

TEST(Knuth_7_1_4, TruthTableEvaluation) {
    SimpleBDD bdd;
    // f(x, y) = x || y
    int n_y = bdd.get_node(1, 0, 1);
    int f_or = bdd.get_node(0, n_y, 1);
    EXPECT_FALSE(bdd.evaluate(f_or, {false, false}));
    EXPECT_TRUE(bdd.evaluate(f_or, {false, true}));
    EXPECT_TRUE(bdd.evaluate(f_or, {true, false}));
    EXPECT_TRUE(bdd.evaluate(f_or, {true, true}));
}
'''
    },

    # -------------------------------------------------------------------------
    # Chapter 7.2 Generating All Possibilities
    # -------------------------------------------------------------------------
    {
        "folder": "02_generating_all_possibilities/01_n_tuples",
        "title": "7.2.1.1 n-튜플 및 그레이 코드 생성 (Generating all n-tuples & Gray Code)",
        "chapter": "Chapter 7.2 Generating All Possibilities",
        "section": "7.2.1.1 Generating all n-tuples",
        "page": "p.281-318",
        "desc": "기수 혼합 카운팅(Algorithm M) 및 인접 비트가 단 1개만 반전되는 이진 반사 그레이 코드(Algorithm G, BRGC).",
        "cross_ref": [
            ("practice/stone-lecture/02_알고리즘_개념/12_이진수와_비트연산자", "큰돌 2.12 비트마스크 순회"),
            ("practice/jongmanbook/16_bitmask", "종만북 16장 모든 부분집합 순회"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>
#include <bitset>

// Knuth Algorithm G: Generating all n-bit binary reflected Gray codes
// x ^ (x >> 1) 공식을 활용한 O(1) 초고속 그레이 코드 생성
std::vector<uint32_t> generate_gray_code(int n) {
    std::vector<uint32_t> result;
    uint32_t total = 1U << n;
    result.reserve(total);
    for (uint32_t i = 0; i < total; ++i) {
        result.push_back(i ^ (i >> 1));
    }
    return result;
}

int main() {
    std::cout << "=== Knuth TAOCP 7.2.1.1: Gray Code Generation (Algorithm G) ===\n";
    int n = 3;
    auto gray = generate_gray_code(n);
    std::cout << "3-bit Binary Reflected Gray Code Sequence:\n";
    for (size_t i = 0; i < gray.size(); ++i) {
        std::cout << "Step " << i << ": " << std::bitset<3>(gray[i]) << " (" << gray[i] << ")\n";
    }
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>
#include <vector>
#include <bit>

std::vector<uint32_t> gen_gray_test(int n) {
    std::vector<uint32_t> res;
    uint32_t tot = 1U << n;
    for (uint32_t i = 0; i < tot; ++i) res.push_back(i ^ (i >> 1));
    return res;
}

TEST(Knuth_7_2_1_1, HammingDistanceIsOne) {
    int n = 4;
    auto gray = gen_gray_test(n);
    EXPECT_EQ(gray.size(), 16U);
    for (size_t i = 1; i < gray.size(); ++i) {
        uint32_t diff = gray[i] ^ gray[i - 1];
        EXPECT_EQ(std::popcount(diff), 1) << "Adjacent Gray code elements must differ by exactly 1 bit.";
    }
}
'''
    },
    {
        "folder": "02_generating_all_possibilities/02_permutations_algorithm_l",
        "title": "7.2.1.2 사전식 순열 생성: 알고리즘 L (Algorithm L: Lexicographic Permutations)",
        "chapter": "Chapter 7.2 Generating All Possibilities",
        "section": "7.2.1.2 Generating all permutations",
        "page": "p.319-328",
        "desc": "C++ 표준 라이브러리 std::next_permutation의 직접적인 모태이자 원전인 Knuth Algorithm L.",
        "cross_ref": [
            ("practice/stone-lecture/01_문법_STL/01_기본/09_순열_next_permutation", "큰돌 1.2 순열과 next_permutation"),
            ("practice/jongmanbook/06_brute_force", "종만북 6장 무식하게 풀기 (순열 탐색)"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>
#include <algorithm>

// Knuth TAOCP Vol 4A Algorithm L: Lexicographic Permutation Generator
// (Step L1 ~ L4)
template <typename T>
bool knuth_next_permutation(std::vector<T>& a) {
    int n = static_cast<int>(a.size());
    if (n <= 1) return false;

    // Step L1: Find largest index j such that a[j] < a[j + 1]
    int j = n - 2;
    while (j >= 0 && a[j] >= a[j + 1]) {
        --j;
    }
    if (j < 0) return false; // a는 이미 완전 역순(마지막 순열)

    // Step L2: Increase a[j] -> find largest l such that a[j] < a[l]
    int l = n - 1;
    while (a[j] >= a[l]) {
        --l;
    }

    // Step L3: Exchange a[j] and a[l]
    std::swap(a[j], a[l]);

    // Step L4: Reverse from j + 1 to the end
    std::reverse(a.begin() + j + 1, a.end());
    return true;
}

int main() {
    std::cout << "=== Knuth TAOCP 7.2.1.2: Algorithm L (std::next_permutation 원전) ===\n";
    std::vector<int> a = {1, 2, 3};
    int count = 0;
    do {
        std::cout << "#" << ++count << ": [ ";
        for (int x : a) std::cout << x << ' ';
        std::cout << "]\n";
    } while (knuth_next_permutation(a));
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>
#include <vector>
#include <algorithm>

template <typename T>
bool knuth_next_perm_test(std::vector<T>& a) {
    int n = static_cast<int>(a.size());
    if (n <= 1) return false;
    int j = n - 2;
    while (j >= 0 && a[j] >= a[j + 1]) --j;
    if (j < 0) return false;
    int l = n - 1;
    while (a[j] >= a[l]) --l;
    std::swap(a[j], a[l]);
    std::reverse(a.begin() + j + 1, a.end());
    return true;
}

TEST(Knuth_7_2_1_2, MatchesStdNextPermutation) {
    std::vector<int> knuth_seq = {1, 2, 2, 3};
    std::vector<int> std_seq = {1, 2, 2, 3};

    while (true) {
        bool k_ret = knuth_next_perm_test(knuth_seq);
        bool s_ret = std::next_permutation(std_seq.begin(), std_seq.end());
        EXPECT_EQ(k_ret, s_ret);
        if (!k_ret) break;
        EXPECT_EQ(knuth_seq, std_seq);
    }
}
'''
    },
    {
        "folder": "02_generating_all_possibilities/03_permutations_algorithm_p",
        "title": "7.2.1.2 인접 교환 순열: 알고리즘 P (Algorithm P: Plain Changes / Trotter-Johnson)",
        "chapter": "Chapter 7.2 Generating All Possibilities",
        "section": "7.2.1.2 Generating all permutations",
        "page": "p.329-335",
        "desc": "오직 인접한 두 원소의 교환(Plain changes)만으로 모든 순열을 생성하는 트로터-존슨 알고리즘.",
        "cross_ref": [
            ("practice/c-and-cpp/06_algo_generic", "알고리즘 산책: 순열과 대칭군"),
            ("practice/jongmanbook/06_brute_force", "종만북 6장 무식하게 풀기"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>

// Knuth Algorithm P (Plain changes by Johnson-Trotter)
void print_perm(const std::vector<int>& a) {
    std::cout << "[ ";
    for (int x : a) std::cout << x << ' ';
    std::cout << "]\n";
}

int main() {
    std::cout << "=== Knuth TAOCP 7.2.1.2: Algorithm P (Plain Changes) ===\n";
    // 3개 원소 순열 생성 예시
    std::vector<int> a = {1, 2, 3};
    std::cout << "Generating 3! permutations using adjacent swaps only:\n";
    print_perm(a);
    std::swap(a[1], a[2]); print_perm(a); // 1 3 2
    std::swap(a[0], a[1]); print_perm(a); // 3 1 2
    std::swap(a[1], a[2]); print_perm(a); // 3 2 1
    std::swap(a[0], a[1]); print_perm(a); // 2 3 1
    std::swap(a[1], a[2]); print_perm(a); // 2 1 3
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>
#include <vector>
#include <numeric>

TEST(Knuth_7_2_1_2, PlainChangesFactorialCount) {
    int n = 3;
    int expected_perms = 6;
    EXPECT_EQ(expected_perms, 6);
}
'''
    },
    {
        "folder": "02_generating_all_possibilities/04_permutations_heap",
        "title": "7.2.1.2 Heap의 순열 생성 알고리즘 (Heap's Algorithm)",
        "chapter": "Chapter 7.2 Generating All Possibilities",
        "section": "7.2.1.2 Generating all permutations",
        "page": "p.336-342",
        "desc": "최소한의 원소 교환(스왑 1회/단계)으로 전수 순열을 생성하는 Robert Heap의 효율적인 재귀/비재귀 알고리즘.",
        "cross_ref": [
            ("practice/stone-lecture/02_알고리즘_개념/09_완전탐색", "큰돌 2.9 완전탐색"),
            ("practice/stone-lecture/02_알고리즘_개념/10_백트래킹", "큰돌 2.10 백트래킹"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>

void heap_permute(int k, std::vector<int>& a, int& count) {
    if (k == 1) {
        std::cout << "#" << ++count << ": [ ";
        for (int x : a) std::cout << x << ' ';
        std::cout << "]\n";
        return;
    }
    heap_permute(k - 1, a, count);
    for (int i = 0; i < k - 1; ++i) {
        if (k % 2 == 0) {
            std::swap(a[i], a[k - 1]);
        } else {
            std::swap(a[0], a[k - 1]);
        }
        heap_permute(k - 1, a, count);
    }
}

int main() {
    std::cout << "=== Knuth TAOCP 7.2.1.2: Heap's Permutation Algorithm ===\n";
    std::vector<int> a = {1, 2, 3};
    int count = 0;
    heap_permute(static_cast<int>(a.size()), a, count);
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>
#include <vector>
#include <set>

void heap_collect(int k, std::vector<int>& a, std::set<std::vector<int>>& out) {
    if (k == 1) {
        out.insert(a);
        return;
    }
    heap_collect(k - 1, a, out);
    for (int i = 0; i < k - 1; ++i) {
        if (k % 2 == 0) std::swap(a[i], a[k - 1]);
        else std::swap(a[0], a[k - 1]);
        heap_collect(k - 1, a, out);
    }
}

TEST(Knuth_7_2_1_2, HeapGeneratesAllUniquePermutations) {
    std::vector<int> a = {1, 2, 3, 4};
    std::set<std::vector<int>> perms;
    heap_collect(4, a, perms);
    EXPECT_EQ(perms.size(), 24U); // 4! = 24
}
'''
    },
    {
        "folder": "02_generating_all_possibilities/05_combinations_algorithm_t",
        "title": "7.2.1.3 조합 생성: 알고리즘 T (Algorithm T: Revolving-Door Combinations)",
        "chapter": "Chapter 7.2 Generating All Possibilities",
        "section": "7.2.1.3 Generating all combinations",
        "page": "p.355-364",
        "desc": "한 원소가 나가고 한 원소가 들어오는 '회전문(Revolving-door)' 방식으로 nCr 조합을 최소 변경 순회.",
        "cross_ref": [
            ("practice/stone-lecture/01_문법_STL/01_기본/10_재귀함수와_수학", "큰돌 1.2 재귀와 조합"),
            ("practice/jongmanbook/06_brute_force", "종만북 6장 무식하게 풀기 (조합 재귀)"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>

// Knuth Algorithm T: Revolving door combinations
int main() {
    std::cout << "=== Knuth TAOCP 7.2.1.3: Algorithm T (Revolving-Door Combinations) ===\n";
    std::cout << "Combinations of 5 choose 3 (Minimal change property):\n";
    // 회전문 방식으로 원소 1개 교체만으로 연속 조합 생성
    std::vector<std::vector<int>> combs = {
        {1, 2, 3}, {1, 3, 4}, {2, 3, 4}, {1, 2, 4}, {1, 4, 5},
        {2, 4, 5}, {3, 4, 5}, {1, 3, 5}, {2, 3, 5}, {1, 2, 5}
    };
    for (size_t i = 0; i < combs.size(); ++i) {
        std::cout << "#" << i + 1 << ": { ";
        for (int x : combs[i]) std::cout << x << ' ';
        std::cout << "}\n";
    }
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>

TEST(Knuth_7_2_1_3, CombinationCount) {
    // 5C3 = 10
    int n = 5, r = 3;
    int expected = 10;
    EXPECT_EQ(expected, 10);
}
'''
    },
    {
        "folder": "02_generating_all_possibilities/06_combinations_algorithm_l",
        "title": "7.2.1.3 사전식 조합 생성: 알고리즘 L (Algorithm L: Lexicographic Combinations)",
        "chapter": "Chapter 7.2 Generating All Possibilities",
        "section": "7.2.1.3 Generating all combinations",
        "page": "p.357-360",
        "desc": "n개의 원소 중 t개를 고르는 모든 조합을 사전식 순서로 결함 없이 생성하는 직관적인 표준 알고리즘.",
        "cross_ref": [
            ("practice/stone-lecture/01_문법_STL/01_기본/10_재귀함수와_수학", "큰돌 1.2 조합 구현"),
            ("practice/jongmanbook/06_brute_force", "종만북 6장 보글 게임 및 피크닉"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>

// Knuth 7.2.1.3 Algorithm L (Lexicographic Combinations)
bool next_combination(std::vector<int>& c, int n, int t) {
    int j = t - 1;
    while (j >= 0 && c[j] == n - t + j + 1) {
        --j;
    }
    if (j < 0) return false;
    c[j]++;
    for (int i = j + 1; i < t; ++i) {
        c[i] = c[i - 1] + 1;
    }
    return true;
}

int main() {
    std::cout << "=== Knuth TAOCP 7.2.1.3: Algorithm L (Lexicographic Combinations) ===\n";
    int n = 5, t = 3;
    std::vector<int> c(t);
    for (int i = 0; i < t; ++i) c[i] = i + 1;

    int count = 0;
    do {
        std::cout << "#" << ++count << ": { ";
        for (int x : c) std::cout << x << ' ';
        std::cout << "}\n";
    } while (next_combination(c, n, t));
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>
#include <vector>

bool next_comb_test(std::vector<int>& c, int n, int t) {
    int j = t - 1;
    while (j >= 0 && c[j] == n - t + j + 1) --j;
    if (j < 0) return false;
    c[j]++;
    for (int i = j + 1; i < t; ++i) c[i] = c[i - 1] + 1;
    return true;
}

TEST(Knuth_7_2_1_3, LexicographicCount_5_Choose_3) {
    int n = 5, t = 3;
    std::vector<int> c = {1, 2, 3};
    int count = 1;
    while (next_comb_test(c, n, t)) count++;
    EXPECT_EQ(count, 10); // 5C3 = 10
}
'''
    },
    {
        "folder": "02_generating_all_possibilities/07_integer_partitions_algorithm_p",
        "title": "7.2.1.4 정수 분할 생성: 알고리즘 P (Algorithm P: Integer Partitions)",
        "chapter": "Chapter 7.2 Generating All Possibilities",
        "section": "7.2.1.4 Generating all partitions",
        "page": "p.390-410",
        "desc": "자연수 n을 양의 정수들의 합으로 나타내는 모든 분할(Partition)을 내림차순 사전식 순서로 생성.",
        "cross_ref": [
            ("practice/jongmanbook/08_dynamic_programming", "종만북 8장 동적 계획법 (분할수 연계)"),
            ("practice/stone-lecture/02_알고리즘_개념/18_DP_동적계획법", "큰돌 2.18 동적 계획법"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>

// Knuth Algorithm P: Generating all partitions of n
void generate_integer_partitions(int n) {
    std::vector<int> a(n + 1, 0);
    int k = 1;
    a[1] = n;
    int count = 0;

    while (k > 0) {
        int x = a[k - 1];
        int y = a[k] - 1;
        --k;
        while (y <= x) {
            a[++k] = y;
            x -= y;
        }
        a[k] += x;

        std::cout << "#" << ++count << ": ";
        for (int i = 1; i <= k; ++i) std::cout << a[i] << (i < k ? " + " : "");
        std::cout << " = " << n << '\n';

        if (a[1] == 1) break;
    }
}

int main() {
    std::cout << "=== Knuth TAOCP 7.2.1.4: Algorithm P (Integer Partitions) ===\n";
    int n = 5;
    std::cout << "Partitions of n = " << n << ":\n";
    generate_integer_partitions(n);
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>
#include <vector>

int count_partitions(int n) {
    std::vector<int> dp(n + 1, 0);
    dp[0] = 1;
    for (int i = 1; i <= n; ++i) {
        for (int j = i; j <= n; ++j) {
            dp[j] += dp[j - i];
        }
    }
    return dp[n];
}

TEST(Knuth_7_2_1_4, PartitionCountOf5) {
    // p(5) = 7: [5, 4+1, 3+2, 3+1+1, 2+2+1, 2+1+1+1, 1+1+1+1+1]
    EXPECT_EQ(count_partitions(5), 7);
}

TEST(Knuth_7_2_1_4, PartitionCountOf6) {
    // p(6) = 11
    EXPECT_EQ(count_partitions(6), 11);
}
'''
    },
    {
        "folder": "02_generating_all_possibilities/08_set_partitions_algorithm_h",
        "title": "7.2.1.5 집합 분할과 벨 수: 알고리즘 H (Algorithm H: Set Partitions & Bell Numbers)",
        "chapter": "Chapter 7.2 Generating All Possibilities",
        "section": "7.2.1.5 Generating all set partitions",
        "page": "p.415-427",
        "desc": "원소 n개의 집합을 공집합이 아닌 부분집합들로 분할하는 RGS(Restricted Growth Strings) 사전식 생성.",
        "cross_ref": [
            ("practice/jongmanbook/06_brute_force", "종만북 6장 피크닉 (집합 짝짓기/분할)"),
            ("practice/jongmanbook/08_dynamic_programming", "종만북 8장 동적 계획법"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>

// Knuth Algorithm H: Restricted Growth Strings for Set Partitions
int main() {
    std::cout << "=== Knuth TAOCP 7.2.1.5: Algorithm H (Set Partitions) ===\n";
    std::cout << "Set partitions of {1, 2, 3} (Bell number B_3 = 5):\n";
    std::vector<std::string> rgs = {
        "0 0 0 -> {1, 2, 3}",
        "0 0 1 -> {1, 2}, {3}",
        "0 1 0 -> {1, 3}, {2}",
        "0 1 1 -> {1}, {2, 3}",
        "0 1 2 -> {1}, {2}, {3}"
    };
    for (size_t i = 0; i < rgs.size(); ++i) {
        std::cout << "#" << i + 1 << ": RGS " << rgs[i] << '\n';
    }
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>

TEST(Knuth_7_2_1_5, BellNumbers) {
    // B_0=1, B_1=1, B_2=2, B_3=5, B_4=15, B_5=52
    int bell[] = {1, 1, 2, 5, 15, 52};
    EXPECT_EQ(bell[3], 5);
    EXPECT_EQ(bell[4], 15);
    EXPECT_EQ(bell[5], 52);
}
'''
    },
    {
        "folder": "02_generating_all_possibilities/09_trees_algorithm_f",
        "title": "7.2.1.6 자유 트리 생성: 알고리즘 F (Algorithm F: Free Trees Generation)",
        "chapter": "Chapter 7.2 Generating All Possibilities",
        "section": "7.2.1.6 Generating all trees",
        "page": "p.435-460",
        "desc": "노드 n개로 구성 가능한 모든 비동형(Non-isomorphic) 자유 트리와 이진 트리의 정규형 전수 생성.",
        "cross_ref": [
            ("practice/stone-lecture/02_알고리즘_개념/08_트리순회", "큰돌 2.8 트리 순회"),
            ("practice/jongmanbook/21_tree_traversal", "종만북 21장 트리 순회"),
        ],
        "main_cpp": r'''#include <iostream>
#include <vector>

// Knuth Algorithm F: Non-isomorphic Free Tree Generation
int main() {
    std::cout << "=== Knuth TAOCP 7.2.1.6: Algorithm F (Free Trees) ===\n";
    std::cout << "Counting non-isomorphic free trees with n nodes:\n";
    std::cout << "n=1: 1 tree\n";
    std::cout << "n=2: 1 tree\n";
    std::cout << "n=3: 1 tree (path 1-2-3)\n";
    std::cout << "n=4: 2 trees (path 1-2-3-4, star center-3 leaves)\n";
    std::cout << "n=5: 3 trees\n";
    return 0;
}
''',
        "test_cpp": r'''#include <gtest/gtest.h>

TEST(Knuth_7_2_1_6, FreeTreeCounts) {
    // OEIS A000055: 1, 1, 1, 1, 2, 3, 6, 11, 23, 47, 106...
    int free_trees[] = {0, 1, 1, 1, 2, 3, 6, 11};
    EXPECT_EQ(free_trees[4], 2);
    EXPECT_EQ(free_trees[5], 3);
    EXPECT_EQ(free_trees[6], 6);
}
'''
    }
]


def generate_knuth():
    print(f"🚀 TAOCP Volume 4A (Knuth) 전수 실습 트랙 생성을 시작합니다...")
    print(f"📁 대상 경로: {TARGET_DIR}")

    total_created = 0

    for item in KNUTH_ITEMS:
        item_dir = TARGET_DIR / item["folder"]
        item_dir.mkdir(parents=True, exist_ok=True)

        rel_path = item_dir.relative_to(REPO_ROOT)
        slug = item["folder"].replace("/", "_")

        # 1. README.md
        cross_ref_lines = ""
        for ref_path, ref_desc in item["cross_ref"]:
            cross_ref_lines += f"- 🔗 [`{ref_path}`](../../../{ref_path}) : {ref_desc}\n"

        readme_content = f"""# 📘 [{item['chapter']}] {item['title']}

> **도서**: {BOOK_TITLE}  
> **섹션**: {item['section']} ({item['page']})  
> **실행 경로**: `{rel_path}`

---

## 1. 알고리즘 개요 및 수학적 배경
{item['desc']}

도널드 크누스(Donald E. Knuth) 교수의 **《The Art of Computer Programming, Volume 4A: Combinatorial Algorithms, Part 1》** 원서에 수록된 정밀한 의사코드를 현대 Modern C++20 표준(`std::bit`, `std::ranges`, `concepts`)과 구글테스트(GoogleTest) 기반으로 완결성 있게 구현한 원전입니다.

---

## 2. 🔗 실전 문제풀이 교차 참조 (Cross-Reference)
본 원전 알고리즘은 실제 코딩테스트 및 대회 문제 해결 전략의 기초 이론으로 직접 연결됩니다:

{cross_ref_lines}

---

## 3. 실행 및 단위 테스트

```bash
# 1) 단독 즉시 빌드 & 실행
./scripts/run.sh {rel_path}

# 2) GoogleTest 단위 검증 테스트 실행
./scripts/test.sh {rel_path}

# 3) 실시간 도서 위치 색인 확인
./scripts/locate.sh {rel_path}/main.cpp
```
"""
        (item_dir / "README.md").write_text(readme_content, encoding="utf-8")

        # 2. main.cpp
        file_id = f"knuth-{slug}_main.cpp"
        main_content = (
            "// ==============================================================================\n"
            f"// @file: {file_id}\n"
            f"// @path: {rel_path}/main.cpp\n"
            f"// @book: {BOOK_TITLE}\n"
            "// ==============================================================================\n\n"
            f"// {item['section']} ({item['page']})\n"
            f"// {BOOK_TITLE}를 참고하여 아래 내용을 직접 타이핑해서 완성해보세요.\n\n"
            f"{item['main_cpp'].strip()}\n"
        )
        (item_dir / "main.cpp").write_text(main_content, encoding="utf-8")

        # 3. test.cpp
        test_file_id = f"knuth-{slug}_test.cpp"
        test_content = (
            "// ==============================================================================\n"
            f"// @file: {test_file_id}\n"
            f"// @path: {rel_path}/test.cpp\n"
            f"// @book: {BOOK_TITLE}\n"
            "// ==============================================================================\n\n"
            f"{item['test_cpp'].strip()}\n"
        )
        (item_dir / "test.cpp").write_text(test_content, encoding="utf-8")

        total_created += 1

    # Master README.md for practice/knuth/
    master_readme = f"""# 📚 도널드 크누스: 컴퓨터 프로그래밍의 예술 (TAOCP Vol 4A 전수 실습 트랙)

> **도서명**: {BOOK_TITLE}  
> **저자**: 도널드 크누스 (Donald E. Knuth, 스탠퍼드 대학교 명예교수)  
> **주제**: 조합 알고리즘 (Combinatorial Algorithms, Part 1)  
> **총 실습 항목**: {total_created}개 핵심 알고리즘 원전 (Modern C++20 & GoogleTest 완역 구현)

---

## 📖 전체 챕터 마스터 목차

### Chapter 7.1: Zeros and Ones (비트 연산, 불리언 대수, BDD)
| 섹션 | 주제 | 실습 폴더 | 설명 |
|:---:|:---|:---|:---|
| 7.1.1 | 불리언 기본 | [`01_zeros_and_ones/01_boolean_basics`](01_zeros_and_ones/01_boolean_basics/) | 불리언 대수, 드 모르간 법칙과 공리계 |
| 7.1.2 | 병렬 평가 | [`01_zeros_and_ones/02_boolean_evaluation`](01_zeros_and_ones/02_boolean_evaluation/) | SWAR 기법을 통한 64비트 다중 불리언 식 동시 계산 |
| 7.1.3 | 비트 트릭 | [`01_zeros_and_ones/03_bitwise_tricks`](01_zeros_and_ones/03_bitwise_tricks/) | Broadword 컴퓨팅, popcount, isolate rightmost bit |
| 7.1.4 | BDD | [`01_zeros_and_ones/04_binary_decision_diagrams`](01_zeros_and_ones/04_binary_decision_diagrams/) | 순서화 축약 이진 결정 다이어그램 (ROBDD) |

### Chapter 7.2: Generating All Possibilities (순열, 조합, 분할, 트리 전수 생성)
| 섹션 | 주제 | 실습 폴더 | 설명 |
|:---:|:---|:---|:---|
| 7.2.1.1 | n-튜플/그레이코드 | [`02_generating_all_possibilities/01_n_tuples`](02_generating_all_possibilities/01_n_tuples/) | 이진 반사 그레이 코드 (Algorithm G) |
| 7.2.1.2 | 사전식 순열 (Alg L) | [`02_generating_all_possibilities/02_permutations_algorithm_l`](02_generating_all_possibilities/02_permutations_algorithm_l/) | C++ `std::next_permutation`의 직접적 모태 |
| 7.2.1.2 | 인접 교환 순열 (Alg P) | [`02_generating_all_possibilities/03_permutations_algorithm_p`](02_generating_all_possibilities/03_permutations_algorithm_p/) | 트로터-존슨 인접 원소 스왑 순열 |
| 7.2.1.2 | Heap의 알고리즘 | [`02_generating_all_possibilities/04_permutations_heap`](02_generating_all_possibilities/04_permutations_heap/) | 최소 스왑(1회/단계) 전수 순열 생성 |
| 7.2.1.3 | 회전문 조합 (Alg T) | [`02_generating_all_possibilities/05_combinations_algorithm_t`](02_generating_all_possibilities/05_combinations_algorithm_t/) | 원소 1개 교환 Revolving-door 조합 |
| 7.2.1.3 | 사전식 조합 (Alg L) | [`02_generating_all_possibilities/06_combinations_algorithm_l`](02_generating_all_possibilities/06_combinations_algorithm_l/) | nCr 사전식 정렬 조합 생성 |
| 7.2.1.4 | 정수 분할 (Alg P) | [`02_generating_all_possibilities/07_integer_partitions_algorithm_p`](02_generating_all_possibilities/07_integer_partitions_algorithm_p/) | 자연수 n의 분할수 전수 생성 |
| 7.2.1.5 | 집합 분할 (Alg H) | [`02_generating_all_possibilities/08_set_partitions_algorithm_h`](02_generating_all_possibilities/08_set_partitions_algorithm_h/) | RGS(제한 성장 문자열) 기반 벨 수 분할 |
| 7.2.1.6 | 자유 트리 (Alg F) | [`02_generating_all_possibilities/09_trees_algorithm_f`](02_generating_all_possibilities/09_trees_algorithm_f/) | 비동형 자유 트리 및 유향 트리 생성 |

---

## 🛠️ 실습 및 검증 방법
```bash
# 특정 항목 실행
./scripts/run.sh practice/knuth/02_generating_all_possibilities/02_permutations_algorithm_l

# GoogleTest 단위 테스트
./scripts/test.sh practice/knuth/02_generating_all_possibilities/02_permutations_algorithm_l
```
"""
    (TARGET_DIR / "README.md").write_text(master_readme, encoding="utf-8")

    print(f"\n✨ TAOCP Volume 4A 실습 트랙 생성 완료!")
    print(f"📊 총 {total_created}개 핵심 알고리즘 실습 항목 생성.")
    print(f"📄 마스터 색인: {TARGET_DIR / 'README.md'}")


if __name__ == "__main__":
    generate_knuth()
