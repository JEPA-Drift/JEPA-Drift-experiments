# GO — Stream 13 : E3, calibration sous H₀

Dates : 2026-10-23 (révision 3, GO remplacé) ; 2026-10-28 (révision 4, GO en vigueur).
Destinataire : instance Claude Code du worktree `stream-13` (base `c284823`).
Forme : transcription verbatim, par l'instance, des messages de l'orchestrateur et du GO. Le GO en vigueur est celui
du 2026-10-28 sur la révision 4 (`prompts/plans/plan-13.md`, section « Décision GO intégrée (2026-10-28, révision
4) »). Le GO du 2026-10-23 sur la révision 3 est conservé ci-dessous comme historique remplacé. L'amorçage est
`prompts/amorcage-13.md`. Un premier plan de la session du
2026-10-22 (base `c8fe24d`) est resté hors dépôt, dans `~/.claude/plans/amor-age-stream-merry-starlight.md`.
Les messages de l'orchestrateur ci-dessous sont reproduits verbatim. Seule modification : un chemin absolu y est
abrégé en `~`, signalé entre crochets, car aucun fichier commité ne porte de chemin absolu de la machine.

## Amorçage (verbatim)

> # Amorçage — stream 13, E3
>
> Vérifie d'abord que le stream 8b est fusionné sur `main`. Lis `CLAUDE.md`,
> `prompts/streams/INDEX.md` et `prompts/streams/prompt-13-e3.md` dans le worktree `stream-13`.
> Reste en mode `plan`. Sépare les garanties sous D6 des diagnostics sur placebos bruts ; détaille
> la calibration, les niveaux atteints, les IC et la censure d'ARL₀. Présente le coût et le
> fractionnement des 20 000 trajectoires, les fichiers touchés et les questions.
> Vérifie Γ^spec pondéré de Bartlett, la génération gaussienne distincte de t₇, le flux P1-D de
> l'Article B et le statut descriptif des fenêtres brutes chevauchantes. Diffère `mixture_s2`
> jusqu'à l'intégration de la porte Holm du stream 12.
> Révise le plan : borne réelle stricte au 2005-01-04, mêmes cinq titres
> `composition_for(5, N)` que dans E1 et test de remise à zéro par fenêtre pour les lectures
> locales P1-C, P1-D, dépassement et encodeurs. Les défauts Q1/Q3/Q4/Q5 sont retenus :
> la porte ±5 % à 2 000 trajectoires reste primaire, avec échec rapporté sans nouveaux tirages.
> Attends le GO de l'orchestrateur. Après ce GO seulement, enregistre `prompts/plans/plan-13.md` avec
> « Décision GO intégrée » et implémente.
> Utilise `.venv`, rédige les nouveaux audits en anglais et arrête-toi au commit local vérifié avant fetch, fusion ou push.

## Révision demandée après la reconnexion MCP (verbatim)

L'orchestrateur a d'abord exécuté `/mcp reconnect all` (2 serveurs reconnectés sur 3).

> Stream 13 : reprends en mode plan. Lis [~]/JEPA-Drift-experiments/prompts/amorcage-13.md. Révise le plan : date
> réelle strictement >= 2005-01-04, mêmes cinq titres composition_for(5,N), tests de reset P1-C/P1-D et
> overshoot/encodeurs, pas de drift/onset dans le préfixe. D6 : fenêtres chevauchantes descriptives et trajectoire ARL
> circulaire continue à la couture. Test primaire 2000 répétitions ±5 %, sans reruns opportunistes. Présente le plan
> révisé ; aucun GO implementation avant audit. MCP reconnectés ; Opus 5.5 Max, .venv.

Après un nouveau `/mcp reconnect all` (2 serveurs sur 3) :

> Reprends le plan 13 interrompu par le redémarrage sans refaire les sondes. Intègre les corrections déjà transmises
> sur date, cinq titres, reset CUSUM et fenêtrage D6. Écris le plan révisé puis présente-le pour audit ; reste en mode
> plan.

## NO-GO statistique provisoire sur la révision 2 (verbatim)

> NO-GO statistique provisoire pour le plan 13. (1) Lignes 215-221 : la borne supérieure d'E[min(T,60γ)] < γ ne
> prouve pas E[T] < γ si des trajectoires sont censurées. Avec censure, classe l'ARL₀ « indéterminée » ; tu peux
> rapporter séparément un déficit de moyenne restreinte. Un FAIL d'ARL exige une borne valide sur la queue. (2) Lignes
> 448-450 : les 58 cellules partagent trajectoires/tirages ; leur nombre de sorties de région n'est pas binomial. Garde
> ce compte descriptif ou utilise une analyse qui respecte la dépendance, sans p-valeur binomiale naïve. Conserve les
> autres arbitrages, révise le plan et repropose la sortie du mode plan.

## GO sur la révision 3 (verbatim) — historique, remplacé par le GO du 2026-10-28

L'orchestrateur a exécuté `/mcp reconnect all` (0 serveur reconnecté sur 1, graphify et jcodemunch étant déjà
connectés) avant ce message.

> GO final pour la révision du plan 13. Je viens d'exécuter /mcp reconnect all et de vérifier graphify et jcodemunch
> connectés. Lance ExitPlanMode puis implémente en mode auto. Maintiens la porte primaire 2000 répétitions/±5 %, les
> resets CUSUM, la date stricte et la qualification indéterminée des ARL censurées, sans relance opportuniste.

## Application par l'instance (révision 3, historique)

- La révision 3 est approuvée sans amendement.
- Les questions ouvertes prennent leur défaut :
  - Q-A : `wilson` est déplacé d'E10 vers `jepadrift/stats/intervals.py` ;
  - H4 à H13 ;
  - H14 : le contrôle au temps d'arrêt borné est inclus.
- Avant la première écriture, l'instance a vérifié par appels que graphify (`graph_stats`) et jcodemunch
  (`resolve_repo`) répondent.

## Reprise du 2026-10-28 : demande de delta de plan (verbatim)

> Tu reprends uniquement le stream 13 E3 déjà ouvert, en mode plan sans aucune écriture ni run expérimental. Préserve
> les fichiers non commités. Lis CLAUDE.md, prompts/streams/prompt-13-e3.md, prompts/amorcage-13.md,
> prompts/plans/plan-13.md, prompts/GO-stream-13.md, le code E3 existant, et
> [~]/JEPA-Drift-experiments/prompts/wrapups/handover-01-27.md sections 2.7-2.8/3.6. Le plan 12 révision 2 a GO avec
> cinq titres composition_for(5,N): D2 [24,71,56,46,75], D3 [60,177,141,116,184]. Vérifie la borne stricte
> 2005-01-04, les mêmes indices littéraux en tests, la remise à zéro P1-C/P1-D/dépassement/encodeurs à chaque fenêtre,
> la séparation FPR(H)/ARL0/Γ, les 20000 trajectoires, les IC avec deff et la portée descriptive des placebos bruts.
> Fournis un delta de plan concis, un audit des fichiers partiels et seules questions bloquantes. Ne traite pas le GO
> antérieur comme GO de cette révision; attends mon arbitrage.

## GO final sur la révision 4 (verbatim, en vigueur)

> GO FINAL STREAM 13 pour le plan révision 4 du 2026-10-28
> (~/.claude/plans/tu-reprends-uniquement-le-imperative-truffle.md), avec corrections obligatoires. Préserve les cinq
> fichiers non commités, conserve le GO antérieur comme historique remplacé, ajoute le présent arbitrage verbatim à
> prompts/GO-stream-13.md et enregistre prompts/plans/plan-13.md révision4 avec Décision GO intégrée avant code. Q-J2:
> le verdict primaire J2(i) est E1/stream12 à 2000 répliques; e3_j2_check.txt à 20000 est contrôle secondaire de
> calibration sans verdict J2 distinct. Les comptes multi-cellules E3 partagent des tirages: descriptifs seulement, sans
> probabilité conjointe sous indépendance. P1-D D5: pour publier un IC Wilson de FPR, estime lambda_iid sur 20000
> trajectoires de calibration et mesure le FPR sur 20000 trajectoires d'évaluation indépendantes, avec SeedSequence
> rôles distincts, n_cal/n_eval et coût consignés; sinon CI=NA et ligne descriptive exclue de toute porte. Ne présente
> jamais un Wilson du même échantillon de calibration comme inférentiel. La borne réelle doit être stricte et
> l'exclusion du 2005-01-03 D3 doit être explicitement comptée, jamais silencieuse. Fige les cinq indices littéraux
> communs avec E1; teste reset de chaque fenêtre et séparation FPR/ARL/Γ. Le contrôle CLI confirme graphify et
> jcodemunch connectés; recharge et vérifie les deux MCP par appel avant la première écriture. Implémente uniquement E3
> dans ce worktree via .venv et MPLBACKEND=Agg, TDD RED avant corrections, deux quick identiques par cmp, un run
> complet, make check, empreintes, wrapup et commit local. Aucun autre stream, aucun fetch/rebase/push/fusion. En cas de
> blocage outillage ou temps, stoppe et rapporte précisément.

## Reprise après redémarrage de session (verbatim)

> Resume the approved Stream 13 GO and plan revision 4 in this existing worktree. Preserve all five uncommitted paths
> and do not launch a new stream.
>
> Before leaving plan context for implementation, explicitly reload/reconnect the graphify and jcodemunch MCP servers,
> call their tools, and report both connections. Stop if either is unavailable. Use the project .venv for all Python
> commands and MPLBACKEND=Agg.
>
> Complete E3 configuration, meaningful tests, analyses, wrapup, and a local conventional commit with explicitly
> staged paths and no attribution trailers. Log and exclude D3 2005-01-03 before the strict window check, use the same
> five titles as E1, use 2,000 E1 replications for the primary J2 comparison and 20,000 E3 trajectories as a secondary
> analysis, and correct uncertainty reporting for design effect. For P1-D D5, calibrate the thresholds on draws
> independent of evaluation draws before giving Wilson intervals; otherwise mark those intervals unavailable and the
> FPR descriptive. Do not make a separate J2 verdict from E3.
>
> Run the planned focused tests, two identical quick runs, full run, and make check. Check produced CSV rows, FAIR
> hashes, figures, and logs. If a scientific reproduction gate fails, stop and report without tuning to force
> convergence. Report exact paths, commands, outcomes, and commit hash.

## Application par l'instance (révision 4)

- Après le redémarrage, l'instance a rechargé les deux MCP et les a vérifiés par appel avant la première écriture :
  graphify (`graph_stats` : 3 506 nœuds, 4 218 arêtes) et jcodemunch (`resolve_repo` : index chargeable, 2 336
  symboles).
- Les cinq fichiers non commités sont conservés ; leurs empreintes de départ seront reportées dans le wrapup.
- Les corrections obligatoires sont intégrées au plan (section R4) : Q-J2 (verdict primaire J2 (i) d'E1 à 2 000
  réplications, contrôle E3 secondaire sans verdict), comptes multi-cellules descriptifs, P1-D D5 en calibration et
  évaluation indépendantes, exclusion comptée du 2005-01-03 de D3 avant le contrôle strict, indices littéraux figés,
  tests de remise à zéro et de séparation FPR/ARL₀/Γ, arrêt sur échec d'une porte de reproduction.
