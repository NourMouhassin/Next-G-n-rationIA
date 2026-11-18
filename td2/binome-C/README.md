# TD2 — Binôme C: deterministic routing policy

This folder is **only** the group's Step 3 / Pair C. It does not replace the
other two branches. Inputs remain the group's original TD1 files at repo root.
There are no network calls and no API credentials are needed.

## To reproduce on the group repository

From the repository root with Python 3.10+:

```powershell
python td2/binome-C/atelier-routage-original.py
python td2/binome-C/atelier-routage-adapte.py --check-rates
python td2/binome-C/atelier-routage-adapte.py --table
python td2/binome-C/atelier-routage-adapte.py
python td2/binome-C/atelier-routage-adapte.py --extra
python td2/binome-C/test_routage.py
python td2/binome-C/produce_evidence.py
```

`produce_evidence.py` saves the seven unchanged-kit decisions, seven adapted
decisions, four additional route demonstrations, per-family success rates,
unit-test log and a manifest with the SHA-256 of the actual source comparison.
Those files are written only under `evidence/td2-binome-C/`.

**Pack basis:** official TD2 routing code from the student kit, as preserved in
a public ESILV student kit copy; original simulator copied without edits.
The adapted simulator substitutes the group's own five model routes and family
observations. It deliberately takes its model identifiers from the existing
`modeles-autorises.json`, its results from `model-question-comparison-en.csv`,
its pricing from the dated `docs/paid-route-snapshot.json`, and its family
preferences from `policy.json`.

The check named in a routing result is a **required downstream validation**, not
a verification carried out by this simulator. The simulator does not issue model
calls or run a production SQL verifier. Quota availability and waiting times are
illustrative. The Oct 21 price snapshot is not a current price guarantee.

Group report section: [`../../reports/td2-binome-C.md`](../../reports/td2-binome-C.md).

## Merge without overriding the other pairs

The A branch is `td2/binome-A-vote`; B is
`td2/binome-B-wrong-consensus`. Neither is yet integrated into `main` in the
checked repository state. Pair C adds only these new paths:

- `td2/binome-C/*`
- `reports/td2-binome-C.md`
- `docs/td2-binome-C-prompt.md`
- `evidence/td2-binome-C/*`

The team should merge A/B/C and collect the three sections in
`reports/td2.md`, crediting actual member contributions only after review.
