import subprocess
import json

from collections import defaultdict
from typing import DefaultDict

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

for repo in repos:
    name = repo["name"]
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


for lang, value in sorted(languages.items(), key=lambda x: x[1], reverse=True):
    percent = (value / total) * 100
    bar = "█" * int(percent / 2)
    
    lines.append(f"| {lang} | {bar} {percent:.1f}% |")

markdown = "\n".join(lines)

# README aktualisieren
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start = "<!--START_LANG_STATS-->"
end = "<!--END_LANG_STATS-->"

new_content = content.split(start)[0] + start + "\n" + markdown + "\n" + end + content.split(end)[1]

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_content)

print("README updated.")
