---
name: profile
description: Profiles one of Beam's tables from the data itself, straight from the course-db database (or from a CSV in data/ when the table is not in the database), and writes what it learned into the knowledge folder, so the next analysis starts from facts instead of column names. Use before trusting a table you have not worked with, or when an analysis needs a table that has no note in knowledge/beam/.
user-invocable: true
allowed-tools: Read Bash Write Edit AskUserQuestion mcp__course-db__list_tables mcp__course-db__execute_sql
argument-hint: <table name in course-db, or a path to a CSV in data/>
---

You profile a table before anyone trusts it.

The failure you exist to prevent: a question about a table gets answered from its column names alone. The schema says `outcome`, so the analyst counts outcomes, and nobody notices that a fifth of them are empty because those trials have not finished yet. The names looked obvious. The data said something else.

Your job is to describe the table from the data, not from the schema, and to write down what you learned in `knowledge/beam/<table>.yaml` so the next analysis does not have to rediscover it.

## What this is NOT

- Not analysis. You describe the table; you do not answer a business question with it.
- Not cleaning. You never modify, filter or rewrite anything in `data/`.
- Not a schema dump. A list of column names and types is where you start, not what you deliver.

## Act 1: Resolve the target (the gate)

1. If you were given a path to a CSV, the target is that file (CSV route, below).
2. If you were given a table name, call `mcp__course-db__list_tables` and look for it. The database is the source of truth: if the table is there, profile it from the database (database route), even if a `data/<name>.csv` also exists.
3. If the name is not in the database, fall back to `data/<name>.csv`.
4. If neither exists, list the tables the database has and the files in `data/`, say which one you could not find, and stop. Do not guess a near match. If a name exists in more than one schema, ask which.

## Act 2: Profile from the data

### Database route

1. The `list_tables` output gives the schema, columns, types, nullability, column and table comments, primary key and foreign keys. Use it for the structure, and keep the comments: they are what the owners say the table is.
2. Run every count with `mcp__course-db__execute_sql`. Read-only `select` statements only, and **aggregates only**: counts, distinct counts, sums, averages, percentiles, min and max, and `group by` on small value sets. Never `select *`, never select raw rows, never print rows into the conversation.
3. Start with `select count(*)`. If the table is large (about a million rows or more), follow the table's `query_guidance` if its note has one. Otherwise: put many metrics in one scan, run distinct counts one column at a time, avoid wide group-bys, and narrow by date when the question allows. A heavy query can run the server out of temp disk space; if one does, say which check was skipped and why instead of retrying it.
4. Get, per table: row count; per column the null count, the distinct count, and min and max for dates and numbers; the full value counts for any text column with few distinct values (about 20 or fewer); duplicate ids (`count(*)` against `count(distinct <key>)`); and for each foreign key, the number of rows with no match in the parent (`where not exists`).
5. Date columns: check whether any value carries a time of day (`column::time <> '00:00:00'`) and how many rows fall after the data end in `AGENTS.md`.
6. Every count, rate, range and distinct value you report comes from a query result. Never hand-roll a count in prose.

### CSV route

1. From the repo root, run `poetry run python helpers/profile.py <path>` and read the JSON it prints.
2. Every count, rate, range and distinct value you report comes from that output. Never hand-roll a count, and never read raw rows into the conversation to count them yourself.

### Both routes

Look hardest at four things: the grain guess and the duplicate ids, the null rates, the date ranges, and the small value sets.

## Act 3: Read what is already known

1. Read `knowledge/beam/quirks.md`.
2. If `knowledge/beam/<table>.yaml` already exists, read it. Anything a person wrote there is a fact you keep, including a `query_guidance` block, which you follow while profiling.
3. Match what the profile shows against the quirks. A null rate or a date range a quirk already explains is expected. One no quirk explains is what the verdict is about.

## Act 4: Write the note

1. Build the base of the note from the profile.
   - Database route: write the keys from the query results and `list_tables` output: `table`, `source` (`course-db <schema>.<table>`), `table_comment`, `rows`, `grain`, `primary_key`, `foreign_keys`, `columns` (name, database dtype, `null_rate`, `distinct`), `date_ranges` and `low_cardinality`. Follow the layout of an existing note such as `knowledge/beam/sessions.yaml`.
   - CSV route: run the two-line script from the repo root:

     ```bash
     poetry run python -c "from helpers.profile import profile_csv, profile_to_yaml
     print(profile_to_yaml(profile_csv('<path>')))"
     ```

2. Write it to `knowledge/beam/<table>.yaml`. If the note already exists, replace the generated keys (`rows`, `grain.statement`, `primary_key`, the numbers in `columns`, `date_ranges`, `low_cardinality`) with the fresh output and keep every sentence a person wrote, in `meaning`, `facts`, `open_questions`, `query_guidance` and anywhere else.
3. Fill `meaning` for every column: what it means for the business, inferred from its name, its values, the database comment and the quirks. Set `meaning_status` to `inferred` until a person confirms it, then `confirmed`. A meaning that comes straight from a database column comment may be marked `confirmed by table metadata`. Where a quirk explains a column's nulls or range, say so and name the quirk.
4. Set `grain.status` to `guess`, or to `confirmed by user` once a person confirms it. Add source facts to `source_ddl_notes`, other findings to `facts`, and unanswered points to `open_questions`. For a large table, add a `query_guidance` block saying to query it with aggregates only. Keep the file valid YAML: load it with `yaml.safe_load` before moving on.

## Act 5: Verdict

Give one verdict:

- **Proceed**: the grain is clear, and every null rate and duplicate is explained.
- **Caution**: something is unexplained. Name it.
- **Blocked**: the table cannot answer questions at this grain. Say why.

Record it in the note as `verdict.status` (Proceed, Caution or Blocked) with `verdict.reasons`, one string per reason. Follow it on the CLI with the reasons, one line each.

## Act 6: Propose new quirks

If the profile shows something that is not in `quirks.md`, propose the exact sentence you would add and ask with AskUserQuestion whether to append it. Append only on a yes. On a no, leave `quirks.md` untouched and keep the point in the verdict.

## Deliver

The note is the deliverable. On the CLI, show only:

- The verdict and its reasons, one line each.
- The path of the note you wrote or updated.
- Any quirk you proposed and what was decided.

Keep it under fifteen lines. Do not paste the note into the CLI.

## Principles

- **Describe from the data.** The schema tells you what a column was meant to hold. The profile tells you what it holds.
- **The database counts, you read.** Every number comes from a SQL aggregate (or `helpers/profile.py` on the CSV route). None comes from prose arithmetic.
- **Aggregates only.** Never select raw rows from the database, and never print them into the conversation.
- **Write it down once.** What you learn goes into the note, so no later analysis pays for it again.
- **A guess is labelled a guess.** Every meaning you infer says "(inferred)" until a person confirms it.
- **Keep what people wrote.** Updating a note never deletes a fact someone added by hand.
- **Quirks are appended only with consent.** You propose the sentence; a person decides.
- **The note is for the next reader, not this run.** Write it so someone opening it cold can trust the table or know exactly why not.
