# Amendement technique Codex — enveloppe mémoire de la reproduction R5

Date : 2026-11-14. Référence : STOP R5 SHA-256
`a5a4b590146c3b00648528d32f80e0a2dd0e3562e2fc1564089b4d4e03c1fe88`.
Le nouvel amorçage du chercheur demande la clôture rapide du seul E6 phase 1 déjà autorisé. Cet amendement porte
exclusivement sur une limite d'infrastructure introduite par Codex pour R5, pas sur un choix scientifique.

## Diagnostic reçu, sans relance

R1 mutant a donné deux échecs attendus ; R2 donne 27 passed ; R3 pyflakes passe ; R4 quick jobs=1 reproduit
exactement le CSV `874be21275625e7f160a8ee351ee05811f71dc5673107ee7e2f54998b409a1e2`.
Le premier R5 jobs=48 est interrompu avec `Result=oom-kill`, MemoryMax=8589934592, OOMPolicy=stop,
après 18.45 secondes. Aucun résultat complet n'existe, donc aucune divergence numérique C3 n'est établie.
Le scope arrêté conserve CPUUsageNSec=280250667000 : **280.250667 CPU_s mesurées**, incluant son infrastructure.
Ce compteur récupéré remplace la seule qualification UNKNOWN du coût R5 dans le journal antérieur ; il ne
chevauche aucune mesure GNU time finalisée de R5, puisque celle-ci est vide. Les preuves antérieures restent.

Le code historique crée jusqu'à min(48,ceil(2000/64)) = 32 workers spawn. Chaque tâche alloue au minimum
64*500*239*8 = 61184000 octets pour X, avant les transformations et copies. Les imports indépendants et les
autres buffers s'ajoutent dans chaque processus. L'OOM agrégé est établi ; sa répartition exacte par processus
ne l'est pas. Le quick séquentiel ne mesure pas ce pic agrégé. Aucun noyau ou paramètre n'est modifié.

La machine dispose d'environ 192 Go de RAM ; le relevé hôte Codex après incident rapporte plus de 155 Gio
disponibles. La limite de 8 Gio de ce GO R5 était une enveloppe choisie par Codex ; le plafond de 8 Gio du GO
E4 n'est pas étendu automatiquement à tous les streams. Le GO scientifique E6 autorise déjà la reproduction
historique jobs=48. L'allocation de ressources reste sous contrôle Codex.

## GO technique de reprise unique

Codex autorise **une reprise R5 seulement**, avec MemoryMax=64G, OOMPolicy=stop, timeout=1200 secondes,
jobs=48 et tous les paramètres/versions/graines/empreintes C3 strictement identiques. Cela remplace uniquement
MemoryMax=8G pour cette invocation. Source reçu SHA-256
`5af91240df658f8ec7e8f45139cf74144ed9c6665d52bc6f8aec67da42902855`, tests
`39d706c0e11658f47a87283cc7e73a236c68e2919b97af25c9e77576d5ebedfc`, configuration
`ca74d2e117edb47b0ff11822501a20a381460c35c69e81b57a6d11de81a2bcf5` restent inchangés.

Préflight : verrou exclusif, aucune autre charge numérique orchestrée, RAM disponible >=96 Gio et disque libre
>=5 Gio. Si ces ressources ne sont pas disponibles, attendre sans lancer ni changer les jobs. Ne pas refaire
R0–R4 déjà reçus. La sortie logs/23-phase1/full est encore absente et doit le rester avant ce lancement.

La mesure GNU time doit envelopper systemd-run DEPUIS L'EXTÉRIEUR du scope, pour conserver un reçu même si
le scope est tué ; relever également le compteur CPU du scope et son état dès la sortie. Garder séparés coûts
par processus et compteur agrégé, sans double comptage. Préserver le scope défaillant initial et ses journaux.

Si la reprise réussit : vérifier immédiatement le CSV et les quatre figures contre sealed-full.sha256, puis R6.
Toute divergence numérique, timeout ou nouvel OOM impose STOP définitif de ce lot et retour au chercheur, sans
autre reprise. Aucune augmentation supplémentaire de RAM ni baisse de jobs n'est autorisée ici.

Les restrictions scientifiques, fenêtres antérieures à 2020, H-cal, D6 descriptif/in-sample, D5 indépendant,
conventions PCA, Wilson et critères de reproduction restent ceux du GO historique. Pas de donnée privée,
J4, JEPA, phase 2, nouveau code, exploration ni retouche de hash. Pas de Git en écriture par Claude.

Cet amendement lève uniquement l'arrêt d'enveloppe R5 pour cet essai borné. Il ne déclare ni C3 reçu ni le stream
23 clos. En parallèle, la préparation documentaire du stream 32 est autorisée par le nouvel amorçage, sans calcul.
