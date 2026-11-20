#!/usr/bin/env python3
"""Build and manage practice pages for the motion offense playbook.

Usage:
  python3 practice.py new 2026-11-24            # copy the latest practice to a new date
  python3 practice.py new 2026-11-24 --from 2026-11-21
  python3 practice.py list                      # show all practices and their total minutes
  python3 practice.py build                     # rebuild docs/ (the shareable website)

Each practice is a JSON file in practices/. Edit the blocks (minutes, title,
drill, items) and run `build`. The newest practice becomes docs/index.html.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRACTICES = ROOT / "practices"
DOCS = ROOT / "docs"
TEMPLATE = ROOT / "template.html"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def drill_ids():
    return sorted(set(re.findall(r'id="d-([\w-]+)"', TEMPLATE.read_text(encoding="utf-8"))))


def load_all():
    items = []
    for f in sorted(PRACTICES.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        data.setdefault("date", f.stem)
        items.append((f, data))
    return items


def check(data, valid):
    problems = []
    if not DATE_RE.match(data.get("date", "")):
        problems.append("date must look like 2026-11-24")
    for i, b in enumerate(data.get("blocks", []), 1):
        if not isinstance(b.get("min"), int) or b["min"] <= 0:
            problems.append(f"block {i}: 'min' must be a positive whole number")
        if not b.get("title"):
            problems.append(f"block {i}: missing 'title'")
        d = b.get("drill")
        if d and d not in valid:
            problems.append(f"block {i}: unknown drill '{d}' (choose from: {', '.join(valid)})")
    return problems


def total(data):
    return sum(b.get("min", 0) for b in data.get("blocks", []))


def cmd_list():
    for f, d in load_all():
        print(f"{d['date']}  {total(d):>3} min  {d.get('title', '')}")


def cmd_new(args):
    if not args or not DATE_RE.match(args[0]):
        sys.exit("Give a date: python3 practice.py new 2026-11-24")
    date = args[0]
    target = PRACTICES / f"{date}.json"
    if target.exists():
        sys.exit(f"{target.name} already exists. Edit it directly.")
    allp = load_all()
    if not allp:
        sys.exit("No practices to copy from.")
    src = allp[-1]
    if "--from" in args:
        want = args[args.index("--from") + 1]
        matches = [p for p in allp if p[1]["date"] == want]
        if not matches:
            sys.exit(f"No practice dated {want}")
        src = matches[0]
    data = json.loads(json.dumps(src[1]))
    data["date"] = date
    data["title"] = "New practice (edit me)"
    data["notes"] = ""
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Created practices/{target.name} (copied from {src[1]['date']}).")
    print("Edit it, then run: python3 practice.py build")


def cmd_build():
    valid = drill_ids()
    allp = load_all()
    if not allp:
        sys.exit("No practices found in practices/.")
    bad = False
    for f, d in allp:
        for p in check(d, valid):
            print(f"{f.name}: {p}")
            bad = True
    if bad:
        sys.exit("Fix the problems above, then build again.")
    tmpl = TEMPLATE.read_text(encoding="utf-8")
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    plist = [{"date": d["date"], "title": d.get("title", ""), "file": f"{d['date']}.html"}
             for _, d in reversed(allp)]
    plist_js = json.dumps(plist, ensure_ascii=False)
    for _, d in allp:
        html = tmpl.replace("__PRACTICE_LIST__", plist_js).replace(
            "__PRACTICE__", json.dumps(d, ensure_ascii=False).replace("</", "<\\/"))
        (DOCS / f"{d['date']}.html").write_text(html, encoding="utf-8")
        print(f"built docs/{d['date']}.html  ({total(d)} min)  {d.get('title', '')}")
    latest = allp[-1][1]["date"]
    shutil.copy(DOCS / f"{latest}.html", DOCS / "index.html")
    (DOCS / ".nojekyll").write_text("")
    print(f"docs/index.html -> {latest}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        cmd_build()
    elif cmd == "new":
        cmd_new(sys.argv[2:])
    elif cmd == "list":
        cmd_list()
    else:
        print(__doc__)
