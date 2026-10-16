# GO — Stream 05 (injections F1–F4, fonds D5/D6) : revue du plan et réponses aux hypothèses

Date : 2026-10-16.
Destinataire : instance Claude Code en charge de l'implémentation du stream 05
(`prompts/streams/prompt-05-injections.md`).
Plan concerné : `prompts/plans/plan-05.md` (déjà enregistré avant exécution, en attente de GO).

## Instruction préalable — à exécuter AVANT l'implémentation

Intégrer ce GO dans `prompts/plans/plan-05.md`, section « Décision GO intégrée » (Tâche 0 du plan),
avant toute implémentation. Lors de l'intégration :
- mettre la base du plan à jour : `b74ad6c` → `9a5d76b` (pass de fix du stream 04 ; aucun
  chevauchement de fichiers avec le stream 05) ;
- supprimer le `# noqa: E402` sur la ligne d'import d'E2 (inerte : `make check` ne lint que pyflakes,
  qui n'implémente pas E402 ; la règle « aucun commentaire sauf `# ponytail:` » s'applique ; l'import
  modèle `from jepadrift import floors as fl` n'en porte pas).

## Verdict

**GO.** Le plan est conforme au prompt 05 sur tous les points : déplacement E2 avec hash inchangé
(`make j1` avant/après), générateurs D5, D6, `inject` F1–F4 sur rendements uniquement, conventions
(a)/(b), onset et `tau_star.json`, tests du item 7, livrables, contraintes numpy/scipy, générateurs
passés explicitement, aucune injection en espace latent. Extensions justifiées : Ledoit–Wolf dans
`jepadrift/stats/covariance.py` (partagé avec les représentations, streams 06/11) ; `nu=None` pour
innovations gaussiennes (contrat stream 13) ; pinning octet par octet du code déplacé ; champs `meta`
pour la reconstruction de Δ (oracle P7, stream 07). Formules F4 revérifiées analytiquement
(déformation d/2·(r−1−ln r) ; rotation ½ sin²θ (λ_i−λ_j)²/(λ_iλ_j)). Discipline pré-J4 respectée :
tests sur `d3_239` limités aux lignes 0–5030 (≤ 2019-12-31), estimations sur la calib 4090–5030.

Le canal retenu est ce fichier (prompt destiné à l'instance), et non l'édition directe de
`prompts/plans/plan-05.md` : le plan est déjà enregistré (règle C-plan-recording, AGENTS.md:86), sa
Tâche 0 prévoit l'intégration de la décision GO par l'instance elle-même, et la trace de décision
reste dans le dépôt (précédents `GO-stream-03.md`, `GO-stream-04.md`, commités avec leurs streams ;
la Tâche 8 du plan prévoit de commiter le fichier GO du stream 05).

## Réponses aux cinq hypothèses — les cinq défauts sont CONFIRMÉS

### 1. Normalisation de F2 — CONFIRMÉ : moyenne des informations journalières sur la fenêtre de calibration

Trois motifs. (i) Le prompt 05 le dit lui-même : « même normalisation sur la moyenne de calibration »
(item 4, F2). (ii) La théorie : le glossaire AGENTS.md définit I comme la KL **par jour** et
τ_γ = ln(γ)/I (Lemme 1 : l'information s'additionne jour par jour) ; les floors de `floors.py`
sont exprimés en I par jour, donc l'injection doit réaliser exactement ce I par jour — la KL de la
dérive moyenne (73–95 % de la moyenne des KL journalières, sonde 6) réaliserait une information
différente de 5 à 27 % et fausserait les comparaisons ADD/floors. (iii) La formule du plan (étape 4 :
q = ½·moyenne des formes D_refᵀΣ̂⁻¹D_ref sur la calib) implémente déjà cette lecture, et
`meta["info"]` la rapporte. Écart `C-inject-F2-norm` consigné.

### 2. Convention (b) — CONFIRMÉ : RMS des Sharpe annualisés par titre √252·Δ_i/σ̂_i, cible 1 (F1/F3), κ (F2)

Le prompt 05 dit « amplitude par titre fixée » et le prompt 19 « SR de marché par titre = 1 » ; la
lecture RMS est cohérente avec les deux et, sous le modèle équicorrélé du plan v4, redonne
κ = dispersion transversale orthogonale aux chargements / dérive de marché — exactement la définition
de κ du prompt 05. σ̂_i² = Σ̂_ii ; pour F2, RMS sur les titres **et** les jours de calib. Le test
épingle la cible à 1e-12 (F1/F3) et à κ (F2). Écart `C-inject-conv-b` consigné.

### 3. NaN dans C_t — CONFIRMÉ : exposition nulle (rang neutre 0), nombre imputé dans `meta["c_nan_imputed"]`, ±inf → ValueError

Les caractéristiques sont des rangs centrés dans [−0,5 ; 0,5] : 0 est la valeur neutre, donc
« manquante = neutre » est l'imputation sans hypothèse (contre l'abandon du jour, qui changerait la
forme du panel, ou l'imputation par moyenne, qui est une hypothèse). Refuser les NaN rendrait F2
inutilisable sur D3 (24 jours de calib touchés sur `d3_239` ; 13 % de NaN dans `d3_500`). Le test
`test_f2_nan_characteristics_imputed` épingle l'équivalence avec des zéros explicites. Écart
`C-inject-F2-nan` consigné.

### 4. Test SHA-256 d'E2 — CONFIRMÉ (mode rapide, hash `7828e1a3…`, ~25 s) + un renforcement

Le run complet (73 s, `e315e537…`) doublerait la durée de `make check` ; le mode rapide parcourt
les quatre bras et `h0_sign_check`, et le run complet reste la vérification du prompt (`make j1`
avant/après le déplacement, Tâches 0 et 8). **Renforcement** : le hash dépend de numpy 2.4.4 et de
la build BLAS (leçon stream 04, `lb_pvalue_warmup` : les versions épinglées ne pincent pas BLAS).
`make check` tourne dans `.venv` (canonical, `requirements.lock`) où le test est fiable, mais il
échouerait dans un autre environnement (`external/articleB-venv`, Trading). Ajouter un guard
`pytest.mark.skipif` sur l'environnement de référence (numpy 2.4.4), sur le modèle du skip de
`test_r01_reader_bit_identical_in_article_b_env` (stream 04).

### 5. garch_panel — CONFIRMÉ : `nu=None` → innovations gaussiennes

Le glossaire D5 (« Gaussian i.i.d. latent ; GARCH(1,1)-t7 ») est couvert par `gaussian_latent` +
`garch_panel(nu=7)` ; le contrat stream 13 (E3) exige « innovations t₇ **et gaussiennes** » —
`nu=None` est requis. Le χ²_ν commun par jour préserve le clustering de volatilité transversal quand
N est grand (sonde 8 : variance ≈ 1, ACF(1) du carré moyen quotidien ≈ 0,21).

## Choix d'architecture — CONFIRMÉS

- **Ledoit–Wolf dans `jepadrift/stats/covariance.py`** : `stats/` est le module partagé bas niveau ;
  les représentations (streams 06, 11) pourront l'importer sans toucher `jepadrift.injection` ;
  `monitors/` reste numpy-only.
- **`inject` renvoie la dérive appliquée (`delta`)** : l'oracle P7 (stream 07) a besoin de Δ connu
  (w* = Σ̂⁻¹Δ) ; `tau_star.json` stocke `direction_sha256` des octets float64 de `delta`.

## Autres points entérinés

- **Exécution en session unique, sans sous-agents** : endossé (interfaces couplées, sensibilité du
  hash E2, précédent stream 04).
- **Chargeur commun de C_t** : le report au premier consommateur (06 ou 12) est conforme à YAGNI ;
  le premier consommateur le placera dans `jepadrift/data_loader/` pour que les streams 12 et 14
  le réutilisent (le pivot local du test reste tel quel).
- **F2 sur D2** : hors périmètre, correctement signalé — décision à prendre dans le stream 12 (E1) :
  calculer les caractéristiques depuis les rendements, ou réserver F2 à D3.
- **« Entorse » Trading vs `.venv`** : pas une entorse en substance — `.venv` est bâti sur
  l'interpréteur Trading 3.12.9 (même binaire, site-packages du projet), la convention du dépôt est
  `.venv`, et le hash de référence d'E2 dépend de numpy 2.4.4 (`.venv`) ; Trading (1.26.4)
  produirait un hash différent. Transparence appréciée, aucune action.
