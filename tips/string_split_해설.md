---
title: "C++ 문자열 split() 함수 완벽 해부 (라인별 주석 및 동작 추적)"
aliases:
  - string split 해설
  - C++ split 함수
tags:
  - cpp
  - string
  - split
  - coding-test
  - stoneCpp
created: 2026-10-23
status: completed
---

# 🔪 C++ 문자열 `split()` 함수 완벽 해부 (`12_string_split_콤마`)

> [!info] 왜 C++에서는 `split()`을 직접 만들어 쓸까?
> Python의 `.split()`, Java의 `.split()`, JavaScript의 `.split()`과 달리 C++ 표준 라이브러리(STL)에는 문자열을 특정 구분자(`delimiter`)로 쪼개어 배열(`vector`)로 반환하는 기본 함수가 없습니다.  
> 따라서 코딩테스트에서는 `string::find()`와 `string::substr()`을 조합한 아래 패턴을 손에 익혀 두고 기계적으로 작성할 수 있어야 합니다.

- 원본 소스: [`12_string_split_콤마/main.cpp`](../practice/stone-lecture/01_문법_STL/03_타입과_타입변환/12_string_split_콤마/main.cpp)

---

## 1. 라인별 주석 코드 (Line-by-Line Annotation)

```cpp
#include <bits/stdc++.h> // 코딩테스트용 만능 헤더 (iostream, string, vector 등 모든 표준 라이브러리 포함)
using namespace std;     // std:: 접두사 생략 (std::string -> string, std::vector -> vector)

// [함수 선언부]
// - 반환 타입: vector<string> (쪼개진 문자열 조각들을 동적 배열에 담아 반환)
// - const string& input: 원본 문자열을 복사하지 않고 참조(&)로 받아 메모리/시간 절약 + 원본 수정 방지(const)
// - string delimiter: 기준이 되는 구분자 문자열 (예: ",", "->", " ")
vector<string> split(const string& input, string delimiter) {

    // 1. 쪼개진 문자열 토큰(조각)들을 차곡차곡 담을 결과 바구니(동적 배열) 생성
    vector<string> result;

    // 2. 잘라낼 부분 문자열의 '시작 인덱스'를 0(맨 앞)으로 초기화
    //    (auto는 우변의 리터럴 0을 보고 int로 추론됨, 엄밀히는 size_t/string::size_type 역할)
    auto start = 0;

    // 3. input의 맨 처음부터 탐색하여 첫 번째 구분자(delimiter)가 등장하는 '시작 인덱스'를 찾음
    //    - 찾으면: 해당 위치의 인덱스(size_t) 반환
    //    - 못 찾으면: string::npos 반환
    auto end = input.find(delimiter);

    // 4. 구분자를 더 이상 찾지 못할 때까지(end가 string::npos가 아닐 동안) 반복
    //    string::npos는 "찾지 못함(no position)"을 뜻하는 특수 상수(-1, size_t 최대값)
    while (end != string::npos) {

        // 5. [핵심] start 위치부터 (end - start) 길이만큼 부분 문자열을 잘라내어 result에 추가
        //    주의: substr(시작위치, 끝위치)가 아니라 substr(시작위치, 잘라낼_길이)임!
        result.push_back(input.substr(start, end - start));

        // 6. 다음 조각의 시작 위치(start)를 '방금 찾은 구분자 바로 뒤'로 이동
        //    + 1 이 아니라 + delimiter.size()를 하는 이유:
        //    "," 처럼 1글자뿐만 아니라 "->" 처럼 2글자 이상인 구분자도 정확히 건너뛰기 위함
        start = end + delimiter.size();

        // 7. 갱신된 start 위치부터 시작해서 '다음 구분자'의 위치를 다시 탐색
        //    input.find(찾을문자열, 탐색시작위치) 오버로딩 함수 사용
        end = input.find(delimiter, start);
    }

    // 8. [마지막 조각 처리] 반복문이 끝났다는 것은 마지막 구분자 뒤편에 남은 문자열이 있다는 뜻!
    //    input.substr(start)처럼 두 번째 인자(길이)를 생략하면 start부터 문자열 끝까지 전부 잘라냄
    result.push_back(input.substr(start));

    // 9. 완성된 문자열 조각 배열을 호출한 곳으로 반환
    return result;
}

int main() {
    // 테스트할 원본 문자열 준비
    string str = "apple,banana,orange,grape";

    // str을 "," 기준으로 쪼개어 fruits 벡터에 저장
    vector<string> fruits = split(str, ",");

    // 범위 기반 for문(Range-based for loop)으로 결과 출력
    // const string& 로 받아 각 요소를 복사 없이 읽기 전용 참조로 순회
    for (const string& fruit : fruits) {
        cout << fruit << endl; // 각 과일 이름 출력 후 줄바꿈
    }

    return 0; // 프로그램 정상 종료
}
```

---

## 2. 핵심 문법 & 디테일 짚어보기

### ① 왜 `input.substr(start, end - start)` 인가요?
C++의 [`std::string::substr`](https://en.cppreference.com/w/cpp/string/basic_string/substr) 시그니처는 다음과 같습니다:
```cpp
string substr(size_type pos = 0, size_type count = npos) const;
```
- 첫 번째 인자(`pos`): 시작 인덱스 (`start`)
- 두 번째 인자(`count`): 끝 인덱스가 아니라 잘라낼 글자 수(길이) 입니다!
- 구간 `[start, end)`(즉, `start` 이상 `end` 미만)의 길이는 हमेशा `end - start` 입니다.
  - 예: `"apple,banana"`에서 `start = 6` (`'b'`), `end = 12` (다음 콤마 위치)일 때 길이는 `12 - 6 = 6`글자(`"banana"`).

### ② 왜 `start = end + delimiter.size()` 인가요?
- 만약 구분자가 `","` (길이 1)라면 `end + 1`과 같지만, 다음 예제인 [`13_string_split_화살표`](../practice/stone-lecture/01_문법_STL/03_타입과_타입변환/13_string_split_화살표/main.cpp)처럼 구분자가 `"->"` (길이 2)인 경우에도 코드를 단 한 줄도 수정하지 않고 그대로 재사용하기 위해서입니다.

### ③ 왜 `while` 루프 밖에서 `result.push_back(input.substr(start))`를 한 번 더 하나요?
- `"apple,banana,orange,grape"`에는 콤마(`,`)가 3개 있고, 단어가 4개 있습니다.
- `while (end != string::npos)` 루프는 콤마를 찾을 때마다 앞쪽 단어를 하나씩 넣으므로 루프 안에서는 `"apple"`, `"banana"`, `"orange"` 3개만 들어갑니다.
- 마지막 `"grape"` 뒤에는 콤마가 없어서 `end`가 `string::npos`가 되며 루프를 탈출합니다. 따라서 루프 직후에 `start`(마지막 콤마 다음 위치)부터 끝까지 남은 `"grape"`를 챙겨 넣어야 합니다.

---

## 3. 단계별 동작 추적 (Dry Run)

입력 문자열 `input = "apple,banana,orange,grape"`, `delimiter = ","` (`size = 1`)일 때의 인덱스 배치입니다.

```text
인덱스:  0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
문자열:  a p p l e , b a n a n  a  ,  o  r  a  n  g  e  ,  g  r  a  p  e
                  ^               ^                    ^
                콤마(5)          콤마(12)             콤마(19)
```

| 단계 | `start` | `end` (`find` 결과) | `while` 조건 (`end != npos`) | 잘라낼 길이 (`end - start`) | `substr` 추출 결과 | 실행 후 `result` 상태 | 다음 `start` (`end + 1`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| 초기화 | `0` | `5` | - | - | - | `[]` | - |
| 루프 1회차 | `0` | `5` | `true` | `5 - 0 = 5` | `"apple"` | `["apple"]` | `5 + 1 = 6` |
| 루프 2회차 | `6` | `12` | `true` | `12 - 6 = 6` | `"banana"` | `["apple", "banana"]` | `12 + 1 = 13` |
| 루프 3회차 | `13` | `19` | `true` | `19 - 13 = 6` | `"orange"` | `["apple", "banana", "orange"]` | `19 + 1 = 20` |
| 루프 탈출 | `20` | `string::npos` | `false` (종료) | - | - | `["apple", "banana", "orange"]` | - |
| 루프 직후 (마무리) | `20` | - | - | 끝까지 (`substr(20)`) | `"grape"` | `["apple", "banana", "orange", "grape"]` | - |

---

## 4. 자주 하는 실수 체크리스트

> [!warning] 직접 타이핑할 때 주의할 점
> 1. `substr` 두 번째 인자 실수: `input.substr(start, end)`라고 쓰면 `end`를 '끝 인덱스'가 아니라 '글자 수'로 인식해서 문자열이 엉뚱하게 길게 잘립니다. 반드시 `end - start`!
> 2. `find` 두 번째 인자 누락: `while`문 마지막 줄에서 `end = input.find(delimiter);`처럼 두 번째 인자 `start`를 빼먹으면 매번 0번 인덱스부터 다시 찾아 무한 루프에 빠집니다. 반드시 `input.find(delimiter, start)`!
> 3. 주석 `@snippet` 오타 주의: [`12_string_split_콤마/main.cpp`](../practice/stone-lecture/01_문법_STL/03_타입과_타입변환/12_string_split_콤마/main.cpp) 25번째 줄 주석에는 `result.push_back(input.substr(start);`처럼 닫는 소괄호 `)` 하나가 빠져 있으니, 실제 코드(39번째 줄)처럼 `result.push_back(input.substr(start));`로 괄호 짝을 맞춰야 합니다.
