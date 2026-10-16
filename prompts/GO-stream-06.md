# GO — Stream 06 (représentations linéaires et interface Z) : revue du plan et réponses aux hypothèses

Date : 2026-10-16.
Destinataire : instance Claude Code en charge de l'implémentation du stream 06
(`prompts/streams/prompt-06-representations-z.md`).
Plan concerné : `~/.claude/plans/iterative-swinging-quasar.md` → plan final à consigner dans
`prompts/plans/plan-06.md`.

## Instruction préalable — à exécuter AVANT l'implémentation

**`prompts/plans/plan-06.md` n'existe pas encore** (constaté à la rédaction de ce GO :
`prompts/plans/` ne contient que `plan-03-temp.md`, `plan-03.md`, `plan-04.md`, `plan-05.md`).
Enregistrer le plan dans `prompts/plans/plan-06.md` (règle C-plan-recording, AGENTS.md:86) en y
intégrant les réponses ci-dessous dans la section « Décision GO intégrée » (Tâche 0 du plan), en
remplaçant chaque marqueur (H) par (GO) ou par la décision révisée — comme `plan-05.md` l'a fait.
**Aucune ligne de code avant que `prompts/plans/plan-06.md` soit écrit.**

## Verdict

**GO.** Le plan est conforme au prompt 06 sur tous les points : classe de base `Representation`
(fit / transform_day / transform_panel / state_hash / odd_head / sidecar), `PCAOrthogonal` avec les
trois modes et les deux shrinkages, `DegreeZero` et `CenteredRanks` selon les formules du prompt,
CLI d'extraction et extractions de référence, tests (imparité ≤ 1e-12, invariance de degré 0,
perturbation de la fenêtre de surveillance, D attendus sans NaN), contrat versionné
`docs/sections/interface_Z.md`. Contraintes respectées : numpy seul, aucun import de
`jepadrift.monitors`/`jepadrift.injection` (test AST d'isolation), aucune statistique sur la fenêtre
de surveillance (fit sur calib ; tests ≤ 2019-12-31 ou tirages synthétiques). Revérifications
indépendantes menées à la revue : la règle MP sur la corrélation de calib redonne K = 5 (D2,
N/T = 0,1031, λ₊ = 1,7452) et K = 10 (`d3_239`, N/T = 0,2540, λ₊ = 2,2619) ; les coefficients
Ledoit–Wolf de calib redonnent δ̂ = 0,0192 et 0,0252 ; la décomposition triée/signée de Σ̂_LW est
**bit-identique** à `fit_background` sur les deux jeux (les deux `True`), donc la refactorisation
partagée (H9) est sans effet sur les résultats.

Le canal retenu est ce fichier (prompt destiné à l'instance), et non l'édition directe de
`~/.claude/plans/iterative-swinging-quasar.md` : le plan appartient au workflow
`superpowers:executing-plans` de l'instance, la règle C-plan-recording fait enregistrer le plan final
par l'instance dans `prompts/plans/`, et la trace de décision reste dans le dépôt (précédents
`GO-stream-03/04/05.md`, commités avec leurs streams).

## Réponses aux dix hypothèses — les dix défauts sont CONFIRMÉS

- **H1 (K au bord MP, σ² = 1 sur la corrélation) — CONFIRMÉ.** Le prompt fixe la formule
  λ₊ = σ²(1 + √(N/T))² « sur la corrélation » ; σ² = trace/N d'une corrélation vaut 1, donc le
  défaut du plan est exactement la spécification. K = 5 (D2) et K = 10 (`d3_239`), soit D = 6 et
  D = 11 (marché + résiduel), ce qui redonne les « 11 composantes » du prompt 18. La variante de
  Laloux (σ² = 1 − λ₁/N, K = 9 et 15) reste documentée comme écart `C-repr-mp-K`.
- **H2 (shrinkage = `ledoit_wolf` par défaut) — CONFIRMÉ.** C'est la propriété d'alignement
  décisive (point de vigilance 2) : en mode full, ½‖z(δ)‖² = ½δᵀΣ̂⁻¹δ, l'information exacte de
  l'injecteur (sonde 5, 1,7e-16 en relatif). Sans LW, l'alignement avec `fit_background` serait
  perdu. Écart `C-repr-whiten-lw`.
- **H3 (colonnes, pas de centrage) — CONFIRMÉ.** z = x @ W, W = V_sel Λ_sel^(−1/2) ; le centrage
  rendrait la transformation affine, donc non impaire (le test d'imparité l'attraperait). Colonne 0
  = canal marché `v₁ᵀx/√λ₁` dans les trois modes ; `channels = {"market": [0], "residual": …}`
  déclare la disposition, conforme à « PC1 is never discarded silently » (AGENTS.md). Écart
  `C-repr-layout`.
- **H4 (tail10) — CONFIRMÉ.** m = max{m : somme des m plus petites valeurs propres ≤ 0,10·tr Σ̂},
  sur les valeurs propres du Σ̂ utilisé (LW par défaut) ; m = 0 → ValueError. Conforme au prompt
  (« composantes des derniers 10 % de variance ») et à [Kuncheva & Faithfull, 2014]. Sonde 4 :
  m = 46 (D2), 123 (`d3_239`).
- **H5 (têtes paires) — CONFIRMÉ.** ACP et rangs : z_even = z_odd², D' = D — c'est le texte du
  prompt (« la tête paire contient les carrés des coordonnées blanchies »). DegreeZero :
  z_even = [‖Px‖], D' = 1, homogène de degré 1 — justifié par P3-CS (b) qui lit σ̂ comme moyenne
  exponentielle de ‖Px_{t−1}‖ ; en mode full, Σ z_k² = 1 et les carrés seraient dégénérés. Écart
  `C-repr-even-heads`.
- **H6 (DegreeZero) — CONFIRMÉ.** Conforme au prompt item 3 : z = UᵀPx/‖Px‖, P = I − bbᵀ (b
  unitaire : v₁ de Σ̂_LW ou 1/√N), U directions résiduelles figées de la même décomposition ;
  z_odd = 0 si ‖p‖ = 0 (issue explicite, point de vigilance 4) ; aucun canal marché (b retiré),
  déclaré dans `channels`/`normalization`. P3-CS observe les mêmes directions que P3-C : la
  comparaison isole la normalisation.
- **H7 (lignes extraites) — CONFIRMÉ, écart `C-repr-rows` consigné.** fit sur les lignes de calib
  repérées par `splits.yaml` ; transformation du premier jour de pretrain à la fin du panel ;
  valeur non finie → ValueError. Sur `d3_239`, la ligne 0 (NaN) et les années 2000–2004 sont
  antérieures au pretrain : exclues en démarrant au premier jour de pretrain. Sur D2, toutes les
  lignes sont transformées. Le « T × D » du prompt est la forme nominale.
- **H8 (extractions de référence) — CONFIRMÉ.** pca, mode factor, LW, sur `d2_us97` (D = 6) et
  `d3_239` (D = 11) — les commandes de vérification du prompt ; ~0,5 et ~1 Mo, bien sous les 50 Mo.
  La grille complète (~80 Mo) reste exclue du dépôt.
- **H9 (décomposition partagée `eigh_desc`) — CONFIRMÉE.** `stats/covariance.py::eigh_desc`,
  appelée par `injection.fit_background` ; opérations identiques, sorties bit-identiques
  (revérifié à la revue sur les deux jeux). Indispensable : le canal marché de P3-C doit être
  exactement la direction de F3 (b₁ = v₁√λ₁). Respecte la contrainte « aucun import de
  monitors/injection » (le prompt 06 la formule explicitement). La modification d'`injection.py`
  (fichier du stream 05) est couverte : `tests/test_injection.py` inchangé et au vert, test
  d'égalité au bit près (Tâche 1).
- **H10 (chargeur de C_t reporté) — CONFIRMÉ.** Aucune des trois représentations ne lit C ;
  `extract` passe `C=None`. Le GO-05 confie le chargeur partagé au premier consommateur réel
  (stream 17 IPCA ou 14) — conforme à YAGNI.

## Points de vigilance (Review Focus) — endossés

1. **Fuite d'apprentissage** : test bien construit — deux tirages synthétiques différents pour les
   lignes post-2019-12-31 laissent `state_hash`, `normalization` et les Z antérieurs inchangés ;
   modifier une ligne de calib change `state_hash` (le test n'est pas vide).
2. **Alignement avec l'injecteur** : revérifié à la revue — identité bit à bit de la décomposition
   (H9) ; les deux contrôles (F3 dans la colonne 0 ; ½‖z_full(δ)‖² = I_target) sont les bons.
3. **Bit à bit** : `transform_panel` = empilement de `transform_day` (la boucle s'impose, sonde 6 :
   le produit panel BLAS n'est pas bit-égal au produit par ligne) ; octets du `.npz`/`.json`
   déterministes (sonde 10, `np.savez` date 1980-01-01 ; re-vérifié par le test de déterminisme).
4. **Cas dégénérés à issue explicite** : liste complète et cohérente (zéros pour ‖Px‖ = 0 ;
   ValueError pour K ≤ 0, m = 0, valeur propre retenue ≤ 0, entrée non finie, colonne de variance
   nulle).
5. **Isolation** : test AST sur les imports de `jepadrift/representations/*.py` — nécessaire, le
   stream 08 ne couvrant que `monitors` et `jepa`.

## Risques — endossés

- **τ\* dans la calib ou avant** : bon cadrage — l'interface accepte toutes les lignes
  d'apprentissage ; le choix des lignes sans dérive (pretrain, ou lignes antérieures à τ\*)
  revient aux streams 07 et 12 ; signalé dans `interface_Z.md` et le wrapup.
- **Hashes dépendants de LAPACK/BLAS** : bonne politique — aucun hash d'état épinglé dans les
  tests, valeurs de référence dans le wrapup (cohérent avec la leçon BLAS des streams 04/05).
- **K sensible à σ²** : tranché par le prompt (σ² = 1 sur la corrélation) ; H1 confirmé.
- **tail10 = 123 dimensions** : conforme à la règle ; conséquence SPLL au stream 19.
- **Boucle jour par jour** : 0,04 s (ACP) / 0,15 s (rangs) par panel ; plafond `# ponytail:` avec
  vectorisation différée à une sous-classe.
- **Modification d'`injection.py` (H9)** : opération identique, revérifiée bit à bit ; parade
  correcte.
- **Hypothèse renversée au GO** : chaque hypothèse isolée (`mp_count`, `TAIL_SHARE`, `_day`,
  `segment_rows`) ; changement local.
