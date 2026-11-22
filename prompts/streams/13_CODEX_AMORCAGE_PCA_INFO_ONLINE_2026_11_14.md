# AMORÇAGE CODEX — clôture rapide du stream 23, puis priorité absolue PCA-INFO-ONLINE

**Décision du chercheur — 14 novembre 2026.** Le prochain test scientifique prioritaire est la **sélection PCA informationnelle sans oracle**. Les expériences E4 sont conservées comme baselines/diagnostics ; elles ne testent pas notre cible. Cette instruction change l'ordre des priorités, **sans modifier rétroactivement les GO, données ou résultats scellés**.

## 1. Première action : finaliser le stream 23, sans élargir sa portée

Contrôle immédiatement l'état local réel de `main`, de l'instance, de la branche et du worktree du **stream 23 / E6 phase 1**. Ne présume pas la clôture à partir des comptes rendus historiques. Récupère et vérifie les conditions des GO applicables et de `docs/audits/stream_23_compatibility_2026_11_06.md`.

Finalise **au plus vite** le seul périmètre déjà autorisé : réconciliation avec `main`, reproduction bornée si son GO le permet, contrôle des résultats archivés, maintien de la qualification descriptive D6 et de la calibration indépendante D5, non-régression, `DEVIATIONS`, wrapup, revue, intégration et push contrôlés. Les résultats divergents imposent un STOP documenté, **pas** de retouche des paramètres pour reproduire une empreinte. Ne pas étendre à P4-D, P5-D, JEPA, J4 ni à de nouvelles explorations.

Dès que 23 est effectivement clos et publié, **ne lance pas 27, 21, 16 ou une nouvelle E4 par inertie**. La prochaine expérience devient le nouveau stream 32.

## 2. Mission suivante immédiate : stream 32 — PCA-INFO-ONLINE

Lis intégralement **`prompts/streams/prompt-32-pca-info-online.md`**, ainsi que les sources exactes qu'il cite, lorsqu'elles sont réellement accessibles. Les anciennes notes de clarification et le deck peuvent être des pièces externes au dépôt : ne présume pas leur présence sur GitHub ; la nouvelle spécification est autonome sur ses contrats essentiels. Priorité P0 : produire un pipeline **sans oracle**, où les contributions informationnelles `qhat_{k,t-1}` sont estimées avec le passé uniquement, puis les axes et `d*` sont recalculés avant la nouvelle observation.

Vérifie également la prise en charge du nouveau fichier par `prompts/streams/INDEX.md`, le master dérivé et `tools/check_prompts.py` ; resynchronise uniquement via le mécanisme canonique contrôlé.

Le plan devra implémenter et comparer :
- axes **triés par information** versus **préfixe PCA canonique** (sans recherche d'intervalles) ;
- coût fluide `M(d,γ_M)` versus coût affine `a+cd` ;
- versions **oracle** de sélection (borne) versus **online non-oracle** (cible) ;
- baselines variance seule, sous-ensemble ex ante figé et full-K ;
- **même famille de détecteur**, calibration nulle indépendante de la politique adaptative, RMST et FPR effectivement observés.

La comparaison décisive est `ONLINE_INFO_MIX` contre `ONLINE_PREFIX_MIX`, puis contre les baselines fortes, **à FPR atteints comparables**. L'oracle seul ne prouve rien sur la méthode utilisable. Le glouton et le tri top-q sont **le même optimum** sous information additive ; pas de doublon expérimental.

Cette mission est **strictement synthétique** avant toute confrontation à des données financières réelles. Base PCA initialement figée ; pas de JEPA, pas de 2020+, pas de J4, pas de covariance main claim, pas de modification du benchmark PCA `/2` ni des résultats E4.

## 3. Orchestration et autorisations

Tu restes **superviseur architectural et intégrateur Git**, pas auteur direct du code applicatif. Respecte `prompts/Protocole Codex.md` et les GO d'orchestration encore applicables. Lance un Claude Code Opus / effort Max dans un worktree neuf, par plan natif en lecture seule, puis revue contradictoire **sur les points mathématiques et les fuites temporelles**. Inscris un plan canonique et un **GO technique écrit** avant implémentation TDD.

N'attends pas une nouvelle discussion générale sur l'intérêt de PCA : le choix de priorité scientifique est acté par cette instruction. Les détails nouveaux du protocole (fenêtre online, estimateur, modèle synthétique, `s2`, grilles, règle statistique et ressources) sont des **propositions pré-enregistrables**, non des résultats acquis ; fais-les expliciter et geler avant lecture des performances alternatives.

**Le GO d'implémentation n'est pas un GO illimité de calcul scientifique.** Après tests et revue, sollicite/enregistre un GO distinct pour le pilote synthétique borné. Ne lance le full qu'avec un GO confirmatoire supplémentaire, une prévision CPU/RAM/disque fondée sur ce pilote et une grille verrouillée. Aucun travail réel/J4 implicite.

## 4. Ressources : accélérer réellement

Le chercheur autorise pour **cette nouvelle campagne** le principe du multi-processus CPU sur serveur partagé AMD EPYC 8224P (24 cœurs physiques, 48 threads SMT, 192 Go RAM), **pas** l'hypothèse d'un gain linéaire 40×. Conserver BLAS/OMP/MKL à un thread **par worker**, paralléliser les répliques avec graines indépendantes des workers et écriture/fusion déterministes. **Pilote proposé : 8 workers** ; mesurer `jobs=1/4/8/12` puis envisager 16 selon charge, RAM et autorisations. Codex doit fixer un nouveau plafond de ressources pour ce stream, sans importer aveuglément celui d'E4, et respecter les verrous partagés.

## 5. Premier retour attendu de Codex

Un état compact et vérifiable contenant :
1. **Stream 23 :** statut réel, commit(s), tests, résultats/limites, blocage éventuel.
2. **Stream 32 :** worktree, plan revu, contrats mathématiques et temporels, choix de l'estimateur, familles synthétiques, schéma FPR/RMST, calendrier de GO.
3. **Ressources :** plafond proposé, coût smoke mesuré si exécution autorisée, politique de multi-worker.
4. **Portes fermées :** travaux et données interdits, aucun résultat présenté avant son exécution.

**Instruction d'arrêt :** si 23 présente une divergence scientifique ou une condition de GO non remplie, formalise le STOP et préserve les artefacts ; ne déclare pas une clôture fictive. La préparation documentaire du stream 32 reste possible, mais aucun lancement scientifique ne contourne un verrou ou une autorisation.
