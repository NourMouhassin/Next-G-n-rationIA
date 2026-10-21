# Informations à demander au groupe avant les appels

| Lot | Modèle | Questions | Fournisseur | Budget à prévoir |
|---|---|---|---|---|
| A | `openai/gpt-oss-120b` | C01 à C20 | Groq | 20 appels initiaux + réserve cible de 5 |
| B | `openai/gpt-oss-20b` | C01 à C20 | Groq | 20 appels initiaux + réserve cible de 5 |
| C | `cohere/north-mini-code:free` | C01 à C20 | OpenRouter | 20 appels initiaux + réserve cible de 5 |
| D | `qwen/qwen3.8-27b` | C01 à C20 | Groq | 20 appels initiaux + réserve cible de 5 |
| E | `dots-studio/dots-3-note-preview:free` | C01 à C20 | OpenRouter | 20 appels initiaux + réserve cible de 5 |

Source : `consigne-etudiante-en.md`, §5 et `modeles-autorises.json`.
Ce budget n'est pas un quota fournisseur garanti. Chaque opérateur lit son quota
réel après les contrôles et vérifie les limites par minute, par jour et par tokens.
Le total est de 100 appels initiaux : 60 Groq et 40 OpenRouter, hors reprises/contrôles.
Un `check_access.py` complet consomme 3 appels Groq et 2 OpenRouter. Si un seul
contrôle a eu lieu, ces nombres sont à décompter ; ne pas supposer qu'il n'y en a eu
qu'un sans consulter les compteurs. La réserve de 5 est partagée entre contrôles
supplémentaires et reprises, pas 5 en plus pour chacun.

Message simple à transmettre personnellement au groupe :

> Quel lot A/B/C/D/E m'est attribué, et dois-je faire toutes les questions C01–C20 ?
> Qui prend les autres lots ? C et E ont-ils deux comptes OpenRouter personnels
> distincts, et A/B/D chacun leur compte Groq personnel gratuit ?
> Quand est-ce mon tour, avec personne d'autre en train d'appeler les modèles ?
> Qui contre-vérifie mes références et qui consolide les fichiers originaux ?

Sur ton compte : relever le quota restant après les contrôles déjà consommés.
S'il ne permet pas les 20 appels et la réserve, répartir les questions avec le
groupe ou demander le secours identifié au professeur. Ne pas créer une nouvelle
clé pour prétendre augmenter la capacité du même compte.

Les confirmations restent absentes dans `allocation.json`. Aucun lot n'a été choisi.
Pour lancer ensuite depuis ton terminal PowerShell VS Code déjà configuré,
rester dans le dossier du kit et utiliser son environnement existant :

```powershell
.\.venv\Scripts\python.exe submission\td1.py prepare
# Remplacer LETTRE uniquement après attribution et configuration d'allocation.json :
# .\.venv\Scripts\python.exe submission\td1.py run --member LETTRE
```

Les clés sont héritées du terminal. Ne pas les afficher, les transmettre ou les
copier dans un fichier. La préparation est hors réseau ; `run` fait les vrais appels.
Après le lot, conserver `runs/state-LETTRE.jsonl` et `runs/traces-LETTRE.csv` et relever
le compteur de quota final. Ne pas supprimer l'état pour recommencer une cellule.
