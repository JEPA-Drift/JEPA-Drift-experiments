# NO-GO technique — plan E4 v0, 19-e4-code-20261112

Base ef48fa299c9d3ca6c32022dc5af2e509df903c55. Plan natif de 247 lignes, SHA-256 57d95420db59721d3f0a7a01647712bc9ab510ffab21e644a7941266dd404d7c.

Le chercheur a autorisé explicitement la transmission de la réponse proposée, SHA-256 36ef245a9365dd3eadaa26811bf21f6537f8dc94e64cf5f72bb79b7fafbd0cc9, puis le retour à la procédure habituelle. Cette revue demande une révision du plan et ne vaut pas GO technique. Même session Claude, UUID 4da0c70c-efef-4647-8f66-9252acfb9078, Opus 5.5 Max.

## Réponse approuvée, conservée comme trace

Plan reçu. **Je demande une révision ciblée avant GO technique.** Le GO scientifique conditionnel reste inchangé ; aucune implémentation, aucun pilote et aucune campagne full ne sont encore autorisés par cette revue.

## Arbitrages techniques proposés pour Q1–Q5

- **Q1(a)** : calibration scalaire directe par signes nuls indépendants. Tirer B ~ Bernoulli(1/2), puis transmettre **2B−1** au même `log_edetector(..., "cusum")`, avec les mêmes huit mises signées et la même règle de franchissement. Un seul seuil commun à EW/O-dir/O-score1, tous N et fonds ; aucune trajectoire réutilisée dans holdout ou alternative.
- **Q2(a)** : refuser les quatre méthodes dépendantes d'une base ambiguë pour le couple (fond, N), conserver EW/O-dir et toutes les lignes de statut. Aucun sous-ensemble de N choisi pour sauver une pente.
- **Q3(a)** : nouvelles entrées de `DEVIATIONS.md` en français, conformément aux instructions actuelles du projet. L'ancien GO 17 ne remplace pas cette règle.
- **Q4(a)** : implémenter et tester maintenant l'analyse sur tableaux factices. Son coût peut être mesuré sur une fixture explicitement COST_FIXTURE ; aucune analyse des performances du pilote.
- **Q5(a)** : GE au seuil `nextafter(b,+inf)` en espace log, sans aller-retour exp/log. La réutilisation de `pdb.rank_threshold` et le maintien du code scellé conviennent.

Je retiens la convention spectrale locale avec tolérance `64 * eps_float64 * max(1, lambda_max)`, le maintien de `eigh_desc` historique, l'adaptateur local de chemins log et le refus de `--mode full`. Il reste les corrections suivantes à intégrer au plan natif avant tout GO technique.

## 1. Corriger la forme et la convention des jours d'alarme

Deux incompatibilités sont présentes dans D3/D4 et les interfaces :

- D4 transmet un chemin `(H,)` à `pdb.first_index`, alors que `experiments/pca_drift_benchmark.py:842-844` utilise `axis=1` et attend une matrice. Pour une API scalaire, l'adaptation minimale est `int(pdb.first_index((log_m >= h)[None, :])[0])`. Ne pas modifier le helper scellé.
- D3 utilise directement `eprocess.first_alarm`, qui renvoie un **offset 0..H−1**, ou −1 (`eprocess.py:122-125`). `_rmst_fields` attend des **jours 1..H**, ou −1 (`pca_drift_benchmark.py:1147-1157`). Sans conversion, une alarme au premier jour deviendrait censurée et les autres délais seraient raccourcis d'un jour.

Fixer un contrat unique `first_hit ∈ {1,…,H} ∪ {−1}` pour les deux lectures. Convertir les offsets secondaires par `offset + 1` quand ils sont >= 0, conserver −1 sinon. Ajouter les témoins littéraux : alarme au jour 1, au jour H et absence d'alarme, pour chaque lecture. Le temps censuré d'une absence d'alarme vaut H.

Unifier aussi la signature de `log_path` : D3 écrit `log_path(spec, x)`, tandis que la section Interfaces décrit `log_path(method, spec, state, X, rec)`. Si ce sont deux fonctions distinctes, leur donner deux noms et préciser leur lien.

## 2. Rendre cohérents manifeste, identité et reprise des partitions

D5 refuse tout manifeste existant, mais D6 donne quatorze commandes vers le même `--out` et annonce une reprise. Ces règles ne définissent pas comment la deuxième invocation peut fonctionner. De plus, une empreinte globale incluant toutes les bases et calibrations réalisées ne peut pas être disponible avant le calcul des premières partitions ; le pilote ne doit pas produire de seuils scientifiques pour la construire.

Décrire une organisation minimale, sans framework supplémentaire : identité immuable de la session de calcul (configuration, code, environnement, domaines de graines et mode), emplacement et identité de chaque partition, puis hashes des objets réalisés lorsque le stade les produit effectivement. Séparer le pilote des fixtures scientifiques et d'une éventuelle campagne future.

Préciser les cas : sortie nouvelle ; continuation d'identité identique ; partition déjà achevée ; partition incomplète ; identité divergente. Une continuation autorisée ne doit ni échouer simplement parce que son manifeste existe, ni écraser une partition achevée. Un hash divergent doit être refusé avant écriture. Les sorties doivent être finalisées atomiquement ; une partition incomplète ne vaut pas succès.

Ajouter des témoins exécutables de deux partitions successives dans le même espace de sortie, d'une reprise sans recalcul d'une partition achevée, et d'une divergence refusée sans mutation. Les commandes du plan doivent employer exactement cette convention de reprise.

## 3. Définir le coût réellement mesuré et la prévision

Le facteur 50 ne s'applique qu'aux tâches réellement linéaires dans le nombre de trajectoires. Donner la correspondance entre chaque poste mesuré et son nombre futur d'exécutions : génération, projections/flux, noyaux de surveillance des six méthodes, calibrations, comparaison des deux lectures, analyse, IO et reprise.

Compter la calibration scalaire commune une seule fois, les calibrations des dictionnaires par cellule et le coût total du fit de chaque cellule une seule fois. Si `fit_cell` appelle plusieurs routines de fit pour fabriquer ses états, mesurer leur coût complet ; ne pas le confondre avec celui d'un unique appel à `pdb.fit_basis`. Les deux lectures peuvent réutiliser un chemin log, sans facturer deux fois son calcul.

Le bootstrap COST_FIXTURE doit avoir des dimensions et un facteur d'extrapolation déclarés : une mesure déjà faite aux dimensions finales ne doit pas être multipliée de nouveau par 50. Nommer les coûts non mesurés comme tels et garder la prévision `ESTIMATE`, avec ses hypothèses. Présenter aussi le coût du pilote déjà consommé et sa relation au plafond global de 24 CPU-heures ; aucune absence de mesure ne vaut un coût nul.

## 4. Préciser les mesures et limites de ressources

Pour ce premier pilote, je propose **jobs=1 imposé** ; les témoins de reproductibilité jobs=3 restent limités aux fixtures. Cela évite de prétendre mesurer la mémoire simultanée de plusieurs processus avec `ru_maxrss`.

Définir `cpu_s` comme temps CPU utilisateur + système, distinct du temps mural. `ru_maxrss` est un maximum cumulé du processus, pas une consommation de stade obtenue en soustrayant deux pics. `RUSAGE_CHILDREN` ne mesure pas en continu les travailleurs encore actifs ; additionner des pics parent/enfants ne donne pas un pic simultané. Déclarer la portée réelle de `peak_rss_kib`. Toute prévision parallèle ultérieure reste une hypothèse explicitée, pas une mesure de ce pilote sériel.

Indiquer où les limites sont contrôlées : avant les allocations importantes et entre blocs bornés, avec une échéance effective par invocation. Un contrôle uniquement en fin de partition ne borne pas une opération déjà en dépassement.

En cas de BLOCKED_RESOURCE, conserver les mesures achevées et signaler les cellules non mesurées. « Sauter les N plus grands » ne doit pas modifier silencieusement la grille scientifique ni produire une prévision complète artificielle. Les seuls replis scientifiques restent ceux approuvés, dans leur ordre ; une mesure manquante reste inconnue ou conduit au STOP.

## 5. Ajouter les témoins numériques de l'analyse approuvée

Q4(a) exige des témoins explicites au-delà de l'interface `analyse` :

- Avec H=5 et `first_hit=[1,5,-1]`, temps censurés `[1,5,5]`, RMST `11/3`, taux de détection `2/3`, deff=1 et erreur standard `4/3`.
- Rééchantillonnage commun des indices de réplicats pour tous les N et toutes les méthodes ; identité descriptive Delta = Delta_1 + Delta_2.
- Pente sur la grille entière, labels et absence de sélection d'un sous-ensemble ; cellule refusée => contraste NOT_IDENTIFIED selon la règle annoncée.
- Qualification Wilson de faible censure et comparabilité appariée des FPR dans ±0,01 ; échec de qualification visible sans suppression de cellule ni attribution causale.

La borne « n <= 40 » convient aux petites simulations, mais pas à tous ces témoins d'analyse : même 40 succès sur 40 donnent une borne inférieure Wilson 95 % inférieure à 0,95. Autoriser des tableaux d'alarmes factices plus grands, par exemple 80 réplicats, sans générer de trajectoires, pour exercer aussi la branche qualifiée. Conserver les intervalles conditionnels au fit et à la calibration. `_rmst_fields` fournit déjà deff=1 ; il n'est pas nécessaire de réécrire ce calcul.

## 6. Lier les hashes à la base effectivement utilisée et compléter la trace FAIR

Après orientation E4, recalculer le hash des eigen-paires réellement utilisées. Le `basis_hash` renvoyé initialement par `pdb.fit_basis` décrit sa convention historique ; le garder sans distinction après changement de signe serait une provenance ambiguë. Vérifier que les états PCA et DegreeZero proviennent des mêmes lignes de fit et sont cohérents avec la base canonique ; normaliser une seule fois le sous-panel contigu si nécessaire.

`pdb.check_env()` renvoie une liste de problèmes, pas une description complète de l'environnement. Séparer la validation de l'environnement de l'instantané haché : versions pertinentes, BLAS et variables déterministes. Les nombres de workers, temps et RSS ne doivent pas faire varier l'identité des CSV scientifiques destinés à la comparaison jobs=1/3.

Utiliser `save_fair_csv` et conserver un SHA-256 complet des fichiers produits. Toute lecture CSV destinée au contrôle d'identité doit employer `float_precision="round_trip"` ; garder `float.hex` pour le seuil de rang dans le manifeste.

## 7. Encadrer l'adaptateur et les sorties du pilote

L'adaptateur local réutilisant les constructeurs de flux du registre et les noyaux existants convient pour garder les maxima en espace log. Déclarer explicitement sa dérogation limitée à l'usage direct de `run_pipeline`, avec ses tests d'équivalence et ses labels de lecture. Elle ne doit ni changer le registre partagé ni devenir un nouveau runner générique.

Le contrôle des sorties du pilote doit porter sur les fichiers et leurs schémas effectifs, pas seulement sur une recherche de mots dans un journal. Les identités de code/configuration, statuts de ressource et informations de coût peuvent contenir des mots techniques légitimes ; ils ne doivent pas être confondus avec des résultats de détection. Interdire toute persistance de trajectoire ou de métrique de performance du pilote, y compris dans les partitions de reprise. Des assertions sur les champs et fichiers effectivement écrits sont nécessaires.

Après ces corrections : fournir une révision native ciblée, au plus 300 lignes, et son SHA-256. Ne pas recommencer une exploration générale et ne pas produire de code, test, configuration, pilote ou mutation Git. Le chercheur recevra cette révision et la prochaine réponse proposée de Codex avant tout nouvel envoi. Attendre en mode plan ; aucun GO technique n'est implicite.

## Instruction ultérieure du chercheur — prévalence

La phrase de fin de la réponse archivée imposant de présenter chaque révision et chaque réponse au chercheur appartient à l'exception temporaire, maintenant levée explicitement. Codex reprend la revue technique et peut émettre le GO technique séparé sans nouvelle confirmation du chercheur. La limite de deux sessions Claude est conservée. La campagne full reste interdite jusqu'au GO d'exécution scientifique distinct après tests et pilote de coût.

