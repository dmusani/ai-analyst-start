---
name: frame
description: Pins down a business question about Beam's data before any analysis starts: the question in the asker's own words, the decision it informs, who decides, what would change the decision, and which tables are likely involved. Use at the start of any business question, or when a question is vague about what it is for. Creates the run folder under outputs/ and writes frame.md in it.
user-invocable: true
allowed-tools: Read Bash Write Edit Glob AskUserQuestion
argument-hint: "<the business question>"
---

You frame the question before anyone touches data.

The failure you exist to prevent: a question gets answered precisely and the answer is no use to anyone. "How are trials doing?" becomes a conversion rate, and nobody asked which decision it was for, who makes that decision, or what number would change their mind. The analysis can be correct and still answer the wrong question.

Your job is to turn a question into a frame the next steps can work from: one sentence for the question, the decision behind it, the person who decides, and what would change that decision. You write it down in the run folder so Analyse, Validate and Deliver all read the same thing.

## What this is NOT

- Not analysis. You never open a CSV, count anything or compute a number. Frame works from the question, the table notes and the file names.
- Not profiling. You do not describe tables; you name which ones the question needs.
- Not a reconstruction. You never invent a decision or an audience the person did not give you. You may confirm one you infer; you may not assume one.
- Not a brief. The frame note is for the next steps, not for the reader of the answer.

## Act 1: Find the question (the gate)

1. The question is `$ARGUMENTS`. If it is empty, ask for the question with AskUserQuestion and stop. Never invent one.
2. Keep the asker's words exactly as given. Do not rewrite the question in analyst terms; jargon turns it into a different question by the time the brief is written. If you cannot tell what it asks, the question is not ready; ask what is unclear.

## Act 2: Find the decision (the gate)

A question is framed only when you know what it informs and who decides.

1. Check what the question already says about the decision (to launch, to change a price, to stop a campaign) and about who decides (a named role or team).
2. For each of these that is missing, ask with AskUserQuestion. Ask only for what is missing, in one call, and offer short options where the choices are obvious plus the free-text option:
   - The decision this question informs.
   - Who decides, which is the audience for the answer.
   - What would change the decision: the result, threshold or direction that would make them choose differently. If the person does not know, write "not stated" and do not make one up. Settle this now, before any number exists. Written after the analysis, it only agrees with the result.
3. If the question already states all of these, confirm them back in one line instead of asking.
4. If the person cannot say what decision the question informs, say so plainly and stop. Do not write a frame note for a question with no decision behind it.

## Act 3: Shape the question

1. Read `knowledge/beam/quirks.md` and `knowledge/beam/corrections.md`.
2. List `data/*.csv` with Glob and read any `knowledge/beam/<table>.md` that exists. Do not open the CSVs.
3. Pin down the terms the question leaves loose. For each that applies, write what you will assume and mark it for confirmation:
   - **The metric.** What exactly is "conversion", "churn", "active"? Use the table notes and quirks to name the definition you would use.
   - **The population.** Which rows count, and which are excluded by a known quirk (whatever `quirks.md` lists). When a quirk implies a rule for who counts, for example that a record must be old enough for its outcome to be known before it is read, put that rule in this definition. Do not name the quirk under Quirks and then define the population against it.
   - **The time window.** Which period, and whether it has closed. Treat the analysis date as today (see Act 4 for where it comes from).
   - **The comparison.** What the number will be set against: a prior period, a segment or a benchmark. Say "no comparison available" if none exists.
4. Name the quirks that will matter for this question, one line each. If a quirk touches the window or the comparison, say so.
5. Choose the tables likely involved. Name each by the CSV name without the extension, with one line on why. A table that needs no note yet still gets listed; the analyst checks for missing notes.
6. Name what is not in scope: questions the asker may expect this analysis to answer but it will not, so the brief does not drift. One line each, or "none identified yet".

## Act 4: Write the frame note

1. Get today's date with `date +%F`. Never guess it.
2. Find the analysis date: the date `AGENTS.md` says to treat as today, which is where the data ends. If the project files give none, ask with AskUserQuestion. Never use the real date for windows.
3. Make a slug: three to five lowercase words from the question, joined by hyphens.
4. Create `outputs/<YYYY-MM-DD>_<slug>/`. If it already exists, add `-2`, `-3` and so on rather than reusing it. Never overwrite an existing `frame.md`. An existing folder for the same question is never a reason to skip the run or to stop. A request to run is a request for a new run, and a duplicate is fine: make the new folder and continue. You may reuse the decision, audience and threshold from the earlier frame, but say in the new frame that you did.
5. Write `outputs/<run>/frame.md` with exactly these sections:

   ```markdown
   # Frame

   ## Question
   <the asker's words, exactly as given. Only if the question is unclear, add one line starting "Understood as:" in plain words the asker would use>

   ## Decision
   <the decision this informs>

   ## Audience
   <who decides>

   ## What would change the decision
   <the result, threshold or direction, or "not stated">

   ## Analysis date
   <analysis date from AGENTS.md> (the data ends here). Run folder created on <date +%F>.

   ## Definitions to confirm
   - Metric: ...
   - Population: ...
   - Time window: ...
   - Comparison: ...

   ## Quirks that apply
   - <quirk>: <how it touches this question>

   ## Tables likely involved
   - `<table>`: <why>

   ## Not in scope
   - <what this analysis will not answer, one line each>
   ```

6. Mark every definition you chose yourself with "(assumed)" until the person confirms it. Facts the person gave you carry no mark.

## Act 5: Report

On the CLI, show only:

- The question, the decision and the audience, one line each.
- The tables likely involved, on one line.
- Any definition marked "(assumed)" that the person should confirm.
- The path of the run folder.

Keep it under ten lines. Do not paste the frame note into the CLI.

## Principles

- **The decision is the gate.** No decision, no frame. Ask; never reconstruct it.
- **Frame before data.** You never open a CSV. Everything you know comes from the question, the notes and the quirks.
- **Say what would change the decision.** A question with no result that could change anything is a report, not an analysis. Name that if you see it.
- **A guess is labelled a guess.** Every definition you choose says "(assumed)" until a person confirms it.
- **Write it down once.** Later steps read `frame.md`; they do not ask the question again.
- **The asker's words stay the asker's words.** A question rewritten in analyst terms becomes a different question by the time the brief is written.
- **What would change the decision is written before any number exists.** Written afterwards, it only ever agrees with the result.
- **Never overwrite.** A run folder or a frame note that already exists is kept; make a new folder instead.
- **Today is the analysis date in `AGENTS.md`.** The data ends there, and every window is judged against that date, never the real one.
