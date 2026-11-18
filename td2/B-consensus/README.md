# B — The wrong consensus — Ilyess et Nour

[Section Step 2 du rapport](../../reports/td2.md) · [Preuves C09](evidence/C09-evidence.json)

Depuis `kit-td1` :

```powershell
.\.venv\Scripts\python.exe submission\td2\B-consensus\td2_wrong_consensus.py
```

Le script lit exclusivement `td1/` et réexécute le SQL en lecture seule. Il conserve
les requêtes originales dans `sql/`, le delta ligne par ligne dans `evidence/`,
et confronte les deux comptes manuels au `vote_k_sur_n` livré par A.
Résultats attendus : 0 à 2/3 et 0 à 3/5, tous deux faux ; référence et delta
487980 centimes. Les deux `pair_A_check` doivent être `passed`.
Relectures : [revue 1](review-1.md), [revue 2](review-2.md), À compléter.
