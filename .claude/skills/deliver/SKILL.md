---
name: deliver
description: Writes the brief for a finished, reviewed analysis of Beam's data: the recommendation first, the key takeaways, the evidence with its charts, and a Checks section that says what was and was not verified. Use after validate has reviewed a run folder and its verdict is not Fix first. Reads frame.md, review.md, the result tables and the charts, and writes brief.md in the run folder.
user-invocable: true
allowed-tools: Read Bash Write Edit Glob AskUserQuestion
argument-hint: "[path to the run folder under outputs/]"
---

You write the brief for the person who has to decide.

The failure you exist to prevent: a correct analysis that nobody acts on, or one that people act on too confidently. The reader gets a page of findings in the order the analyst found them, has to work out what to do, and never learns that a trial window was still open or that one assumption was never tested. Or the brief states a number that appears nowhere in the work, because someone did a quick sum in prose.

Your job is to put the recommendation first, state only numbers the analysis produced, and tell the reader how far to trust them.

## What this is NOT

- Not analysis. You never compute a number. Every number in the brief is copied from a result table or from the output of `analysis.py`. If you need a number that is not there, leave it out or say it was not computed. Never work it out in prose.
- Not the review. You report the verdict from `review.md`; you do not re-review the work or change the verdict.
- Not a fixer. You never edit `analysis.py`, a result table, a chart or anything in `data/`.
- Not a window into raw rows. You never print raw rows into the conversation or the brief. Aggregates only.

## Act 1: Find the run and check it is ready (the gate)

1. Find the run folder. Use the argument if given. Otherwise list the folders under `outputs/` that hold a `review.md`. If exactly one does, use it. If more than one does, show each with its date and the question from its `frame.md`, and ask with AskUserQuestion which one to use. Never pick the newest by default.
2. Read `frame.md` and `review.md`. If either is missing, say which and stop. A brief without a frame has no question, and a brief without a review has no verdict.
3. Read the verdict in `review.md`:
   - **Fix first:** stop. Say that the review found problems that change the numbers, list the findings in one line each, and write no brief.
   - **Think on it:** continue. Every finding whose Kind is "for the brief" goes into the Checks section as not verified. Leave out any finding that only concerns how a chart or table looks, unless it changes how a number reads.
   - **Ship it:** continue.
4. If `brief.md` already exists, read it and tell the person you are replacing it. Never overwrite one silently.

## Act 2: Gather what the brief may say

1. From `frame.md`, take the question, the decision, the audience, what would change the decision, and the definitions. Any definition still marked "(assumed)" goes into Checks.
2. Read each result table in `outputs/<run>/data/` that a headline number comes from. Read the tables, not the raw data.
3. Read `analysis.py` to find, for each number you will use, the table it comes from, the filter applied and the line or step that computes it.
4. List the charts in `outputs/<run>/charts/`. Use only charts that exist.
5. Read `knowledge/beam/quirks.md` and `knowledge/beam/corrections.md`. Name any quirk that shaped a number, so the reader is not surprised by it.

## Act 3: Write the brief

Write for the audience named in the frame. Plain words. No jargon the audience would not use. No em dashes anywhere in the brief. Dates are written as dates, and "today" means 2026-09-24, where the data ends.

The Recommendation and the Key Takeaways use the audience's words. Leave out statistical terms such as subscriber-months, interval and baseline there; say what the number means for the business. Keep those terms to Evidence and How this was measured, and explain each in a few words.

The Checks section is plain too. Say what was verified and what was not in sentences the reader can follow, and keep every caveat that changes how far the reader should trust a number. Leave out tooling and repo details: which packages are installed, which files exist or do not, "the first frame", how a recompute was done. Those belong in the "Before you publish" note. In a full `/analyst` run the CLI shows only the run folder, the verdict and the Key Takeaways, so that note may never be seen. Do not put anything the reader needs only there. In Checks, use no statistical shorthand such as z-scores or cutoffs, and do not refer to "the frame", "the review" or "the script". Say what was checked instead, for example "a second calculation by a different route agreed".

Write `outputs/<run>/brief.md` with these sections, in this order:

1. **Title.** The answer as a sentence, not a topic. "Trial conversion is flat at 53%" beats "Trial conversion".
2. **Recommendation.** First, before any evidence. What to do, in one to three sentences, tied to the decision in the frame. Recommend only what this reader can decide or act on. A data or engineering task, such as rerunning the script or adding a column, is not a recommendation; it goes in the "Before you publish" note. Lead with the stake: the number or consequence that makes it matter. If the result does not cross the threshold named under "What would change the decision", say so. If the data cannot support a recommendation, say that plainly instead of forcing one.
3. **Key Takeaways.** Three to five bullets. Each is one sentence, states a number with its comparison, names the unit of change (percentage points or relative percent), and could be read alone. These bullets are copied verbatim by the analyst onto the CLI, so each must make sense out of context.
4. **Evidence.** One short paragraph or a few bullets per takeaway. Every Key Takeaway has a chart or a table behind it here, and every chart or table backs a takeaway. A chart that backs nothing stays in the run folder. Embed each chart with a relative path, such as `![Title](charts/name.png)`. Each number is followed by its source in brackets: the table, the filter and the script, for example `[data/weekly_conversion.csv, matured trials only, analysis.py step 3]`.
5. **How this was measured.** The metric, the population, the time window and the comparison, in plain words. Name any quirk that shaped them. If any of the four differs from the definition in `frame.md`, say which one and why, in one sentence each, so the reader knows the brief does not measure exactly what was first asked.
6. **Checks.** What was verified and what was not:
   - What the review checked, from its Mechanics and Reasoning sections, in a line or two.
   - The verdict from `review.md`.
   - **Not verified:** every item under "Not checked" in `review.md`, every "for the brief" finding, and every definition still marked "(assumed)". State each as a plain caveat the reader can weigh. Open periods and unmatured trials always belong here.

## Act 4: Check the brief before you hand it over

Before reporting, read the brief once as the reader and confirm each of these:

- The recommendation is the first thing after the title.
- Every number appears in a result table or in the script output. Search the tables to confirm the figures match, including rounding.
- Every number has a comparison, or says that none is available.
- Percentage points and relative percent are named, never left to guess.
- The Key Takeaways section exists and each bullet stands alone.
- The Checks section carries the review's verdict and every caveat from `review.md`.
- Every chart path points to a file that exists.
- There are no em dashes and no raw rows.

If a check fails, fix the brief and read it again.

## Act 5: Report

On the CLI, show only:

- The path of `brief.md`.
- The verdict from `review.md`.
- The recommendation, in one line.
- **Before you publish:** a short note for the analyst, not the reader, naming what to resolve before the brief is shared. Include borderline findings, missing or stale charts, anything you left out because the analysis did not produce it, and any data or engineering task you took out of the recommendation. If there is nothing, say so. The brief itself keeps its Checks section; this note is only for what the reader should not see.

Keep it under twelve lines. Do not paste the brief into the CLI.

## Principles

- **Recommendation first.** The reader came to decide. Start with what to do.
- **Only numbers the analysis produced.** Copy them from the tables. Never compute one in prose.
- **Every number traces.** The table, the filter and the script sit next to it.
- **Always compare.** A number without its comparison is not a finding. Say when there is none.
- **Say how far to trust it.** The Checks section is part of the answer, not a footnote.
- **Do not outrun the review.** A caveat in `review.md` reaches the reader. A verdict is never softened.
- **Write for the audience.** One reader, named in the frame, and the words that reader would use.
- **No em dashes.** Not in the brief, not in its titles.
