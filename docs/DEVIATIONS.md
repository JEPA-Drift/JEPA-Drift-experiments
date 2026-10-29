# DEVIATIONS — JEPA-Drift (Article C)

Écarts au plan ou à l'Article B, consignés sous un identifiant `C-<topic>`.

## C-push-policy — politique de push (2026-10-16)

Le plan initial (« aucun `git push` avant l'accord de propriété intellectuelle LUSIS CIFRE »,
mémoire projet) est amendé par le chercheur le 2026-10-16 : après chaque stream traité, l'agent
qui le termine exécute `tools/reindex_graphify_jcodemunch.sh`, `make check`, un commit explicite
(Conventional Commits) puis `git push origin <branche courante>`. Condition : l'adresse du dépôt
n'est ni partagée publiquement ni liée à une publication — le dépôt est le compagnon anonymisé
d'une soumission anonyme (« anonymous submission »), les commits restent anonymisés (identité
`JEPA-Drift Authors <jepa.drift@gmail.com>`, aucun nouvel identifiant d'auteur ou d'institution).
Les gardes EUROFIDAI sont inchangées : les données propriétaires ne quittent jamais la machine,
`data/raw/eurofidai/` et `data/derived/d4_eurofidai/` restent ignorées et bloquées, et aucun push
ne doit les contenir (aucun fichier de plus de 50 Mo non plus).

Vérification 2026-10-16 : `https://github.com/JEPA-Drift/JEPA-Drift-experiments` répond HTTP 200
(dépôt public, soumission anonyme) ; l'alias SSH `github-jepa-drift` pointe vers `github.com` ;
aucune donnée EUROFIDAI suivie par git ; la plage `origin/main..HEAD` ne contient aucun chemin
eurofidai. Le push est effectué conformément à l'amendement, la condition portant sur le partage
de l'adresse (et non sur l'accessibilité du dépôt, voulue pour la soumission anonyme).

## C-eos-protocol — protocole de fin de stream (amendement complémentaire, 2026-10-16)

Complément de `C-push-policy`. Avant **chaque** commit, l'instance chargée de l'implémentation
(Mistral Vibe ou Claude Code) invoque sa directive de wrapup et enregistre le résumé produit dans
`prompts/wrapups/wrapup-[XX].md` ([XX] = numéro ou référence du stream ; fichier rafraîchi à chaque
commit). Chronologie exacte en fin de stream : (1) wrapup + enregistrement ; (2) réindexation via
`tools/reindex_graphify_jcodemunch.sh` ; (3) `make check` puis commit unique — ou multiples si les
travaux sont hétérogènes et risquent des erreurs sur une partie des livrables — ; (4)
`git push origin <branche>`. Le chercheur a confirmé le 2026-10-16 que le dépôt GitHub, public,
n'est connu de personne : l'instruction de push après chaque stream ne souffre aucune exception.
Les rôles des répertoires sont désormais décrits dans AGENTS.md (« Repository layout »), notamment
`prompts/streams/` (prompts des streams planifiés) et `prompts/wrapups/` (résumés des traitements
des streams).

## C-plan-recording — enregistrement des plans de stream (2026-10-16)

Nouvelle règle du projet (amendement 2026-10-16) : lorsqu'un plan d'implémentation est créé pour
un stream [XX] (demande textuelle explicite de l'utilisateur, ou appel direct de la directive
`/plan`), il est enregistré dans `prompts/plans/plan-[XX].md` AVANT son exécution. Le rôle du
répertoire `prompts/plans/` est documenté dans AGENTS.md (« Repository layout »).

## C-D2-survivor — périmètre des données (2026-10-16)

D2 est le panel des 97 actions américaines survivantes du dépôt B (R15 : 5154 jours × 97 titres,
2005-01-04 à 2025-06-30). Échantillon biaisé par la survie, réutilisé tel quel et sans re-filtrage :
le panel est la population de l'Article B, et tout re-filtrage romprait l'identité bit à bit avec le
code de référence.

## C-interface-f64 — interface (2026-10-16)

`ret` est stocké et retourné en float64 (et non float32) : lu avec `float_precision='round_trip'`,
il est identique bit à bit aux séries CSV de l'Article B (chaîne SHA-256 des entrées et des sorties
dans `data/derived/MANIFEST.json`).

## C-D3-no239 — liste des 239 titres CD-DFM absente (2026-10-16)

Le dépôt `alexouadi/CD-DFM` (cloné dans `external/cd-dfm/`, commit épinglé dans le manifeste) ne
contient pas la liste explicite des 239 titres du S&P 500 utilisés par Alouadi & Lehalle
(arXiv:2607.24410) : le README indique « We cannot redistribute the panel » (caractéristiques
RavenPack/Compustat sous licence). Règle de repli déterministe appliquée : parmi les 503
constituants actuels du S&P 500 (Wikipedia), les 239 titres retenus sont ceux ayant le plus grand
nombre de jours de trading depuis 2000-01-01 (ex æquo : ordre alphabétique). La sélection est
enregistrée dans `data/derived/d3_239/selection.json` et vérifiée par le test
`test_d3_239_selection`.

## C-D3-survivor — constituants actuels du S&P 500 (2026-10-16)

`d3_500` est construit à partir des constituants actuels du S&P 500 (table Wikipedia « List of
S&P 500 companies », 503 titres au 2026-10-16), et non d'une sélection par survie. Contrairement
à D2 (97 survivants biaisés par la survie), D3 n'a pas de biais de survie : les titres sont les
constituants actuels, et l'historique individuel de chaque titre peut être partiel (géré par
`in_universe`). 503/503 titres téléchargés avec succès depuis Yahoo Finance.

## C-D3-gics-static — secteur GICS statique (2026-10-16)

Le secteur GICS utilisé dans `chars.parquet` est le secteur actuel (table Wikipedia), non une
classification point-in-time. Un titre ayant changé de secteur au cours de la période conserve
son secteur actuel sur toute la période. Les 11 secteurs GICS sont encodés en one-hot
(`c_gics_<sector>`).

## C-D3-provenance — provenance et reproductibilité (2026-10-16)

Les cours ajustés proviennent de Yahoo Finance via yfinance 1.7.0 (installé dans `.venv`, figé
dans `requirements.lock`). Les hashes SHA-256 des bruts Yahoo (`data/raw/d3_yf/`, gitignoré) sont
une provenance à date fixe : Yahoo révise l'historique ajusté, un re-téléchargement n'est pas
garanti bit-identique. L'ancrage reproductible est le panneau dérivé commité
(`data/derived/d3_239/`, `data/derived/d3_500/`) + hash de sortie dans le manifeste. Le test de
reconstruction depuis le cache (`test_reconstruction_from_cache`) vérifie que `ret_wide.npy` est
bit-identique à la reconstruction depuis les caches bruts. Le déterminisme bit-à-bit du parquet
repose sur pyarrow 26.0.0 épinglé + codec fixé (snappy par défaut) + pas de timestamp embarqué.
Tous les fichiers dérivés sont sous la limite de 50 Mo (plus grand : `d3_500/panel.parquet` à
45,97 Mo) : pas de compression zstd ni de sharding nécessaires, aucun écart C-D3-shard requis.

## C-D3-manifest-merge — préservation des entrées D3 dans le manifeste (2026-10-16)

`articleB.build()` (exécuté par le fixture de test de `test_data_d1_d2.py`) recrée le manifeste
et préserve désormais les entrées des autres builders (`datasets`, `results`, `sources` non
D1/D2) : sans ce mécanisme, le rebuild D1/D2 écrasait les entrées D3 (`d3_239`, `d3_500`,
`sources.d3`) ajoutées par `sp500._update_manifest`.

## C-R01-parse — lecture des CSV dérivés par R01 (2026-10-16)

R01 (`exp_R01_real_world_backtest.py` l.249) lit `data/derived_firstrate/R01_daily_<ETF>.csv` avec
le convertisseur flottant par défaut de pandas, alors que D1 (prompt 2) lit les mêmes fichiers avec
`float_precision='round_trip'`. Les deux lectures diffèrent sur 6258 des 6414 rendements SPY,
jusqu'à 7356 ulp, sous pandas 2.3.2 comme sous 3.0.6. Effet sur la réplication de R01 depuis le
chargeur D1 (`results/identity/articleB_R01_R08.csv`, entrée `d1_loader`, identique dans les deux
environnements) : `omega` ≤ 2.64e-14 et `sigma_unc` ≤ 1.32e-14 en relatif (4 cellules chacune),
`S_over_thr_Data` ≤ 1.97e-14 (220 cellules sur 253). Les sorties discrètes (α, β, Γ̂, q̂, alarmes
2020, délais, taux, IC, ADD, SEM) sont bit-identiques. Avec le lecteur de R01 (entrée diagnostique
`articleB_csv`, seule exception délibérée à `round_trip`), ces colonnes sont bit-identiques.

## C-R01-env — environnements de contrôle R01 (2026-10-16)

Les contrôles d'identité tournent dans `.venv` (numpy 2.4.4, scipy 1.17.1, pandas 3.0.6,
statsmodels 0.15.0) et dans `external/articleB-venv` (créé par `~/miniforge3/envs/Trading/bin/python
-m venv`, puis `pip install -r` des requirements de l'Article B : numpy 1.26.4, scipy 1.16.2,
pandas 2.3.2, statsmodels 0.14.5 ; PyYAML 6.0.3 ajouté pour importer le chargeur D1, sans rôle
numérique). Résultat identique dans les deux : 1401 cellules R01 et 32 cellules R08 conformes ;
SLSQP (`fit_garch_qmle`) bit-identique sous scipy 1.16.2 et 1.17.1. Seul écart d'environnement :
`lb_pvalue_warmup`, 4 cellules à 4.63e-15 en relatif. Cause établie : `acorr_ljungbox` appelle
`acf(fft=False)`, donc `np.correlate`, dont le résultat dépend de la BLAS liée à numpy ; les roues
PyPI (openblas64) donnent Q = 0x1.8a1ef17b13742p+4 pour SPY, la build conda-forge de
l'environnement `Trading` (versions de l'Article B) donne 0x1.8a1ef17b13749p+4 et reproduit le CSV
de l'Article B bit à bit (1401/1401 cellules `articleB_csv`, exécution diagnostique non écrite) ;
`chi2.sf` est identique partout. Les versions de paquets n'épinglent pas la build BLAS : le test
diagnostique exige la bit-identité de l'entrée `articleB_csv` hors `lb_pvalue_warmup`, colonne qui
reste soumise au seuil de 1e-12.

## C-garch-pyflakes — exclusion de `jepadrift/stats/garch.py` de pyflakes (2026-10-16)

`fit_garch_qmle` est porté sans modification (R01 l.84–100) et lie une exception inutilisée
(`except (TypeError, np.linalg.LinAlgError) as e`, R01 l.99), que pyflakes signale. Modifier la ligne
romprait l'identité octet par octet exigée par le prompt 04. La cible `check` du `Makefile` exclut
donc ce seul fichier de pyflakes ; `tests/test_identity_articleB.py::test_ported_sources_byte_identical`
fige son contenu sur la source de l'Article B.

## C-lattice-midpoint — seuil flottant des CUSUM calibrés sur le treillis (2026-10-16)

`select_threshold` (`jepadrift/monitors/lattice.py`) renvoie le point du treillis λ = L·u et le seuil
opérationnel `threshold` = (L + ½)·u (règle stricte) ou (L − ½)·u (règle large), à comparer en
flottant par `S > threshold`. L'Article B compare au point du treillis lui-même ; l'accumulation
flottante des pas +0.4/−0.6 y fait alors appliquer la règle large sur une partie des trajectoires
(écart B `R08-delivered-level-above-nominal`). Le seuil au milieu laisse une marge d'une demi-unité ;
l'équivalence avec la règle exacte est vérifiée trajectoire par trajectoire
(`test_midpoint_threshold_reproduces_lattice_rule`). Valeurs inchangées : à H = 5000 et 5 %, L = 57
(λ = 11.4, niveau exact 0.043428228893176074) ; le seuil flottant vaut 11.5.

## C-e2-sim — déplacement du générateur GARCH d'E2 vers `jepadrift/sim.py` (2026-10-16)

`NU`, `T_SCALE`, `t_innov` et `Garch` quittent `experiments/e2_floor_validation.py` pour
`jepadrift/sim.py`, copiés octet par octet depuis `3e3a804` ; les SHA-256 des segments source sont
épinglés par `tests/test_injection.py::test_e2_uses_moved_generator`. Le prompt 05 dit qu'E2 « les
importe » : E2 importe `NU`, `T_SCALE` et `Garch`, mais pas `t_innov`, appelé seulement par `Garch`.
L'importer créerait un import inutilisé, que pyflakes rejette dans `make check`. La ligne d'import ne
porte aucun `# noqa` (revue GO : inerte, pyflakes n'implémentant pas E402). `results/e2/e2_cells.csv`
est inchangé : SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` avant et
après le déplacement (`make j1`) ; seule la durée change dans `results/e2/e2_j1_summary.txt` et
`logs/e2/run.log`, qui sont restaurés. `experiments.e2_floor_validation.Garch` reste importable pour le
contrôle GARCH du stream 04.

## C-inject-F2-norm — normalisation de F2 sur la moyenne de calibration (2026-10-16)

Le prompt 05 normalise F2 « sur la moyenne de calibration ». Lecture retenue (confirmée au GO) :
½·moyenne_{t ∈ calib}(Δ_tᵀΣ̂⁻¹Δ_t) = I_target, soit la moyenne des informations journalières, et non
l'information ½·Δ̄ᵀΣ̂⁻¹Δ̄ de la dérive moyenne. Motifs : I est une KL par jour (glossaire AGENTS.md) ;
l'information s'additionne jour par jour (Lemme 1) ; la Prop. « Latent delay floors » (c) écrit
SR² = 252·E[Δμ_tᵀΣ_t⁻¹Δμ_t]. Sur la calib de `d3_239` (K = 11, trois directions tirées), l'information
de la dérive moyenne vaut 73 à 95 % de la moyenne des informations journalières, et l'information
journalière varie de −17 % à +26 % autour de cette moyenne (sondes de `prompts/plans/plan-05.md`).
Après τ*, l'information réalisée suit C_t ; elle n'est pas renormalisée, faute de quoi l'échelle
dépendrait des lignes surveillées.

## C-inject-F2-nan — caractéristiques manquantes de F2 (2026-10-16)

Une caractéristique NaN compte comme une exposition nulle, soit le rang centré neutre 0 pour les rangs
de D3 dans [−0.5 ; 0.5]. Le nombre d'entrées imputées est consigné dans `meta["c_nan_imputed"]` ;
±inf déclenche une `ValueError`. Motif : sur `d3_239`, `c_beta_252`, `c_vol_63` et `c_mom_12_1`
manquent sur 8 jours de pretrain et 24 jours de calib où le rendement existe ; refuser les NaN rendrait
F2 inutilisable sur D3. Lecture retenue au GO ; `test_f2_nan_characteristics_imputed` vérifie
l'équivalence avec des zéros explicites.

## C-inject-conv-b — convention (b), amplitude par titre (2026-10-16)

Le prompt 05 définit la convention (b) comme une « amplitude par titre fixée » et κ comme le rapport
entre la dispersion transversale orthogonale aux chargements et la dérive de marché ; le prompt 19 fixe
le « SR de marché par titre » à 1. Lecture retenue (confirmée au GO) : l'amplitude par titre est la
moyenne quadratique, sur les titres et, pour F2, sur les jours de calib, des Sharpe annualisés
√252·Δ_i/σ̂_i, avec σ̂_i² = Σ̂_ii. Elle vaut `SR_ASSET_B` = 1 pour F1 et F3, et κ·`SR_ASSET_B` pour F2,
κ ∈ {0.25 ; 0.5 ; 1}. Sous le modèle équicorrélé à un facteur du plan v4 (volatilités égales,
chargements de PC1 proportionnels à 1), cette définition redonne κ = dispersion / dérive de marché et
le rapport d'information κ²(1 + (N − 1)ρ)/(1 − ρ) entre largeur et marché.

## C-inject-lw-test — correction du contrôle de shrinkage Ledoit–Wolf (2026-10-16)

Le plan du stream 05 attendait un coefficient de shrinkage inférieur à 0,05 sur données gaussiennes
isotropes (4000 × 5). C'est l'inverse : la cible de Ledoit–Wolf est l'identité, donc le shrinkage est
élevé sur données isotropes (mesuré ≈ 0,6–0,9) et faible sur covariance anisotrope (≈ 0,001). Le
contrôle porte désormais sur des données anisotropes (shrinkage < 0,05), et le cas isotrope 40 × 7
sert à vérifier l'écrêtage à 1 de la formule de référence. Correction apportée par l'instance du
stream 05 (règles tranchées 4 et 5 de `prompts/wrapups/wrapup-05.md`), revérifiée numériquement lors
du pass de fix post-stream.

## C-repr-mp-K — K au bord de Marčenko–Pastur (2026-10-16)

Le prompt 06 fixe K « au bord de Marčenko–Pastur λ₊ = σ²(1 + √(N/T))² sur la corrélation ». Lecture retenue
(confirmée au GO, H1) : σ² = 1, trace/N d'une matrice de corrélation ; n₊ = nombre de valeurs propres de la
corrélation empirique de la calib au-dessus de λ₊, PC1 compris ; K = n₊ − 1, car PC1 est le canal marché et le
résiduel factoriel est PC2..PC(K+1). Sur les fenêtres de calib : K = 5 pour `d2_us97` (N/T = 0,1031,
λ₊ = 1,7452, six valeurs au-dessus) et K = 10 pour `d3_239` (N/T = 0,254, λ₊ = 2,2619, onze valeurs au-dessus),
soit les « marché plus dix facteurs » du prompt 18. La variante σ² = 1 − λ₁/N [Laloux et al., 2000], qui retire
le mode de marché de la variance de bruit, donnerait K = 9 (λ₊ = 1,1752) et K = 15 (λ₊ = 1,6256) ; elle n'est pas
retenue. K ≤ 0 déclenche une `ValueError` (sondes 2 et 8 de `prompts/plans/plan-06.md`).

## C-repr-whiten-lw — blanchiment par la covariance Ledoit–Wolf (2026-10-16)

Le prompt 06 demande des sorties « blanchies » et propose `shrinkage="ledoit_wolf"|None`. Défaut retenu (GO, H2) :
blanchiment par Σ̂_LW de la calib, la covariance de l'injecteur (`injection.fit_background`). Pour toute dérive δ,
en mode full, ½‖z(δ)‖² = ½δᵀΣ̂⁻¹δ, l'information journalière visée par `inject` (écart relatif 1,7e-16 sur la
calib de `d3_239`, sonde 5). Contrepartie : la variance de calib de chaque coordonnée vaut λ_S/λ_LW, entre 0,49 et
1,03 sur `d3_239`, et non 1 ; avec `shrinkage=None`, elle vaut 1 exactement.

## C-repr-layout — disposition des colonnes de l'ACP et règle tail10 (2026-10-16)

La colonne 0 de `z_odd` est le canal marché v₁ᵀx/√λ₁ dans les trois modes de `PCAOrthogonal`, y compris
« tail10 », et `channels` déclare la disposition (GO, H3) : PC1 n'est jamais écarté en silence (AGENTS.md), et
P3-KF lit le seul bloc résiduel. Pas de centrage : un décalage constant rendrait la transformation affine, donc non
impaire. « tail10 » (GO, H4) : m = plus grand nombre de dernières composantes dont la somme des valeurs propres
reste ≤ 10 % de tr Σ̂, sur les valeurs propres de la Σ̂ utilisée (Ledoit–Wolf par défaut) ; m = 46 sur `d2_us97`
et 123 sur `d3_239` (48 et 130 avec les valeurs propres empiriques, sonde 4).

## C-repr-even-heads — têtes paires (2026-10-16)

Le prompt définit la tête paire de l'ACP (carrés des coordonnées blanchies), pas celles des représentations de
degré 0. Décision (GO, H5) : z_even = z_odd² pour `PCAOrthogonal` et `CenteredRanks` ; z_even = [‖Px‖] pour
`DegreeZero`, une tête paire homogène de degré 1. Motifs : la mise prévisible de P3-CS (b) (prompt 07) lit
σ̂ = moyenne exponentielle de ‖Px_{t−1}‖, que Z fournit alors ; en mode full, Σ z_k² = 1, et les carrés de
`DegreeZero` seraient dégénérés.

## C-repr-rows — lignes extraites (2026-10-16)

Le prompt décrit `Z_odd` comme une matrice T × D. Décision (GO, H7) : la représentation est ajustée sur les lignes
de calib de `splits.yaml` et transforme les lignes allant du premier jour de pretrain à la fin du panel ; une valeur
non finie déclenche une `ValueError`. Sur `d3_239`, les lignes 0–1255 (2000–2004) n'appartiennent à aucun segment
et la ligne 0 n'a pas de rendement : `Z_odd` compte 5482 lignes, datées par `dates`, et le JSON déclare
`rows = [1256, 6738]`. Sur `d2_us97`, les 5154 lignes sont transformées. `d3_500` (13 % de NaN) n'est pas proposé
par la CLI : l'appelant y choisit un sous-panel complet.

## C-BAF-synthetic — dérive native d'un jeu synthétique (2026-10-16)

Le jeu D7 (BAF — Bank Account Fraud, Jesus et al., NeurIPS 2022 Datasets and Benchmarks) est
un jeu **synthétique** : les demandes d'ouverture de compte sont générées à partir de données
réelles, mais le jeu lui-même est artificiel. La dérive observée (augmentation du taux de
fraude de 0,87 % au mois 2 à 1,47 % au mois 7) est une **dérive native d'un jeu synthétique**.
Ne jamais décrire cette dérive comme « in-the-wild » ou « réelle » : les données sont
synthétiques, générées par un processus connu des auteurs du jeu.

## C-pipe-delay — convention de délai des pipelines (2026-10-16)

`alarms.csv` (stream 07) définit `delay = alarm_index − tau_star + 1` : le nombre de jours surveillés jusqu'à l'alarme
incluse, soit T_γ du Lemme 1 (convention d'E2 et de `jepadrift/floors.py`), la seule comparable aux planchers. Les
délais de l'Article B (`bilateral_delay`, `strict_cusum`, course de R15) comptent à partir de 0 : délai Article B =
`delay − 1`. Les portages de R15 gardent leur convention en interne (GO H1, `prompts/GO-stream-07.md`).

## C-pipe-null-targets — garanties sous H₀ et cibles des tests (2026-10-16)

Le prompt 07 demande un FPR sous H₀ « dans l'IC binomial à 99 % de la cible » pour P3-C, P3-CS (pari) et la lecture
anytime-valid de P2-C. Les lectures anytime-valid sont des e-détecteurs CUSUM (P2-C, P3-C, P3-CS b ; Prop. « floors »
(a), ARL₀ ≥ γ), un e-processus (P3-CS a, Ville : P₀(sup ≥ γ) ≤ 1/γ) et le CUSUM du LLR gaussien de P7 (borne seule)
(GO H2). Un e-détecteur à γ = 20 dépasse 1/γ sur 750 jours (FPR 0,71 pour P3-C, 0,29 pour P2-C, sonde 4 du plan) sans
violer sa garantie. Cibles retenues (GO H3) : borne de Lorden min(1, H/γ) testée à γ = 20H pour les e-détecteurs, 1/γ à
γ = 20 pour l'e-processus, niveau exact du treillis canal par canal pour P3-C (test net du Lemme 2 sur D6), α pour les
lectures calibrées. Région à 99 % : p ± z√(p(1 − p)(1/n + 1/n_cal)), z = 2,5758, où 1/n_cal (N_cal ou B tirages nuls)
porte le bruit du quantile empirique ; le recouvrement des fenêtres est ignoré. L'ARL₀ des e-détecteurs revient à E3.

## C-P2C-port — portage de R15 dans P2-C (2026-10-16)

`composition_for`, `worker_null_window_real` et `worker_race_h1_real` sont recopiés de
`exp_R15_cross_sectional_b.py` (segments AST identiques à l'octet). Adaptations (GO H4, H5) : (1) les fenêtres nulles du
bootstrap sont tirées dans les lignes antérieures au segment de surveillance (2005–2019 avant J4), alors que R15 lisait
le panel complet ; (2) une `SeedSequence` par tirage, clé `key + [1, i]`, au lieu des clés MD5 de R15 ;
`composition_for` garde la graine MD5 % 2³² de R15, car elle fixe la composition (sur D2, les titres agrégés sont ceux
de R15) ; (3) la lecture anytime-valid porte sur les signes bruts exacts (zéros tranchés par pièce : 2864 rendements
nuls sur D2 avant 2020), sans recentrage par médiane ; (4) pour les fonds D6, le seuil se calibre sur une symétrisation
(λ_boot = 33,25 contre 20,05 sur le brut à K = 20, sonde 7). L'identité R15 (`results/identity/articleB_R15.csv`)
reproduit ρ̂, K_eff, λ_boot, FPR_boot et la course à c = 0,25 avec les graines de R15 ; le panel 2005–2025 n'y sert qu'à
cette reproduction (`C-identity-R15`).

## C-P3D-windows — fenêtres nulles de P3-D (2026-10-16)

Le seuil de P3-D est le λ minimal dont le FPR à l'horizon H est ≤ α sur toutes les fenêtres de longueur H du segment de
calib, énumérées (GO H8) ; λ_iid vient de trajectoires i.i.d. (χ²_D − D)/√(2D) et Γ_z^op = λ_req/λ_iid. L'énergie
blanchie n'est pas stationnaire entre 2005 et 2019 : moyenne de q_t de 0,469 (factor) et 9,47 (full) sur le pretrain
contre 0,024 et −0,332 sur la calib, d'où Γ^op ≈ 191 et 2346 sur des fenêtres 2005–2019, contre 7,64 et 25,19 sur la
calib (H = 500). La calib compte 941 jours : un horizon plus long lève une `ValueError`, et l'horizon de 2000 jours
d'E1 demande une décision au stream 12 (`null_rows="pre_monitor"` reste disponible).

## C-P3CS-design — mises et calibration de P3-CS (2026-10-16)

(a) Les pivots s_{t,k} = u_kᵀPx_t/‖Px_t‖ sont petits dans les directions de faible variance (médiane |p| = 0,057 en full
sur D2) : l'e-processus de pari utilise les mises ±{0,1 ; 0,25 ; 0,5 ; 0,9}, jusqu'à la borne de validité |λ| < 1,
et le CUSUM « à design fixe » divise chaque pivot par son RMS de calib (poids figés), puis retient le maximum sur
directions et côtés ; seuil par inversion de signe, B = 2000, un signe par jour commun aux directions (GO H9). Avec
les mises |λ| ≤ 0,4 du stream 04 et sans standardisation, une F2 de SR = 8 n'était détectée qu'à 35 % et 17,5 %
(H = 2000), contre 100 %. (b) σ̄ = médiane de calib de ‖Px_t‖, c_j = 2η₀_j·σ̄, σ̂ repart de σ̄ au premier jour surveillé
puis suit une moyenne exponentielle de demi-vie 20 ; λ_{t,j} = min(0,5 ; c_j/σ̂_{t|t−1}) (GO H10). La variante « rangs »
est reportée (GO H14).

## C-P3C-mixture-gate — test d'indépendance de l'option mélange (2026-10-16)

L'option mélange sous-gaussien de P3-C n'est autorisée que si |ρ̂| < 3/√T sur toutes les paires de flux de signe
résiduels de la calib (règle littérale du prompt, GO H7) ; un échec lève `ValueError`, sans repli. Sur D2 le test
échoue dans les deux modes : factor, 1 paire sur 10 (max |ρ̂| = 0,1308 contre 0,0978) ; full, 13 paires sur 4560. En
full, il échouerait même sous indépendance, par multiplicité (P ≈ 0,9973^4560 ≈ 4e-6) : une correction de multiplicité
serait un changement de spécification.

## C-identity-R15 — périmètre de l'identité R15 (2026-10-16)

Le prompt 07 demande ρ̂ et K_eff pour K ∈ {5, 10, 20} à 1e-12. L'identité les étend (GO H12) aux compositions, à
K_eff_ana, à λ_boot et FPR_boot, et au DetRate et à l'ADD de la course à c = 0,25, avec les graines de R15
(`get_deterministic_seed`, recopié). Résultat : 56 cellules, toutes dans la porte de 1e-12, dont 54 identiques au bit ;
ρ̂ et K_eff_ana à K = 10 diffèrent d'un ulp (2,1e-16 et 1,5e-16, ordre de sommation de `np.corrcoef`). Le panel D2
complet (2005–2025) n'y sert qu'à reproduire les valeurs publiées de l'Article B, comme l'identité R01 du stream 04 ;
aucun choix de conception n'en dépend.

## C-audit-debias — débiaisage du SR² de dérive et IC bootstrap (2026-10-17)

La formule du prompt 11, SR²_S = 252·[Δμ̂ᵀΣ̂⁻¹Δμ̂ − d(1/n₁ + 1/n₂)]·(n − d − 1)/n, garde un biais de
252·d·c·(d + 1)/ν, avec c = 1/n₁ + 1/n₂ et Σ̂ la covariance intra-phase poolée à ν = n₁ + n₂ − 2 degrés de liberté
(E[Σ̂⁻¹] = ν/(ν − d − 1)·Σ⁻¹) : 3,8 en SR² à d = 30 et n₁ = n₂ = 250. Décision (GO H8) : `sr2_debiased` =
252·[D̂²(ν − d − 1)/ν − d·c], sans biais sous normalité, sert aux IC, aux médianes, à la part du budget et aux gains
prévus ; la formule littérale reste dans `sr2_spec`. `test_debiased_sr2_unbiased` (2000 réplications) vérifie l'absence
de biais et chiffre celui de `sr2_spec`. IC : chaque réplique bootstrap rajoute le bruit d'échantillonnage à la
différence de moyennes observée, si bien que les répliques se placent environ 252·d·c au-dessus de l'estimation
débiaisée (exécution rapide sur D2, `lt_spy` : médiane `idio` de 16,6 pour un IC percentile brut de [175 ; 582]).
L'IC retenu est l'intervalle percentile à 95 % décalé du biais bootstrap, moyenne(répliques) − estimation
[Efron & Tibshirani, 1993, An Introduction to the Bootstrap, ch. 10] ; `test_drift_ci_brackets_the_estimate` échoue
avec le percentile brut et passe avec le décalage. Le GO H9 disait « IC percentile » ; le prompt dit seulement « IC par
bootstrap par blocs mobiles ».

## C-audit-subspaces — sous-espaces de dimension ≤ 30 et caractéristiques (2026-10-17)

Le prompt demande le « résiduel complet » (96 dimensions sur D2, 238 sur D3) avec d_S ≤ 30. Décision (GO H7) :
PC2..PC(K+1) forment `factor` ; le bloc idiosyncratique PC(K+2)..PCN est découpé en blocs d'au plus 30 PC consécutives
(`idio:b1`, …) ; `idio` est la somme des blocs et `residual_full` = `factor` + `idio`. Les covariances entre blocs
sont ignorées : la somme est exacte si les blocs sont non corrélés dans les phases. Caractéristiques (GO H4) : D3
seulement (D2 n'a pas de caractéristiques), les 15 colonnes de `chars.parquet`, NaN → 0 (lecture de
`C-inject-F2-nan`), projection euclidienne sur le sous-espace idiosyncratique (I − V_fV_fᵀ, V_f = PC1..PC(K+1)),
normalisée chaque jour ; le sous-espace `chars` est ainsi disjoint du marché et des facteurs. Les directions F2 de N2
suivent en revanche la construction de `inject` (résidu GLS sur les chargements).

## C-audit-transitions — transitions des datations SPY (2026-10-17)

(GO H6) Lignes SPY des trois `phases_*.csv`. La phase k regroupe les jours datés dans (début_k, fin_k], convention de
`T_days` ; la frontière fin_k appartient à [2005-01-01, 2019-12-31) ; les phases sont découpées à la fenêtre ; une
transition est gardée si n₁ et n₂ ≥ 20 (un bloc de bootstrap). Sur SPY, `lt_spy` et `symmetric` sont identiques
(30 phases) : les deux sont traités, sans déduplication. Transitions gardées : 9 (`lt_spy`, `symmetric`) et 10
(`strict_ps`) ; `lt_spy` perd 2008-10-27, 2008-11-04 et 2008-11-20 (phases de 6 et 12 jours). Mise en garde : les
frontières sont des points de retournement de SPY datés ex post ; le débiaisage du bruit ne corrige pas cette
sélection, qui gonfle le SR² du sous-espace marché.

## C-audit-ceilings — lectures de N1, N2 et N3 (2026-10-17)

N1 (GO H10) : s²_t = moyenne des carrés des coordonnées blanchies du bloc PC(K+2)..PCN (blanchiment Ledoit–Wolf de
la calib) ; N1 = moyenne(s²)·moyenne(1/s²) sur 2005–2019, brute et corrigée de la loi χ² (facteur (d − 2)/d). N2
(GO H11) : Σ_t = Ledoit–Wolf des 60 lignes précédentes ; directions F1 = colonnes de B (`fit_background(X_calib,
K + 1)`, PC1 compris), F2 = résidus GLS des caractéristiques ; Σ̄ et ā sont moyennés sur les mêmes jours, d'où un
rapport ≥ 1 exactement. Ce rapport contient aussi l'écart de Jensen dû au bruit d'estimation de Σ_t (60 jours pour
97 ou 239 titres) : il majore le gain du canal. N3 (GO H12) : loi t multivariée de localisation nulle ajustée par
ECME [Liu & Rubin, 1995, Statistica Sinica 5, 19–39] ; variante citée `mvt_static` (bloc blanchi par la calib, lecture
littérale) ; `mvt_garch` (chaque coordonnée divisée par son σ̂_{t|t−1} GARCH) et `t_garch` (loi t univariée par
direction) restent dans le CSV.

## C-audit-gains — gains prévus (2026-10-17)

(GO H14) Les formules du tableau « Gains prévus » du plan v4 (§2.4) sont évaluées sur ρ̂ (corrélation moyenne des
rendements sur 2005–2019), ρ̂_signe, N, K et les médianes des SR² débiaisés : G(1→2) = N/(1 + (N − 1)ρ̂), et sa
version en signes ; G(2→3, F1) = SR²_factor/SR²_market, taxe M(1)/M(K) ; κ̂² = (SR²_idio/SR²_market)(1 − ρ̂)/
(1 + (N − 1)ρ̂), d'où G(2→3, F2) = SR²_idio/SR²_market, taxe M(1)/M(N − 1) ; G(1→3) = N/(1 + (N − 1)ρ̂) + κ̂²N/(1 − ρ̂),
sans taxe. M = `floors.mixture_multiplier`. Une médiane ≤ 0 (R9) donne NaN, sans substitution des valeurs de
planification ; `test_planning_table_reproduced` redonne les valeurs du tableau (2,46 ; 3,74 ; 16,4 ; 42,9 pour
N = 97 et κ = 0,5).

## C-worktree-data-raw — `data/raw/` dans les worktrees de stream (2026-10-17)

La recette d'AGENTS.md (un lien absolu unique `data/raw` vers l'arbre principal) fait échouer
`tests/test_data_eurofidai.py::test_gitignore_blocks_eurofidai` dans tout worktree : `git check-ignore` refuse un
chemin situé au-delà d'un lien symbolique (« pathspec 'data/raw/eurofidai/x' is beyond a symbolic link », y compris
avec `--no-index`). Le worktree du stream 11 utilise un répertoire `data/raw/` réel qui contient des liens absolus vers
`d3_yf` et `baf` seulement : aucune donnée EUROFIDAI n'y est exposée, et les trois tests EUROFIDAI sur données réelles
y sont sautés (D4 absent). Le partage par liens absolus reste celui d'AGENTS.md, un niveau plus bas.

## C-audit-n2-noise — bruit d'estimation de N2 : fond permuté et valeur nette (2026-10-18)

Le GO 11b demandait de mesurer le bruit de N2 sur des fonds D6 (`injection.symmetrize`) et de rapporter
`value − bruit`. Décision du chercheur (2026-10-18) : le fond « bruit seul » est une **permutation aléatoire des jours
entiers** de 2005–2019. D6 multiplie chaque jour par un signe de Rademacher : |x_t|, les corrélations transversales et
le clustering de volatilité survivent, donc la dynamique de Σ_t aussi ; une sonde le confirme (rapport N2 de PC1 :
5,44 sur D6 contre 5,54 sur D2, 11,2 contre 11,33 sur D3). La permutation garde la coupe de chaque jour et efface la
dynamique temporelle : chaque fenêtre Ledoit–Wolf de 60 jours estime le même Σ̄, et le rapport y mesure l'écart de
Jensen pur de l'estimation. Seules les lignes de X sont permutées ; les directions F1 et F2 gardent l'ordre du
calendrier. B = 2000 fonds, graines `SeedSequence([11, 11, crc32(jeu), b])`, calcul parallèle indépendant du nombre de
processus. Valeur nette : `lw60_net` = `lw60` / `lw60_shuffle` (écart de Jensen multiplicatif ; vaut 1 sous le nul et
annule le facteur de variation des directions F2, qui ne dépend pas de l'ordre des jours), et non la différence du
GO. Schéma inchangé : variantes `lw60_shuffle` (médiane du rapport sur les fonds) et `lw60_net` dans
`channel_ceilings.csv`. Borne documentée : sur données i.i.d. gaussiennes, le rapport « bruit » n'est pas proche de 1
aux dimensions réelles (3 à 8 à N = 97/239 et 60 jours), puisqu'il mesure le bruit lui-même ; sous un Σ constant, la
valeur nette vaut 1 (`test_n2_noise_null_and_workers`), et elle dépasse 1,5 avec des régimes de volatilité
(`test_n2_noise_volatility_regimes`).

## C-audit-placebo — frontières placebo par rotation circulaire et facteur de sélection (2026-10-18)

Décision du chercheur (2026-10-18) : chaque jeu placebo est une **rotation circulaire** de la chaîne réelle des phases
SPY dans la fenêtre (départ uniforme, retour au début de la fenêtre) ; le multiset des (n₁, n₂) et le nombre de
transitions sont ceux de la datation réelle, et la phase qui enjambe le joint rassemble ses deux segments de lignes.
P = 2000 rotations, graines `SeedSequence([11, 12, crc32(jeu), crc32(datation)])` ; IC de la médiane placebo par
bootstrap i.i.d. des P médianes (B tirages, `SeedSequence([11, 13, …])`). Constat d'exécution : les médianes placebo du
SR² de marché débiaisé sont négatives (l'estimateur débiaisé a une loi asymétrique dont la médiane est négative près de
0), si bien que le rapport réel/placebo du GO n'a pas de sens. `selection_factor` vaut donc NaN quand la médiane
placebo est ≤ 0, et le CSV dédié `placebo_selection.csv` rapporte aussi `selection_excess` = réel − placebo (unités de
SR²) et `p_placebo` = (1 + #{placebo ≥ réel})/(1 + P). Les tests suivent : contrôle positif (frontières sur les vrais
changements de moyenne : excès > 0, p < 0,05) et nul (panel sans structure : p dans [0,025 ; 0,975]) dans
`test_placebo_controls` ; sur les données réelles, excès > 0 et p < 0,05 pour les deux jeux et les trois datations
(`test_placebo_selection_committed`), à la place de « rapport > 1 ». Niveau `placebo` ajouté à
`drift_sharpe_transitions.csv` (colonnes inchangées).

## C-D3-survivor-correction — biais de survie de D3 (2026-10-18)

Correction de `C-D3-survivor`. Un univers formé des constituants actuels du S&P 500, projeté en
arrière jusqu'en 2000, est biaisé par la survie : un titre n'y figure que parce qu'il a survécu et a
rejoint l'indice. `d3_239` (les 239 plus longs historiques parmi ces constituants, `C-D3-no239`) l'est
doublement. Portée : les expériences sur fonds symétrisés D6 avec dérives injectées en dépendent peu ;
les mesures sur données brutes (recensement, E8, placebos) héritent du biais et servent d'appui, jamais
de preuve de détectabilité. Aucune donnée n'est modifiée.

## C-D4-survivor — sélection de D4 (2026-10-18)

D4 contient 498 titres EUROFIDAI retenus pour au moins 5 000 observations entre 2001 et 2026 (places
AMS, BRU, EPA, LSE, MIL, XET). Cette sélection sur la longueur d'historique est une sélection par la
survie ; l'export ne fournit ni date de radiation ni statut (radiations inférées par l'absence de
données), et MIL n'a pas de données pour 2024–2026. `in_universe` couvre 91 % des cellules : les
appelants choisissent des sous-panels complets sur leur fenêtre (`inject` exige un panel fini). D4 n'a
pas de secteur GICS : F2 n'y utilise que les quatre caractéristiques continues.

## C-stats-drift — statistiques de dérive partagées dans `jepadrift/stats/drift.py` (2026-10-22)

Stream 8b. `debiased_sr2`, `mbb_indices`, `transitions` et `rotate_phases` quittent
`experiments/audit_information.py` sans modification de corps, et `_ci` y est exportée sous le nom
`shifted_percentile_ci` (seule la ligne `def` change). Le transfert verbatim impose de déplacer aussi le helper `_sr2`
(appelé par `debiased_sr2` et par `drift_rows`) et les constantes `WINDOW`, `MIN_PHASE` et `BLOCK` que lisent ces corps :
`transitions` reste donc borné à la fenêtre 2005–2019 dans le module partagé, et une expérience postérieure à J4 (E8)
devra le paramétrer. L'audit importe ces noms et garde les anciens (`tests/test_audit.py` inchangé). Contrôles : les
SHA-256 des segments `ast.get_source_segment` des neuf nœuds égalent ceux de `5048a96` (figés dans
`tests/test_drift_stats.py`), le reste de l'AST de l'audit est inchangé, et les neuf CSV de
`audit_information.py --datasets d2_us97 d3_239 --quick` sont identiques au SHA-256 avant et après le déplacement.

## C-e10-backgrounds — E10 backgrounds: D5 grid, local GJR and shock generator, matched null, raw placebo (2026-10-22)

Stream 27, E10 linear stage (`prompts/plans/plan-27.md`, GO `prompts/GO-stream-27.md`). D5: each replicate is an
independent path of 941 calib rows (the D2 calib length) followed by H = 750 monitored rows, around the base
`sim.garch_panel(alpha = 0.08, beta = 0.90, nu = 7, factor_rho = 0.40, N = 97)`, one factor varied at a time:
t_nu with nu in {3, 4, 5, 7}; GJR leverage gamma in {0.05, 0.10} with alpha = 0.08 - gamma/2 and beta = 0.90
(persistence 0.98, unit variance), the indicator being the sign of the previous cross-sectional mean; a compensated
common negative jump in the factor, g_t = sqrt(1 - w) N(0, 1) + sqrt(w) (p - 1{U < p}) / sqrt(p (1 - p)) with
w in {0.25, 0.50} and p = 0.05 (mean 0, variance 1; q of the factor 0.525 and 0.561, which brackets the raw PC1 rates);
zero returns by rounding to a tick 2 Q_p0(|x|) estimated on a 20,000-day pilot path of the base generator, applied after
the F1 injection (p0 in {2 %, 5 %}). Decision B3: the GJR and shock terms live in a local generator
(`experiments/e10_robustness.py::d5_panel`), which reproduces `sim.garch_panel` bit for bit when gjr = 0 and no shock
(test), so that `jepadrift/sim.py` stays untouched while stream 13 may extend it. P3-C on D5 uses an integer K = 5:
the one-factor panel has a single eigenvalue above the Marchenko-Pastur edge, where `K = "mp"` would give 0. On D6, every
replicate fits P3-C with K fixed at the MP value of the raw calib basis (5 on d2_us97, 10 on d3_239): a symmetrization
changes the centring, and an eigenvalue near the edge could otherwise change the number of channels between replicates.
Reference null levels: each valid D5 generator (base, t_nu, GJR, zeros) is its own attained level by direct simulation;
only the shock receives a matched valid generator, the same generator with one Rademacher sign per day shared by all
assets applied in the loop (its recursion reads past magnitudes only, so it equals the post-hoc symmetrized path bit
for bit, test), with the state and q_hat refitted. GJR is not re-symmetrized: keeping the magnitudes would not
reproduce a generator in which the past sign drives future volatility. Raw placebo: every 750-day window of the pretrain
rows, fitted on the later calib rows (retrospective, descriptive); the `half` arm is referred to the same window
symmetrized with fresh daily signs and the same state; the `qhat` and `zero_neg` arms keep the raw calib rates and form
descriptive contrasts, without fpr_ref nor inflation.

## C-e10-streams — E10 streams: shared bits, recentred arms, zero = negative arm, P1-C outside the registry (2026-10-22)

Both arms of a pipeline use the same realized bits B = 1{y > 0}, every tie y = 0 broken by an independent fair coin
of a local PRNG; `half` centres B at 1/2 and `qhat` at q_hat_u, the calib mean of B under the same coin convention,
frozen in [0, 1]. The anytime-valid input is x = (B - c) / max(c, 1 - c) in [-1, 1], never 2 (B - q_hat); the exact
reading of a recentred stream keeps the lattice threshold 9.1 and claims no exactness (a recentred stream is not a
two-point +-1/2 stream). Article B's zero = negative rule is a distinct arm (`zero_neg_half`, `zero_neg_qhat`), on
P1-C only and on backgrounds with zeros: its sign-stream null is invalid (P(B0 = 1) = (1 - p0)/2 under symmetry) and it
carries no FPR guarantee. P1-C reuses the monitors core (`cusum.P1["P1-C/C"]`, `streams`, `lattice`, `eprocess`)
without a registry entry, on 20 assets (D5: columns 0-19; D6 and raw: drawn once per dataset with
SeedSequence([27, crc32(dataset), 1])). The P3-C `half` arm runs through `pipelines.run_pipeline` on a Z input; its
exact state is the anytime-valid state with the lattice keys of `_cal_p3c` (equal to `fit_pipeline` on the exact spec,
test), and the `qhat` arm reuses the bits drawn with run_pipeline's coin convention SeedSequence([*seed, 7]) (bit
identity, test).

## C-e10-readings — E10 readings, references, intervals and gains (2026-10-22)

H = 750, gamma_H = `pipelines.horizon_gamma(750)` = 15,000, alpha = 0.05; exact reading at the lattice level 0.043947
(L = 45, threshold 9.1); F1 at SR in {4, 8, 16} (convention a), anytime-valid reading only. Every cells row carries
`null_valid`, `design` (prospective, symmetrized, retrospective, iid_scenario) and `reference_kind` (level_exact,
self_valid, matched_valid_generator, symmetrized_window, descriptive_contrast, none). `fpr_iid_mc` is a Monte Carlo
estimate on independent fair coins (design iid_scenario): it estimates the exact law only for the `half` arm of a single
stream under a valid null, and its `half` exact value must lie within the 99 % binomial region of 0.043947 (test and
log); for `qhat` and the P3-C dictionary it is an iid reference scenario only. `fpr_pred_iid` = lattice exceedance at
the observed mean bit rate is an iid-bit reference, reported as `pred_gap` without any conformity criterion. Intervals:
Wilson 95 % per unit on independent replicates (D6 replicates are i.i.d. conditionally on the panel); paired bootstrap
for the shock inflation and the gains; Wilson on symmetrized raw windows is conditional on the state and the magnitudes
and approximate (`ci_kind = wilson_conditional_approx`); on overlapping raw windows, deff = `gamma_spectral(series,
L = H - 1)`, with an interval only if deff is finite and 1 <= n_eff = n / deff <= n (an estimated deff below 1 also gives
NA), and the raw-minus-symmetrized inflation interval is NA whenever the raw rate interval is. Gains: RMST_P1 / RMST_P3
is a ratio of delays restricted to H, a lower bound of the ADD ratio only when P3-C is never censored
(`bounds_add_ratio`); the ratio of median delays is reported when both detection rates exceed 1/2; the median asset is
the rank (m - 1) // 2 by F1 RMST (selected on F1 without aiming at the best), the best asset is an exploratory oracle;
each gain carries the H0 FPR of the same asset and of the P3-C dictionary with their paired difference. No equal false
alarm is claimed (decision B2).

## C-e3-design — E3 design: strict real window, E1 tickers, scope, shared draws (2026-10-28)

Real rows are the pre-monitor rows dated 2005-01-04..2019-12-31. Rows before 2005-01-04 are excluded only as declared
in `EXCLUDED_DAYS` (none on d2_us97; 2005-01-03 on d3_239), counted in the run log; any other early row raises,
then `check_window` raises on any row outside the window, so nothing is truncated silently. Both panels keep 3,774
rows and 941 calib days. The P1 readings use the five J2 (i) titles of E1, `pipelines.composition_for(5, N)`: d2_us97
[24, 71, 56, 46, 75] = COST, SHW, SO, MDLZ, PSA and d3_239 [60, 177, 141, 116, 184] = CASY, KEY, GPC, ERIE, LRCX,
frozen as literals in `tests/test_e3.py` as in `tests/test_e1.py`. D5 covers the univariate P1 readings, the overshoot
and the encoders (`sim.py` unchanged: t7 paths by `sim.Garch`, Gaussian paths by `garch_panel(nu=None)`). P3-C, P3-D
and P3-CS run in factor mode; D6 fits fix K at the raw MP edge (5, 10), as E10. The mixture cell waits for the Holm gate
of stream 12. Every local CUSUM restarts at S_0 = 0 at the start of its window or path (tests against the scalar
Article B ports, prefix invariance, non-vacuity); E3 imports only `symmetrize` from `injection` and every record carries
family H0. Cells share draws (fit symmetrizations and panels, P1-C replicates across tickers and arms, D5 paths across
H, ARL0 paths across gamma and types, overshoot paths across statistics, encoder draws across L): intervals and regions
are marginal, and counts over cells are descriptive, without binomial law, p-value or joint probability under
independence; only the expectation by linearity and the union bound, valid under any dependence, are reported.
`wilson` moved verbatim from E10 to `jepadrift/stats/intervals.py` (AST identity with `c284823`, `tests/test_e10.py`
unchanged).

## C-e3-readings — E3 readings, calibration samples and intervals (2026-10-28)

P1-C: exact arm (ties by an independent coin) at the lattice threshold `select_threshold(0.05, H=H)["threshold"]` (9.1
at H = 750, 10.3 at H = 2,000; exact levels 0.0439467 and 0.0456695), and the Article B label arm 1{y > 0} - q_hat
with q_hat from the calib rows of one fit symmetrization (D6) or from the clean days (D5), a reference without
exactness. P1-D on D5: the 941 clean days give mu = mean(r^2), sigma = std(r^2) and Gamma_hat (R01 QMLE); lambda_req
and lambda_iid (global permutation of the monitored energies) are calibrated on 20,000 calibration paths, and the FPR at
lambda_req, lambda_iid * Gamma_hat_r, lambda_iid and 65 * Gamma_hat_r is measured on 20,000 independent evaluation
paths (SeedSequence roles `d5|<background>|cal` and `d5|<background>|eval`), with a Wilson interval (deff = 1) and the
columns `n_cal` and `n_eval`; P1-C on D5 is read on the evaluation paths. Real P1-D (five tickers), P3-D and the raw
placebos calibrate on their own sample or read overlapping windows of one trajectory: `ci_kind = na`, descriptive,
outside any gate. The P2-C bootstrap (R15, H = 750; H_ref + H = 1,250 exceeds the 941 calib days, hence an explicit
`null_rows = pre_monitor`) is calibrated on the fit symmetrization and read on fresh symmetrizations of the same panel:
its Wilson interval is conditional on the panel and on the threshold (`calibrated_conditional`), and 1/n_cal
understates its calibration noise. Encoders: lambda_iid from independent i.i.d. N(0, 1) paths (`n_cal`), FPR on
independent replicates. e-detectors read at gamma_H = H/alpha; the P3-CS (a) e-process at gamma = 1/alpha = 20 by
Ville's inequality is an FPR(H) reading, distinct from the ARL0 gamma = 20. `fpr_threshold` sorts precomputed CUSUM
peaks instead of bisecting (`required_threshold`); both agree to 1e-6 (test). `e3_j2_check.txt` is a secondary
calibration check of prompt 13 item 7 at 20,000 replicates, without J2 verdict: the primary J2 (i) verdict is E1's
(stream 12) at 2,000 replicates.

## C-e3-arl0 — E3 ARL0 of the e-detectors (2026-10-28)

Backgrounds: fair coins (one +-1 coin per monitored column; P3-CS (b) with constant stakes 2 eta0_j), circular D6
(uniform start, rows (s + t) mod n, a fresh Rademacher sign every day, the registry stream built on one unrolled record
so that the detector and the EWMA continue at the seam; base fitted on one symmetrization) and raw starts (descriptive,
censored at the end of the rows). One path of 60 * max(gamma) steps per replicate is read at gamma in {20, 100, 252}
for both types (common random numbers). Restricted mean mu_R = mean of min(T, 60 gamma), SE with deff = 1 and lb99 =
mu_R - 2.326 SE: PASS iff lb99 >= gamma, else INDETERMINATE, never FAIL, since E3 has no valid bound on the tail
E[(T - 60 gamma)+]; the restricted-mean deficit gamma - mu_R and its 99 % interval are descriptive. Tail-free check at
the bounded stopping time sigma = min(T, 60 gamma): E[M_sigma] <= E[sigma] (equality for the SR type). The per-row 99 %
lower bound of mean(M_sigma - sigma) is descriptive: under the exact SR equality it exceeds 0 in 1 % of the rows (one
coin row of 33 SR rows did so in the first --quick run, z = 3.04). A violation is certified only when the Bonferroni
lower bound over the m classified rows, at family-wise level 1 % (union bound, valid under any dependence), is above 0
(`ineq_lb_fw`, `ineq_violated`). This replaces the per-row rule of plan 13 (H14); the change was made after that quick
run and before the full run, and it does not touch any FPR, ARL0 or overshoot reading.

## C-e3-overshoot — E3 overshoot penalty reproduction (2026-10-28)

Primary gate: replicates 0..1,999 of each cell, |ARL0_MC/ref - 1| <= 5 % against the Monte Carlo references of plan v1
(2,587, 889, 1,894, 669, 213, 214), seeds fixed in `configs/e3.yaml` (`seed_labels`) before any run, one full run, no
rerun. The exact i.i.d. ARL0 (Brook-Evans with m = 2,000: 2,553.1 and 1,962.8; lattice: 213.09) differ from the
references by -1.3 % and +3.6 %, the attribution of any i.i.d. FAIL. A censored primary cell is INDETERMINATE unless its
restricted mean already exceeds the band. Under `--quick` the first 200 trajectories are labelled `quick_diagnostic`
and carry no gate; the pre-specified D8 decision uses the first 2,000 trajectories of the full run. SE = sd /
sqrt(n_eff) with n_eff = n / deff and deff = 1 (independent replicates), as for the ARL0 rows. Diagnostics: all 20,000 replicates, Gamma^spec of x, and lambda_req of the
GARCH paths at the exact i.i.d. ARL0 (an upper bound under censoring), hence Gamma^op.

## C-e3-encoders — E3 window encoders (2026-10-28)

z_t = mean of u'x over L days, L in {1 (daily control), 5, 20, 60}; the L - 1 earlier days are an input delay and the
CUSUMs restart at the first monitored day. Backgrounds: D5 i.i.d. N(0, 1) (Gamma_z = L exactly) and the market channel
of SYM-d2_us97. Gamma_z^spec is reported at the default Bartlett bandwidth of the prompt and at 10 L (diagnostic): the
expected value L is reached only with a bandwidth of order L.

## C-e3-sizes — E3 sizes and cost (2026-10-28)

Full run: 20,000 replicates per sign cell and per `null_check` spec, 20,000 D5 calibration paths and 20,000 D5
evaluation paths per background, 20,000 ARL0 paths per structure, 2,000 primary overshoot replicates within 20,000, and
20,000 encoder replicates; `--quick` uses 500 / 500 / 200 / 200 with every real unit. The `--quick` CPU time projects
the full run at about 7.4 CPU hours, under one wall hour at `--jobs 24`: no size reduction is applied. The script
writes the CPU seconds of each block to its run log.

## C-e3-d8-fail — E3 overshoot gate D8 fails on iid/first_order_d1_l3, archived without rerun (2026-10-29)

Observed (established): the single full run of 2026-10-28 (`results/e3/e3_overshoot.csv`, SHA-256 1ca7c3ae..., the
hash recorded in `logs/e3/run.log`) fails the pre-specified primary gate D8 (replicates 0..1,999 of each cell,
|ARL0_MC/ref - 1| <= 0.05 for every cell) on `iid/first_order_d1_l3`, the one-sided strict first-order CUSUM with
delta = 1 and lambda = 3 on i.i.d. N(0, 1) paths: ARL0_MC = 1,994.0665 (SE 43.592, deff = 1, n_eff = 2,000) against the
reference 1,894, relative gap +0.0528334213 > 0.05, with no censored path (T_max = 40,000). It is a FAIL by excess,
not an INDETERMINATE cell, and D8 fails as a whole. The five other primary cells pass, all uncensored: relative gaps
-0.0124 and +0.0349 (i.i.d. first order delta = 0.5 and sign), -0.0367, -0.0382 and -0.0234 (GARCH first order
delta = 0.5, delta = 1 and sign). The plan required a stop before commit on a D8 FAIL (`prompts/STOP-stream-13-D8.md`);
the researcher's archive GO of 2026-10-29 (`prompts/GO-stream-13-archive.md`) lifts only that stop. The result is
committed as a FAIL: no E3 or `--quick` run, new draw, selective rerun, threshold, tolerance or reference change, and
no reinterpretation of the primary gate.

Attribution (plan D8 and section 15; descriptive, it does not change the gate outcome). Established: the reference
1,894 is a Monte Carlo value of plan v1 with unknown seeds and unknown Monte Carlo error; it lies 3.50 % below the
Brook-Evans i.i.d. value 1,962.7935 (m = 2,000), and the band [1,799.3, 1,988.7] leaves that value 25.9 units, 0.59
primary SE, under its upper edge. Plan 13 section 6 put the marginal probability of a FAIL of this cell under correct
code at about 27 % (normal approximation; 0.276 with the measured SE) and bounded the probability of at least one FAIL
among the six cells, whose statistics share paths within a background, by 0.27 <= P <= 0.83. Descriptive: the primary
mean lies +0.72 SE above the Brook-Evans value and +2.30 SE above the reference, and its 95 % interval
[1,908.6, 2,079.5] contains the first and excludes the second; the 20,000-path diagnostic, a superset of the primary
paths and not an independent sample, gives 1,964.2627 (SE 13.93), +0.11 SE from the Brook-Evans value. Hypothesis (not
established): the FAIL combines the Monte Carlo deficit of the reference with a +0.72 SE deviation of the primary
sample. Insufficient evidence: the absence of a defect in the overshoot simulation. `tests/test_e3.py` checks the
overshoot run lengths against the scalar Article B port `strict_cusum` on the same paths and the Brook-Evans values
against the tables; no test compares a Monte Carlo ARL0 with its Brook-Evans value. The GARCH first-order references
(889, 669) have no exact value: their passes are relative to Monte Carlo references of unknown error.

Consequence: E3 does not reproduce the plan v1 overshoot references within the pre-specified tolerance, so the
overshoot table is not a reproduction of plan v1. Replacing the reference by the Brook-Evans value, widening the
tolerance or reading the 20,000-path diagnostic as the gate after seeing the result would reinterpret the primary
gate; none is done. D8 covers the overshoot cells only (`e3_overshoot.csv`); the other E3 files carry their own
classifications.
