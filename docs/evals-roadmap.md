# Podcast Summarizer — LLM Evaluation Roadmap (Langfuse)

Audience: beginners. Goal: a reliable, mostly automated evaluation setup that improves your summaries over time while you keep manual control over promotions.

Top priorities we’ll optimize (in order):
- Actionability/usefulness
- Conciseness
- Faithfulness to the transcript

You have two output modes:
- Catch‑up: brief topical digest + “where to read more.”
- How‑to: concise step‑by‑step instructions to replicate guest processes/tooling.

---
## Quick glossary (plain English)
- Dataset: a named list of test cases you’ll re-run repeatedly. Use it to compare prompts/models.
- Dataset item: one test case (one episode). Minimal fields: title, transcript text, desired_style (catchup or howto). Optional: feed metadata, word limits, expected_output for gold items.
- Evaluator: a check that grades a summary. Can be automated (LLM-as-judge), human (you), or custom code.
- Score: a single metric saved in Langfuse by an evaluator (e.g., `actionability_score: 4.5`).
- Experiment: run a dataset through your app with a specific prompt/model; apply evaluators; compare results.
- Offline evaluation: controlled tests on datasets (repeatable, great for CI and safe comparison).
- Online evaluation: signals from real usage (thumbs up/down, comments, occasional A/B canaries).
- Generation: the single LLM call that writes a summary. Trace: the whole pipeline for an episode (download → transcribe → clean → summarize).
- Prompt version: a saved template in Langfuse Prompts with a label (e.g., `production`, `candidate`).

---
## Architecture decisions (so everything is consistent)
- Maintain two prompts in Langfuse Prompts:
  - `summarization-catchup`
  - `summarization-howto`
- Style routing: use a feed-level default, with a simple episode-title heuristic override (e.g., titles containing “how to”, “workflow”, “setup” → howto; otherwise catchup). Save the chosen `desired_style` in the trace metadata.
- Deterministic sections (always present):
  - TL;DR (strict word cap)
  - Catch‑up: Key topics (bullets) + “Where to read more” (links)
  - How‑to: Step‑by‑step (bullets with verbs) + Pitfalls/Notes
  - References & Tools (links, products, frameworks)

---
## Phase 0 — Instrumentation baseline
- What this is (newbie): Add labels/tags so every run is traceable and comparable later.
- What you do: Record on each generation: `feed_id`, `feed_title`, `desired_style`, `transcript_length`, `summary_word_count`, `compression_ratio`, `model`, `prompt_version`. Ensure you can attach Scores later (keep generation/trace IDs around).
- Why it helps: Lets you slice results by feed/style, track improvements, and attach feedback properly.
- Deliverables: Consistent metadata on each generation; Langfuse traces already captured via `@observe` and `langfuse.openai`.

---
## Phase 1 — Datasets (create ~5; start small and iterate)
- What this is (newbie): A dataset is a list of episodes you’ll use for testing. You run them again and again to see if a new prompt/model is better.
- What is an “item”: One episode’s test case. Minimum fields:
  - `title` (the episode title)
  - `transcript` (plain text; paste or load from your DB)
  - `desired_style` (either `catchup` or `howto` — what you want the summary to look like)
  - Optional but helpful: `feed_id`, `feed_category`, word limits per section (e.g., `max_words_tldr`), and notes about tricky content.
  - Later for “Gold” items, you can add `expected_output` or your human Scores.
- Why it helps: Gives you a stable, repeatable test-bed, so changes are measured, not guessed.
- Datasets to create:
  - DS‑1 `CatchUp_v1` (15–30 items): recurring shows suited for brief digests.
  - DS‑2 `HowTo_v1` (15–30 items): episodes with concrete, reproducible workflows.
  - DS‑3 `Smoke_v1` (8–10 items): quick mixed set for fast checks and PRs.
  - DS‑4 `HardCases` (start empty): add items that fail online or via evaluators.
  - DS‑5 `Gold_v1` (start 5, grow to ~20): you’ll human‑annotate these.
- Example dataset item (Catch‑up):
  ```json
  {
    "title": "Acquired: OpenAI’s latest moves and market dynamics",
    "transcript": "<paste full transcript text here>",
    "desired_style": "catchup",
    "feed_id": "acquired_fm",
    "feed_category": "startups",
    "max_words_tldr": 80
  }
  ```
- Example dataset item (How‑to):
  ```json
  {
    "title": "How we scaled our AI data pipeline to 100M events/day",
    "transcript": "<paste full transcript text here>",
    "desired_style": "howto",
    "feed_id": "data_engineering_hour",
    "feed_category": "ai/ops",
    "max_words_tldr": 60
  }
  ```

---
## Phase 2 — Evaluators & Scores (what we measure)
- What this is (newbie): After your app generates a summary, evaluators grade it. Each grade is a Score saved in Langfuse (like a spreadsheet column).
- Why it helps: Turn fuzzy opinions into clear numbers you can compare.
- Use LLM-as-a-Judge for automation (it reads the transcript + summary and outputs numbers), plus occasional human ratings from you.
- Evaluators to create (with suggested Score keys):
  - Actionability (`ev_actionability_v1`): 1–5. For how‑to: are steps replicable and complete? For catch‑up: useful quick context?
    - Scores: `actionability_score`, `actionability_notes`
  - Faithfulness (`ev_faithfulness_v1`): 1–5. Are claims grounded in the transcript?
    - Scores: `faithfulness_score`, `hallucination_count`, `hallucination_examples`
  - Conciseness (`ev_conciseness_v1`): 1–5. Minimal redundancy; meets word caps.
    - Scores: `conciseness_score`, `redundancy_notes`
  - Format adherence (`ev_format_v1`): binary + 1–5. Required sections present and correct.
    - Scores: `format_adherence` (0/1), `format_score`, `missing_sections`
  - Category match (`ev_category_match_v1`): binary. Did the output follow the intended style?
    - Scores: `category_match` (0/1), `predicted_category`
  - Coverage (`ev_coverage_v1`): 1–5. Key topics covered; for how‑to: major phases captured.
    - Scores: `coverage_score`, `missed_topics`
  - Pairwise preference (`ev_preference_v1`): Given A vs B, which is better for your rubric?
    - Scores: `preference_winner` ("A"/"B"), `preference_strength` (1–3), `preference_reason`
  - Manual rating (`ev_manual_rating`): your occasional human rating.
    - Scores: `human_actionability`, `human_faithfulness`, `human_conciseness`, `human_notes`
  - Auto/custom (no judge): quick counters
    - Scores: `word_count`, `compression_ratio`, `references_count` (URLs + tools), `tools_count`
- One composite metric for dashboards:
  - `WeightedQuality = 0.5*actionability + 0.3*faithfulness + 0.2*conciseness` (range 1–5)

---
## Phase 3 — Baseline experiments
- What this is (newbie): A snapshot of how your current setup performs on your datasets today.
- What you do: Run Experiments on DS‑1/DS‑2/DS‑3 with your production prompt/model; apply the evaluators above.
- Why it helps: Establishes “before” numbers so you can tell if changes are real improvements.
- Deliverables: Saved experiment runs, e.g., `baseline-catchup-v1`, `baseline-howto-v1`.

---
## Phase 4 — Prompt structure hardening
- What this is (newbie): Split the single prompt into two strict templates (catch‑up vs how‑to) with mandatory sections and word caps.
- What you do: Create `summarization-catchup` and `summarization-howto` prompts in Langfuse; require TL;DR, section bullets, and a final References & Tools list.
- Why it helps: Increases consistency, makes format adherence ~automatic, and improves conciseness.
- Deliverables: Two prompts labeled (e.g., `production` and `candidate-*`).

---
## Phase 5 — Offline optimization loop
- What this is (newbie): Try multiple prompt/model variations and compare on datasets.
- What you do: Vary prompt wording/section caps, models, and decoding settings (temperature, max_tokens). Use pairwise preference on DS‑3/DS‑4.
- Why it helps: Find versions that score higher before touching production.
- Gating criteria for a “candidate” to move forward:
  - `format_adherence ≥ 0.9`
  - `WeightedQuality ≥ 4.0` on DS‑1 and `≥ 4.1` on DS‑2
  - `faithfulness ≥ 4.2`; `hallucination_count ≤ 1` per summary
  - `conciseness ≥ 4.0` and meets word caps
  - No regression on DS‑4 HardCases by > 0.2 vs baseline

---
## Phase 6 — Gold dataset & judge calibration
- What this is (newbie): A small set you personally rate once; it becomes ground truth to sanity‑check the automated judges.
- What you do: Add 5–20 “Gold” items in DS‑5; record your human Scores. Compare judge vs human scores (directionally we want a decent correlation).
- Why it helps: Ensures the judge aligns with your taste and goals.

---
## Phase 7 — Online evaluation & A/B (lightweight)
- What this is (newbie): Collect real‑use feedback and try small canaries before promoting changes.
- What you do: Add thumbs up/down + optional comment to the episode page. Save as Scores on the generation (`online_thumb` −1/0/+1, `feedback_comment`).
- A/B canary: Serve the best “candidate” to 10–20% of episodes for 1–2 weeks.
- Online gates to pass vs control:
  - Thumbs‑up rate not worse by > 3% absolute
  - No spike in faithfulness‑related negative comments
  - Periodic offline preference test on new episodes doesn’t flip against the candidate
- You still manually promote prompt versions in Langfuse when gates pass.

---
## Phase 8 — Automation (nightly/weekly)
- Nightly: run DS‑3 `Smoke_v1` for current candidates; notify if gates fail.
- Weekly: run DS‑1/DS‑2 comparing `production` vs top `candidate-*`.
- Auto‑append poorly performing online episodes to DS‑4 `HardCases` and include HardCases in every experiment.

---
## Phase 9 — Dashboards & monitoring
- Create Langfuse saved views by style (`catchup` / `howto`) to track:
  - `WeightedQuality` trend
  - `format_adherence %`, `faithfulness`, `hallucination_count`
  - `conciseness` and word cap compliance
  - `online_thumb` rate and negative comment flags
  - Breakdown by `feed_id` / `feed_category`

---
## Phase 10 — Iteration backlog
- Style router improvements (title heuristics → better routing; monitor `category_match`).
- Entity/Tool extraction emphasis: ensure named tools/frameworks are captured; track `tools_count` and missed tools.
- Optional later: add timestamps section and a format/coverage check for it.

---
## Gates & targets (cheat‑sheet)
- `format_adherence ≥ 0.9`
- `actionability ≥ 4.0` (early Catch‑up ≥ 3.8 acceptable), `faithfulness ≥ 4.2`, `conciseness ≥ 4.0`
- `WeightedQuality ≥ 4.0`; no HardCases regression > 0.2 vs baseline
- Online thumbs‑up rate: not worse by > 3% absolute during canary

---
## Your next 5 concrete actions
1) In Langfuse, create DS‑1/DS‑2/DS‑3 and add ~10 items each (paste titles + transcripts; set `desired_style`).
2) Create evaluators listed above with exactly the Score keys (so dashboards aggregate cleanly).
3) Split your prompt into `summarization-catchup` and `summarization-howto` with strict sections and word caps.
4) Run baseline experiments on DS‑1/DS‑2/DS‑3; add 5 hard items to DS‑4 from the worst outputs.
5) Add thumbs + comment UI; save as Scores on generations; start collecting online signals.

---
## Appendix A — Example item templates (copy/paste)
Catch‑up item (minimum fields):
```json
{
  "title": "<episode title>",
  "transcript": "<full transcript text>",
  "desired_style": "catchup"
}
```
How‑to item (with optional fields):
```json
{
  "title": "<episode title>",
  "transcript": "<full transcript text>",
  "desired_style": "howto",
  "feed_id": "<feed>",
  "feed_category": "<domain>",
  "max_words_tldr": 60
}
```

---
## Appendix B — Evaluator rubrics (short)
- Actionability (1–5):
  - How‑to: steps are clear, ordered, and reproducible; includes tools/configs; minimal gaps.
  - Catch‑up: quickly tells me what happened and why it matters.
- Faithfulness (1–5): claims match transcript; 0–1 minor hallucinations only.
- Conciseness (1–5): no fluff; meets word caps; avoids repetition.
- Format adherence (0/1 + 1–5): all required sections present and correctly formatted.
- Coverage (1–5): key topics/major phases included; few misses.
- Category match (0/1): output matches the requested style.
- Pairwise preference: pick the better of A vs B for the above goals and explain briefly.

---
## Appendix C — Score keys (use exactly these)
- actionability_score, actionability_notes
- faithfulness_score, hallucination_count, hallucination_examples
- conciseness_score, redundancy_notes
- format_adherence, format_score, missing_sections
- category_match, predicted_category
- coverage_score, missed_topics
- preference_winner, preference_strength, preference_reason
- human_actionability, human_faithfulness, human_conciseness, human_notes
- word_count, compression_ratio, references_count, tools_count
- online_thumb, feedback_comment
- WeightedQuality (computed in dashboards)

