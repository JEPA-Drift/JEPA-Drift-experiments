# MISSION PRIORITAIRE : ARBITRAGE DES STREAMS DE RECHERCHE ET EXÉCUTION DU BANC D'ESSAI COMPARATIF « PCA BASELINE vs PCA-DRIFT INFORMATIONNEL » (EXPÉRIENCES 1, 2 ET 3)

## 1. ÉTAT D'ATTERRISSAGE DU DÉPÔT ET ARBITRAGE DES CHANTIERS EN COURS

Le projet **JEPA-Drift** étudie la détection séquentielle rapide de changements de distribution (*data drift* de moyenne et de covariance) dans des coupes journalières d'actions à taux de fausses alarmes strictement contrôlé.
Le point de situation scientifique (`DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v4_CGPT.md`, Slides 1 à 20) a établi les propriétés spectrales de l'ACP régularisée (Ledoit–Wolf), le calibrage exact des moniteurs de signes sous symétrie conditionnelle ($4{,}395\,\%$ mesuré pour $4{,}3947\,\%$ théorique sur $H=750$), et la mise en évidence des angles morts des indices de référence sur les rotations de covariance (Slides 2, 8, 12, 13). En revanche, l'avantage incrémental réel d'un espace latent issu d'un réseau auto-supervisé compact (JEPA transversal) par rapport aux représentations linéaires sans réseau n'est **pas encore établi** (Slide 1, Slide 20).

### 1.1 Bilan consolidé des streams d'ingénierie (État au commit `d8e644b` sur `main`)
Les streams de la Phase 1 sont clôturés et intégrés sur `main` ; il est formellement interdit de relancer des calculs redondants sur ces volets :
1. **Stream 12 (E1 — J2 Pooling & Calibration) : TERMINÉ ET FUSIONNÉ (commit `77991ac`).**
   - Les 54 contrôles J2(i)–(iv) à 2 000 réplications sont validés. Les bornes empiriques de pooling ($K_{\mathrm{eff}} \approx 3{,}85$, plateau de dispersion $\approx 1{,}96\times$) sont scellées. Worktree supprimé, branche archivée.
2. **Stream 13 (E3 — Overshoots, Délais CUSUM & Porte D8) : TERMINÉ, ARCHIVÉ ET FUSIONNÉ (commit `4811bda`).**
   - Le résultat E3 est consigné avec le verdict contractuel de la porte D8 : **FAIL préspécifié sur `iid/first_order_d1_l3` à $+5{,}2833\,\%$ pour une tolérance de $5{,}0\,\%$** (1 994,07 vs 1 894). Conformément aux règles d'intégrité anti-p-hacking, aucun rerun n'a été toléré et cet échec est acté dans `docs/DEVIATIONS.md`. Worktree supprimé, branche archivée.
3. **Stream 14 (CA-T-JEPA v2 — Bottleneck compact & Anti-fuite) : TERMINÉ ET FUSIONNÉ (commit `779e3fb`).**
   - L'architecture native compacte ($d \in \{2, 4, 8, 16\}$ sans ACP aval), le lecteur `panel.parquet` sécurisé (rejet du fichier Fortran `ret_wide.npy`), la liaison d'identité des 239 actifs par condensat SHA-256 dans `config.json`, et les 4 gardes Torch sont validés sans `skip`. L'Invariant 1 (format binaire CRLF natif de `results/e2/e2_cells.csv`, SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`) est vérifié à l'octet dans l'arbre de travail et dans le blob Git indexé. Worktree supprimé, branche archivée.
4. **Stream 17 (IPCA — Baseline factorielle P4) : TERMINÉ ET FUSIONNÉ (commit `b95f077`).**
   - Le socle commun C (`data_loader/chars.py`, tenseurs $C_{i,t}$, convention `C-repr-rows`) est intégré. Le résultat nul P4-D sur D3 (0 alarme sur 500 par surapprentissage des seuils sur fenêtres réutilisées) est consigné comme échec de calibration, interdisant toute assertion de FPR calibré hors échantillon pour P4-D. Worktree supprimé, branche archivée.
5. **Stream 18 (CD-DFM — Modèle à facteurs dynamiques) : CLÔTURÉ DOCUMENTAIREMENT (commit `d8e644b`).**
   - En l'absence de licence open-source dans le clone amont et faute de chargeur d'ingestion adapté à l'interface Z-1, CD-DFM est formellement déclassé en diagnostic documentaire secondaire dans `docs/sections/cd_dfm.md`, conformément à la clause d'exclusion de `07_STREAM_22_E5_J4_REWRITE.md`. Worktree supprimé.
6. **Stream 23 (F4 / Effets de second ordre & P4-D) : EN SOMMEIL.**
   - La Phase 1 est archivée dans sa branche locale ; son worktree est maintenu intact sous `~/JEPA-stream-23` (commit `3d0bd20`), sans aucun processus actif.

### 1.2 Réorientation stratégique immédiate
Avant d'engager le pré-entraînement lourd de JEPA (Stream 16) et la porte confirmatoire J4 (Streams 21 et 22) :
* **GEL TEMPORAIRE DE LA FILIÈRE NEURONALE :** Les streams 16 (Pré-entraînement JEPA), 19 (Lois d'échelle en $N$), 21 (Freeze runner) et 22 (Expérience confirmatoire E5 / J4) sont suspendus jusqu'à nouvel ordre.
* **ACTIVATION DU CHANTIER PRIORITAIRE ABSOLU :** Déployer immédiatement le banc d'essai expérimental complet (Expériences 1, 2 et 3) sur l'ACP pour prouver empiriquement la rupture de performance apportée par notre règle de dimensionnement séquentielle face aux critères historiques fondés sur la variance.

---

## 2. FONDEMENTS THÉORIQUES DU BANC D'ESSAI COMPARATIF

### 2.1 Le paradoxe de la variance et de l'information séquentielle
Dans la littérature standard du contrôle statistique multivarié des procédés (MSPC) et de la détection de dérive, la dimension $d$ d'une ACP est sélectionnée selon la **variance historique cumulée sous $H_0$** (ex. retenir $90\,\%$ de la trace de $\Sigma$, ou la règle de Marčenko–Pastur $\lambda_k > \lambda_+$ de la Slide 10).
Or, pour un changement de moyenne $\Delta \in \mathbb{R}^N$ au jour de rupture, l'information de Kullback–Leibler apportée par le $k$-ième axe propre unitaire $v_k$ de variance $\lambda_k$ (Slide 11, Annexe A6) vaut :
$$q_k = \frac{(v_k^\top \Delta)^2}{2\lambda_k}$$
```starmath
q_k = {left(v_k^T %DELTA right)^2} over {2 %lambda_k}
```
La variance historique $\lambda_k$ apparaît au **dénominateur**. Une dérive touchant un facteur résiduel de faible variance historique produit un rapport signal/bruit $q_k$ potentiellement colossal, alors que le premier axe de marché (plus grande variance $\lambda_1$) n'apporte qu'une information marginale négligeable si le choc est sectoriel ou orthogonal au marché. Ordonner les axes par variance décroissante revient donc fréquemment à classer les composantes par information croissante.

### 2.2 La taxe de surveillance et la vitesse fluide de détection
Surveiller un espace latent multivarié de dimension $d$ dont l'orientation de dérive est inconnue impose une pénalité incontournable. D'après l'analyse de la martingale de mélange Gaussien (Slides 15, 37, Annexe A11), l'espérance de la log-preuve atteint le seuil d'alarme $A = \ln \gamma$ lorsque le budget d'information cumulé moyen atteint la racine unique $x_d$ de :
$$x_d = A + \frac{d}{2}\ln\left(1 + \frac{2x_d}{d}\right)$$
```starmath
x_d = A + {d} over {2} ln left(1 + {2 x_d} over {d} right)
```
Le multiplicateur de coût de surveillance :
$$M(d, \gamma) = \frac{x_d}{\ln \gamma} > 1$$
```starmath
M left(d, %gamma right) = {x_d} over {ln %gamma}
```
quantifie l'inflation exacte du délai par rapport à un oracle 1D parfaitement aligné.
Pour un sous-ensemble d'axes $S$ de cardinal $|S| = d$ capturant une information totale $I(S) = \sum_{j \in S} q_j$, la vitesse fluide théorique de détection (Slides 15, 38) est :
$$V(S) = \frac{I(S)}{M(|S|, \gamma)}$$
```starmath
V left(S right) = {{I left(S right)} over {M left(abs{S}, %gamma right)}}
```
Maximiser $V(S)$ équivaut rigoureusement à **minimiser le délai moyen de détection $\mathbb{E}_1[T]$**.
Ajouter une dimension $j$ n'est optimal que si son gain d'information marginale compense la croissance de la taxe $M(|S|+1, \gamma) - M(|S|, \gamma)$ (Slide 16, Annexe A12).

---

## 3. SPÉCIFICATION CHIRURGICALE DES EXPÉRIENCES ET DES TABLEAUX

Les tests sont exécutés sur deux environnements de données :
- **Données synthétiques contrôlées ($N=239$ actions, $T=1\,000$ séances) :** Innovations Student $t_7$, corrélation factorielle commune 0,40 (environnement Slide 5).
  - *Rupture A (Saut de moyenne marché) :* Translation $\Delta$ parallèle au 1er axe propre $v_1$ (Sharpe 4 annuel). Information : $q_k^{\mathrm{mean}} = \frac{(v_k^\top \Delta)^2}{2\lambda_k}$.
  - *Rupture B (Rotation de covariance 30°, Slide 13) :* Rotation orthogonale $R_{12}(30^\circ)$ entre $v_1$ et $v_2$. L'information marginale est portée par la déformation de variance : $q_k^{\mathrm{cov}} = \frac{1}{2}\left[\frac{v_k^\top \Sigma_1 v_k}{\lambda_k} - 1 - \ln\left(\frac{v_k^\top \Sigma_1 v_k}{\lambda_k}\right)\right]$, surveillée via les résidus quadratiques.
  - *Rupture C (Saut de moyenne résiduel) :* Dérive $\Delta$ orthogonale au marché, concentrée sur les axes de bruit 10 à 20 avec rapport signal/bruit calibré à $I_{\mathrm{total}} = 3{,}0$ nats/jour.
- **Données réelles S&P 500 :** Panel historique de 239 actions (calibration 2016–2019, test 2020–2025).
  - *Événement Réel 1 :* Choc Covid-19 (24 fév. – 23 mars 2020). Le vecteur $\Delta_{\mathrm{real}}$ pour l'oracle est estimé ex-post par $\bar{r}_{\mathrm{crise}} - \bar{r}_{\mathrm{calib}}$.
  - *Événement Réel 2 :* Rotation de style (janvier – juin 2022). Vecteur $\Delta_{\mathrm{real}}$ estimé sur la même convention.
  - *Garde-fou bibliothèque ex-ante :* La bibliothèque de stress $\bar{q}_k$ de l'Heuristique (3) est strictement confinée au segment 2005–2015 (crises 2008 et 2011), sans aucune fuite post-2016.

---

### EXPÉRIENCE 1 : LA BASELINE HISTORIQUE DES ARTICLES DE RÉFÉRENCE (`Tableau_PCA_1`)

**Motivation :** Évaluer les performances du pipeline standard de contrôle de procédé (MSPC) où les dimensions sont sélectionnées par ordre naturel de variance historique décroissante $\lambda_k$ sous $H_0$.

**Spécifications d'exécution :**
- Calculer la matrice de covariance rétrécie Ledoit–Wolf $\Sigma_{\mathrm{LW}}$ sur la période de calibration (Slide 8).
- Extraire les valeurs propres $\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_N$ et les vecteurs propres associés $v_k$.
- Calculer pour chaque $k \in \{1, \dots, n\}$ (avec $n = 20$) la proportion cumulée de variance expliquée sous $H_0$ :
$$\mathrm{CPV}_k = \frac{\sum_{j=1}^k \lambda_j}{\operatorname{tr}(\Sigma_{\mathrm{LW}})}$$
```starmath
nitalic{CPV}_k = {sum from {j=1} to {k} %lambda_j} over {nitalic{tr} left(%SIGMA_{nitalic{LW}} right)}
```
- Pour chaque bloc de préfixe spectral $\mathcal{P}_k = \{1, \dots, k\}$, déployer le détecteur CUSUM multivarié à seuil $\gamma$ calibré pour cibler $\mathrm{FPR}(250) = 0{,}05$.
- Mesurer par Monte Carlo sur $2\,000$ répétitions :
  - Le délai moyen plafonné à $H=250$ jours : $\mathrm{RMST}_{250} = \mathbb{E}[\min(T, 250)]$ (Slide 48).
  - Le taux empirique de fausses alarmes sur $H=250$ jours hors dérive : $\mathrm{FPR}(250) = P_0(T \le 250)$.

**Formatage obligatoire de `Tableau_PCA_1` :**

| Indice $k$ | Valeur propre $\lambda_k$ | Variance cumulée $\mathrm{CPV}_k$ (%) |    Drapeau Critères Standards     | Délai moyen mesuré $\mathrm{RMST}_{250}$ (j) | Dimension retenue $d^*$ | Taux de fausse alarme $\mathrm{FPR}(250)$ |
| :--------: | :-----------------------: | :-----------------------------------: | :-------------------------------: | :------------------------------------------: | :---------------------: | :---------------------------------------: |
|   **1**    |        $\lambda_1$        |           $\mathrm{CPV}_1$            |                 —                 |                  $\dots$ j                   |            1            |                $5{,}0\,\%$                |
|   **2**    |        $\lambda_2$        |           $\mathrm{CPV}_2$            |                 —                 |                  $\dots$ j                   |            2            |                $4{,}9\,\%$                |
|  $\dots$   |          $\dots$          |                $\dots$                |                 —                 |                  $\dots$ j                   |         $\dots$         |                  $\dots$                  |
|   **6**    |        $\lambda_6$        |           $\mathrm{CPV}_6$            | Coupure Kaiser ($\lambda_k < 1$)  |                  $\dots$ j                   |            6            |                $5{,}1\,\%$                |
|  $\dots$   |          $\dots$          |                $\dots$                |                 —                 |                  $\dots$ j                   |         $\dots$         |                  $\dots$                  |
|   **11**   |      $\lambda_{11}$       |          $\mathrm{CPV}_{11}$          | Seuil Marčenko-Pastur $\lambda_+$ |                  $\dots$ j                   |           11            |                $4{,}8\,\%$                |
|  $\dots$   |          $\dots$          |                $\dots$                |                 —                 |                  $\dots$ j                   |         $\dots$         |                  $\dots$                  |
|   **14**   |      $\lambda_{14}$       |             $90{,}2\,\%$              |   Seuil conventionnel CPV 90 %    |                  $\dots$ j                   |           14            |                $5{,}0\,\%$                |
|  $\dots$   |          $\dots$          |                $\dots$                |                 —                 |                  $\dots$ j                   |         $\dots$         |                  $\dots$                  |
|   **20**   |      $\lambda_{20}$       |          $\mathrm{CPV}_{20}$          |                 —                 |                  $\dots$ j                   |           20            |                $5{,}2\,\%$                |

---

### EXPÉRIENCE 2 : LE PROFILING INFORMATIONNEL SOUS CONTRAINTE D'ORDRE NATUREL (`Tableau_PCA_2`)

**Motivation :** Mettre en évidence l'effondrement de l'efficacité séquentielle du préfixe $\{1, \dots, k\}$ face à la sélection du sous-ensemble optimal extrait de ce même réservoir $\{1, \dots, k\}$.

**Spécifications d'exécution :**
À chaque ligne $k$ (périmètre restreint aux $k$ premières composantes $\{1, \dots, k\}$) :
1. Calculer l'information marginale réelle $q_k = \frac{(v_k^\top \Delta)^2}{2\lambda_k}$.
2. Évaluer le **Bloc Préfixe Naïf $\{1, \dots, k\}$** :
   $$I_{\mathrm{pref}}(k) = \sum_{j=1}^k q_j, \quad V_{\mathrm{pref}}(k) = \frac{I_{\mathrm{pref}}(k)}{M(k, \gamma)}$$
   Le délai mesuré sur ce préfixe **doit être rigoureusement identique au bit près** à celui de la ligne $k$ du `Tableau_PCA_1`.
3. Évaluer le **Bloc Sous-ensemble Optimal $S_k^* \subseteq \{1, \dots, k\}$** :
   $$S_k^* = \arg\max_{S \subseteq \{1, \dots, k\}} \frac{\sum_{j \in S} q_j}{M(|S|, \gamma)}$$
   Enregistrer le score optimal $V(S_k^*)$, le cardinal optimal $d_k^* = |S_k^*|$, la composition de $S_k^*$, et mesurer le délai empirique $\mathrm{RMST}_{250}$ associé.

**Formatage obligatoire de `Tableau_PCA_2` :**

| Indice PCA $k$ | Variance $\lambda_k$ sous $H_0$ | Info réelle $q_k$ (nats) | Score Préfixe $V(\{1..k\})$ | Délai Préfixe $\mathrm{RMST}_{250}$ (j) | Sous-ensemble optimal $S_k^* \subseteq \{1..k\}$ | Score Optimal $V(S_k^*)$ | Délai Optimal $\mathrm{RMST}_{250}$ (j) | Dimension retenue $d_k^*$ | $\mathrm{FPR}(250)$ |
| :------------: | :-----------------------------: | :----------------------: | :-------------------------: | :-------------------------------------: | :----------------------------------------------: | :----------------------: | :-------------------------------------: | :-----------------------: | :-----------------: |
|     **1**      |             $\dots$             |          $q_1$           |   $V_{\mathrm{pref}}(1)$    |                $\dots$ j                |                     $\{1\}$                      |        $V(S_1^*)$        |                $\dots$ j                |           **1**           |     $5{,}0\,\%$     |
|     **2**      |             $\dots$             |          $q_2$           |   $V_{\mathrm{pref}}(2)$    |                $\dots$ j                |                     $S_2^*$                      |        $V(S_2^*)$        |                $\dots$ j                |          $d_2^*$          |     $4{,}9\,\%$     |
|    $\dots$     |             $\dots$             |         $\dots$          |           $\dots$           |                $\dots$ j                |                     $\dots$                      |         $\dots$          |                $\dots$ j                |          $\dots$          |       $\dots$       |
|     **11**     |             $\dots$             |         $q_{11}$         |   $V_{\mathrm{pref}}(11)$   |                $\dots$ j                |                    $S_{11}^*$                    |      $V(S_{11}^*)$       |                $\dots$ j                |        $d_{11}^*$         |     $5{,}0\,\%$     |
|    $\dots$     |             $\dots$             |         $\dots$          |           $\dots$           |                $\dots$ j                |                     $\dots$                      |         $\dots$          |                $\dots$ j                |          $\dots$          |       $\dots$       |
|     **20**     |             $\dots$             |         $q_{20}$         |   $V_{\mathrm{pref}}(20)$   |                $\dots$ j                |                    $S_{20}^*$                    |      $V(S_{20}^*)$       |                $\dots$ j                |        $d_{20}^*$         |     $5{,}1\,\%$     |

---

### EXPÉRIENCE 3 : SYNTHÈSE DES ABLATIONS ET HEURISTIQUE EX-ANTE (`Tableau_PCA_3`)

**Motivation :** Valider la robustesse de l'heuristique sans oracle de dérive face aux variantes oracles et à la baseline classique.

**Périmètre d'exploration des axes :** Pour toutes les variantes de l'Expérience 3, l'univers des axes candidats est strictement restreint aux $n_{\max} = 20$ premières composantes de l'ACP (identique au réservoir terminal $k=n$ de l'Expérience 2).

**Variantes méthodologiques évaluées (Lignes du tableau) :**
- **(0) Baseline classique CPV 90 % :** Préfixe spectral coupant à $90\,\%$ de variance (Expérience 1).
- **(1) Oracle Tri $q_k$ + Coût affine :** Tri par $q_k$ décroissant, coût affine $C(d) = a + cd$ (Slide 40, Annexe A12 bis), maximisation de $V_{\mathrm{aff}}(d)$.
- **(2) Oracle Tri $q_k$ + Coût exact $M(d, \gamma)$ :** Tri par $q_k$ décroissant, coût exact $M(d, \gamma) = x_d / \ln \gamma$, dimension $d^* = \arg\max \frac{\sum_{j=1}^d q_{(j)}}{M(d, \gamma)}$.
- **(3) Heuristique Forward Greedy ex-ante :** Sélection gloutonne évaluant l'information moyenne $\bar{q}_k$ issue d'une bibliothèque historique de chocs passés (sans connaissance de la rupture actuelle).

**Formatage obligatoire de `Tableau_PCA_3` (Dimension retenue $d^*$ placée entre Délai et FPR) :**

| Rupture testée                         | Pipeline & Règle de sélection d'axes     | Information $I(d^*)$ (nats) | Coût de mélange $M(d^*)$ | Score théorique $V(d^*)$ | Délai moyen mesuré $\mathrm{RMST}_{250}$ (j) | Dimension retenue $d^*$ | Taux de fausse alarme $\mathrm{FPR}(250)$ |
| :------------------------------------- | :--------------------------------------- | :-------------------------: | :----------------------: | :----------------------: | :------------------------------------------: | :---------------------: | :---------------------------------------: |
| **Simulé : Rupture B (Rotation 30°)**  | (0) Baseline classique CPV 90 %          |           $\dots$           |         $\dots$          |         $\dots$          |                  $\dots$ j                   |         $\dots$         |                $5{,}0\,\%$                |
|                                        | (1) Oracle Tri $q_k$ + Coût affine       |           $\dots$           |         $\dots$          |         $\dots$          |                  $\dots$ j                   |         $\dots$         |                $4{,}9\,\%$                |
|                                        | (2) Oracle Tri $q_k$ + Coût exact $M(d)$ |           $\dots$           |         $\dots$          |         $\dots$          |                  $\dots$ j                   |         $\dots$         |                $5{,}0\,\%$                |
|                                        | (3) Heuristique Forward Greedy ex-ante   |           $\dots$           |         $\dots$          |         $\dots$          |                  $\dots$ j                   |         $\dots$         |                $5{,}0\,\%$                |
| **Simulé : Rupture C (Résiduelle)**    | (0) Baseline classique CPV 90 %          |           $\dots$           |         $\dots$          |         $\dots$          |                  $\dots$ j                   |         $\dots$         |                $4{,}8\,\%$                |
|                                        | (1) Oracle Tri $q_k$ + Coût affine       |           $\dots$           |         $\dots$          |         $\dots$          |                  $\dots$ j                   |         $\dots$         |                $5{,}1\,\%$                |
|                                        | (2) Oracle Tri $q_k$ + Coût exact $M(d)$ |           $\dots$           |         $\dots$          |         $\dots$          |                  $\dots$ j                   |         $\dots$         |                $4{,}9\,\%$                |
|                                        | (3) Heuristique Forward Greedy ex-ante   |           $\dots$           |         $\dots$          |         $\dots$          |                  $\dots$ j                   |         $\dots$         |                $5{,}0\,\%$                |
| **Réel : Mars 2020 (Covid-19)**        | (0) Baseline classique CPV 90 %          |              —              |         $\dots$          |            —             |                  $\dots$ j                   |         $\dots$         |                $5{,}2\,\%$                |
|                                        | (2) Oracle Tri $q_k$ + Coût exact $M(d)$ |              —              |         $\dots$          |            —             |                  $\dots$ j                   |         $\dots$         |                $5{,}0\,\%$                |
|                                        | (3) Heuristique Forward Greedy ex-ante   |              —              |         $\dots$          |            —             |                  $\dots$ j                   |         $\dots$         |                $5{,}0\,\%$                |
| **Réel : S1 2022 (Rotation de style)** | (0) Baseline classique CPV 90 %          |              —              |         $\dots$          |            —             |                  $\dots$ j                   |         $\dots$         |                $4{,}9\,\%$                |
|                                        | (2) Oracle Tri $q_k$ + Coût exact $M(d)$ |              —              |         $\dots$          |            —             |                  $\dots$ j                   |         $\dots$         |                $5{,}1\,\%$                |
|                                        | (3) Heuristique Forward Greedy ex-ante   |              —              |         $\dots$          |            —             |                  $\dots$ j                   |         $\dots$         |                $5{,}0\,\%$                |

---

## 4. SPÉCIFICATION CHIRURGICALE DE LA FIGURE 1

La figure comportera deux panneaux verticaux synchronisés sur l'axe des abscisses commun : **Indice spectral $k \in \{1, \dots, 20\}$**.

1. **Panneau supérieur (Dual-Axis) — Découplage Variance vs Efficacité Informationnelle :**
   - **Axe gauche (Bleu continu) :** Courbe de variance cumulée $\mathrm{CPV}_k$, strictement concave de $\approx 35\,\%$ à $95\,\%$. Ligne horizontale en tirets à $90\,\%$ interceptant la courbe à $k=14$.
   - **Axe droit :**
     - *Courbe Rouge pointillée :* Score préfixe $V_{\mathrm{pref}}(k) = \frac{\sum_{j=1}^k q_j}{M(k, \gamma)}$. Pic précoce à $k=2$ puis effondrement monotone vers zéro sous l'effet du bruit.
     - *Courbe Verte pleine :* Score optimal $V(S_k^*)$ sur le meilleur sous-ensemble extrait de $\{1, \dots, k\}$. Saut à $k=2$ et plateau horizontal stable.
2. **Panneau inférieur — Conséquence opérationnelle sur le Délai moyen $\mathrm{RMST}_{250}$ :**
   - Axe des ordonnées : Délai moyen de détection $\mathrm{RMST}_{250}$ (jours, échelle de 0 à 250 jours).
   - *Courbe Rouge :* Délai du bloc préfixe $\{1, \dots, k\}$. Explosion au-delà de $k=2$, dépassant 180 jours pour $k=11$ (Marčenko–Pastur) et atteignant le plafond de censure (250 jours) pour $k=20$.
   - *Courbe Verte :* Délai du sous-ensemble optimal $S_k^*$. Maintien au plancher minimal ($\approx 12$ jours).

---

## 5. ÉQUIVALENCE COMBINATOIRE ET CONTRAT LOGICIEL (`pytest`)

### 5.1 Démonstration de l'équivalence Knapsack = Forward Greedy = Tri $q_k$
Sur une base orthogonale décorrélée, le gain d'information d'un sous-ensemble est strictement additif : $I(S) = \sum_{j \in S} q_j$. Comme le coût $M(|S|, \gamma)$ ne dépend que du cardinal $|S|$, le sous-ensemble de taille $d$ maximisant $V(S)$ est obligatoirement formé des $d$ éléments de plus fort $q_j$.
- La résolution combinatoire $\max_{S \subseteq \{1..k\}} V(S)$,
- Le tri des $k$ éléments par $q_j$ décroissants,
- L'algorithme glouton (*Forward Greedy*),
**aboutissent au même sous-ensemble $S_k^*$ au bit près**.

### 5.2 Contrat d'intégrité logicielle (`pytest`)
La suite de tests unitaires vérifie obligatoirement :
1. **Égalité stricte Expérience 1 / Expérience 2 :** Pour tout $k \in \{1, \dots, n\}$ :
   $$\mathrm{RMST}_{250}(\text{Tableau\_PCA\_1, ligne } k) == \mathrm{RMST}_{250}(\text{Tableau\_PCA\_2, col. Délai Préfixe, ligne } k)$$
2. **Égalité stricte Expérience 2 / Expérience 3 :** Le périmètre d'exploration des axes candidats pour l'Expérience 3 étant strictement borné aux $n_{\max} = 20$ premières composantes de l'ACP (garantissant l'égalité de l'espace de recherche avec $k = n_{\max}$ de `Tableau_PCA_2`) :
   $$S_{n_{\max}}^* == S^*(\text{Tableau\_PCA\_3, Oracle Tri } q_k \text{ + Coût exact})$$
   $$V(S_{n_{\max}}^*) == V^*(\text{Tableau\_PCA\_3, Oracle Tri } q_k \text{ + Coût exact})$$
   $$\mathrm{RMST}_{250}(S_{n_{\max}}^*) == \mathrm{RMST}_{250}(\text{Tableau\_PCA\_3, Oracle Tri } q_k \text{ + Coût exact})$$
Toute divergence numérique lève une assertion bloquante immédiate.

---

## 6. INSTRUCTIONS D'ORCHESTRATION ET MANDAT POUR CHATGPT-6 (TA PERSONA)

### 6.1 Intégration obligatoire du `Protocole Codex.md`
L'instance *ChatGPT-6* doit structurer ses nouveaux prompts selon le protocole d'orchestration autonome formalisé dans `prompts/Protocole Codex.md` :
1. **Rôle exclusif de Codex :** Superviseur architectural et intégrateur Git ; interdiction de modifier le code applicatif directement.
2. **Protocole bi-phase des sous-agents Claude Code :**
   - *Phase A (Lecture seule) :* `claude -p "MODE PLAN..." --model opus --effort max --permission-mode plan > PLAN.md`.
   - *Phase B (Exécution détachée) :* Script autonome `run_stream.sh` avec `--dangerously-skip-permissions > execution.log 2>&1 &`.
3. **Surveillance non-bloquante :** Inspection instantanée des fichiers `.status_*` et des PID sans aucune boucle active `sleep`.
4. **Contrôles de non-régression avant fusion :** Extinction des processus, absence de verrou `index.lock`, `make check` propre et maintien de l'Invariant 1 (J1 binaire CRLF natif).
*ChatGPT-6* peut référer directement à `~/JEPA-Drift-experiments/prompts/Protocole Codex.md` dans ses instructions.

### 6.2 Livrables demandés à ChatGPT-6 (TA PERSONA)
ChatGPT-6 doit rédiger et livrer l'ensemble des prompts opérationnels suivants :
1. **`12_CODEX_AMORCAGE_PCA_EXPERIMENTS_2026_10_30.md` :**
   Prompt d'amorçage destiné à Codex, établissant la feuille de route prioritaire du banc d'essai PCA, ordonnançant les sous-agents Claude Code, et actant la suspension temporaire des streams 16 et 22.
2. **Prompts modulaires de stream (destinés à `prompts/streams/`) :**
   - Spécification du runner expérimental `experiments/pca_drift_benchmark.py` générant les données simulées et réelles, les détecteurs CUSUM calibrés et les métriques $\mathrm{RMST}_{250}$.
   - Spécification du script de génération des trois tableaux (`Tableau_PCA_1`, `Tableau_PCA_2`, `Tableau_PCA_3`) au format CSV et Markdown conforme aux grilles de la section 3.
   - Spécification du script de tracé `experiments/figures/plot_figure_1.py` générant le graphique vectoriel et raster conforme à la section 4.
   - Spécification de la suite de tests de contrat `tests/test_pca_drift_contracts.py` validant les égalités strictes de la section 5.2.
3. **Instruction de synchronisation :**
   Rappel de l'exécution de `tools/check_prompts.py --sync-master` et de `make prompts-check` pour maintenir le contrat de synchronisation du dépôt à 100 %.