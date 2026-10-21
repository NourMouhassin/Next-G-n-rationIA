# Next-G-n-rationIA — TD1

Trustworthy Generative AI, ESILV DIA A4, 21 October 2026.
Class: **to complete**. Sub-group: **to complete**. Members and contributions:
[reports/contributions.csv](reports/contributions.csv).

This is an explicitly **partial** submission: all 20 references are executed and
independently recomputed from CSV, but **0/100 model cells have been executed**.
The 100 comparison rows are `not_executed`, not measured failures. Human cross-check,
account allocation, live quota checks and the group handover remain pending.
See [reports/td1.md](reports/td1.md). No TD2 or TD3 work was implemented.

Pack: `2026-10-18-students-1`; model selection: `2026-10-14`.
Original database SHA-256:
`0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`.
Original CSVs, schema and manifest are included unchanged.

## Reproduce offline from a clean clone

Python 3.10+ and its standard library suffice. The user's environment is Python
3.12.10 on Windows. Use the existing `.venv` when available. Its base interpreter
is accessible outside the agent sandbox; sandbox-only discovery initially exposed
Python 3.15. Final checks use the user's actual Python 3.12.10. No environment or
dependencies are committed. `.gitattributes` preserves the authenticated data bytes.

```powershell
git clone https://github.com/NourMouhassin/Next-G-n-rationIA
cd Next-G-n-rationIA
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe td1.py prepare
.\.venv\Scripts\python.exe test_td1.py
.\.venv\Scripts\python.exe sandbox_sqlite.py --db data/boutique.sqlite --out evidence/sandbox-tests.json
.\.venv\Scripts\python.exe td1.py pivot
```

`.\.venv\Scripts\python.exe validate_submission.py` executes these offline checks and stores their
outputs, the integrity result and a secret-pattern scan in `evidence/validation.json`.

On other systems replace `.\.venv\Scripts\python.exe` with the available `python` or `python3`.
`prepare` verifies integrity, regenerates references and exact prompts, merges
existing `runs/state-*.jsonl`, then regenerates the comparison and model summary.
It makes **no network calls**. It never substitutes simulated traces for real ones.

## Run only an assigned lot

Before running, fill `allocation.json` with the actual operator, assigned questions,
remaining quota **after** access checks, controls consumed and Free-plan confirmation.
Confirm the group turn and personal accounts: A/B/D each use their own Groq account;
C/E use two distinct personal OpenRouter accounts. The account owner checks the
dashboard; this program cannot infer the account's actual quota from a key.
Reserve five extra calls where possible. If capacity is insufficient, coordinate
a smaller allocation or instructor fallback before running.

| Operator | Model | Planned cells |
|---|---|---|
| A | Groq `openai/gpt-oss-120b` | C01–C20 |
| B | Groq `openai/gpt-oss-20b` | C01–C20 |
| C | OpenRouter `cohere/north-mini-code:free` | C01–C20 |
| D | Groq `qwen/qwen3.8-27b` | C01–C20 |
| E | OpenRouter `dots-studio/dots-3-note-preview:free` | C01–C20 |

The relevant `GROQ_API_KEY` or `OPENROUTER_API_KEY` must already exist in the
executing process environment. Never put a key in a file or commit it.
Both variables were absent in the preparation process. An environment variable
set in another PowerShell window is not automatically inherited here.

```powershell
# Example ONLY after A's assignment, quota and group turn are confirmed:
.\.venv\Scripts\python.exe td1.py run --member A
```

This reuses the official skeleton, model JSON and sandbox. One model is selected;
temperature 0, configured caps (Qwen 1000, others 1024), timeout 45 s, spacing at
least 3 s, one retry at most per cell. Only timeout, 5xx, or 429 with a suitable
Retry-After can be retried. An operator budget stops further calls after the
assigned count plus five, including prior attempts in that operator's state.
No paid OpenRouter route is allowed. A local lock prevents overlapping local
operators; it cannot coordinate different machines, so group handover is essential.
Update the quota/handover declaration before each resumed run.

Every response is appended immediately to `runs/state-A.jsonl`; retries retain
separate rows. CSV export is `runs/traces-A.csv`. Retain both on resume and share
them with the consolidator. Do not delete or rename states to bypass attempt limits.
After interruption inspect the saved last attempt and provider counters. A crash
between server receipt and local persistence is inherently uncertain: do not
blindly repeat that cell; reconcile it with the provider before continuing.
If a crash leaves `.run.lock`, remove it only after confirming no operator is running.

Record quota after execution and actual controls/retries in `allocation.json` and
the report. Do not rerun `check_access.py` merely for a screenshot: it uses five calls.
The earlier successful access check was reported by the user; its output is not
present as experimental evidence in this repository.

## Consolidate and inspect

Copy each member's original state and CSV into `runs/`, using distinct A–E names.
All files must come from the same prompt/reference experiment. Then:

```powershell
.\.venv\Scripts\python.exe td1.py consolidate
.\.venv\Scripts\python.exe td1.py pivot
.\.venv\Scripts\python.exe skeleton-multi-llm-en.py --rates --state traces-td1.jsonl
```

The merger rejects conflicting duplicate attempts, unknown model/case IDs and
changed fingerprints/references. Identical duplicate imports are deduplicated;
original files are retained. Final real results use the largest attempt number.
Real, replay and simulation are separated. The official skeleton spells the
simulated nature `simulation`; this means simulated, never a real API result.
Replay/simulation remain in raw files and separate rates, not in the real matrix.
For instructor fallback, retain its origin and explain separately in the report.

`prompts-en.md` and `evidence/prompts.json` contain the exact common system/user
messages and SHA-256 for every question. The hash is UTF-8 SHA-256 of
`system + "\n" + user`, not a model-specific identifier.
Changing a prompt or reference requires separate experiment files. Do not merge
different experiments. For each observed failure, review the SQL/HTTP evidence
and refine its explanation; a value mismatch alone does not establish its cause.

`five-model-summary-en.csv` uses the course portfolio's dated public indices and
the exact-model paid-route snapshot in `docs/paid-route-snapshot.json`. N/A means
undocumented, never zero. Family groups are disjoint: period 6, age 5, products 4,
combined 5. No accuracy can be estimated from zero real calls.

## Assistance and hand-in

For the existing VS Code terminal, stay in the original kit directory (parent of
`submission`). This reuses both its `.venv` and the already configured environment
variables without copying, displaying or writing keys:

```powershell
.\.venv\Scripts\python.exe submission\td1.py prepare
# Only after your group assigns YOUR letter and allocation.json is filled:
# .\.venv\Scripts\python.exe submission\td1.py run --member YOUR_LETTER
```

The commented example is deliberately not executable until YOUR_LETTER is replaced
with the confirmed A, B, C, D or E. Do not rerun the access check to demonstrate keys.

Codex assisted with SQL/script development, tests and documentation. Reference
amounts were obtained by actual SQLite execution and independent CSV arithmetic,
not from accepting an AI numeric answer. The exact development request is retained
in [docs/development-prompt.txt](docs/development-prompt.txt). Members must review,
explain and cross-check the work; assistance does not replace their responsibility.

Official sources: [protocol](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/kit-td1/consigne-etudiante-en.html),
[submission](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/submission-en.html),
[assessment](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/assessment-en.html).
Snapshots are kept in `docs/`. Moodle is submitted personally by the student,
with repository URL, full commit hash and report permalink, by **25 October 2026,
23:59 Europe/Paris**. A partial commit must not be described as a finished 100-cell run.
