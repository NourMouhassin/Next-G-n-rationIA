# TD 2 — The quorum, then the routing rule

**ESILV DIA4 · Trustworthy Generative AI · subgroup 5 · 18 November 2026 · course pack 2026-11-18-students-5.**
Repository: <https://github.com/NourMouhassin/Next-G-n-rationIA>. This report is submitted at the commit given on Moodle.

All three steps use only the stored TD 1 data of the five-model consolidation (commit `52a8fcf`): `traces-td1.csv` (104 real attempts, 100 final cells, 5 models × 20 questions, batch of 2026-10-21) and `reference-td1.csv` (20 reference SQL queries written without a model). No new provider call was made for TD 2.

## Contributions, AI assistance and review

| Step | Pair | Members | AI assistance (declared) | Main files |
|---|---|---|---|---|
| 1 — k-of-n vote | A | Mathias Silvert--Lis, Fakhar Hussain | Claude (Anthropic) — [`docs/td2-binome-A-prompt.md`](../docs/td2-binome-A-prompt.md) | `skeleton-multi-llm-en.py`, `comparer_quorums.py`, `atelier-vote.py`, `reports/td2-vote-*`, `reports/td2-tableau-vote.md` |
| 2 — wrong consensus | B | Ilyess, Nour | Codex — declared in Step 2 | `td2_wrong_consensus.py`, `sql/td2-binome-B/`, `evidence/td2-binome-B/` |
| 3 — routing rule | C | Arman Lacaze, Alexandre Lorphelin, Emma Trotignon | ChatGPT — [`docs/td2-binome-C-prompt.md`](../docs/td2-binome-C-prompt.md) | `td2/binome-C/`, `evidence/td2-binome-C/` |

**Cross-checks on the merged `main`** (run by Pair A, Mathias Silvert--Lis and Fakhar Hussain): Pair B's `td2_wrong_consensus.py` was rerun and both `pair_A_check` fields returned `passed`; Pair C's 15 unit tests passed; the Step 1 quorum table regenerated identically from the repository.

## Cross-checks between the steps

- **Step 1 ↔ Step 2.** Pair A's merged `vote_k_sur_n`, run on the stored traces, gives exactly Pair B's manual C09 counts: fixed 2-of-3 → consensus 0 with 2 votes (Cohere, Qwen); 3-of-5 → consensus 0 with 3 votes (+ Dots); reference 487980.
- **Step 1 ↔ Step 3.** Pair C's per-family success rates (computed from `model-question-comparison-en.csv`) were recomputed independently from `traces-td1.csv` (last attempt of each model) during assembly: identical for all 25 family × model cells, and the five families cover the 20 questions exactly once.
- **All steps.** The ten period and product questions are answered correctly by all five models; every disagreement, abstention and the wrong consensus fall on age-bearing questions. Common conclusion: agreement, even 3-of-5, is not proof of correctness. For customer-visible amounts and payouts on age-bearing families, the routing rule requires a deterministic reference SQL check (with human review for payouts), not a vote.

## Reproduce from the repository root

```bash
# Step 1 — vote (needs sandbox_sqlite.py, already in the repository)
python3 atelier-vote.py
for i in $(seq -w 1 20); do python3 atelier-vote.py --traces traces-td1.csv --case C$i; done
python3 comparer_quorums.py --traces traces-td1.csv --reference reference-td1.csv | diff - reports/td2-tableau-vote.md && echo "Step 1 reproducible"
# Step 2 — wrong consensus
python3 td2_wrong_consensus.py
# Step 3 — routing
python3 td2/binome-C/test_routage.py
python3 td2/binome-C/produce_evidence.py
```

## Step 1 — Pair A: the k-of-n vote

Pair A: **Mathias Silvert--Lis and Fakhar Hussain**. AI assistance is declared in [`docs/td2-binome-A-prompt.md`](../docs/td2-binome-A-prompt.md).

### 1.1 The method `Orchestrateur.vote_k_sur_n`

Implemented in [`skeleton-multi-llm-en.py`](../skeleton-multi-llm-en.py), following the contract of its docstring:

1. only proposals with `verdict == "executed"` that carry a value vote; a member in error (HTTP 429, invalid SQL, missing) **stays counted in n** but casts no vote;
2. `k` must be a strict majority, `n // 2 < k <= n`, otherwise `ValueError`;
3. two proposals with the same `(provider, model_requested)` pair raise `ValueError`, even if one of them is an error: a duplicate is not a second opinion;
4. if a value reaches k votes: `{"consensus": True, "value": v, "votes": count, "models": ["provider:model_requested", ...]}`;
5. otherwise: `{"consensus": False, "value": None, "votes": largest count, "models": []}`. The method never invents a value.

Because `k > n // 2`, two different values cannot both reach k (that would require 2k > n votes), so returning the first value that reaches k is unambiguous. The method never receives the reference.

**Synthetic examples** ([`atelier-vote.py`](../atelier-vote.py) without arguments, nature `simulation`, n = 3, k = 2, reference 100):

| Example | Proposals | Decision | Matches reference |
|---|---|---|---|
| agreement | 100, 100, 120 | consensus 100 (2 votes) | yes |
| disagreement | 100, 110, 120 | abstention (max 1) | n/a |
| unavailable | 100, error, error | abstention (max 1) | n/a |
| wrong consensus | 0, 0, 100 | consensus 0 (2 votes) | **no** |

The last example shows the limit of voting: a majority agreeing on a wrong value wins.

### 1.2 Comparison protocol

- **Data**: `traces-td1.csv`, 104 rows, all `nature = real`, batch of 2026-10-21, five models. Single chronological export (increasing dates), so the last row of a model on a question is its last attempt. `qwen/qwen3.8-27b` has 24 rows instead of 20: new attempts after HTTP 429 on C16, C18, C19 and C20.
- **Configurations**: fixed 2-of-3 panel (`groq:openai/gpt-oss-120b`, `openrouter:cohere/north-mini-code:free`, `groq:qwen/qwen3.8-27b`, k = 2); 3-of-5 quorum on the five models (+ `openrouter:dots-studio/dots-3-note-preview:free`, `groq:openai/gpt-oss-20b`, k = 3).
- **Decision**: always taken by our `vote_k_sur_n`. A proposal votes if its TD 1 verdict is `correct` or `incorrect` with a value (same rule as `atelier-vote.py`); `not_executed` and `sql_invalid` stay in n without a vote. The reference is read only **after** the decision.
- **Reference**: `reference-td1.csv` (20 SQL queries written without a model, with their `revenue_cents`). Its 20 values are identical to the `reference` column of the traces.
- **Cross-check**: the 20 fixed-panel decisions of [`comparer_quorums.py`](../comparer_quorums.py) are identical to those of `atelier-vote.py --traces traces-td1.csv --case Cxx`, run question by question.
- **Evidence**: [synthetic examples](td2-vote-synthetique.jsonl); [fixed panel, question by question, with `atelier-vote.py`](td2-vote-panel.jsonl); [table generated by the script](td2-tableau-vote.md) (its labels are in French; the table below is the same output, translated).

### 1.3 The twenty decisions

| Question | Reference | 2-of-3 (fixed panel) | Agreement | 3-of-5 (five models) | Agreement | Change |
|---|---|---|---|---|---|---|
| C01 | 792800 | consensus 792800 (3/3) | ✅ = ref. | consensus 792800 (5/5) | ✅ = ref. | — |
| C02 | 590320 | consensus 590320 (2/3) | ✅ = ref. | abstention (max 2/5) | ⏸ abstention | consensus → abstention |
| C03 | 936350 | consensus 936350 (3/3) | ✅ = ref. | consensus 936350 (5/5) | ✅ = ref. | — |
| C04 | 2826250 | consensus 2826250 (3/3) | ✅ = ref. | consensus 2826250 (5/5) | ✅ = ref. | — |
| C05 | 38480 | consensus 38480 (3/3) | ✅ = ref. | consensus 38480 (5/5) | ✅ = ref. | — |
| C06 | 0 | consensus 0 (3/3) | ✅ = ref. | consensus 0 (5/5) | ✅ = ref. | — |
| C07 | 13970 | consensus 13970 (3/3) | ✅ = ref. | consensus 13970 (5/5) | ✅ = ref. | — |
| C08 | 605580 | consensus 605580 (2/3) | ✅ = ref. | consensus 605580 (3/5) | ✅ = ref. | — |
| C09 | 487980 | consensus 0 (2/3) | ❌ wrong consensus | consensus 0 (3/5) | ❌ wrong consensus | — |
| C10 | 558980 | consensus 558980 (2/3) | ✅ = ref. | consensus 558980 (3/5) | ✅ = ref. | — |
| C11 | 446690 | consensus 446690 (2/3) | ✅ = ref. | abstention (max 2/5) | ⏸ abstention | consensus → abstention |
| C12 | 1666490 | consensus 1666490 (3/3) | ✅ = ref. | consensus 1666490 (5/5) | ✅ = ref. | — |
| C13 | 107740 | consensus 107740 (3/3) | ✅ = ref. | consensus 107740 (5/5) | ✅ = ref. | — |
| C14 | 0 | consensus 0 (3/3) | ✅ = ref. | consensus 0 (5/5) | ✅ = ref. | — |
| C15 | 168680 | abstention (max 1/3) | ⏸ abstention | abstention (max 2/5) | ⏸ abstention | — |
| C16 | 376740 | consensus 376740 (2/3) | ✅ = ref. | consensus 376740 (4/5) | ✅ = ref. | — |
| C17 | 258180 | abstention (max 1/3) | ⏸ abstention | abstention (max 2/5) | ⏸ abstention | — |
| C18 | 62480 | consensus 62480 (2/3) | ✅ = ref. | consensus 62480 (3/5) | ✅ = ref. | — |
| C19 | 1990 | abstention (max 1/3) | ⏸ abstention | consensus 1990 (3/5) | ✅ = ref. | abstention → consensus |
| C20 | 1106090 | consensus 1106090 (3/3) | ✅ = ref. | consensus 1106090 (5/5) | ✅ = ref. | — |

**Summary**: 2-of-3 → 16 correct, 1 wrong consensus (C09), 3 abstentions (C15, C17, C19). 3-of-5 → 15 correct, 1 wrong consensus (C09), 4 abstentions (C02, C11, C15, C17).

### 1.4 Last attempt of each model

| Question | Reference | gpt-oss-120b (groq) | north-mini-code:free (openrouter) | qwen3.8-27b (groq) | dots-3-note-preview:free (openrouter) | gpt-oss-20b (groq) |
|---|---|---|---|---|---|---|
| C01 | 792800 | 792800 (correct) | 792800 (correct) | 792800 (correct) | 792800 (correct) | 792800 (correct) |
| C02 | 590320 | 590320 (correct) | 2606320 (incorrect) | 590320 (correct) | 0 (incorrect) | 0 (incorrect) |
| C03 | 936350 | 936350 (correct) | 936350 (correct) | 936350 (correct) | 936350 (correct) | 936350 (correct) |
| C04 | 2826250 | 2826250 (correct) | 2826250 (correct) | 2826250 (correct) | 2826250 (correct) | 2826250 (correct) |
| C05 | 38480 | 38480 (correct) | 38480 (correct) | 38480 (correct) | 38480 (correct) | 38480 (correct) |
| C06 | 0 | 0 (correct) | 0 (correct) | 0 (correct) | 0 (correct) | 0 (correct) |
| C07 | 13970 | 13970 (correct) | 13970 (correct) | 13970 (correct) | 13970 (correct) | 13970 (correct) |
| C08 | 605580 | 605580 (correct) | 1188090 (incorrect) | 605580 (correct) | 25920 (incorrect) | 605580 (correct) |
| C09 | 487980 | 487980 (correct) | 0 (incorrect) | 0 (incorrect) | 0 (incorrect) | 487980 (correct) |
| C10 | 558980 | 558980 (correct) | 119410 (incorrect) | 558980 (correct) | 119410 (incorrect) | 558980 (correct) |
| C11 | 446690 | 446690 (correct) | 0 (incorrect) | 446690 (correct) | 0 (incorrect) | 322160 (incorrect) |
| C12 | 1666490 | 1666490 (correct) | 1666490 (correct) | 1666490 (correct) | 1666490 (correct) | 1666490 (correct) |
| C13 | 107740 | 107740 (correct) | 107740 (correct) | 107740 (correct) | 107740 (correct) | 107740 (correct) |
| C14 | 0 | 0 (correct) | 0 (correct) | 0 (correct) | 0 (correct) | 0 (correct) |
| C15 | 168680 | 68670 (incorrect) | 314020 (incorrect) | 0 (incorrect) | 168680 (correct) | 168680 (correct) |
| C16 | 376740 | 376740 (correct) | 376740 (correct) | not_executed | 376740 (correct) | 376740 (correct) |
| C17 | 258180 | 258180 (correct) | 0 (incorrect) | 248490 (incorrect) | sql_invalid | 258180 (correct) |
| C18 | 62480 | 62480 (correct) | 286650 (incorrect) | 62480 (correct) | 39580 (incorrect) | 62480 (correct) |
| C19 | 1990 | 1990 (correct) | 0 (incorrect) | 83580 (incorrect) | 1990 (correct) | 1990 (correct) |
| C20 | 1106090 | 1106090 (correct) | 1106090 (correct) | 1106090 (correct) | 1106090 (correct) | 1106090 (correct) |

### 1.5 Questions where the decision changes between 2-of-3 and 3-of-5

**C02** (exactly 25 on 2026-09-25, all orders; reference 590320) — *correct consensus → abstention.*
In the panel, `gpt-oss-120b` and `qwen3.8-27b` return 590320 and `north-mini-code` returns 2606320: correct consensus at 2/3. In 3-of-5, `dots-3-note-preview` and `gpt-oss-20b` both return **0** (shared wrong value). Votes: 590320 → 2, 0 → 2, 2606320 → 1; no value reaches 3, hence the abstention. The shared wrong value does not win, but it ties the correct one and blocks the consensus.

**C11** (exactly 25 on 2026-12-01, all orders; reference 446690) — *correct consensus → abstention.*
Panel: `gpt-oss-120b` and `qwen3.8-27b` return 446690, `north-mini-code` returns 0: correct consensus at 2/3. In 3-of-5, `dots-3-note-preview` also returns **0** (the same wrong value as `north-mini-code`) and `gpt-oss-20b` returns 322160. Votes: 446690 → 2, 0 → 2, 322160 → 1, hence abstention.

**C19** (product d, September 2026, exactly 25 on 2026-09-25; reference 1990) — *abstention → correct consensus.*
Panel: three different values, 1990 (`gpt-oss-120b`), 0 (`north-mini-code`) and 83580 (`qwen3.8-27b`, obtained at its second attempt after an HTTP 429): abstention at 1/3. In 3-of-5, `dots-3-note-preview` and `gpt-oss-20b` return 1990: the value reaches 3/5, correct consensus.

### 1.6 Same decision, shifted margin

- **C16** (reference 376740): `qwen3.8-27b` is `not_executed` after two HTTP 429. It stays in n = 3 without voting: the 2/3 consensus (`gpt-oss-120b`, `north-mini-code`) is reached **exactly at the threshold**; one more error and the panel would have abstained. In 3-of-5 the margin rises to 4/5.
- **C17** (reference 258180): abstention in both configurations. In 3-of-5, `dots-3-note-preview` returns invalid SQL (`syntax_error near "AS"`): it stays in n = 5 without voting. The correct value only gathers 2 votes (`gpt-oss-120b`, `gpt-oss-20b`), below the threshold of 3.
- **C15** (reference 168680): the three panel members are wrong with three different values (68670, 314020, 0). Abstention **protects** against an error here. In 3-of-5 the correct value leads (`dots-3-note-preview`, `gpt-oss-20b`) but with 2 votes, below the threshold: still an abstention.
- **C18** (reference 62480): `qwen3.8-27b` succeeds at its second attempt after an HTTP 429; that last attempt votes and gives the 2/3 consensus. Without the retry the panel would have abstained (1/3).
- **C10** (age at order date; reference 558980): `north-mini-code` and `dots-3-note-preview` share the wrong value **119410**; it is outvoted (1/3 in the panel, 2/5 in 3-of-5). Correct consensus in both cases.

### 1.7 Wrong consensus in our batch: C09 (handed to Pair B)

**C09** (exactly 25 on 2026-09-26, all orders; reference 487980). `north-mini-code`, `qwen3.8-27b` and `dots-3-note-preview` all return **0**; only `gpt-oss-120b` and `gpt-oss-20b` return 487980.

- 2-of-3: consensus on **0** (`north-mini-code` + `qwen3.8-27b`), wrong.
- 3-of-5: consensus on **0** (+ `dots-3-note-preview`), wrong, with one more vote.

Enlarging the quorum does not correct an error shared by a majority; here it confirms it. The SQL cause is diagnosed in Step 2.

### 1.8 What we conclude

- **3-of-5 is not better on this batch**: it gains C19, loses C02 and C11 (correct consensuses turned into abstentions) and does not fix C09. An abstention is safe (no wrong value), but it has a cost: a reference or a human review is then needed.
- **All errors are on age questions**: the ten period-only and product-only questions (C01, C03 to C07, C12 to C14, C20) are unanimous 5/5 and correct; every disagreement and the wrong consensus concern age (C02, C08 to C11, C15 to C19). On simple questions a vote costs without adding anything; on age questions it is not always enough.
- **Voters are not independent**: `north-mini-code` and `dots-3-note-preview` share the same wrong value on C09, C10 and C11, and `gpt-oss-120b` / `gpt-oss-20b` belong to the same model family, so the 3-of-5 quorum does not bring together five distinct families, unlike the fixed panel.
- **Limits**: 20 questions and a single batch. These figures are an observation on this batch, not a general error rate, a durable ranking or an error guarantee for any quorum.

## Step 2 — The wrong consensus

Pair B: **Ilyess and Nour**. Analysis executed offline on 18 November 2026 with
the existing Python 3.12.10 environment. Codex assisted development and analysis;
the pair's personal review remains pending. This section covers Step 2 only.
Source: [official TD2, Step 2](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/kit-td1/enonce-td2-en.html#section-7),
pack `2026-11-18-students-5`. Base commit:
`52a8fcf9db349fa87a7e55848d56a579d929c7b4`; the exact source file hashes are
recorded in [C09-evidence.json](../evidence/td2-binome-B/C09-evidence.json).

### Real case and final proposals

We inspected all **104 real attempts / 100 final cells** in `traces-td1.csv`,
retaining the largest attempt number per provider/model/question, then the latest
timestamp on a tie. Four cases contain a shared wrong numeric value, recorded in
the evidence JSON. C09 is a **real TD1 case**, not a synthetic example or a new
API call. SQL is re-executed locally; original latency/token measurements are not
replaced with diagnostic timings.

C09 asks: *What is the total revenue excluding VAT, in euro cents, generated by
customers who are exactly 25 years old on the reference date 2026-09-26 (all their orders)?*
The reference is **487980 cents**, recomputed by read-only SQL and independent CSV
arithmetic. Age is evaluated on **26 September 2026**, not at each order date;
eligible birth dates satisfy **2000-09-26 < birth_date <= 2001-09-26**.

| Model (provider) | Value, cents | TD1 verdict | Original trace, attempt 1 |
|---|---:|---|---|
| GPT-OSS 120B (Groq) | 487980 | correct | [state-A.jsonl, line 5](../runs/state-A.jsonl#L5) |
| GPT-OSS 20B (Groq) | 487980 | correct | [state-B.jsonl, line 9](../runs/state-B.jsonl#L9) |
| Cohere north-mini-code (OpenRouter) | 0 | incorrect | [state-C.jsonl, line 9](../runs/state-C.jsonl#L9) |
| Qwen3.8-27B (Groq) | 0 | incorrect | [state-D.jsonl, line 9](../runs/state-D.jsonl#L9) |
| Dots3-Note Preview (OpenRouter) | 0 | incorrect | [state-E.jsonl, line 9](../runs/state-E.jsonl#L9) |

The two diagnosed trace IDs are **`groq:qwen/qwen3.8-27b:C09`** (attempt 1,
`2026-10-21 12:50:05` UTC) and **`openrouter:cohere/north-mini-code:free:C09`**
(attempt 1, `2026-10-21 12:54:25` UTC). The JSON evidence also records all five
cell IDs, timestamps, prompt fingerprints and logical CSV record numbers.

### Manual quorum counts

| Declared panel / threshold | Votes for 0 | Votes for 487980 | Decision | Correct against reference? |
|---|---:|---:|---|---|
| Fixed 2/3: GPT-OSS 120B, Cohere, Qwen | 2 (Cohere, Qwen) | 1 (120B) | consensus 0; 2 voices; no abstention | No |
| 3/5: all five TD1 models | 3 (Cohere, Qwen, Dots) | 2 (120B, 20B) | consensus 0; 3 voices; no abstention | No |

Dots and 20B do **not** participate in the fixed 2/3 panel. An incorrect numeric
answer still votes: the voting algorithm cannot use the reference as an oracle.
An error without a value stays in the panel denominator, without a vote; none
of the five C09 proposals has such an error.

Pair A's `Orchestrateur.vote_k_sur_n` is now merged into `main` (merge commit `1837d60`). Run on the stored traces, it returns exactly these manual counts: fixed 2-of-3, consensus 0 with 2 votes (`openrouter:cohere/north-mini-code:free`, `groq:qwen/qwen3.8-27b`); 3-of-5, consensus 0 with 3 votes (+ `openrouter:dots-studio/dots-3-note-preview:free`). See Pair A's [panel evidence](td2-vote-panel.jsonl) and [quorum table](td2-tableau-vote.md). The diagnostic script also calls the method for both panels and fails an assertion on any difference from the manual counts; it was rerun on the merged `main` before hand-in.
Pair B does not implement or edit Pair A's voting method.

### Complete faulty queries and exact causes

These blocks reproduce the complete SQL from the two CSV trace fields, also
saved verbatim in the linked `.sql` files. Both execute successfully and return 0.

**Qwen — [original SQL](../sql/td2-binome-B/C09-qwen-original.sql)**

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25
  AND (strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date))
  AND (strftime('%m-%d', o.date) < strftime('%m-%d', date(c.birth_date, '+26 years')));
```

The second and third predicates require the order's month-day to be both **>=**
and **<** the same birthday month-day: adding 26 years does not change that
month-day for these customers (the original data excludes leap-day births).
Their conjunction is false, so all order lines are removed. In addition, the
first predicate incorrectly evaluates age at `o.date` instead of `2026-09-26`;
removing only the contradictory predicate would not fully fix C09. The joins are
correct key joins; the error is in the WHERE, not a lost or duplicated join.

**Cohere — [original SQL](../sql/td2-binome-B/C09-cohere-original.sql)**

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
  -- Compute age on 2026-09-26
  (
    -- Age = year difference
    CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) -
    -- Subtract 1 if birthday hasn't occurred yet this year on 2026-09-26
    CASE
      WHEN SUBSTR(c.birth_date, 6, 2) > '09' THEN 1
      WHEN SUBSTR(c.birth_date, 6, 2) = '09' AND SUBSTR(c.birth_date, 9, 2) > '26' THEN 1
      ELSE 0
    END
  ) = 25;
```

The expression is **birth year − birthday correction**, not completed age:
it omits `2026 − birth_year`. Its value is around the customer's birth year,
never 25 in this dataset, so every line is removed. The month/day correction is
for the right reference day, but it is applied to the wrong leading expression.
The joins are again correct. The required expression is
`2026 - birth_year - (birthday_month_day > '09-26') = 25`.

The [executed original reference SQL](../sql/td2-binome-B/C09-reference.sql)
uses that completed-age expression on `2026-09-26`, sums quantity times unit
price over all qualifying order lines and returns 487980 cents. It introduces
no order-period filter and returns zero rather than NULL for an empty selection.

### Row-preserving SQL delta and independent check

[C09-delta.sql](../sql/td2-binome-B/C09-delta.sql) replaces only the aggregate
projection of each original query with order-line columns, retaining its full
FROM/JOIN/WHERE. It compares the reference and each faulty selection by
**(order_id, product_id)**, the order-line primary key, using two anti-joins
(`NOT EXISTS`) for omissions and additions and combining with **UNION ALL**.
It does not use DISTINCT or collapse equal-valued sales. Output includes model,
difference type, customer_id, order_id, product_id, order date, birth date,
quantity, price and revenue in cents. Execution uses the supplied read-only
sandbox with a larger result-row cap for this diagnostic SELECT only.

[C09-delta.csv](../evidence/td2-binome-B/C09-delta.csv) contains 136 diagnostic
rows: the same 68 genuinely omitted sales listed once for each faulty model.
Do **not** add the two model deltas together as though they were different sales.

| Customer | Omitted order lines per model | Omitted revenue per model, cents |
|---|---:|---:|
| C001 | 18 | 135000 |
| C002 | 6 | 25920 |
| C003 | 6 | 47900 |
| C007 | 18 | 118740 |
| C008 | 11 | 99090 |
| C009 | 9 | 61330 |
| Total | 68 | 487980 |

For **each** of Qwen and Cohere: omitted **487980** − wrongly added **0**
= reference **487980** − faulty answer **0**. Six customers are affected;
no added order lines exist. The independent Python calculation reads the three
original CSVs, tests reference membership via the interval from the 25th to 26th
birthday, transcribes each faulty predicate with Python date/integer operations,
and multiplies each line's quantity by its product price. It matches not only
the total but the multiset of model/direction/order/product/customer/amount tuples.
Database, input CSV and reference hashes are unchanged after execution.

From the original `kit-td1` directory, reproduce without network or API keys:

```powershell
.\.venv\Scripts\python.exe submission\td2_wrong_consensus.py
```

From a clone root, use its available Python 3.12 interpreter on
`td2_wrong_consensus.py`. The script refreshes only Pair B evidence/SQL, validates
the two raw queries, reference, detailed delta, CSV arithmetic and vote-method
comparison when available. It does not regenerate TD1 or other pairs' sections.

**Consequence:** agreement, even 3/5, does not prove correctness; an independent
reference/data check is needed to detect this shared wrong answer.

### Ilyess and Nour: review before the group meeting

- Read both original WHERE clauses and explain why changing only Qwen's date is insufficient.
- Recount both panels, including Dots only in 3/5; distinguish an incorrect vote from an unavailable proposal.
- Inspect several (order_id, product_id) delta rows and the six customer subtotals against the CSVs.
- Rerun the script on the merged `main` and require both `pair_A_check` fields to say passed.
- Confirm the pair's review and merge only this Step 2 section with the other pairs' work.

## Step 3 — Pair C: routing policy and simulator

Pair C: **Arman Lacaze, Alexandre Lorphelin and Emma Trotignon**. This section was merged into `main` together with Steps 1 and 2 (merge commit `6d25926`); it does not change Pair A's or Pair B's code, tables or reported contributions. AI coding support is declared in [`docs/td2-binome-C-prompt.md`](../docs/td2-binome-C-prompt.md).

### Goal and sources

Choose a model and a checking strategy for each SQL-question family based on
our five-model TD1 comparison; test the official simulator's 7 scenarios
before and after changing the resources and policy. The real input is the
team's `model-question-comparison-en.csv`: 100 final cells, 5 models × 20
questions, derived from the retained `traces-td1.csv` (104 attempts). The
models and parameters are loaded from `modeles-autorises.json`.

No new provider calls or new benchmarks were made. The simulated availability,
budgets and refill delays are **not provider measurements**. The catalog is the
dated snapshot `docs/paid-route-snapshot.json` (2026-10-21), not a live quote.
The fixed token envelope (650 in + 300 out) is illustrative.

#### Family-specific real TD1 results

A correct cell is one with status `correct`; `incorrect`, `sql_invalid` and
`not_executed` count as non-success. Exactly 20 distinct questions occur in five
disjoint categories. Derived programmatically by `--table`.

| Family | IDs | GPT-OSS 120B | GPT-OSS 20B | Cohere | Qwen | Dots |
|---|---|---:|---:|---:|---:|---:|
| F1 period | C01,C04–C07,C20 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| F2 age on date | C02,C08,C09,C11 | 4/4 | 2/4 | 0/4 | 3/4 | 0/4 |
| F2b age at order | C10 | 1/1 | 1/1 | 0/1 | 1/1 | 0/1 |
| F3 product list | C03,C12–C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| F4 combinations | C15–C19 | 4/5 | **5/5** | 1/5 | 1/5 | 3/5 |

**Interpretation:** F1 and F3 are easy for this batch; age predicates produce
most observed mistakes. F2 only has GPT-OSS 120B at 4/4. F4 only has GPT-OSS
20B at 5/5, and even this does not prove future correctness. F2b has only one
pure-age-at-order question. A model not correct on all family cells is *not*
selected as an unverified downgrade when the primary route fails.

**Full one-page rule:** [`td2/binome-C/routing-rule-en.md`](../td2/binome-C/routing-rule-en.md)
with explicit family, first model, checks for dashboard/customer/payout,
free-provider fallback, deferral, paid budget and abstention. The policy is
machine-readable in [`policy.json`](../td2/binome-C/policy.json). The model
selection is based on observed family correctness, not global model size. Ties
among free zero-cash routes are broken explicitly: Cohere F1; Dots F3; GPT-OSS
120B F2; GPT-OSS 20B F2b/F4. A later exact-model paid route is used only if
its documented hypothetical cost fits the request budget.

For customer-visible and payout values, every age-bearing family needs a
**deterministic independent SQL reference** (with human review for payouts),
not merely an LLM vote. In our real **C09**, Cohere, Qwen and Dots agreed on 0
while the reference was 487980 cents; both 2/3 and 3/5 returned the wrong
value. These facts are diagnosed in Pair B's own report. The simulator merely
*names* the required check and does not run it.

### Official workshop: seven scenarios, before and after

Original code kept unchanged as
[`atelier-routage-original.py`](../td2/binome-C/atelier-routage-original.py).
Its three example resources are fictional. Our
[`atelier-routage-adapte.py`](../td2/binome-C/atelier-routage-adapte.py)
replaces them with the five configured free routes and the documented paid
versions of the exact models, and selects only models that got every question
of the requested family correct in TD1. Both scripts implement the same priority:
**included capacity → defer when feasible → paid when authorised → abstain**.

| Official scenario | Before: supplied fake resources | After: our group policy | Why |
|---|---|---|---|
| `simple` | Run `small-free` | Run Cohere Free | F1 period 6/6, no new cash, dashboard logs result |
| `complex` | Run `senior-subscription` | Run GPT-OSS 20B Free | F4 mixed filters 5/5; deterministic SQL check required |
| `deferrable` | Defer `senior-subscription` 60 min | Defer GPT-OSS 20B Free 60 min | Only fully eligible F4 model's free quota simulated exhausted; recheck on waking |
| `urgent` | Run `senior-api`, **$0.30** fictional | Run paid exact GPT-OSS 20B, **$0.0000387** illustrative | Cannot wait for free refill, cost fits $0.30 budget |
| `budget exhausted` | Abstain | Abstain | No F4-eligible included route and zero budget |
| `high impact` | Run subscription with source + human review | Run GPT-OSS 20B Free with reference SQL + human approval | Paying out requires objective verification |
| `unknown capability` | Abstain (`difficulty=4`) | Abstain (`F_unknown`) | No TD1 evidence for a new family |

The seven named scenarios are **intent-preserving mappings** from the official
`difficulty` examples to real TD1 families: difficulty 1 → F1; difficulty 3 → F4;
unknown 4 → unknown family. The original resource list had a *subscription*;
our TD1 actually used Free plans, not a subscription. Scenario price and
availability differences are deliberately not apples-to-apples measurements.
The generated JSONL outputs preserve the full reason and configured check.

**Supplementary scenarios:** with Cohere unavailable on F1, Dots (also 6/6)
becomes the next eligible free route. With F2 age-at-date, GPT-OSS 120B (4/4)
is selected; when it is quota-blocked with a 20-minute reset and the deadline
allows it, the request is deferred rather than silently using a less-proven
model. F2b payout uses GPT-OSS 20B (1/1) with SQL reference and human approval.
The extra cases illustrate explicit next-route and risk-based checking behavior.

### Priority question: included subscription vs waiting

In the supplied `choose` implementation, `included` is tested **before**
`waiting`. An available subscription can have `cash == 0` (no incremental
spend) and `allocation > 0` (already-paid quota); it therefore immediately
qualifies as included capacity even if a free route could reset within the
deadline. This is reasonable when the capacity is already paid, latency
matters, and the refill time is not guaranteed. The unit test
`test_included_subscription_before_wait` demonstrates the behavior with an
**explicitly synthetic** subscription resource; it is **not** presented as one
of our five measured routes.

Reverse this priority if the remaining subscription allocation is scarce,
future high-impact work must reserve it, the current request is low-impact
and deferrable, and a free refill has a sufficient timing buffer. Such a
reversal would require a quota-reservation policy and new simulator branch;
we explain the condition without falsely claiming it is implemented here.

### Execution, validation and limitations

Commands from the group repo root (Python 3.10+ standard library):

```powershell
python td2/binome-C/atelier-routage-original.py
python td2/binome-C/atelier-routage-adapte.py --table
python td2/binome-C/atelier-routage-adapte.py --check-rates
python td2/binome-C/atelier-routage-adapte.py
python td2/binome-C/atelier-routage-adapte.py --extra
python td2/binome-C/test_routage.py
python td2/binome-C/produce_evidence.py
```

The final command writes only under
[`evidence/td2-binome-C/`](../evidence/td2-binome-C/), including `scenarios-before.jsonl`,
`scenarios-after.jsonl`, `family-rates.csv`, tests and a manifest with the actual
TD1 comparison file SHA-256. The other scripts never mutate the TD1 base or
call an external provider.

**Validation performed in the assistant's execution environment:** 15 unit
tests passed on a **status-only fixture independently transcribed from and
checked against** the group's real 100-cell GitHub comparison; the original and
adapted simulators emitted 7 decisions each. The archived evidence was then
regenerated by `produce_evidence.py` on the merged `main` before hand-in, so its
manifest links (SHA-256) to the exact TD1 matrix of the repository. The test
fixture is **not** a second experimental sample.

#### Limitations and remaining review

- The router selects a route and *declares* checks; it does **not** execute
  extra LLM calls, quorums, SQL verification or a real payout. Production
  integration would be a separate task.
- TD1 measures only 20 specific questions with one final cell per model;
  1/1 for F2b and 5/5 for F4 do not estimate broad future error rates.
- A paid exact-model route shown in the **October 21 catalog snapshot** is
  not proof of its November 18 current price or availability. Budget figures
  are illustrative fixed-token costs, not billing measurements.
- If TD1 input paths change during A/B merge, re-run the scripts on the merged
  repo to ensure the 100-cell coverage and model configuration are intact.
- Human cross-review and **actual Pair C member contributions** must be
  confirmed by the students, then included in the single `reports/td2.md`.

**Integration:** merged into `main` with Steps 1 and 2; evidence regenerated on the merged checkout before hand-in.
