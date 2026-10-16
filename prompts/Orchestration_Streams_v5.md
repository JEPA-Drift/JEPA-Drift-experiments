# Orchestration des streams — `Prompts_Claude_Code_v5.md`

Date : 2026-10-16. Sources : `prompts/Prompts_Claude_Code_v5.md` (28 prompts) et
`prompts/Plan_Claude_Opus_v4_correction.md` (lot 1, étape 2).

## 0. Lot 1 déjà incorporé et vérifié (étape 2)

Les 6 fichiers du lot 1 sont en place à leurs chemins cibles et vérifiés :

```
jepadrift/floors.py                  (147 l)   bibliothèque des planchers analytiques (Lemme 1, Prop. 2-3, M(D), absorption)
jepadrift/__init__.py                (0 l)    marqueur de package (ajouté, nécessaire à l'import)
tests/test_floors.py                 (52 l)    6 tests de contrat
paper/sec3_theory.tex                (112 l)   §3 théorie (v0)
paper/appA_proofs.tex                (46 l)    annexe A, preuves
paper/articleC_biblio_addendum.bib   (81 l)    addendum bibliographique
experiments/e2_floor_validation.py   (367 l)   script E2 (validation Monte Carlo, jalon J1)
```

Vérification (env Trading : Python 3.12.9, numpy 1.26.4, scipy 1.16.2) :
- `pytest -q tests/test_floors.py` → **6/6 passés**.
- `python experiments/e2_floor_validation.py --reps 2000 --out results/e2` → **46/46 cellules, « J1: PASS »**, 75 s.
- H0 : mean=0.4998, acf1=+0.0002, cross=−0.0009, acf1(squares)=+0.067 → reproduit exactement le tableau de la correction.
- SHA-256 de `results/e2/e2_cells.csv` = `bce6d2b7f0be452e…`. La référence `e315e537ead0f656…` de la correction est bit-à-bit pour numpy 2.4.4 / scipy 1.17.1 : dans le `.venv` de prompt 1 (qui épingle ces versions), le hash de référence doit être reproduit ; ailleurs, le gate est « J1: PASS » (tolérance ±10 %), robuste à la version.

Les 6 fichiers sont aussi copiés dans `incoming/lot1/` (staging, gitignoré) : le **prompt 1 tourne tel quel**, sans adaptation.

## 1. Graphe de dépendances (28 streams)

Prérequis = section 3 du v5, précisés par les « Entrées » de chaque prompt.

| # | Stream | Piste | Prio | Jalon | Prérequis |
|---|--------|-------|------|-------|-----------|
| 1 | Socle + lot 1 + E2 | X | A | J1 | — |
| 2 | D1 + D2 (dépôt B) | X | A | J2 | 1 |
| 3 | D3 S&P 500 | X | A | J2, J3 | 1 |
| 4 | Surveillance : noyau, portage B | T→CC | A | J2 | 1, 2 |
| 5 | Injections F1–F4, fonds D5/D6 | T→CC | A | J2 | 1, 2, 3 |
| 6 | Représentations linéaires, interface Z | T→CC | A | J2 | 2, 3 |
| 7 | Pipelines P2-C, P3-C/D, P3-CS, P7 | T→CC | A | J2 | 4, 5, 6 |
| 8 | Tests de contrat, découplage, hooks | T→CC | A | fusions | 4, 5, 6, 7 |
| 9 | BAF | X | B | E9 | 1 |
| 10 | EUROFIDAI (D4) | X | B | E4-EU | 1 |
| 11 | Audit informationnel | T→CC | A | J2 | 2, 3, 6 |
| 12 | E1 | T→CC | A | J2 | 4, 5, 6, 7, 8, 11 |
| 13 | E3 | T→CC | A | J2 | 4, 5, 6, 7, 8 |
| 14 | CA-T-JEPA (code) | T→CC | A/B | J3 | 3, 6, 8 |
| 15 | T-JEPA pour BAF (code) | T→CC | B | E9 | 9 |
| 16 | Pré-entraînement + RankMe | X | A | J3 | 14 |
| 17 | IPCA | T→CC | A | E4, E5 | 3, 6 |
| 18 | Adaptateur CD-DFM | T→CC | B | E4, E5 | 3, 6 |
| 19 | E4 + P3-KF | T→CC | A/B | J4 | 5, 7, 11, 17 |
| 20 | Transmission T(u), dictionnaire | T→CC | B/C | J4 | 16, 17 |
| 21 | Gel config, runner, figures, traçabilité | T→CC | A | J4, J6 | 12, 13 |
| 22 | E5 | T→CC | A/B/C | J4 | 16, 17, 19, 21 |
| 23 | E6 | T→CC | B | J4 | 7, 16 |
| 24 | E9 | T→CC | B | J5 | 9, 15 |
| 25 | E8 | T→CC | A/B | J5 | 21 |
| 26 | E7 | T→CC | C | J5 | 16 |
| 27 | E10 | T→CC | C | J5 | 7 |
| 28 | E11 | T→CC | C | J5 | 5, 7, 14 |

T→CC = tâche piste T exécutée par Claude Code. Piste X = données/exécution (déléguée à l'agent via le prompt).

## 2. Chemin critique

- **J1 (18 oct.)** : stream 1 seul.
- **J2 (25 oct.)** : `1 → 2/3 → 4/5/6 → 7 → 8 → {12, 13}` (audit 11 en parallèle de 7–8). 6 niveaux.
- **J3 (1er nov.)** : `1 → 3 → 6 → 8 → 14 → 16`. 6 niveaux.
- **J4 (8 nov.)** : `1 → 2 → 4 → 7 → 8 → 12 → 21 → 22` (E5). 8 niveaux — **chemin critique global**.
- **J5 (15 nov.)** : `… → 21 → 25` (E8) et `… → 16 → 26` (E7). 7 niveaux.

Deux grandes familles parallèles dès que le socle (1) est posé :
- **Piste Data (X)** : 2, 3 (critiques), puis 9, 10 (indépendants, prio B).
- **Piste Surveillance/Représentations (T→CC)** : 4, 5, 6 → 7 → 8 → {12, 13, 14} → 16 → {20, 22, 23, 26}.
- **Piste JEPA** : 14 → 16 (compute lourd, fond de tâche).
- **Piste BAF** : 9 → 15 → 24 (indépendante de la finance).

## 3. Vagues recommandées (2–4 streams parallèles)

| Vague | Streams (parallèles) | Modèles | Déclencheur |
|-------|----------------------|---------|-------------|
| 0 | **1** socle + E2 + commit | Vibe High | immédiat (racine) |
| 1 | **2** D1+D2 · **3** D3 · **9** BAF · **10** EUROFIDAI | Vibe High/High/Med/High | CLAUDE.md + `.venv` posés (fin vague 0) |
| 2 | **4** noyau (Opus) · **5** injections · **6** interface Z (Opus) | Opus xhigh / Vibe High / Opus high | D1+D2+D3 prêts (fin vague 1) |
| 3 | **7** pipelines (Opus) · **11** audit · **17** IPCA · **18** CD-DFM | Opus xhigh / Vibe High ×3 | 4, 5, 6 prêts (fin vague 2) |
| 4 | **8** contrats · **19** E4+P3-KF · **27** E10 | Vibe High ×3 | 7 prêt (fin vague 3) |
| 5 | **12** E1 (Opus) · **13** E3 (Opus) · **14** CA-T-JEPA (Opus) | Opus high ×3 | 8 prêt (fin vague 4) — **pic de quota Claude** |
| 6 | **16** campagne pré-entraînement · **21** gel/runner · **15** T-JEPA BAF | Vibe High ×3 | 14 prêt + 12,13 prêts |
| 7 | **22** E5 (Opus max) · **20** transmission · **23** E6 · **26** E7 | Opus max / Vibe High/Med | 16 + 21 prêts (J4) |
| 8 | **25** E8 · **24** E9 · **28** E11 | Vibe High/High/Med | gel J4 (21) + 9, 15 prêts |

Notes de planification :
- La vague 0 est un **prérequis dur** : tous les streams lisent `CLAUDE.md` et le `.venv` produits par le prompt 1.
- Les streams 9 et 10 (prio B) sont des **fillers indépendants** : ils ne bloquent rien et amortissent les slots parallèles.
- La vague 5 concentre 3 streams Opus (pic de quota Claude Pro) : c'est le goulot. Les auto-relances au reset de quota la rendent autonome, mais c'est le point à surveiller.
- Stream 16 (campagne de pré-entraînement, 12+6 runs CPU) est un **fond de tâche long** : à lancer en arrière-plan dès que 14 est prêt.

## 4. Modèle recommandé par stream

Principe : **Claude Opus** (quota Pro 5 h, consommé ~3–4× plus vite en parallèle) réservé aux streams à haute précision / raisonnement où une erreur invalide un jalon. **Mistral Vibe Large-4** (quota team quasi illimité) pour le bulk mécanique / data / tooling / campagnes compute, ce qui permet de tenir 3–4 streams en parallèle la nuit sans épuiser le quota Claude.

| # | Stream | Modèle | Effort | Justification |
|---|--------|--------|--------|---------------|
| 1 | Socle + lot 1 + E2 | Mistral Vibe | High | mécanique, `CLAUDE.md` verbatim, lot 1 pré-vérifié |
| 2 | D1 + D2 | Mistral Vibe | High | data prep, critères vérifiables (effectifs, dates, SHA) |
| 3 | D3 | Mistral Vibe | High | data prep (yfinance), spec détaillée |
| 4 | Surveillance noyau | **Claude Opus** | **xhigh** | identité B à 1e-12, treillis exact (Markov), portage MIX/GARCH — précision critique |
| 5 | Injections F1–F4, D5/D6 | Mistral Vibe | High | générateurs, tests (|X̃|=|X|, orthogonalité, I_target) |
| 6 | Représentations, interface Z | **Claude Opus** | **high** | contrat d'interface porteur (tout s'y branche) |
| 7 | Pipelines P2/P3/P7 | **Claude Opus** | **xhigh** | portage R15, 3 calibrations (sign-flip, bootstrap, treillis) |
| 8 | Contrats, découplage, hooks | Mistral Vibe | High | tests spécifiés, garde-fous |
| 9 | BAF | Mistral Vibe | Medium | téléchargement Kaggle + prep |
| 10 | EUROFIDAI spec | Mistral Vibe | High | spec + loader (ingestion manuelle chercheur) |
| 11 | Audit informationnel | Mistral Vibe | High | mesures statistiques spécifiées |
| 12 | E1 | **Claude Opus** | **high** | expérience J2, grille + lectures + critères |
| 13 | E3 | **Claude Opus** | **high** | calibration exacte, critère J2 |
| 14 | CA-T-JEPA code | **Claude Opus** | **high** | archi ML, anti-effondrement, têtes impaire/paire |
| 15 | T-JEPA BAF | Mistral Vibe | High | enveloppe tabulaire |
| 16 | Pré-entraînement + RankMe | Mistral Vibe | High | campagne compute (peu de raisonnement, J3 gate) |
| 17 | IPCA | Mistral Vibe | High | ALS numpy, vérifiable (angles < 5°) |
| 18 | Adaptateur CD-DFM | Mistral Vibe | High | repo externe, fallback diagnostique prévu |
| 19 | E4 + P3-KF | Mistral Vibe | High | lois d'échelle (s'appuie sur le noyau Opus) |
| 20 | Transmission, dictionnaire | Mistral Vibe | High | spectres T(u) |
| 21 | Gel config, runner, figures | Mistral Vibe | High | tooling, traçabilité |
| 22 | E5 | **Claude Opus** | **max** | test central, porte J4, rétention r(D)/M(D), attribution |
| 23 | E6 | Mistral Vibe | High | second ordre F4 |
| 24 | E9 | Mistral Vibe | High | BAF (scikit-learn) |
| 25 | E8 | Mistral Vibe | High | régimes réels, après gel J4 (mesure sur pile construite) |
| 26 | E7 | Mistral Vibe | Medium | absorption |
| 27 | E10 | Mistral Vibe | High | robustesse |
| 28 | E11 | Mistral Vibe | Medium | second domaine |

Streams Opus (quota compté) : **4, 6, 7, 12, 13, 14, 22**. Tous les autres : Mistral Vibe.
Si le quota Claude est très serré, 12/13 peuvent basculer en Vibe High (la pile 4–8 est déjà Opus et les prompts sont prescriptifs) — mais 4, 6, 7, 14, 22 doivent rester sur Opus.

## 5. Une étape de plan est-elle recommandée ?

**Oui — et elle est fournie ici.** Aucun plan scientifique supplémentaire n'est nécessaire : le plan v4 + la correction + les 28 prompts sont complets et « prêts à copier-coller ». L'étape de plan indispensable est **l'orchestration au niveau des streams** (ce document) : graphe de dépendances, découpage en vagues, affectation des modèles. C'est le seul plan manquant avant de lancer les tmux. Ne pas sur-planifier au-delà.

## 6. Points de coordination / risques

1. **Dépendances hors `requirements` de base (prompt 1)** : `torch` (CPU) pour 14/15/16, `scikit-learn` pour 24, `yfinance` pour 3. Le `requirements.txt` de base (numpy 2.4.4, scipy 1.17.1, pandas, pyarrow, statsmodels, matplotlib, pytest, pyflakes) ne les couvre pas. Chaque stream concerné doit ajouter/épingler sa dépendance dans `requirements.txt` + `requirements.lock`.
2. **Épinglage numpy/scipy** : vérifier que `numpy==2.4.4` et `scipy==1.17.1` existent sur PyPI (le hash de référence E2 en dépend). Sinon, épingler les versions disponibles et consigner l'écart (`C-E2-env`).
3. **EUROFIDAI (10)** : l'ingestion des données nécessite l'export manuel du chercheur sur le portail ; le stream ne produit que la spec + le loader. Ne pas bloquer J2/J3 dessus (prio B).
4. **Niveaux du treillis (J2)** : le plan v4 indique 4,29 % / 5,03 % ; la correction donne la loi exacte 5,10 % (λ=11,2) et 4,34 % (λ=11,4) à H=5000. La bibliothèque recalcule ; le texte du plan est à corriger (piste T, lot 3).
5. **Contingence C1** : si J2 ne trouve aucune information de dérive exploitable, E6 (second ordre) passe avant E5 et F1/F2 deviennent secondaires — re-ordonnancer les vagues 7–8.
6. **Lot 2/3 non faits** : la correction s'arrête au lot 1. `monitors.py` (lot 2) = prompts 4–8 ; §1 v0 + Tableaux 1–3 + T6–T7 (lot 3) = piste T (Claude Opus, pas un prompt Claude Code).

## 7. Fin de stream (tous les streams)

Chronologie exacte, une fois le traitement d'un stream terminé : (1) l'instance invoque sa directive
de wrapup et enregistre le résumé dans `prompts/wrapups/wrapup-[XX].md` ([XX] = numéro du stream) ;
(2) `tools/reindex_graphify_jcodemunch.sh` (réindexe jCodeMunch et Graphify) ; (3) `make check`, puis
commit unique — ou plusieurs si les travaux sont hétérogènes — (Conventional Commits) ; (4)
`git push origin <branche courante>`. Avant chaque commit, l'instance invoque sa directive de
wrapup et enregistre le résumé dans `prompts/wrapups/wrapup-[XX].md`. Rôles : `prompts/streams/`
stocke les prompts des streams planifiés ; `prompts/wrapups/` stocke les résumés des traitements
des streams. Push autorisé tant que l'adresse du dépôt n'est ni partagée publiquement ni liée à
une publication (soumission anonyme ; le chercheur a confirmé le 2026-10-16 que le dépôt, public,
n'est connu de personne) ; les données EUROFIDAI ne quittent jamais la machine. Voir AGENTS.md
(règles d'ingénierie et « Repository layout ») et `prompts/streams/INDEX.md` (« Fin de stream »).
