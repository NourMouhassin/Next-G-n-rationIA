# Réception par G — aucun appel API

Les lots A–D proviennent de main (`196005d`); E de la PR #1 examinée
(`14150ae94d32aeb1db92b2a7f005c62e905de483`). Les cinq paires sont reçues.
Le tableau `reports/group-tracking.csv` distingue réception et éléments manquants.
La PR E reste ouverte, non fusionnée : seuls ses fichiers de résultats, causes et
déclarations individuelles ont été intégrés sur G. Les confirmations globales
de comptes et de coordination n'ont pas été supposées.

Pour un nouveau lot ou une correction, fournir les deux fichiers originaux
`state-LETTRE.jsonl` et `traces-LETTRE.csv`, la branche/PR et son commit, le nom
de l'opérateur, les quotas avant/après, les contrôles consommés et les incidents.
Ne fournir aucune clé ni capture contenant des identifiants privés.

Depuis le dossier `kit-td1`, déposer les deux fichiers dans `incoming\A` (exemple A),
puis contrôler sans modifier les résultats existants :

```powershell
.\.venv\Scripts\python.exe submission\receive_batch.py --member A --source incoming\A --origin "PR ou commit fourni"
```

Si le contrôle passe et qu'il s'agit d'un nouveau lot ou du même fichier identique :

```powershell
.\.venv\Scripts\python.exe submission\receive_batch.py --member A --source incoming\A --origin "PR ou commit fourni" --accept
.\.venv\Scripts\python.exe submission\validate_submission.py
.\.venv\Scripts\python.exe submission\td1.py pivot
```

`--accept` conserve une copie exacte dans `runs/received/A`, les SHA-256 et
l'origine, avant consolidation. Un original différent est refusé : ne pas le
remplacer automatiquement, examiner les différences et conserver les versions
comme expériences distinctes. Un hash local atteste les octets reçus, pas à lui
seul l'authenticité d'un appel API. Les doublons identiques sont dédupliqués ; les
doublons conflictuels, prompts/références incompatibles, mauvais modèles et écarts
CSV/JSONL sont refusés. Le SQL est réévalué exclusivement dans le sandbox local.

Pour F : fournir son compte rendu réellement effectué, son nom, la date et les
questions vérifiées. `reports/reference-review.csv` reste pending jusque-là.
Les 40 incidents 401 archivés ne doivent pas être importés comme un nouveau lot A :
ils restent distincts du lot principal et sont comptés dans l'audit global.
