# Stream 28 — revue Codex du plan v1 : NO-GO

Date : 2026-10-30. Supervision déléguée par le mandat du chercheur ; aucun GO d'implémentation.

Plan audité : 690 lignes, SHA-256 `6e1a6e5a9aa5d9d93702a981df3f0f0f0fd4b649982bab636603a8f53f7b7c5d`, archive locale `logs/pca_drift_orchestration/PLAN-v1.md`. Aucun plan aval amorcé. Le hash initialement transcrit ici était incomplet (62 caractères) ; correction d'après le fichier archivé, sans modification de celui-ci.

## Corrections bloquantes

1. **Terminaison (§3.2).** La boucle nextafter depuis un quantile interpolé est exclue. Reproduction .venv : maxima [0.,1.,2.,3.,4.], alpha=0.05, quantile=3.8, fraction GE=0.2 ; environ 450359962737050 pas ULP pour atteindre 4. Choisir un rang directement : n maxima finis non vides, r=floor(alpha*n), b=sort(maxima)[n-r-1], seuil GT=b, seuil GE=nextafter(b,+inf). Vérifier une seule fois le compte <=r ; refuser les seuils non finis. Tester n=1, n=5, alpha non multiple de 1/n, maxima égaux, GE/GT et entrées invalides. Un arrondi de rang conservateur est documenté, jamais une boucle ULP.

2. **Centrage covariance (§3.3).** Figer le centrage vech avec les seules données de fit, ou un rôle de nuisance indépendant hashé. Ne pas employer les trajectoires qui fournissent les maxima de calibration. Même noyau/paramètres/centrage pour calibration, holdout, alternatives. Tester qu'empoisonner les autres rôles ne modifie pas ce centrage. Rapporter le biais résiduel de population et conserver la calibration empirique. Nommer explicitement le scan de vech quadratique : ce n'est pas un CUSUM à récursion additive.

3. **Ingestion pré-J4 (§6.1, D18).** Mmap limité au pré-2020 obligatoire. Ne pas appeler load_d3_239() qui matérialise tout le panel. Adaptateur local : ret_wide.npy en mmap_mode='r', calendrier, puis matérialisation de la seule tranche autorisée ; filtre Parquet avant matérialisation également admissible. Hash du fichier pour provenance permis. Tester les plages réellement indexées. Aucun retour post-2019 lu pour fit/design/évaluation, aucune dérogation Covid, aucun FROZEN.json fabriqué.

4. **Scénario A (§4.4, D5).** Le blanchiment LW estimé n'a pas variance 1 sous la population. Fixer Delta_A=(4/sqrt(252))*sqrt(v1.T@Sigma0@v1)*v1 : SR projeté réellement standardisé=4, KL marginale gaussienne=16/504. Rapporter séparément I plug-in LW et KL jointe complète, non contraintes à cette valeur. F3 avec normalisation locale permis, sans changer injection.py. Tests analytiques avant run, aucune adaptation après résultat.

5. **LLR (§4.4).** C0=V.T@Sigma0@V est non blanchi, tandis que z est ailleurs blanchi. Employer un espace cohérent pour données/moyenne/covariance dans les deux LLR. Tester l'équivalence avant/après blanchiment.

## Schéma, bornes et protocole

6. GAUSS_PROXY_CHECK est utilisé mais absent des metric_kind : fermer les énumérations et identifier explicitement le proxy t7. Les fingerprints distinguent graine résolue, entrées, code scientifique, environnement, S, détecteur/paramètres/centrage, calibration, scénario, horizon et cohorte. Séparer provenance Git et identité scientifique, expliquer le comportement après commit. Métriques bloquées NA, jamais zéros empiriques.

7. Valider/refuser dimensions nulles, données vides/non finies, n_cal/n_null/n_alt nuls, alpha hors (0,1), mémoire/durée. Si nmax=1 est admis, coût affine défini : corde de M entre 1 et 20, indépendante du réservoir/nmax réduit des tests. Éviter les tests probabilistes fragiles quand une identité suffit.

8. DEVIATIONS.md en **français** ; code/tests/schéma/wrapup en anglais ; plans/revues en français. Plan canonique commitable avec chemins relatifs/variable racine, aucun chemin personnel de serveur. Retirer le plafond arbitraire de deux sessions successives : la limite utilisateur porte sur les streams simultanés.

9. Base avancée proprement à e1f80847245b14498e331abda1e3d13cf415ec8f après extinction du processus v1, contrôles des verrous et de E2. Seul le protocole Remote Control a changé ; code scientifique inchangé depuis le contrôle initial (401 passed, 5 skipped). Prochains lancements : --remote-control avec nom de worktree, --model opus, --effort max. Aucun retrait silencieux du flag si le CLI refuse sa combinaison avec -p.

## Arbitrages acceptés pour révision, sans GO

- D1 : nouveau titre PROMPT 28-PCA après GO, seule ligne 1 ; préserver E11. Futur Stream 31 : identifiants {28-PCA,29,30,31}.
- D2–D3 : répertoires results/pca_drift_benchmark/{smoke,full}/, trials CSV normalisé ; CSV >50 Mo local non suivi avec hash, sans compression/force-add implicite.
- D4 : q plug-in LW additif comme objectif déclaré ; KL jointe de population séparée, sans équivalence des optima.
- D6 : coefficients égaux axes 10..20, contrainte C=3 sous Sigma0 ; injection en rendements avant projection.
- D7 : s2(p)=2*ln(H/alpha)/(H*p) ex ante ; M(d,504) seulement substitut fluide à prior apparié.
- D8–D11 : scan vech à centrage indépendant, énergie EW séparée ; recherche covariance jointe exhaustive <=20 ; affine principal, M en HEURISTIC_COST ; corde entre 1 et 20.
- D12 : nul réel D6 pré-2020 avec limites recouvrement/ajustement ; aucun FPR holdout indépendant fictif.
- D13 : stress [2008-09-15,2008-11-20] et [2011-07-25,2011-10-03], poids égaux, lignes complètes ; aucun remplissage depuis 2020/2022.
- D14–D15 : 2022 aligné sur onset, diagnostic ; Covid R1–R5 conservant chaque alarme pré-onset, reset explicite, lectures aiguë/H250 séparées.
- D17 : smoke N=239,H=250,n_cal=n_null=n_alt=40, deux fonds A/B30/C, deux répertoires neufs, aucun full, un processus/BLAS un thread, mémoire <=8 Gio. BLOCKED_RESOURCE si budget dépassé ; aucun remplacement du scan.
- D19–D20 : sweep 15°/45° différé jusqu'à audit budget full ; contrôles de formule descriptifs et coordonnées cohérentes.

## Suite

Phase A seulement, même worktree, lecture seule, sans sous-agent. Produire un PLAN.md révisé autonome et concis (300–400 lignes), sans contradictions, avant nouvel audit Codex. Aucun smoke, code applicatif, résultat, commit, push ou faux GO.
