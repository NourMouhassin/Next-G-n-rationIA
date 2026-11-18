# Development request — Pair B

User request preserved verbatim below. Codex assistance is declared in the report;
personal review by Ilyess and Nour is not inferred from automated execution.

Réalise directement dans VS Code et le terminal la partie 2 du TD2 ESILV, « The wrong consensus », attribuée à Ilyess et Nour (binôme B). Limite les modifications à notre partie.

Sujet officiel : https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/kit-td1/enonce-td2-en.html

Dépôt : https://github.com/NourMouhassin/Next-G-n-rationIA

Retrouve le dépôt local, qui était dans `kit-td1/submission`, et utilise le Python 3.12 du `.venv` existant. Vérifie `git status`. Pars d’une branche qui contient les cinq lots TD1 consolidés. Le commit `bd79f79dd738a292ae11f831b9e44ac53a10e8ad` les contient, alors que le README de `main` affiche encore 80/100. Préserve les travaux des autres binômes. Tout le diagnostic se fait hors ligne, sans appel aux API des modèles.

1. Parcours les résultats finaux des 100 cellules à partir de `traces-td1.csv`. Utilise la dernière tentative retenue par modèle et question. Vérifie le cas réel C09 signalé dans `reports/td1.md` : Qwen et Cohere donnent 0, pour une référence annoncée de 487 980 centimes. Cites-en les identifiants de traces.
2. Pour C09, affiche les cinq propositions et leurs verdicts. Calcule les votes à la main pour le panel fixe **2 sur 3** (GPT-OSS 120B, Cohere, Qwen) et le quorum **3 sur 5** (les cinq modèles TD1). Indique pour chacun la valeur retenue ou l’abstention, le nombre de voix, et l’accord avec la référence. Les erreurs sans valeur restent dans le panel, sans voix. Vérifie avec `vote_k_sur_n` dès que le binôme A l’a livré.
3. Reproduis les **deux requêtes fautives complètes**, telles qu’enregistrées dans les traces, et exécute-les sur `data/boutique.sqlite` en lecture seule. Compare-les à la requête de référence. Explique précisément quelle condition `WHERE` ou `JOIN` produit chaque erreur et à quelle date l’âge doit être évalué selon C09.
4. Écris et exécute une requête SQL de diagnostic qui liste les `customer_id`, les lignes de commande omises ou ajoutées à tort et leur chiffre d’affaires HT en centimes. Préserve chaque ligne de commande pour éviter de perdre des ventes identiques. Vérifie que le total des lignes omises moins celui des lignes ajoutées vaut exactement `référence − valeur fautive`. Contre-vérifie le total par un calcul indépendant avec les CSV.
5. Rédige la section « Step 2 — The wrong consensus » dans `reports/td2.md`, en respectant les sections des autres binômes. Ajoute le fichier SQL de diagnostic, la commande pour le reproduire et les résultats réellement obtenus. Explique en une phrase ce que ce cas implique pour le contrôle des réponses. Prépare un commit sur une branche dédiée et pousse cette branche si les droits le permettent. Laisse la fusion à l’équipe.

Économise les tokens : lis les fichiers utiles, réutilise l’existant et évite de recopier les logs. Termine par un bilan court avec les deux verdicts, le total du delta, le hash du commit et ce qui reste à vérifier. Présente à Ilyess et Nour les éléments à relire eux-mêmes avant la revue du groupe.
