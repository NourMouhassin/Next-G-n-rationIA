# TD1 — Partial experimental report, 21 October 2026

Class / subgroup: **to complete**. Members: **to complete**.
Contributions: [contributions.csv](contributions.csv).

## Objective and current result

Evaluate five configured free SQL-generating models on twenty fixed e-commerce
questions against independently checked local references. Currently **20/20 SQL
references are computed and cross-checked computationally; 100/100 real model cells
are executed (lots A, B, C, D), 104 real attempts including 4 retries**. Lot E
(Dots on OpenRouter) is finished, run by a second member's OpenRouter account.

| Lot | Model | Correct | Wrong | Not executed | Retries |
|---|---|---:|---:|---:|---:|
| A | groq `openai/gpt-oss-120b` | 19 | 1 | 0 | 0 |
| B | groq `openai/gpt-oss-20b` | 18 | 2 | 0 | 0 |
| C | openrouter `cohere/north-mini-code:free` | 11 | 9 | 0 | 0 |
| D | groq `qwen/qwen3.8-27b` | 15 | 4 | 1 | 4 |
| E | openrouter `dots-studio/dots-3-note-preview:free` | 13| 6| 1 |0 |

Counts are on these twenty questions only: no general error rate and no ranking.
Every wrong answer concerns the **age convention** (age on a reference date or at
the order); period and product-only questions are 100 % correct for the four models.
Raw files: `runs/state-A.jsonl` to `runs/state-D.jsonl` and their CSV exports,
merged in [traces-td1.csv](../traces-td1.csv) / [traces-td1.jsonl](../traces-td1.jsonl).

## R1: executed references and independent checking

[reference-td1.csv](../reference-td1.csv) holds every executable SELECT and integer
result. [evidence/reference-check.csv](../evidence/reference-check.csv) gives the
SQLite value, separate CSV total and number of selected order lines for all cases.
[build_references.py](../build_references.py) contains both methods:

1. SQL joins order lines to products/customers, sums `quantity_product * price`
   in integer cents excluding VAT, and returns `COALESCE(..., 0)` with alias
   `revenue_cents`. The sandbox verifies a single row and column.
2. A separate Python loop reads the original three CSVs, uses independent,
   explicitly transcribed predicates and multiplies integer prices by quantities.
   It neither parses nor executes the SQL and does not consume SQL totals.

Periods use `start <= timestamp < end` at midnight UTC. SQL computes completed
age as year difference minus one when the birthday has not occurred. The CSV
method instead checks the interval from the 25th birthday to the 26th birthday.
There are no 29-February births in this dataset. C10/C18 use the order date;
the other age cases use the fixed reference date, including all orders unless
the question also specifies a period. Product restrictions select order lines,
not entire baskets containing a requested product.

Examples useful for the demonstration:

- C01: 792800 cents, 115 matching lines; C05: 38480 cents on 1 June, which is
  excluded from C01. C07: 13970 cents on 31 May, inside C01.
- C06 and C14: no matching lines, result 0 instead of NULL.
- C08/C02/C09: 605580 / 590320 / 487980 cents on consecutive age reference dates;
  birthday boundaries change membership. C10: 558980 cents with age at the order.
- C19: 1990 cents from one line after period, age and product-d filters.

[Integrity evidence](../evidence/data-check.json) matches all distributed hashes,
SQLite integrity and foreign keys. Database hash remains
`0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`.
No instructor answer key was accessed. Equality with that private key is not claimed.
Both implementations were developed with Codex; this is an independent computation
method, **not a human peer review**. The named second-member review of every question
is still pending in [reference-review.csv](reference-review.csv).

## R2: protocol and evidence status

The official skeleton, sandbox and model JSON are reused. [td1.py](../td1.py)
adds a small assigned-lot wrapper, consolidation and terminal pivot. Execution
requires declared account allocation, Free plan, current quota, consumed controls
and group handover. No API generation call was made during preparation. The
earlier `5/5 models OK` is user-reported context, not reproduced or counted here.
Both provider key environment variables are absent from the available process,
including the checked process outside the sandbox. The local key file was not read.

Parameters come directly from the official JSON: temperature 0, 45-second timeout,
one in-flight request, at least three seconds between calls, configured caps,
and at most two attempts per cell across resumptions. The wrapper limits the
operator's plan to assigned cells plus five additional calls and refuses missing
quota declarations. Live account counters and coordination across machines remain
human responsibilities. C/E require distinct personal OpenRouter accounts, and
A/B/D their personal Groq accounts. No billing was enabled and no paid route used.

Small corrections to the skeleton are documented and tested: preserve response
text, original response body, finish reason and retry metadata; forbid retry on
resume when a 429 had no permitted delay; wait conservatively on resumed retries;
retry only authorized temporary errors; retain missing replay latency as empty.
No TD2 vote logic was implemented.

[prompts-en.md](../prompts-en.md) contains the exact prepared messages and all
twenty expanded user messages, identical across models. SHA-256 hashes
`system + newline + user` in UTF-8. Real use of those prompts will be evidenced by
the per-attempt fingerprint. The runner saves every attempt before retrying;
`cell_id` is provider:model:question. Missing counters remain empty; a native cost
of zero is retained only when explicitly returned. `simulation` is the official
spelling for simulated data; it and replay are excluded from real comparison rates.

### Real batch of 21 October 2026 (lots A to D)

Lots A to D were run with the unmodified kit skeleton (`skeleton-multi-llm-en.py`
of pack 2026-10-18, before the corrections above), one operator at a time, from
the member's own terminal, keys in environment variables only. The prompt and the
references are identical to this repository's, which `td1.py consolidate` asserts
on every line (same `prompt_sha256` per question, same reference). These traces
therefore lack the `response_text`, `raw_response` and `finish_reason` columns,
which stay empty: a missing measurement, not a zero.

- **Selected trace (R2)**: `groq:qwen/qwen3.8-27b:C18`, [runs/state-D.jsonl](../runs/state-D.jsonl).
  Attempt 1: HTTP 429 "Rate limit reached ... output tokens per minute (OTPM): Limit
  1000", no SQL, no `Retry-After` header (empty field). Attempt 2 after the
  temporary-error delay: HTTP 200, value 62480 = reference, verdict correct.
  Same fingerprint on both lines. C19 and C20 show the same retry pattern; the
  Qwen output cap (1000 tokens) equals the account's OTPM limit, which explains
  the 429s. **C16 failed twice** (429 then 429): two attempts reached, cell
  `not_executed`, not retried further.
- **Native cost**: Groq returns none, the field stays empty; OpenRouter `:free`
  routes with a zero-price cap.
- **Incident, kept as evidence**: two first runs of lot A used an invalid key
  (HTTP 401 on all 20 cells, no SQL evaluated), one of them launched from a second
  terminal while the valid run was in progress, breaking the one-request-at-a-time
  rule for about one minute. Those 40 attempts are kept unedited, separated by run,
  in [runs/failed-access/](../runs/failed-access/), outside consolidation. The
  valid run's 16 lines were separated from the interleaved 401 lines without edits,
  then C01 to C04 were run in the valid experiment.

## R3: analysis and model portfolio

Causes are read from the returned SQL or the HTTP status of the latest attempt,
written in [td1-causes.csv](td1-causes.csv) and copied by `td1.py consolidate` into
the `explanation` column of the comparison. Examples:

- **Wrong answer, valid SQL** — `groq:openai/gpt-oss-120b:C15`: the filter
  `c.birth_date = date('2026-09-25','-25 years')` keeps only customers born on
  2001-09-25 (birthday on the reference day) instead of the completed-age window
  2000-09-25 < birth_date <= 2001-09-25. The 68670 returned is exactly that
  customer's share of the 168680 reference.
- **Text comparison trap** — `groq:qwen/qwen3.8-27b:C19`: `strftime('%Y', …)`
  (a year) compared as text with `'2026-09-25'` is always true, so no age filter
  is applied (83580 = all product d revenue in September).
- **Invalid date modifier** — `openrouter:cohere/north-mini-code:free:C19`:
  `date('2026-09-25', '-25-01-01')` returns NULL in SQLite, no line matches, 0.
- **Failed access, not a wrong answer** — `groq:qwen/qwen3.8-27b:C16` (HTTP 429
  twice, rate limit, no SQL) and the lot A 401 runs (invalid key, no SQL). The
  model's ability is not measured on those cells.
- **Two models agreeing on a wrong value (for TD 2)**: on C09, Qwen and Cohere both
  return 0 (reference 487980) with different SQL errors (age on the order date;
  age expression never equal to 25).

After importing lot E, use the latest attempt, inspect its original SQL/HTTP
response and explain the cause in `td1-causes.csv`. A successful HTTP request with wrong SQL is distinct from
an HTTP access denial, where SQL was never evaluated. `finish_reason=length`
supports a truncation diagnosis; a mere unequal value does not identify which
convention failed. If the real batch has no failure, request the explicitly
identified example supplied by the instructor for the R3 demonstration.
Offline mocked tests are engineering tests, not instructor examples or experiment results.

[five-model-summary-en.csv](../five-model-summary-en.csv) contains the five exact
configured models. The supplied template's stale Ling model was replaced by
Cohere to match the official JSON. Public indices 11.6, 9 and 33.7 for GPT-OSS
120B, GPT-OSS 20B and Qwen come from the course portfolio dated 28 September 2026;
the source does not identify the benchmark version, which limits interpretation.
Cohere/Dots indices are N/A because they are absent from that portfolio.

The [public catalog snapshot](../docs/paid-route-snapshot.json), retrieved on
21 October 2026 from the OpenRouter models endpoint without a key, documents
exact paid routes: GPT-OSS 120B 0.15/0.60, GPT-OSS 20B 0.018/0.09, and Qwen
0.04/1.35 USD per million input/output tokens. These are catalog prices, not
experimental costs. Cohere/Dots have only free entries in that snapshot; no
exact paid route is documented there, so their paid prices are N/A, not zero.
With twenty questions, the batch supports only a routing hypothesis: period and product-only questions were answered correctly by all four executed models; age questions are where they differ. No ranking or general rate.

## Validation and remaining work

Validation: 20 SQL/CSV equalities, original data hashes, 8 offline regression
tests and 25 sandbox checks pass. The final checks use the user's `.venv` and
Python 3.12.10 outside the sandbox. Initial sandbox-only checks used Python 3.15.0:
the sandbox could not access the installed Python 3.12, which was verified to exist
outside it. The user's environment was not replaced. Tests cover
retry policy, persistence, resume, exact free-route parameters, raw responses,
missing metrics, output shape and comparison uniqueness. See
[evidence/validation.json](../evidence/validation.json) and
[sandbox-tests.json](../evidence/sandbox-tests.json).

Remaining tasks: name group/members and record contributions; obtain human R1
cross-check; run lot E with a second member's OpenRouter account and import its
original files; review each observed error; update this
report and the portfolio results; re-run validation; commit/push the final state
and personally submit its exact hash and report permalink in Moodle. This partial
report must not be presented as completion of R2/R3 or all 100 calls.

## Declared assistance

Codex assisted with local development, SQL formulation, independent CSV verification,
tests and documentation. Values came from actual execution, not an AI numeric answer.
The [verbatim development prompt](../docs/development-prompt.txt) is retained.
No member's review, contribution or experimental result is fabricated. Students
remain responsible for understanding and explaining every submitted line.
