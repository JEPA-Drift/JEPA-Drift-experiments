# Plan natif v1 — stream 19-protocol-20261112 : protocole E4 synthétique à question unique

**PLAN ONLY v1 — révision ciblée selon `prompts/NO-GO-stream-19-protocol-20261112.md` (points 1 à 7), en attente de revue et d'un GO
documentaire séparé ; aucun GO scientifique.** v0 archivé : `logs/stream_19_protocol/native-plan-v0.md`, SHA-256
`c8829ca27920a55ea5485050909536d430ff5be054e0fbab4306f37b86f13efc`. Mandat `logs/stream_19_protocol/mission-plan.md` ; base `891cfa5`,
branche `stream-19-protocol-20261112`, session `jepa-s19-protocol-20261112` (UUID 0a586401-6f3b-49b0-8900-d4f7cdff4a09), Opus 5.5,
effort max, sans Agent/Task. Phase plan : lectures de texte, `grep`, `wc`, `sha256sum` ; aucun Python, test, calcul, simulation, donnée ni Git.

## 1. Contexte et tâche documentaire
- Stream 19 PARTIEL (amorçage du 12/11, §C, §D/P1) : oracle `docs/sections/e4_oracle_reference.md` (I_N d'une dérive de marché à
  direction connue, sans détecteur ni délai), note `docs/audits/stream_19_theory_spll_20261107.md`, audit
  `docs/audits/stream_19_replan_2026_11_06.md`. Aucune campagne E4, aucune pente en N ; le benchmark PCA scellé fixe N = 239 (replan F1).
  Aucune source ne sépare, quand N varie, le délai mesuré d'un dictionnaire, l'information et l'alignement.
- Tâche après GO documentaire : UN document anglais `docs/audits/stream_19_protocol_proposal_20261112.md` (≤ 250 lignes), protocole
  prospectif d'une seule question synthétique falsifiable. Chaque défaut scientifique y est PROPOSED pour un GO scientifique ultérieur du
  chercheur ; le GO documentaire n'en approuve aucun.

## 2. Faits bornés établis pendant le plan (lecture seule)
- P3-CS(b) (`jepadrift/pipelines.py:54,64,395-432` ; `jepadrift/representations/cross_section.py:13-43`) : défauts `K="mp"`,
  `mode="factor"`, `b="pc1"`, `variant="b"`, seuil anytime-valid γ ; aucune caractéristique (`CHAR_PIPELINES = ("P4-C", "P4-D")`) ;
  z_odd = U'p/‖p‖, p = x − b̂ b̂'x ; mises prévisibles (EWMA de ‖p‖, σ̄ = médiane calib du fit) ; `log_dictionary_edetector(…, "cusum",
  eta0=(STAKE_CAP/2,))`. Il retire b̂ estimé : exactement aveugle au marché vrai seulement si b̂ ∥ 1 ; indéfini à N = 1. Le mode factor
  exige K_MP ≥ 1 (note §1, C-repr-mp-K) ; K_MP = 0 étant attendu [H] dans un modèle à un facteur, le mode `full` est PROPOSÉ.
- Revue Codex (NO-GO, point 5) : P2-C est une moyenne des signes, pas le signe de la moyenne (`pipelines.py:242-247`) ; P7 est un LLR
  gaussien, pas un oracle de signes (`pipelines.py:435-448`). Aucun alias ni changement de ces implémentations.
- Benchmark scellé (`configs/pca_drift_benchmark.yaml` ; schéma §2, §4, §6) : rôles indépendants ; règle
  `predictive_exchangeable_rank_v2` (r = ⌊α(n+1)⌋ − 1, échec sous 19 maxima à α = 0,05, borne 100/2001 à n = 2000) ; FPR holdout avec
  IC de Wilson ; RMST = moyenne de min(T, H) ; first_hit compté alarme incluse ; graines `[28, seed, crc32(domain), …]` à CRC
  distincts et entropies uniques ; 8 GiB et 30 min par invocation.
- DEVIATIONS : C-inject-conv-b (convention (b) historique) ; C-P3CS-design (mises (b)) ; C-e1-readings (« α nominal commun » ; « FPR égal »
  seulement si l'IC apparié tient dans ±0,01) ; C-e1-amplitude-grid (pilote sur délais, non repris) ; C-P4D-null-insample (nul indépendant
  écrit avant résultat ; un contrôle D5 ne certifie que son modèle) ; C-pca-predictive-rank (garantie marginale, chemins synthétiques).

## 3. Question unique PROPOSÉE et justification
**Q.** Fond gaussien équicorrélé (ρ = 0,4), dérive résiduelle Δμ ⊥ 1 de direction isotrope dans 1^⊥ et d'information journalière I*
identique pour tout N : le délai restreint mesuré du dictionnaire spectral ex ante (tous les axes LW-PCA, PC1 incluse) croît-il avec N
alors que l'oracle à direction connue reste invariant, et comment cette croissance covarie-t-elle avec le meilleur canal mesuré ?
- Information fixée par construction (loi de l'oracle O-dir invariante en N [A]) ; meilleur canal a_best mesuré par essai (diagnostic
  oracle) ; délai du dictionnaire mesuré par RMST(H). Nuisances nommées : N/T et fit Ledoit–Wolf varient avec N ; alignement,
  estimation et calibration ne sont pas séparés causalement.
- Falsification : prédiction opérationnelle nulle du protocole, β_Δ = 0, pente de Δ(N) = log RMST_H(dictionnaire) − log RMST_H(O-dir)
  sur la grille N fixée ; rejet si l'IC apparié à 95 % exclut 0. Un rejet ne réfute que cette prédiction sous ces choix (fond, amplitude,
  fit, lecture), pas une équivalence générale entre information et délai. Identité comptable prédéclarée : Δ = Δ_1 (O-score1 contre
  O-dir) + Δ_2 (dictionnaire contre O-score1) ; Δ_1 et Δ_2 ne sont pas des effets purs identifiés d'alignement ou de dimension.
- Choix parmi les candidats G1 (replan F7) : la saturation F1 relève de l'information de marché déjà donnée par l'oracle (G → 1/ρ) ;
  D4 exige des données réelles, tandis que N = 500 synthétique n'en exige aucune et figure dans la grille PROPOSÉE ; P3-KF/SPLL garde
  des choix non résolus (note §5.7), donc omis ; la « prévision du dictionnaire contre pente mesurée » se teste en synthétique seul.
  Elle fixe la référence ex ante non concentrée qu'une représentation apprise future devra dépasser.
- Classement par projection sur les espaces propres de Σ_N : marché, Δμ ∈ span(1) (I_N borné, oracle ; EW = direction du rapport de
  vraisemblance), hors lot ; facteur ≡ marché dans ce modèle à un facteur (multi-facteurs hors lot) ; résiduel, Δμ ⊥ 1, question
  primaire ; mixte = somme exacte des deux informations gaussiennes [A], non retenu.
- Lot minimal sans lecture de données : ni D6, ni rendement réel, ni EUROFIDAI, ni 2020+, ni JEPA/VAE, ni modèle entraîné.

## 4. Défauts scientifiques PROPOSÉS
- Covariance Σ_N = ρ11ᵀ + (1−ρ)I_N, ρ = 0,4 (oracle et benchmark scellé), jours i.i.d. ; sensibilité t7 : même Σ_N, un χ²₇ par jour
  partagé, variance unité, innovations normales communes avec le fond gaussien ; I* y est un proxy gaussien à deux moments, jamais une KL t7.
- Dérive : u_N = P_{1⊥}g_{1:N}/‖P_{1⊥}g_{1:N}‖, g ~ N(0, I_{N_max}) par réplique (emboîtée en N, uniforme sur la sphère de 1^⊥) ;
  Δμ = c·u_N, c = √(2(1−ρ)I*), d'où I = I* exactement [A] ; présente dès le jour 1 ; injectée dans l'espace des rendements ; identifiant
  descriptif PROPOSÉ `SYNTH_RESIDUAL_ISOTROPIC_FIXED_INFO`, jamais « F2 » (adoption réservée au GO scientifique).
- Amplitude : information fixée, variante restreinte à 1^⊥ du budget de norme totale fixe (note §3.1) ; I* fixé analytiquement par
  τ_γ = ln γ_H / I* = H/40, jamais ajusté sur un effet de test ou de pilote ; quitter la convention (b) historique reste une proposition.
- N varié, grille figée avant tout tirage scientifique : {8, 16, 32, 64, 128, 239, 500}, N = 500 sous le seul pilote de coût ; N = 1 et 2
  réservés aux témoins de code.
- k et d fixés : préfixe spectral k = d = 8 (plus petit N) ; dictionnaire complet d = N ; O-score1 : réservoir de N axes, d = 1.
- Fit : T_fit = 2000 lignes sans dérive par fond ; base Ledoit–Wolf gelée par N sur les N premières colonnes ; N/T et fit varient avec
  N (nuisances déclarées, fuite de PC1 enregistrée).
- H = 2000, α = 0,05, γ_H = H/α (prompt 19) ; délai = first_hit, jour d'alarme inclus (C-pipe-delay) ; censure à H.

## 5. Méthodes : ex ante contre oracle
EW, SPEC-* et O-* : e-détecteur CUSUM sur flux de signes exacts (entrées dans [−1, 1]) ; P3-CS(b) garde ses mises prévisibles propres
(C-P3CS-design) : les méthodes ne diffèrent donc pas seulement par direction et dimension.
- Ex ante, rôle fit seulement : EW, signe de 1'x, défini par formule et distinct de P2-C (d = 1 ; exactement aveugle à toute translation
  orthogonale à 1, d'où témoin négatif) ; SPEC-prefix8 (axes 1..8 par variance) ; SPEC-full (P3-C `full`, N axes dont PC1, moyenne
  équipondérée d'e-détecteurs) ; P3-CS(b) `full` (N − 1 directions résiduelles, b̂ estimé retiré).
- Oracles, étiquetés ORACLE_* (dérive injectée, Σ vraie), jamais déployables : O-dir, oracle de signes sur u_N'x, défini par formule et
  distinct de P7 ; O-score1, axe estimé maximisant J_k = (v̂_kᵀΔμ)²/(2 v̂_kᵀΣv̂_k).
- Diagnostics oracle par essai : I* ; information du flux de signes de O-dir (forme fermée) ; meilleur canal a_best = max_k J_k / I*
  (coordonnées PCA empiriques non indépendantes sous Σ : la somme des J_k n'est pas I*) ; rétention d'un préfixe = KL jointe projetée
  rapportée à I*, jamais une somme de J_k ; a_max plug-in, diagnostic de modèle distinct ; K_MP ; fuite de PC1 ; multiplicateur fluide descriptif.
- Interdits pour toute sélection ex ante : dérive d'évaluation cachée, alternatives futures, issues de calibration ou de holdout. Rôle de
  développement de sélecteur vide ; une sélection PCA apprise sans oracle est un stream futur distinct (amorçage P4), jamais ajoutée à 19.

## 6. Rôles, graines, lectures, métriques
- Rôles indépendants : fit (T_fit) ; calibration nulle (n_cal) ; holdout nul intouché jusqu'au gel des seuils (n_hold) ; alternatives
  (n_alt). Pas de rôle centering (dérive de moyenne seulement).
- SeedSequence `[19, seed, crc32(domaine), crc32(fond), crc32(rôle), réplique]`, domaines path, direction, coins, boot, pilot ;
  contrôles CRC et entropies du benchmark scellé. Chemins tirés à N_max puis tronqués : essais appariés entre N, détecteurs et fonds.
  Sorties identiques octet pour octet quel que soit `--jobs`.
- Lecture primaire, proposition au chercheur : seuil `predictive_exchangeable_rank_v2` sur le maximum du log e-détecteur des chemins de
  calibration ; garantie marginale sur la calibration, un seuil réalisé pouvant avoir un FPR conditionnel supérieur à α. Secondaire :
  anytime-valid à horizon, P∞(alarme avant H) ≤ H/γ_H. Motif [H] : à α nominal égal, le FPR atteint du dictionnaire anytime-valid peut
  varier avec N et biaiser la pente. Un α nominal égal n'établit pas un FPR atteint égal.
- Métriques : first_hit, min(T, H), RMST(H) (ET par cellule, deff = 1 entre chemins indépendants), taux de détection et FPR(H) holdout
  avec IC de Wilson ; contrastes et pentes par bootstrap apparié des répliques, sans indépendance supposée entre N ni entre détecteurs.
- Cinq objets séparés : budget τ_γ (règle d'amplitude seulement), anytime-valid (borne à horizon H/γ, non Ville), ARL0 (non estimé),
  diffusion Φ(γI)/I (non utilisée), RMST(H) (moyenne restreinte, jamais un ADD de Lorden).

## 7. Règles de décision PROPOSÉES
- Observations : toutes les cellules sont conservées. r < 0 ⇒ CALIBRATION_FAILED (déterministe). Une borne inférieure de Wilson du FPR
  holdout au-dessus de α est étiquetée FPR_ABOVE_NOMINAL (diagnostic, incertitude conditionnelle au fit et à la calibration) : ni preuve
  de violation ni preuve de défaut de code, aucun STOP scientifique automatique. Seule une défaillance déterministe d'intégrité est un STOP.
- Comparabilité : « FPR atteint comparable » seulement si l'IC apparié à 95 % de la différence des FPR holdout tient dans ±0,01
  (précédent C-e1-readings) ; sinon étiquette « α nominal commun » ; une étiquette, jamais une exclusion.
- Grille et censure : pentes descriptives sur la grille N fixée avant tirage, toutes cellules conservées ; aucun N choisi après
  observation, aucun sous-ensemble retenu par le taux de détection. Qualification PROPOSÉE de faible censure : borne inférieure de
  Wilson du taux de détection ≥ 0,95 pour chaque détecteur du contraste sur toute la grille, sinon NOT_IDENTIFIED pour l'interprétation
  visée (valeurs rapportées). Pente locale de moyennes restreintes, jamais un exposant de `cor:scaling`.
- Verdicts sur β_Δ : COST_GROWS, NO_GROWTH_DETECTED, COST_SHRINKS, NOT_IDENTIFIED ; Δ_1 et Δ_2 rapportés avec IC comme termes
  comptables, sans verdict ni attribution causale. Intégrité : pente de O-dir et taux EW comparé au FPR EW ⇒ avertissements.

## 8. Tailles, ressources, pilote de coût
- n_cal = n_hold = n_alt = 2000 par fond (précédent scellé), T_fit = 2000, B_boot = 2000, graine 42. Puissance, faisabilité, durée et
  coût INCONNUS jusqu'au pilote autorisé, concluance de la marge ±0,01 comprise ; aucune campagne ajoutée maintenant pour les établir.
- RAM ≤ 8 GiB ; ≤ 30 min par invocation avec reprise par partitions (motif scellé) ; plafond total PROPOSÉ de 24 h CPU ; dépassement
  ⇒ BLOCKED_RESOURCE, jamais d'approximation.
- Pilote de coût seul, avant tout tirage scientifique : 40 répliques par rôle, domaine de graines `pilot` disjoint, durées et RSS
  seulement (aucun délai, FPR ni taux écrit ou lu) ; projection linéaire = ESTIMATION. Replis fixés d'avance : (1) retirer N = 500 ;
  (2) t7 sur N ∈ {8, 64, 239} ; (3) STOP et retour au chercheur. Ni I*, ni H, ni seuils, ni méthodes ne changent.

## 9. Plan du document anglais (≤ 250 lignes)
1 Status and scope (PROPOSED, not an E4 result, certifies the synthetic model only) · 2 Question, operational null, falsification ·
3 Model: covariance, t7 proxy, drift classes, amplitude rule, N/k/d/T_fit · 4 Methods: ex ante/oracle, diagnostics, forbidden information ·
5 Roles, seeds, pairing, jobs · 6 Readings, metrics, five separated objects · 7 Analysis: endpoint, fixed grid, labels, verdicts ·
8 Sizes, resources, cost-only pilot · 9 Acceptance witnesses, TDD order · 10 Exclusions, open choices · 11 Controls, source SHA-256.
Étiquettes [D], [A], [H] ; aucun nombre calculé ni pente pré-remplie ; sources citées, jamais ré-auditées.

## 10. Exigences futures d'API et de TDD RED→GREEN (spécification ; rien n'est écrit ni exécuté)
- Lot de code distinct, avec plan propre et GO scientifique du chercheur. Noms PROPOSÉS : `experiments/e4_alignment.py`,
  `configs/e4_alignment.yaml`, `results/e4_alignment/`, `logs/e4_alignment/`, `tests/test_e4_alignment.py`.
- Réutilisation d'abord : registre `pipelines` pour P3-C full et P3-CS(b) full seulement (EW et O-dir définis par formule, sans alias de
  P2-C ni de P7), `eprocess`, `exact_sign_stream`, Ledoit–Wolf de `representations.pca`, `save_fair_csv`, motifs seed-plan, manifeste
  et partitions du benchmark scellé. Ce lot documentaire n'autorise aucune extraction ni modification de la règle de rang scellée ;
  toute réutilisation future, sous GO distinct, préserve ses hashes et les 44 contrats.
- Témoins écrits d'abord et observés RED, sur fixtures factices réduites (`make check` < 5 min) :
  (a) dimensions finies : N = 1 sans direction résiduelle non nulle (dérive résiduelle, O-dir résiduel et P3-CS(b) refusés ; EW seul,
      témoin séparé), N = 2, k > N refusé ;
  (b) entrées vides ou invalides (grille vide ; N non entier, booléen, ≤ 0 ; I*, ρ, α, H hors domaine ; ν ≤ 2 ; n_cal < 19) ⇒ refus ;
  (c) aucun accès futur : modifier x_{t+1..H} ne change aucune alarme ≤ t ; mises prévisibles ; aucune méthode ex ante ne reçoit la dérive ;
  (d) source ou hash périmé : config, code, environnement, base ou calibration de hash différent ⇒ refus ; sortie déjà munie d'un
      manifeste refusée ; partition d'empreinte différente refusée ;
  (e) rôles indépendants : clés distinctes, collision CRC ⇒ erreur, chemins de calibration et de holdout disjoints ;
  (f) étiquettes oracle : chaque ligne O-dir, O-score1 ou diagnostic porte ORACLE_* et reste hors des tableaux ex ante ;
  (g) `--jobs 1` contre `--jobs 3` et ordre des répliques permuté ⇒ CSV identiques octet pour octet ; autre graine ⇒ sorties différentes ;
  (h) exactitudes : troncature emboîtée = colonnes 1..N ; Δμ ⊥ 1 ⇒ alarmes EW identiques au nul ; nul t7 apparié = nul gaussien
      pour les flux de signes à base fixée ; first_hit, censure et RMST sur alarmes connues ; grille de pente figée.
- GREEN : implémentation minimale jusqu'au vert ; `monitors/` en numpy seul ; aucune donnée réelle ; `make check` complet par Codex.

## 11. Faits bornés à vérifier pendant la rédaction (`grep -n`, puis une fonction au plus par fait)
1. `log_dictionary_edetector` : bilatéral ou unilatéral ; grille `EDETECTOR_ETA0`. 2. `pca_directions` : refus si K_MP = 0 en mode
factor ; conventions de signe et d'égalité des valeurs propres. 3. Noms exacts : `horizon_gamma`, `save_fair_csv`, `exact_sign_stream`,
`dictionary_multiplier`. P2-C et P7 sont réglés par la revue (§2). Tout écart avec ce plan ⇒ arrêt et signalement, sans adaptation.

## 12. Propriété des fichiers et séquence
- Codex : `prompts/plans/plan-19-protocol-20261112.md`, `prompts/GO-stream-19-protocol-20261112.md`,
  `docs/audits/streams_01_31_continuation_2026_11_12.md`, revue, Git, réindexation, `make check`. Claude n'y écrit pas.
- Claude, après GO documentaire écrit et sortie officielle de cette même session plan : le protocole anglais et des journaux ignorés sous
  `logs/stream_19_protocol/`. Après réception Codex et créneau de clôture explicite : skill wrap-up, puis `prompts/wrapups/wrapup-19-protocol-20261112.md`
  en anglais (Context, Validated Results, Errors and Dead Ends, Current State, Vigilance Points, Recommendations).
- Rien d'autre : sources scientifiques, tests, configurations, résultats, figures, papier, MAPPING, DEVIATIONS, dépendances et mémoire
  projet inchangés ; ni commit, ni push, ni réindexation, ni `make check` complet par Claude.

## 13. Contrôles documentaires shell (aucune commande Git sans autorisation du GO)
- Avant : journal initial écrit avec l'outil Write (référence temporelle) ; `sha256sum` des sources lues, des trois fichiers Codex et
  des invariants E2, E3 et manifeste PCA (valeurs de l'amorçage, §B).
- Après : `wc -l` ≤ 250 ; `grep -n '^## '` conforme au §9 ; `grep -c PROPOSED` ; `grep -nE 'APPROVED|proves|validates'` vide ; toute
  KL proche de « t7 » étiquetée proxy ; `grep -nE '[0-9]+\.[0-9]+'` revu (sources ou défauts PROPOSÉS) ; `grep -n '/home/'` vide ;
  `grep -nE '[àâçéèêëîïôùûü]'` vide ; `find . -newer <journal> -type f -not -path './.git/*'` limité au protocole et au journal
  (fichiers étrangers signalés) ; `sha256sum` avant/après identiques.
- Signal : `REVIEW_READY stream-19-protocol-20261112`, chemin et SHA-256, puis attente du créneau Codex.

## 14. Choix non résolus du chercheur (défaut entre parenthèses)
1. Convention d'amplitude primaire (information fixée I*, proposition) ou convention (b) historique, I ∝ N.
2. Lecture primaire (calibrée par rang, proposition) ou anytime-valid à horizon (continuité du prompt 19).
3. Budget τ_γ(I*) (H/40) et grille N (historique ; N = 500 sous porte de coût).
4. Tailles (2000 par rôle) ; n_hold plus grand si la marge ±0,01 doit être concluante.
5. Qualification de faible censure (Wilson ≥ 0,95 sur toute la grille du contraste) et plafond CPU (24 h).
6. Sensibilité t7 (même grille, secondaire) ; adoption éventuelle de l'identifiant `SYNTH_RESIDUAL_ISOTROPIC_FIXED_INFO`.

## Décision GO intégrée — 12 novembre 2026

GO Codex au titre du mandat documentaire délégué, sans signature du chercheur ni approbation de protocole scientifique. La révision native v1, conservée à l'identique dans le journal, est reçue après les sept corrections du NO-GO v0. Celui-ci reste une trace historique ; son refus est levé pour la rédaction documentaire sous les précisions suivantes, qui priment sur tout passage antérieur.

1. **Nouveauté bornée.** E1 bras B rapporte déjà des pentes en N, de l'information injectée et de l'alignement (audit du 6 novembre, F2-F3). Le nouveau sujet est une comparaison contrôlée synthétique à information gaussienne de population fixée, distincte de l'E1 D6 rétrospectif à amplitude par titre et du full PCA à N=239. Ne pas revendiquer une première séparation générale de ces quantités ni l'absence globale de travaux existants.
2. **Appariement.** La recette de clés du §6 doit être explicitée sans contradiction : les innovations normales communes sont tirées une fois sous un domaine partagé entre fonds ; le facteur chi-square propre au t7 a un domaine distinct. Les directions sont partagées de façon déclarée entre N et fonds ; les rôles fit, calibration, holdout et alternatives restent disjoints. Aucun appel présenté comme indépendant ne réutilise une entropie pour forcer un appariement. Cette recette est PROPOSED et non exécutée.
3. **Oracles et calibration.** Déclarer quand la direction et le meilleur axe oracle sont fixés, et quelle loi nulle permet de partager une calibration entre flux scalaires de signes. N'inférer aucune réutilisation légitime à partir du seul nom de l'oracle. À défaut de recette entièrement spécifiée, conserver ce point OPEN pour le GO scientifique ; ne pas créer une simulation pour le résoudre.
4. **Incertitude.** Avec un fit et une calibration communs aux trajectoires, les IC de Wilson et le bootstrap apparié décrivent une incertitude conditionnelle à ces objets. Ils n'intègrent pas leur variabilité d'estimation. Aucune conclusion sur l'ensemble des fits n'en découle ; un niveau externe de rééchantillonnage serait une décision scientifique et un budget supplémentaires. Les pentes descriptives à alpha nominal commun gardent cette qualification si le contrôle de comparabilité des FPR échoue.
5. **Amplitude.** La phrase I proportionnel à N pour la convention (b) est limitée à la famille résiduelle et au modèle équicorrélé ici proposés ; aucune loi universelle d'amplitude n'est déclarée. Les choix I*, seuil de rang, grille, effectifs, censure, t7 et budget restent des propositions non approuvées.
6. **Vérification documentaire.** Git en lecture seule est permis avec GIT_OPTIONAL_LOCKS=0 : status porcelain, diff --quiet HEAD, diff --name-only HEAD. Les empreintes avant/après et le périmètre Git portent l'intégrité ; find -newer est complémentaire, incapable de détecter suppression ou date restaurée. Aucun statut 0 d'une commande de comptage ne vaut PASS si un contrôle échoue.
7. **Budget et limites.** Un seul document anglais, au plus 250 lignes. Rédaction bornée à 20 minutes à partir du signal de Codex ; pas de nouvelle exploration générale, dérivation étendue, recherche SPLL ou campagne destinée à régler les paramètres. Un point non résolu est déclaré OPEN. Au plus trois corrections d'un même défaut d'infrastructure, puis arrêt déclaré.
8. **Périmètre.** Le protocole prospectif et les journaux propres seulement ; wrapup après réception et allocation explicite. Aucun code, test, donnée, configuration, résultat, figure, papier, mapping, déviation, mémoire ou dépendance ne change. Le registre scientifique et les scellés restent inchangés. Sortie officielle du mode plan dans la même session et vérification du mode par Codex avant le signal de rédaction.

Le GO séparé nomme le SHA-256 du présent plan. Il autorise la production d'une proposition à soumettre au chercheur, pas la réalisation de la proposition. Tous les choix scientifiques et toute future implémentation E4/SPLL gardent leur GO spécifique.
