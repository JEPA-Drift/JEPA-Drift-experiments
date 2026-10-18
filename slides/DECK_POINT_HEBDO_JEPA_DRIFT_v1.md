# DECK — Point hebdo du 12/10/2026 — JEPA-Drift : l'idée du nouvel article (12 diapositives)
Schéma : chaque diapositive commence par « ### SLIDE n — TYPE — Titre ». TYPE ∈ {TITLE, CONTENT, TABLE, DIVIDER, ANNEX}.
Champs : [TITLE] · Badge · blocs de contenu ([BULLET POINTS]) · [EQUATIONS] · [VISUAL] · Pied · Notes.
Conventions : « • » ouvre un paragraphe distinct. « Texte simplifié » est la version de la formule écrite sur la diapositive ; le code LibreOffice Math qui la précède s'insère à la main. « Couleur » donne le fond et le texte d'une ligne de tableau.

### SLIDE 1 — TITLE — JEPA-Drift

[TITLE] JEPA-Drift — Escaping the Sharpe Ceiling of Sequential Drift Detection

[BULLET POINTS]
- Ligne 1 (28 pt, gras) : JEPA-Drift
- Ligne 2 (28 pt, gras) : Escaping the Sharpe Ceiling
- Ligne 3 (26 pt, gras) : of Sequential Drift Detection
- Ligne 4 (16 pt, italique) : through Latent Information Concentration
- Bandeau orange (14 pt, gras) : Point hebdo du lundi 12/10/2026 — Article C : l'idée du nouvel article
- Ligne sous bandeau (12 pt) : R. Minato — suite de « The Whitening Advantage » (Article B, soumis à KDD 2027)

[EQUATIONS] Aucune.

[VISUAL] Aucun : aplats de couleur du modèle.

Notes : Cette semaine, l'idée et les raisons d'y croire. La semaine prochaine, la théorie et les démonstrations.

### SLIDE 2 — CONTENT — Le point de départ : le plancher de Sharpe

[TITLE] Le point de départ : le plancher de Sharpe

Badge : CONSTAT (RED, w = 0.95)

[BULLET POINTS]

Colonne gauche — en-tête : « Détecter une dérive, c'est accumuler des preuves »
• Chaque jour apporte un peu de preuve qu'une dérive a commencé. On la mesure par la divergence de Kullback-Leibler (KL) entre la loi des rendements avant et après la rupture.
• Un détecteur conclut quand la preuve cumulée franchit un seuil. Le délai moyen de détection (ADD) vaut donc, au mieux, seuil ÷ preuve quotidienne.
• Le seuil traduit la tolérance aux fausses alarmes : ln(1/α₀), où α₀ = 1/ARL₀ et ARL₀ est le nombre moyen de jours entre deux fausses alarmes.
• Pour une petite dérive μ de la moyenne journalière, à volatilité σ, la preuve quotidienne vaut μ²/(2σ²) : la moitié du carré du Sharpe journalier μ/σ.

Colonne droite — en-tête : « Ce que cela coûte en jours »
• En annualisant (252 jours ; SR annuel = √252 · μ/σ), la preuve quotidienne vaut SR²/504.
• SR = 1, une fausse alarme par an (ARL₀ = 252) : au moins 2 800 jours, soit 11 ans. SR = 0,5 : 44 ans.
• Avec une fausse alarme par mois (ARL₀ = 20), SR = 1 coûte encore 1 500 jours, soit 6 ans.
• Sur 66 phases haussières et baissières datées (4 ETF, 2000–2025) : 80 % durent moins que leur plancher même avec une fausse alarme par mois ; 97 % avec une fausse alarme par an.
• Sur une série seule, aucun algorithme n'y échappe : il manque de l'information, pas de la méthode.

Encadré — titre : « Le plancher de Sharpe (Article B) »
• Texte simplifié : ADD_min ≥ 504 · ln(1/α₀) / SR²  (jours de bourse)
• Diviser le Sharpe par deux multiplie le délai par quatre.

[EQUATIONS]

F1 — preuve quotidienne d'une petite dérive
$$\mathrm{KL} \approx \frac{\mu^2}{2\sigma^2} = \frac{\mathrm{SR}_{\text{jour}}^2}{2}$$
```text
nitalic{KL} approx {{%mu}^{2}} over {2 {%sigma}^{2}} = {{{nitalic{SR}}_{nitalic{jour}}}^{2}} over {2}
```
Texte simplifié : KL ≈ μ² / (2σ²) = SR_jour² / 2

F2 — délai = seuil ÷ preuve quotidienne
$$\mathrm{ADD} \approx \frac{\ln(1/\alpha_0)}{\mathrm{KL}}$$
```text
nitalic{ADD} approx {ln left( {1} over {{%alpha}_{0}} right)} over {nitalic{KL}}
```
Texte simplifié : ADD ≈ ln(1/α₀) / KL

F3 — plancher de Sharpe
$$\mathrm{ADD}_{\min} \ge \frac{504\,\ln(1/\alpha_0)}{\mathrm{SR}^2}$$
```text
{nitalic{ADD}}_{nitalic{min}} >= {504 cdot ln left( {1} over {{%alpha}_{0}} right)} over {{nitalic{SR}}^{2}}
```
Texte simplifié : ADD_min ≥ 504 · ln(1/α₀) / SR²

[VISUAL] Aucune figure existante. À dessiner si besoin : ADD_min en années (échelle log) en fonction du SR annuel de 0,25 à 3, deux courbes (ARL₀ = 20 et 252), bande grise des durées typiques de phases (quelques mois à quelques années).

Pied : Lorden (1971) · Lai (1998) · Tartakovsky et al. (2014) · Pagan & Sossounov (2003)

Notes : Le délai varie comme l'inverse du carré du Sharpe. Le « 80 % » reste entre 73 et 80 % selon la méthode de datation.

### SLIDE 3 — CONTENT — Additionner des actifs corrélés ne suffit pas

[TITLE] Additionner des actifs corrélés ne suffit pas

Badge : CONSTAT (RED, w = 0.95)

[BULLET POINTS]

Colonne gauche — en-tête : « Le pooling : additionner les signaux de K actifs »
• Idée naturelle : surveiller K actions à la fois et additionner leurs signaux.
• Avec K séries indépendantes, la preuve quotidienne serait multipliée par K.
• Sur 97 actions américaines (2005–2025), les signes des rendements sont corrélés : ρ̂ ≈ 0,26. Le panel vaut K_eff ≈ 1/ρ̂ ≈ 3,8 actions indépendantes, quel que soit K.
• Mesuré : le budget de détection ne baisse que d'un facteur 2, la limite √K_eff, et plafonne dès K ≈ 20.
• Supposer l'indépendance fait grimper les fausses alarmes vers 100 % dès K = 40 ; un bootstrap sur fenêtres réelles tient les 5 %.
• Le pooling ne regarde qu'une direction, la moyenne du panel, c'est-à-dire le marché : le mur s'élargit, il ne tombe pas.

Colonne droite — en-tête : « Mesure réelle (Article B, Fig. 30) » ; la figure remplace le texte.

Encadré — titre : « Pourquoi ça plafonne »
• Texte simplifié : Var(moyenne de K actifs) = σ² · (ρ + (1 − ρ)/K)  ;  K_eff = K / (1 + (K − 1)·ρ) → 1/ρ ≈ 3,8
• ρ : corrélation moyenne entre deux flux surveillés, ici les signes. La part commune ne se diversifie jamais.

[EQUATIONS]

F4 — variance de la moyenne de K actifs équicorrélés
$$\mathrm{Var}(\bar r) = \sigma^2\left(\rho + \frac{1-\rho}{K}\right)$$
```text
nitalic{Var} left( bar r right) = {%sigma}^{2} left( %rho + {1 - %rho} over {K} right)
```
Texte simplifié : Var(moyenne de K actifs) = σ² · (ρ + (1 − ρ)/K)

F5 — taille effective du panel, quand K grandit
$$K_{\mathrm{eff}} = \frac{K}{1+(K-1)\rho} \;\longrightarrow\; \frac{1}{\rho} \approx 3{,}8$$
```text
{K}_{nitalic{eff}} = {K} over {1 + left( K - 1 right) %rho} ~ rightarrow ~ {1} over {%rho} approx "3,8"
```
Texte simplifié : K_eff = K / (1 + (K − 1)·ρ) → 1/ρ ≈ 3,8

[VISUAL] Fichier Fig30_RealCrossSectional_Escape_UPDATED.png. (A) Taux de fausses alarmes selon K : calibration naïve vers 100 %, bootstrap autour de 5 %. (B) Réduction du budget selon K : plateau près de 2 (√K_eff), contre √K pour un panel indépendant.

Pied : Article B, Fig. 30 · 97 actions US survivantes, 2005–2025

Notes : Le panel élargit la cible sans déplacer le mur. L'information supplémentaire se noie dans le mode commun.

### SLIDE 4 — CONTENT — L'idée : chercher la dérive là où le marché ne fait pas de bruit

[TITLE] L'idée : chercher la dérive là où le marché ne fait pas de bruit

Badge : IDÉE (GREEN, w = 0.90)

[BULLET POINTS]

Colonne gauche — en-tête : « Ce qui noie la dérive : le mode de marché »
• On surveille N actifs à la fois : chaque jour, un vecteur de N rendements.
• Sa covariance Σ se découpe en directions orthogonales v₁, …, v_N (composantes principales), de variances λ₁ ≥ … ≥ λ_N.
• La première, le marché, porte 36 à 40 % de la variance de nos panels S&P 500, davantage en crise.
• Une dérive logée dans cette direction se heurte à tout ce bruit : c'est le sort du pooling.

Colonne droite — en-tête : « Où se loge l'information »
• Une dérive Δμ, déplacement du vecteur des moyennes, apporte dans chaque direction une preuve égale à (part de Δμ dans cette direction)² ÷ variance de la direction.
• À taille égale, une dérive dans une direction calme pèse bien plus qu'une dérive alignée sur le marché.
• Projeter ne crée aucune information (inégalité de traitement des données) : on retire le bruit qui la masquait.
• Si la dérive touche beaucoup de titres dans des directions calmes, les preuves s'additionnent : le gain peut croître avec le nombre de titres au lieu de plafonner.

Encadré — titre : « La preuve quotidienne, direction par direction »
• Texte simplifié : KL = ½ · Σ_k (v_kᵀ Δμ)² / λ_k
• Chaque direction pèse en 1/λ_k : à dérive égale, une direction dix fois plus calme pèse dix fois plus.

[EQUATIONS]

F6 — décomposition de la preuve quotidienne
$$\mathrm{KL} = \frac{1}{2}\sum_{k=1}^{N}\frac{\left(v_k^{\top}\Delta\mu\right)^2}{\lambda_k}$$
```text
nitalic{KL} = {1} over {2} sum from{k=1} to{N} {{left( {{v}_{k}}^{nitalic{T}} %DELTA %mu right)}^{2}} over {{%lambda}_{k}}
```
Texte simplifié : KL = ½ · Σ_k (v_kᵀ Δμ)² / λ_k

[VISUAL] À dessiner : nuage de rendements en ellipse allongée, grand axe étiqueté « marché » ; deux flèches de même longueur depuis le centre, l'une sur le grand axe (« noyée »), l'autre sur le petit axe (« visible »).

Pied : Kullback (1959) · Cover & Thomas (2006) · Alouadi & Lehalle (2026)

Notes : On ne fabrique pas de preuve, on arrête de la diluer.

### SLIDE 5 — CONTENT — Deux façons de construire l'espace latent

[TITLE] Deux façons de construire l'espace latent

Badge : MÉTHODE (BLUE, w = 1.00)

[BULLET POINTS]

Colonne gauche — en-tête : « Référence linéaire : PCA-orthogonal »
• On calcule les composantes principales (PCA) du panel sur une fenêtre passée.
• On écarte la première, le marché, et on surveille les directions restantes.
• Linéaire, interprétable, rapide : c'est la référence à battre.
• Limite : directions fixes, choisies pour leur variance et non pour la dérive ; aveugle aux effets non linéaires (queues épaisses, volatilité commune).

Colonne droite — en-tête : « Représentation apprise : JEPA »
• JEPA (Joint-Embedding Predictive Architecture) : on masque une partie des actifs, et un réseau prédit leur représentation à partir des autres, sans reconstruire les données brutes.
• T-JEPA pour les données tabulaires ; CA-T-JEPA (cross-asset) pour la coupe d'actions, chaque actif devenant un jeton décrit par ses caractéristiques.
• Prédire dans l'espace latent favorise les directions prévisibles plutôt que les plus variables (démontré pour des réseaux linéaires profonds).
• Ce qu'il ne verra pas : une dérive propre à un seul titre, imprévisible depuis les autres.

Bandeau — « Une comparaison à armes égales »
• Ligne 1 — Même moniteur (surveillance séquentielle) — les deux espaces alimentent les mêmes détecteurs, calibrés de la même façon.
• Ligne 2 — Même dimension (espace compact) — quelques dimensions seulement : chaque dimension surveillée ajoute son propre bruit.
• Ligne 3 — Même bruit de fond (données réelles) — mêmes panels, mêmes dérives injectées, mêmes dates de rupture.

Encadré crème : ★ À dimension égale, la représentation apprise retient-elle plus d'information de dérive que la projection linéaire ?

[EQUATIONS] Aucune.

[VISUAL] À dessiner : panel de rendements → (a) PCA, direction marché retirée | (b) encodeur JEPA → espace latent compact → même moniteur → alarme.

Pied : Assran et al. (2023) · Thimonier et al. (2025) · Littwin et al. (2024)

Notes : La référence linéaire passe en premier ; sans elle, un gain JEPA ne se lit pas.

### SLIDE 6 — TABLE — Ce qui existe, et ce qui manque

[TITLE] Ce qui existe, et ce qui manque

Badge : ANALYSE (BLUE, w = 1.00)

[BULLET POINTS]

Tableau (cinquième colonne en italique) :

| Méthode          | Représentation    | Objectif            | Détection séquentielle | Limite pour notre question          | Couleur             |
| ---------------- | ----------------- | ------------------- | ---------------------- | ----------------------------------- | ------------------- |
| PCA / Sparse PCA | Linéaire          | Variance            | Non                    | Facteurs statiques, non économiques | BG_BLUE_LT / BLUE   |
| IPCA (2019)      | Linéaire, caract. | Valorisation        | Non                    | Lien linéaire caract. → expositions | BG_BLUE_LT / BLUE   |
| GKX (2021)       | Non linéaire      | Valorisation        | Non                    | Latent opaque, visé pour le pricing | BG_BLUE_LT / BLUE   |
| CD-DFM (2026)    | Non lin., caract. | Covariance future   | Non                    | Visé pour le risque, pas la dérive  | BG_BLUE_LT / BLUE   |
| T-JEPA (2025)    | Non lin., JEPA    | Représentation      | Non                    | Jamais testé en détection           | BG_BLUE_LT / BLUE   |
| Notre approche   | JEPA, compact     | Détection de dérive | Oui, calibrée          | —                                   | BG_GREEN_LT / GREEN |

Bloc — « Lecture : ce qui est nouveau, et ce qui ne l'est pas »
• Déjà connu : les changements de distribution ressortent davantage dans les composantes de faible variance d'une PCA (Kuncheva & Faithfull, 2014 ; Qahtan et al., 2015). Ce n'est pas notre revendication.
• Nouveau : une borne de délai dans l'espace latent, qui prolonge le plancher de Sharpe et chiffre ce qu'un espace latent peut gagner.
• Nouveau : une calibration exacte des moniteurs latents, valable quelle que soit la volatilité.
• Nouveau : une représentation apprise jugée contre ces références, à dimension et à fausses alarmes égales.
• ★ (gras, GREEN) Au-delà de la finance : toute surveillance de capteurs corrélés (fraude, réseaux, industrie) bute sur le même mur.

[EQUATIONS] Aucune.

[VISUAL] Le tableau.

Pied : Kelly et al. (2019) · Gu et al. (2021) · Alouadi & Lehalle (2026) · Thimonier et al. (2025) · Kuncheva & Faithfull (2014) · Qahtan et al. (2015)

Notes : L'intuition « faible variance » existe déjà ; notre apport porte sur la borne, la calibration et la représentation apprise.

### SLIDE 7 — CONTENT — Les grandes étapes

[TITLE] Les grandes étapes

Badge : ÉTAPES (TEAL, w = 0.95)

[BULLET POINTS]

Liste à barres verticales (libellé en gras, sous-titre entre parenthèses, description) :
1. Étape 1 — (Théorie) — Borne de délai dans l'espace latent, concentration de l'information, taxe dimensionnelle.
2. Étape 2 — (Audit des données) — Vérifier que l'information de dérive existe dans les panels financiers réels, et où elle se loge.
3. Étape 3 — (Pile de surveillance) — Moniteurs séquentiels à calibration exacte, quelle que soit la volatilité.
4. Étape 4 — (Référence linéaire) — Benchmark PCA-orthogonal sur bruit de fond réel.
5. Étape 5 — (Représentations JEPA) — Pré-entraînement et contrôle de la qualité de l'espace latent.
6. Étape 6 — (Confrontation) — JEPA contre PCA-orthogonal, sur données réelles et semi-synthétiques.
7. Étape 7 — (Second domaine et rédaction) — Validation sur la fraude bancaire, puis rédaction.

Encadré crème : ★ Sans moniteurs calibrés, aucun gain d'espace latent ne se mesure : la surveillance passe avant JEPA.

[EQUATIONS] Aucune.

[VISUAL] Liste à barres verticales.

Pied : aucun.

Notes : L'ordre est voulu : la théorie et la référence linéaire avant JEPA.

### SLIDE 8 — TABLE — Données et protocole de dérive

[TITLE] Données et protocole de dérive

Badge : PROTOCOLE (BLUE, w = 1.10)

[BULLET POINTS]

Tableau :

| Jeu de données    | Domaine           | Taille         | Dérives             | Rôle                      | Couleur             |
| ----------------- | ----------------- | -------------- | ------------------- | ------------------------- | ------------------- |
| Simulations       | Contrôle          | Illimitée      | Injectées           | Vérifier les bornes       | BG_BLUE_LT / BLUE   |
| S&P 500           | Actions US        | 239–500 titres | Réelles + injectées | Domaine principal         | BG_GREEN_LT / GREEN |
| EUROFIDAI         | Actions Europe    | Panel N × T    | Réelles + injectées | Grands N, sans survivants | BG_GREEN_LT / GREEN |
| BAF (fraude)      | Comptes bancaires | ≈ 1 M demandes | Mensuelles          | Second domaine            | BG_BLUE_LT / BLUE   |
| Électricité / IoT | Énergie, capteurs | —              | Réelles             | Option hors finance       | BG_BLUE_LT / BLUE   |

Bloc — « Protocole : des dérives à date connue sur un bruit de fond réel »
• Bruit de fond 100 % réel ; on injecte des dérives contrôlées (translations de moyenne, rotations de facteurs) à une date de rupture connue : le délai se mesure exactement.
• Fond neutralisé : on inverse au hasard le signe de journées entières de la coupe. Volatilité et corrélations réelles restent, toute dérive réelle disparaît. On obtient autant de trajectoires sans dérive que nécessaire pour compter les fausses alarmes.
• Mesure : délai moyen de détection (ADD) à fréquence de fausses alarmes fixée (ARL₀), comparé au plancher de Sharpe et au pooling.
• Validation réelle : phases haussières et baissières datées a posteriori (Pagan & Sossounov, 2003). BAF est synthétique, généré à partir d'un jeu réel anonymisé de fraude à l'ouverture de compte.

[EQUATIONS] Aucune.

[VISUAL] Le tableau. Option à dessiner : série réelle neutralisée, avec une dérive injectée à la date de rupture τ* marquée par une ligne verticale.

Pied : Jesus et al. (2022) · Pagan & Sossounov (2003) · Article B

Notes : Le fond neutralisé rend fiable la mesure des fausses alarmes sur données réelles.

### SLIDE 9 — TABLE — Conférences cibles, par échéance

[TITLE] Conférences cibles, par échéance

Badge : ANALYSE (BLUE, w = 1.00)

[BULLET POINTS]

Tableau :

| Conférence             | Rang     | Échéance (est.)  | Adéquation | Rôle                           | Couleur             |
| ---------------------- | -------- | ---------------- | ---------- | ------------------------------ | ------------------- |
| FINEC 2027 (Lancaster) | Finance* | 1er déc. 2026    | ★★         | Premiers retours d'économètres | BG_CREAM / ORANGE   |
| ICML 2027              | A*       | 22 janv. 2027    | ★★★        | Cible principale               | BG_GREEN_LT / GREEN |
| SoFiE 2027             | Finance* | ≈ fin janv. 2027 | ★★         | Visibilité en économétrie      | BG_CREAM / ORANGE   |
| UAI 2027               | A        | ≈ 12 févr. 2027  | ★★★        | Repli si janvier glisse        | BG_GREEN_LT / GREEN |
| ICLR 2027 (ateliers)   | Workshop | ≈ févr. 2027     | ★★         | Visibilité ML                  | BG_BLUE_LT / BLUE   |
| NeurIPS 2027           | A*       | ≈ mi-mai 2027    | ★★★        | Repli après décision ICML      | BG_GREEN_LT / GREEN |

Bloc — « Lecture stratégique »
• Écartées : KDD 2027 (cycle 2) et ECML-PKDD 2027, voies possibles de l'Article B ; IJCAI 2027 (11 janv.), exclusive avec ICML ; ICAIF 2027 (≈ août), hors fenêtre.
• Filets : ECAI 2027 (14 avr., A), ICDM 2027 (≈ début juin, A*), CIKM et DSAA 2027 (≈ fin mai).
• * Conférences de finance sans actes : compatibles avec une relecture ICML en cours, règle à confirmer dans l'appel ICML 2027.
• ★ (gras, GREEN) Si ICML refuse, les décisions tombent avant l'échéance NeurIPS : on resoumet avec les relectures.

[EQUATIONS] Aucune.

[VISUAL] Le tableau, lignes colorées par rôle.

Pied : Rangs CORE · ★★★ viser · ★★ option · est. = estimée d'après l'édition 2026 · * sans actes

Notes : Deux soumissions sans actes encadrent la cible principale ; elles apportent des retours sans bloquer ICML. Le calendrier des décisions ICML reste à confirmer.

### SLIDE 10 — CONTENT — Prochaines étapes

[TITLE] Prochaines étapes

Badge : ACTIONS (ORANGE, w = 1.00)

[BULLET POINTS]

Bandeau : « D'ici deux semaines : un premier test qui peut réfuter l'idée »

Points (couleur — titre — description) :
1. TEAL — Écrire la théorie — Borne de délai dans l'espace latent et calibration exacte des moniteurs latents ; chaque borne vérifiée par simulation.
2. BLUE — Auditer le panel S&P 500 — Part de variance du marché, corrélations, et information de dérive des régimes passés, direction par direction.
3. ORANGE_LT — Construire moniteurs et références — Surveillance univariée, pooling et PCA-orthogonal, branchés sur la même pile de détection.
4. RED — Premier test d'échappement — Sur bruit de fond réel neutralisé, le gain doit continuer de croître avec le nombre d'actifs là où le pooling plafonne. Sinon, l'idée est à revoir.

[EQUATIONS] Aucune.

[VISUAL] Aucun.

Pied : Article B (The Whitening Advantage) · Pagan & Sossounov (2003)

Notes : Le quatrième point peut échouer, et c'est voulu : il décide de la suite.

### SLIDE 11 — DIVIDER — Questions et discussion

[TITLE] Questions et discussion

[BULLET POINTS]
- Carré (RED) : ?
- Titre (2 lignes, 24 pt) : Questions & / discussion
- Sous-titre (12 pt) : Contact : R. Minato · Code : dépôt public à venir, anonymisé pendant la relecture

[EQUATIONS] Aucune.

[VISUAL] Aplats du modèle.

### SLIDE 12 — ANNEX — Annexe : d'où vient le plancher de Sharpe

[TITLE] Annexe : d'où vient le plancher de Sharpe

Badge : ANNEXE (TEAL, w = 0.95)

[BULLET POINTS]

Bandeau : « Quatre lignes, pour une dérive gaussienne de la moyenne »

Étapes :
1. « 1. Preuve quotidienne d'un décalage μ de la moyenne, à volatilité σ : » — Texte simplifié : KL = μ² / (2σ²) = SR_jour² / 2, avec SR_jour = μ/σ
2. « 2. Annualisation sur 252 jours de bourse : » — Texte simplifié : SR = √252 · SR_jour ⇒ KL = SR² / 504
3. « 3. Borne de la détection la plus rapide, atteinte par le CUSUM ; (1 + o(1)) s'efface quand ARL₀ grandit : » — Texte simplifié : ADD ≥ ln(ARL₀) / KL · (1 + o(1))
4. « 4. D'où le plancher, avec α₀ = 1/ARL₀ : » — Texte simplifié : ADD_min ≥ 504 · ln(1/α₀) / SR²  □

Bloc rose — « Portée : » (gras, RED)
• La borne vise la loi inconditionnelle d'une seule série. Un moniteur qui connaîtrait la volatilité du jour ferait mieux : l'Article B le mesure avec un oracle à anticipation.
• Le moniteur de signe de l'Article B paie un facteur π/2 sous loi gaussienne, en échange d'une calibration exacte.
• En multivarié, SR² devient le carré du Sharpe du portefeuille aligné sur la dérive : sujet de la semaine prochaine.

[EQUATIONS]

F7
$$\mathrm{KL} = \frac{\mu^2}{2\sigma^2} = \frac{\mathrm{SR}_{\text{jour}}^2}{2}, \qquad \mathrm{SR}_{\text{jour}} = \frac{\mu}{\sigma}$$
```text
nitalic{KL} = {{%mu}^{2}} over {2 {%sigma}^{2}} = {{{nitalic{SR}}_{nitalic{jour}}}^{2}} over {2} , ~ {nitalic{SR}}_{nitalic{jour}} = {%mu} over {%sigma}
```

F8
$$\mathrm{SR} = \sqrt{252}\,\mathrm{SR}_{\text{jour}} \;\Rightarrow\; \mathrm{KL} = \frac{\mathrm{SR}^2}{504}$$
```text
nitalic{SR} = sqrt{252} cdot {nitalic{SR}}_{nitalic{jour}} ~ drarrow ~ nitalic{KL} = {{nitalic{SR}}^{2}} over {504}
```

F9
$$\mathrm{ADD} \ge \frac{\ln \mathrm{ARL}_0}{\mathrm{KL}}\,\bigl(1+o(1)\bigr)$$
```text
nitalic{ADD} >= {ln left( {nitalic{ARL}}_{0} right)} over {nitalic{KL}} left( 1 + o(1) right)
```

F10
$$\mathrm{ADD}_{\min} \ge \frac{504\,\ln(1/\alpha_0)}{\mathrm{SR}^2}, \qquad \alpha_0 = \frac{1}{\mathrm{ARL}_0}$$
```text
{nitalic{ADD}}_{nitalic{min}} >= {504 cdot ln left( {1} over {{%alpha}_{0}} right)} over {{nitalic{SR}}^{2}} , ~ {%alpha}_{0} = {1} over {{nitalic{ARL}}_{0}}
```

[VISUAL] Aucun.

Pied : Lorden (1971) · Moustakides (1986) · Lai (1998) · Tartakovsky et al. (2014)