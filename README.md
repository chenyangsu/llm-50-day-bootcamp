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

A Claude cloud routine fires every evening at 8:11 pm America/Winnipeg (cron `11 1 * * *` UTC — Winnipeg
holds CDT, UTC−5, for the whole bootcamp). It clones this repo, reads `data/schedule.yml`, works out
tomorrow's date, and emails the `prep_for_tomorrow` items from today's record along with a summary of
tomorrow. After 11 September it finds no matching day and sends nothing.

Because it reads the YAML from `main`, editing the schedule and pushing is enough to change what the
emails say — there's nothing to keep in sync by hand.

Manage or disable it at <https://claude.ai/code/routines>.

## Deployment

Pushing to `main` triggers `.github/workflows/publish.yml`, which renders with Quarto and publishes
`_site/` to the `gh-pages` branch. Pages must be set to serve from `gh-pages` (Settings → Pages → Branch:
`gh-pages`, folder `/`).
