## PROMPT 12 — E1 : le problème sur données réelles (§2), pipelines 1 → 2 → 3 et critères de J2

### Contexte
E1 mesure ce que coûte la détection d'une dérive pour un actif seul (P1), pour le pooling de signes (P2) et pour la projection orthogonale au marché (P3), puis compare ces gains aux prévisions de l'audit. Il fournit les chiffres du §2 et deux des trois critères de J2 (25 octobre). Lire `CLAUDE.md`.

Définitions :
- **ADD** : délai moyen de détection, pire cas de Lorden.
- **ARL₀** : durée moyenne avant fausse alarme.
- **Lecture anytime-valid** : e-détecteur arrêté à γ.
- **Lecture exacte** : CUSUM de signe calibré sur le treillis à ARL₀ = γ.
- **G_ADD = ADD_A/ADD_B**, à lecture et γ égaux.

### Tâche
Écrire `experiments/e1_problem.py` avec une option `--include-test-window`, refusée tant que la configuration n'est pas gelée (prompt 21). Fenêtres par défaut : 2005–2019.
1. **Bras injecté, sur fonds D6 (SYM-D2, SYM-`d3_239`).**
   - Familles F3, F1, F2 ; convention (a), SR ∈ {1, 2, 4}.
   - 1000 onsets par cellule ; H_det = 2000 jours.
   - Pipelines :
     - P1-C et P1-D sur chaque actif, en rapportant la médiane et le meilleur actif ;
     - P2-C, avec K ∈ {1, 5, 10, 20, 30, 40, 50, 60, 75, 97}, et jusqu'à 239 sur D3 ;
     - P3-C (marché plus résiduel factoriel, et résiduel complet pour F2) ;
     - P3-D ;
     - P7.
   - γ ∈ {20, 252}.
   - Lectures : anytime-valid pour tous ; exacte pour les CUSUM de signe ; Article B (λ = 10, bootstrap R15) pour P1-C et P2-C.
2. **Bras d'échelle, pour J2.** Convention (b), amplitude par titre fixée ; N ∈ {8, 16, 32, 64, 97} sur D2 et jusqu'à 239 sur D3 ; 20 sous-ensembles emboîtés par N. Mesurer les pentes de log G_ADD en log N :
   - P2-C sur F3 ;
   - P3-C sur F2.
3. **Bras réel.** Phases des trois datations comprises dans 2005–2019 :
   - part des phases dans le budget (L·Î ≥ ln γ) par pipeline ;
   - délais observés dans les phases.
4. **Mesures.**
   - ADD moyen et médian, taux de détection dans H_det, taux de censure ;
   - G_ADD_av, G_ADD_ex, G_floor (rapport des I de l'oracle) ;
   - G_SR : plus petit SR détecté dans 250 jours avec probabilité au moins 1/2, par bissection ;
   - K_eff ;
   - comparaison mesuré/prévu avec `results/audit/predicted_gains.csv`.
5. **Résumé J2** dans `results/e1/e1_j2_summary.txt` :
   - (i) FPR des flux de signe sur fonds D6 à ±1 point du niveau exact du treillis à l'horizon retenu (niveau calculé par `lattice.py`) ;
   - (ii) pente de P2-C sur F3 proche de 0 au-delà de N ≈ 20 (IC bootstrap à 95 % contenant 0, ou borne haute < 0.15) ;
   - (iii) pente de P3-C sur F2 positive, IC à 95 % excluant 0 ;
   - (iv) tableau des gains 1 → 2 → 3, mesurés et prévus.

### Entrées
Prompts 2 à 8 et 11 ; `CLAUDE.md`.

### Livrables
`experiments/e1_problem.py`, `configs/e1.yaml`, `results/e1/{e1_cells.csv,e1_slopes.csv,e1_real_phases.csv,e1_j2_summary.txt}`, `figures/e1/*`, `logs/e1/`.

### Contraintes techniques
- Graines par (cellule, réplication).
- Parallélisme par cellule sans effet sur les résultats.
- Option `--quick` (100 onsets, deux SR) pour un test de fumée en moins de 10 minutes.

### Critères de succès
Exécution complète déterministe ; résumé J2 rempli avec les IC ; chaque nombre du §2 présent dans un CSV.

### Commandes de vérification
```bash
python experiments/e1_problem.py --quick --out results/e1_quick
python experiments/e1_problem.py --out results/e1 && cat results/e1/e1_j2_summary.txt
```
