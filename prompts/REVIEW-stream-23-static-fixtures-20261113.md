# Réception Codex — témoins statiques 23, 13 novembre 2026

Source de production inchangée : `072b7b0c…8c750`. Tests reçus :
`3670376920d933f52658f668927f9d2f9a891b2be98fd1bf23773494231a943e`. Aucun runtime exécuté.
Les treize tests historiques sont conservés ; les sept fichiers non patchés et C1/C2 restent identiques.

Trois lacunes du témoin nécessitent une correction statique, dans le périmètre déjà autorisé :

1. `_bounded` vérifie stop mais accepte un start négatif ou `slice(None, 0, -1)` qui lit les observations de fin
   de tableau. Imposer un début non négatif, un début <= fin et un pas None ou 1. Ajouter des contrôles négatifs
   explicites pour les tranches inversées et à début négatif, en plus du dépassement de stop existant.
2. Le second appel avec last_day 2018 n'est pas protégé contre une lecture pleine. Le plus petit correctif est
   que `_spy` refuse un mode autre que `r` pour chaque ouverture de ret_wide, avant `np.load`. Cela couvre tous
   les appels, sans nouveau framework ni nouvelle interface.

3. Le cas `dates_not_increasing` n'introduit qu'un doublon. Ajouter un seul cas de permutation de deux dates
   adjacentes distinctes, idéalement à la frontière 2019/2020. Garder le cas doublon : les deux doivent refuser
   avant ouverture des rendements. Aucune nouvelle famille de tests ni choix scientifique.

Corriger aussi le journal : `git diff --numstat` mesure 86 lignes ajoutées, zéro retirée ; 72 ne comptait que les
lignes ajoutées non vides. Actualiser ses comptes, hashes et le diff après correction, ainsi que le nombre d'items
attendus après le nouveau cas calendrier. Ne pas modifier le journal
pour prétendre à des tests exécutés : les nouveaux items restent des attentes non observées.

Autorisation de correction : seulement `tests/test_e6.py` et ses journaux/manifestes ignorés. Aucun patch de la
production, Python, import, test, CLI, pyflakes, donnée réelle/métadonnée, Git en écriture, mémoire partagée ou
module E4. Après contrôle shell et hashes : arrêt pour réception Codex. Budget 10 minutes, même session interactive.
