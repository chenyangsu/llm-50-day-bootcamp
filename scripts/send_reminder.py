#!/usr/bin/env python3
"""Send the evening reminder email for tomorrow's bootcamp day.

Reads data/schedule.yml, works out tomorrow's date in the schedule's timezone,
and emails the prep items from *today's* record (prep_for_tomorrow on day N
describes how to get ready for day N+1) along with a preview of tomorrow.

Run by .github/workflows/daily-reminder.yml. To see the email without sending:

    python3 scripts/send_reminder.py --dry-run
    python3 scripts/send_reminder.py --dry-run --today 2026-08-19

Requires Python 3.9+ (zoneinfo) and PyYAML.
"""

import argparse
import html
import os
import smtplib
import sys
from datetime import date, datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "data" / "schedule.yml"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def as_iso(value):
    """schedule.yml dates may load as str or datetime.date depending on quoting."""
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return str(value)


def long_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.strftime('%A')}, {d.day} {d.strftime('%B %Y')}"


def build_html(day, prep, meta):
    """Plain, inline-styled HTML. Gmail strips <style> blocks, so everything is inline."""
    e = html.escape
    slug = f"day-{day['day']:02d}"
    url = f"{meta['site_url']}/days/{slug}.html"

    grey = "color:#6c757d"
    wrap = "font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;font-size:15px;line-height:1.5;color:#212529;max-width:640px"
    h2 = "font-size:15px;font-weight:700;margin:22px 0 8px 0"

    parts = [f'<div style="{wrap}">']
    parts.append(
        f'<p style="{grey};font-size:13px;margin:0 0 14px 0">'
        f"Day {day['day']} of 50 &middot; {e(long_date(as_iso(day['date'])))} &middot; "
        f"Week {day['week']}, {e(day['phase'])} &middot; {e(str(day.get('hours', '3-4 h')))}</p>"
    )
    parts.append(f'<p style="font-style:italic;margin:0 0 4px 0">{e(day.get("why", ""))}</p>')

    # The part that matters at 8pm.
    parts.append(
        f'<div style="background:#eef5fb;border-left:4px solid #2c7fb8;'
        f'padding:12px 16px;margin:20px 0;border-radius:6px">'
        f'<div style="{h2};margin-top:0">Tonight, about ten minutes</div><ul style="margin:0;padding-left:20px">'
    )
    for item in prep:
        parts.append(f"<li style='margin:5px 0'>{e(str(item))}</li>")
    parts.append("</ul></div>")

    parts.append(f'<div style="{h2}">Tomorrow</div><ul style="margin:0;padding-left:20px">')
    for task in day.get("tasks", []):
        mins = task.get("minutes")
        badge = (
            f"<span style='{grey};font-size:12px;font-weight:600'>{mins} min</span> &nbsp;"
            if mins else ""
        )
        parts.append(f"<li style='margin:6px 0'>{badge}{e(task['text'])}</li>")
    parts.append("</ul>")

    if day.get("resources"):
        parts.append(f'<div style="{h2}">Links you\'ll need</div><ul style="margin:0;padding-left:20px">')
        for res in day["resources"]:
            parts.append(
                f"<li style='margin:5px 0'><a href=\"{e(res['url'])}\">{e(res['label'])}</a></li>"
            )
        parts.append("</ul>")

    if day.get("deliverable"):
        parts.append(
            f'<div style="{h2}">Deliverable</div>'
            f'<p style="margin:0">{e(day["deliverable"])}</p>'
        )

    parts.append(
        f'<p style="margin:26px 0 0 0"><a href="{e(url)}">Open day {day["day"]} on the site</a></p>'
    )
    parts.append("</div>")
    return "\n".join(parts)


def build_text(day, prep, meta):
    slug = f"day-{day['day']:02d}"
    lines = [
        f"Day {day['day']} of 50 - {long_date(as_iso(day['date']))} - "
        f"Week {day['week']}, {day['phase']} - {day.get('hours', '3-4 h')}",
        "",
        day.get("why", ""),
        "",
        "TONIGHT, ABOUT TEN MINUTES",
    ]
    lines += [f"  - {item}" for item in prep]
    lines += ["", "TOMORROW"]
    for task in day.get("tasks", []):
        mins = f"[{task['minutes']} min] " if task.get("minutes") else ""
        lines.append(f"  - {mins}{task['text']}")
    if day.get("resources"):
        lines += ["", "LINKS"]
        lines += [f"  - {r['label']}: {r['url']}" for r in day["resources"]]
    if day.get("deliverable"):
        lines += ["", "DELIVERABLE", f"  {day['deliverable']}"]
    lines += ["", f"{meta['site_url']}/days/{slug}.html"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print the email instead of sending it")
    ap.add_argument("--today", help="override today's date as YYYY-MM-DD, for testing")
    args = ap.parse_args()

    data = yaml.safe_load(SCHEDULE.read_text(encoding="utf-8"))
    meta, days = data["meta"], data["days"]

    tz = ZoneInfo(meta.get("timezone", "America/Winnipeg"))
    today = (
        datetime.strptime(args.today, "%Y-%m-%d").date()
        if args.today
        else datetime.now(tz).date()
    )
    tomorrow_iso = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    today_iso = today.strftime("%Y-%m-%d")

    by_date = {as_iso(d["date"]): d for d in days}

    target = by_date.get(tomorrow_iso)
    if target is None:
        print(f"No scheduled day for {tomorrow_iso} — bootcamp not started or finished. Nothing to send.")
        return 0

    current = by_date.get(today_iso)
    if current is not None:
        prep = current.get("prep_for_tomorrow") or []
    else:
        # Only happens the night before day 1.
        prep = meta.get("prep_for_day_1") or []

    if not prep:
        prep = ["Nothing to prepare tonight — just show up."]

    subject = f"Day {target['day']} tomorrow — {target['title']}"
    body_html = build_html(target, prep, meta)
    body_text = build_text(target, prep, meta)

    if args.dry_run:
        print(f"Subject: {subject}")
        print(f"Would send for {tomorrow_iso}, prep taken from {today_iso}")
        print("-" * 72)
        print(body_text)
        return 0

    sender = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL") or sender

    if not sender or not password:
        print("GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set.", file=sys.stderr)
        return 1

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body_text)
    msg.add_alternative(body_html, subtype="html")

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(sender, password)
        server.send_message(msg)

    print(f"Sent '{subject}' to {recipient}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
