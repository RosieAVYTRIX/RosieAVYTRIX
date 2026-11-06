"""Refresh the profile using public repositories; no third-party dependencies."""
import json
from pathlib import Path
from urllib.request import Request, urlopen

OWNER = "RosieAVYTRIX"
README = Path(__file__).resolve().parents[1] / "README.md"
START, END = "<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"

def fetch_projects():
    projects = []
    page = 1
    while True:
        request = Request(
            f"https://api.github.com/users/{OWNER}/repos?type=owner&sort=updated&per_page=100&page={page}",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-portfolio"},
        )
        with urlopen(request, timeout=30) as response:
            batch = json.load(response)
        projects.extend(r for r in batch if not r["fork"] and not r["archived"] and r["name"].lower() != OWNER.lower())
        if len(batch) < 100:
            break
        page += 1
    return projects[:6]

def plain(value):
    return " ".join(str(value or "").split()).replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("[", "&#91;").replace("]", "&#93;")

def main():
    projects = fetch_projects()
    rows = []
    for repo in projects:
        description = plain(repo.get("description")) or "Xem README trong repository."
        language = plain(repo.get("language")) or "—"
        rows.append(f'- **[{plain(repo["name"])}]({repo["html_url"]})** · {language}\n  {description}')
    section = "\n\n".join(rows) if rows else "*Chưa có dự án công khai để hiển thị.*"
    current = README.read_text(encoding="utf-8")
    if current.count(START) != 1 or current.count(END) != 1:
        raise ValueError("README must contain exactly one pair of project markers")
    before, remaining = current.split(START)
    _, after = remaining.split(END)
    README.write_text(before + START + "\n" + section + "\n" + END + after, encoding="utf-8")

if __name__ == "__main__":
    main()
