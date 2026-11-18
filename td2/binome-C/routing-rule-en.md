# TD2 — Pair C: one-page routing rule

**Scope:** ESILV DIA4, subgroup 5. Empirical input: the 100 final cells in the
team's TD1 `model-question-comparison-en.csv`. Rule for an *internal dashboard*,
a *customer-facing number* and a *payout*. This is a batch-specific policy, not a
verified general ranking. Free-tier status and quota are not guaranteed.

## Route by family

All routes below have **zero marginal cash** in the recorded TD1 free-tier
experiment. Ties are broken by explicit policy preference, not by invented
paid-route prices. `F1`/`F3` prefer a small free OpenRouter route, preserving other
routes for age-related tasks. A model is primary-eligible if **all** the observed
TD1 cases for that family were correct. Errors and missing answers are failures.

| Family (TD1 cells) | Observed evidence and first route | Dashboard | Customer-facing | Payout |
|---|---|---|---|---|
| **F1 period** C01,C04,C05,C06,C07,C20 | Cohere 6/6 (also other four 6/6). Free. | Log only, no secondary check | 2/3 diverse-family quorum; if insufficient, deterministic SQL or abstain | Reference SQL + human approval |
| **F2 age at reference date** C02,C08,C09,C11 | GPT-OSS **120B 4/4**; Qwen 3/4, GPT-OSS 20B 2/4, Cohere/Dots 0/4. Groq Free. | Read-only reference SQL | Reference SQL, reject mismatch | Reference SQL + human approval |
| **F2b age at order** C10 | GPT-OSS **20B 1/1** (120B/Qwen also 1/1); smallest documented paid equivalent, Groq Free. | Reference SQL | Reference SQL, reject mismatch | Reference SQL + human approval |
| **F3 product list** C03,C12,C13,C14 | Dots **4/4** (also other four 4/4). OpenRouter Free. | Log only, no secondary check | 2/3 diverse-family quorum; if insufficient, deterministic SQL or abstain | Reference SQL + human approval |
| **F4 combinations** C15,C16,C17,C18,C19 | GPT-OSS **20B 5/5**; 120B 4/5, Dots 3/5, Cohere/Qwen 1/5. Groq Free. | Read-only reference SQL | Reference SQL, reject mismatch | Reference SQL + human approval |

F2b isolates age at order *without another filter* (C10); C18 is age at order
**combined** with a period and belongs to F4. F2/F2b/F4 insist on a deterministic
check because the group's **C09 real wrong consensus** is `0` versus `487980`
cents even for the fixed 2-of-3 and full 3-of-5 panels. The simulator outputs
the **required check**, but does not itself execute that verifier.

## Fallbacks, deadlines and costs

1. **Included**: choose an available zero-cash route that got **every case of
   the family correct**, preferring truly free (allocation 0) to an already-paid
   subscription allocation. The `policy.json` preference breaks zero-cash ties.
2. **Next route**: for F1/F3 (all five models passed), use the next measured
   zero-cash route if the preferred provider is down (Cohere → Dots for F1;
   Dots → Cohere for F3). F2 has only 120B meeting all its family cells; F4
   has only 20B. Do not silently downgrade F2/F4 to weaker candidates.
3. **Defer**: if no included route is up, and an eligible free quota may reset
   before the deadline, defer, record a wake-up, then **re-measure** availability.
4. **Paid**: if cannot wait or no suitable refill, use only a documented paid
   route of the **exact same model** and within the allowed incremental budget.
5. **Abstain**: unknown family, no eligible model, deadline impossible or no
   authorised budget. High-impact requests never bypass the required verifier.

The hypothetical paid costs use the **21 Oct 2026** OpenRouter catalog in
`docs/paid-route-snapshot.json` and an **illustrative** 650 input + 300 output
token envelope. GPT-OSS 20B: **$0.0000387/request**; GPT-OSS 120B:
**$0.0002775/request**. These are *not measured prices or November-2026 offers*.
Cohere/Dots have no documented exact-model paid counterpart in this snapshot;
their paid equivalent is **N/A**, not zero.

**Why included before deferral?** In the kit, an *available* subscription with
`cash == 0` and `allocation > 0` enters the `included` branch before `waiting`.
Its fee is already paid, so executing avoids a certain delay for an uncertain
free reset. **Reverse only if** scarce remaining subscription quota must be
reserved for expected urgent/high-impact work, while a nonurgent request has
sufficient slack for a likely free refill; no reset is guaranteed.

The seven kit scenarios and four group-specific scenarios are recorded in
`evidence/td2-binome-C/`. They use **fictional availability**. No new LLM request
was issued; the approval/quorum steps are **prescriptions, not live verifications**.
