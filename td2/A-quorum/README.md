# A — Quorum

[Rapport A conservé](report.md) · [Rapport commun](../../reports/td2.md)

La méthode de A est conservée dans [le squelette partagé](../../td1/skeleton-multi-llm-en.py).
`comparer_quorums.py` la charge depuis `td1/`, sur les traces canoniques, sans appel API.
Le driver officiel `atelier-vote.py` est fourni ici pour reproduire les exemples.

Depuis `kit-td1` :

```powershell
.\.venv\Scripts\python.exe submission\td2\A-quorum\comparer_quorums.py
.\.venv\Scripts\python.exe submission\td2\A-quorum\atelier-vote.py
```

`../verify_structure.py` régénère le [tableau](results/td2-tableau-vote.md), vérifie
ses 20 décisions contre celles déjà livrées et contrôle les résultats JSONL de A.
Relectures : [revue 1](review-1.md), [revue 2](review-2.md), À compléter.
Noms/contributions individuels A : À compléter dans le rapport A.
