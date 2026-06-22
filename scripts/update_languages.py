import re
import subprocess
import json

from collections import defaultdict
from typing import DefaultDict

BADGE_MAP: dict[str, str] = {
    "TypeScript": "![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)",
    "JavaScript": "![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)",
    "C#": "![C#](https://img.shields.io/badge/C%23-239120?style=flat&logo=csharp&logoColor=white)",
    "Python": "![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)",
    "SQL": "![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat&logo=postgresql&logoColor=white)",
    "CSS": "![CSS](https://img.shields.io/badge/CSS-1572B6?style=flat&logo=css3&logoColor=white)",
    "HTML": "![HTML](https://img.shields.io/badge/HTML-E34F26?style=flat&logo=html5&logoColor=white)",
    "Go": "![Go](https://img.shields.io/badge/Go-00ADD8?style=flat&logo=go&logoColor=white)",
    "Java": "![Java](https://img.shields.io/badge/Java-ED8B00?style=flat&logo=openjdk&logoColor=white)",
    "Gherkin": "![Gherkin](https://img.shields.io/badge/Gherkin-23D96C?style=flat&logo=cucumber&logoColor=white)",
    "XSLT": "![XSLT](https://img.shields.io/badge/XSLT-FF6600?style=flat&logo=xml&logoColor=white)",
    "Vue": "![Vue](https://img.shields.io/badge/Vue-4FC08D?style=flat&logo=vuedotjs&logoColor=white)",
    "PowerShell": "![PowerShell](https://img.shields.io/badge/PowerShell-5391FE?style=flat&logo=powershell&logoColor=white)",
    "Astro": "![Astro](https://img.shields.io/badge/Astro-FF5D01?style=flat&logo=astro&logoColor=white)",
    "Shell": "![Shell](https://img.shields.io/badge/Shell-4EAA25?style=flat&logo=gnubash&logoColor=white)",
    "Dockerfile": "![Dockerfile](https://img.shields.io/badge/Dockerfile-2496ED?style=flat&logo=docker&logoColor=white)",
    "YAML": "![YAML](https://img.shields.io/badge/YAML-CB171E?style=flat&logo=yaml&logoColor=white)",
    "Bicep": "![Bicep](https://img.shields.io/badge/Bicep-0078D4?style=flat&logo=microsoftazure&logoColor=white)",
    "Rust": "![Rust](https://img.shields.io/badge/Rust-000000?style=flat&logo=rust&logoColor=white)",
    "Kotlin": "![Kotlin](https://img.shields.io/badge/Kotlin-7F52FF?style=flat&logo=kotlin&logoColor=white)",
    "Swift": "![Swift](https://img.shields.io/badge/Swift-F05138?style=flat&logo=swift&logoColor=white)",
    "Ruby": "![Ruby](https://img.shields.io/badge/Ruby-CC342D?style=flat&logo=ruby&logoColor=white)",
    "PHP": "![PHP](https://img.shields.io/badge/PHP-777BB4?style=flat&logo=php&logoColor=white)",
    "Dart": "![Dart](https://img.shields.io/badge/Dart-0175C2?style=flat&logo=dart&logoColor=white)",
    "Scala": "![Scala](https://img.shields.io/badge/Scala-DC322F?style=flat&logo=scala&logoColor=white)",
    "Lua": "![Lua](https://img.shields.io/badge/Lua-2C2D72?style=flat&logo=lua&logoColor=white)",
    "R": "![R](https://img.shields.io/badge/R-276DC3?style=flat&logo=r&logoColor=white)",
    "Haskell": "![Haskell](https://img.shields.io/badge/Haskell-5D4F85?style=flat&logo=haskell&logoColor=white)",
    "Elixir": "![Elixir](https://img.shields.io/badge/Elixir-4B275F?style=flat&logo=elixir&logoColor=white)",
    "Clojure": "![Clojure](https://img.shields.io/badge/Clojure-5881D8?style=flat&logo=clojure&logoColor=white)",
    "Markdown": "![Markdown](https://img.shields.io/badge/Markdown-000000?style=flat&logo=markdown&logoColor=white)",
}

README = "README.md"

def run(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

user = run("gh api user --jq .login")

raw = run(f"gh repo list {user} --limit 500 --json name,isFork")
if not raw:
    print("Error: gh repo list returned empty output. Check GH_PAT secret and token scope.")
    exit(1)
repos = json.loads(raw)

languages: DefaultDict[str, int] = defaultdict(int)

excluded_repos = {"vscode"}

for repo in repos:
    name = repo["name"]

    if name in excluded_repos:
        print(f"Skipping {name} (excluded)...")
        continue

    print(f"Processing {name}...")

    try:
        data = json.loads(run(f"gh api repos/{user}/{name}/languages"))
        for lang, value in data.items():
            languages[lang] += value
    except:
        continue

total = sum(languages.values())

lines: list[str] = []
lines.append("| Language | Usage |")
lines.append("|---------|--------|")


def to_percent(value: int) -> float:
    return (value / total) * 100 if total > 0 else 0


def format_row(lang: str, percent: float) -> str:
    bar = "█" * int(percent / 2) or "▏"
    return f"| {lang} | {bar} {percent:.1f}% |"


other = 0

for lang, value in sorted(languages.items(), key=lambda x: x[1], reverse=True):
    percent = to_percent(value)

    if percent < 0.1:
        other += value
        continue

    lines.append(format_row(lang, percent))

if other > 0:
    lines.append(format_row("Other", to_percent(other)))

markdown = "\n".join(lines)

with open(README, "r", encoding="utf-8") as f:
    content = f.read()

start = "<!--START_LANG_STATS-->"
end = "<!--END_LANG_STATS-->"

new_content = content.split(start)[0] + start + "\n" + markdown + "\n" + end + content.split(end)[1]

with open(README, "w", encoding="utf-8") as f:
    f.write(new_content)

print("README updated.")

# Gap-Sync: add missing language badges to Technologies/Languages row
languages_row_re = re.compile(r'(\| \*\*Languages\*\* \|)(.*?)(\|)', re.DOTALL)
match = languages_row_re.search(new_content)
if match:
    existing_badges = match.group(2)
    existing_labels = set(re.findall(r'!\[([^\]]+)\]\(', existing_badges))

    new_badges: list[str] = []
    for lang in languages:
        if lang in existing_labels:
            continue
        badge = BADGE_MAP.get(lang)
        if badge is None:
            safe = lang.replace(" ", "%20")
            badge = f"![{lang}](https://img.shields.io/badge/{safe}-grey?style=flat)"
            print(f"No badge mapping for '{lang}', using generic badge.")
        new_badges.append(badge)

    if new_badges:
        updated_row = match.group(1) + existing_badges + " " + " ".join(new_badges) + " " + match.group(3)
        new_content = new_content[:match.start()] + updated_row + new_content[match.end():]
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Technologies/Languages updated: {[b.split(']')[0][2:] for b in new_badges]}")
    else:
        print("Technologies/Languages already up to date.")
