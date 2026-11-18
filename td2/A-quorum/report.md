## Étape 1 — Vote k-sur-n (binôme A)

### 1.1 La méthode `Orchestrateur.vote_k_sur_n`

Implémentée dans `skeleton-multi-llm-en.py`, conformément au contrat de la docstring :

1. seules les propositions `verdict == "executed"` qui portent une valeur votent ; un membre en erreur (HTTP 429, SQL invalide, absent) **reste compté dans n** mais ne vote pas ;
2. `k` doit être une majorité stricte, `n // 2 < k <= n`, sinon `ValueError` ;
3. deux propositions avec le même couple `(provider, model_requested)` sont refusées par `ValueError`, y compris si l'une est en erreur : un doublon n'est pas un second avis ;
4. si une valeur atteint k voix : `{"consensus": True, "value": v, "votes": nombre, "models": ["provider:model_requested", ...]}` ;
5. sinon : `{"consensus": False, "value": None, "votes": plus grand nombre de voix, "models": []}`. La méthode n'invente jamais de valeur.

Comme `k > n // 2`, deux valeurs ne peuvent pas atteindre k en même temps (il faudrait 2k > n voix) : la boucle peut donc renvoyer la première valeur qui atteint k sans ambiguïté. La méthode ne reçoit jamais la référence.

**Exemples synthétiques** (`python td2/A-quorum/atelier-vote.py`, nature `simulation`, n = 3, k = 2, référence 100) :

| Exemple | Propositions | Décision | Conforme à la référence |
|---|---|---|---|
| agreement | 100, 100, 120 | consensus 100 (2 voix) | oui |
| disagreement | 100, 110, 120 | abstention (max 1) | sans objet |
| unavailable | 100, erreur, erreur | abstention (max 1) | sans objet |
| wrong consensus | 0, 0, 100 | consensus 0 (2 voix) | **non** |

Le dernier exemple montre la limite du vote : une majorité d'accord sur une valeur fausse l'emporte.

### 1.2 Protocole de la comparaison

- **Données** : `traces-td1.csv`, 104 lignes, toutes `nature = real`, batch du 2026-10-21, cinq modèles. Export chronologique unique (dates croissantes), donc la dernière ligne d'un modèle sur une question est bien sa dernière tentative. `qwen/qwen3.8-27b` a 24 lignes au lieu de 20 : nouvelles tentatives après HTTP 429 sur C16, C18, C19 et C20.
- **Configurations** : panel fixe 2-sur-3 (`groq:openai/gpt-oss-120b`, `openrouter:cohere/north-mini-code:free`, `groq:qwen/qwen3.8-27b`, k = 2) ; quorum 3-sur-5 sur les cinq modèles (+ `openrouter:dots-studio/dots-3-note-preview:free`, `groq:openai/gpt-oss-20b`, k = 3).
- **Décision** : toujours prise par notre `vote_k_sur_n`. Une proposition vote si son verdict TD 1 est `correct` ou `incorrect` avec une valeur (même règle que `atelier-vote.py`) ; `not_executed` et `sql_invalid` restent dans n sans voix. La référence n'est lue qu'**après** la décision.
- **Référence** : `reference-td1.csv` (20 requêtes SQL écrites sans modèle et leurs valeurs `revenue_cents`). Les 20 valeurs sont identiques à la colonne `reference` des traces, chargée depuis ce même fichier au moment du batch TD 1 : aucune incohérence signalée par le script.
- **Contrôle croisé** : les 20 décisions 2-sur-3 de notre script sont identiques à celles de `atelier-vote.py --traces td1/traces-td1.csv --case Cxx` lancé question par question.
- **Reproduire** : `python td2/A-quorum/comparer_quorums.py`

### 1.3 Tableau des vingt décisions

| Question | Référence | 2-sur-3 (panel fixe) | Accord | 3-sur-5 (5 modèles) | Accord | Changement |
|---|---|---|---|---|---|---|
| C01 | 792800 | consensus 792800 (3/3) | ✅ = réf. | consensus 792800 (5/5) | ✅ = réf. | — |
| C02 | 590320 | consensus 590320 (2/3) | ✅ = réf. | abstention (max 2/5) | ⏸ abstention | consensus → abstention |
| C03 | 936350 | consensus 936350 (3/3) | ✅ = réf. | consensus 936350 (5/5) | ✅ = réf. | — |
| C04 | 2826250 | consensus 2826250 (3/3) | ✅ = réf. | consensus 2826250 (5/5) | ✅ = réf. | — |
| C05 | 38480 | consensus 38480 (3/3) | ✅ = réf. | consensus 38480 (5/5) | ✅ = réf. | — |
| C06 | 0 | consensus 0 (3/3) | ✅ = réf. | consensus 0 (5/5) | ✅ = réf. | — |
| C07 | 13970 | consensus 13970 (3/3) | ✅ = réf. | consensus 13970 (5/5) | ✅ = réf. | — |
| C08 | 605580 | consensus 605580 (2/3) | ✅ = réf. | consensus 605580 (3/5) | ✅ = réf. | — |
| C09 | 487980 | consensus 0 (2/3) | ❌ faux consensus | consensus 0 (3/5) | ❌ faux consensus | — |
| C10 | 558980 | consensus 558980 (2/3) | ✅ = réf. | consensus 558980 (3/5) | ✅ = réf. | — |
| C11 | 446690 | consensus 446690 (2/3) | ✅ = réf. | abstention (max 2/5) | ⏸ abstention | consensus → abstention |
| C12 | 1666490 | consensus 1666490 (3/3) | ✅ = réf. | consensus 1666490 (5/5) | ✅ = réf. | — |
| C13 | 107740 | consensus 107740 (3/3) | ✅ = réf. | consensus 107740 (5/5) | ✅ = réf. | — |
| C14 | 0 | consensus 0 (3/3) | ✅ = réf. | consensus 0 (5/5) | ✅ = réf. | — |
| C15 | 168680 | abstention (max 1/3) | ⏸ abstention | abstention (max 2/5) | ⏸ abstention | — |
| C16 | 376740 | consensus 376740 (2/3) | ✅ = réf. | consensus 376740 (4/5) | ✅ = réf. | — |
| C17 | 258180 | abstention (max 1/3) | ⏸ abstention | abstention (max 2/5) | ⏸ abstention | — |
| C18 | 62480 | consensus 62480 (2/3) | ✅ = réf. | consensus 62480 (3/5) | ✅ = réf. | — |
| C19 | 1990 | abstention (max 1/3) | ⏸ abstention | consensus 1990 (3/5) | ✅ = réf. | abstention → consensus |
| C20 | 1106090 | consensus 1106090 (3/3) | ✅ = réf. | consensus 1106090 (5/5) | ✅ = réf. | — |

**Bilan** : 2-sur-3 → ⏸ abstention : 3, ✅ = réf. : 16, ❌ faux consensus : 1 ; 3-sur-5 → ⏸ abstention : 4, ✅ = réf. : 15, ❌ faux consensus : 1

### 1.4 Dernière tentative de chaque modèle

| Question | Référence | gpt-oss-120b (groq) | north-mini-code:free (openrouter) | qwen3.8-27b (groq) | dots-3-note-preview:free (openrouter) | gpt-oss-20b (groq) |
|---|---|---|---|---|---|---|
| C01 | 792800 | 792800 (correct) | 792800 (correct) | 792800 (correct) | 792800 (correct) | 792800 (correct) |
| C02 | 590320 | 590320 (correct) | 2606320 (incorrect) | 590320 (correct) | 0 (incorrect) | 0 (incorrect) |
| C03 | 936350 | 936350 (correct) | 936350 (correct) | 936350 (correct) | 936350 (correct) | 936350 (correct) |
| C04 | 2826250 | 2826250 (correct) | 2826250 (correct) | 2826250 (correct) | 2826250 (correct) | 2826250 (correct) |
| C05 | 38480 | 38480 (correct) | 38480 (correct) | 38480 (correct) | 38480 (correct) | 38480 (correct) |
| C06 | 0 | 0 (correct) | 0 (correct) | 0 (correct) | 0 (correct) | 0 (correct) |
| C07 | 13970 | 13970 (correct) | 13970 (correct) | 13970 (correct) | 13970 (correct) | 13970 (correct) |
| C08 | 605580 | 605580 (correct) | 1188090 (incorrect) | 605580 (correct) | 25920 (incorrect) | 605580 (correct) |
| C09 | 487980 | 487980 (correct) | 0 (incorrect) | 0 (incorrect) | 0 (incorrect) | 487980 (correct) |
| C10 | 558980 | 558980 (correct) | 119410 (incorrect) | 558980 (correct) | 119410 (incorrect) | 558980 (correct) |
| C11 | 446690 | 446690 (correct) | 0 (incorrect) | 446690 (correct) | 0 (incorrect) | 322160 (incorrect) |
| C12 | 1666490 | 1666490 (correct) | 1666490 (correct) | 1666490 (correct) | 1666490 (correct) | 1666490 (correct) |
| C13 | 107740 | 107740 (correct) | 107740 (correct) | 107740 (correct) | 107740 (correct) | 107740 (correct) |
| C14 | 0 | 0 (correct) | 0 (correct) | 0 (correct) | 0 (correct) | 0 (correct) |
| C15 | 168680 | 68670 (incorrect) | 314020 (incorrect) | 0 (incorrect) | 168680 (correct) | 168680 (correct) |
| C16 | 376740 | 376740 (correct) | 376740 (correct) | not_executed | 376740 (correct) | 376740 (correct) |
| C17 | 258180 | 258180 (correct) | 0 (incorrect) | 248490 (incorrect) | sql_invalid | 258180 (correct) |
| C18 | 62480 | 62480 (correct) | 286650 (incorrect) | 62480 (correct) | 39580 (incorrect) | 62480 (correct) |
| C19 | 1990 | 1990 (correct) | 0 (incorrect) | 83580 (incorrect) | 1990 (correct) | 1990 (correct) |
| C20 | 1106090 | 1106090 (correct) | 1106090 (correct) | 1106090 (correct) | 1106090 (correct) | 1106090 (correct) |

### 1.5 Questions où la décision change entre 2-sur-3 et 3-sur-5

**C02** (âge exact 25 ans au 2026-09-25, toutes commandes ; référence 590320) — *consensus correct → abstention.*
Dans le panel, `gpt-oss-120b` et `qwen3.8-27b` donnent 590320, `north-mini-code` donne 2606320 : consensus correct à 2/3. Au 3-sur-5, `dots-3-note-preview` et `gpt-oss-20b` donnent tous deux **0** (valeur fausse partagée). Les voix se répartissent 590320 : 2, 0 : 2, 2606320 : 1 ; aucune valeur n'atteint 3, d'où l'abstention. La valeur fausse partagée ne gagne pas, mais elle égale la bonne et bloque le consensus.

**C11** (âge exact 25 ans au 2026-12-01, toutes commandes ; référence 446690) — *consensus correct → abstention.*
Panel : `gpt-oss-120b` et `qwen3.8-27b` donnent 446690, `north-mini-code` donne 0 : consensus correct à 2/3. Au 3-sur-5, `dots-3-note-preview` donne aussi **0** (même valeur fausse que `north-mini-code`) et `gpt-oss-20b` donne 322160. Répartition : 446690 : 2, 0 : 2, 322160 : 1, donc abstention.

**C19** (produit d, période septembre 2026, âge exact 25 ans au 2026-09-25 ; référence 1990) — *abstention → consensus correct.*
Panel : trois valeurs différentes, 1990 (`gpt-oss-120b`), 0 (`north-mini-code`), 83580 (`qwen3.8-27b`, obtenue à la 2e tentative après un HTTP 429) : abstention à 1/3. Au 3-sur-5, `dots-3-note-preview` et `gpt-oss-20b` donnent 1990 : la valeur atteint 3/5, consensus correct.

### 1.6 Décision identique, marge modifiée

- **C16** (référence 376740) : `qwen3.8-27b` est `not_executed` après deux HTTP 429. Il reste dans n = 3 sans voter : le consensus 2/3 (`gpt-oss-120b`, `north-mini-code`) est obtenu **au seuil exact**. Une erreur de plus et le panel s'abstenait. Au 3-sur-5, la marge remonte à 4/5.
- **C17** (référence 258180) : abstention dans les deux configurations. Au 3-sur-5, `dots-3-note-preview` renvoie un SQL invalide (`syntax_error near "AS"`) : il reste dans n = 5 sans voter. La bonne valeur ne réunit que 2 voix (`gpt-oss-120b`, `gpt-oss-20b`), sous le seuil de 3.
- **C15** (référence 168680) : les trois membres du panel se trompent avec trois valeurs différentes (68670, 314020, 0). L'abstention **protège** ici d'une erreur. Au 3-sur-5, la bonne valeur arrive en tête (`dots-3-note-preview`, `gpt-oss-20b`) mais avec 2 voix, sous le seuil : toujours abstention.
- **C18** (référence 62480) : `qwen3.8-27b` réussit à sa 2e tentative après un HTTP 429 ; c'est cette dernière tentative qui vote et donne le consensus 2/3. Sans cette relance, le panel se serait abstenu (1/3).
- **C10** (âge au moment de la commande ; référence 558980) : `north-mini-code` et `dots-3-note-preview` partagent la valeur fausse **119410** ; elle est mise en minorité (1/3 dans le panel, 2/5 au 3-sur-5). Consensus correct dans les deux cas.

### 1.7 Consensus erroné dans notre batch : C09 (transmis au binôme B)

**C09** (âge exact 25 ans au 2026-09-26, toutes commandes ; référence 487980). `north-mini-code`, `qwen3.8-27b` et `dots-3-note-preview` renvoient tous **0**. Seuls `gpt-oss-120b` et `gpt-oss-20b` donnent 487980.

- 2-sur-3 : consensus sur **0** (`north-mini-code` + `qwen3.8-27b`), faux.
- 3-sur-5 : consensus sur **0** (+ `dots-3-note-preview`), faux, avec une voix de plus.

Agrandir le quorum ne corrige pas une erreur partagée par une majorité ; ici il la confirme. La cause SQL (requêtes qui renvoient 0) est analysée à l'étape 2.

### 1.8 Ce que nous en concluons

- **Bilan** : 2-sur-3 → 16 corrects, 1 faux consensus (C09), 3 abstentions (C15, C17, C19). 3-sur-5 → 15 corrects, 1 faux consensus (C09), 4 abstentions (C02, C11, C15, C17).
- **Le 3-sur-5 n'est pas meilleur sur ce batch** : il gagne C19, perd C02 et C11 (consensus corrects devenus abstentions) et ne corrige pas C09. Une abstention est sûre (pas de mauvaise valeur), mais elle a un coût : il faut alors une référence ou une revue humaine.
- **Les erreurs sont toutes sur les questions d'âge** : les dix questions de période et de produits seuls (C01, C03 à C07, C12 à C14, C20) sont unanimes 5/5 et correctes ; tous les désaccords et le faux consensus concernent l'âge (C02, C08 à C11, C15 à C19). Sur les questions simples, le vote coûte sans rien apporter ; sur les questions d'âge, il ne suffit pas toujours.
- **Les votants ne sont pas indépendants** : `north-mini-code` et `dots-3-note-preview` partagent la même valeur fausse sur C09, C10 et C11. Et `gpt-oss-120b` / `gpt-oss-20b` appartiennent à la même famille : le quorum 3-sur-5 ne réunit donc pas cinq familles distinctes, contrairement au panel fixe.
- **Limites** : 20 questions et un seul batch. Ces chiffres sont une observation sur ce batch, pas un taux d'erreur général, un classement durable ni une garantie d'erreur du quorum.

### 1.9 Contribution du binôme A

- [Nom 1] : …
- [Nom 2] : …
