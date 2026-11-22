# NOTIFICATION À CODEX — Stream 32 : revue contradictoire du plan natif v1 et corrections avant GO

**Décision du chercheur — 14 novembre 2026.** Je conserve **PCA-INFO-ONLINE comme priorité scientifique P0** après la clôture du stream 23. Le plan natif `pasted-content-id-9c4b-mission-polymorphic-scott.md` (540 lignes, 14 novembre 2026) est une base satisfaisante, mais **n'est pas approuvé en l'état pour le GO d'implémentation**. Traite les observations ci-dessous **avant** de figer `prompts/plans/plan-32.md` et d'autoriser les lots R/A/B.

Révise **dans la session Claude Code déjà ouverte**, par plan natif v2 puis revue Codex ; ne recommence pas l'architecture et ne lance aucun pilote/full sur ce message. Ne modifie aucun artefact E4, PCA `/2`, J1 ou E3 scellé. La priorité est une **comparaison scientifique déployable sans oracle**, pas un certificat forcé de gain.

## A. Corrections bloquantes

### A1 — INVARIANCE DE CALIBRATION NON-ORACLE AUX FAMILLES DE DRIFT [CRITICAL]

Le plan §5 introduit `family_oracle`, `mask_law_id` et des clés de scénario dans l'identité de calibration. **Démontrer** si `ONLINE_*`, `FIXED_PREFIX_*`, `FIXED_EXANTE_QBAR_*`, `FULL_K`, `CPV90` utilisent ou non la famille F0/F1/F2 pour déterminer un seuil ou une politique.

**Règle à imposer :** pour un `(arm, N, fit, eligible_universe, policy, cost, window, s2, H, alpha)` donné, la procédure opérationnelle sans oracle, **son jeu CAL_NULL et son seuil h sont identiques pour les alternatives F0, F1 et F2**. Le sélecteur n'a accès ni à la famille d'injection, ni à `Δ`, ni à `tau*`. `family_id` peut apparaître sur les lignes de test et dans les diagnostics après l'alarme, mais **pas comme entrée de décision ni dans l'identité du seuil non-oracle**. L'appartenance à l'univers marché ou résiduel est un choix explicite de l'application ; ne pas faire choisir cet univers par une étiquette alternative cachée.

Les ORACLE peuvent utiliser une loi de métadonnées par famille, uniquement avec la mention `NON_DEPLOYABLE_ORACLE_CALIBRATION`; garder leur FPR distincts. Ne jamais masquer cette asymétrie dans un gain comparatif.

**Tests bloquants :** (i) mêmes observations et même setup mais permutation des noms de familles ⇒ mêmes `S_t`, `h`, `T` pour les non-oracles ; (ii) le même `calibration_id` doit être réutilisé pour les F0/F1/F2 au même setup ; (iii) aucune métadonnée oracle dans la chaîne de dépendance des non-oracles.

### A2 — ÉVITER UNE GRILLE CONFIRMATOIRE CONSTRUITE SEULEMENT CONTRE LE PRÉFIXE [IMPORTANT]

Le plan §4 donne F1 sur les quatre axes résiduels de queue et F2 sur `{3,9,17,21}` : ces familles sont volontairement défavorables au préfixe. Ajouter **un contrôle `F_HEAD_RESIDUAL`**, centré sur PC2–PC5, à même information gaussienne `I*`; conserver `F0_ISOTROPIC_RESIDUAL` comme contrôle négatif de concentration a priori. Pré-enregistrer supports, poids, signes et amplitudes **sans lire les résultats ALT**. Dans le bras FITTED, les dérives restent définies dans le repère population et les informations jointes atteintes sont diagnostiquées.

Ne pas revendiquer de supériorité « générale » si le gain ne tient que sur F1/F2. Les comparaisons sur F_HEAD doivent indiquer si INFO se comporte correctement lorsque le préfixe est déjà informatif. Pour un protocole équilibré, choisir une cellule primaire favorable à INFO et une cellule contrôle favorable au préfixe, les autres exploratoires ou confirmatoires secondaires. **Codex doit figer le choix de la famille confirmatoire et sa correction de multiplicité avant le pilote de puissance utilisé pour la sélection.**

### A3 — PORTE STATISTIQUE ET TAILLES : NE PAS REPRODUIRE L'IMPASSE E4 [IMPORTANT]

Le plan §6 cumule : (i) borne Clopper–Pearson supérieure 95 % de FPR HOLDOUT ≤0.06, (ii) TOST apparié ±1 point de pourcentage, (iii) borne de gain RMST, puis (iv) succès des **six** contrastes pour ouvrir la famille 2. La conjonction risque de produire un projet déclaré inconclusif malgré une estimation utilisable.

**Contrôle quantitatif :** à n=2000 trajectoires nulles indépendantes et vrai FPR=0.05, le critère CP supérieur ≤0.06 n'est franchi que dans environ **60.7 %** des répétitions de l'évaluation HOLDOUT. Ne pas appeler FAIL un moniteur correctement calibré qui échoue par bruit d'échantillonnage. Le TOST à ±1 pp peut aussi requérir nettement plus de 2000 nulls selon la discordance appariée.

Proposer une stratégie échantillonnale **fondée uniquement sur l'information nulle** : conserver la garantie marginale de calibration par rang sous échangeabilité ; rapporter FPR HOLDOUT et IC comme contrôles indépendants ; distinguer `NULL_VALIDATED`, `NULL_INCONCLUSIVE` et `NULL_FAILED` selon une règle pré-enregistrée. Calculer à partir des discordances nulles un budget `n_holdout` suffisant pour l'équivalence, sans consulter ALT. La marge ±0.01 reste un objectif strict, mais ne doit pas être confondue avec la garantie marginale de la calibration. Ne pas exiger automatiquement que six cellules toutes significatives débloquent tout contrôle FULL_K : établir un critère confirmatoire scientifique concentré et un reporting honnête des six cellules.

Vérifier numériquement la formule de Tango et ses cas limites (b=c=0, zéro discordance unilatérale, symétrie b/c) contre une maximisation de vraisemblance contrainte ; ne pas remplacer un calcul non vérifié par un résultat présenté comme exact.

## B. Corrections scientifiques et de comparabilité

### B1 — COHÉRENCE DU COÛT M AVEC LE DÉTECTEUR RÉEL [IMPORTANT]

Le plan §2.6 reconnaît `s2=2log(H/alpha)/(HK)`, alors que la dérivation du coût fluide `M(d,gamma_M)` suppose un prior de moyenne apparié à la véritable information dans `d` coordonnées. Avec `H=250, alpha=.05, K=20, I*=.25`, ce choix produit `s2≈0.0034069`, contre `2I*/d=0.5/d`, soit un décalage d'environ **7.3× pour d=20 et 73× pour d=2** si toute l'information était retenue.

Ce décalage **n'invalide pas le scan ni la calibration**, mais empêche d'interpréter `I/M` comme une prédiction exacte du délai de ce détecteur. Préserver le `s2` commun pour une comparaison causale contrôlée, **et** ajouter au minimum un diagnostic/sensibilité préenregistré de prior fixe `s2` choisi sur DEVELOPMENT **sans fuite ALT** ; mesurer la corrélation/rang entre valeur théorique `V` et RMST observé. Ne pas choisir `s2` à partir du test ou adapter rétroactivement un prior de segment. Examiner la cohérence de `gamma_M=504` avec le niveau opérationnel `H/alpha=5000` (`H=250`) ; garder 504 comme choix historique si nécessaire mais l'étiqueter **proxy analytique** et proposer une sensibilité `gamma_M=H/alpha`, gelée avant ALT.

### B2 — BASELINES SPECTRALES ET NOMENCLATURE [IMPORTANT]

`FIXED_PREFIX_KAISER_E` du §4 utilise `lambda_k >= mean_E(lambda)`. Ce **n'est pas la règle classique de Kaiser** (valeurs propres >1 d'une matrice de corrélation standardisée). Renommer `FIXED_EIGENMEAN_PREFIX` et décrire sa définition. Conserver `CPV90` sur le spectre complet avec `OUTSIDE_UNIVERSE` sans l'altérer, **mais ajouter `RESIDUAL_CPV90`** : 90 % de la variance *au sein du seul univers résiduel*, explicitement distinct du CPV90 global. En contrôle fort supplémentaire, proposer un préfixe de dimension `d` choisi sur DEVELOPMENT parmi `{1,2,4,8,16,20}` (selon K), sans jamais sélectionner `d` sur TEST_ALT. C'est indispensable pour ne pas comparer INFO à une baseline artificiellement faible.

### B3 — LIBELLÉ ORACLE DANS LE BRAS FITTED ET RISQUE DE COÛT DE RECHERCHE [IMPORTANT]

Dans `FITTED_LW_GAUSSIAN`, `Σ_k q_k` n'est qu'un **surrogate diagonal**, non la KL jointe lorsque la base estimée ne diagonalise pas exactement `Σ0`. `ORACLE_INFO_*` y désigne un oracle sur les `q_k` du surrogate et **non** le véritable optimum sur tous les sous-espaces pour la KL jointe. Étiqueter explicitement ces deux notions, conserver le diagnostic `I_joint(S)`, et interdire une revendication de « KL optimale » hors du bras EXACT.

**Contrôle FITTED sous H0 :** le plan §2.7 reconnaît un biais de centre `c`, mais la correction `−1/m_t` suppose aussi une variance nulle effectivement égale à 1. Sous une covariance LW estimée, `Var0(y_k)` peut différer de 1. Par conséquent, avant écrêtage et sous absence de drift, `E[bhat_k² − 1/m_t] = c_k² + (Var0(y_k)−1)/m_t`. Ajouter un test analytique et un diagnostic de sélection anormale des axes sous H0 ; toute correction via un échantillon nul additionnel doit être apprise **avant le test**, sur un rôle indépendant, et faire l'objet d'une ablation étiquetée (ne pas injecter les vrais `c` ou `Cov0` du simulateur dans `ONLINE_*`).

Par ailleurs, `M(d,gamma_M)` ne pénalise que la dimension du mélange **fixe** : il n'intègre pas l'erreur d'estimation ni les recherches répétées sur K axes. Rapporter le coût additionnel de la sélection online, les commutations, l'évolution de `d_t`, l'alignement avec l'oracle et le seuil empirique propre à la politique. Ne pas attribuer à `M` une garantie d'optimalité RMST pour le pipeline adaptatif.

## C. Ingénierie et livraison

- Conserver le protocole plan → revue contradictoire Codex → **GO technique écrit distinct** → lots R/A/B → tests → **GO pilote scientifique distinct** → éventuel GO full. Pas de full automatique ; pas de données réelles/2020+, JEPA/J4 ni extension covariance.
- Les 5–50 ns par mise à jour de la section 10 restent une **hypothèse non mesurée** ; aucun budget scientifique fondé exclusivement dessus. Profil réel 1/4/8/12 workers après libération du verrou, BLAS à 1 thread/worker ; sécurité RAM et disque.
- Le lot R peut ajuster le titre et synchroniser le master par l'outil canonique, **sans changer silencieusement les contrats scientifiques du prompt 32**. Le plan amendé doit identifier tout écart à la spec et la décision d'autorité Codex ; préserver les SHA historiques et publier les nouveaux.
- Les deux fichiers sources externes signalés `REFERENCE_NOT_MOUNTED` ne sont pas des blocages s'ils restent non nécessaires aux équations autonomes de la spec ; ne pas prétendre les avoir lus localement.
- Lire `CLAUDE.md` pour l'emplacement exact des modules ; 4 fichiers au lieu de 6 est acceptable si les noyaux ont des tests séparés et une interface réutilisable.

## Livrable demandé à Codex, immédiatement après revue

Produis et communique :
1. Un **tableau de disposition** A1–A3, B1–B3 : `ACCEPTED / MODIFIED / REJECTED` + justification technique, fichier/ligne et test de non-régression proposé ;
2. Le plan natif **v2** (ou un amendement versionné au plan v1) et `prompts/plans/plan-32.md` réconcilié sur le `main` local réel après le stream 23 ;
3. Les nouveaux statuts de GO **sans lancer le code tant que les portes de revue ne sont pas franchies** ;
4. Le protocole final de calibration non-oracle, le jeu de familles équilibré, la famille confirmatoire, et le dimensionnement HOLDOUT à partir des seuls nulls ;
5. Les limites conservées : divergence entre coût fluide et délai réel, estimateur `qhat` bruité, fit conditionnel, censure, et comparabilité FPR.

**Décision provisoire du chercheur : PLAN v1 À RÉVISER ; GO technique non accordé par cette notification.** Pas de changement de priorité : terminer stream 23 puis engager stream 32 dès que les préconditions sont réunies.
