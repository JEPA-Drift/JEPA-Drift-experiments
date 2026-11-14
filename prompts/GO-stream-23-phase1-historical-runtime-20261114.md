# GO technique distinct — témoins et reproductions historiques E6 phase 1

Date : 2026-11-14. Codex active la suite du lot R déjà autorisé scientifiquement par le chercheur, sans nouvelle
question, cohorte, famille, amplitude, graine ou règle statistique.

## Réception préalable

E4 est publié au commit `461f2b13894be2cca954676dc3aab10e0b640a2b`. GR0–GR3 restent satisfaits ; R0 versions
et emplacements a passé. Le RED initial a donné les 14 erreurs DERIVED attendues avant lecture. P-IO est reçu :

- source `experiments/e6_second_order.py` :
  `5af91240df658f8ec7e8f45139cf74144ed9c6665d52bc6f8aec67da42902855` ;
- tests `tests/test_e6.py` : `39d706c0e11658f47a87283cc7e73a236c68e2919b97af25c9e77576d5ebedfc` ;
- GREEN : 14 passed en 0.64 s ; pyflakes code 0 ; manifeste SHA256SUMS vérifié par Codex depuis son répertoire ;
- revue indépendante : READY_FOR_BOUNDED_HISTORICAL_RUNTIME, aucun constat bloquant. Hors I/O/log autorisés,
  le texte du source est identique à 3d0bd20 : noyaux numériques, paramètres, graines et Wilson inchangés.

Journaux sources : `logs/23-phase1/pio-green-20261114/`. Cette réception ne vaut pas approbation d'intégration :
les preuves C3 et C4 restent à établir.

## Signal du lot historique

Après le signal de démarrage distinct dans la session conservée, exécuter dans l'ordre, avec arrêt au premier écart :

1. R1 mutant jetable du plan, sous logs/23-phase1/mutant/e6_full_read.py. Ne sélectionner que
   `tests/test_e6.py::test_bounded_reader_slices_no_return_row_after_last_day` (deux cas C/F). Attendu : deux
   échecs du témoin d'ouverture pleine, pytest code 1, sur panels synthétiques. Le plugin n'est chargé que dans
   ce processus ; aucun mutant sur données réelles. Pour R1 seulement, PYTHONPATH=.:logs/23-phase1/mutant.
2. R2 : le fichier tests/test_e6.py entier, dans un nouveau processus sans plugin ni shim torch, via
   `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_e6.py`. Attente : 27 cas, dont treize historiques
   inchangés ; rapporter les comptes réellement observés. La fixture d6 réelle est maintenant autorisée sur
   les seules lignes lues par le lecteur borné reçu, antérieures à 2020.
3. R3 pyflakes des deux fichiers ; sans correction du source gelé après un échec scientifique.
4. R4 quick historique, jobs=1, exactement selon le plan canonique, sortie neuve logs/23-phase1/quick.
   Vérifier immédiatement sealed-quick.sha256 :
   `874be21275625e7f160a8ee351ee05811f71dc5673107ee7e2f54998b409a1e2`.
5. R5 complet historique, jobs=48, mêmes paramètres du plan, sorties neuves logs/23-phase1/full, avec figures
   et journal dans ses sous-répertoires prévus. Vérifier sealed-full.sha256 : CSV
   `4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249` et quatre figures archivées inchangées.
6. R6 : vérifier les témoins de provenance du plan : aucune mention de ret_wide.npy dans le journal ; config et
   splits hachés ; calib [2834,3775), 941 jours du 2016-04-07 au 2019-12-31 ; empreinte des 3775 x 239 seules
   lignes de rendements consommées, en ordre C. Cette empreinte de traçabilité n'est pas une nouvelle cible C3.

R0 déjà reçu n'est pas à refaire sans changement d'environnement. Les exemples de noms de tests et comptes
2 failed/15 passed du plan natif sont remplacés par les noms reçus et les comptes effectifs ci-dessus.

## Enveloppe, refus et arrêt

Chaque invocation : .venv, environnement déterministe du plan, PYTHONPATH retiré hors R1, verrou partagé du
checkout principal, scope MemoryMax=8G, GNU time et journaux neufs. Timeouts du plan : R1 300 s, R2 600 s,
R4 900 s, R5 1200 s ; au plus 30 minutes par invocation. Aucune concurrence numérique. Les coûts 23 restent
séparés d'E4. Aucun paquet, module partagé, configuration, donnée, résultat archivé, figure scellée ou test
reçu n'est modifié. Les sorties de reproduction restent sous logs ignorés ; aucune intégration Git par Claude.

H-cal accepté : dates.npy et splits.yaml sont lus en entier comme métadonnées. Aucun rendement 2020+ n'est
indexé, copié, haché ou calculé ; aucune fenêtre n'est raccourcie. D6 reste descriptif/in-sample ; D5 reste un
contrôle indépendant conditionnel à son unique fit ; indices PCA, labels, CI indisponibles et Wilson inchangés.
Pas de J4, FROZEN, données privées, phase 2, JEPA/P5-D ni harmonisation pour obtenir un hash.

Tout timeout, résultat de témoin différent, échec R2/R3 ou divergence C3/R6 impose STOP immédiat et un rapport
français non suivi `prompts/STOP-stream-23-phase1-<porte>.md`, avec commande, codes, hashes attendu/observé,
écart disponible et environnement R0. Aucune relance, modification de paramètre, de jobs ou de hash pour forcer
la reproduction. Si tout passe : transmettre les preuves et attendre réception Codex avant les notes de clôture.
