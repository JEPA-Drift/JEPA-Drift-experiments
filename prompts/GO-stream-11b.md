# GO — Stream 11b : raffinements de l'audit (bruit de N2 sur fond D6, biais de sélection des frontières placebo)

Date : 2026-10-17.
Destinataire : instance Claude Code ayant livré le stream 11 (suivi « 11b »).
Contexte : `prompts/wrapups/wrapup-11.md` (audit livré et poussé, `9a36c2f`).

## Contexte

L'audit a livré les 8 CSV de `results/audit/`. Deux mises en garde du wrapup-11 doivent être
quantifiées avant que le §2 de l'article ne cite N2 ou le SR² de marché :

- **N2** (rapports 3,6–11 pour les directions F1, jusqu'à 501 pour `rev_21`) inclut le bruit
  d'estimation de la covariance Ledoit–Wolf glissante sur 60 jours : le rapport surestime le canal.
- **SR² de marché** : les frontières sont des points de retournement de SPY datés ex post ; cette
  sélection gonfle le SR² de marché, que le débiaisage du bruit ne corrige pas.

Deux mesures manquent, toutes deux réalisables dans `experiments/audit_information.py` avec les
briques existantes (`injection.symmetrize`, `rolling_lw`, `info_ratio`, `spy_phases`,
`transitions`, `debiased_sr2`, `_ci`).

## Tâche

1. **Bruit de N2 sur fond symétrisé (D6).** Pour chaque jeu (`d2_us97`, `d3_239`), chaque
   direction F1 (colonnes de B) et F2 (15 caractéristiques) :
   - tirer B = 2000 fonds D6 de la fenêtre W (`injection.symmetrize`, graines
     `SeedSequence([11, 11, …])`) — le vrai Σ_t y est constant ;
   - calculer `info_ratio` sur chaque fond : c'est le rapport « bruit seul » (écart de Jensen de
     l'estimation LW 60 jours) ;
   - rapporter dans `results/audit/channel_ceilings.csv` : les variantes existantes, plus une
     variante `lw60_d6` (médiane du rapport bruit sur les B fonds) et la valeur nette
     `value_net = value − bruit` (nouvelle colonne ou variante ; documenter le schéma).
   Test : sur données i.i.d. gaussiennes, le rapport bruit est proche de 1 (borne documentée) ;
   sur D6, strictement supérieur à 1.
2. **Biais de sélection du SR² de marché, frontières placebo.** Pour chaque datation
   (`lt_spy`, `strict_ps`, `symmetric`) et chaque jeu :
   - tirer P = 2000 jeux de frontières placebo : mêmes longueurs de phases que la datation réelle,
     débuts uniformes dans W (graines fixes), phases reconstruites comme (début, fin] ;
   - pour chaque jeu placebo, médiane `sr2_debiased` du sous-espace `market` sur les transitions
     résultantes (mêmes règles : n₁, n₂ ≥ `MIN_PHASE`, contrôle de fenêtre) ;
   - rapporter (niveau `placebo` dans `drift_sharpe_transitions.csv`, ou CSV dédié) : médiane
     réelle, médiane placebo, rapport réel/placebo (facteur de sélection), IC bootstrap de la
     médiane placebo.
   Test : le rapport réel/placebo est > 1 sur les deux jeux ; sur un panel i.i.d. sans structure,
   il est ≈ 1 (borne documentée).

## Contraintes

- Fenêtre 2005–2019 uniquement, contrôle bloquant ; aucune donnée postérieure au 2019-12-31.
- Interpréteur `.venv/bin/python` (chaîne `conda activate Trading` puis venv — règle AGENTS.md).
- `SeedSequence` uniquement ; déterminisme au SHA-256 près : deux exécutions complètes donnent
  les mêmes octets pour les CSV modifiés ou ajoutés.
- CSV écrits par `save_fair_csv` ; pas de nouvelle figure.
- Tests dans `tests/test_audit.py` (contrat de chaque fonction publique nouvelle + bornes).
- Ne pas casser les lecteurs existants des CSV : préférer de nouvelles valeurs de `variant` /
  `level` à de nouvelles colonnes ; documenter dans le wrapup.
- `docs/DEVIATIONS.md` : entrées `C-audit-n2-noise` et `C-audit-placebo` (français) si les choix
  s'écartent du wrapup-11.

## Exécution

- Attendre le correctif d'environnement du chercheur (hook pre-commit + recette worktree d'AGENTS.md),
  puis créer le worktree depuis `origin/main` à jour :
  `git worktree add -b stream-11b ~/JEPA-Drift-stream-11b origin/main`, liens absolus `.venv` et
  `external`, `data/raw` en liens par sous-dossier (`d3_yf`, `baf`).
- Enregistrer le plan dans `prompts/plans/plan-11b.md` avant toute ligne de code
  (règle C-plan-recording).
- Clôture : wrapup `prompts/wrapups/wrapup-11b.md`, reindex, `make check`, commit
  `feat(audit): quantify the N2 estimation noise on D6 and the market SR2 selection bias`,
  rebase sur `origin/main`, range check (aucun chemin `data/raw/eurofidai/` ni
  `data/derived/d4_eurofidai/`, aucun fichier > 50 Mo), `git push origin stream-11b:main`.

## Commandes de vérification

```bash
pytest -q tests/test_audit.py
python experiments/audit_information.py --datasets d2_us97 d3_239 --out results/audit
python experiments/audit_information.py --datasets d2_us97 d3_239 --out $SCRATCH/audit2 --fig-dir $SCRATCH/fig2 --log-dir $SCRATCH/log2
diff <(sha256sum results/audit/*.csv) <(sha256sum $SCRATCH/audit2/*.csv)
make check
```
