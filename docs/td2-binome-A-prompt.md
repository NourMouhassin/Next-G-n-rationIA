# TD 2 — Pair A: AI assistance declaration

**Assistant:** Claude (Anthropic), in a claude.ai chat, 18 November 2026.

**Requests from the student** (Mathias Silvert-Lis, summarised from French): explain the TD 2 assignment; do or guide Pair A's step; adapt the work to the uploaded `atelier-vote.py`, `skeleton-multi-llm-en.py`, `traces-td1.csv` and `reference-td1.csv`; give the Git commands to integrate it; assemble the group report from the three pairs' sections.

## What the assistant did

- Implemented `Orchestrateur.vote_k_sur_n` from the skeleton docstring and the assignment contract, with unit tests covering its five rules (strict majority, duplicates, errors kept in n, consensus, abstention).
- Wrote `comparer_quorums.py` (fixed 2-of-3 panel vs 3-of-5 quorum on C01–C20), reusing the proposal-building logic of `atelier-vote.py`.
- Ran both on the uploaded traces in its own sandbox (with a stub replacing the kit's `sandbox_sqlite.py`), and drafted the Pair A section.
- Checked Pair C's package before integration (code offline, no file collision, per-family rates recomputed from the traces) and assembled `reports/td2.md`, translating the Pair A section into English.

**Correction during the work:** a first version of the method read proposals as dictionaries, whereas `atelier-vote.py` passes `SimpleNamespace` objects. It was corrected (attribute access, dictionaries still accepted) before any use on the real traces. The `models` format (`provider:model_requested`) was taken from the skeleton docstring.

## What the student did

- Ran `atelier-vote.py` on his machine with the real kit, on the four official synthetic examples and on C01–C20, and checked every output.
- Generated the evidence files and checked that the quorum table regenerates identically from the repository alone.
- Checked that `main` contains exactly the 104 traces analysed, created the `td2/binome-A-vote` branch, merged the A, B and C branches into `main` and pushed.

## Review

The members of Pair A must be able to explain the method and every result in the report without assistance (individual quiz). Contribution and review of the second Pair A member: **[to fill]**.
