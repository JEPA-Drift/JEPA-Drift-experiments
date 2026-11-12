# Décision du chercheur — 19-e4-code-20261112

Décision explicite reçue dans la conversation le 12 novembre 2026 : **GO SCIENTIFIQUE CONDITIONNEL** sur `docs/audits/stream_19_protocol_proposal_20261112.md`, version publiée au commit `ef48fa299c9d3ca6c32022dc5af2e509df903c55`, SHA-256 `602e7abcc50ac671464eb7323f578b1bdd8f002a5e04020e073b2c3764831e19`. Cette consignation ne constitue ni une signature inventée, ni le GO technique du plan de code, ni le GO d'exécution full.

## Question et périmètre approuvés

Mesurer en simulation synthétique équicorrélée comment varie avec N le délai d'un dictionnaire spectral défini ex ante quand l'information gaussienne totale de la dérive résiduelle est constante. Ce lot diffère de l'E4 historique à amplitude par actif fixée, ne le remplace pas et ne constitue pas une validation de la sélection PCA informationnelle apprise sans oracle.

- Gaussian equicorrelated, rho = 0.4 ; dérive résiduelle isotrope orthogonale au marché ; information quotidienne I* constante. Conserver la règle d'amplitude et la grille du §3 : ln(gamma_H)/I* = H/40 ; N = 8, 16, 32, 64, 128, 239, 500, sous les seuls replis de coût prédéclarés.
- Méthodes et distinctions du §4 : EW, SPEC-prefix8, SPEC-full, P3-CS(b), O-dir et O-score1 ; les deux dernières restent ORACLE.
- Lecture principale : calibration prédictive par rang, alpha = 0.05, H = 2000 ; lecture anytime-valid secondaire.
- T_fit = 2000 ; n_cal = n_hold = n_alt = 2000 ; 2000 tirages bootstrap appariés ; seed 42.
- Sensibilité Student t7 ; information étiquetée INFO_GAUSS_PROXY_T7, jamais KL t7.
- Qualification de faible censure : borne inférieure Wilson du taux de détection >= 0.95 sur toute la grille du contraste. Publier toutes les cellules, y compris NOT_IDENTIFIED ; aucun recalage d'amplitude après observation.
- Budget total maximal 24 CPU-heures, replis du §8, sans approximation algorithmique silencieuse. Les limites de 8 GiB et 30 minutes par invocation du protocole restent actives.
- Inférence conditionnelle à la base PCA et aux calibrations réalisées ; aucun rééchantillonnage externe des fits dans ce lot.

## Arbitrage B — calibration scalaire commune

Le chercheur décide de partager **une calibration nulle unique** entre EW, O-dir et O-score1, sous l'hypothèse de projections fixées indépendamment des trajectoires et d'un même e-détecteur scalaire sur signes i.i.d. Bernoulli(1/2).

Conditions : indépendance de toutes les alternatives et du holdout ; mêmes paramètres de mise et règle de franchissement ; calcul du seuil une seule fois puis gel ; aucune trajectoire de calibration partagée avec holdout ou alternative. SPEC-prefix8, SPEC-full et P3-CS(b) gardent leurs calibrations propres par cellule. Les FPR holdout sont mesurés séparément pour toutes les méthodes. Les intervalles des contrastes conservent les dépendances dues à l'appariement entre méthodes et N.

## Arbitrage C — valeurs propres

Avant le plan de code, lire `eigh_desc` et documenter ses conventions réelles. La base provient uniquement du fit nul ; aucune dérive ne la choisit.

- Ordre décroissant déterministe des valeurs propres.
- Signe de chaque vecteur propre fixé par sa coordonnée de valeur absolue maximale ; égalités de coordonnées départagées par le plus petit indice.
- Bloc ambigu si des écarts de valeurs propres sont <= une tolérance numérique prédéclarée. Exemple fourni par le chercheur : 64 * eps * max(1, lambda_max) en float64. Le plan technique doit fixer explicitement sa valeur ; aucun choix fondé sur les sorties.
- Si aucune base canonique reproductible justifiée n'est disponible dans un tel bloc : refuser la cellule avec EIGENVALUE_TIE_UNRESOLVED. Ne pas choisir une orientation arbitraire.
- Témoins explicites : covariance à valeurs propres répétées, classement stable et invariance aux signes. Aucun départage numérique ne vaut identification statistique d'axes individuels dans un sous-espace dégénéré.

## Qualification et contrôle analytique D

Pente locale de log-RMST sur la grille fixée ; ni ADD de Lorden ni exposant universel. Conserver Delta = Delta_1 + Delta_2 comme décomposition descriptive sans attribution causale. Une différence de FPR reste visible ; aucun masquage pour obtenir une pente favorable.

Avant exécution, vérifier analytiquement la détectabilité plausible du dictionnaire à grand N à l'amplitude I* fixée, indépendamment des résultats de simulation. Ne pas adapter I* après observation des performances.

## Autorisation E et portes restantes

Le chercheur autorise maintenant : mise à jour tracée du protocole ; plan d'implémentation distinct soumis à revue technique Codex ; préparation des tests RED/GREEN, non-fuite, identité et appariement ; puis, **après validation du plan et GO technique séparé**, implémentation et pilote strictement de coût CPU/mémoire, sans exploiter ses performances de détection pour ajuster les choix scientifiques. Le cycle Claude Code reste interactif : plan, revue, GO distinct, implémentation, tests et clôture.

**Campagne scientifique full E4 NON AUTORISÉE.** Après tests et pilote, remettre au chercheur coût prévisionnel, risque de censure et protocole effectivement figé, puis obtenir son GO d'exécution. Aucun accès aux données financières réelles, aucune activation J4, aucun entraînement JEPA/VAE, aucun changement aux résultats PCA full 2000 ou scellés E2/E3.
