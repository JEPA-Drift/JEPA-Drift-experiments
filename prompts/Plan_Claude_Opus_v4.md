# Plan d'orchestration — JEPA-Drift (Article C)

**Projet** : JEPA-Drift — Escaping the Sharpe Ceiling of Sequential Drift Detection through Latent Information Concentration
**Date** : 11 octobre 2026
**Objectif** : première version de l'article (v1) gelée le **29 novembre 2026**
**Cible principale** : ICML 2027 (résumé 16 janvier, article 22 janvier 2027)

---

## 1. Principes directeurs

### 1.1 Autonomie

Le projet est mené de façon autonome par le chercheur principal et Claude Opus (co-auteur IA). Aucune dépendance externe n'est requise pour la rédaction et le déroulement du plan. José Lucas De Melo Costa pourra être sollicité ultérieurement, mais aucune tâche du plan ne dépend de son intervention.

### 1.2 Deux pistes parallèles

| Piste | Responsable | Rôle |
|---|---|---|
| **T** (Théorie, code, rédaction) | Claude Opus | Props, preuves, bibliothèque de surveillance, scripts, sections de l'article |
| **X** (Données, exécution, vérification) | Chercheur principal | Extraction de données, exécution des expériences, vérification des résultats |

Le code de la semaine k+1 est livré en semaine k par la piste T.

### 1.3 Priorités

- **A** : cœur de l'article ; sans lui, pas de v1.
- **B** : complète la démonstration.
- **C** : robustesse et extensions.

Tout est planifié et rien n'est retiré. Un item B ou C inachevé au jalon J5 (15 nov.) continue en décembre pour la version ICML. La v1 le présente comme « en cours », sans résultat provisoire présenté comme définitif.

### 1.4 Charge

Le plan suppose 15 à 20 h/semaine de la part du chercheur principal. Le périmètre complet en demande davantage en S3–S5 (risque R1, §5).

### 1.5 Taxonomie Data / Concept Drift

- **CONCEPT** = tâche de prédiction de signe avec classifieur non anticipatif (capteur de localisation, 1er ordre).
- **DATA** = statistique sans classifieur (capteur d'échelle ou projection, 2nd ordre).

Cette taxonomie est alignée sur l'Article B (« The Whitening Advantage », KDD 2027) et le Tableau 2 (§4.2).

---

## 2. Calendrier accéléré

### 2.1 Phases

| Phase | Semaines | Objet | Sortie |
|---|---|---|---|
| **I — Socle** | S1–S2 (12–25 oct.) | théorie, pile de surveillance, données, pipelines 1 → 2 → 3 sur données réelles | §1 et §2 rédigés avec leurs chiffres ; J1, J2 |
| **II — Représentations** | S3–S4 (26 oct.–8 nov.) | audit, lois d'échelle, IPCA et CD-DFM, JEPA, BAF, second ordre | §3 et §4 rédigés ; J3, J4 |
| **III — Complétude** | S5 (9–15 nov.) | grille finale gelée, régimes réels, absorption, robustesse | CSV et figures ; J5 |
| **IV — Rédaction** | S6–S7 (16–29 nov.) | §5 à §7, annexes, relectures adverses | v1 le 29 nov. |

### 2.2 Détail hebdomadaire

| Semaine | Piste T (Claude Opus livre) | Piste X (chercheur principal exécute) |
|---|---|---|
| **S1 · 12–18 oct.** | Props 1–3, lemme d'encodeur impair, critère d'absorption, avec preuves [A]. Γ_z spectral et opérationnel, échelle d'efficacité des moniteurs [B]. Bibliothèque de surveillance [A] : P1-C/P1-D portés de l'Article B, P2-C (bootstrap de blocs), P3-C/D, P3-CS, randomisation par inversion de signe, injections F1–F4, e-détecteur à mélange. Scripts E2 [A]. §1 et Tableaux 1–3 v0 [A]. | D1 et D2 depuis le dépôt de l'Article B ; D3 (cours, secteurs GICS) [A]. Extraction EUROFIDAI lancée [B]. BAF téléchargé [B]. Exécution d'E2 et relecture des preuves [A]. |
| **S2 · 19–25 oct.** | Notebook d'audit [A] : spectre, η, corrélation des signes, test de symétrie centrale, spectre de Sharpe de dérive débiaisé, plafonds des canaux N1–N3. Scripts E1 et E3 [A]. CA-T-JEPA avec variantes MAE et prétexte temporel [A/B]. Enveloppe T-JEPA pour BAF [B]. §2 v0 avec le tableau des gains prévus [A]. | Exécution d'E1, E3 et de l'audit sur D2–D3 [A]. |
| **S3 · 26 oct.–1er nov.** | IPCA sur caractéristiques tirées des rendements [A]. CD-DFM : code public, entrées adaptées [B]. Scripts E4 [A]. Diagnostics RankMe [A]. §3 complet, rapprochement avec CD-DFM compris [A]. §4 [A]. | Pré-entraînement de CA-T-JEPA sur D3 : 3 graines, D ∈ {2, 4, 8, 16} [A]. T-JEPA sur BAF, mois 0–2 [B]. Nettoyage de D4 [B]. E4 sur D2–D3 [A]. |
| **S4 · 2–8 nov.** | Analyse E5 : JEPA contre P3, P3-CS et P4, attribution, balayage de D [A]. MAE, spectres de transmission, prétexte temporel [B]. Dictionnaire contre sous-espace [C]. Scripts E6 et E9 [B]. | Exécution d'E5, E6 et E9 ; E4 sur D4 [A/B]. |
| **S5 · 9–15 nov.** | Hash de configuration, figures générées depuis les CSV, Annexe B, encadrés de configuration [A]. Scripts E7 et E10 [C]. | Grille finale E1–E6, E8 sur D1–D4, E9 [A/B] ; E7 et E10 [C]. |
| **S6 · 16–22 nov.** | §5 avec un encadré de configuration par sous-section, §6, §7, résumé, annexes A à E [A]. | Relecture, voix d'auteur, reprise des items C en cours. |
| **S7 · 23–29 nov.** | Relectures adverses sur trois axes (théorie, empirique, présentation). Contrôle chiffre par chiffre contre les CSV. Audit bibliographique. Audit DPI : aucune phrase ne doit suggérer une hausse de KL [A]. | Corrections, gel de la v1 le dimanche 29 nov., dépôt FINEC le 30 nov. |

### 2.3 Métriques

- **G_ADD(A→B)** = ADD_A / ADD_B, à ARL₀ égal, sur la même dérive injectée et avec la même famille de détecteur.
- **G_SR(A→B)** = SR_min,A / SR_min,B. SR_min est le plus petit Sharpe de dérive détecté dans un horizon H avec une probabilité ≥ ½, à ARL₀ fixé. En régime KL, G_SR ≈ √G_ADD.
- **G_floor(A→B)** = rapport des planchers oracles, c'est-à-dire des KL : c'est la borne théorique.

Ces trois métriques sont définies explicitement pour éviter toute ambiguïté dans la comparaison des pipelines (notamment pour le pooling, où la métrique de la Fig. 30 de l'Article B n'est pas documentée).

### 2.4 Jalons et seuils

| Jalon | Date | Critère | Si échec |
|---|---|---|---|
| **J1** | dim. 18 oct. | E2 : ADD simulés à ±10 % des Props 2–3, sur fond gaussien et sur fond GARCH symétrisé | La théorie est corrigée avant tout contact avec les données réelles. |
| **J2** | dim. 25 oct. | E1 et E3 : FPR des flux de signe à ±1 point du **niveau atteignable du treillis** (le CUSUM sur une pièce équilibrée n'atteint que des niveaux discrets : 4,29 % et 5,03 % autour de 5 %). Pente de log G_ADD en log N proche de 0 pour P2 sur F3, et positive pour P3 sur F2 (IC à 95 % excluant 0). Gains 1 → 2 → 3 mesurés. | Si l'audit ne trouve aucune information de dérive exploitable, la contingence C1 s'applique. |
| **J3** | dim. 1er nov. | RankMe de la tête de lecture ≥ 0,5·D ; panel D4 prêt | Rang faible : régularisation de variance renforcée et modèle réduit. D4 en retard : E4-EU passe en S5. |
| **J4** | dim. 8 nov. | G_ADD(meilleur de P3-CS et P4 → P5) ≥ 1,25 sur au moins deux familles parmi F1, F2, F4, IC excluant 1 ; hash de configuration gelé | Titre B ; JEPA présenté comme résultat conditionnel. |
| **D4** | sam. 14 nov. | Notification KDD de l'Article B | Matrice des venues mise à jour (§3). |
| **J5** | dim. 15 nov. | CSV complets pour tous les items A et B | Les items manquants sont signalés « en cours » et poursuivis en décembre. |
| **J6** | dim. 29 nov. | v1 gelée | — |

**Seuils de validation de la thèse.**

- Échappement face au pooling : pente positive au J2, et G_ADD(P2 → meilleur pipeline latent) ≥ 2 au plus grand N, IC excluant 1.
- Face au plancher univarié : au moins 25 % des phases datées dans le budget oracle à ARL₀ = 252, contre 2 sur 66 dans l'Article B.

### 2.5 Contenu de la v1 du 29 novembre

- **Manuscrit** complet au gabarit ICML (8 pages et annexes), avec les Tableaux 1–3.
- **Théorie** T1–T11, détaillées au §4.4. La Prop. 3 est énoncée comme résultat d'atteignabilité.
- **Expériences** E1–E6, E8 et E9 [A/B] ; E7, E10 et E11 [C].
- **Code** : bibliothèque de surveillance, CA-T-JEPA, scripts E1–E11, tests de contrat, CSV et figures régénérables.

### 2.6 Raccourcissement à l'approche d'une échéance

On retire dans cet ordre : E11 → E10 → E7 → dictionnaire (E5-C) → MAE, transmission et prétexte temporel (E5-B) → E6 → E4 sur D4 → E9.

Restent intouchables : E1, E2, E3, E4 sur D2–D3, le cœur d'E5 et E8 sur le S&P 500.

---

## 3. Stratégie de publication par ordre d'urgence

| # | Conférence | Rang | Échéance | Scope | Adéq. | Décision |
|---|---|---|---|---|---|---|
| 1 | FINEC 2027, Lancaster | finance, sans actes | 1er déc. 2026 ; frais de 30 £ ; présentiel | économétrie financière, dont détection en temps réel d'événements extrêmes, modèles à facteurs, IA | ★★ | Soumettre la v1 le 30 nov. |
| 2 | IJCAI 2027 | A* | 4 janv. (résumé), 11 janv. 2027 | IA générale | ★ | Écartée : exclusive avec ICML |
| 3 | AFFI 2027 | finance, sans actes | ≈ 15 janv. 2027 (est. ; 15 janv. en 2026, notification mi-mars) | toute la finance ; atelier doctoral | ★★ | Option |
| 4 | ECML-PKDD 2027, Journal Track | A (revue) | ≈ mi-janv. (est., deck du 28/09) | ML, fouille | — | Écartée : repli de l'Article B |
| 5 | **ICML 2027** | A* | 16 janv. (résumé), 22 janv. 2027, date projetée depuis le cycle précédent | ML : théorie, représentations | ★★★ | **Cible principale** |
| 6 | SoFiE 2027 | finance, sans actes | ≈ fin janv. 2027 (est. ; 23 janv. en 2026) | économétrie financière | ★★ | Soumettre la version ICML |
| 7 | IJCNN 2027 | B | 31 janv. 2027 | réseaux de neurones | ★ | Filet (archivé, exclusif) |
| 8 | COLT 2027 | A* | 5 févr. 2027 | théorie de l'apprentissage | — | Écartée : pas de place pour l'empirique |
| 9 | EUSIPCO 2027 | B (à vérif.) | 6 févr. 2027 ; Darmstadt, fin août | détection séquentielle | ★ | À éviter : scinderait l'apport |
| 10 | UAI 2027 | A | 12 févr. 2027 (projection) | incertitude, tests séquentiels | ★★★ | **Repli si janvier glisse** |
| 11 | KDD 2027, cycle 2 | A* | févr. 2027, dates non publiées | fouille de données | ★ / — | Conditionné à D4 (voir ci-dessous) |
| 12 | Ateliers ICLR 2027 | workshop | ≈ début févr. (est. ; conférence du 26 au 30 avril 2027) | selon les ateliers | ★★ | Visibilité ML |
| 13 | ECML-PKDD 2027, Research Track | A | ≈ mi-mars (est., deck du 28/09) | ML, fouille | ★ | Seulement si l'Article B n'est pas à ECML |
| 14 | ECAI 2027 | A | 14 avr. 2027, Athènes | IA générale | ★ | Filet |
| 15 | NeurIPS 2027 | A* | 14 mai (résumé), 21 mai 2027 (projection) ; l'article complet était dû le 6 mai en 2026 | ML | ★★★ | **Repli après décision ICML** |
| 16 | Ateliers KDD 2027 | workshop | ≈ mai (est.) | séries temporelles, finance | ★ | Visibilité |
| 17 | CIKM 2027 | A | ≈ fin mai (est., deck du 28/09) | données | ★ | Filet |
| 18 | DSAA 2027 | B | ≈ fin mai (est., deck du 28/09) | science des données appliquée | ★ | Filet |
| 19 | Ateliers ICML 2027 | workshop | ≈ fin mai–juin (est.) | ML | ★★ | Si ICML refuse sans viser NeurIPS |
| 20 | ICDM 2027 | A* | ≈ début juin (est., deck du 28/09) | fouille, flux | ★★ | Repli tardif ; 10 pages tout compris |

Hors fenêtre : ICAIF 2027 (échéance du 18 juillet en 2025 ; 9 août en 2026 après report), ateliers NeurIPS 2027 (≈ fin août), ICLR 2028 (≈ fin septembre).

**Cible principale : ICML 2027.** C'est la première échéance A* qui laisse, après la v1, sept semaines pour terminer les items B et C et mener une relecture adverse. ICML correspond aussi mieux qu'IJCAI à un article de théorie et de représentation.

**Replis.**

- Calendrier : UAI 2027, trois semaines plus tard. Son public lit directement la partie e-processus et calibration.
- Après décision : NeurIPS 2027, avec les relectures ICML. Les décisions ICML tombent d'ordinaire début mai, à confirmer.

**KDD.** Il dépend de D4. Si l'Article B est accepté au cycle 1, le cycle 2 devient un repli possible pour l'Article C. Sinon, il reste exclu, puisque B l'utiliserait.

**En parallèle.** FINEC et SoFiE n'ont pas d'actes. Leur compatibilité avec la règle de double soumission d'ICML 2027 et avec l'anonymat se vérifie à la parution de l'appel.

---

## 4. Structure cible de l'article

### 4.1 Ordre et budget de pages (ICML, 8 pages)

| Section | Contenu | Pages |
|---|---|---|
| Abstract | plafond de Sharpe, objectif de concentration, garanties de calibration, résultats chiffrés | — |
| **§1 The Sharpe ceiling and the objective** | formule et ordres de grandeur ; objectif de concentration sous la DPI ; contributions ; Tableaux 1–3 | 1,3 |
| **§2 The problem on real financial data** | pipelines 1 → 2 → 3, gains prévus et mesurés | 1,2 |
| **§3 Concentrating exploitable divergence** | dérivations, rapprochement avec CD-DFM | 1,8 |
| **§4 Learned representations and latent monitors** | CA-T-JEPA, T-JEPA, têtes impaire et paire, calibration | 0,8 |
| **§5 Experiments** | une sous-section par expérience, chacune ouverte par sa configuration | 2,3 |
| **§6 Related work** | — | 0,35 |
| **§7 Limitations and conclusion** | — | 0,25 |
| Annexes | A preuves · B génération des données synthétiques et des dérives · C tableaux longs · D résultats complémentaires · E reproductibilité | — |

### 4.2 Ouverture (§1, en anglais)

**Problem.** A sequential monitor of one return series cannot detect a directional regime faster than the series' information allows. A drift with annualized Sharpe ratio SR adds SR²/504 nats of Kullback–Leibler divergence per trading day, so the first-order bound of quickest detection reads

$$\mathrm{ADD}_{\min} \;\ge\; \frac{504\,\ln(1/\alpha_0)}{\mathrm{SR}^2}\ \text{trading days},\qquad \alpha_0 = 1/\mathrm{ARL}_0 .$$

At one false alarm per year, SR = 1 requires at least 2,787 trading days, about eleven years. On four ETFs over 2000–2025, 64 of 66 dated bull and bear phases end before their own floor. Pooling correlated series does not move this wall: with an average sign correlation of 0.26, a panel of any size behaves like 3.8 independent series.

**Objective.** We seek a representation of the cross-section in which the drift becomes cheap to detect. Write $x_t \in \mathbb{R}^N$ for the day-$t$ returns of $N$ assets, with principal directions $v_k$ and variances $\lambda_k$. A mean shift $\Delta\mu$ adds $\tfrac12\sum_k (v_k^\top\Delta\mu)^2/\lambda_k$ to the daily divergence: a drift of given size weighs more where the residual variance is low. The objective is a map $z_t = \phi(x_t) \in \mathbb{R}^D$, $D \ll N$, that concentrates this divergence, so that a detector watching $D$ coordinates harvests most of it. The data-processing inequality caps the divergence of $z_t$ at that of $x_t$, and no representation creates information. The gain over a univariate monitor comes from two sources only. The cross-section carries more divergence than any single series, and a good representation gathers it into a few directions that the market mode does not dilute.

Le §3 donne la forme exacte : maximiser $r_\phi(D)/M(D)$, avec $r_\phi(D) = \mathcal{I}_{\phi_D}/\mathcal{I}_x \le 1$ par la DPI.

### 4.3 §2 — Le problème sur données financières réelles

**Configuration** (encadré en tête de section) :

- jeux : D1, D2, D3, et D6 pour les dérives injectées ;
- pipelines : P1-C, P1-D, P2-C, P3-C, P3-D, P7 ;
- dérives : réelles (trois datations) et injectées (F3, F1, F2) ;
- calibration : ARL₀ ∈ {20, 252} ;
- mesures : G_ADD, G_SR, G_floor, part des phases dans le budget, K_eff.

**Sous-sections.**

- §2.1 Un actif : le plafond en pratique.
- §2.2 Plusieurs actifs : K_eff = 1/ρ̂, saturation, bootstrap obligatoire.
- §2.3 Projection orthogonale au mode dominant : le canal marché est surveillé à part, puis recombiné par mélange.
- §2.4 Gains prévus contre gains mesurés.

**Gains prévus, à remplacer par les mesures de l'audit.** Hypothèses de planification :

- covariance équicorrélée à un facteur, ρ = 0,40 pour les rendements et ρ_signe = 0,26 pour les flux de signe ;
- résidu isotrope ;
- κ = rapport entre la dispersion transversale de la dérive orthogonale aux chargements et la dérive de marché ;
- ARL₀ = 252 ;
- l'efficacité 2/π des capteurs de signe est commune à tous les pipelines et s'annule dans les rapports.

| Étape | Gain au plancher (oracle) | Gain après taxe dimensionnelle | Repère existant |
|---|---|---|---|
| 1 → 2 (dérive de marché, F3) | N/(1+(N−1)ρ) → 1/ρ : 2,5 en KL gaussienne ; 3,7 (N = 97) à 3,8 (N = 239) en flux de signes | identique (une dimension) | ≈ 2 dans la métrique de la Fig. 30 (design fixe, c = 0,25), plateau dès N ≈ 20 |
| 2 → 3, dérive factorielle (F1) | SR²_F⊥ / SR²_marché, borné en N | × M(1)/M(K), K ≈ 10 | à mesurer (E1, E4) |
| 2 → 3, dérive de largeur (F2) | κ²(1+(N−1)ρ)/(1−ρ) : 4,1 / 16 / 66 pour N = 97 et κ = 0,25 / 0,5 / 1 ; 10 / 40 / 160 pour N = 239 | × M(1)/M(N−1) : 1,1 / 4,2 / 17 pour N = 97 ; 1,7 / 6,9 / 28 pour N = 239 | à mesurer |
| 1 → 3 cumulé (κ = 0,5) | 43 (N = 97), 102 (N = 239) | — | pour SR = 1 par actif : 2 787 jours → 65 jours en oracle, 317 jours à direction inconnue (N = 97) |

Ces chiffres sont des plafonds sous résidu isotrope. Les facteurs sectoriels les réduisent pour F1, et seule la dispersion orthogonale aux chargements alimente F2. Le §2 publiera les gains mesurés avec les formules évaluées sur ρ̂, le spectre résiduel et κ̂ estimés, jamais ces valeurs de planification.

**Note sur la variance du marché.** Le facteur de marché explique R² = 0,36 de la variance sur les 239 titres S&P 500 de Lehalle & Alouadi (CD-DFM, test 2022–2024). La corrélation de signe ρ̂ ≈ 0,26 de l'Article B correspond, par la relation gaussienne ρ_signe = (2/π)·arcsin ρ, à une corrélation de rendements ρ ≈ 0,40 sur les 97 survivants de l'Article B. Ces deux valeurs sont citées séparément, aucune n'est présentée comme mesurée sur les panels du projet avant l'audit (E4).

### 4.4 §3 — Dérivations (T1–T11)

- **3.1 Cadre.** Taux d'information au sens de Lai (1998), DPI.
- **3.2 Prop. 1 (T1), hiérarchie informationnelle.** Linéaire statique ≤ gaussien conditionnel ≤ Fisher = $\mathcal{I}_x$. Canaux récupérables : N1 volatilité commune, N2 chargements variables, N3 queues.
- **3.3 Prop. 2 (T2), plancher latent.** $\mathrm{SR}_z$ est le Sharpe du portefeuille aligné sur la dérive. Décomposition $\mathrm{SR}_F^2$ + largeur ; on retrouve $K_{\mathrm{eff}} = 1/\rho$ dans le cas à un facteur.
- **3.4 Objectif de concentration (T11).** $r_\phi(D)/M(D)$. L'ordre par variance (PCA) ne coïncide pas avec l'ordre par information de dérive.
- **3.5 Prop. 3 (T3), alternative composite.** Taxe $M(D)$. Dictionnaire contre sous-espace (T9). Lois d'échelle en $N^0$, $N^{1/2}$ et $N^1$ (T8).
- **3.6 Calibration dans le latent (T4–T7).**
  - Lemme d'encodeur impair et orthogonalité latente (têtes impaire et paire).
  - Homogénéité de degré 0.
  - Γ_z spectral contre opérationnel.
  - Échelle d'efficacité des moniteurs.
  - Critère d'absorption (T5).
  - **Combinaison des canaux** : par **mélange** (moyenne de martingales de test), jamais par produit, car un produit n'est une martingale de test que si les incréments des deux canaux sont conditionnellement non corrélés, ce que rien ne garantit hors loi elliptique.
- **3.7 Rapprochement avec les modèles à facteurs pilotés par les caractéristiques (T10).**
  - Les facteurs cash-neutral de CD-DFM sont linéaires en rendements, pondérés par des appartenances prédéterminées. Ils sont donc impairs, et le lemme s'applique : ils forment la version pilotée par les caractéristiques du pipeline PCA-orthogonal (P4).
  - Leur covariance prévue $\hat\Sigma(t)$ fournit le blanchiment conditionnel de la Prop. 1 (canal N2).
  - Leur perte de Stein classe les directions par risque expliqué, et non par information de dérive par dimension. Ce sont deux principes de sélection : variance (PCA, CD-DFM) contre prédiction (JEPA, biais implicite de Littwin et al.). E5 les compare sur $r(D)$.
  - Hypothèse à tester : une dérive pilotée par les caractéristiques sans contenu de covariance (F2) échappe aux latents ciblés sur le risque.

### 4.5 §4 à §7

**§4 Méthode.**

- Surveillance latente : un flux de signe exact par direction, e-détecteur à mélange, mises prévisibles, randomisation par inversion de signe, martingales conformes pour BAF.
- CA-T-JEPA :
  - encodeur par jour, actifs en jetons avec tokenisation des caractéristiques à la CD-DFM ;
  - masquage d'actifs, cible EMA, régularisation de variance ;
  - tête impaire par antisymétrisation, tête paire ;
  - aucune normalisation temporelle d'instance ; encodeur gelé pendant la surveillance.
- T-JEPA sur BAF.
- Protocole de choix de D*.

**§5 Expériences.** Ordre : E2, E3, E4, E5, E6, E8, E9, E7 ; E10 et E11 en annexe. Chaque sous-section s'ouvre sur son encadré de configuration (§5.4).

**§6 Travaux liés.**

- Détection la plus rapide : Lorden, Lai, Moustakides, Tartakovsky et al., e-détecteurs.
- Détection de changement par PCA : Kuncheva & Faithfull, Qahtan et al.
- Facteurs latents : IPCA, GKX, CD-DFM.
- JEPA : I-JEPA, T-JEPA, TS-JEPA, Littwin et al.
- Article B.

**§7 Limites.** BAF synthétique, biais du survivant de D2–D3, statut de la Prop. 3, information de localisation intrinsèquement rare en finance.

---

## 5. Tableaux récapitulatifs

### 5.1 Tableau 1 — Jeux de données et représentation latente

| ID | Nom / référence | Réel ou synthétique | Brève description | Représentation latente | Sélection / compression |
|---|---|---|---|---|---|
| D1 | ETF-4 : SPY, PFF, VNQ, BWX (FirstRate Data ; Article B) | Réel | quotidien, 2000–2025 ; référence univariée et recensement des 66 phases | Aucune | — |
| D2 | US-97 (Article B) | Réel ; panel de survivants | 97 actions US, cours ajustés publics, 2005–2025 ; référence du pooling | Aucune · PCA · JEPA | PCA : PC1 suivie à part (canal marché) ; résiduel factoriel PC2…PC(K+1), K au seuil de Marčenko–Pastur ; résiduel complet (N−1 directions) pour F2 ; variante « queue » limitée aux composantes des derniers 10 % de variance (Kuncheva & Faithfull). JEPA : tête impaire, D ∈ {2, 4, 8, 16}, D* fixé sur la fenêtre de calibration par validation sur dérives injectées |
| D3 | SP500-N (univers de CD-DFM, étendu) | Réel | 239 à 500 constituants, quotidien. Caractéristiques datées : bêta, volatilité, momentum 12-1, retournement 1 mois, secteur GICS ; fondamentaux si disponibles [C] | Aucune · PCA · IPCA · CD-DFM · JEPA | PCA : comme D2. IPCA : K par validation. CD-DFM : K = 11 (marché et dix facteurs cash-neutral, comme Alouadi & Lehalle). JEPA : comme D2 |
| D4 | EU-EUROFIDAI | Réel ; constituants point-in-time | actions européennes, N jusqu'à environ 1 000 ; échelle en N et recensement européen | Aucune · PCA · IPCA · JEPA | comme D3, avec des caractéristiques tirées des rendements |
| D5 | MC | Synthétique | flux latents gaussiens i.i.d. en dimension D (Props 2–3) ; GARCH(1,1) à innovations t₇, α = 0,08, β ajusté au Γ cible (Article B). Génération : Annexe B | Aucune (le latent est simulé) | D ∈ {1, 5, 10, 20, 64, 128, 500} |
| D6 | SYM-D2, SYM-D3, SYM-D4 | Semi-synthétique | coupe réelle dont chaque journée entière reçoit un signe tiré au hasard : volatilité et corrélations réelles conservées, dérives réelles effacées ; dérives F1–F4 injectées à τ*. Génération : Annexe B | celles de D2–D4 | celles de D2–D4 |
| D7 | BAF (Jesus et al., NeurIPS 2022), variante Base | Synthétique, issu de données réelles | 1 M de demandes d'ouverture de compte, **30 attributs**, 8 mois (colonne « month ») ; six jeux de 1 M ; génération par GAN après injection de bruit et catégorisation des données personnelles à visée de confidentialité différentielle ; fort déséquilibre de classes et dynamique temporelle | Aucune · PCA · JEPA (T-JEPA) | PCA : attributs standardisés et encodés en one-hot, composantes jusqu'à 90 % de variance. T-JEPA : plongement blanchi, D* fixé sur les mois 0–2 |
| D8 | Électricité (UCI, 370 clients), IoT (SWaT, WADI) — option [C] | Réel | coupe de capteurs corrélés | Aucune · PCA · JEPA | comme D2 |

**Découpages temporels** : pré-entraînement 2005–2015, calibration 2016–2019, test 2020–2025 pour D2–D4 ; mois 0–2, 3 et 4–7 pour BAF. Aucun choix n'utilise la fenêtre de test avant J4.

### 5.2 Tableau 2 — Pipelines

| ID | Pipeline | Type | Drift | Ground truth du drift | Données utilisées | Classifieur | Détecteur |
|---|---|---|---|---|---|---|---|
| P1-C | CONCEPT univarié (Article B) | Concept (localisation) | réel ; synthétique (F3) | réel : Pagan–Sossounov, Lunde–Timmermann, trois variantes ; synthétique : translation à τ* | rendements passés d'un actif ; cible = signe du rendement du jour | Hoeffding Tree non adaptatif | CUSUM bilatéral sur l'erreur binaire (δ = 0,1, seuil au niveau exact du treillis) ; e-processus MIX |
| P1-D | DATA univarié (Article B) | Data (échelle) | synthétique (F4 univariée) ; réel | dérive de variance injectée ; datation | résidu au carré standardisé | — | CUSUM, PHT, seuil λ_iid × Γ̂ |
| P2-C | CONCEPT poolé (Article B) | Concept | réel ; synthétique (F1–F3) | idem P1-C | K flux d'erreur binaire ; cibles = signes | Hoeffding Tree par actif | CUSUM sur la somme des erreurs, seuil par bootstrap de fenêtres réelles ; ρ̂ et K_eff rapportés |
| P3-C | CONCEPT latent PCA-orthogonal | Concept | réel ; synthétique (F1–F3) | idem | projections v_kᵀx_t (PC1 en canal séparé ; résiduel factoriel ou complet) ; cibles = signes des projections | Hoeffding Tree ou prédicteur médian figé, par direction | un flux de signe exact par direction (lemme) ; e-détecteur à mélange sur les directions ; canal marché recombiné par **mélange** |
| P3-D | DATA latent PCA | Data | synthétique (F4) ; réel | rotation factorielle, déformation de Σ_t | projections au carré | — | CUSUM d'énergie, seuil λ_iid × Γ_z^op mesuré sur D6 |
| P3-KF | PCA « queue » (antériorité) | Data | synthétique (F1–F4) | injections | composantes des derniers 10 % de variance | — | SPLL (Kuncheva, 2013) |
| P3-CS | Coupe normalisée de degré 0 ; rangs centrés | Concept (signe) ; Data (pivot) | synthétique (F1–F3) ; réel | idem | x_t/‖Px_t‖ projeté ; rangs transversaux centrés | prédicteur médian figé (C) | CUSUM à design fixe sur le pivot ; e-détecteur de signe à mise ∝ 1/σ̂_{t∣t−1} |
| P4-C, P4-D | Facteurs pilotés par les caractéristiques (IPCA, CD-DFM) | Concept ; Data | synthétique (F1, F2, F4) ; réel | idem | rendements de facteurs cash-neutral ; caractéristiques datées | Hoeffding Tree par facteur (C) | comme P3-C et P3-D |
| P5-C | CONCEPT latent JEPA (tête impaire de CA-T-JEPA) | Concept | synthétique (F1–F3) ; réel | idem | coupe du jour et caractéristiques → z_t impair, D* dimensions ; cibles = signes | prédicteur médian figé ou Hoeffding Tree | e-détecteur à mélange sur les directions ; CUSUM de signe |
| P5-D | DATA latent JEPA (tête paire) | Data | synthétique (F4) | idem | énergie de la tête paire | — | CUSUM d'énergie, λ_iid × Γ_z^op |
| P5-MAE, P5-TEMP | Ablations : objectif MAE ; prétexte temporel | Concept | synthétique (F1, F2) | idem | comme P5-C | comme P5-C | comme P5-C |
| P5-ADAPT | JEPA mis à jour en ligne (absorption) | Concept | synthétique (F1, F2) | idem, τ_a balayé | comme P5-C | comme P5-C | comme P5-C |
| P6-D | BAF, dérive des données | Data | natif du jeu (mensuel) | frontières de mois ; confirmation hors ligne par test MMD à permutation entre mois consécutifs | attributs tabulaires → plongement T-JEPA (PCA et attributs bruts en références) | — | martingale de test conforme (Vovk et al., 2003) sur un score de non-conformité |
| P6-C | BAF, dérive de concept | Concept | natif du jeu (mensuel) | frontières de mois ; taux de fraude mensuel | attributs et étiquette de fraude, avec délai d'étiquetage simulé | gradient boosting entraîné sur les mois 0–2, puis figé | e-détecteur sur l'erreur binaire, taux nul q̂ recentré, ou p-valeurs conformes |
| P7 | Oracle à direction connue | Data (borne) | synthétique (F1–F4) | injections | projection w* = Σ⁻¹Δμ | — | CUSUM du rapport de vraisemblance |

**Familles de dérive injectées** (amplitudes calibrées sur les transitions historiques, Δμ̂ rétrécis ; τ* tiré uniformément dans la fenêtre de test) :

- **F1** : primes factorielles, de la forme B_tΔλ ;
- **F2** : largeur pilotée par les caractéristiques, (C_tΔγ)_⊥ ;
- **F3** : translation du mode de marché ;
- **F4** : rotation factorielle ou déformation de Σ_t.

### 5.3 Tableau 3 — Configuration expérimentale (jeu × pipeline)

| Exp. | Section | Jeux | Pipelines | Dérives | Calibration et mesures | Prio. |
|---|---|---|---|---|---|---|
| E1 | §2 | D1, D2, D3 ; D6 | P1-C, P1-D, P2-C, P3-C, P3-D, P7 | réelles ; F3, F1, F2 | ARL₀ ∈ {20, 252} ; G_ADD, G_SR, G_floor ; part dans le budget ; K_eff | A |
| E2 | §5.1 | D5 | P7 ; mélange en dimension D ; signe | translations gaussiennes connues | ADD mesuré rapporté au prédit ; M(D) | A |
| E3 | §5.2 | D5 (GARCH), D6, D2–D3 bruts (placebo) | P1-C, P1-D, P2-C, P3-C/D, P3-CS, P5-C/D | aucune (H₀) | FPR au niveau du treillis ; ARL₀ ; Γ^spec et Γ^op ; encodeurs à fenêtre L ∈ {5, 20, 60} | A |
| E4 | §5.3 | D2, D3 [A] ; D4 [B] ; D6 | P2-C, P3-C, P3-KF, P3-CS, P4-C | F1, F2, F3 ; N de 8 à N_max | audit (spectres de Sharpe de dérive débiaisés, plafonds N1–N3) ; pente de log G_ADD en log N | A/B |
| E5 | §5.4 | D3 [A] ; D2, D4 [B] ; D6 | P5-C contre P3-C, P3-CS, P4-C ; P5-MAE, P5-TEMP | F1, F2, F3 | G_ADD ; r(D)/M(D) ; RankMe ; spectre de transmission T(u) ; dictionnaire contre sous-espace [C] | A/B/C |
| E6 | §5.5 | D6 | P1-D, P3-D, P4-D, P5-D | F4 | G_ADD ; Γ_z^op | B |
| E7 | §5.6 | D6 (D3) | P5-ADAPT, P5-C gelé | F1, F2 ; H₀ année par année | délai rapporté au critère 2·ADD_or ; ARL₀ selon l'âge du pré-entraînement | C |
| E8 | §5.7 | D1, D2, D3 [A] ; D4 [B] | P1 à P5 | réelles, trois datations | part dans le budget oracle ; détections dans la phase ; fausses alarmes en phase calme | A/B |
| E9 | §5.8 | D7 | P6-D (T-JEPA, PCA, brut), P6-C | natives mensuelles | délai après frontière de mois ; FPR dans les mois stables | B |
| E10 | Annexe D | D5, D6, D2–D3 bruts | P1-C, P3-C, P5-C | F1, F2 sous queues épaisses, levier, dépendance asymétrique, rendements nuls | FPR, G_ADD | C |
| E11 | Annexe D | D8 | P2-C, P3-C, P5-C | réelles ; F1–F2 | G_ADD | C |

### 5.4 Articulation des jeux et des pipelines

Les règles suivantes, à reprendre en clair dans le corps de l'article, fixent qui lit quoi :

- Les dérives injectées ne vivent que sur les fonds neutralisés D6, où la vérité terrain est exacte et les fausses alarmes se comptent sur autant de trajectoires nulles que nécessaire.
- Les dérives réelles se lisent sur D1–D4 bruts, avec trois datations comme vérité terrain.
- BAF ne porte que ses dérives natives.
- Les simulations D5 valident les bornes et la calibration avant tout contact avec le réel.
- Chaque pipeline P1 à P5 traverse la même pile de détection ; seules changent la représentation et, pour CONCEPT, la cible du classifieur.

**Gabarit d'encadré**, placé en tête de chaque sous-section expérimentale :

> **Configuration.** Data: D·· (window …). Representation: … (selection: …). Pipelines: P·· . Drifts: family …, magnitude calibrated on …, onset τ* ~ U[…]. Calibration: ARL₀ ∈ {20, 252}, exact lattice level / block bootstrap / sign-flip randomization. Replications: … . Metrics: … .

---

## 6. Registre des risques

| # | Risque | Mécanisme | P | I | Signal précoce | Parade |
|---|---|---|---|---|---|---|
| R1 | Charge du périmètre complet | onze expériences et deux domaines en sept semaines, pour 15 à 20 h/semaine | élevée | élevée | retard à J2 | deux pistes, code livré une semaine en avance, débordement des items C, raccourcissement du §2.6 |
| R2 | Métrique du pooling ambiguë | la Fig. 30 de l'Article B ne dit pas si son gain est un rapport de délais ou de Sharpe | certaine | moyenne | — | remesure de P2 dans G_ADD, G_SR et G_floor (E1) avant tout seuil |
| R3 | Antériorité | composantes de faible variance déjà proposées (Kuncheva & Faithfull, 2014 ; Qahtan et al., 2015) | certaine | moyenne | — | citation dès le §1 ; P3-KF reproduit l'antériorité ; revendications limitées à la borne, la calibration et la représentation |
| R4 | Absorption | encodeur adaptatif, BatchNorm en mode entraînement, normalisation temporelle d'instance, EMA active pendant la surveillance | moyenne | élevée | ADD de P5 bien au-dessus de P3 sur F1 | référence gelée, tests de contrat, E7 |
| R5 | Calibration latente | chevauchement (Γ_z = L), carrés (clustering), pénalité de dépassement des statistiques de premier ordre (ARL₀ divisé par 2,9 dans notre test GARCH) | moyenne | élevée | FPR hors du niveau du treillis | chemin surveillé par jour, flux de signe exacts, e-détecteurs, randomisation |
| R6 | Dimension et géométrie | taxe M(D), effondrement spectral, biais de Wishart inverse (+15 % pour n = 500 et D = 64) | moyenne | moyenne | RankMe < 0,5·D ; T(u) faible | D ≤ 16, Ledoit–Wolf, flux de signe |
| R7 | Attribution | le gain JEPA n'est qu'un gain de normalisation transversale | moyenne | élevée | P3-CS ≈ P5 | P3-CS et rangs obligatoires dans chaque tableau principal |
| R8 | Échantillon SSL | environ 5 000 jours | moyenne | moyenne | JEPA ≈ PCA | poids partagés entre actifs ; modèle ≤ 1 M paramètres |
| R9 | Audit bruité | biais de bruit 252·N·(1/n₁+1/n₂) ≈ 482 en SR² (N = 239, deux phases de 250 jours) | élevée | moyenne | estimations débiaisées négatives | projections de dimension ≤ 30, regroupées sur les transitions, bootstrap |
| R10 | Information de localisation rare | un Sharpe sans frictions élevé et persistant serait arbitré | moyenne | élevée | J2 : SR de dérive faible dans tous les sous-espaces | contingence C1 |
| R11 | Peu de phases réelles | 15 à 25 phases par marché | élevée | faible | IC larges | US, Europe et datation sectorielle ; preuve d'appui seulement |
| R12 | BAF synthétique | GAN, huit mois, dérive native | certaine | moyenne | — | parler de « dérive native d'un jeu synthétique », sans revendication « in-the-wild » |
| R13 | Concept drift sur BAF | déséquilibre de classes et délai d'étiquetage : l'erreur binaire n'est plus Bernoulli(½) | élevée | moyenne | — | taux nul q̂ recentré ou p-valeurs conformes ; délai simulé |
| R14 | Biais du survivant | D2 et D3 publics | certaine | moyenne | — | sans effet sur D6, où les dérives sont effacées ; recensement européen sur D4 |
| R15 | Levier effacé par la symétrisation | inversion de signe journalière | certaine | faible | — | bras placebo sur fond brut (E3, E10) |
| R16 | Entrées de CD-DFM | caractéristiques d'actualité propriétaires | élevée | moyenne | — | caractéristiques tirées des rendements et secteurs ; écart déclaré |
| R17 | Retard d'EUROFIDAI | extraction et nettoyage | moyenne | moyenne | panel absent à J3 | E4-EU en S5, débordement en décembre |
| R18 | Degrés de liberté | choix de D, des familles et des seuils après coup | moyenne | élevée | — | hash gelé à J4 ; fenêtre de test intouchée jusque-là |
| R19 | Format ICML | huit pages pour trois tableaux, §2 et la théorie | élevée | moyenne | v0.9 dépasse huit pages | tableaux compacts, versions longues en Annexe C |
| R20 | Revendication théorique | optimalité de second ordre de la Prop. 3 non démontrée | moyenne | faible | — | énoncé d'atteignabilité, conjecture en annexe |
| R21 | Soumissions parallèles | conférences sans actes face à la règle ICML ; anonymat | faible | moyenne | — | vérification de l'appel ICML 2027 |
| R22 | Propriété intellectuelle et licences | clauses CIFRE de LUSIS ; redistribution EUROFIDAI interdite | moyenne | moyenne | — | accord écrit avant tout dépôt public ; chaîne reproductible sur données publiques |

**Contingences.**

- **C1** (R10 ou J2) : les dérives de second ordre (F4) deviennent l'axe empirique principal. Un ratio de variance de 1,5 à 2 offre 24 à 77 fois le budget KL d'une dérive de SR = 1.
- **C2** : accent sur les domaines à fort rapport signal sur bruit (BAF, IoT).
- **C3** (échec de J4) : titre B.
- **C4** (R1) : ordre de raccourcissement du §2.6.

Aucune méthode non publiée n'entre dans le plan : l'anti-effondrement suit la recette publique (cible EMA, stop-gradient, régularisation de variance).

---

## 7. Principes de rédaction

- **Audit DPI** : aucune phrase de l'article ne doit suggérer une hausse de KL. Le gain vient de la concentration, jamais de la création d'information.
- **Métriques du pooling** : toujours préciser la métrique utilisée (G_ADD, G_SR ou G_floor) quand on cite un gain de pooling.
- **FPR des flux de signe** : le critère est le niveau atteignable du treillis, pas une valeur nominale continue.
- **Gains prévus vs mesurés** : les valeurs de planification du §4.3 ne sont jamais présentées comme des résultats.
- **BAF** : toujours « 30 attributs », « six jeux de 1 M », « huit mois ».
- **Variance du marché** : citer séparément R² = 0,36 (CD-DFM) et ρ ≈ 0,40 (Article B), sans les présenter comme mesurées sur les panels du projet.
- **Combinaison des canaux** : toujours par mélange, jamais par produit d'e-processus.
