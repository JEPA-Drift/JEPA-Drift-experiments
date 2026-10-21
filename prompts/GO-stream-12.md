# GO — Stream 12 (E1) : lancement — le problème sur données réelles, pipelines 1 → 2 → 3 et critères de J2

Date : 2026-10-18.
Destinataire : instance Claude Code en charge du stream 12 (relais après le stream 11b).
Contexte : `prompts/streams/prompt-12-e1.md` (tâche, à lire en intégralité et à exécuter telle quelle),
`prompts/wrapups/wrapup-11.md` et `prompts/wrapups/wrapup-11b.md` (l'audit et ses raffinements, livrés),
`CLAUDE.md`, prompts 2 à 8 (injections, représentations, pipelines, contrats).

## Tâche

Exécuter `prompts/streams/prompt-12-e1.md` (E1) : `experiments/e1_problem.py`, `configs/e1.yaml`,
`results/e1/{e1_cells,e1_slopes,e1_real_phases}.csv`, `results/e1/e1_j2_summary.txt`, `figures/e1/*`,
`logs/e1/`. Stream prioritaire : J2 = 25 octobre, E1 fournit deux des trois critères de J2 et les
chiffres du §2 (INDEX : priorité xhigh).

## Contraintes du chercheur (wrapup-11 et wrapup-11b, à intégrer dès le plan)

1. **Comparaison mesuré/prévu sur les dérives injectées.** Le bras injecté (fonds D6, familles F3/F1/F2)
   est le seul sans sélection de frontières : c'est là que la comparaison gains mesurés /
   `results/audit/predicted_gains.csv` a un sens. Le SR² de marché aux frontières datées est de la
   sélection (wrapup-11b : médiane placebo −1,7 à −2,6, excès réel − placebo 21 à 43, p ≤ 0,0015 sur les
   deux jeux et les trois datations) : le bras réel (item 3 du prompt) est descriptif de la datation, et les
   gains 2→3 prévus, qui divisent par ce SR² de marché, sous-estiment le rapport non sélectionné. Ne pas
   corriger `predicted_gains.csv` rétroactivement ; lire ses gains 2→3 comme des rapports à un dénominateur
   sélectionné.
2. **Jamais de valeur de planification à la place d'un NaN** (règle wrapup-11, déjà en vigueur) : les
   médianes négatives de D3 (idiosyncratique, risque R9) donnent NaN, sans substitution.
3. **Flux de signes sur fonds D6** (`injection.symmetrize`) pour les directions rejetées par la symétrie
   centrale (PC1, PC2 sur D3, `char:rev_21`) — le prompt le prévoit déjà (bras injecté SYM-D2/SYM-`d3_239`,
   critère J2 (i)) ; le garantir dans le plan.
4. **N2 citable = `lw60_net`** (F1 : 1,74–2,40 sur D2, 1,89–3,04 sur D3 ; F2 : 1,45–1,88 ; `rev_21` 0,94,
   l'ancien 501 étant un artefact de dénominateur), présenté comme majoritairement de la volatilité commune
   — pour le §2, jamais le rapport brut `lw60` (wrapup-11b).
5. **Correctif d'environnement appliqué** (`985353b`, dont `4ea0ee4`) : le hook pre-commit n'exporte plus
   `GIT_DIR` vers `make check` (`data/derived/MANIFEST.json` et `logs/data/build.log` ne sont plus réécrits) ;
   la recette `CLAUDE.md` prescrit `data/raw/` en liens par sous-dossier. Aucun contournement à prévoir.

## Exécution

- Créer le worktree depuis `origin/main` à jour (`985353b`) :
  `git worktree add -b stream-12 ~/JEPA-Drift-stream-12 origin/main`, liens absolus `.venv` et `external`,
  `data/raw/` en liens par sous-dossier (`d3_yf`, `baf`) — recette `CLAUDE.md`.
- Enregistrer le plan dans `prompts/plans/plan-12.md` avant toute ligne de code (règle C-plan-recording),
  avec les hypothèses à trancher au GO (revue de plan comme au stream 11).
- Interpréteur `.venv/bin/python` (chaîne `conda activate Trading` puis venv). Fenêtres 2005–2019 par défaut ;
  `--include-test-window` refusée tant que la configuration n'est pas gelée (prompt 21).
- `SeedSequence` uniquement ; déterminisme au SHA-256 près sur les CSV ; parallélisme par cellule sans effet
  sur les résultats (même schéma que 11b : `concurrent.futures`, contexte `spawn`, une graine par cellule).
- Option `--quick` (100 onsets, deux SR) pour un test de fumée en moins de 10 minutes.
- Clôture : wrapup `prompts/wrapups/wrapup-12.md`, reindex, `make check`, commit
  `feat(e1): measure the E1 detection problem and the J2 criteria (stream 12)`, rebase sur `origin/main`,
  range check (aucun chemin `data/raw/eurofidai/` ni `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo),
  `git push origin stream-12:main`.

## Commandes de vérification

```bash
pytest -q tests/test_e1.py                       # tests du stream (contrat de chaque fonction publique)
python experiments/e1_problem.py --quick --out results/e1_quick
python experiments/e1_problem.py --out results/e1 && cat results/e1/e1_j2_summary.txt
make check
```
