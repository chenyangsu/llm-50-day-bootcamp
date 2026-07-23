#!/usr/bin/env python3
"""Generate the Quarto pages for the 50-day LLM bootcamp from data/schedule.yml.

data/schedule.yml is the single source of truth. Everything under days/, plus
timeline.qmd, resources.qmd and days.js, is generated from it and should not be
hand-edited -- edit the YAML and re-run this script instead.

    python3 scripts/build.py
"""

import json
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "data" / "schedule.yml"
DAYS_DIR = ROOT / "days"

KIND_LABEL = {
    "study": "Study day",
    "catchup": "Catch-up day",
    "milestone": "Milestone",
    "capstone": "Capstone",
}

KIND_ORDER = ["textbook", "video", "paper", "course", "repo", "tool", "reference"]
KIND_HEADING = {
    "textbook": "Textbooks",
    "video": "Lectures and videos",
    "paper": "Papers",
    "course": "Courses",
    "repo": "Code repositories",
    "tool": "Tools and documentation",
    "reference": "Reference",
}


def yq(value):
    """Quote a string for a YAML frontmatter scalar. JSON strings are valid YAML."""
    return json.dumps(value, ensure_ascii=False)


def long_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.strftime('%A')}, {d.day} {d.strftime('%B %Y')}"


def short_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.strftime('%a')} {d.day} {d.strftime('%b')}"


def slug(day):
    return f"day-{day['day']:02d}"


def total_minutes(day):
    return sum(t.get("minutes", 0) for t in day.get("tasks", []))


def day_page(day, prev_day, next_day):
    kind = day.get("kind", "study")
    lines = []
    title = "Day {} — {}".format(day["day"], day["title"])
    lines.append("---")
    lines.append("title: " + yq(title))
    subtitle = (
        f"{long_date(day['date'])} · Week {day['week']} · "
        f"{day['phase']} · {KIND_LABEL.get(kind, 'Study day')} · {day.get('hours', '3-4 h')}"
    )
    lines.append("subtitle: " + yq(subtitle))
    lines.append("---")
    lines.append("")

    # Previous / next navigation.
    nav = []
    nav.append(f"[← Day {prev_day['day']}]({slug(prev_day)}.qmd)" if prev_day else "[← Setup](../setup.qmd)")
    nav.append("[All 50 days](../timeline.qmd)")
    nav.append(f"[Day {next_day['day']} →]({slug(next_day)}.qmd)" if next_day else "[Milestones →](../milestones.qmd)")
    lines.append(f'::: {{.day-nav .kind-{kind}}}')
    lines.append(" · ".join(nav))
    lines.append(":::")
    lines.append("")

    if day.get("why"):
        lines.append('::: {.why}')
        lines.append(day["why"])
        lines.append(":::")
        lines.append("")

    if day.get("objectives"):
        lines.append("## What you should be able to do tonight")
        lines.append("")
        for obj in day["objectives"]:
            lines.append(f"- {obj}")
        lines.append("")

    tasks = day.get("tasks", [])
    if tasks:
        mins = total_minutes(day)
        lines.append(f"## Tasks <span class='task-total'>{mins} min</span>")
        lines.append("")
        lines.append('::: {.task-list}')
        for task in tasks:
            lines.append('::: {.task}')
            minutes = task.get("minutes")
            badge = f"[{minutes} min]{{.task-min}} " if minutes else ""
            lines.append(f'<input type="checkbox" class="task-check"> {badge}{task["text"]}')
            lines.append(":::")
        lines.append(":::")
        lines.append("")

    if day.get("resources"):
        lines.append("## Resources")
        lines.append("")
        for res in day["resources"]:
            tag = f" [{res['kind']}]{{.res-kind}}" if res.get("kind") else ""
            lines.append(f"- [{res['label']}]({res['url']}){tag}")
        lines.append("")

    if day.get("deliverable"):
        lines.append("## Deliverable")
        lines.append("")
        lines.append('::: {.deliverable}')
        lines.append(day["deliverable"])
        lines.append(":::")
        lines.append("")

    if day.get("checkpoint"):
        lines.append("## Checkpoint")
        lines.append("")
        lines.append('::: {.checkpoint}')
        lines.append(day["checkpoint"])
        lines.append(":::")
        lines.append("")

    prep = day.get("prep_for_tomorrow") or []
    if prep:
        nxt = f"Day {next_day['day']}, {long_date(next_day['date'])}" if next_day else "tomorrow"
        lines.append("## Prepare for tomorrow")
        lines.append("")
        lines.append(f"Ten minutes tonight so {nxt} starts clean. This is what the evening email sends you.")
        lines.append("")
        lines.append('::: {.task-list .prep}')
        for item in prep:
            lines.append('::: {.task}')
            lines.append(f'<input type="checkbox" class="task-check"> {item}')
            lines.append(":::")
        lines.append(":::")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def timeline_page(days, meta):
    lines = []
    lines.append("---")
    lines.append('title: "The 50 days"')
    span_all = "{} → {}".format(long_date(meta["start_date"]), long_date(meta["end_date"]))
    lines.append("subtitle: " + yq(span_all))
    lines.append("---")
    lines.append("")
    lines.append(
        "Six study days, then a catch-up day, seven times over, then the capstone. "
        "Every catch-up day is a Thursday and is deliberately unallocated — if you are on track, "
        "the day is yours."
    )
    lines.append("")
    lines.append('::: {.timeline}')
    lines.append("")

    by_week = {}
    for day in days:
        by_week.setdefault(day["week"], []).append(day)

    for week in sorted(by_week):
        wdays = by_week[week]
        phase = wdays[0]["phase"]
        span = f"{short_date(wdays[0]['date'])} – {short_date(wdays[-1]['date'])}"
        lines.append(f"### Week {week} — {phase} <span class='week-span'>{span}</span>")
        lines.append("")
        lines.append("| Day | Date | Focus | |")
        lines.append("|---:|:---|:---|:---|")
        for day in wdays:
            kind = day.get("kind", "study")
            marker = {"catchup": "catch-up", "milestone": "milestone", "capstone": "capstone"}.get(kind, "")
            marker_cell = f"[{marker}]{{.pill .pill-{kind}}}" if marker else ""
            lines.append(
                f"| [{day['day']}](days/{slug(day)}.qmd) | {short_date(day['date'])} "
                f"| [{day['title']}](days/{slug(day)}.qmd) | {marker_cell} |"
            )
        lines.append("")

    lines.append(":::")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def resources_page(days):
    seen = {}
    for day in days:
        for res in day.get("resources", []):
            entry = seen.setdefault(
                res["url"],
                {"label": res["label"], "kind": res.get("kind", "reference"), "days": []},
            )
            entry["days"].append(day["day"])

    by_kind = {}
    for url, entry in seen.items():
        by_kind.setdefault(entry["kind"], []).append((url, entry))

    lines = []
    lines.append("---")
    lines.append('title: "Every resource"')
    lines.append('subtitle: "Every link the bootcamp uses, grouped by what it is."')
    lines.append("---")
    lines.append("")
    lines.append(
        f"{len(seen)} distinct resources across the 50 days. The day numbers after each entry "
        "tell you where it is used."
    )
    lines.append("")

    ordered = [k for k in KIND_ORDER if k in by_kind] + [k for k in sorted(by_kind) if k not in KIND_ORDER]
    for kind in ordered:
        lines.append(f"## {KIND_HEADING.get(kind, kind.title())}")
        lines.append("")
        for url, entry in sorted(by_kind[kind], key=lambda kv: min(kv[1]["days"])):
            day_nums = sorted(set(entry["days"]))
            refs = ", ".join(f"[{n}](days/day-{n:02d}.qmd)" for n in day_nums)
            lines.append(f"- [{entry['label']}]({url}) — day{'s' if len(day_nums) > 1 else ''} {refs}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def site_js_include(days, meta):
    """Inline the schedule data and progress script into one HTML include.

    Inlining sidesteps relative-path breakage between /index.html and /days/day-01.html
    once the site is served from a project subpath on GitHub Pages.
    """
    payload = [
        {
            "day": d["day"],
            "date": d["date"],
            "title": d["title"],
            "kind": d.get("kind", "study"),
            "week": d["week"],
        }
        for d in days
    ]
    progress = (ROOT / "scripts" / "progress.js").read_text(encoding="utf-8")
    start = json.dumps(meta["start_date"])
    data = json.dumps(payload, ensure_ascii=False)
    return (
        "<!-- Generated by scripts/build.py -- do not edit. -->\n"
        "<script>\n"
        "const BOOTCAMP_START = " + start + ";\n"
        "const BOOTCAMP_DAYS = " + data + ";\n"
        + progress
        + "\n</script>\n"
    )


def main():
    data = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))
    days = sorted(data["days"], key=lambda d: d["day"])
    meta = data["meta"]

    DAYS_DIR.mkdir(exist_ok=True)
    for i, day in enumerate(days):
        prev_day = days[i - 1] if i > 0 else None
        next_day = days[i + 1] if i + 1 < len(days) else None
        (DAYS_DIR / f"{slug(day)}.qmd").write_text(day_page(day, prev_day, next_day), encoding="utf-8")

    (ROOT / "timeline.qmd").write_text(timeline_page(days, meta), encoding="utf-8")
    (ROOT / "resources.qmd").write_text(resources_page(days), encoding="utf-8")
    includes = ROOT / "_includes"
    includes.mkdir(exist_ok=True)
    (includes / "site-js.html").write_text(site_js_include(days, meta), encoding="utf-8")

    total = sum(total_minutes(d) for d in days)
    resources = {r["url"] for d in days for r in d.get("resources", [])}
    print(f"wrote {len(days)} day pages, timeline, resources ({len(resources)} links), site-js")
    print(f"total scheduled time: {total / 60:.0f} h across {len(days)} days")


if __name__ == "__main__":
    main()
