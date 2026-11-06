# Stream 31 — revue Codex du plan v1, révision requise

Date : 2026-11-06. Décision de l'orchestrateur dans le mandat délégué par le chercheur ; ce document n'est ni sa signature personnelle ni un GO d'exécution.

Plan v1 : 562 lignes, SHA-256 `34f07a35ee96abe7e24eb268224b2d75a2da6d653f214ef4c494c5ea437fa01d`, archivé sans changement dans `logs/orchestration_reprise_20261106/plan-v1.md`. Base : `a0c576e13e8e647dfd61350eec52058ffc794dbf`.

**Verdict : NO-GO d'exécution sur v1. Réviser le plan natif seulement, puis attendre la revue.** Aucun code, test, master ou artefact suivi ne doit être modifié. Le GO d'outillage sera un document distinct, après révision. Aucun producteur scientifique ni fichier scellé n'est autorisé à changer.

## Constats vérifiés

- `make check` de la base actuelle : code de sortie 0, 37 passés en 36,66 s puis 538 passés et 5 ignorés en 450,90 s. Pyflakes propre. Aucun test 31 n'existe encore.
- Les 29 blocs historiques extraits avec `blocks()` sont exactement égaux à leurs sources après retrait des seuls séparateurs de fin. Le master sur disque n'a pas été modifié.
- L'ajout en mémoire des 4 prompts PCA conserve le master comme préfixe, mais le deuxième `sync()` n'est pas identique : longueurs 136069 -> 184889 -> 184875 caractères. L'ouverture de fence absorbée par le bloc final 8b explique cet écart. C'est un défaut d'outillage à couvrir en RED.
- Le PDF full corrigé existant `Figure_1_mean.pdf` contient réellement « equality test (n = 40) », alors que son manifeste déclare 2000 trajectoires par rôle. Le même texte est en dur dans `plot_figure_1.py`. Ce défaut d'étiquette est établi, sans changer les mesures ni les fichiers scellés.

## Corrections obligatoires du plan

1. **E1, indexation.** `parse_S` retourne des axes 1-based et `S_json` reçoit des axes 0-based. Le round-trip est `S_json([i - 1 for i in parse_S(text, nmax)]) == text`. L'expression v1 décale tous les axes valides et produirait un faux échec scientifique.
2. **E3, domaine SPD.** Ne pas attribuer à `kl_cov_raw` une validation universelle SPD : le code contrôle le signe du déterminant, ce qui n'est pas équivalent. Tester les cas de rejet effectivement documentés, la finitude et la tolérance `clip_kl` de 1e-12, sans appeler cette constante l'epsilon machine. Consigner la limite de validation SPD comme observation distincte. Une nouvelle exigence de validation complète doit être arbitrée, pas injectée comme faux contrat déjà implémenté.
3. **A18, calibration.** Une égalité numérique fortuite entre un seuil par rang et un logarithme n'est pas une violation. Vérifier la recette du rang et le flux des données, pas une interdiction `threshold != log(gamma)` pour tout échantillon. La séparation calibration/holdout et l'absence de garantie e-process restent obligatoires.
4. **B1/B3, domaine et compteurs.** Séparer les identités de valeurs mesurées des lignes bloquées à NA et de leurs identifiants/statuts. Ne pas compter une égalité de deux NA comme une métrique mesurée vérifiée. Pour B3, filtrer `row_kind=SELECTED` : les candidats ne portent pas de métrique. Conserver le domaine additif plug-in figé ; ne pas lui transférer l'optimum de KL jointe population ou covariance.
5. **F-fake, calendrier.** Un calendrier de jours ouvrés factice n'a pas 941 séances réelles. Déclarer ses propres effectifs/configuration, calculés sur ce calendrier, et conserver la vérification des 941 dates réelles comme contrôle de métadonnées distinct. Aucun rendement réel n'est à lire.
6. **D7a, annotations.** Vérifier qu'une annotation suit les valeurs et son statut. Ne pas interdire des chaînes générales (`≈`, `d*`, 5 %) qui peuvent être licites lorsqu'elles sont calculées ou clairement présentées comme cibles.
7. **Outillage minimal.** Conserver la sémantique générale de synchronisation des blocs canoniques, sans nouvelle restriction permanente « seuls les quatre PCA peuvent être mis à jour ». Pour notre migration : précontrôle des 29 blocs historiques, premier sync à ajout pur, deuxième sync identique, empreintes historiques inchangées. Le contrôle normal doit échouer sur master tronqué, fichier attendu absent/modifié, titre dupliqué ou ensemble incomplet. Préserver l'exigence de présence exacte du texte source, sans normalisation cachée des fins de ligne. L'extraction des étendues doit s'arrêter à l'ouverture de fence suivante pour le cas 8b. Les API de tests sur petits dictionnaires peuvent rester génériques ; la CLI du dépôt vérifie les 33 identifiants attendus, dont `28` distinct de `28-PCA`.
8. **Ordre et arrêt.** Proposer d'abord le lot d'outillage, puis un arrêt pour revue et commit indépendant par Codex, avant toute création de la suite QA. Le plan QA reste complet mais son GO d'exécution est distinct. Le défaut établi D7b reste un véritable FAIL à consigner, sans xfail ni correction producteur. Après son test et le constat, aucun commit QA ni nouvelle tâche de code : rapport/état STOP et arbitrage séparé du chercheur. Ne pas lancer `make check` ni l'outillage après un STOP non levé.
9. **Livrables portables.** Employer `.venv/bin/python` et `.venv/bin/make`, avec PATH du venv ; enlever les chemins personnels absolus du futur plan canonique et des commandes suivies. Ne pas recopier le refus de quota `PLAN.md` ni modifier ses octets.
10. **TDD sur l'existant.** Les témoins mutés vivent dans tmp_path ou en mémoire. Ne pas altérer les producteurs pour fabriquer RED. Les erreurs de référence/fixture de la QA se diagnostiquent séparément, au plus trois corrections tracées ; un défaut numérique/provenance confirmé déclenche STOP.

## Réponses Q1–Q12

1. **Q1 : oui**, références indépendantes pour les invariants demandés ; pas d'import des tests producteurs. Éviter les doublons mécaniques qui ne vérifient rien de nouveau ; recouvrement documenté.
2. **Q2 : oui**, F-tiny et F-fake sont des fixtures unitaires synthétiques à très petite taille, en répertoires temporaires, avec oracle et aucune ligne réelle. Aucun CLI full/smoke de production, aucune régénération des tableaux/figures scellés.
3. **Q3 : oui**, lecture du calendrier `dates.npy` et de ses métadonnées/empreintes seulement. Aucun rendement, caractéristique ou test financier 2020+.
4. **Q4 : oui sous limite**, skip de disponibilité uniquement pour G1 quand aucun chemin local n'est fourni, explicitement compté BLOCKED. Les tests mathématiques ne sautent jamais ; une empreinte erronée ou une divergence numérique est FAIL, pas BLOCKED. Ici, G1 devra réellement être exécuté avec `PCA_FULL2000_TRIALS` vers le fichier existant, en lecture seule, sans copie.
5. **Q5 : option (a)**, diagnostic de test puis STOP et rapport. Aucun GO de correction du traceur et aucune réécriture des figures scellées. Une correction demanderait un plan et un GO séparé du chercheur.
6. **Q6 : oui**, tolérance flottante explicite pour la symétrie de la rotation ; aucune exigence bitwise entre ordres d'opérations différents.
7. **Q7 : oui**, une mutation qui viole un contrat documenté mais reste acceptée constitue un FAIL réel, après vérification que le témoin et le code de rejet attendu sont corrects.
8. **Q8 : retenu**, `docs/audits/PCA_CONTRACTS_VALIDATION.md`.
9. **Q9 : retenu**, A et C sur Gauss et t7, avec l'étiquetage proxy t7 et le domaine additif plug-in explicites ; aucune égalité d'oracle covariance.
10. **Q10 : alternative minimale**, sémantique générale conservée ; migration actuelle append-only contrôlée, idempotence corrigée, contrôle normal non vacu sur l'ensemble des 33 IDs. Pas de réattribution d'ID ni de réécriture d'archive.
11. **Q11 : amendé**, outillage en premier avec GO séparé et revue/commit avant la QA. Cela permet de clôturer ce lot indépendant avant le diagnostic D7b qui peut bloquer la clôture QA. Aucun Git par Claude.
12. **Q12 : oui**, `spec.tags` est une copie du registre ; seules les étiquettes effectives de rendu et de légende portent la promesse conditionnelle. Cette distinction reste vérifiée et documentée.

## Prochaine action autorisée

Réviser le plan natif en v2 avec ces corrections et réponses intégrées au corps. Le plan v1 archivé demeure intact. Proposer un plan d'exécution borné du seul lot d'outillage, les fichiers possédés et les commandes RED/GREEN, puis attendre un GO écrit. La sélection de l'option « modifier le plan » dans l'interface Claude ne donne aucune permission d'implémenter.
