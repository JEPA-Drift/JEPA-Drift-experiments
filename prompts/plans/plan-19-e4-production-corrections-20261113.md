# Annexe corrective — E4 production, driver hôte (R7), 13 novembre 2026

Annexe autonome au plan canonique figé `prompts/plans/plan-19-e4-production-20261112.md` (SHA-256
`22c71798b0bfd7b9cb396f30695ce991819a65c9983bc9ad2190798db2de6504`), qui n'est pas modifié. Elle est couverte par le GO
technique correctif R7 de `prompts/NO-GO-stream-19-e4-production-reception-20261113.md`. Elle ne contient aucun choix
scientifique et ne change ni I*, ni cohorte, ni grille, ni graines, ni méthodes, ni seuils, ni plafonds.

## Objet

La boucle hôte du §9 n'existait que comme bloc de texte. Elle devient un seul script `tools/run_e4_production.sh`,
le fichier même que Codex exécutera, testé par `tests/test_e4_production.py` avec un producteur stub borné.

## Façade minimale du §9

- `tools/run_e4_production.sh attempt ARGS...` : une tentative mesurée. Réservation `A<7 chiffres>` par `mkdir` atomique,
  `cmd.txt` écrit avant le lancement, GNU time (`%U %S %e %M %x`) et `timeout --signal=TERM --kill-after=10s 1790s`,
  puis `exit.txt` après retour (finalisation). Environnement déterministe, `E4_ATTEMPT_ID` transmis. Code de sortie =
  celui du producteur ; 8 si la réservation échoue.
- `tools/run_e4_production.sh campaign MODE ROOT BLOCK TARGET [ACTIVATION]` :
  1. `plan` avec le bloc reçu ; K doit être un entier décimal sans zéro initial avant toute arithmétique, sinon code 5 ;
  2. au plus K + 1 `next` ; code 10 → sortie de boucle ; tout autre code non nul est propagé ;
  3. borne épuisée sans code 10 → code 9 ;
  4. `verify`, puis `publish` vers TARGET, chacun propagé ; succès (0) seulement après 10, `verify` et `publish`.
- Producteur fixe `.venv/bin/python experiments/e4_production.py`, chemins relatifs à la racine du dépôt, journal
  `logs/stream_19_e4_production/attempts`. Verrou partagé par défaut ; seule la variable `E4_LOCK` permet aux tests
  d'utiliser un verrou temporaire (le verrou commun est déjà tenu par la commande de test).

## Tests (producteur stub, aucun calcul E4)

Le test crée, dans un répertoire temporaire, un faux `.venv/bin/python` (script bash) qui journalise ses arguments et
renvoie des codes scriptés. Il exécute le vrai `tools/run_e4_production.sh` et vérifie :
- K non décimal, vide ou à zéro initial refusé avant tout `next` ;
- bloc transmis à `plan` ;
- succès seulement sur 10 suivi de `verify` et `publish` ; propagation d'une erreur de `next`, `verify` ou `publish` ;
- borne K + 1 épuisée → 9, sans `verify` ;
- reprise : les fichiers des tentatives antérieures restent identiques octet pour octet, les nouvelles s'ajoutent.

`bash -n` du script et tests ciblés sous verrou commun, `.venv`, mesures W0018+. Aucun pilote réel par le worker.
