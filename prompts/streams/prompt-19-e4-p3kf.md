## PROMPT 19 — E4 : lois d'échelle en N et antériorité PCA « queue » (P3-KF, SPLL)

### Contexte
La signature falsifiable de JEPA-Drift est la loi d'échelle du gain en fonction de la taille N de la coupe (Corollaire 2) :
- N⁰ pour le pooling face à une dérive de marché ;
- N^{1/2} pour une dérive de largeur surveillée dans tout le résiduel par un mélange isotrope ;
- N¹ pour une largeur portée par quelques directions de caractéristiques.

Sur données réelles, le mélange isotrope n'est pas exactement valide (porte d'indépendance, `C-P3C-mixture-gate`). Le détecteur par défaut est donc le dictionnaire, dont la loi d'échelle dépend aussi de l'alignement. E4 mesure les pentes, les attribue, et reproduit l'antériorité de Kuncheva sur les composantes de faible variance. Lire `CLAUDE.md`.

### Tâche
Écrire `experiments/e4_scaling.py`. Avant J4, seules les lignes antérieures à 2020 sont lues, avec un contrôle bloquant.
1. **Jeux.**
   - `d2_us97`, `d3_239`, `d3_500` [A] ; D4 [B], s'il est construit (`C-D4-survivor`) ; tous symétrisés (D6).
   - Pour `d3_500` et D4 : sous-panel complet sur chaque fenêtre (titres `in_universe` tous les jours de la fenêtre), tiré avec graine.
2. **Grille.** N ∈ {8, 16, 32, 64, 128, 239, 500}, borné par la taille du sous-panel. Par N : 20 sous-ensembles emboîtés, tirés avec graine et communs à tous les pipelines.
3. **Familles**, en convention (b). Les grilles d'amplitude suivent la règle du prompt 12 (délai médian dans [20 ; 0,8·H]) et sont consignées.
   - F1 : primes fixes sur K facteurs.
   - F2 : κ, sur D3 et D4 seulement ; D4 n'a que 4 caractéristiques continues.
   - F3 : SR RMS par titre fixé.
4. **Pipelines.**
   - P2-C, P3-C (factoriel et complet), P3-KF, P3-CS (b), P4-C (IPCA ; CD-DFM si disponible).
   - Lecture anytime-valid à γ_H = H/α, avec H = 2 000 ; canaux exacts en diagnostic.
5. **P3-KF**, dans `jepadrift/monitors/spll.py` : détecteur semi-paramétrique de log-vraisemblance de Kuncheva (2013, IEEE TKDE ; vérifier la référence).
   - Entrées : composantes « tail10 » (m = 46 sur D2, 123 sur `d3_239`).
   - k-moyennes sur la fenêtre de référence, statistique sur fenêtre glissante.
   - Seuil calibré sur des fenêtres nulles D6, pour FPR(H) = α.
6. **Mesures.**
   - Pente de log G_ADD en log N (opposée de la pente de log ADD médian, comme au prompt 12), avec IC bootstrap sur les sous-ensembles.
   - Exposants prévus par le Corollaire 2 (0, 1/2, 1). Pour le dictionnaire, prévision corrigée par l'alignement mesuré a_max(N) (`floors.dictionary_multiplier`).
   - Audit réduit par sous-ensemble, sur les sous-espaces marché, factoriel et résiduel : `stats.drift.debiased_sr2` et `mbb_indices` (stream 8b).

### Entrées
Streams 5, 7, 8b, 11 et 17 (et 18) ; `CLAUDE.md`.

### Livrables
`experiments/e4_scaling.py`, `jepadrift/monitors/spll.py`, `configs/e4.yaml`, `results/e4/{e4_cells.csv,e4_slopes.csv,e4_audit_subsets.csv}`, `figures/e4/*`, `logs/e4/`.

### Contraintes techniques
- `jepadrift/monitors/spll.py` en numpy seul ; k-moyennes implémentées dans le module, graines passées en argument.
- Mêmes graines de sous-ensembles et d'onsets pour tous les pipelines.
- Résultats indépendants de `--jobs` ; option `--quick`.

### Critères de succès
- Pentes et IC pour chaque (jeu, famille, pipeline).
- P3-KF dans la région à 99 % de α sur fonds nuls.
- Chaque pente faible attribuée, à l'information ou à l'alignement.

### Commandes de vérification
```bash
python experiments/e4_scaling.py --quick --out results/e4_quick
python experiments/e4_scaling.py --out results/e4 && head results/e4/e4_slopes.csv
```