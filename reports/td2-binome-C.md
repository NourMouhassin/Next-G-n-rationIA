# TD2 — Step 3 / Pair C: routing policy and simulator

**ESILV DIA4, subgroup 5 · 18 November 2026 · Course pack 2026-11-18-students-5.**

This is the **Pair C section only**, intended for integration in the collective
`reports/td2.md` after merging the separate A and B branches. It intentionally
does not change their code, tables or reported contributions. AI coding support
is declared in `docs/td2-binome-C-prompt.md`. **Actual member attribution and
human cross-review remain to be confirmed by the group.**

## Goal and sources

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

### Family-specific real TD1 results

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

## Official workshop: seven scenarios, before and after

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

## Priority question: included subscription vs waiting

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

## Execution, validation and limitations

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
adapted simulators emitted 7 decisions each. These archived previews should
be regenerated by `produce_evidence.py` on the actual repository before hand-in
for a cryptographic provenance link to the exact copied TD1 matrix. The test
fixture is **not** a second experimental sample.

### Limitations and remaining review

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

**Next steps:** merge the separate A/B/C branches, run the evidence generator
against the final shared checkout, have another pair cross-review the choices
and controls, then submit the full commit SHA and report permalink through Moodle.
