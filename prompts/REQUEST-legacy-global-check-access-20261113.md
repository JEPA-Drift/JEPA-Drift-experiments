# Demande au chercheur — vérification globale historique, 13 novembre 2026

**État : PROPOSITION NON AUTORISÉE. Aucun nouveau contrôle global concerné n'est lancé.**
La campagne scientifique E4 synthétique continue sous son GO existant ; cette demande ne change pas son protocole.

## Conflit concret à résoudre avant la clôture Git

CLAUDE.md impose « tests never read such rows (Article B identity reproductions excepted) » pour les lignes 2020+.
Il impose aussi `make check` avant chaque commit ; le hook pré-commit le relance. La baseline contient notamment :

- `tests/test_data_d3.py::test_d3_500_assets_2020` : effectif de l'univers réel en 2020 ;
- `tests/test_data_d3.py::test_reconstruction_from_cache` : reconstruction et comparaison du panel complet ;
- `tests/test_data_d3.py::test_d3_profile_csv` : profil contenant monitor et eta_2022_2024 ;
- des statistiques descriptives D2 sur la période complète, distinctes des reproductions d'identité Article B ;
- des chargements complets de fichiers avant sélection pré-2020 dans les tests de caractéristiques.

L'audit `docs/audits/legacy_global_checks_data_scope_20261113.md` et la revue indépendante établissent qu'une
fixture synthétique ou un préfixe vérifierait autre chose pour les assertions sur période complète. La présente
demande ne concerne pas l'autorisation Article B déjà acquise et ne la redemande pas.

## Autorisation limitée proposée

Autoriser la baseline locale inchangée `make check` et son hook pour intégrité et non-régression, y compris ces
lectures historiques sur période complète. Aucun test n'est écarté pour faire passer la clôture. Exécution dans
la .venv et l'environnement déterministe épinglés, avec gardes torch/PCA-G1 réellement exécutées, journalisation
des commandes/sorties/CPU/RSS et comptabilité cumulée du lot. Les cinq skips D4 attendus restent explicites.

La commande reste `make check`, sous le même environnement que R0009 et le verrou partagé, après la campagne E4.
`PCA_FULL2000_TRIALS` doit pointer vers l'entrée scellée SHA-256
`40b5f8919684bce13b266a83fe0ddf3e5ff295a6330a15c0fe9cbf5deb310b5c` ; aucun artefact scellé n'est modifié.
Le hook utilise la même baseline. Les journaux complets restent locaux ; seuls les bilans et empreintes admis
sont publiés. Aucun téléchargement, aucune donnée privée/EUROFIDAI ; disponibilité D4 inattendue ⇒ arrêt avant lecture.

Cette exception ne permet aucun choix scientifique à partir de ces données, aucune campagne ou mesure nouvelle
sur monitor, aucune sélection de cohorte/seuil/hyperparamètre, aucun J4/FROZEN, modèle ou checkpoint scientifique,
entraînement expérimental JEPA/VAE, ni modification des scellés E2/E3/PCA. Les résultats scientifiques E4 restent
exclusivement synthétiques. Le code F2 reste derrière ses deux arbitrages et son propre GO technique.

## Alternative sans cette autorisation

Maintenir la restriction stricte et laisser explicitement la clôture QA/Git en attente. Aucun skip silencieux,
indisponibilité artificielle de fichiers, changement du sens des tests ou contournement du hook. Le rapport
scientifique et les sorties E4 peuvent être reçus localement ; leur intégration contrôlée attend la résolution
de cette porte. Une continuation seule ne constitue pas l'exception demandée.
