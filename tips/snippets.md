# 🧩 handcrafted-cpp 코드 스니펫 레지스트리

- 전체: 5개 (`VERIFIED` 0 · `PENDING_REVIEW` 5 · `OUTDATED` 0)

## [PENDING_REVIEW] `solve_kata` — 01_history_and_standards

- 파일 위치: `practice/linux/01_tlpi_system_programming/01_history_and_standards/main.cpp:1`
- 코드 SHA-256: `833ca12e4bcef62521711145277669b5afe7589a0d44a5a97b51daa24868cf8b`
- 검증 정보: `미검증` (-)

```cpp
#include <iostream>

int solve_kata() {
    return 42;
}

int main() {
    std::cout << solve_kata() << std::endl;
    return 0;
}
```

## [PENDING_REVIEW] `solve_kata` — 02_fundamental_concepts

- 파일 위치: `practice/linux/01_tlpi_system_programming/02_fundamental_concepts/main.cpp:1`
- 코드 SHA-256: `833ca12e4bcef62521711145277669b5afe7589a0d44a5a97b51daa24868cf8b`
- 검증 정보: `미검증` (-)

```cpp
#include <iostream>

int solve_kata() {
    return 42;
}

int main() {
    std::cout << solve_kata() << std::endl;
    return 0;
}
```

## [PENDING_REVIEW] `solve_kata` — 56_sockets_introduction

- 파일 위치: `practice/linux/01_tlpi_system_programming/56_sockets_introduction/main.cpp:1`
- 코드 SHA-256: `833ca12e4bcef62521711145277669b5afe7589a0d44a5a97b51daa24868cf8b`
- 검증 정보: `미검증` (-)

```cpp
#include <iostream>

int solve_kata() {
    return 42;
}

int main() {
    std::cout << solve_kata() << std::endl;
    return 0;
}
```

## [PENDING_REVIEW] `solve_kata` — 58_sockets_fundamentals_of_tcp_ip

- 파일 위치: `practice/linux/01_tlpi_system_programming/58_sockets_fundamentals_of_tcp_ip/main.cpp:1`
- 코드 SHA-256: `833ca12e4bcef62521711145277669b5afe7589a0d44a5a97b51daa24868cf8b`
- 검증 정보: `미검증` (-)

```cpp
#include <iostream>

int solve_kata() {
    return 42;
}

int main() {
    std::cout << solve_kata() << std::endl;
    return 0;
}
```

## [PENDING_REVIEW] `split` — 문자열을 delimiter 기준으로 쪼개는 함수

- 파일 위치: `practice/stone-lecture/01_문법_STL/03_타입과_타입변환/12_string_split_콤마/main.cpp:36`
- 코드 SHA-256: `cf3334986b04b1ff637bc3b89ce88c1cc16955d3d40df4b8ef39aeb06fb43055`
- 검증 정보: `미검증` (-)

```cpp
vector<string> split(const string& input, string delimiter) {
    vector<string> result;
    auto start = 0;
    auto end = input.find(delimiter);
    while (end != string::npos) {
        result.push_back(input.substr(start, end - start));
        start = end + delimiter.size();
        end = input.find(delimiter, start);
    }
    result.push_back(input.substr(start));
    return result;
}

int main() {
    string str = "apple,banana,orange,grape";
    vector<string> fruits = split(str,",");

    for (const string& fruit : fruits) {
        cout << fruit << endl;
    }

    return 0;
}
```
