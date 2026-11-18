# TD1 — Données et expérience consolidée

[Rapport](../reports/td1.md) · [Index](../README.md)

Les cinq lots originaux sont dans `runs/`. Les fichiers `traces-td1.csv` et
`traces-td1.jsonl` sont les exports consolidés ; `reference-td1.csv` contient les
20 requêtes et valeurs. `data/` est l'unique base de référence, inchangée.
104 tentatives principales / 100 cellules ; les 40 erreurs 401 historiques
sont conservées à part dans `runs/failed-access/`, sans être confondues avec le panel.
Les déclarations/revues TD1 reçues restent dans `reports/`, sans nouvelles attestations.

Depuis `kit-td1` :

```powershell
.\.venv\Scripts\python.exe submission\td1\verify-data.py
.\.venv\Scripts\python.exe submission\td1\test_td1.py
.\.venv\Scripts\python.exe submission\td1\sandbox_sqlite.py --db submission/td1/data/boutique.sqlite
.\.venv\Scripts\python.exe submission\td1\td1.py pivot
```

Les chemins de ressources sont relatifs aux scripts. `td1.py prepare` et
`validate_submission.py` restent disponibles pour régénérer les livrables TD1 ;
la vérification de structure n'appelle pas ces commandes afin de préserver
les exports expérimentaux originaux octet pour octet.

Empreintes avant déplacement : [reorganization-input-hashes.json](evidence/reorganization-input-hashes.json).
Conserver les clés hors dépôt ; aucune clé n'est nécessaire aux commandes ci-dessus.
