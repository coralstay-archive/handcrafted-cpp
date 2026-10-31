#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_알고리즘교안.pdf 의 각 절/코드예제를 타이핑 연습용 디렉토리로 생성한다.
각 항목마다 main.cpp(타이핑용) 와 test.cpp(GoogleTest 작성용)를 만든다.
이미 존재하는 main.cpp/test.cpp 는 건드리지 않는다 (사용자가 작성한 내용 보존).
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "practice", "stone-lecture", "01_문법_STL")

# (섹션 디렉토리, 섹션 제목), [(항목 슬러그, 항목 제목, 페이지), ...]
SECTIONS = [
    ("01_기본", "1.2 기본", [
        ("예제로_이해하는_Cpp", "입력받은 문자열을 그대로 출력하는 예제", "p.24"),
        ("typedef", "typedef 로 타입 별칭 만들기", "p.25"),
        ("define", "#define 상수/매크로", "p.26"),
    ]),
    ("02_입력과_출력", "1.3 입력과 출력", [
        ("cin_기본", "cin >> a; 기본 입력", "p.27"),
        ("cin_여러변수_입력", "cin >> a >> b; 여러 변수 입력", "p.28"),
        ("scanf_기본", "scanf 형식지정 입력", "p.28"),
        ("scanf_실수를_정수로", "scanf 로 실수를 정수 2개로 나눠 받기", "p.30"),
        ("getline_기본", "getline(cin, s) 기본", "p.31"),
        ("getline_구분자", "getline 세번째 인자로 종결문자 지정", "p.32"),
        ("getline_bufferflush", "cin 과 getline 혼용시 버퍼플러시", "p.33"),
        ("cout_기본", "cout << 기본 출력", "p.34"),
        ("cout_실수출력_setprecision", "fixed << setprecision() 로 실수 출력", "p.34"),
        ("printf_기본", "printf 형식지정 출력", "p.35"),
        ("printf_형식_02d", "printf 로 소수점자리/자릿수(%02d) 맞추기", "p.35"),
        ("printf_문자열포함", "printf 로 여러 타입(문자, 문자열 등) 출력", "p.36"),
    ]),
    ("03_타입과_타입변환", "1.4 타입과 타입 변환", [
        ("void_함수", "void: 리턴값이 없는 함수", "p.37"),
        ("void_함수_선언과_정의분리", "함수 선언부와 정의부 분리하기", "p.38"),
        ("char_기본", "char 문자 선언과 출력", "p.38"),
        ("char_함수리턴", "char 을 리턴하는 함수", "p.39"),
        ("char_초기화_비교", "char a='\\0' 과 char b=0 비교", "p.39"),
        ("string_인덱스접근_한글바이트", "string 인덱스 접근과 한글 바이트 이슈", "p.41"),
        ("string_메서드모음", "+=, begin, end, insert, erase, find, substr 등", "p.42"),
        ("string_pushback", "string.push_back() 으로 문자 하나씩 추가", "p.43"),
        ("string_plusequal_성능비교", "+= 와 + 의 성능 차이 (good/bad)", "p.44"),
        ("string_아스키코드_증가", "s[0]++ 로 아스키코드 기반 증가", "p.46"),
        ("string_reverse", "reverse() 로 문자열 뒤집기", "p.48"),
        ("string_split_콤마", "직접 구현한 split() - 콤마 기준", "p.49"),
        ("string_split_화살표", "직접 구현한 split() - 화살표(->) 기준", "p.50"),
        ("범위기반_for루프_기본", "범위기반 for 루프 기본", "p.51"),
        ("범위기반_for루프_VLA_에러", "런타임 크기 배열(VLA) + 범위기반for 에러 예시", "p.52"),
        ("범위기반_for루프_vector로_해결", "vector 로 런타임 크기 배열 + 범위기반for", "p.53"),
        ("sizeof", "sizeof 연산자로 배열 크기/개수 구하기", "p.53"),
        ("atoi", "atoi(s.c_str()) 로 문자열을 정수로", "p.54"),
        ("stoi", "stoi(s) 로 문자열을 정수로", "p.54"),
        ("stoi_에러", "stoi 에 숫자가 아닌 문자열을 넣었을 때 에러", "p.55"),
        ("bool", "bool 참과 거짓, bool() 형변환", "p.56"),
        ("int연산_나눗셈_버림", "int 끼리 나눗셈시 소수점 버림 vs double", "p.57"),
        ("const_참조_매개변수", "const int& 매개변수로 수정 방지", "p.58"),
        ("const_범위기반for", "범위기반 for 에서 const int& 로 상수 만들기", "p.58"),
        ("오버플로", "int 오버플로 예제", "p.59"),
        ("언더플로", "int 언더플로 예제", "p.59"),
        ("pair_tuple_tie", "tie() 로 pair/tuple 값 꺼내기", "p.61"),
        ("pair_tuple_직접접근", "first/second, get<>() 로 직접 접근", "p.62"),
        ("auto_기본", "auto 타입 추론 기본", "p.63"),
        ("auto_iterator_pair", "auto 로 pair<int,int> 반복문 간결화", "p.63"),
        ("타입변환_double을_int로", "(int) 캐스팅으로 double을 int로", "p.64"),
        ("타입변환_순서주의", "(int) p * 100 과 (int)(100 * p) 차이", "p.65"),
        ("size_음수비교_bad", "size_t 와 음수 비교시 잘못된 예 (bad)", "p.65"),
        ("size_음수비교_good", "(int) 캐스팅으로 올바르게 비교 (good)", "p.65"),
        ("문자를_숫자로", "아스키코드로 문자를 숫자로 변환(a~z -> 0~25)", "p.66"),
        ("숫자문자열_배열로", "s[i] - '0' 으로 숫자문자열을 정수 배열로", "p.67"),
    ]),
    ("04_메모리와_포인터", "1.5 메모리와 포인터", [
        ("변수의_메모리주소", "&i 로 변수의 메모리 주소 출력", "p.69"),
        ("변수값_변경_주소불변", "값을 바꿔도 주소는 변하지 않음", "p.69"),
        ("포인터_기본", "int* a = &i; 포인터 선언", "p.71"),
        ("역참조_연산자", "* 연산자로 포인터 역참조", "p.72"),
        ("array_to_pointer_decay", "배열 이름이 포인터로 decay 되는 예제", "p.73"),
        ("정적할당_BSS_segment", "BSS segment 에 할당되는 변수들", "p.75"),
        ("정적할당_Data_segment", "Data segment 에 할당되는 변수들", "p.75"),
    ]),
    ("05_이터레이터", "1.6 이터레이터", [
        ("이터레이터_기본_순회", "begin/end/advance, *(v.begin()+i) 등", "p.77"),
    ]),
    ("06_함수", "1.7 함수", [
        ("fill_1차원_2차원", "fill() 로 1차원/2차원 배열 초기화", "p.81"),
        ("fill_배열이름_초기화", "배열 이름 기반 fill(a, a+10, val)", "p.82"),
        ("fill_포인터접근_100개요소", "&b[0][0] + 10*10 포인터 접근 부연설명", "p.83"),
        ("fill_8x8_부분초기화_문제", "왜 fill 로 전체초기화를 해야 하는가", "p.84"),
        ("memset_기본", "memset() 로 0, -1 초기화", "p.85"),
        ("memset_char초기화", "memset() 로 char 배열 초기화", "p.86"),
        ("초기화리스트_동적초기화_실패", "{0, } 초기화가 동적으로는 안 되는 예시", "p.86"),
        ("memcpy_기본", "memcpy() 로 배열 깊은 복사", "p.88"),
        ("memcpy_temp보관_활용", "memcpy 로 원본을 temp 에 보관 후 복원", "p.89"),
        ("memcpy_vector_실패", "memcpy 는 vector 에서 깊은 복사가 안 되는 예", "p.90"),
        ("memcpy_trivially_copyable_확인", "is_trivial 로 TriviallyCopyable 확인", "p.91"),
        ("copy_vector", "copy() 로 vector 깊은 복사", "p.92"),
        ("copy_array", "copy() 로 array 깊은 복사", "p.92"),
        ("sort_기본_오름차순", "sort() 기본(오름차순)", "p.94"),
        ("sort_less_greater", "less<>() / greater<>() 로 정렬 방향 지정", "p.95"),
        ("sort_pair_자동정렬", "pair 로 만든 vector 자동 정렬(first,second순)", "p.95"),
        ("sort_pair_커스텀_cmp", "커스텀 비교함수 cmp 로 정렬", "p.96"),
        ("sort_원리_cmp함수", "sort() 의 원리: cmp 가 true 인 순서로 교환", "p.97"),
        ("stable_sort", "stable_sort() 로 원래 순서를 보존하며 정렬", "p.97"),
        ("unique_기본", "unique() 기본 사용", "p.99"),
        ("unique_예제2", "unique() 두번째 예제", "p.99"),
        ("unique_erase_병행", "sort + unique + erase 조합", "p.100"),
        ("lower_upper_bound_기본", "lower_bound / upper_bound 기본", "p.101"),
        ("lower_bound_역참조", "&*lower_bound() 로 주소값 확인", "p.102"),
        ("lower_bound_주소값_뺄셈", "주소값끼리 빼서 인덱스 구하기", "p.103"),
        ("lower_bound_요소출력", "*lower_bound() 로 요소 값 바로 출력", "p.104"),
        ("lower_upper_bound_개수세기", "upper_bound - lower_bound 로 개수 세기", "p.104"),
        ("lower_upper_bound_근방지점", "요소가 없을 때 근방 지점을 반환하는 예", "p.104"),
        ("accumulate", "accumulate() 로 배열의 합 구하기", "p.105"),
        ("max_element", "max_element() 로 최댓값/인덱스 구하기", "p.105"),
        ("min_element", "min_element() 로 최솟값/인덱스 구하기", "p.106"),
        ("메모리주소_뺄셈_인덱스차이", "포인터/이터레이터 뺄셈은 인덱스 차이를 반환", "p.107"),
    ]),
    ("07_자료구조", "1.8 자료구조", [
        ("vector_기본_사용", "push_back/pop_back/erase/find/fill/clear", "p.109"),
        ("vector_2차원_3가지방법", "vector 로 2차원 배열 만드는 3가지 방법", "p.116"),
        ("vector_정적할당", "vector<int> v(5, 100) 정적할당+초기값", "p.115"),
        ("vector_중괄호초기화", "vector<int> v{10,20,30,40,50}", "p.115"),
        ("array_기본", "array(C스타일) 기본 선언/순회", "p.117"),
        ("array_2차원_탐색순서_good_bad", "2차원배열 탐색 순서에 따른 캐시효율(good/bad)", "p.118"),
        ("list_기본_사용", "push_front/back, insert, erase, front, back", "p.122"),
        ("map_기본_사용", "insert, [], size, erase, find, 순회", "p.126"),
        ("map_참조시_자동생성_주의", "대괄호[]로 참조만 해도 요소가 생기는 주의점", "p.128"),
        ("map_요소존재확인_로직", "if(mp[1]) 로 존재를 확인하면 안 되는 이유", "p.129"),
        ("map_find_안전한확인", "find() 로 안전하게 존재 확인 후 대입", "p.130"),
        ("unordered_map_기본", "unordered_map 기본 (정렬 안 됨)", "p.131"),
        ("set_기본", "set 기본, 중복 제거+자동 정렬", "p.132"),
        ("multiset_기본", "multiset 기본(중복 허용)", "p.135"),
        ("multiset_count", "multiset.count() 로 빈도수 계산", "p.135"),
        ("stack_기본", "stack push/pop/top, LIFO 확인", "p.137"),
        ("queue_기본", "queue push/pop/front, FIFO 확인", "p.139"),
        ("deque_기본", "deque push_front/back, pop_front/back", "p.140"),
        ("struct_Ralo_기본", "간단한 struct 정의와 vector에 담기", "p.141"),
        ("struct_Point_생성자_연산자오버로딩", "생성자, 초기값, operator< 오버로딩", "p.142"),
        ("struct_sort_compare함수_string", "숫자로 이루어진 string 배열 정렬(compare)", "p.145"),
        ("struct_sort_compare함수_구조체", "struct 를 compare 함수로 정렬", "p.146"),
        ("struct_3개멤버_정렬", "3개의 멤버변수를 다중 기준으로 정렬", "p.146"),
        ("struct_vector정렬", "vector<struct> 를 cmp 로 정렬", "p.147"),
        ("priority_queue_int_오름차순_내림차순", "priority_queue<int> greater/less 로 방향 지정", "p.149"),
        ("priority_queue_구조체_기본내림", "구조체를 담은 우선순위큐 (operator<)", "p.150"),
        ("priority_queue_구조체_반대설정", "우선순위큐는 반대로 설정해야 하는 이유", "p.150"),
        ("priority_queue_operator함수객체", "cmp 구조체의 operator() 로 커스텀 정렬", "p.151"),
        ("operator_함수호출연산자_Adder", "operator() 함수 호출 연산자 오버로딩(Adder)", "p.152"),
    ]),
    ("08_호출방식", "1.9 값의 의한 호출과 참조에 의한 호출", [
        ("값에의한호출_기본", "call by value: 복사되어 원본이 안 바뀜", "p.155"),
        ("값에의한호출_vector", "vector 를 값으로 넘기면 원본이 안 바뀜", "p.156"),
        ("참조에의한호출_기본", "call by reference(&): 원본이 바뀜", "p.156"),
        ("참조에의한호출_vector", "vector 를 참조로 넘기면 원본이 바뀜", "p.157"),
        ("성능비교_참조호출_맞은코드", "100만개 배열, 참조로 넘긴 맞은 코드", "p.158"),
        ("성능비교_값호출_틀린코드", "100만개 배열, 값으로 넘겨 시간초과 나는 코드", "p.159"),
    ]),
    ("09_배열_수정하기", "1.10 배열 수정하기", [
        ("array_1차원_수정_3가지방법", "int a[], int a[3], int *a 로 배열 수정", "p.160"),
        ("vector_2차원_수정", "vector<vector<int>>& 로 2차원 배열 수정", "p.161"),
        ("array_2차원_수정", "int a[][3] 로 2차원 배열 수정", "p.161"),
    ]),
    ("10_재귀함수와_수학", "1.11 재귀함수와 수학", [
        ("팩토리얼_재귀", "재귀함수로 팩토리얼 구현", "p.162"),
        ("팩토리얼_반복문_비교", "반복문으로 구현한 팩토리얼과 비교", "p.163"),
        ("피보나치_재귀", "재귀함수로 피보나치 수열 구현", "p.163"),
        ("순열_next_prev_permutation", "next_permutation / prev_permutation", "p.167"),
        ("순열_next_permutation_일부범위", "배열의 일부 구간만 순열 만들기", "p.168"),
        ("순열_정렬안된배열_실패예", "정렬 안 된 배열로 next_permutation 시 실패 예", "p.168"),
        ("순열_next_permutation_addr_a0_a3", "next_permutation(&a[0], &a[3])", "p.169"),
        ("순열_next_permutation_addr_a0plus3", "next_permutation(&a[0], &a[0]+3)", "p.170"),
        ("순열_next_permutation_pointer_decay", "next_permutation(a, a+3) pointer decay", "p.170"),
        ("순열_next_permutation_flag_원리", "next_permutation 이 반환하는 flag 의 원리", "p.170"),
        ("순열_재귀구현", "재귀로 직접 구현한 순열(makePermutation)", "p.171"),
        ("순열_재귀구현_디버깅코드", "재귀 순열 구현에 디버깅 로그 추가", "p.173"),
        ("조합_재귀구현", "재귀로 직접 구현한 조합(combi)", "p.174"),
        ("조합_중첩for문_3중", "r=3 일 때 3중 for문으로 구현한 조합", "p.175"),
        ("조합_중첩for문_다른형태", "3중 for문 조합의 다른 순서 형태", "p.176"),
        ("조합_중첩for문_r2", "r=2 일 때 2중 for문으로 구현한 조합", "p.176"),
        ("최대공약수_최소공배수", "gcd, lcm 구현", "p.178"),
        ("에라토스테네스의체", "에라토스테네스의 체로 소수 목록 구하기", "p.179"),
        ("소수판별_함수", "배열 없이 단일 수의 소수 여부 판별", "p.180"),
        ("등차수열의합_forloop", "for문으로 등차수열의 합 구하기", "p.181"),
        ("등차수열의합_공식", "공식 Sn=n(a+l)/2 로 등차수열의 합", "p.182"),
        ("등비수열의합", "등비수열의 합 공식 활용", "p.182"),
        ("승수_pow", "pow() 로 거듭제곱 구하기", "p.183"),
        ("제곱근_sqrt", "sqrt() 로 제곱근 구하기", "p.183"),
    ]),
    ("11_코딩테스트_필수로직", "1.12 코딩테스트 필수로직", [
        ("1차원배열_회전_왼쪽1칸", "rotate() 로 배열 왼쪽(반시계) 1칸 회전", "p.185"),
        ("1차원배열_회전_왼쪽2칸", "rotate() 로 배열 왼쪽 2칸 회전", "p.186"),
        ("1차원배열_회전_일부구간", "배열의 일부 구간만 회전", "p.186"),
        ("1차원배열_회전_오른쪽_rbegin_rend", "rbegin/rend 로 오른쪽(시계) 방향 회전", "p.186"),
        ("rotate_동작원리", "rotate([first,last)) 의 동작 원리", "p.187"),
        ("1차원배열_회전_직접구현", "rotate() 없이 temp 로 직접 구현", "p.188"),
        ("2차원배열_회전_좌우90도", "rotate_left_90 / rotate_right_90 구현", "p.189"),
        ("2차원배열_대칭", "2차원 배열 대각선 대칭시키기", "p.191"),
        ("n진법_변환", "10진수를 n진법으로 변환", "p.192"),
    ]),
    ("12_코딩테스트_팁", "1.13 코딩테스트 팁", [
        ("전역변수_지역변수_비교", "전역변수를 사용한 간결한 코드 예", "p.193"),
        ("지역변수_배열_stack제한", "지역변수 큰 배열은 stack 제한으로 실패", "p.194"),
    ]),
    ("13_맞왜틀_팁", "1.14 맞왜틀 팁", [
        ("define_변수명_충돌회피", "bits/stdc++.h 예약된 변수명 회피(define)", "p.197"),
        ("define_이터레이터_충돌_에러예시", "define 이 sort 의 end 와 충돌하는 에러 예", "p.198"),
        ("입출력싱크_해제", "sync_with_stdio(false), cin/cout.tie(NULL)", "p.198"),
        ("실수형_연산_오차_예제", "0.1을 10번 더해도 1이 안 되는 예제", "p.200"),
        ("실수형_연산_오차_보정", "오차범위(1e-9) 기반으로 비교하기", "p.201"),
        ("실수형_연산_프레임화", "오차 비교를 프레임(함수)화 하기", "p.201"),
        ("문자열크기선언_null문자", "char 배열 크기는 널문자만큼 +1", "p.202"),
        ("버퍼플러시_endl_vs_n", "endl 과 \\n 의 버퍼플러시 차이", "p.203"),
    ]),
    ("14_자주묻는질문", "1.15 자주 묻는 질문", [
        ("bits_stdc_h_없이_iostream만", "bits/stdc++.h 없이 iostream 만으로 풀기", "p.207"),
        ("따닥따닥_입력_string변환", "따닥따닥 붙은 입력을 string 으로 받아 변환", "p.209"),
        ("따닥따닥_입력_scanf_1d", "scanf(\"%1d\", ...) 로 한자리씩 입력받기", "p.210"),
        ("따닥따닥_입력_scanf_c_공백주의", "scanf(\" %c\", ...) 로 char 입력시 공백 주의", "p.210"),
        ("따닥따닥_입력_char_cin", "char 2차원 배열을 cin 으로 바로 받기", "p.211"),
        ("char_cin_동일효과_증명", "char + cin 이 scanf %c 와 동일한 효과", "p.211"),
        ("입력끝_scanf_EOF", "scanf(...) != EOF 로 입력 끝까지 받기", "p.212"),
        ("입력끝_cin", "while(cin >> n) 으로 입력 끝까지 받기", "p.212"),
        ("process_exit_call_일곱난쟁이", "exit(0) 으로 재귀함수 도중 프로세스 종료", "p.213"),
        ("2차원배열_입력_주어진경우", "코드에 2차원 배열이 리터럴로 주어진 경우", "p.215"),
    ]),
]


def make_stub(section_title: str, item_title: str, page: str) -> str:
    return f"""// {section_title}
// {item_title} ({page})
// 《10주완성 C++ 코딩테스트》(큰돌 저)를 참고하여 아래 내용을 직접 타이핑해서 완성해보세요.

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


def make_test_stub(section_title: str, item_title: str, page: str, slug: str) -> str:
    suite = sanitize_test_name(slug)
    return f"""// {section_title}
// {item_title} ({page})
//
// 여기에 GoogleTest 테스트를 직접 작성하세요.
// main.cpp 상단 주석의 예상 입력/출력(있다면)을 참고하세요.
// main.cpp 는 자체 main() 을 갖고 있어 그대로 include 하면 충돌하니,
// 검증하고 싶은 로직은 함수로 분리해서 여기서 다시 선언/정의하거나
// 이 파일에서 필요한 로직만 옮겨와 테스트하세요.

#include <gtest/gtest.h>

TEST({suite}, TODO) {{
    // TODO: 이 항목에 대한 테스트 케이스를 작성하세요.
}}
"""


def main():
    created = 0
    skipped = 0
    test_created = 0
    test_skipped = 0
    for sec_dir, sec_title, items in SECTIONS:
        sec_path = os.path.join(ROOT, sec_dir)
        os.makedirs(sec_path, exist_ok=True)

        index_lines = [f"# {sec_title}", ""]
        for i, (slug, title, page) in enumerate(items, start=1):
            item_dir = f"{i:02d}_{slug}"
            item_path = os.path.join(sec_path, item_dir)
            os.makedirs(item_path, exist_ok=True)
            main_cpp = os.path.join(item_path, "main.cpp")
            if os.path.exists(main_cpp):
                skipped += 1
            else:
                with open(main_cpp, "w", encoding="utf-8") as f:
                    f.write(make_stub(sec_title, title, page))
                created += 1

            test_cpp = os.path.join(item_path, "test.cpp")
            if os.path.exists(test_cpp):
                test_skipped += 1
            else:
                with open(test_cpp, "w", encoding="utf-8") as f:
                    f.write(make_test_stub(sec_title, title, page, slug))
                test_created += 1

            index_lines.append(f"- `{item_dir}/main.cpp` — {title} ({page})")

        with open(os.path.join(sec_path, "README.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines) + "\n")

    print(f"main.cpp created: {created}, skipped: {skipped}")
    print(f"test.cpp created: {test_created}, skipped: {test_skipped}")


if __name__ == "__main__":
    main()
