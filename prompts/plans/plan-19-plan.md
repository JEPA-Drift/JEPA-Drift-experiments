# Plan 19-plan — N, k, d et référence primaire SPLL

## Autorité, provenance et statut

- Mandat : demande du 7 novembre 2026, puis « continue ». Planification théorique et audit bibliographique seulement.
- Base : `1440927b49463c13bdd0c819fcd73f30d6a32c31` ; branche `stream-19-plan`, worktree `~/JEPA-stream-19-plan`.
- Instance : session interactive `jepa-s19-plan`, Claude Opus 5.5, effort Max, mode plan, sans Agent/Task ni délégation.
- Proposition native initiale : 559 lignes, SHA-256 `05ff2c7f0c18bd7518382aa7278bd9951a850497f6ddd1f9e12d227976065d8d`.
- Révision native après revue Codex : `~/.claude/plans/pasted-content-id-f9d7-cadrage-merry-cocke.md`, 698 lignes, SHA-256 final `352e4be46f14f1b35c471bbccb974a9bfac8897f5228eafe6dd69ec9c3971883`. Le relevé précédent `193c2223…` différait seulement par le classement de la réserve sur le transfert des AUC ; ce dernier diff a été relu.
- Ce plan consolidé par Codex retient le périmètre utile et corrige notamment la dimension des canaux P3-C. La proposition native reste une pièce de travail ; le présent fichier fait référence pour toute reprise.
- GO documentaire accordé par le chercheur le 7 novembre 2026 : `prompts/GO-stream-19-plan.md`. Aucun code scientifique, calcul, campagne ou entraînement. Les GO des lots 19 et 19-oracle clos ne sont pas réutilisés.

## 1. Sources et limites de la lecture

Sources du dépôt : `CLAUDE.md`, amorçage du 7 novembre, prompt 19, audit `stream_19_replan_2026_11_06.md`, plans/GO/wrapups 19 et 19-oracle, `experiments/e4_oracle_reference.py`, ses tests et sa note, `paper/sec3_theory.tex`, bibliographie, schéma PCA et déviations pertinentes.

La revue Codex ajoute une lecture textuelle de `jepadrift/pipelines.py` (`DEFAULTS`, `_columns`, `_stream_signs`, `_detect_p3c`), de `experiments/e1_problem.py::subset_ctx` et de `docs/sections/interface_Z.md`. Aucun module n'a été importé ou exécuté.

Les deux articles primaires ont été lus dans les PDF de l'éditeur hébergés par l'autrice. Les copies restent dans le cache natif, hors dépôt.

| Référence | URL primaire | SHA-256 du PDF lu |
|---|---|---|
| Kuncheva, 2013, *Change Detection in Streaming Multivariate Data Using Likelihood Detectors*, IEEE TKDE 25(5), 1175–1180, DOI `10.1109/TKDE.2011.226` | https://lucykuncheva.co.uk/papers/lktkde13a.pdf | `74acaba9eb8fdd1cd43dffdeafa37f872292ad2d05828aef6936c528adc6a052` |
| Kuncheva et Faithfull, 2014, *PCA Feature Extraction for Change Detection in Multidimensional Unlabeled Data*, IEEE TNNLS 25(1), 69–80, DOI `10.1109/TNNLS.2013.2248094` | https://lucykuncheva.co.uk/papers/lkwfTNNLS14.pdf | `52c776175d8e85c68066355bbeb4ad9d71d23bf3c822a46652d5409793797112` |

L'identité bibliographique de TKDE concorde avec la notice institutionnelle de Bangor. Le code de l'autrice, ses choix de covariance/singularité et les éventuels errata n'ont pas été audités ; ils restent des prérequis ouverts avant tout portage. Aucune AUC publiée n'est recalculée ou transférée aux rendements.

## 2. N, k, d : objets distincts

| Symbole | Objet | Domaine et réserve |
|---|---|---|
| N | actifs, dimension du vecteur de rendements | N ≥ 1 dans l'oracle |
| k | réservoir spectral candidat P_k | préfixe d'une base gelée ; k ≤ N |
| S, d | axes retenus et dimension de ce sous-espace | S inclus dans P_k, 1 ≤ d ≤ k |
| p | dimension du flux d'un détecteur du benchmark | d pour MEAN ; d(d+1)/2 pour COV, sans rendre ce flux gaussien par définition |
| D | dimension du bloc auquel un coût M(D,γ) est appliqué | ne pas confondre bloc résiduel et combinaison des canaux ; les hypothèses du coût restent à vérifier |
| K_MP | nombre de facteurs résiduels retenus au bord MP, n_above_edge − 1 | PC1 est séparé ; le mode factoriel exige K_MP ≥ 1 ; ce K n'est ni k ni le nombre de clusters SPLL |
| m | nombre de composantes dans la queue de faible variance | fonction du spectre et de la règle de sélection ; aucune valeur recalculée |

Le full scellé fixe N = 239 et compare k et d ; il ne mesure pas une pente en N. L'oracle clos ne contient ni préfixe estimé ni détecteur : il fournit I_N pour une translation de marché et une covariance connues. Aucun rapport universel N/d/k n'est défini par ces deux objets.

### PC1 et dimensions réellement surveillées

- La représentation PCA expose PC1 en colonne 0 dans tous ses modes, y compris `tail10`.
- P3-C a `channels="all"` par défaut. `_columns` inclut alors marché et résiduel : K_MP + 1 coordonnées en mode factoriel, N en mode full.
- `subset_ctx` d'E1 crée P3-C/full sans remplacer ce défaut. Il ne faut donc pas décrire tout ce pipeline comme un détecteur de N − 1 seules coordonnées résiduelles.
- Dans la variante avec mélange, `_detect_p3c` sépare marché et résiduel puis moyenne leurs e-détecteurs. Le coût d'un mélange sur le seul résiduel n'est pas automatiquement celui de la combinaison entière.
- P3-KF est spécifié sur le seul bloc de queue de dimension m. Sa statistique n'est pas implémentée ; sa représentation conserve néanmoins le canal marché. L'information nulle d'un bloc orthogonal au marché ne s'étend pas au pipeline P3-C complet.

## 3. Énoncés analytiques à retenir

### Oracle gaussien connu

Id désigne l'identité N × N, 1 le vecteur des uns et δ l'amplitude commune par actif. Sous Σ_N = ρ11ᵀ + (1−ρ)Id, Δμ = δ1, N ≥ 1, 0 ≤ ρ < 1 et δ > 0 :

- I_1 = δ²/2 et I_N = δ²N / [2(1+(N−1)ρ)], en nats par observation ; G(N) = I_N/I_1 = N/[1+(N−1)ρ].
- deff_N = 1+(N−1)ρ est ici N fois la variance de la moyenne équipondérée, les variances individuelles étant unitaires. Ainsi G(N) = N/deff_N. Le rapport N/T, avec T lignes d'ajustement, décrit un régime d'estimation ; il n'est pas cette loi de KL.
- À ρ > 0 fixé, G tend vers 1/ρ ; à ρ = 0, G = N sans plafond fini.
- Le pool équipondéré est suffisant pour ce changement. Toute projection contenant la direction 1 conserve I_N ; toute projection explicitement dans 1-perp porte une information nulle.
- Pour ρ > 0, PC1 de population est la direction marché : un préfixe qui la contient conserve I_N même si l'ordre du bulk est dégénéré.
- À ρ = 0, PC1 n'est pas identifié. Une queue ou un résiduel d'ACP arbitraire/estimée n'est pas nécessairement orthogonal à 1. En base estimée, aucune fuite de signal n'est quantifiée ici.

Cas limites : N = 1 n'a pas de résiduel et Σ_1 = [1] ; d = 0 n'a pas de flux ; pour N ≥ 2, ρ = 1 est singulier, et cette valeur est hors du domaine uniforme de l'oracle ; δ = 0 rend le gain relatif indéfini. Les projections complètes inversibles conservent la KL. Ces résultats n'augmentent jamais l'information par transformation.

### Rétention, dimension et alignement

Pour un mélange isotrope de moyenne dans un sous-espace déclaré S, poser r(S) = I(S)/I_N. M(d,γ) est le multiplicateur fluide du mélange à prior apparié, avec γ > 1 sur l'échelle e. Le critère fluide est T_fl(S) = M(d,γ) ln(γ)/I(S). Contre une référence scalaire à direction connue, son gain se décompose en G(N) r(S)/M(d,γ). Il ne s'agit pas d'un ratio d'ADD mesuré ou exact.

Contre le plein espace, le critère fluide favorise S si r(S) > M(d,γ)/M(N,γ). L'expression racine(d/N) n'est qu'une approximation lorsque d et N sont grands devant ln(γ). Pour les dictionnaires, la dimension seule ne suffit pas : le nombre d'atomes et l'alignement interviennent. Pour un pipeline à plusieurs blocs, sa règle de combinaison doit aussi être déclarée.

### Amplitude et espérance

- Une dérive de marché à amplitude par titre fixe a une information d'ordre constant pour ρ > 0 fixé, mais d'ordre N à ρ = 0.
- Pour une largeur de second moment isotrope, un budget de norme totale fixé et une amplitude RMS par actif fixée ne donnent pas le même exposant d'information : respectivement 0 et 1 à ρ fixé.
- Dans le bulk équicorrélé, la fraction m/(N−1) décrit le rapport d'espérances sous le prior déclaré, pas la rétention de chaque dérive. Une dérive réalisée peut être concentrée dans la queue ou lui être orthogonale, même si le bulk est plat.
- Les lois N^(a−b/2), avec I(N) d'ordre N^a et D(N) d'ordre N^b, restent conditionnelles à la convention d'amplitude, à l'alignement et au critère fluide. Elles ne sont pas des pentes mesurées.
- Les espérances de rétention d'une ACP estimée à ρ = 0 demandent une règle orthogonalement équivariante, avec départage explicite des multiplicités. Aucune propriété universelle de l'algorithme numérique n'est postulée.

### Lectures de délai

Séparer le budget ln(γ)/I, les garanties anytime-valid d'un e-détecteur, la lecture dite exact à ARL0 calibré et les approximations fluides. Les formules de délai gaussiennes de `floors`, y compris celles avec correction de Siegmund, ne deviennent pas des ADD exacts à pas fini. La formule Φ(γI)/I est une approximation de diffusion. L'oracle de KL ne fournit à lui seul ni ADD, ni ARL0, ni FPR(H).

## 4. Audit primaire SPLL

### Kuncheva 2013

La source TKDE introduit SPLL comme critère entre deux fenêtres données (§1–2.3, p. 1175–1177). Elle remplace une vraisemblance de mélange par une majoration, puis utilise une moyenne de distances quadratiques de Mahalanobis aux centres les plus proches, avec covariance commune estimée après k-means. Ce critère n'est pas un rapport de vraisemblance séquentiel garanti. Les expériences comparent des ROC/AUC sur des paires de fenêtres ; elles ne donnent ni procédure temporelle complète ni garantie de FPR(H)/ARL0. Les choix exacts de covariance et de traitement des singularités restent à vérifier dans le code auteur avant portage.

### Kuncheva et Faithfull 2014

La source TNNLS ajoute la variante qui prend le maximum des deux sens de comparaison et étudie l'ACP de faible variance (§III.A et IV.B, p. 73–75). La règle de queue écarte un préfixe expliquant une part déclarée de variance ; elle ne retient pas une proportion fixe du nombre de composantes. L'application aux données standardisées et à l'ACP de référence de l'article diffère de la covariance LW de calibration du projet. Le choix d'un seuil séquentiel reste distinct de leurs comparaisons ROC/AUC.

### Conséquences de la revue mathématique

- Avec plusieurs centres, une distance au centre le plus proche ne suit pas en général la loi d'une distance au centre générateur. La référence chi-deux ne peut pas servir de garantie de calibration ; l'estimation ajoute une autre difficulté.
- Dans l'idéalisation à une composante, paramètres connus et observations gaussiennes i.i.d., une comparaison de décalages de moyenne normalisés sous H0 ne suffit pas à établir une domination de puissance : les quantiles et variances sous l'alternative diffèrent.
- Pour des centres et une matrice commune définie positive gelés, la fonction de distance minimale est paire si et seulement si l'ensemble des centres est symétrique. Sur un panneau donné, un aléa de signe exige aussi des lignes dont le score change sous réflexion. Réajustement et comparaison bidirectionnelle ne garantissent pas cet aléa dans toute configuration.
- Même un aléa de signe non dégénéré ne résout ni la réutilisation in-sample ni le recouvrement des fenêtres historiques. Aucune calibration D6 n'est déduite de cette seule propriété.

Les variantes unidirectionnelle et bidirectionnelle doivent être distinguées. Un comparateur financier fondé sur les mêmes idées sera une adaptation explicitement tracée, sans prétendre reproduire le protocole original.

## 5. Question future et hypothèses de travail

Question retenue pour une future note : sous covariance, amplitude et règle de projection déclarées, comment se séparent le gain d'information en N, la rétention r(S), le coût de dimension et l'alignement ? La référence de marché ci-dessus est immédiatement exploitable sur papier ; les bases estimées, les priors de largeur et les détecteurs combinés demandent leurs hypothèses propres.

Défauts de conception : une seule note d'audit, modèle équicorrélé d'abord, maintien de l'identifiant P3-KF avec le qualificatif d'adaptation. Aucun modèle spectral supplémentaire, aucune extension de l'oracle, aucun portage SPLL, simulation ou nouvelle pente n'est ajouté à ce lot.

Les démonstrations étendues proposées dans le plan natif sont des travaux futurs. Leur rédaction ne doit pas transformer des hypothèses, rapports d'espérances ou critères de moments en garanties opérationnelles.

## 6. Propriété, dépendances et séquence conditionnelle

- Phase autorisée : Claude écrit `docs/audits/stream_19_theory_spll_20261107.md` en anglais ; Codex possède le plan, le GO, la revue et la clôture Git. Aucun fichier partagé avec le stream 21 n'est modifié.
- Après réception de la note, Claude invoque le wrap-up et écrit `prompts/wrapups/wrapup-19-plan.md` en anglais à six sections, dans le créneau de clôture attribué par Codex. Les journaux sont ignorés. Code, résultats, données, configurations, papier, mémoire et audits historiques restent hors de ce lot.
- Aucun livrable CD-DFM, JEPA ou gel n'est requis pour cette note documentaire. Ces dépendances restent ouvertes pour les expériences qui les nécessiteraient.
- Toute extension analytique codée demandera un plan/GO séparé et un créneau exclusif pour `floors`/`pipelines`. Toute campagne D5 ou D6 demandera son autorisation scientifique ; D6 réel et entraînement JEPA restent exclus du mandat actuel.
- La lecture éventuelle du code auteur, sans clonage ni exécution, devra lever les lacunes d'estimation avant de prétendre porter SPLL. Aucune installation n'est proposée.

## 7. Contrôles à prévoir

1. Contrôles documentaires : provenance des citations, distinction faits/hypothèses, variantes SPLL, dimensions avec et sans PC1, conventions d'amplitude, absence de transfert d'AUC vers une garantie séquentielle. Pour toute étude future, états et seuils sont ajustés sur des lignes sans dérive puis gelés pendant la surveillance.
2. Cas limites analytiques : N = 1, ρ = 0, ρ tendant vers 1, sous-espace sans signal, projection complète, spectre multiple, dérive concentrée ou orthogonale à la queue.
3. Pour un portage futur seulement : matrice non inversible, fenêtres vides/insuffisantes, centres symétriques ou non, support invariant sous signes malgré des centres non symétriques, graines locales et indépendance du nombre de workers. Une pseudo-inverse ou une régularisation ne sera jamais introduite silencieusement.
4. J1 : SHA-256 disque/index attendu, 47 CRLF, zéro LF isolé. E3/D8 reste FAIL ; aucune tentative de recalibration pour obtenir PASS. Les manifestes PCA restent inchangés et le benchmark n'est pas relancé.
5. Aucun `configs/FROZEN.json`, accès aux données réelles 2020+ ou entraînement. Les tests scientifiques ne sont pas lancés pour cette préparation documentaire.
6. En cas de futur commit : wrapup, réindexation prescrite et `make check` avec le venv épinglé, dans un créneau exclusif, avant audit Git et intégration. Cette séquence n'est pas exécutée par le présent plan.

## Décision GO intégrée

**GO DOCUMENTAIRE ACCORDÉ — décision explicite du chercheur, 7 novembre 2026.**

La note datée et son wrapup sont autorisés dans le périmètre de `prompts/GO-stream-19-plan.md`. Aucun code, calcul ni nouvelle expérience. Le créneau de clôture est attribué par Codex ; toute la séquence wrapup → réindexation AST → make check → commit → fetch/rebase → audit de plage → push reste sérialisée. Le push attend la confirmation exigée au moment de l'action. La date J4 n'ouvre aucun accès expérimental.
