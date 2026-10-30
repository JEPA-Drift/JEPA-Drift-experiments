# Stream 28 — GO Codex après audit unitaire du plan v2

**Politique courante prioritaire :** `prompts/POLICY-PCA-PLAN-ONLY.md`. Les autorisations ci-dessous décrivent le travail déjà réalisé ; elles n'autorisent plus de nouvelle implémentation Claude. Le 28 doit être finalisé avant tout plan aval. Ses corrections encore nécessaires sont décrites dans `prompts/plans/plan-28-closeout.md`, approuvé comme plan uniquement par `prompts/GO-stream-28-closeout-plan.md` ; leur exécution reste à autoriser.

Date : 2026-10-30. Décision prise par Codex dans le périmètre de supervision et d'arbitrage explicitement délégué par le chercheur. Ce document ne constitue ni une approbation de résultats non produits ni une signature personnelle du chercheur.

## Décision

**GO pour l'implémentation TDD du runner et ses tests, la documentation du schéma et deux exécutions smoke synthétiques.** Aucun GO pour un run full, une évaluation réelle post-2019, un commit, un push, une fusion sur main ou un autre stream.

**Avenant chercheur prioritaire :** `prompts/GO-stream-28-amendment-P0-P1.md`. Autorisation ciblée de corriger P0 puis P1 dans le travail existant, de mettre à jour schéma/tests/documentation et de réaliser un nouveau double smoke ; relance unique à 18:52 UTC. La règle empirique floor(alpha*n) n'est plus autorisée.

Source auditée : PLAN.md v2, 365 lignes, SHA-256 `e3633497fb791bf3be336315a7ae553a0d392179d5bfa12b82126338ea2a9e3b`. Base `e1f80847245b14498e331abda1e3d13cf415ec8f`. Le plan canonique est enregistré avant code dans `prompts/plans/plan-28.md`, avec la présente décision intégrée.

## Clôture des objections du NO-GO

1. Seuil choisi par statistique d'ordre et au plus un nextafter, sans boucle ULP ; validation des petits n, égalités, alpha et maxima non finis.
2. Centrage covariance appris sur le rôle indépendant centering, hashé et figé avant les trajectoires de calibration ; aucun ajustement sur holdout/alternatives.
3. mmap en lecture seule et matérialisation limitée au pré-2020 ; tests des indices effectivement lus ; les cohortes historiques restent bloquées avant J4.
4. Scénario A normalisé par v1.T@Sigma0@v1 pour un SR projeté réel de 4 ; information marginale 16/504 séparée des informations plug-in et jointes.
5. Moyennes, covariances et LLR exprimés dans le même espace z, avec tests d'invariance au blanchiment.
6. Proxy t7, identités scientifiques, bornes, langues et référence Git sont explicités dans v2. Le hash v1 tronqué dans la première revue a été corrigé d'après l'archive (64 caractères) ; aucun octet de l'archive n'a changé.

## Décisions GO intégrées et précisions normatives

- Les arbitrages D1–D20 de v2 sont retenus avec les restrictions de cette décision. Le scan mélange évalue tous les tau ; ni GLR, ni troncature, ni substitution pour gagner du temps. La covariance jointe n'est jamais une somme marginale ; M n'est jamais un coût exact de délai.
- La normalisation des coefficients est : beta=V.T@Delta, mu=beta/sqrt(lambda), q_plugin=mu**2/2. L'égalité de contrôle de §6.2 porte sur beta, **pas sur q_plugin**. Employer les noms de coordonnées cohérents dans le code et les tests.
- Les colonnes communes de §4.4 s'appliquent aux tables détaillées. Pour trials.csv, le schéma normalisé comprend exactement group_id, role, replicate, first_hit, censored_time, detected, stat_max, pre_onset_alarm et detected_during_event. Les colonnes communes et identités sont retrouvées par les jointures documentées vers calibration/aggregates ; ne pas dupliquer des dizaines de chaînes sur chaque tirage. issue_id est la clé explicite d'issues.csv. Ces précisions doivent figurer dans le schéma avant exécution, sans ambiguïté de jointure.
- Defaults full : N=239, H=250, T_fit=1000, nmax=20, n_center=n_cal=n_null=n_alt=2000. Smoke : seuls ces quatre effectifs deviennent 40. A/B30/C et deux fonds ; seed déterministe pré-déclarée. Aucun tirage réel ou propriétaire dans le smoke, aucune donnée illustrative étiquetée réelle.
- Budget smoke : un processus, threads BLAS/OMP=1, plafond mémoire 8 Gio, limite murale de 30 minutes par invocation du runner, vérifiée aux frontières de partition. Un dépassement produit un état honnête BLOCKED_RESOURCE et un arrêt ; aucun changement de statistique ni de cible scientifique. Les tests utilisent des tailles minuscules et restent hors Monte Carlo de production. Transmettre le coût mesuré et l'extrapolation full, sans le lancer.
- Le .venv partagé et les versions épinglées restent inchangés ; aucune installation. Variables fixées avant NumPy : OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42, MPLBACKEND=Agg. Toutes les commandes Python/tests/Make utilisent ce .venv.
- Schéma à publier : pca_drift_benchmark/2, sept fichiers sous results/pca_drift_benchmark/smoke_predictive_v2/, CSV FAIR, empreintes et règles de référence explicites. Les préfixes E1/E2 et MIX E3/E2 k20 réutilisent les mêmes métriques, sans recalcul. Le schéma n'est scellé pour les consommateurs qu'après audit du code, du smoke et intégration propre sur main.
- Autorisation limitée au titre du nouveau prompt 28-PCA ; ancien E11 intact. Ne pas toucher aux prompts, plans ou fichiers possédés par 29/30/31, ni à tools/check_prompts.py. Le futur Stream 31 traitera la découverte de {28-PCA,29,30,31}.
- DEVIATIONS en français et ajouts uniquement ; préserver l'échec E3/D8. Code, tests, schéma et wrapup en anglais. Aucun chemin personnel dans les fichiers destinés au commit ; pas d'identité supplémentaire ni de commentaire promotionnel.
- E2 conserve sur disque et dans l'index ses CRLF et son SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` ; aucune écriture dans results/e2/. Aucun fichier EUROFIDAI suivi, aucun fichier >50 Mo proposé au suivi.
- Le processus Claude réalise les contrôles ciblés, le double smoke et son rapport. Codex conserve les contrôles d'intégration make check, la réindexation, les opérations Git et l'autorisation du full ; tous les processus du stream devront être éteints à cette clôture.

## Livrables et arrêt demandé

Runner, tests unitaires propres, configuration, document de schéma, sept artefacts smoke et hashes, plan/GO/trace NO-GO, déviations justifiées et wrapup anglais aux six sections du projet. Avant de s'arrêter, rapporter les commandes réellement exécutées, résultats, limites, SHA-256 et coût CPU/RSS, avec honnêteté sur les cas non exécutés.

Aucun autre stream n'est amorcé avant le gel du schéma, le smoke audité et l'intégration de 28 sur main. Les audits ultérieurs restent unitaires ; la Phase 2 aura au plus deux streams actifs et les intégrations Git resteront sérialisées.
