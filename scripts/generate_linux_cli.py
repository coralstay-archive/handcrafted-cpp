#!/usr/bin/env python3
"""Generator for Linux Track 02: CLI and Shell Automation
(Efficient Linux at the Command Line & Adventures with the Linux Command Line)
-> stone/linux/02_cli_and_shell_automation/
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = REPO_ROOT / "stone" / "linux" / "02_cli_and_shell_automation"

import _init_paths


def load_all_items():
    from linux_data import (
        cli_01_pipelines,
        cli_02_scripting,
        cli_03_processes,
    )
    items = []
    for mod in (cli_01_pipelines, cli_02_scripting, cli_03_processes):
        items.extend(mod.ITEMS)
    return items


def render_readme(item: dict) -> str:
    num = item["num"]
    title = item["title"]
    source = item["source"]
    chapter = item["chapter"]
    concept = item["concept"]
    target_code = item["target_code"].strip()
    expected_output = item["expected_output"].strip()
    verify_cmd = item.get("verify_cmd", "bash script.sh")

    return f"""# [{num}] {title}

> **도서**: {source}  
> **장/절**: {chapter}  
> **환경**: Bash 4+ / POSIX Shell

---

## 1. 핵심 명령어 및 자동화 원리

{concept}

---

## 2. 따라쳐볼 목표 스크립트 (`script.sh` 완성본)

아래 스크립트를 `script.sh`에 직접 타이핑하며 파이프라인 결합, 리다이렉션, 프로세스 제어 기법을 체득해 보세요.

```bash
{target_code}
```

### 예상 실행 출력

```text
{expected_output}
```

---

## 3. 실행 및 검증 방법

```bash
# 스크립트 직접 실행
./scripts/linux_run.sh stone/linux/02_cli_and_shell_automation/{item['section_dir']}/{num}_{item['slug']}

# 또는 수동 실행:
{verify_cmd}
```
"""


def render_script_skeleton(item: dict) -> str:
    num = item["num"]
    title = item["title"]
    chapter = item["chapter"]
    steps = item.get("steps", [
        "필요한 환경 변수 및 안전 옵션(set -euo pipefail)을 설정하세요.",
        "README.md를 참고하여 핵심 명령어 파이프라인 또는 함수를 작성하세요.",
        "스크립트 실행 후 결과를 확인하세요.",
    ])
    expected_output = item["expected_output"].strip()

    step_lines = "\n".join(f"# Step {i+1}: {s}" for i, s in enumerate(steps))
    exp_lines = "\n".join(f"#   {line}" for line in expected_output.splitlines())

    return f"""#!/usr/bin/env bash
# ==============================================================================
# [리눅스 CLI & 셸 자동화] {num}. {title}
# 장/절: {chapter}
# ==============================================================================
# [따라치기 가이드]
# README.md에 수록된 목표 코드를 직접 타이핑하며 셸 파이프라인 기법을 익히세요.
#
# 예상 출력:
{exp_lines}
# ==============================================================================
set -euo pipefail

{step_lines}

echo "TODO: README.md의 완성본 코드를 타이핑하세요."
"""


def verify_items(items: list[dict]) -> bool:
    print(f"[검증] 총 {len(items)}개 CLI/셸 스크립트 target_code를 bash 문법 검사(bash -n) 및 실행 테스트합니다...")
    ok_count = 0
    fail_count = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        for item in items:
            num = item["num"]
            script_path = os.path.join(tmpdir, f"script_{num}.sh")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(item["target_code"].strip() + "\n")
            # 1. 문법 검사
            res_syntax = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True)
            if res_syntax.returncode != 0:
                print(f"  [문법 오류] {num} ({item['title']}):\n{res_syntax.stderr}")
                fail_count += 1
                continue
            # 2. 실행 검사
            res_run = subprocess.run(["bash", script_path], capture_output=True, text=True, cwd=tmpdir, timeout=10)
            if res_run.returncode != 0:
                print(f"  [실행 실패] {num} ({item['title']}):\n{res_run.stderr}")
                fail_count += 1
            else:
                ok_count += 1
    print(f"[검증 결과] 성공: {ok_count}/{len(items)}, 실패: {fail_count}")
    return fail_count == 0


def generate_files(items: list[dict], force: bool = False):
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    updated_readme = 0

    sections: dict[str, list[dict]] = {}
    for item in items:
        sec = item["section_dir"]
        sections.setdefault(sec, []).append(item)
        item_dir = BASE_DIR / sec / f"{item['num']}_{item['slug']}"
        item_dir.mkdir(parents=True, exist_ok=True)

        readme_path = item_dir / "README.md"
        script_path = item_dir / "script.sh"

        readme_path.write_text(render_readme(item), encoding="utf-8")
        updated_readme += 1

        if force or not script_path.exists():
            script_path.write_text(render_script_skeleton(item), encoding="utf-8")
            script_path.chmod(0o755)
            created += 1

    lines = [
        "# 02. 리눅스 CLI 및 셸 스크립트 자동화 (Linux CLI & Shell Automation)",
        "",
        "> 원본 도서: `Efficient Linux at the Command Line` & `Adventures with the Linux Command Line`",
        "> 환경: **Bash 4+ / POSIX Shell**",
        "",
        "## 실행 방법",
        "",
        "```bash",
        "# 스크립트 실행 (예: 01_pipeline_and_filters/01_pipes_stdin_stdout)",
        "./scripts/linux_run.sh stone/linux/02_cli_and_shell_automation/01_pipeline_and_filters/01_pipes_stdin_stdout",
        "```",
        "",
        "## 전체 목차",
        "",
    ]
    for sec in sorted(sections.keys()):
        lines.append(f"### `{sec}`")
        for it in sections[sec]:
            rel = f"{sec}/{it['num']}_{it['slug']}"
            lines.append(f"- [{it['num']}. {it['title']}](./{rel}/README.md) (`{it['chapter']}`)")
        lines.append("")

    (BASE_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[완료] CLI 자동화 총 {len(items)}개 항목 생성 완료 (README 갱신: {updated_readme}, 스켈레톤 생성: {created})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Syntax & execution test of all scripts")
    parser.add_argument("--force", action="store_true", help="Overwrite existing script.sh")
    args = parser.parse_args()

    items = load_all_items()
    if args.verify:
        if not verify_items(items):
            sys.exit(1)
    generate_files(items, force=args.force)


if __name__ == "__main__":
    main()
