# Next-G-n-rationIA — ESILV

| TD | Livrables et reproduction | Rapport |
|---|---|---|
| TD1 | [Données, références, traces et scripts](td1/README.md) | [Rapport TD1](reports/td1.md) |
| TD2 | [A : quorum, B : consensus, C : routage](td2/README.md) | [Rapport TD2](reports/td2.md) |
| TD3 | [À compléter](td3/README.md) | [Rapport TD3](reports/td3.md) |

Python 3.12, bibliothèque standard uniquement. Les données et traces TD1 ont une
seule localisation canonique : `td1/`. Le vote partagé est dans
`td1/skeleton-multi-llm-en.py`, chargé par A et B sans copie du code.

Depuis le dossier existant **kit-td1**, qui contient `.venv` et `submission` :

```powershell
.\.venv\Scripts\python.exe submission\td2\verify_structure.py
```

Depuis un clone autonome, utiliser Python 3.12 : `python td2/verify_structure.py`.
Cette commande est entièrement hors réseau : tests TD1, tableau A sur 20 questions,
comparaison B avec le vote A, contrôle des empreintes et liens du rendu.
Aucun appel API ni nouvelle expérience n'est nécessaire.

Les branches A (`3bb1dce`) et B (`c993264`) sont intégrées sur
`td2/structure-rendu` ; la fusion sur main reste à l'équipe. Aucune branche ou PR C
n'a été trouvée lors de la vérification. Ses livrables, les revues humaines TD2 et
le TD3 restent explicitement « À compléter ». L'assistance Codex n'est pas une revue humaine.
