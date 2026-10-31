#!/usr/bin/env python3
"""외부 라이브러리(헤더/구현) 내비게이션 인덱스 생성기.

프로젝트가 의존하는 외부 코드(C++ 표준 라이브러리 libc++, C/POSIX 시스템 헤더,
GoogleTest)의 실제 소스 위치를 전수 조사하여 루트의 EXTERNAL_LIBRARIES.md 로 출력한다.
링크를 클릭하면 해당 소스(헤더/구현)로 바로 이동할 수 있다.

사용법:
    python3 scripts/generate_external_libs_index.py
"""

import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "EXTERNAL_LIBRARIES.md"
CXX = "clang++"
STD = "c++17"

# ---------------------------------------------------------------------------
# 환경 탐지
# ---------------------------------------------------------------------------


def run(cmd, inp=None):
    return subprocess.run(cmd, input=inp, capture_output=True, text=True)


def detect_search_dirs():
    res = run([CXX, f"-std={STD}", "-E", "-x", "c++", "/dev/null", "-v"])
    dirs, on = [], False
    for line in res.stderr.splitlines():
        if line.startswith("#include <...> search starts here"):
            on = True
            continue
        if line.startswith("End of search list"):
            break
        if on:
            dirs.append(line.strip().replace(" (framework directory)", ""))
    return dirs


SEARCH_DIRS = detect_search_dirs()
SDK = Path(run(["xcrun", "--show-sdk-path"]).stdout.strip())
SDK_INC = SDK / "usr" / "include"
V1 = SDK_INC / "c++" / "v1"
CLANG_VER = run([CXX, "--version"]).stdout.splitlines()[0]
CLANG_RES_INC = next((Path(d) for d in SEARCH_DIRS if "/clang/" in d), None)

GTEST_ROOT = None
if (REPO / ".opensource" / "googletest").exists():
    GTEST_ROOT = (REPO / ".opensource" / "googletest").resolve()
else:
    for cand in ("cmake-build-debug", "cmake-build-practice"):
        p = REPO / cand / "_deps" / "googletest-src"
        if p.exists():
            GTEST_ROOT = p
            break
GTEST_LIB_DIR = None
for cand in ("cmake-build-debug", "cmake-build-practice"):
    lib_cand = REPO / cand / "lib"
    if lib_cand.exists():
        GTEST_LIB_DIR = lib_cand
        break


LINK_DIR = REPO / "external_libs"
# (실제 경로, 심볼릭 링크 이름) — 구체적인(깊은) 경로가 먼저 와야 한다.
LINK_MAP = []


def build_symlinks():
    """저장소 안에 외부 라이브러리로의 심볼릭 링크를 만들어 짧은 상대 링크를 가능하게 한다."""
    cands = [
        (V1, "libcxx"),
        (CLANG_RES_INC, "clang-include"),
        (SDK_INC, "sdk-include"),
        (SDK / "usr" / "lib", "sdk-lib"),
        (SDK, "sdk"),
        (Path("/Library/Developer/CommandLineTools/usr/include"), "clt-include"),
        (GTEST_ROOT, "googletest"),
    ]
    LINK_DIR.mkdir(exist_ok=True)
    for target, name in cands:
        if target is None or not Path(target).exists():
            continue
        lnk = LINK_DIR / name
        if lnk.is_symlink() or lnk.exists():
            if lnk.is_symlink() and Path(os.readlink(lnk)) == Path(target):
                pass
            else:
                lnk.unlink()
                lnk.symlink_to(target)
        else:
            lnk.symlink_to(target)
        LINK_MAP.append((Path(target), lnk))
    LINK_MAP.sort(key=lambda t: -len(str(t[0])))
    (LINK_DIR / "README.md").write_text(
        "# external_libs\n\n"
        "`scripts/generate_external_libs_index.py` 가 만드는 **심볼릭 링크 모음**입니다 (git 제외 대상).\n"
        "[EXTERNAL_LIBRARIES.md](../EXTERNAL_LIBRARIES.md) 의 링크가 이 경로를 통해 시스템 헤더/GoogleTest 소스로 이동합니다.\n\n"
        + "\n".join(f"- `{l.name}` → `{t}`" for t, l in sorted(LINK_MAP, key=lambda x: x[1].name))
        + "\n",
        encoding="utf-8",
    )


def link_path(path: Path) -> str:
    """파일 경로 -> 마크다운 링크 URL (external_libs 심볼릭 링크 우선, 저장소 내부는 상대경로)."""
    path = Path(path)
    for target, lnk in LINK_MAP:
        try:
            rel = path.relative_to(target)
        except ValueError:
            continue
        full = lnk.relative_to(REPO) / rel
        return quote(str(full).replace(os.sep, "/"), safe="/+")
    try:
        rel = path.relative_to(REPO)
        return quote(str(rel).replace(os.sep, "/"), safe="/+")
    except ValueError:
        return "file://" + quote(str(path), safe="/+")


def L(text, path, line=None):
    url = link_path(path)
    if line:
        url += f"#L{line}"
    return f"[{text}]({url})"


def short(path: Path) -> str:
    """링크 표시용 짧은 경로."""
    path = Path(path)
    for base in (V1, SDK_INC, CLANG_RES_INC, GTEST_ROOT, REPO):
        if base is None:
            continue
        try:
            return str(path.relative_to(base))
        except ValueError:
            continue
    return str(path)


# ---------------------------------------------------------------------------
# 프로젝트가 사용하는 #include 수집
# ---------------------------------------------------------------------------

INC_RE = re.compile(r"^\s*#\s*include\s*<([^>]+)>", re.M)
USED = defaultdict(set)  # header -> {파일 상대경로}


def scan_project_includes():
    p_dir = REPO / "practice" if (REPO / "practice").exists() else REPO / "stone"
    roots = [p_dir, REPO / "main.cpp"]
    exts = {".cpp", ".c", ".h", ".hpp", ".md"}
    for root in roots:
        files = [root] if root.is_file() else root.rglob("*")
        for f in files:
            if f.suffix not in exts or not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for h in INC_RE.findall(text):
                USED[h.strip()].add(str(f.relative_to(REPO)))


# ---------------------------------------------------------------------------
# 헤더 해결 + 트랜지티브 클로저 (clang -H)
# ---------------------------------------------------------------------------

RESOLVED = {}  # header -> Path | None
CLOSURE = {}  # header -> set(Path)


def resolve_header(h: str):
    extra = []
    if GTEST_ROOT:
        extra = [f"-I{GTEST_ROOT / 'googletest/include'}", f"-I{GTEST_ROOT / 'googlemock/include'}"]
    res = run(
        [CXX, f"-std={STD}", *extra, "-E", "-H", "-x", "c++", "-o", os.devnull, "-"],
        inp=f"#include <{h}>\n",
    )
    if res.returncode != 0:
        return None, set()
    files, first = set(), None
    for line in res.stderr.splitlines():
        m = re.match(r"^(\.+) (/.*)$", line)
        if not m:
            continue
        p = Path(m.group(2))
        if p.suffix == ".json":  # SDKSettings.json 등 depfile 항목 제외
            continue
        if first is None and len(m.group(1)) == 1:
            first = p
        files.add(p)
    return first, files


# ---------------------------------------------------------------------------
# 분류
# ---------------------------------------------------------------------------

CXX_C_WRAPPERS = {
    "cassert", "cctype", "cerrno", "cfenv", "cfloat", "cinttypes", "climits",
    "clocale", "cmath", "csetjmp", "csignal", "cstdarg", "cstdbool", "cstddef",
    "cstdint", "cstdio", "cstdlib", "cstring", "ctime", "cuchar", "cwchar",
    "cwctype",
}
C_STD = {
    "assert.h", "ctype.h", "errno.h", "float.h", "limits.h", "locale.h",
    "math.h", "setjmp.h", "signal.h", "stdarg.h", "stddef.h", "stdio.h",
    "stdlib.h", "string.h", "time.h", "stdint.h", "inttypes.h", "stdbool.h",
    "wchar.h", "wctype.h", "iso646.h", "stdalign.h", "stdatomic.h",
    "stdnoreturn.h", "tgmath.h", "complex.h", "fenv.h", "uchar.h", "threads.h",
}
LINUX_ONLY = {
    "sys/epoll.h", "sys/inotify.h", "sys/eventfd.h", "sys/timerfd.h",
    "sys/signalfd.h", "sys/sendfile.h", "sys/prctl.h", "sys/syscall.h",
    "sys/capability.h", "sys/fsuid.h", "sys/vfs.h", "sys/xattr.h",
    "linux/futex.h", "bits/stdc++.h", "malloc.h", "features.h",
}


WINDOWS_ONLY = {"conio.h", "direct.h", "windows.h", "io.h", "process.h", "dos.h"}


def classify(h: str, resolved):
    if h in WINDOWS_ONLY:
        return "Windows/비표준 전용 (macOS 미존재)"
    if h.startswith(("gtest/", "gmock/")):
        return "GoogleTest"
    if resolved is None:
        return "Linux/GCC 전용 (macOS 미존재)"
    if str(resolved).startswith("/Library/Developer/CommandLineTools/usr/include"):
        return "비표준 GCC 헤더 (CLT 호환 shim)"
    if h in CXX_C_WRAPPERS:
        return "C++ 표준 (C 래퍼)"
    if h in C_STD:
        return "C 표준"
    try:
        resolved.relative_to(V1)
        return "C++ 표준 (libc++)"
    except ValueError:
        pass
    if CLANG_RES_INC and str(resolved).startswith(str(CLANG_RES_INC)):
        return "C 표준 (clang 내장)"
    return "POSIX / Darwin 시스템"


def underlying_c_header(h: str, resolved):
    """libc++ 가 감싸는 C 헤더(stdio.h 등)의 실제 SDK/clang 헤더 경로를 찾는다."""
    if resolved is None:
        return None
    name = h
    if h in CXX_C_WRAPPERS:
        name = h[1:] + ".h"
    elif h not in C_STD:
        return None
    for base in (SDK_INC, CLANG_RES_INC):
        if base and (Path(base) / name).exists():
            return Path(base) / name
    return None



IMPL_NOTE = {
    "C++ 표준 (libc++)": "템플릿/인라인은 하위 `__*/` 헤더에 구현, 비템플릿은 `libc++.dylib` ([§6](#6-구현체-바이너리와-업스트림-소스))",
    "C++ 표준 (C 래퍼)": "C 헤더를 감싸는 래퍼 → `libSystem` ([§6](#6-구현체-바이너리와-업스트림-소스))",
    "C 표준": "선언은 헤더, 구현은 `libSystem` ([§6](#6-구현체-바이너리와-업스트림-소스))",
    "C 표준 (clang 내장)": "컴파일러 내장 헤더 (구현 없음/매크로·타입)",
    "POSIX / Darwin 시스템": "선언은 헤더, 구현은 `libSystem`/`libpthread` ([§6](#6-구현체-바이너리와-업스트림-소스))",
    "GoogleTest": "GoogleTest 소스 ([§7](#7-googletest-v1152))",
    "Linux/GCC 전용 (macOS 미존재)": "macOS 에서는 `#if defined(__linux__)` 분기로 우회 ([§8](#8-리눅스-전용-헤더와-macos-대체))",
    "Windows/비표준 전용 (macOS 미존재)": "Windows(MSVC) 전용 비표준 헤더 — 교재 원문 코드에만 등장, macOS/Linux 에서는 사용 불가",
    "비표준 GCC 헤더 (CLT 호환 shim)": "Apple CLT 가 제공하는 `<bits/stdc++.h>` 호환 shim — 표준 헤더들을 한꺼번에 include (구현 없음)",
}

# ---------------------------------------------------------------------------
# 심볼 정의 위치 찾기
# ---------------------------------------------------------------------------

_file_cache = {}


def read_lines(p: Path):
    if p not in _file_cache:
        try:
            _file_cache[p] = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            _file_cache[p] = []
    return _file_cache[p]


def libcxx_files():
    # 하위 구현 헤더(__*/...)를 우선하고, 그다음 공개 헤더 순으로 탐색
    # __cxx03/ 는 -std=c++03 전용 동결 사본이므로 C++17 심볼 탐색에서 제외
    files = sorted(V1.rglob("*"), key=lambda p: (0 if p.parent != V1 else 1, str(p)))
    return [p for p in files if p.is_file() and "__cxx03" not in p.relative_to(V1).parts]


def find_in(files, pattern, hint=None):
    """files 에서 pattern 첫 매치 (파일, 줄). /* ... */ 블록 주석(헤더 상단 synopsis) 안은 건너뛴다."""
    rx = re.compile(pattern)
    if hint:
        files = sorted(files, key=lambda p: 0 if str(p).endswith(hint) else 1)
    for f in files:
        in_comment = False
        for i, line in enumerate(read_lines(f), 1):
            stripped = line.strip()
            if in_comment:
                if "*/" in stripped:
                    in_comment = False
                continue
            if stripped.startswith("/*") and "*/" not in stripped:
                in_comment = True
                continue
            if rx.search(line):
                return f, i
    return None


def type_rx(name):
    pre = r"(?:[A-Z_][A-Z0-9_]*(?:\([^)]*\))?\s+)*"
    return rf"^(?:class|struct)\s+{pre}{re.escape(name)}\s*(?:final\s*)?(?::|\{{|$)"


def spec_rx(name):
    """템플릿 특수화 형태 (예: class function<_Rp(_ArgTypes...)>)"""
    pre = r"(?:[A-Z_][A-Z0-9_]*(?:\([^)]*\))?\s+)*"
    return rf"^(?:class|struct)\s+{pre}{re.escape(name)}\s*<"


def alias_rx(name):
    return rf"^(?:using\s+{re.escape(name)}\s*=|typedef\s+.*\b{re.escape(name)};)"


def func_rx(name):
    n = re.escape(name)
    # 반환형과 같은 줄 / 반환형이 윗줄에 있고 이름이 줄 맨 앞에 오는 libc++ 스타일,
    # 그리고 [[__nodiscard__]] 같은 속성 접두 모두 허용
    tok = r"(?:\[\[[^\]]*\]\]\s+|[\w:]+(?:<[^<>]*>)?[\s\*&]+)"
    return rf"^(?:{tok}+{n}\s*\(|{n}\s*\()"


PUBLIC_HEADER = {
    "basic_string": "string", "string": "string", "to_string": "string", "getline": "string",
    "priority_queue": "queue", "pair": "utility", "move": "utility", "forward": "utility",
    "swap": "utility", "basic_string_view": "string_view", "unique_ptr": "memory",
    "shared_ptr": "memory", "weak_ptr": "memory", "make_unique": "memory",
    "make_shared": "memory", "function": "functional", "promise": "future",
    "basic_ostream": "ostream", "basic_istream": "istream", "basic_ifstream": "fstream",
    "basic_stringstream": "sstream", "path": "filesystem", "duration": "chrono",
    "mersenne_twister_engine": "random", "sort": "algorithm", "find": "algorithm",
    "lower_bound": "algorithm", "accumulate": "numeric",
}

HINTS = {
    "move": "__utility/move.h",
    "forward": "__utility/forward.h",
    "swap": "__utility/swap.h",
    "find": "__algorithm/find.h",
    "sort": "__algorithm/sort.h",
    "lower_bound": "__algorithm/lower_bound.h",
    "accumulate": "__numeric/accumulate.h",
    "getline": "__string/string.h",
    "to_string": "__string/to_string.h",
    "make_unique": "__memory/unique_ptr.h",
    "make_shared": "__memory/shared_ptr.h",
}


LIBCXX_SYMBOLS = [
    # (표시, 종류, 탐색 이름)
    ("std::vector", "type", "vector"),
    ("std::basic_string (std::string)", "type", "basic_string"),
    ("std::string 별칭", "alias", "string"),
    ("std::map", "type", "map"),
    ("std::unordered_map", "type", "unordered_map"),
    ("std::set", "type", "set"),
    ("std::unordered_set", "type", "unordered_set"),
    ("std::list", "type", "list"),
    ("std::deque", "type", "deque"),
    ("std::array", "type", "array"),
    ("std::stack", "type", "stack"),
    ("std::queue", "type", "queue"),
    ("std::priority_queue", "type", "priority_queue"),
    ("std::pair", "type", "pair"),
    ("std::tuple", "type", "tuple"),
    ("std::optional", "type", "optional"),
    ("std::variant", "type", "variant"),
    ("std::any", "type", "any"),
    ("std::string_view (basic_string_view)", "type", "basic_string_view"),
    ("std::unique_ptr", "type", "unique_ptr"),
    ("std::shared_ptr", "type", "shared_ptr"),
    ("std::weak_ptr", "type", "weak_ptr"),
    ("std::function", "spec", "function"),
    ("std::thread", "type", "thread"),
    ("std::mutex", "type", "mutex"),
    ("std::condition_variable", "type", "condition_variable"),
    ("std::atomic", "type", "atomic"),
    ("std::future", "type", "future"),
    ("std::promise", "type", "promise"),
    ("std::basic_ostream (cout)", "type", "basic_ostream"),
    ("std::basic_istream (cin)", "type", "basic_istream"),
    ("std::basic_ifstream", "type", "basic_ifstream"),
    ("std::basic_stringstream", "type", "basic_stringstream"),
    ("std::filesystem::path", "type", "path"),
    ("std::chrono::duration", "type", "duration"),
    ("std::mt19937 (mersenne_twister_engine)", "type", "mersenne_twister_engine"),
    ("std::bitset", "type", "bitset"),
    ("std::exception", "type", "exception"),
    ("std::sort", "func", "sort"),
    ("std::find", "func", "find"),
    ("std::lower_bound", "func", "lower_bound"),
    ("std::accumulate", "func", "accumulate"),
    ("std::move", "func", "move"),
    ("std::forward", "func", "forward"),
    ("std::swap", "func", "swap"),
    ("std::make_unique", "func", "make_unique"),
    ("std::make_shared", "func", "make_shared"),
    ("std::to_string", "func", "to_string"),
    ("std::getline", "func", "getline"),
]

POSIX_FUNCS = [
    "open", "read", "write", "close", "lseek", "dup2", "pipe", "fork",
    "execve", "waitpid", "_exit", "getpid", "kill", "sigaction",
    "sigprocmask", "alarm", "pthread_create", "pthread_join",
    "pthread_mutex_lock", "pthread_cond_wait", "mmap", "munmap", "mprotect",
    "sbrk", "socket", "bind", "listen", "accept", "connect", "send", "recv",
    "setsockopt", "select", "poll", "fcntl", "stat", "mkfifo", "shm_open",
    "sem_open", "mq_open", "printf", "malloc", "free", "memcpy", "strlen",
    "qsort", "getenv", "fopen", "fread", "strerror", "perror", "clock_gettime",
]
POSIX_HEADER_DIRS = ["", "sys", "pthread", "arpa", "netinet", "malloc"]

GTEST_SYMBOLS = [
    ("TEST", r"#\s*define\s+TEST\s*\("),
    ("TEST_F", r"#\s*define\s+TEST_F\s*\("),
    ("TEST_P", r"#\s*define\s+TEST_P\s*\("),
    ("TYPED_TEST", r"#\s*define\s+TYPED_TEST\s*\("),
    ("INSTANTIATE_TEST_SUITE_P", r"#\s*define\s+INSTANTIATE_TEST_SUITE_P\s*\("),
    ("EXPECT_EQ", r"#\s*define\s+EXPECT_EQ\s*\("),
    ("ASSERT_EQ", r"#\s*define\s+ASSERT_EQ\s*\("),
    ("EXPECT_TRUE", r"#\s*define\s+EXPECT_TRUE\s*\("),
    ("EXPECT_NEAR", r"#\s*define\s+EXPECT_NEAR\s*\("),
    ("EXPECT_STREQ", r"#\s*define\s+EXPECT_STREQ\s*\("),
    ("EXPECT_THROW", r"#\s*define\s+EXPECT_THROW\s*\("),
    ("EXPECT_DEATH", r"#\s*define\s+EXPECT_DEATH\s*\("),
    ("SUCCEED", r"#\s*define\s+SUCCEED\s*\("),
    ("FAIL", r"#\s*define\s+FAIL\s*\("),
    ("RUN_ALL_TESTS", r"^inline\s+int\s+RUN_ALL_TESTS\s*\("),
    ("testing::Test (fixture 베이스)", r"^class\s+GTEST_API_\s+Test\b"),
    ("testing::InitGoogleTest", r"GTEST_API_\s+void\s+InitGoogleTest\(int\*"),
    ("testing::Environment", r"^class\s+(?:GTEST_API_\s+)?Environment\b"),
]


def collect_dir(path: Path, patterns=("*",), recursive=False):
    it = path.rglob if recursive else path.glob
    out = []
    for pat in patterns:
        out.extend(p for p in it(pat) if p.is_file())
    return sorted(set(out))


# ---------------------------------------------------------------------------
# 마크다운 생성
# ---------------------------------------------------------------------------


def dot_join(links):
    return " · ".join(links)


def main():
    build_symlinks()
    scan_project_includes()

    # --- 사용 헤더 해결 ---
    headers = sorted(USED.keys())
    closure_all = set()
    for h in headers:
        first, files = resolve_header(h)
        RESOLVED[h] = first
        CLOSURE[h] = files
        closure_all |= files

    out = []
    w = out.append

    w("# 외부 라이브러리 소스 내비게이션 인덱스")
    w("")
    w("> ⚙️ **이 문서는 자동 생성됩니다.** 환경/라이브러리 버전이 바뀌면 아래 명령으로 재생성하세요.")
    w(">")
    w("> ```bash")
    w("> python3 scripts/generate_external_libs_index.py")
    w("> ```")
    w(">")
    w("> - 링크를 클릭하면 해당 **헤더(선언/템플릿 구현)** 또는 **구현 소스(.cc)** 로 바로 이동합니다.")
    w("> - 저장소 내부 파일은 상대 경로, 시스템/SDK 파일은 `file://` 절대 경로 링크입니다.")
    w("> - AI 에이전트는 §1(탐색 순서) → §2(사용 헤더) → §3(심볼) 순으로 따라가면 정의 위치를 즉시 찾을 수 있습니다.")
    w("")

    # ---- 목차 ----
    w("## 목차")
    w("")
    for t in [
        "0. [환경 요약](#0-환경-요약)",
        "1. [헤더 탐색 순서](#1-헤더-탐색-순서-include-search-path)",
        "2. [프로젝트가 실제 사용하는 헤더](#2-프로젝트가-실제-사용하는-헤더)",
        "3. [심볼 → 정의 위치 빠른 찾기](#3-심볼--정의-위치-빠른-찾기)",
        "4. [C++ 표준 라이브러리(libc++) 공개 헤더 전체](#4-c-표준-라이브러리libc-공개-헤더-전체)",
        "5. [C 표준 / POSIX 시스템 헤더](#5-c-표준--posix-시스템-헤더)",
        "6. [구현체 바이너리와 업스트림 소스](#6-구현체-바이너리와-업스트림-소스)",
        "7. [GoogleTest (v1.15.2)](#7-googletest-v1152)",
        "8. [리눅스 전용 헤더와 macOS 대체](#8-리눅스-전용-헤더와-macos-대체)",
        "9. [프로젝트 빌드 글루 (내부 소스)](#9-프로젝트-빌드-글루-내부-소스)",
        "10. [사용 헤더의 트랜지티브 include 클로저](#10-사용-헤더의-트랜지티브-include-클로저)",
        "11. [부록: libc++ 내부 구현 헤더 전체](#11-부록-libc-내부-구현-헤더-전체)",
    ]:
        w(f"- {t}")
    w("")

    # ---- 0 ----
    w("## 0. 환경 요약")
    w("")
    libcxx_ver = ""
    cfg = V1 / "__config"
    for line in read_lines(cfg):
        m = re.match(r"#\s*define _LIBCPP_VERSION (\d+)", line)
        if m:
            v = m.group(1).zfill(6)
            libcxx_ver = f"{int(v[:2])}.{int(v[2:4])}.{int(v[4:])} (`_LIBCPP_VERSION {m.group(1)}`)"
            break
    gtest_ver = "v1.15.2 (FetchContent)"
    w("| 항목 | 값 |")
    w("|---|---|")
    w(f"| **C++ 표준** | **C++17** — `set(CMAKE_CXX_STANDARD 17)` ({L('CMakeLists.txt', REPO / 'CMakeLists.txt', 4)}), `-std=c++17` ({L('run.sh', REPO / 'scripts/run.sh')}, {L('linux_run.sh', REPO / 'scripts/linux_run.sh')}) |")
    w(f"| 컴파일러 | {CLANG_VER} |")
    w(f"| 표준 라이브러리 | LLVM **libc++** {libcxx_ver} — 헤더 디렉터리 {L(str(V1), V1)} |")
    w(f"| SDK 루트 | {L(str(SDK), SDK)} |")
    w(f"| C/POSIX 헤더 | {L(str(SDK_INC), SDK_INC)} |")
    if GTEST_ROOT:
        w(f"| GoogleTest | {gtest_ver} — 소스 {L('googletest-src', GTEST_ROOT)} |")
    else:
        w(f"| GoogleTest | {gtest_ver} — **빌드 디렉터리 미구성** (CMake 구성 후 재생성 필요) |")
    w(f"| 링크 라이브러리 | `libc++`, `libSystem`, `libpthread` ({L('usr/lib/*.tbd', SDK / 'usr/lib')}), GoogleTest `libgtest`/`libgtest_main` |")
    w("")

    # ---- 1 ----
    w("## 1. 헤더 탐색 순서 (include search path)")
    w("")
    w(f"`{CXX} -std={STD}` 가 `#include <...>` 를 찾는 순서입니다 (위에서부터 먼저 발견되는 파일이 사용됨).")
    w("")
    w("| 순서 | 디렉터리 | 역할 |")
    w("|---|---|---|")
    for i, d in enumerate(SEARCH_DIRS, 1):
        if d.endswith("c++/v1"):
            role = "C++ 표준 라이브러리 (libc++) 공개/내부 헤더"
        elif "/clang/" in d:
            role = "컴파일러 내장 헤더 (`stdint.h`, `stddef.h`, `stdarg.h`, intrinsics)"
        elif d.endswith("SDKs/MacOSX.sdk/usr/include"):
            role = "C 표준 + POSIX + Darwin 시스템 헤더"
        elif "System/Library" in d:
            role = "macOS Framework 헤더"
        else:
            role = "툴체인 보조 헤더"
        w(f"| {i} | {L(d, Path(d))} | {role} |")
    if GTEST_ROOT:
        w(f"| (CMake) | {L(short(GTEST_ROOT / 'googletest/include'), GTEST_ROOT / 'googletest/include')} | `gtest/gtest.h` — `target_link_libraries(... gtest_main)` 로 주입 |")
        w(f"| (CMake) | {L(short(GTEST_ROOT / 'googlemock/include'), GTEST_ROOT / 'googlemock/include')} | `gmock/gmock.h` |")
    w("")

    # ---- 2 ----
    w("## 2. 프로젝트가 실제 사용하는 헤더")
    w("")
    w(f"`practice/` 하위 `*.cpp`/`*.c`/`*.h`/`README.md` 및 루트 `main.cpp` 에서 `#include <...>` 로 사용된 헤더 **{len(headers)}종** 입니다. "
      "사용 파일 수 내림차순이며, 링크는 컴파일러가 실제로 해결한 파일입니다.")
    w("")
    w("| 헤더 | 사용 파일 수 | 분류 | 실제 소스 (클릭) | 구현 위치 |")
    w("|---|---:|---|---|---|")
    by_class = defaultdict(list)
    for h in sorted(headers, key=lambda x: (-len(USED[x]), x)):
        r = RESOLVED[h]
        cls = classify(h, r)
        by_class[cls].append(h)
        src = L(short(r), r) if r else "— (macOS 에 없음)"
        under = underlying_c_header(h, r)
        if under and under != r:
            src += f" → {L(short(under), under)}"
        w(f"| `<{h}>` | {len(USED[h])} | {cls} | {src} | {IMPL_NOTE[cls]} |")
    w("")
    w("**분류별 요약**: " + ", ".join(f"{k} {len(v)}종" for k, v in sorted(by_class.items())))
    w("")

    # ---- 3 ----
    w("## 3. 심볼 → 정의 위치 빠른 찾기")
    w("")
    w("정의/선언이 있는 파일과 줄로 바로 이동합니다 (자동 탐색 결과).")
    w("")
    w("### 3-1. C++ 표준 라이브러리 (libc++)")
    w("")
    w("| 심볼 | 정의 위치 | 공개 헤더 |")
    w("|---|---|---|")
    cxx_files = libcxx_files()
    for disp, kind, name in LIBCXX_SYMBOLS:
        rx = {"type": type_rx, "alias": alias_rx, "func": func_rx, "spec": spec_rx}[kind](name)
        hit = find_in(cxx_files, rx, HINTS.get(name))
        if not hit:
            w(f"| `{disp}` | (자동 탐색 실패) | |")
            continue
        f, ln = hit
        pubname = PUBLIC_HEADER.get(name, name)
        pub = f"<{pubname}>" if (V1 / pubname).exists() else ""
        w(f"| `{disp}` | {L(f'{short(f)}:{ln}', f, ln)} | {('`' + pub + '`') if pub else ''} |")
    w("")
    w("### 3-2. C / POSIX 함수 선언 (SDK 헤더)")
    w("")
    w("| 함수 | 선언 위치 |")
    w("|---|---|")
    posix_files = []
    for d in POSIX_HEADER_DIRS:
        posix_files += collect_dir(SDK_INC / d, ("*.h",))
    for fn in POSIX_FUNCS:
        hit = find_in(posix_files, rf"^\s*(?:extern\s+)?(?:[\w]+[\s\*]+)*{re.escape(fn)}\s*\(")
        if not hit:  # 속성 매크로(__sized_by_or_null(...) 등)가 낀 선언 대비 완화 패턴
            hit = find_in(posix_files, rf"^(?!\s*(?://|\*|#))[^;{{}}]*?[\s\*]{re.escape(fn)}\s*\(.*\)\s*[\w\s(),]*;")
        if hit:
            f, ln = hit
            w(f"| `{fn}()` | {L(f'{short(f)}:{ln}', f, ln)} |")
        else:
            w(f"| `{fn}()` | (SDK 헤더에서 선언을 찾지 못함 — macOS 미지원 API 이거나 매크로로 감싸진 선언) |")
    w("")
    w("### 3-3. GoogleTest 매크로 / 클래스")
    w("")
    if GTEST_ROOT:
        gfiles = collect_dir(GTEST_ROOT / "googletest/include", ("*.h",), True)
        w("| 심볼 | 정의 위치 |")
        w("|---|---|")
        for disp, rx in GTEST_SYMBOLS:
            hit = find_in(gfiles, rx)
            if hit:
                f, ln = hit
                w(f"| `{disp}` | {L(f'{short(f)}:{ln}', f, ln)} |")
            else:
                w(f"| `{disp}` | (자동 탐색 실패) |")
    else:
        w("GoogleTest 소스가 아직 없습니다 (CMake 구성 필요).")
    w("")

    # ---- 4 ----
    w("## 4. C++ 표준 라이브러리(libc++) 공개 헤더 전체")
    w("")
    pubs = sorted(p for p in V1.iterdir() if p.is_file() and not p.name.startswith("_"))
    w(f"`usr/include/c++/v1` 의 공개 헤더 **{len(pubs)}개** 전체입니다. `프로젝트 사용` 칸이 `●` 이면 `practice/` 에서 실제로 사용 중입니다.")
    w("")
    w("| 헤더 | 링크 | 종류 | 프로젝트 사용 |")
    w("|---|---|---|---|")
    for p in pubs:
        name = p.name
        if name in CXX_C_WRAPPERS:
            kind = "C 래퍼"
        elif name.endswith(".h"):
            kind = "C 호환 .h"
        elif name.startswith(("experimental", "ext")):
            kind = "실험/확장"
        else:
            kind = "C++ 표준"
        used = len(USED.get(name, ()))
        w(f"| `<{name}>` | {L(name, p)} | {kind} | {('● ' + str(used)) if used else ''} |")
    w("")

    # ---- 5 ----
    w("## 5. C 표준 / POSIX 시스템 헤더")
    w("")
    w("`★` 는 프로젝트에서 사용 중인 헤더입니다. 하위 디렉터리는 파일 수와 함께 링크합니다.")
    w("")
    for sub, title in [
        ("", "최상위 (`usr/include/*.h`) — C 표준 + POSIX"),
        ("sys", "`sys/` — 시스템 콜/커널 인터페이스 타입·상수"),
        ("pthread", "`pthread/` — POSIX 스레드 보조 헤더"),
        ("arpa", "`arpa/` — 인터넷 주소 변환"),
        ("netinet", "`netinet/` — TCP/IP 소켓 구조체"),
        ("net", "`net/` — 네트워크 인터페이스"),
        ("_types", "`_types/` — Darwin 내부 타입 정의 (`sys/types.h` 등이 include)"),
        ("machine", "`machine/` — 아키텍처 추상화"),
    ]:
        files = collect_dir(SDK_INC / sub, ("*.h",))
        if not files:
            continue
        w(f"### {title} — {len(files)}개")
        w("")
        links = []
        for f in files:
            rel = f.relative_to(SDK_INC).as_posix()
            star = "★" if rel in USED else ""
            links.append(L(rel + star, f))
        w(dot_join(links))
        w("")
    other_dirs = sorted(
        d for d in SDK_INC.iterdir()
        if d.is_dir() and d.name not in {"", "sys", "pthread", "arpa", "netinet", "net", "_types", "machine", "c++"}
    )
    w("### 기타 SDK 헤더 디렉터리 (이 프로젝트에서 미사용, 위치만 색인)")
    w("")
    w(dot_join(f"{L(d.name + '/', d)}({sum(1 for _ in d.rglob('*.h'))})" for d in other_dirs))
    w("")

    # ---- 6 ----
    w("## 6. 구현체 바이너리와 업스트림 소스")
    w("")
    w("macOS 시스템 라이브러리의 실제 `.dylib` 는 **dyld shared cache** 안에 있어 디스크에 개별 파일로 존재하지 않습니다. "
      "링크 시 사용되는 SDK 스텁(`.tbd`)과, 구현 소스를 볼 수 있는 업스트림 저장소를 정리합니다.")
    w("")
    w("| 라이브러리 | 역할 | 링크 스텁 (로컬) | 구현 소스 (업스트림) |")
    w("|---|---|---|---|")
    lib = SDK / "usr/lib"
    rows = [
        ("libc++", "C++ 표준 라이브러리 (비템플릿 구현: iostream, string, locale, thread, filesystem 등)", ["libc++.tbd", "libc++.1.tbd"], "[llvm/libcxx/src](https://github.com/llvm/llvm-project/tree/main/libcxx/src)"),
        ("libc++abi", "예외, RTTI, `new/delete`, 가드 변수", ["libc++abi.tbd"], "[llvm/libcxxabi/src](https://github.com/llvm/llvm-project/tree/main/libcxxabi/src)"),
        ("libSystem", "libc + libm + libpthread + 시스템 콜 래퍼 통합", ["libSystem.tbd", "libSystem.B.tbd", "libc.tbd", "libm.tbd"], "[apple-oss-distributions/Libc](https://github.com/apple-oss-distributions/Libc), [xnu](https://github.com/apple-oss-distributions/xnu)"),
        ("libpthread", "POSIX 스레드 (`pthread_*`)", ["libpthread.tbd"], "[apple-oss-distributions/libpthread](https://github.com/apple-oss-distributions/libpthread)"),
    ]
    for name, role, tbds, up in rows:
        stubs = ", ".join(L(t, lib / t) for t in tbds if (lib / t).exists())
        w(f"| `{name}` | {role} | {stubs} | {up} |")
    w("")
    w("> **참고**: libc++ 는 템플릿 중심이므로 `std::vector`, `std::sort`, `std::unique_ptr` 등의 **구현 본문은 로컬 헤더(§4, §11)에 전부 있습니다.** "
      "`.cpp` 구현이 필요한 일부(`std::cout`, `std::string` 일부 멤버, `std::thread` 등)만 업스트림 `libcxx/src` 를 보면 됩니다.")
    w("")

    # ---- 7 ----
    w("## 7. GoogleTest (v1.15.2)")
    w("")
    if GTEST_ROOT:
        w(f"- 취득 방식: {L('CMakeLists.txt', REPO / 'CMakeLists.txt', 16)} 의 `FetchContent_Declare(googletest URL …v1.15.2.zip)`")
        w(f"- 소스 루트: {L(short(GTEST_ROOT), GTEST_ROOT)}  _(빌드 디렉터리 내부이므로 `cmake-build-*` 삭제 시 CMake 재구성으로 복구)_")
        w("")
        for title, path, pats, rec in [
            ("공개 헤더 `gtest/`", GTEST_ROOT / "googletest/include/gtest", ("*.h",), False),
            ("내부 헤더 `gtest/internal/`", GTEST_ROOT / "googletest/include/gtest/internal", ("*.h",), False),
            ("구현 소스 `googletest/src/` (.cc)", GTEST_ROOT / "googletest/src", ("*.cc", "*.h"), False),
            ("GoogleMock 헤더 `gmock/`", GTEST_ROOT / "googlemock/include/gmock", ("*.h",), False),
            ("GoogleMock 내부 헤더", GTEST_ROOT / "googlemock/include/gmock/internal", ("*.h",), False),
            ("GoogleMock 구현 소스 `googlemock/src/`", GTEST_ROOT / "googlemock/src", ("*.cc",), False),
        ]:
            files = collect_dir(path, pats, rec)
            w(f"### {title} — {len(files)}개")
            w("")
            w(dot_join(L(f.name, f) for f in files))
            w("")
        w("### 컴파일된 정적 라이브러리 / 진입점")
        w("")
        w(f"- `main()` 정의: {L('gtest_main.cc', GTEST_ROOT / 'googletest/src/gtest_main.cc')} (`gtest_main` 라이브러리가 제공 → `test.cpp` 에 `main` 불필요)")
        if GTEST_LIB_DIR and GTEST_LIB_DIR.exists():
            for a in sorted(GTEST_LIB_DIR.glob("*.a")):
                w(f"- {L(a.name, a)}")
        w("")
    else:
        w("GoogleTest 가 아직 다운로드되지 않았습니다. `cmake -S . -B cmake-build-debug` 후 이 스크립트를 다시 실행하세요.")
        w("")

    # ---- 8 ----
    w("## 8. 리눅스 전용 헤더와 macOS 대체")
    w("")
    w("리눅스 트랙(`practice/linux/`)은 일부 Linux 커널 API 를 사용합니다. macOS SDK 에는 없으므로 "
      "`#if defined(__linux__)` 분기 또는 Docker(`gcc:12`)로 실행합니다 ([linux_run.sh](scripts/linux_run.sh)).")
    w("")
    w("| 리눅스 헤더 | macOS 로컬 존재 | Docker `gcc:12` 내 경로 | 매뉴얼 | macOS 대체 | 사용 파일 |")
    w("|---|---|---|---|---|---|")
    kq = SDK_INC / "sys/event.h"
    subs = {
        "sys/epoll.h": ("epoll", f"kqueue — {L('sys/event.h', kq)}" if kq.exists() else "kqueue"),
        "sys/inotify.h": ("inotify", "FSEvents / kqueue `EVFILT_VNODE`"),
        "sys/eventfd.h": ("eventfd", "`pipe()` 로 대체"),
        "sys/timerfd.h": ("timerfd_create", "kqueue `EVFILT_TIMER`"),
        "sys/signalfd.h": ("signalfd", "`sigaction` + self-pipe"),
    }
    for h, (man, alt) in subs.items():
        local = SDK_INC / h
        exist = L("있음", local) if local.exists() else "없음"
        users = sorted(USED.get(h, ()))
        shown = ", ".join(L(Path(u).parent.name, REPO / u) for u in users[:3])
        if len(users) > 3:
            shown += f" 외 {len(users) - 3}개"
        w(f"| `<{h}>` | {exist} | `/usr/include/x86_64-linux-gnu/{h}` (aarch64 는 `aarch64-linux-gnu`) | [man7 {man}](https://man7.org/linux/man-pages/man7/{man}.7.html) | {alt} | {shown or '—'} |")
    w("")
    w("> 커널 시스템 콜 번호/UAPI 원본: [torvalds/linux — include/uapi](https://github.com/torvalds/linux/tree/master/include/uapi), "
      "glibc 구현: [glibc](https://sourceware.org/git/?p=glibc.git;a=tree;f=sysdeps/unix/sysv/linux)")
    w("")

    # ---- 9 ----
    w("## 9. 프로젝트 빌드 글루 (내부 소스)")
    w("")
    w("외부 라이브러리를 프로젝트에 연결하는 내부 파일입니다.")
    w("")
    w("| 파일 | 역할 |")
    w("|---|---|")
    glue = [
        ("CMakeLists.txt", "C++17 설정, GoogleTest FetchContent, 항목별 타겟 생성"),
        ("scripts/run.sh", "`main.cpp` 단일 컴파일+실행 (`-std=c++17`)"),
        ("scripts/test.sh", "항목 `test.cpp` GoogleTest 빌드+실행"),
        ("scripts/linux_run.sh", "리눅스 트랙 실행기 (호스트/Docker)"),
        ("scripts/cxx_wrapper.sh", "`[[snippet]]` 전처리 컴파일러 래퍼"),
        ("scripts/build_all.sh", "전체 빌드 검증"),
        ("scripts/generate_external_libs_index.py", "이 문서 생성기"),
    ]
    for rel, desc in glue:
        if (REPO / rel).exists():
            w(f"| {L(rel, REPO / rel)} | {desc} |")
    w("")

    # ---- 10 ----
    w("## 10. 사용 헤더의 트랜지티브 include 클로저")
    w("")
    w(f"위 §2 의 헤더들이 (`clang -H` 기준) 실제로 끌어오는 **모든 파일 {len(closure_all)}개** 입니다. "
      "정의를 추적하다 막히면 여기서 파일명으로 찾으세요.")
    w("")
    groups = defaultdict(list)
    for f in sorted(closure_all):
        if CLANG_RES_INC and str(f).startswith(str(CLANG_RES_INC)):
            groups[("clang 내장 헤더", CLANG_RES_INC)].append(f)
        elif str(f).startswith(str(V1)):
            rel = f.relative_to(V1)
            key = rel.parts[0] if len(rel.parts) > 1 else "(공개 헤더)"
            groups[(f"libc++ — {key}", V1)].append(f)
        elif str(f).startswith(str(SDK_INC)):
            rel = f.relative_to(SDK_INC)
            key = rel.parts[0] if len(rel.parts) > 1 else "(최상위)"
            groups[(f"SDK — {key}", SDK_INC)].append(f)
        elif GTEST_ROOT and str(f).startswith(str(GTEST_ROOT)):
            groups[("GoogleTest", GTEST_ROOT)].append(f)
        else:
            groups[("기타", Path("/"))].append(f)
    for (title, base), files in sorted(groups.items(), key=lambda kv: kv[0][0]):
        w("<details>")
        w(f"<summary><b>{title}</b> ({len(files)}개)</summary>")
        w("")
        w(dot_join(L(str(f.relative_to(base)) if base != Path('/') else str(f), f) for f in files))
        w("")
        w("</details>")
        w("")

    # ---- 11 ----
    w("## 11. 부록: libc++ 내부 구현 헤더 전체")
    w("")
    w("공개 헤더(`<vector>` 등)가 `#include <__vector/vector.h>` 처럼 끌어오는 **내부 구현 헤더** 전체 목록입니다 "
      "(실제 알고리즘/컨테이너 본문이 여기 있음).")
    w("")
    internal_dirs = sorted(d for d in V1.iterdir() if d.is_dir())
    internal_files = sorted(p for p in V1.iterdir() if p.is_file() and p.name.startswith("_"))
    total = sum(1 for d in internal_dirs for _ in d.rglob("*") if _.is_file()) + len(internal_files)
    w(f"총 **{total}개** 파일, 디렉터리 {len(internal_dirs)}개.")
    w("")
    if internal_files:
        w("<details>")
        w(f"<summary><b>(V1 최상위 내부 파일)</b> ({len(internal_files)}개)</summary>")
        w("")
        w(dot_join(L(f.name, f) for f in internal_files))
        w("")
        w("</details>")
        w("")
    for d in internal_dirs:
        files = sorted(p for p in d.rglob("*") if p.is_file())
        w("<details>")
        note = " — ⚠️ `-std=c++03` 전용 동결 사본 (C++17 컴파일에서는 사용되지 않음)" if d.name == "__cxx03" else ""
        w(f"<summary><b>{L(d.name + '/', d)}</b> ({len(files)}개){note}</summary>")
        w("")
        w(dot_join(L(str(f.relative_to(d)), f) for f in files))
        w("")
        w("</details>")
        w("")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"[완료] {OUT} 생성 ({size_kb:.0f} KB, 사용 헤더 {len(headers)}종, 클로저 {len(closure_all)}개 파일)")
    unresolved = [h for h in headers if RESOLVED[h] is None]
    if unresolved:
        print(f"[정보] macOS 에서 해결되지 않은 헤더 {len(unresolved)}종: {', '.join(unresolved)}")


if __name__ == "__main__":
    sys.exit(main())
