# PROMPT 22 — E5/J4 : JEPA contre degré zéro et IPCA, test de valeur incrémentale

**Statut : remplacement intégral proposé de** `prompts/streams/prompt-22-e5.md`. Agent Claude Code Opus 5.5 / Max après notification de quota et GO. Le travail de ce stream est impossible sans `configs/FROZEN.json` validé par le stream 21 ; il doit échouer **avant** d'ouvrir les données de test si le gel est absent ou incohérent. Lire `CLAUDE.md`, handover section 3.6 et les directives Codex, streams 14/16/17/19/21/23.

## Contexte

L'affirmation principale de l'Article C est désormais conditionnelle : un JEPA résiduel compact de dimension native `D` peut améliorer l'efficacité séquentielle, mais `P3-CS(b)` récupère déjà le canal N1 par normalisation instantanée sans apprentissage. Le but d'E5 n'est pas de battre P2-C ou P3-C naïfs, mais d'isoler la contribution **spécifiquement prédictive de JEPA** après neutralisation/normalisation et face à IPCA `P4`. Les résultats E6 de rotation exploratoire PC1–PC2 et E10 sous null asymétrique ne constituent pas une validation J4.

## Tâche

### 0. Pré-vol strict

- Relire le `FROZEN.json` du stream 21 et vérifier tous les hashes (code, données, splits, checkpoints, têtes, normalisations, seeds, seuils, nulls, dimension, famille et baseline). Toute divergence => `BLOCKED_FROZEN_MISMATCH`, aucun accès au test. Charger P5 et P4 en `eval` avec paramètres, EMA, coefficients, adaptateurs et statistiques figés ; `Representation.state_hash` inchangé avant/après chaque trajectoire.
- Conserver l'interface Z-1, `pipelines.run_pipeline` avec état `fit` sur lignes non injectées, `tau_star` et convention `delay=alarm_index-tau_star+1`. Enregistrer la fenêtre d'observation réelle et sa cohérence avec les datasets. Ne jamais modifier les découpages à partir des résultats.
- Vérifier que les variantes éligibles à la porte sont **exactement** celles enregistrées avant gel : principale `CA-T-JEPA` à bottleneck compact natif ; toute ablation post-ACP, tête orthogonale, MAE, temporal, adaptation online, dictionnaire de mélange ou modèle sans préentraînement est un diagnostic secondaire, sauf autorisation préspécifiée explicite dans `FROZEN.json`.

### 1. Grille confirmatoire et données

- Familles : F1 (prime factorielle), F2 (largeur caractéristique, uniquement panel avec C disponibles point-in-time), F4 (déformation/rotation de covariance) selon la définition source `jepadrift.injection` et les amplitudes fixées par `FROZEN.json`. Inclure les contrôles négatifs F4 (par exemple rotation PC2–PC3) et ne pas utiliser uniquement PC1–PC2 exploratoire comme preuve d'une capacité F4 générale. Ne pas substituer F3 à F4 si la puissance manque.
- Paires de fonds H0/H1 : D5 indépendant et D6 construit par **un signe de Rademacher par coupe journalière** ; onsets, seeds, amplitudes et composition d'actifs appariés entre P5, P4 et P3-CS(b). Les cellules brutes de données réelles ne sont pas une preuve de niveau exact ; les panels D2/D3/D4 sont biaisés par sélection/survie. Aucun ajustement sur `monitor` n'est autorisé.
- Grille historique de puissance `SR in {2,4,8}` pour les alternatives de localisation, avec convention (a) ou (b) explicitement inscrite par famille. F4 utilise ses paramètres de covariance `r`, `theta` et KL théorique, non un « Sharpe » artificiellement substitué au second ordre. Le mécanisme d'estimation de KL exact pour F4 est la divergence gaussienne de covariance si le fond est gaussien ; sous GARCH/heavy tails employer uniquement une mesure justifiée ou l'étiquette « information de design sous modèle ».
- Horizon de référence, alpha, garantie et N de replicates : **prendre exactement les valeurs gelées**. Un changement de `H`, de fenêtre d'injection ou de nombre de réplications après lecture des résultats doit être déclaré exploratoire. Référence unique de même classe de null pour tous les bras ; pas de course entre méthodes où un détecteur est calibré exactement et l'autre au niveau approximatif sans analyse des écarts.

### 2. Comparateurs et estimandes

- Primaires : **P5-C/P5-D** (modèle JEPA gelé), **P3-CS(b)** degré zéro, **P4-C/P4-D** IPCA. P3-C/P3-D et P2-C restent des points d'ancrage mécanistiques ; P7 est un oracle connaissant la direction (borne opérationnelle, jamais une baseline déployable). CD-DFM n'entre au primaire que si réellement disponible, licite, préspécifié et gelé avant J4 ; sinon diagnostic secondaire ou « non disponible » sans remplacement caché.
- La règle de sélection de la baseline `best(P3-CS(b),P4)` est celle du `FROZEN.json` : choix indépendant des résultats finaux ou, par défaut conservateur approuvé, victoire exigée contre **les deux** à la fois. Il est interdit de sélectionner ex post le contrôle le plus faible ou la dimension JEPA qui gagne le mieux.
- Estimande principale : `RMST_H(A)=E[min(T_A,H)]` avec `T` délai depuis l'onset, non-détections codées H, puis `G_H=RMST_H(best_control)/RMST_H(P5)`. **Ne jamais** calculer la moyenne des seuls délais détectés comme métrique principale. Compléter par taux de détection, fraction de censure, médiane seulement si >50% détectés, FPR(H) même fond/canal, IC sur différence FPR, et alignement `a_max` du dictionnaire par rapport à l'alternative injectée.
- Décomposer la valeur ajoutée : (i) retrait du marché et de dispersion de degré zéro, (ii) représentation linéaire pilotée par C, (iii) non-linéarité sans prédiction (témoin `untrained` de même capacité), (iv) apprentissage JEPA. Cette attribution se fait via ablations avec mêmes entrées disponibles et mêmes budgets de calibration ; ne jamais comparer P5 doté de C à une référence artificiellement privée de C et appeler le contraste « effet JEPA ».
- Rétention informationnelle `r_phi(D)=I_z(D)/I_x` : la calculer à partir de l'alternative et des distributions après projection **sur injections appariées**, sous une hypothèse de famille probabiliste clairement nommée. Pour une transformation non linéaire, ne pas traiter `0.5 Δm_z^T Σ_z^{-1} Δm_z` comme la KL exacte ; c'est une information de localisation de second ordre / proxy gaussien, au plus une borne sur l'information locale si les conditions de score sont satisfaites. Déclarer `NA` pour les cellules où une mesure crédible est impossible. DPI `r_phi<=1` pour les mesures de KL valides ; violation persistante => erreur d'estimation/modèle, non découverte de « création de KL ».

### 3. Calibration et validité

- Le signe d'une tête impaire est exactement Bernoulli(1/2) **univarié** sur un fond à symétrie centrale conditionnelle comme D6, avec pièce indépendante aux égalités. Ne supposer aucune indépendance entre sorties latentes contemporaines. Si combinaison multicanaux : utiliser une règle de combinaison sûre sous dépendance ou fournir une preuve/test du proxy sous-gaussien joint exigé par le mélange. L'indépendance marginale n'est pas une preuve.
- Chaque ligne de résultat porte `reading` (`exact`, `anytime-valid`, `bootstrap`, `randomization`), `H`, `gamma_H`, `alpha_target`, `alpha_attainable`, `fpr_measured`, `fpr_ci`, `fpr_comparable`, `null_assumption`, `threshold_hash`, `state_hash`. L'ARL0 est distinct de la FPR(H), et le « plafond Sharpe » une borne de budget d'évidence, pas une borne universelle sur ADD à ARL fini.
- Pour données brutes asymétriques : bras descriptif distinct avec recalibrage empirique `qhat` si applicable, sans mention « exact » ; si FPR n'est pas comparable, `gate_eligible=false`, même si `G_H` est élevé. Pour D6, le contrôle de niveau suit les lectures et les seuils préspécifiés de E3.

### 4. Détermination de J4, une seule fois

- Effectuer exactement les comparaisons primaires gelées et des IC définis avant lecture du test. Rapporter par famille `G_H`, intervalle, `FPR(H)` des deux méthodes, différence FPR avec incertitude, taux de détection/censure, effective N, paramètres, hash et étiquette `PASS/FAIL/INDETERMINATE` ; marquer non éligible toute cellule à null non valide ou FPR non comparable. Préserver le niveau exact de décision défini par le freeze (y compris éventuel contrôle des comparaisons multiples, jamais reconstruit après résultats).
- J4 **PASS** si, et seulement si, `G_H >= 1.25` avec IC admissible excluant 1 et FPR comparables dans **au moins deux familles distinctes** parmi F1, F2, F4, relativement au meilleur contrôle gelé. Le plan doit décider au préalable si `G_H >=1.25` s'applique au point estimé ou à la borne inférieure ; par défaut historique : point estimé >=1.25 **et** borne inférieure de l'IC >1.00. Ne jamais changer cette interprétation après les résultats.
- J4 **FAIL** si protocole exécutable, données suffisantes et seuil non atteint ; appliquer contingence C3/titre B. J4 **INDETERMINATE/BLOCKED** si dépendance critique absente, FPR non comparable ou impossibilité de calcul ; ne pas annoncer le titre A, mais ne pas convertir artificiellement un blocage logistique en échec scientifique.
- Si une seule famille passe, aucune interpolation ni combinaison de bras exploratoires ne crée une seconde. Les variantes `post_pca_legacy`, `MAE`, `TEMP`, `P5-ADAPT` et mélange ne changent pas le verdict principal.

### 5. TDD adversarial et reproductibilité

- Tests RED→GREEN : absence/modification du freeze => refus pré-test ; `state_hash` change après `monitor` => échec ; délai décalé d'un jour => échec ; onsets non appariés => échec ; meilleure baseline choisie après lecture du test => échec ; score de test utilisé pour sélectionner `D` => échec ; moyenne des détectés contre RMST => échec ; FPR 0.10 contre 0.05 déclaré « égal » => échec ; `qhat` déclaré exact sur données brutes => échec ; KL latente > KL source déclarée découverte => échec ; test de `D` fixé contourné par `--best-d` => échec.
- Une exécution `--quick` sur données **synthétiques non-test** doit reproduire exactement ses propres empreintes entre `jobs=1` et plusieurs workers. Les full runs sont explicitement enregistrés avec CPU, packages, seeds, SHA-256 des CSV et comptage des cas censurés. Graphiques exclusivement issus de CSV ; pas de chiffres recopiés manuellement.

## Entrées

`configs/FROZEN.json` et `MAPPING.md` du stream 21 ; checkpoints du stream 16 ; P4 du stream 17 ; E4/stream 19 ; E6/stream 23 phase 2 ; `jepadrift/pipelines.py`, `jepadrift/injection.py`, interface Z-1, tests de gel, manifests/splits, E2/J1, E3 et E10 ; prompt 22 historique et GO/plans. Si un chemin n'existe pas, diagnostique `BLOCKED` ou le crée comme livrable selon contrat ; ne jamais inventer des mesures.

## Livrables

`experiments/e5_jepa_comparison.py` (ou conserver nom déjà décidé), `configs/e5.yaml` qui référence/valide FROZEN, `tests/test_e5.py`, `results/e5/e5_cells.csv`, `results/e5/e5_gains.csv`, `results/e5/j4_verdict.json`, figures vectorielles/raster depuis CSV, rapport d'attribution, table `MAPPING.md` mise à jour, journaux de provenance, compte rendu de FPR/IC et wrapup. Les CSV incluent explicitement les NA / motifs et `gate_eligible`.

## Contraintes techniques

Ne pas changer J1 ou les versions de base ; `.venv/bin/python` et `make check` obligatoire. Aucun entraînement/fit/EMA update sur `monitor`. Pas de résultats issus d'un test sélectionné post hoc. `numpy.SeedSequence` pour appariements et reproductibilité, pool `spawn`, encodage des dates exact. Plafond mémoire du dépôt, pas de données D4 exportées. Toujours conserver un capteur marché explicite pour l'interprétation de F1 lorsque P5 residualise le marché.

## Critères de succès

Pipeline E5 et protocole pré-gelé correctement exécutés, même en cas de verdict défavorable, tests de gel/fuite positifs, FPR et censure visibles, attribution aux baselines correcte, décision J4 unique et traçable, `make check` et J1/CRLF inchangés. Aucun succès n'est déclaré avant vérification des hashes et du JSON de verdict.

## Commandes de vérification

```bash
cd "$(git rev-parse --show-toplevel)"  # dans le worktree de ce stream déjà ouvert par Codex
.venv/bin/python -m pytest -q -rs tests/test_e5.py tests/test_contracts.py tests/test_decoupling.py
.venv/bin/python experiments/e5_jepa_comparison.py --config configs/e5.yaml --quick --out results/e5_quick
.venv/bin/make check
.venv/bin/make j1
.venv/bin/python - <<'PY'
from pathlib import Path
import hashlib
b=Path('results/e2/e2_cells.csv').read_bytes()
assert hashlib.sha256(b).hexdigest()=='e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823'
assert b'\r\n' in b and b'\n' not in b.replace(b'\r\n',b'')
print('J1 preserved')
PY
```

Le nom des commandes `e5_jepa_comparison.py` / options peut être adapté dans le plan par Codex si une entrée CLI approuvée existe déjà, sans changement sémantique.
