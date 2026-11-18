#!/usr/bin/env python3
"""
TD 2 - binôme A : tableau 2-sur-3 (panel fixe) vs 3-sur-5 (cinq modèles du TD 1)
sur les vingt questions C01 à C20, à partir des seules traces stockées du TD 1.

Même logique que atelier-vote.py : colonnes case_id / provider / model_requested /
value / verdict / nature / reference, dernière ligne du CSV = dernière tentative,
membre sans trace valide = gardé dans n sans voix. La décision est prise par VOTRE
Orchestrateur.vote_k_sur_n ; la référence n'est lue qu'après, pour comparer.

Depuis la racine du dépôt, chemins par défaut indépendants du répertoire courant :
    python td2/A-quorum/comparer_quorums.py
    python td2/A-quorum/comparer_quorums.py --traces td1/traces-td1.csv --reference td1/reference-td1.csv
"""
import argparse
import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

TD1 = Path(__file__).resolve().parents[2] / "td1"

PANEL_FIXE = [  # identique à PANEL dans atelier-vote.py
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
]
AUTRES_MODELES = ["dots-studio/dots-3-note-preview:free", "openai/gpt-oss-20b"]
QUESTIONS = [f"C{i:02d}" for i in range(1, 21)]
COLONNES_REF_POSSIBLES = ["revenue_cents", "reference", "value", "reference_cents", "expected", "expected_value"]


def charger_vote(chemin):
    spec = importlib.util.spec_from_file_location("student_skeleton", chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda propositions, k: module.Orchestrateur.vote_k_sur_n(None, propositions, k)


def lire_csv(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f))
    if not lignes:
        sys.exit(f"{chemin} est vide.")
    return lignes


def cinq_membres(lignes):
    """Panel fixe + les deux autres modèles, avec le provider trouvé dans les traces."""
    membres = list(PANEL_FIXE)
    paires = {(l["provider"], l["model_requested"]) for l in lignes}
    for modele in AUTRES_MODELES:
        providers = sorted(p for (p, m) in paires if m == modele)
        if len(providers) != 1:
            sys.exit(f"{modele} : provider introuvable ou ambigu {providers}.\n"
                     f"Paires présentes : {sorted(paires)}")
        membres.append((providers[0], modele))
    absents = [m for m in membres if m not in paires]
    if absents:
        print(f"Attention, membres sans aucune trace : {absents}", file=sys.stderr)
    return membres


def propositions_pour(lignes, case, membres):
    """Copie de la logique de proposals_for (atelier-vote.py), pour n membres."""
    retenue = {}
    for l in lignes:  # la dernière ligne du fichier écrase les précédentes
        cle = (l["provider"], l["model_requested"])
        if l["case_id"] == case and cle in membres:
            retenue[cle] = l
    propositions, details = [], []
    for provider, modele in membres:
        l = retenue.get((provider, modele), {})
        valeur = l.get("value", "")
        valide = l.get("verdict") in {"correct", "incorrect"} and valeur not in {None, ""}
        propositions.append(SimpleNamespace(provider=provider, model_requested=modele,
                                            value=int(valeur) if valide else None,
                                            verdict="executed" if valide else "error"))
        if not l:
            details.append("absent")
        else:
            details.append(f"{valeur} ({l.get('verdict')})" if valeur not in {None, ""}
                           else (l.get("verdict") or "?"))
    return propositions, details


def references_traces(lignes, case):
    refs = {int(l["reference"]) for l in lignes
            if l["case_id"] == case and l.get("reference") not in {None, ""}}
    if len(refs) > 1:
        sys.exit(f"{case} : références contradictoires {refs} dans les traces.")
    return next(iter(refs), None)


def references_fichier(chemin):
    lignes = lire_csv(chemin)
    col_q = "case_id" if "case_id" in lignes[0] else None
    col_v = next((c for c in COLONNES_REF_POSSIBLES if c in lignes[0]), None)
    if not col_q or not col_v:
        sys.exit(f"Colonnes de {chemin} non reconnues : {list(lignes[0])}.\n"
                 f"Adaptez COLONNES_REF_POSSIBLES ou envoyez le fichier.")
    refs = {l[col_q]: int(float(l[col_v])) for l in lignes if (l[col_v] or "").strip() != ""}
    if not refs:
        print(f"Attention : {chemin} ne contient aucune valeur ({col_v} vide partout). "
              f"Références prises dans la colonne reference des traces.", file=sys.stderr)
    return refs


def decrire(d, n):
    if d["consensus"]:
        return f"consensus {d['value']} ({d['votes']}/{n})"
    return f"abstention (max {d['votes']}/{n})"


def accord(d, ref):
    if ref is None:
        return "réf. manquante"
    if not d["consensus"]:
        return "⏸ abstention"
    return "✅ = réf." if d["value"] == ref else "❌ faux consensus"


def changement(d3, d5):
    if d3["consensus"] and not d5["consensus"]:
        return "consensus → abstention"
    if not d3["consensus"] and d5["consensus"]:
        return "abstention → consensus"
    if d3["consensus"] and d3["value"] != d5["value"]:
        return "valeur différente"
    return "—"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--traces", type=Path, default=TD1 / "traces-td1.csv")
    p.add_argument("--reference", type=Path, default=TD1 / "reference-td1.csv", help="reference-td1.csv (sinon colonne reference des traces)")
    p.add_argument("--skeleton", type=Path, default=TD1 / "skeleton-multi-llm-en.py")
    p.add_argument("--nature", choices=["real", "replay", "simulation"], default="real")
    args = p.parse_args()

    vote = charger_vote(args.skeleton)
    lignes = [l for l in lire_csv(args.traces) if l.get("nature") == args.nature]
    if not lignes:
        sys.exit(f"Aucune ligne de nature '{args.nature}' dans {args.traces}.")
    membres5 = cinq_membres(lignes)
    refs_fichier = references_fichier(args.reference) if args.reference else {}

    tableau, detail, bilan = [], [], {"2-sur-3": {}, "3-sur-5": {}}
    for q in QUESTIONS:
        if not any(l["case_id"] == q for l in lignes):
            tableau.append(f"| {q} | — | aucune trace | | aucune trace | | |")
            continue
        p3, _ = propositions_pour(lignes, q, PANEL_FIXE)
        p5, det = propositions_pour(lignes, q, membres5)
        d3, d5 = vote(p3, 2), vote(p5, 3)
        # Référence lue APRES la décision, uniquement pour comparer.
        ref_t = references_traces(lignes, q)
        ref = refs_fichier.get(q, ref_t)
        if args.reference and ref_t is not None and q in refs_fichier and refs_fichier[q] != ref_t:
            print(f"Attention {q} : reference-td1.csv={refs_fichier[q]} mais traces={ref_t}",
                  file=sys.stderr)
        a3, a5 = accord(d3, ref), accord(d5, ref)
        bilan["2-sur-3"][a3] = bilan["2-sur-3"].get(a3, 0) + 1
        bilan["3-sur-5"][a5] = bilan["3-sur-5"].get(a5, 0) + 1
        tableau.append(f"| {q} | {ref} | {decrire(d3, 3)} | {a3} | {decrire(d5, 5)} | {a5} | {changement(d3, d5)} |")
        detail.append(f"| {q} | {ref} | " + " | ".join(det) + " |")

    print(f"## Vote : panel fixe 2-sur-3 vs quorum 3-sur-5 (traces TD 1, nature = {args.nature})\n")
    print("| Question | Référence | 2-sur-3 (panel fixe) | Accord | 3-sur-5 (5 modèles) | Accord | Changement |")
    print("|---|---|---|---|---|---|---|")
    print("\n".join(tableau))
    print("\n**Bilan** : " + " ; ".join(
        f"{cfg} → " + ", ".join(f"{k} : {v}" for k, v in sorted(b.items()))
        for cfg, b in bilan.items()))
    print("\n### Dernière tentative de chaque modèle (valeur et verdict TD 1)\n")
    print("| Question | Référence | " + " | ".join(f"{m.split('/')[-1]} ({pr})" for pr, m in membres5) + " |")
    print("|---|---|" + "---|" * len(membres5))
    print("\n".join(detail))


if __name__ == "__main__":
    main()
