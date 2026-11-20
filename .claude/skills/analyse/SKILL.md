---
name: analyse
description: Answers a framed business question about Beam's data, using aggregate SQL against the course-db database and one pandas script that can be rerun, where every headline number carries its comparison. Use after a question has been framed, when it is time to compute the answer. Reads the frame note in the run folder under outputs/ and writes the script, result tables and charts next to it.
user-invocable: true
allowed-tools: Read Bash Write Edit Glob AskUserQuestion mcp__course-db__list_tables mcp__course-db__execute_sql
argument-hint: "[path to the run folder under outputs/]"
---

You answer the framed question with code that can be rerun.

The failure you exist to prevent: a confident number with no baseline, or a number that came out of a chain of arithmetic written in prose that nobody can check. "Trial conversion is 50%" tells a reader nothing until it says 50% against what. And a number computed in the conversation cannot be rerun, reviewed or corrected. The answer might even be right. Nobody can tell.

So the model reasons and the code computes. You decide what to compute and what to compare it with. A script in the run folder does every count, rate, check and chart.

## What this is NOT

- Not the brief. You report numbers on the CLI; the Deliver step writes the brief.
- Not the review. You run the checks your plan needs; the Validate step reviews the work.
- Not a notebook. The output is one script that runs top to bottom.
- Not a window into raw rows. You never print raw rows into the conversation. SQL queries return aggregates only, and the script prints aggregates only.
- Not a data editor. You never modify anything in `data/`, and you only run read-only `select` statements against the database.

## The rules

These hold in every act.

- **A number alone is not a finding.** Every headline number carries a comparison: a prior period, a segment, or a benchmark.
- **If no comparison exists, say "no comparison available".** Never invent a baseline to fill the gap.
- **Segment before you average** when the frame or a quirk suggests groups behave differently. An average over groups that move in opposite directions hides both.
- **Percentage points and relative percent are different numbers.** A rate going from 40% to 44% is up 4 percentage points and up 10% relative. Name which one you mean, every time.
- **Never trust a period that has not closed.** A month still in progress, or any record whose outcome is still open (see `quirks.md`), is not a result yet.

## Act 1: Find the question (the gate)

1. Find the run folder. Use the argument if given. Otherwise use the newest folder under `outputs/` that holds a `frame.md`.
2. Read `frame.md` for the question, the decision it informs, the audience, and what would change the decision.
3. If there is no frame note, ask with AskUserQuestion for the question and the decision it informs. Then write `outputs/<YYYY-MM-DD>_<slug>/frame.md` yourself before anything else, with the same fields the Frame step writes: question, decision, audience, what would change the decision, and the tables likely involved. Get the date with `date +%F`; never guess it.
4. Never proceed on a guessed question. You may confirm a question you infer; you may not assume one.

## Act 2: Load the context

1. Read `knowledge/beam/quirks.md`, `knowledge/beam/corrections.md`, and `knowledge/beam/<table>.yaml` for each table involved. Obey any `query_guidance` in a table note: a large table is queried with aggregates only.
2. If a table involved has no note, run the profile skill on it first: read `.claude/skills/profile/SKILL.md` and follow it, then come back here.
3. Call `mcp__course-db__list_tables` if you need to confirm a table or column exists in the database. The database is the source of truth; use `data/*.csv` only for a table the database does not have.
4. Say in one line which quirks apply to this question, and which corrections, if any.

## Act 3: Plan

Write three to six bullets describing the computation. The plan must say:

- What each headline number is and the comparison it will carry (prior period, segment or benchmark), or that none exists.
- How each applicable quirk is handled. Take them from `knowledge/beam/quirks.md`: apply each rule it gives for the tables involved, and name any listed anomaly that enters a comparison.
- Which segments you will split by and why.
- Which checks the script will run.
- Which aggregate queries pull the data, and at what grain (for example by month and plan), so the script can compute rates, comparisons and checks from the result tables.

Show the plan before writing the script.

## Act 4: Pull the data, write and run the script

### Pull the data from the database

1. Write each query to `outputs/<run>/queries.sql`, one block per result, headed by a comment `-- name: <name>`. Read-only `select` only. Aggregate in SQL to the grain the plan needs (by day, month, plan, segment) and return only that small table. Never `select *`, and never pull session-level or other row-level data. Apply the quirks' filters in the SQL (for example `session_date <= '2026-09-24'`, closed periods only, scheduled starts excluded).
2. Run each query with `mcp__course-db__execute_sql` and save its result exactly as returned, with no edits, to `outputs/<run>/data/raw_<name>.csv`. If a query fails (for example a large table runs the server out of temp disk space), narrow it with a date filter or split it, and say so in the report. Do not retry the same query unchanged.
3. For a join, check the fan-out in SQL (row count or distinct key count before and after the join) and record the result, because `helpers.checks.join_fan_out` needs the rows themselves.

### Write the script

Write one script at `outputs/<run>/analysis.py`:

1. Read the `outputs/<run>/data/raw_*.csv` result tables with pandas, and `data/*.csv` for any table the database does not have.
2. Use `helpers.checks` for at least the checks the plan needs: `date_boundaries` for partial periods at the edges, `matured_only` for windows that have not closed, `join_fan_out` where a join happens in pandas, `parts_sum_to_total` when segments should add back to a total. Print each check's `summary`.
3. Save each result table to `outputs/<run>/data/<name>.csv`.
4. Make charts only through `helpers.charts`: `bar` or `line`, then `save` into `outputs/<run>/charts/<name>.png`. Every title states the takeaway the chart proves, not a label.
5. Print the headline numbers, each with its comparison, and the check summaries. Print aggregates only.

Run it from the repo root with `poetry run python outputs/<run>/analysis.py`. If it fails, fix it and rerun until it runs clean. If a check fails, decide whether it changes the answer and fix the script or report it. If the data cannot answer the question, say so plainly and stop.

The script reruns from the saved result tables. Refreshing them means rerunning `queries.sql`; the script itself has no database connection.

## Act 5: Report

On the CLI, report:

- Each headline number with its comparison, stated as percentage points or relative percent, saying which.
- What was segmented and why.
- Which checks ran and what each said.
- Which queries ran, and any that failed or were narrowed.
- What was not checked.
- The path of the run folder.

Keep it under twenty lines. No brief here; the Deliver step writes the brief.

## Principles

- **The question is the gate.** No frame note, no analysis. Ask; never guess.
- **The model reasons, the code computes.** Every number comes out of `analysis.py`. None comes from prose arithmetic.
- **Always compare.** A number without its comparison is not a finding. When there is no comparison, say so.
- **Quirks first.** Read what is known about the tables before computing anything, and say how each applicable quirk was handled.
- **Closed periods only.** An open month or a record whose outcome is not yet known (see `quirks.md`) is not a result.
- **Name the unit of change.** Percentage points or relative percent, never left for the reader to guess.
- **Aggregates from the database, arithmetic in code.** SQL returns small aggregate tables; the script computes every number from them.
- **Rerunnable or it did not happen.** Anyone can run the script again and get the same tables, charts and numbers, and `queries.sql` shows exactly where the data came from.
- **Say what you did not check.** A gap you name is safer than one a reader finds later.
