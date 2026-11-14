# Précision Codex — préparation des témoins avant le patch I/O

Ce complément restreint l'ordre du GO statique, sans changer les choix scientifiques ni les identités du plan et
du GO déjà remis. Il évite d'écrire un nouveau comportement de production avant d'avoir observé son témoin RED.

Pendant E4, Codex peut matérialiser les deux commits historiques dans l'ordre, sans commit. Claude prépare
uniquement les fixtures et témoins de `tests/test_e6.py`, les manifestes et le journal ignorés. Aucun patch de
`experiments/e6_second_order.py` n'est encore autorisé. Les références historiques ne sont pas modifiées.
Les treize tests historiques sont conservés. Aucun Python, test, import, CLI, sonde réelle ou autre calcul.

Au futur créneau runtime, après E4 clôturé/publié, Codex autorisera la séquence : exécuter les nouveaux témoins
synthétiques contre le code historique → constater RED sans lecture réelle → appliquer le patch I/O borné du plan
dans le même contexte → GREEN sur fixtures → contrats/reproduction C3 selon les portes existantes.
L'ancien mutant peut compléter cette vérification ; il ne remplace pas le RED préalable au nouveau patch.

Cette précision prime sur toute phrase du lot S qui permettrait S1 avant le runtime. La sortie native du mode plan
et le signal distinct restent requis. Les sources partagées/E4 restent intouchées ; 27/21 restent sans implémentation.
