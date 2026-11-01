# Evaluation and Results

**Project:** Personal AI Coworkers  
**Evaluation evidence:** Local terminal results and generated reports from October 27–29, 2026  
**Scope:** Functionality, recommendation quality proxies, persisted feedback, and career-coach grading behavior.

## 1. Evaluation approach

The two agents have different success criteria:

| Agent | What we measured | Why it matters |
|---|---|---|
| DailyTechUpgradeAgent | Article count, URL uniqueness, required metadata presence, recency, publisher diversity, marked-read count | Checks freshness, traceability, novelty, and continued use |
| Career Coach | Session persistence, answer evaluation count, topic/session scores, feedback contents, negative and positive answer tests | Checks functioning interviews and whether grading responds sensibly to answer quality |
| Opportunity discovery | Live board retrieval and classifier unit tests | Checks whether opportunity labels are relevant and avoids title false positives |

These are **prototype-level measures**, not proof of factual accuracy, recommendation optimality, or predictive hiring performance.

## 2. DailyTechUpgradeAgent — recorded results

Command: `python -m evaluations.evaluate_articles`

| Metric | Observed result |
|---|---:|
| Initial discovered articles | 30 |
| Total stored recommendations at evaluation | **12** |
| Unique article URL rate | **100.0%** |
| Required metadata completeness | **100.0%** |
| Published within previous 30 days | **100.0%** |
| Distinct publishers | **3** |
| Articles marked completed | **1** |

The source pool shown in the terminal included AWS, Google Research, and Microsoft Research. The workflow retrieved actual article bodies before generating briefs; previously demonstrated extraction lengths were approximately 4,990–7,437 characters for three selected pages. A subsequent run reported that a brief for the current day already existed, confirming the date-based duplicate-run guard.

**Interpretation:** The recorded output supports functional discovery, deduplication, recency filtering outcomes, and durable read tracking. Here, “metadata completeness” means the fields were nonempty—not that each publication date or URL was independently verified. The 100% values are based on the 12 stored recommendations at that point, not all possible articles.

**Not yet measured:** Expert ratings of article relevance, factual accuracy of each summary against its source, diversity over many weeks, true reading time, and whether daily learning improves future performance.

## 3. Career Coach — recorded results

### 3.1 Early development sessions: intentional negative tests

Command: `python -m evaluations.evaluate_career`

An earlier terminal evaluation, **before Session 6**, produced:

| Metric | Recorded value |
|---|---:|
| Interview sessions | **5** |
| Evaluated answers | **20** |
| Mean recorded answer score | **6.17/100** |
| Session 1 | 10.0/100 |
| Session 2 | 6.0/100 |
| Session 3 | 11.25/100 |
| Session 4 | 2.08/100 |
| Session 5 | 0.0/100 |

The student intentionally supplied short, incomplete, and sometimes nonresponsive answers (for example, a function signature without implementation or simply “No”) to test whether the agent would assign appropriately low scores and give a correction path. These scores **must not be interpreted as a baseline of the student's actual technical ability**. Some sessions included follow-up evaluation results; consequently, “evaluated answers” is not necessarily synonymous with distinct original interview questions.

### 3.2 Session 6: substantial-response positive test

Evidence: `outputs/career_readiness_session_6.md` and the full October 29 CLI transcript. Role: **Software Engineering Intern — Backend & Platform Engineering**, Example Technologies (synthetic description, not an employer posting).

| Topic / task | Agent score | Observed answer behavior |
|---|---:|---|
| Python: reverse a singly linked list | **92.5/100** | Correct iterative pointer reversal with `prev`, `curr`, and a saved next pointer |
| Backend architecture: authentication and sessions | **86.5/100** | API gateway, auth service, PostgreSQL, Redis, short-lived access tokens, refresh rotation, password hashing |
| Distributed systems: high-scale rate limiting | **86.5/100** | Token bucket, Redis atomic Lua script, local token reservations, lazy refill and failure considerations |
| **Session 6 average** | **88.5/100** | Three substantial technical answers were graded and persisted |

The linked-list solution is functionally correct for empty, single-node, and multi-node lists, with **O(n)** time and **O(1)** extra space. The evaluator accurately praised its pointer manipulation and noted the omission of explicit complexity discussion. For authentication, the evaluator requested greater depth on token compromise, session invalidation, and logging. For rate limiting, it identified synchronization and enforcement-granularity trade-offs.

**Independent review caveat:** The answers are strong on their face, so the high grades are directionally plausible; however, the grader was not benchmarked against a human-scored rubric. In particular, local rate-limit token reservations require atomic accounting at the central store, and fail-open behavior trades security for availability. A proposed “98%” Redis call reduction is an illustrative batch-size calculation, not measured production throughput.

**Important interpretation:** Session 6 demonstrates that the grader produces different feedback and scores for substantial versus deliberately incomplete submissions. The contrast is **not a measured learning gain**, because the early answers were intentionally poor. The evaluation also does not establish whether answers were produced unaided.

### 3.3 Reports and persistence

The Session 6 workflow logged `Assessment saved!`, `Session ID: 6`, and `Report generated: outputs/career_readiness_session_6.md`. The report shows all three topic scores, the 88.5 average, strengths, resources, and a seven-day plan. The underlying report generator computes the latest session's topic averages and writes Markdown from saved SQLite results.

**Limitation:** The current seven-day plan is a fixed list (Python, linked lists, REST APIs, SQL, timed practice, reassessment), even when the actual session tests other topics. Resource suggestions also fall back to generic documentation for topics not matched by known keywords. These features should be described as a starting coaching plan, **not fully adaptive learning-path generation**.

## 4. Opportunity discovery and automated tests

An Anthropic Greenhouse query returned **681** jobs in a live API test. After correcting a substring-classification false positive (“International” incorrectly treated as “Intern”), discovery returned two relevant **Research / Fellowship** listings: AI Safety & Security and ML Systems & Reinforcement Learning. These examples validate title classification for this board; they do not prove that every opening is eligible or still open at the time of application.

Command: `pytest tests/test_opportunity_classifier.py -v`

| Unit test | Observed result |
|---|---|
| Internship identification | Passed |
| International-title false positive | Passed |
| Research / fellowship classification | Passed |
| Unrelated-position rejection | Passed |
| **Total** | **4 passed** |

The run also emitted 13 dependency deprecation warnings; those warnings did not fail the tests. This is a focused classifier test, **not** evidence that the entire application's test suite passed.

## 5. Accuracy, effectiveness, and progress measures

### Already implemented

- **Article uniqueness:** Unique recommended URLs ÷ all stored recommendations.
- **Metadata completeness:** Recommendations with nonempty title, source, URL, publication date ÷ all recommendations.
- **Article recency:** Recommendations with parseable dates no more than 30 days old ÷ all recommendations.
- **Publisher diversity:** Count of unique source labels.
- **Reading completion:** Count marked read in learning memory; understanding is also recorded on a 1–5 self-rating scale.
- **Career performance:** Arithmetic mean of persisted evaluator scores and per-topic averages; sessions remain available for historical comparison.

### Recommended stronger validation before broader use

1. Create a small reference set of retrieved articles. Human-review each summary for unsupported claims, correct source attribution, and relevance to the user profile.
2. Grade a fixed set of correct, partly correct, and incorrect technical answers using a human rubric; compare the agent's scores and feedback.
3. Repeat the exact same answer multiple times to quantify model grading variability.
4. Use genuine unaided baseline and later retest sessions with comparable difficulty to track personal improvement.
5. Assess opportunity eligibility using full descriptions and application requirements, not only titles.

## 6. Conclusion

Both LangGraph prototypes demonstrated their core workflows: technical article discovery and briefing, learning-memory persistence, job-description analysis, interactive interview evaluation, and report generation. Recorded tests support useful **functional reliability and sensible grading behavior on sampled inputs**. Stronger human-reviewed accuracy and longitudinal learning studies remain future work.
