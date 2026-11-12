# GO technique Codex — 19-e4-code-20261112

12 novembre 2026. **GO TECHNIQUE ACCORDÉ** au plan canonique `prompts/plans/plan-19-e4-code-20261112.md`, SHA-256 `9b11cb50d3273c36fd5bb937ad62a9dca846461d40ed7f6a407bfee1c5d0e819`, avec ses huit précisions de la « Décision GO intégrée », qui priment sur la proposition native v1. Celle-ci est archivée à l'identique, SHA-256 `9aadf2a23688f126677ccfbf5e10bc51fbac4b3841b2d621689025e0910afd40`. Le NO-GO v0 reste une trace conservée, et ses corrections bloquantes sont reçues.

Autorité : GO scientifique conditionnel explicite du chercheur, consigné dans `prompts/GO-stream-19-e4-science-20261112.md`, puis autorisation explicite de transmettre la revue et de reprendre la procédure normale. Codex exerce la revue et le GO techniques délégués ; aucune signature du chercheur n'est inventée et aucun GO full n'est attribué.

Base `ef48fa299c9d3ca6c32022dc5af2e509df903c55`, branche `stream-19-e4-code-20261112`, worktree natif existant. Même session interactive `jepa-s19-e4-code-20261112`, UUID `4da0c70c-efef-4647-8f66-9252acfb9078`, Opus 5.5 Max, aucun Agent/Task ni sous-Claude. Le plafond reste deux instances Claude, toutes sessions comprises.

## Réception et décisions

Les adaptateurs produisent des jours 1..H ou -1 ; les témoins RMST, censure, appariement et branches de qualification sont présents dans v1. Les deux précisions statistiques restantes sont intégrées au plan : appliquer le seuil commun au holdout et aux alternatives avec des trajectoires distinctes ; qualifier la censure par contraste, en conservant EW comme contrôle négatif.

Q1–Q5 sont retenues en (a). Q6(a) retient le coût cumulé conservateur. Le prototype reste limité aux trois nouveaux fichiers de code/configuration/test prévus, avec adaptateur local du registre et modules partagés intacts. La dérogation `C-e4-registry-adapter` est bornée, tracée et testée. Les choix scientifiques, I*, H, grille, effectifs, méthodes, information proxy t7 et absence de rééchantillonnage externe sont inchangés.

## Périmètre d'écriture du worker

- Créer `experiments/e4_alignment.py`, `configs/e4_alignment.yaml`, `tests/test_e4_alignment.py`.
- Ajouter les entrées prévues à `docs/DEVIATIONS.md` (français) et `docs/MAPPING.md`, après lecture, sans réécrire les entrées existantes et sans chiffres non produits.
- Tenir un journal anglais ignoré sous `logs/stream_19_e4_code/`, avec commandes RED/GREEN, résultats, corrections, état exact et SHA-256.
- Après réception du code et signal distinct de Codex : rédiger le rapport anglais du pilote à partir des seuls résultats de coût effectivement obtenus. Aucun rapport de performances de détection.
- Wrapup anglais à six rubriques uniquement après réception indépendante et allocation explicite du créneau de clôture.

Codex possède les plans, GO, NO-GO, notes de pré-implémentation, registres, contrôles globaux et Git. Le worker relève leurs empreintes avant l'implémentation et ne les modifie pas. Aucun module partagé, mémoire, Makefile, hook, dépendance, résultat/figure scellé, papier ou donnée n'entre dans son périmètre.

## Séquence autorisée

1. Sortie officielle du mode plan dans cette même CLI. Attendre la vérification de mode et un **signal distinct de démarrage** de Codex avant toute écriture de code.
2. Appliquer TDD via les skills installés : tests signifiants, RED observé pour la bonne raison, puis minimum GREEN. Exécuter les 18 tâches du plan sur fixtures, avec corps de code, noms et docstrings en anglais. Ne pas remplacer les assertions numériques par des calculs issus du code testé.
3. Utiliser exclusivement `.venv/bin/python` du projet. Avant tout import numérique : OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1, MKL_CBWR=COMPATIBLE, PYTHONHASHSEED=42, MPLBACKEND=Agg, pont torch existant conservé. Aucun pip/conda install.
4. Toute exécution Python/test du worker passe sous le verrou existant `logs/.jepa_execution.lock` de l'arbre principal. Pas d'autre suite en parallèle. Tests E4 ciblés seulement pour le worker ; contrôle global, contrats historiques, précheck réel et pilote sont supervisés par Codex.
5. Fixtures de simulation N <= 8, H <= 60, n <= 40 ; tableaux d'alarmes factices jusqu'à 80 réplicats pour les branches Wilson. Le précheck analytique peut couvrir la grille approuvée sans tirage. Aucun accès à des lignes financières réelles dans le nouveau producteur ou ses tests.
6. Livrer `IMPLEMENTATION_READY` avec chemins, SHA-256, nombre de tests ciblés, commandes effectivement exécutées, journal TDD, limites et état Git en lecture seule. Arrêter les éditions pour réception. Budget de travail de ce lot : 60 minutes à partir du signal d'implémentation ; si incomplet, conserver le travail et déclarer exactement ce qui reste, sans inventer de réussite.
7. Après tests ciblés verts et réception : précheck reproductible et pilote **CPU/mémoire uniquement** sous contrôle Codex, jobs=1, 40 réplicats par rôle, identités de session/partitions et listes blanches du plan. Les tests de workers jobs=3 restent sur petites fixtures. Limites internes et limite de temps externe par invocation ; garder les mesures inconnues explicites.

## Arrêts et clôture

Trois corrections maximum d'un même défaut d'infrastructure ou de test, puis arrêt déclaré. Une rupture de reproduction scientifique ne se résout pas en changeant générateur, amplitude ou seuil. Toute extension du périmètre doit être examinée et tracée par Codex avant action.

La CLI doit refuser full avant toute écriture. Après tests et pilote : rapport de coût mesuré/prévu, risques de censure et identité du protocole figé ; **STOP avant la campagne scientifique full**, qui attend un GO d'exécution ultérieur du chercheur. Aucune nouvelle confirmation du chercheur n'est nécessaire pour les étapes d'ingénierie ci-dessus.

Aucun D6/E6, lecteur réel/privé/2020+, J4/FROZEN, entraînement JEPA/VAE, résultat PCA full 2000 ni scellé E2/E3 modifié. Aucun commit, push, rebase, réindexation ou `make check` par le worker. Codex organise la revue finale, le wrapup, la réindexation AST sans résumé IA, le contrôle global et la publication suivant les règles du projet.
