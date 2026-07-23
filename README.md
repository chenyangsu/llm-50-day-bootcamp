# 50-Day LLM Bootcamp

A day-by-day study plan taking you from backpropagation to building, fine-tuning and honestly evaluating a
language model. 24 July – 11 September 2026.

**Site:** <https://chenyangsu.github.io/llm-50-day-bootcamp>

Fifty days, each sized for three to four focused hours. Six study days then a catch-up day, seven times
over, then a capstone. Every day page carries its own objectives, timed tasks with checkboxes that
persist in your browser, every link it needs, a deliverable, a checkpoint question, and the two-to-four
things worth doing the night before.

## Layout

```
data/schedule.yml       Single source of truth. All 50 days.
scripts/build.py        schedule.yml -> days/*.qmd, timeline.qmd, resources.qmd, _includes/site-js.html
scripts/progress.js     Checkbox persistence and the "today is day N" banner. Inlined by build.py.
_quarto.yml             Site config (cosmo / darkly, navbar, search).
styles.css              Day cards, task list, timeline, phase grid.
index.qmd               Landing page.
setup.qmd               Day 0: Python, PyTorch, GPU, accounts, repos to clone.
milestones.qmd          The five deliverables and what makes each one good.
assessment.qmd          Self-check questions per phase, plus the day-50 list.
timeline.qmd            Generated — all 50 days at a glance.
resources.qmd           Generated — every link, grouped by kind.
days/day-01.qmd …       Generated — one page per day.
```

Generated files are committed so the site builds with Quarto alone, no Python step in CI.

## Changing the schedule

Edit `data/schedule.yml`, then regenerate:

```bash
python3 scripts/build.py
```

Never edit `days/*.qmd`, `timeline.qmd`, `resources.qmd` or `_includes/site-js.html` directly — the next
build overwrites them.

A day record looks like this:

```yaml
- day: 3
  date: "2026-07-26"
  weekday: Sunday
  week: 1
  phase: Foundations
  kind: study            # study | catchup | milestone | capstone
  title: The Value object and the expression graph
  hours: 3-4 h
  why: One sentence on what this day unlocks.
  objectives: [...]      # 2-3 checkable claims
  tasks:
    - text: What to actually do.
      minutes: 75
  resources:
    - label: micrograd lecture
      url: https://www.youtube.com/watch?v=VMj-3S1tku0
      kind: video        # textbook | video | paper | course | repo | tool | reference
  deliverable: The artifact you should have by the end of the day.
  checkpoint: The question you must be able to answer without notes.
  prep_for_tomorrow: [...]   # 2-4 ten-minute items; this is what the evening email sends
```

`prep_for_tomorrow` on day N describes how to prepare for day N+1. Day 50's is empty. The items for the
night before day 1 live in `meta.prep_for_day_1`.

## Local preview

Quarto is the only dependency for rendering; PyYAML is the only one for regenerating.

```bash
quarto preview          # live reload at localhost:4200
quarto render           # writes _site/
```

## The daily email

`.github/workflows/daily-reminder.yml` runs `scripts/send_reminder.py` every evening at 8:11 pm
America/Winnipeg (cron `11 1 * * *` UTC — Winnipeg holds CDT, UTC−5, for the whole bootcamp). The script
reads `data/schedule.yml`, works out tomorrow's date, and emails the `prep_for_tomorrow` items from
*today's* record together with a preview of tomorrow. After 11 September no day matches and it sends
nothing.

Editing the schedule and pushing is enough to change what the emails say — there is nothing to keep in
sync by hand.

### Setup

Three repository secrets, under Settings → Secrets and variables → Actions:

| Secret | Value |
|:--|:--|
| `GMAIL_ADDRESS` | the Gmail account that sends |
| `GMAIL_APP_PASSWORD` | a Google **app password**, not your account password — requires 2-Step Verification, generated at <https://myaccount.google.com/apppasswords> |
| `RECIPIENT_EMAIL` | optional; defaults to `GMAIL_ADDRESS` |

### Testing without sending

```bash
python3 scripts/send_reminder.py --dry-run                    # tonight's email
python3 scripts/send_reminder.py --dry-run --today 2026-08-19 # any date
```

The workflow also has a manual trigger (Actions → Daily reminder email → Run workflow) with `dry_run` and
`today` inputs, so you can exercise the real send path on demand.

An earlier version used a Claude cloud routine instead. It could read the schedule but never sent
anything — connector tools were not reachable from the scheduled cloud session — so it is disabled at
<https://claude.ai/code/routines> and SMTP replaced it.

### One caveat

GitHub disables scheduled workflows in a repository after 60 days without activity. The bootcamp is 50
days, so it fits, but if the repo goes completely quiet the schedule can be switched off — any commit
resets the clock, and the Actions tab shows a banner if it happens.

## Deployment

Pushing to `main` triggers `.github/workflows/publish.yml`, which renders with Quarto and publishes
`_site/` to the `gh-pages` branch. Pages must be set to serve from `gh-pages` (Settings → Pages → Branch:
`gh-pages`, folder `/`).
