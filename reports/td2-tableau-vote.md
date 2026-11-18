## Vote : panel fixe 2-sur-3 vs quorum 3-sur-5 (traces TD 1, nature = real)

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

### Dernière tentative de chaque modèle (valeur et verdict TD 1)

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
