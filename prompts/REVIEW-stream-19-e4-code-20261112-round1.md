# Réception technique E4 — corrections ciblées, passe 1

12 novembre 2026. Base ef48fa299c9d3ca6c32022dc5af2e509df903c55 ; même branche et même session Opus 5.5 Max.
Version reçue : `experiments/e4_alignment.py` SHA-256 `bc7beb7af7f400dd0db742a2b1bd4af0e042648f7fdaa35c8591f1be607314dc` ; tests `1cd1ca32679d06896802aca999d4671d8c4dc246c372ec4ea2217b1580f7fcd3` ; configuration `5b9086948f3d7a49753a64d5b2ff01616ecaa1e02e2574777f45db51a3b3d1f2`.

Réception indépendante : **86 tests passent en 8,36 s**, sans cache pytest. Deux contre-revues indépendantes ont lu les calculs scientifiques et le pilote. Aucun précheck réel ni pilote n'a été lancé. La réception du code est différée jusqu'aux corrections suivantes ; le GO technique existant couvre leur réalisation. Aucun nouvel accord du chercheur n'est demandé, aucun GO full n'est donné.

## Corrections requises

### R1 — K_MP doit compter les axes résiduels

`fit_cell` (l.284) exporte `basis["mp_count"]`, nombre total de valeurs propres au-dessus du bord MP, PC1 compris. Le diagnostic K_MP désigne le nombre résiduel après PC1. Dans le cas unifacteur, il doit donc être 0 et non 1. Calculer le compte résiduel non négatif et conserver le compte total séparément si utile. Ajouter un témoin littéral « marché seul au-dessus du bord ⇒ K_MP=0 ».

### R2 — Exporter les diagnostics scientifiques approuvés

`oracle_diagnostics` et `DIAG_COLUMNS` (l.341-342, 369-380) perdent des quantités exigées par le protocole §4 : I*, information du flux de signes O-dir, J_k par axe et a_max plug-in. Compléter les sorties et leurs tests sur une base connue, en conservant a_best et la KL jointe projetée comme objets distincts.

Les informations gaussiennes portent les labels appropriés ; sous t7, I* reste INFO_GAUSS_PROXY_T7. L'information du flux de signes est la KL Bernoulli correspondante, et ne doit pas être présentée comme la KL des rendements t7. Conserver ORACLE_* sur les lignes des méthodes et diagnostics oracle, y compris leurs métadonnées par méthode. Ne pas générer de sortie scientifique réelle : les nouveaux témoins restent factices et le full reste refusé.

### R3 — Ne pas perdre le CPU consommé lors d'un arrêt

`Meter.stage` (l.739-749) ne finalise aucune mesure si le corps lève une exception. `_pilot_cell` ne marque un rôle terminé qu'après tous ses blocs (l.827-828), et `_cost_rows` efface alors des mesures déjà présentes en les remplaçant par NOT_MEASURED. Enfin `forecast` ne compte que les lignes COMPLETE (l.914).

Finaliser les compteurs en `finally`, distinguer travail achevé et travail interrompu, et conserver les coûts finis effectivement consommés. Une ligne partielle peut porter BLOCKED_RESOURCE ; elle ne doit ni annoncer une trajectoire achevée qui ne l'est pas ni être extrapolée comme un stade complet. Les coûts consommés incluent les mesures partielles, tandis que la prévision reste INCOMPLETE. Tester un arrêt après un premier bloc achevé et un arrêt au milieu d'un contexte mesuré, pas seulement avant le premier tirage.

### R4 — Mesurer le travail effectivement prévu dans la route scientifique

La route `_cell` calcule `oracle_diagnostics` pour chaque alternative (l.435), mais le pilote ne le mesure pas. Ajouter un stade pour ce travail, jeter son résultat en mémoire et extrapoler selon n_alt/pilot_n. Son coût est obligatoire même si les diagnostics ne changent pas les alarmes. Une réutilisation exacte de termes indépendants de la dérive au niveau du fit est permise si elle est testée et utilisée aussi par le prototype ; aucune approximation silencieuse.

`bootstrap_fixture` (l.766-771) ne représente qu'une partie des opérations de `analyse` : il manque les gathers du holdout, les avertissements O-dir, les pentes, percentiles et regroupements. Mesurer l'analyse effective sur tableaux d'alarmes COST_FIXTURE aux dimensions approuvées, pour les deux lectures qui seront rapportées, puis jeter ses sorties. Ni performance simulée du pilote ni résultat factice ne doit être persisté. Ne pas multiplier de nouveau par 50 une mesure déjà aux dimensions finales.

### R5 — Comptabilité de l'invocation complète

Les imports, la validation initiale, la seconde écriture CSV, les hashes/JSON finaux et la journalisation sont en partie hors des compteurs de stade. Le journal déclare certains de ces manques, mais `forecast` appelle encore la somme des stades le coût consommé du pilote.

Fournir une mesure CPU de l'invocation complète, imports compris, et réconcilier cette mesure avec la somme des stades sans double comptage. Un relevé externe vérifié par Codex est acceptable si l'interface de prévision l'utilise explicitement ; sinon employer un compteur cumulatif du processus, avec une borne de mesure documentée. Conserver toute différence comme coût d'orchestration mesuré ou comme inconnue explicite, jamais comme zéro caché. Les projections de reprise/import/IO futurs restent des hypothèses distinctes des mesures. Ajouter un témoin où le total d'invocation dépasse la somme des stades et où le surplus compte bien sous Q6(a).

### R6 — Empreinte de tous les modules effectivement appelés

`CODE_FILES` (l.651-654) omet `jepadrift/representations/extract.py`, alors que `fit_pipeline` appelle `_rows` de ce module à chaque fit. Inclure ce fichier dans l'identité et tester qu'une empreinte de ce module modifiée change la session et interdit la reprise. Aucun fichier partagé n'est modifié par cette correction.

### R7 — Une base refusée ne doit pas rendre artificiellement complet le coût des six méthodes

Sur EigenTieUnresolved, `_pilot_cell` réduit ses méthodes à EW/O-dir, puis retourne COMPLETE et une liste de stades également réduite. `forecast` peut donc chiffrer une cellule « complète » sans les quatre méthodes dépendantes de la base.

Conserver la liste des stades attendus pour les six méthodes. Les stades refusés reçoivent EIGENVALUE_TIE_UNRESOLVED ou NOT_MEASURED, sans coût fabriqué ; la projection reste INCOMPLETE. Tester un fit ambigu forcé dans la route pilote et l'absence de prévision complète. Les statuts ne changent ni la grille scientifique ni les graines.

## Discipline de correction et livraison

- Écrire et observer d'abord les témoins RED qui reproduisent ces comportements, puis appliquer le minimum GREEN. Ne pas modifier les tests précédents pour masquer une erreur ; conserver le journal TDD antérieur et y ajouter cette passe.
- Garder le périmètre du GO : script, tests, configuration uniquement si correction justifiée, ajouts documentaires nécessaires. Aucun module partagé, scellé, mémoire, dépendance ou choix scientifique ne change.
- Corriger aussi l'hygiène locale simple : docstrings publiques sur une ligne et commentaires uniquement sous la forme ponytail prescrite. Pas de refonte générale, framework ou fichier de code supplémentaire.
- Toutes les exécutions restent sous le verrou partagé et `.venv/bin/python`, avec les variables déterministes. Aucun make check, précheck réel, pilote réel ou Git par le worker. Les stades COST_FIXTURE aux dimensions finales peuvent être validés par un témoin borné ; les tests usuels restent petits.
- Budget de cette passe : 40 minutes depuis le signal explicite de Codex ; trois corrections maximum pour un même défaut. Fournir CORRECTIONS_READY, nouveaux SHA-256, tests ciblés, journal, limites restantes, puis arrêter les éditions pour réception.

La campagne scientifique full reste désactivée. Cette revue ne demande aucun ajustement de seuil, d'amplitude, de grille ou de performance de détection.
