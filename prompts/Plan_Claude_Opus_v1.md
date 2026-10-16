Quatre points du cadrage actuel sont faux ou manquants ; une fois corrigés, la thèse tient.

1. **η ≈ 0,9 contredit les données du projet.** Sur les 239 titres S&P 500 de Lehalle & Alouadi, le facteur de marché explique R² = 0,36 de la variance. La corrélation de signe ρ̂ ≈ 0,26 de l'Article B correspond, par la relation gaussienne ρ_signe = (2/π)·arcsin ρ, à une corrélation de rendements de 0,40 : η ≈ 0,40. Avec γ = 0,5, la formule G = γ/(1−η) de `KL_PCA_PIVOT.md` donne G ≈ 0,8, soit une perte. Cette formule mesure un rapport signal/bruit par direction. Elle omet le terme de largeur (breadth), qui croît avec N et constitue la seule échappatoire non bornée.
2. **Un JEPA à masquage inter-actifs ne peut pas isoler le signal idiosyncratique.** Il apprend ce qui se prédit depuis les actifs de contexte, donc la structure systématique. La cible atteignable est la dérive orthogonale au mode de marché et pilotée par les caractéristiques, pas l'idiosyncratique au sens des modèles factoriels.
3. **Surveiller ‖z_target − ẑ‖² branche un capteur d'échelle sur une dérive de localisation.** La Proposition d'orthogonalité de l'Article B le cantonne au second ordre. Un résidu de prédiction est de plus aveugle à toute dérive cohérente que le prédicteur reproduit depuis le contexte.
4. **La taxe dimensionnelle manque.** Ignorer la direction de la dérive dans un sous-espace de dimension D multiplie l'ADD par 2,0 à D = 10 et par 3,9 à D = 64, à ARL₀ = 504 (formule analytique validée par Monte Carlo à 4 % près, §1.2). Un latent de 128 dimensions surveillé tel quel paie 5,2× avant toute considération de KL. Le gain d'un espace latent ne vient pas de la KL (DPI) ; il vient de la compression de la dimension de l'alternative composite.

Titre retenu : *JEPA-Drift: Escaping the Sharpe Ceiling of Sequential Drift Detection through Latent Information Concentration*. « Concentrating Kullback-Leibler Divergence » se lit comme une hausse de KL, qu'un reviewer familier de la DPI attaquera d'emblée. Si le jalon G2 échoue, l'article sort sous *Latent Information Floors: What Learned Representations Can and Cannot Buy for Sequential Drift Detection* ; le protocole garde les deux issues publiables.

## 1. Analyse critique et positionnement

### 1.1 Du linéaire au non linéaire sans violer la DPI

Notations. $x_t \in \mathbb{R}^N$ : rendements du jour $t$ ; $C_t \in \mathbb{R}^{N\times P}$ : caractéristiques prédéterminées ($\mathcal{F}_{t-1}$-mesurables) ; $\Sigma_t$ : covariance conditionnelle ; après la rupture en $\tau^*$, la moyenne conditionnelle se déplace de $\Delta\mu_t$. Pour une représentation $\phi$, $\mathcal{I}_\phi$ désigne le taux d'information de Kullback-Leibler par observation du processus $\phi(x_t;C_t)$ au sens de Lai (1998), et $\mathcal{I}_x$ celui des données brutes.

**Proposition 1 (hiérarchie informationnelle, alternatives de localisation locales).**
$$\tfrac12\,\overline{\Delta\mu}^{\top}\bar\Sigma^{-1}\overline{\Delta\mu}\;\le\;\tfrac12\,\mathbb{E}\!\left[\Delta\mu_t^{\top}\Sigma_t^{-1}\Delta\mu_t\right]\;\le\;\tfrac12\,\mathbb{E}\!\left[\Delta\mu_t^{\top}\mathcal{J}_t\,\Delta\mu_t\right]=\mathcal{I}_x,\qquad \mathcal{I}_\phi\le\mathcal{I}_x\ \ \forall\phi,$$
avec $\bar\Sigma=\mathbb{E}[\Sigma_t]$ et $\mathcal{J}_t$ l'information de Fisher conditionnelle de localisation. La première inégalité découle de la convexité jointe de $(a,S)\mapsto a^\top S^{-1}a$ (Jensen), la deuxième de $\mathcal{J}_t\succeq\Sigma_t^{-1}$ (Cramér-Rao, égalité ssi gaussien conditionnel), la dernière de la DPI. Le terme de gauche borne tout moniteur linéaire statique.

Un encodeur non linéaire ne crée pas d'information. Il récupère ce que la classe linéaire statique jette, par trois canaux, seules sources légitimes d'un gain JEPA :

- **(N1) Volatilité commune.** L'écart $\mathbb{E}[\sigma_t^2]\,\mathbb{E}[\sigma_t^{-2}]$ est le gain de Jensen que l'Article B n'atteignait qu'avec un oracle à paramètres GARCH connus par anticipation (×10,6 sur le krach de 2020). En univarié, $\sigma_t$ ne s'obtient que par un modèle ajusté sur le passé. Dans la coupe, la dispersion du jour le mesure sans modèle, avec une erreur relative en $O(N_{\text{eff}}^{-1/2})$, et une statistique homogène de degré 0, inaccessible à toute application linéaire non nulle, l'exploite en ligne.
- **(N2) Chargements variables pilotés par les caractéristiques** (IPCA, CD-DFM) : écart entre $(\overline{\Delta\mu},\bar\Sigma)$ et $(\Delta\mu_t,\Sigma_t)$.
- **(N3) Non-gaussianité résiduelle** : écart entre $\mathcal{J}_t$ et $\Sigma_t^{-1}$ une fois la volatilité retirée.

**Définition (concentration).** Pour une famille $\phi_D$ de dimension $D$, la rétention vaut $r_\phi(D)=\mathcal{I}_{\phi_D}/\mathcal{I}_x\in[0,1]$. La thèse s'énonce $\max_D r_{\text{JEPA}}(D)/M(D)>\max_D r_{\text{lin}}(D)/M(D)$, où $M$ est la taxe dimensionnelle de la Proposition 3. JEPA gagne en retenant plus d'information à faible dimension.

Le plafond du gain JEPA sur le meilleur modèle linéaire se mesure donc avant tout pré-entraînement. Pour le canal N1, sous volatilité commune log-normale ($s$ = écart-type de $\ln\sigma_t^2$, fixé à 0,9 pour l'illustration), l'efficacité relative au rapport de vraisemblance conditionnel s'ordonne ainsi :

| Moniteur sur une même projection $u$                          | Efficacité                          | Calibration                          |
| ------------------------------------------------------------- | ----------------------------------- | ------------------------------------ |
| CUSUM de moyenne, variance inconditionnelle                   | $e^{-s^2}=0{,}44$                   | faussée (§3.2)                       |
| CUSUM de signe, mise fixe (Article B)                         | $\tfrac{2}{\pi}e^{-s^2/4}=0{,}52$   | exacte                               |
| e-détecteur de signe, mise $\propto 1/\hat\sigma_{t\mid t-1}$ | $2/\pi=0{,}64$ (prévision parfaite) | exacte, quelle que soit $\hat\sigma$ |
| statistique auto-normalisée de degré 0 ($N\to\infty$)         | $e^{-s^2/4}=0{,}82$                 | pivot exact sous échelle commune     |
| RV conditionnel, $\sigma_t$ connu                             | $1$                                 | oracle                               |

Une normalisation transversale non apprise (dé-moyennage puis division par la dispersion du jour, soit une LayerNorm appliquée au vecteur de coupe) atteint déjà 0,82. Sur N1, il ne reste au JEPA qu'un facteur 1,22. Sans ce témoin, le gain attribué au JEPA risque d'être celui d'une couche de normalisation.

**Corrections de `KL_PCA_PIVOT.md`.**
- Le calcul du §4 suppose une variance résiduelle isotrope et compare des normes euclidiennes. L'objet correct est la norme de Mahalanobis résiduelle, qui porte un facteur d'ordre $N-1$ quand la dérive résiduelle est dispersée.
- « On jette $v_1$ » jette un canal d'information : $\Delta\mu^\top\Sigma^{-1}\Delta\mu=\sum_k(v_k^\top\Delta\mu)^2/\lambda_k$ est additif sur les directions propres. Le mode de marché se surveille à part (moniteur de l'Article B), et les deux flux se combinent par produit d'e-processes.
- $\alpha=0{,}05$ avec $\ln(1/\alpha)\approx3$ correspond à ARL₀ = 20 jours, une fausse alarme par mois : le point permissif du recensement de l'Article B. Au point opérationnel ARL₀ = 252, $\ln(1/\alpha_0)=5{,}53$, et détecter en 60 jours exige SR = 6,8 en univarié, pas 5,0.
- Le « paradoxe du hedge fund » n'est déplacé qu'à moitié. $\mathrm{SR}_x$ est exactement le Sharpe sans frictions du portefeuille tangent à la dérive ; un détecteur qui conclut en 60 jours certifie des Sharpe sans frictions d'environ 6,8 sur la durée du régime. L'échappatoire vaut dans la mesure où Sharpe sans frictions et Sharpe net divergent.

### 1.2 Plancher de délai dans l'espace latent

**Proposition 2 (plancher oracle).** Sous la condition de taux d'information de Lai (1998), à savoir la convergence r-rapide du log-rapport de vraisemblance normalisé vers $\mathcal{I}_z$, tout temps d'arrêt $T$ adapté à la filtration latente avec $\mathrm{ARL}_0(T)\ge1/\alpha_0$ vérifie, quand $\alpha_0\to0$ et sous modèle gaussien conditionnel :
$$\mathrm{ADD}_z\;\ge\;\frac{504\,\ln(1/\alpha_0)}{\mathrm{SR}_z^2}\bigl(1+o(1)\bigr),\qquad \mathrm{SR}_z^2:=252\,\mathbb{E}\!\left[\Delta\mu_{z,t}^{\top}\Sigma_{z,t}^{-1}\Delta\mu_{z,t}\right].$$
$\mathrm{SR}_z$ est le Sharpe annualisé du portefeuille tangent à la dérive dans l'espace latent, puisque $\max_w(w^\top\Delta\mu_z)^2/(w^\top\Sigma_zw)=\Delta\mu_z^\top\Sigma_z^{-1}\Delta\mu_z$ (Cauchy-Schwarz). Le plafond de Sharpe de l'Article B en est le cas $N=D=1$, et la DPI impose $\mathrm{SR}_z\le\mathrm{SR}_x$. À direction connue, $D=1$ suffit : $w^*=\Sigma^{-1}\Delta\mu$ atteint l'égalité. La dimension latente ne sert qu'à couvrir l'incertitude sur la direction.

**Structure factorielle.** Avec $x_t=B_tf_t+\varepsilon_t$, $\mathrm{Cov}(f_t)=\Sigma_F$, $\mathrm{Cov}(\varepsilon_t)=\Psi$ diagonale et $\Delta\mu=B\Delta\lambda+\Delta\alpha$, des facteurs pervasifs donnent, quand $N\to\infty$ :
$$\mathrm{SR}_x^2\;\to\;\underbrace{252\,\Delta\tilde\lambda^{\top}\Sigma_F^{-1}\Delta\tilde\lambda}_{\mathrm{SR}_F^2,\ \text{borné en }N}\;+\;\underbrace{252\,\Delta\alpha_\perp^{\top}\Psi^{-1}\Delta\alpha_\perp}_{\text{largeur},\ \propto N},$$
où $\Delta\alpha_\perp$ est le résidu GLS de $\Delta\alpha$ sur les chargements et $\Delta\tilde\lambda$ en absorbe la partie alignée. La saturation $K_{\text{eff}}\approx1/\hat\rho\approx3{,}8$ de l'Article B correspond à un seul facteur qui dérive : rapporté au Sharpe d'un titre isolé, le premier terme vaut $1/\rho$. Il n'existe que deux échappatoires. Soit plusieurs facteurs dérivent ensemble et le plateau monte à $\mathrm{SR}_F^2/\mathrm{SR}_1^2$, toujours borné ; soit une dérive idiosyncratique se disperse sur beaucoup de titres et le gain croît avec $N$. La table 6 de Lehalle & Alouadi plaide pour la première : sur leur fenêtre de crise (247 jours, une graine, à lire pour le signe selon les auteurs), les facteurs cash-neutral utilities, santé, consommation discrétionnaire, technologie et financières varient de +13 % à −16 %. À 8 % de volatilité annuelle, hypothèse à mesurer, chacun porterait un SR de dérive de 1 à 2.

**Proposition 3 (alternative composite).** Pour une dérive de direction inconnue dans un sous-espace de dimension $D_{\text{eff}}$, le détecteur à mélange gaussien isotrope accordé à l'amplitude (méthode des mélanges de Robbins ; GLR de Siegmund & Venkatraman, 1995) atteint
$$\mathrm{ADD}_z\approx\frac{504\,\ln(1/\alpha_0)}{\mathrm{SR}_z^2}\,M(D_{\text{eff}},\alpha_0),\qquad M=\frac{x}{\ln(1/\alpha_0)},\quad x=\ln\frac{1}{\alpha_0}+\frac{D_{\text{eff}}}{2}\ln\!\Bigl(1+\frac{2x}{D_{\text{eff}}}\Bigr).$$
Le terme $\frac D2\ln(\cdot)$ est la redondance minimax d'une famille à $D$ paramètres (Rissanen ; Clarke & Barron, 1990). Quand $\alpha_0\to0$, il devient d'ordre $\frac D2\ln\ln(1/\alpha_0)$ et négligeable. Aux ARL₀ opérationnels, il domine dès $D\approx10$ ; pour $D\gg\ln(1/\alpha_0)$, $x\approx\sqrt{D\ln(1/\alpha_0)}$.

| $D_{\text{eff}}$        | 1    | 5    | 10   | 20   | 64   | 128  | 500  |
| ----------------------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| $M$, ARL₀ = 252         | 1,24 | 1,71 | 2,08 | 2,62 | 4,10 | 5,50 | 10,2 |
| $M$, ARL₀ = 504         | 1,22 | 1,66 | 2,01 | 2,51 | 3,91 | 5,23 | 9,64 |
| Monte Carlo, ARL₀ = 504 | 1,27 | 1,63 | 2,06 | —    | 3,83 | —    | 9,82 |

Monte Carlo : 300 réplications (150 à $D=500$) ; l'oracle à direction connue donne $M\in[0{,}95;1{,}04]$. Trois conséquences de design en découlent. Le latent surveillé a $D_{\text{eff}}\le10$–16, et un JEPA de dimension 128 ne se surveille qu'à travers une tête de lecture compressée. Un dictionnaire de $M$ directions économiques (facteurs CD-DFM, secteurs, styles) coûte $\ln M$ au lieu de $\frac D2\ln(\cdot)$ mais perd $\cos^2\theta$, où $\theta$ est l'angle entre la dérive blanchie et l'atome le plus proche : à ARL₀ = 504, vingt atomes battent le mélange continu de dimension 10 si $\theta<22°$, de dimension 64 si $\theta<48°$, et jamais celui de dimension 5. Enfin, la loi d'échelle en $N$ devient la signature falsifiable de l'article : $G\propto N^0$ (pooling, dérive de marché, Article B), $G\propto N^{1/2}$ (coupe entière non structurée, la taxe en $\sqrt N$ absorbant la moitié de l'exposant), $G\propto N$ (dérive de largeur pilotée par $P$ caractéristiques, latent structuré de dimension fixe).

**Niveau du moniteur et décomposition du gain.** $\mathrm{ADD}_{\text{mon}}\approx(\Gamma_z^{\text{op}}/e_m)\,\mathrm{ADD}_z$, où $e_m$ vient de la table d'efficacité et $\Gamma_z^{\text{op}}$ est la pénalité de calibration opérationnelle définie au §3.2. Le gain sur l'univarié se factorise :
$$G=\frac{\mathrm{ADD}_{\text{univ}}}{\mathrm{ADD}_{\text{lat}}}=\underbrace{\frac{\mathrm{SR}_z^2}{\mathrm{SR}_1^2}}_{\text{concentration}}\times\underbrace{\frac{M(1)}{M(D_{\text{eff}})}}_{\text{taxe}}\times\underbrace{\frac{e_z\,\Gamma_1^{\text{op}}}{e_1\,\Gamma_z^{\text{op}}}}_{\text{blanchiment}}.$$
Ordre de grandeur : détecter en 252 jours au plus à ARL₀ = 504 exige $\mathrm{SR}_z\ge3{,}53$ (oracle), 4,54 ($D_{\text{eff}}=5$), 5,00 ($D_{\text{eff}}=10$), 6,97 ($D_{\text{eff}}=64$). Ces seuils fixent ce que l'audit de Phase 0 doit trouver dans les données.

### 1.3 Verrous théoriques immédiats

**V1 — Aveuglement jacobien.** Pour une petite dérive, $\Delta\mu_z\approx\mathbb{E}[J_\phi]\,\Delta\mu$ : toute composante dans le noyau de $J_\phi$ disparaît. Dans les réseaux linéaires profonds, le biais implicite des JEPA privilégie les directions prédictives sur les directions de forte variance, à l'inverse de MAE (Littwin et al., NeurIPS 2024). C'est l'argument théorique de JEPA contre PCA pour les directions peu variables mais structurées, et la raison pour laquelle les dérives non prédictibles depuis le contexte sont perdues. Instrument : le rapport de transmission $T(u)=\|\Sigma_z^{-1/2}\mathbb{E}[J_\phi]u\|^2/\|\Sigma^{-1/2}u\|^2$, calculé par différences finies sur les directions injectées ; $T>1$ n'est possible que par les canaux N1–N3. Prédiction testable : à $D$ égal, $T_{\text{JEPA}}>T_{\text{MAE}}$ sur les directions de faible variance.

**V2 — Validité de $H_0$ dans le latent.**

*Lemme (blanchiment par encodeur impair).* Soit $\phi(\cdot\,;C)$ impaire en $x$, $\phi(-x;C)=-\phi(x;C)$, avec $C_t$ et une direction $u_t$ $\mathcal{F}_{t-1}$-mesurables. Si, sous $H_0$, la loi de $x_t$ sachant $\mathcal{F}_{t-1}$ est centralement symétrique et $\mathbb{P}(u_t^\top\phi(x_t;C_t)=0\mid\mathcal{F}_{t-1})=0$, alors $b_t=\mathbf 1\{u_t^\top\phi(x_t;C_t)>0\}$ est i.i.d. Bernoulli(1/2), quelles que soient les dynamiques de volatilité, de corrélation et de queues.

*Preuve.* $g=u_t^\top\phi(\cdot\,;C_t)$ est impaire conditionnellement à $\mathcal{F}_{t-1}$ ; la symétrie donne $\mathbb{P}(g(x_t)>0\mid\mathcal{F}_{t-1})=\mathbb{P}(g(x_t)<0\mid\mathcal{F}_{t-1})=1/2$, et une suite de bits de loi conditionnelle constante 1/2 est i.i.d. ∎

Le lemme étend la propriété de blanchiment de l'Article B du signe d'un rendement au signe d'une projection impaire de toute la coupe. Il fournit aussi la version latente de la Proposition d'orthogonalité. Avec $\phi_{\text{imp/pair}}(x)=\tfrac12[\phi(x)\mp\phi(-x)]$, toute statistique impaire est exactement aveugle à un changement qui préserve la symétrie centrale (volatilité, corrélation, queues), et toute statistique paire ne voit une translation qu'au second ordre. Le JEPA reçoit donc deux têtes : impaire pour le pipeline Concept latent (capteur de signe), paire pour le pipeline Data latent (capteur énergétique recalibré). Si $\phi$ est en outre homogène de degré 0, la statistique entière, pas seulement son signe, a une loi nulle libre de l'échelle commune.

Trois limites s'appliquent. Les égalités (rendements nuls, valeurs manquantes imputées à zéro sur les petites capitalisations) se tranchent par tirage aléatoire, ce qui préserve l'exactitude. L'asymétrie de dépendance de queue (Longin & Solnik, 2001 ; Ang & Chen, 2002) viole la symétrie centrale et impose un recentrage sur un taux $\hat q_u$ estimé, comme pour l'asymétrie dans l'Article B. La prime de risque déplace la médiane, moins dans les directions cash-neutral que sur l'indice (SPY : de 0,541 à 0,554 de jours haussiers sur 2011–2018 dans l'Article B).

**V3 — Agrégation.** Le flux poolé de l'Article B perd sa blancheur au-delà de K = 10, parce que la variance conditionnelle d'une somme de signes suit la corrélation transversale du jour. Le lemme ne couvre qu'un signe par direction. Plusieurs directions se combinent par mélange d'e-processes : une moyenne de martingales de test sous la même filtration reste une martingale de test, quelle que soit la dépendance entre directions. Ni Bonferroni ni bootstrap.

**V4 — Taxe dimensionnelle.** $D_{\text{eff}}\le10$–16, ou priors structurés (dictionnaire, parcimonie), par la Proposition 3.

**V5 — Non-anticipation.** Encodeur pré-entraîné strictement avant la fenêtre surveillée ; caractéristiques datées à leur publication, les fondamentaux trimestriels arrivant avec plusieurs semaines de retard ; statistiques de normalisation gelées ; embargo d'au moins la longueur de contexte plus 5 jours.

## 2. Orchestration et jalons

### 2.1 Phases

| Phase                                       | Fenêtre                 | Contenu                                                                                                                   | Livrable                                 | Jalon         |
| ------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------------- |
| P0 — Théorie et audit                       | 12 oct. – 8 nov. 2026   | Props 1–3, lemme, critère d'absorption ; validation Monte Carlo ; audit S&P 500                                           | note théorique v1, notebook d'audit, CSV | G0, 9 nov.    |
| P1 — Pile de surveillance, échelle linéaire | 26 oct. – 13 déc.       | moniteurs (signe, e-détecteurs, degré 0) ; fonds symétrisés S&P 500 et EUROFIDAI ; familles F1–F4 ; échelle B0–B5         | `benchmark_runner`, courbes ADD–ARL₀     | G1, 14 déc.   |
| P2 — Représentations (José, en parallèle)   | 26 oct. – 17 janv. 2027 | CA-T-JEPA à têtes impaire/paire ; T-JEPA sur BAF ; diagnostics anti-collapsus                                             | checkpoints conformes au contrat         | G2a, 18 janv. |
| P3 — Confrontation, attribution             | 4 janv. – 28 févr.      | JEPA contre l'échelle linéaire ; ablations (normalisation seule, MAE, TAU-JEPA, balayage de D) ; spectres de transmission | tableaux principaux                      | G2, 1er mars  |
| P4 — In-the-wild, BAF, rédaction            | 1er mars – 30 avr.      | régimes datés ; dérive mensuelle BAF ; rapport anytime-valid ; relecture interne mi-avril                                 | manuscrit gelé le 30 avril               | soumission    |

Échelle de référence : B0, indice univarié (signe, Article B) ; B1, pooling équipondéré ; B2, PCA résiduel ; B3, normalisation transversale de degré 0 et rangs transversaux centrés (impairs, invariants d'échelle et de translation) ; B4, facteurs cash-neutral CD-DFM et IPCA ; B5, oracle à direction connue. Les familles de dérive injectées sont calibrées sur les transitions historiques (vecteurs $\Delta\hat\mu$ rétrécis) : F1, primes factorielles $B_t\Delta\lambda$ (plateau attendu) ; F2, largeur $(C_t\Delta\gamma)_\perp$ (croissance attendue en $N$) ; F3, mode de marché (témoin qui doit reproduire la saturation de l'Article B) ; F4, rotation factorielle ou déformation de $\Sigma_t$ (tête paire).

### 2.2 Jalons Go/No-Go

- **G0 (9 nov.)** — (a) Les ADD simulés reproduisent les Propositions 2–3 à ±10 % sur fond gaussien et sur fond GARCH symétrisé. (b) L'audit place le plancher oracle transversal sous la durée d'au moins 25 % des phases datées à ARL₀ = 252, contre 2 sur 66 (3 %) en univarié dans l'Article B. Échec de (b) : contingence C1 ou C2 (§3.4), car par la DPI aucun encodeur ne fera mieux que l'oracle.
- **G1 (14 déc.)** — Le meilleur moniteur de l'échelle linéaire tient sa FPR à ±15 % du nominal sur fonds nuls symétrisés ; les flux de signe étant exacts par construction, cela teste la pile elle-même. Il atteint G ≥ 4 contre l'univarié composite sur événements appariés, et l'exposant d'échappement $\hat\beta$ (pente de $\log G$ en $\log N$) est positif sur F2 avec un IC à 95 % qui exclut 0. Si G0 passe et G1 échoue, l'information existe mais la surveillance la perd : on corrige la pile, pas l'encodeur.
- **G2a (18 janv.)** — Rang effectif RankMe de la tête de lecture ≥ 0,5·D ; $T_{\text{JEPA}}(u)\ge T_{\text{PCA}}(u)$ sur au moins la moitié des directions injectées ; aucun collapsus selon les critères Drive vs. Decay.
- **G2 (1er mars)** — Le JEPA bat le meilleur de B3 et B4 d'un facteur ≥ 1,25 en ADD à ARL₀ égal, sur au moins deux des familles F1, F2, F4, avec un IC à 95 % qui exclut 1 et $D^*\le16$. Échec : titre de repli, résultat JEPA négatif ou conditionnel documenté.

### 2.3 Seuils minimaux pour valider la thèse

**Contre le plafond de Sharpe univarié : G ≥ 4**, composite contre composite ($M(1)$ des deux côtés), sur événements appariés. Un facteur 4 divise par deux le SR requis ; en deçà, la part des régimes datés qui entre dans le budget bouge à peine (64 phases sur 66 hors budget à ARL₀ = 252 dans l'Article B). Le critère lisible par un reviewer reste la part des phases dans le budget, avec une cible de 25 %.

**Contre la saturation transversale : borne inférieure de l'IC de G au-dessus de 3,8**, et non de 2. Le pooling de l'Article B réalise 2× pour un plafond théorique de 3,8, et battre le réalisé ne prouve rien. Une valeur ponctuelle de G ne démontre pas l'échappement ; une pente $\hat\beta>0$ au-delà de $N\approx20$, si.

**Contre le benchmark PCA-orthogonal : ≥ 1,25× (−20 % d'ADD) face au meilleur concurrent linéaire ou non appris (B3, B4).** Passer de $D=5$ à $D=10$ change déjà $M$ de 1,21×, si bien qu'un gain inférieur relève du réglage, pas de la représentation. La normalisation non apprise prend 0,82 sur N1 et laisse au JEPA 1,22× sur ce canal, plus ce que N2 et N3 apporteront, inconnu avant l'audit.

### 2.4 Séquence technique

Le benchmark PCA résiduel passe d'abord côté surveillance ; le pré-entraînement JEPA démarre en parallèle le 26 octobre côté représentation. Trois raisons imposent l'ordre côté surveillance. Un ADD JEPA médiocre reste ininterprétable sans pile calibrée, car il faut savoir si l'information manque (G0), si la calibration fuit (G1) ou si l'encodeur perd la direction (G2a). L'audit et l'échelle linéaire peuvent arrêter ou réorienter le projet avant toute dépense JEPA. L'échelle linéaire fixe enfin le contrat d'interface, des tableaux $Z$, dans lequel le JEPA se branche.

Le parallélisme tient au calendrier. En séquentiel strict, P3 commencerait en mars et laisserait huit semaines à P4. Chemin critique : contrats de données → pile de surveillance → G1 → confrontation → G2 → rédaction.

### 2.5 Arbitrages structurants

| Décision             | Retenu                                                                                                                              | Écarté                                   | Motif de clôture                                                                                                                                                       |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ordre                | linéaire d'abord (surveillance), JEPA en parallèle                                                                                  | JEPA d'abord ; séquentiel strict         | ininterprétable sans pile calibrée ; chemin critique trop long                                                                                                         |
| Architecture finance | CA-T-JEPA : actifs comme jetons, conditionné par $C_t$, équivariant par permutation, têtes impaire/paire, chemin surveillé par jour | TAU-JEPA comme socle du chemin surveillé | fenêtres chevauchantes (Γ_z ≈ L) ; normalisation d'instance temporelle (absorption) ; échantillon T au lieu de N·T. TAU-JEPA reste en ablation comme prétexte temporel |
| Capteur              | signe de projection impaire, e-détecteurs, statistique de degré 0                                                                   | ‖z − ẑ‖²                                 | capteur d'échelle, aveugle aux dérives cohérentes, Γ_z > 1                                                                                                             |
| Calibration finance  | signe exact ; randomisation par inversion de signe pour les statistiques à amplitude                                                | permutation                              | l'échangeabilité échoue sous GARCH                                                                                                                                     |
| Statut de l'encodeur | gelé, rafraîchissement programmé                                                                                                    | adaptatif en ligne                       | critère d'absorption (§3.1)                                                                                                                                            |
| Baseline             | échelle B0–B5 avec CD-DFM, IPCA et normalisation transversale                                                                       | PCA statique seule                       | épouvantail qu'un reviewer relèvera                                                                                                                                    |
| Conférence           | NeurIPS 2027                                                                                                                        | ICML 2027 ; KDD 2027 cycle 2             | calendrier ; chevauchement avec l'Article B (§5)                                                                                                                       |

Un résultat récent montre ce que coûte le capteur écarté : avec un encodeur V-JEPA 2 gelé, le score d'erreur de prédiction atteint 0,89 d'AP sur un banc inter-jeux de données mais 0,29, proche du hasard, sur un banc équitable intra-nuScenes, alors qu'une sonde supervisée retrouve le signal dans les embeddings gelés. Le score de densité implicite des JEPA relève de la tête paire : le terme anti-collapsus d'un JEPA estime implicitement la densité des données, extractible sous le nom de JEPA-SCORE, ce qui en fait un capteur de nouveauté, pas de localisation.

## 3. Arbre des risques et contingences

### 3.1 (i) Absorption selon le statut de l'encodeur

Un encodeur adaptatif de constante de temps $\tau_a$ fait décroître la dérive latente, $\Delta\mu_z(s)=\Delta\mu_z(0)\,e^{-s/\tau_a}$, et l'information cumulée plafonne à $\mathcal{I}_z\tau_a/2$. Le critère de détectabilité et le délai qui en résulte sont :
$$\tau_a>2\,\mathrm{ADD}_{\text{or}},\qquad \mathrm{ADD}=-\frac{\tau_a}{2}\ln\!\Bigl(1-\frac{2\,\mathrm{ADD}_{\text{or}}}{\tau_a}\Bigr),\qquad \mathrm{ADD}_{\text{or}}=\frac{\ln(1/\alpha_0)}{\mathcal{I}_z}.$$
Pour $\tau_a$ = 2,5, 4 et 8 fois $\mathrm{ADD}_{\text{or}}$, le délai vaut 2,01, 1,39 et 1,15 fois l'oracle ; à $\tau_a\le2\,\mathrm{ADD}_{\text{or}}$, la dérive n'est jamais détectée. Comme $\mathrm{ADD}_{\text{or}}$ se compte en centaines de jours pour une dérive de localisation, un encodeur en ligne doit garder plusieurs années de mémoire : il est gelé de fait. C'est la « starvation » que tu as caractérisée entre ensembles adaptatifs (ARF, SRP) et détecteurs externes, transposée à l'encodeur. L'encodeur gelé, lui, n'absorbe rien mais vieillit : l'évolution lente des corrélations et des distributions de caractéristiques déplace la loi nulle latente et produit le pendant « flooding », celui que tu as observé sur tous les flux réels.

L'absorption se cache aussi hors de l'apprentissage : BatchNorm laissée en mode entraînement à l'inférence ; normalisation d'instance temporelle de type RevIN, standard dans PatchTST, qui retire la moyenne de la fenêtre et efface une translation après L jours ; mise à jour EMA du target encoder si l'entraînement continue pendant la surveillance.

Protocole :
1. Référence gelée $\phi_{\text{ref}}$ pré-entraînée sur $[t_0,t_1)$, rafraîchie à des intervalles $T_{\text{ref}}\ge4\,\mathrm{ADD}_{\text{cible}}$ sur une fenêtre qui exclut les $\mathrm{ADD}_{\text{cible}}$ derniers jours.
2. Après alarme confirmée, ré-ancrage : réentraînement sur le nouveau régime avant reprise de la surveillance.
3. Test de contrat : en mode `eval`, aucun buffer ne change ; aucune normalisation calculée sur l'axe temporel dans le chemin surveillé.
4. Vieillissement mesuré : ARL₀ réalisé par tranche annuelle depuis le pré-entraînement, sur fond symétrisé.

### 3.2 (ii) Calibration sous hétéroscédasticité latente

Γ_z a trois sources distinctes dans le latent.

- **Chevauchement temporel.** Un encodeur à fenêtre de L jours produit des latents autocorrélés ; pour une moyenne glissante uniforme, $\Gamma_z^{\text{spec}}=1+2\sum_{k<L}(1-k/L)=L$. Un encodeur temporel à fenêtre de 60 jours inflige Γ_z ≈ 60 à une statistique de premier ordre sans aucun GARCH.
- **Agrégats quadratiques.** ‖z‖² et ‖z − ẑ‖² héritent du clustering de volatilité ($\hat\Gamma\in[2{,}6;15{,}0]$ sur les ETF de l'Article B).
- **Pénalité de dépassement des statistiques de premier ordre**, absente de la définition spectrale de l'Article B. Des rendements non autocorrélés ont $\Gamma^{\text{spec}}=1$, et pourtant un CUSUM de premier ordre calibré en i.i.d. perd sa calibration sous GARCH dès que le seuil est profond. Vérification sur GARCH(0,08 ; 0,90) à innovations gaussiennes, 2 000 trajectoires : à δ = 0,5 et λ = 6, l'ARL₀ passe de 2 587 (i.i.d.) à 889, soit ÷2,9 ; à δ = 1 et λ = 3, de 1 894 à 669. À seuil peu profond (ARL₀ ≈ 190), l'erreur s'inverse (+17 %, côté conservateur). Le CUSUM de signe reste exact (213 contre 214). La pénalité croît avec ARL₀, donc dans la zone opérationnelle : c'est une Lethargy Tax que le facteur spectral ne voit pas.

Protocole :
1. Chemin surveillé par jour, sans fenêtre chevauchante, ou par blocs disjoints au prix d'un retard d'au plus L.
2. Premier ordre : signe de projection impaire (exact), ou e-détecteur par paris avec mises prévisibles $\lambda_t\propto1/\hat\sigma_{t\mid t-1}$, $\hat\sigma$ étant tiré de la dispersion transversale passée. Le modèle de volatilité n'entre que dans la mise, donc dans la puissance, jamais dans la validité (inégalité de Ville).
3. Statistiques à amplitude : calibration par randomisation d'inversion de signe, $x_t\mapsto\epsilon_tx_t$ avec $\epsilon_t$ de Rademacher appliqué à toute la coupe du jour ; exacte sous symétrie conditionnelle sans effet de levier, approchée sinon.
4. Fonds symétrisés : la même transformation appliquée au fond réel conserve $|x_t|$, donc clustering et corrélations, et détruit toute dérive de localisation. Chaque tirage fournit une trajectoire nulle avec la vraie hétéroscédasticité, et l'estimation de l'ARL₀ cesse de dépendre des quelques fausses alarmes que 25 ans de données autorisent. La symétrisation détruit l'effet de levier : un bras placebo sur fond brut (Δ = 0) reste obligatoire, comme dans l'Article B.
5. Mesure : $\Gamma_z^{\text{op}}:=\lambda_{\text{requis}}/\lambda_{\text{iid}}$ à ARL₀ fixé, pour chaque moniteur, sur fonds symétrisés.

### 3.3 (iii) Dimension latente et perte géométrique

La Proposition 3 rend l'ADD en U en fonction de D : la rétention $r(D)$ croît puis sature, la taxe croît en $\sqrt D$. Passer de D = 5 à 10 doit augmenter la rétention de plus de 21 % ; de 20 à 64, de plus de 56 %. L'effondrement spectral partiel des représentations auto-supervisées (Jing et al., ICLR 2022) frappe d'abord les petites valeurs propres, précisément celles où une dérive isotrope porte le plus de KL, puisque la contribution de la direction $k$ vaut $(v_k^\top\Delta\mu)^2/\lambda_k$. Le blanchiment estimé ajoute un biais : une Mahalanobis calculée avec $\hat\Sigma_z^{-1}$ sur $n$ points est gonflée d'un facteur proche de $n/(n-D-1)$ (moyenne de la Wishart inverse), soit +15 % à $n=500$ et $D=64$, ce qui se paie en fausses alarmes.

Protocole : balayage de la tête de lecture $D\in\{2,4,8,16,32\}$ sur un tronc JEPA fixe ; $D^*$ choisi sur la seule fenêtre de calibration ; retrait de Ledoit-Wolf, ou capteurs de signe qui n'inversent aucune matrice ; RankMe rapporté pour chaque $D$ ; spectres de transmission $T(u)$ sur une base fixée a priori (vecteurs propres, facteurs CD-DFM, directions de caractéristiques).

### 3.4 Registre complémentaire et contingences

| #   | Risque                                     | Mécanisme ou signal                                                                                                                                                                                                            | Contournement                                                                                                                                                                                                                          |
| --- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R4  | Comparaison univarié/transversal mal posée | événements différents comparés                                                                                                                                                                                                 | événements appariés : chaque dérive injectée, calibrée sur une transition historique, est mesurée sur l'indice et sur la coupe                                                                                                         |
| R5  | Survivant, look-ahead                      | panel de 97 survivants dans l'Article B ; fondamentaux publiés en retard                                                                                                                                                       | constituants point-in-time (EUROFIDAI) ; fondamentaux datés à leur publication                                                                                                                                                         |
| R6  | Gain de normalisation attribué au JEPA     | LayerNorm transversale = dé-moyennage + degré 0                                                                                                                                                                                | B3 obligatoire dans tout tableau principal                                                                                                                                                                                             |
| R7  | Échantillon SSL en finance                 | T ≈ 6 300 jours ; JEPA ≈ PCA par sur-apprentissage                                                                                                                                                                             | poids partagés entre actifs (1,5–3 M actif-jours) ; modèles ≤ 5 M paramètres                                                                                                                                                           |
| R8  | Audit bruité                               | biais de bruit $252N(1/n_1+1/n_2)\approx482$ en SR² pour N = 239 et deux phases de 250 jours                                                                                                                                   | projections de dimension ≤ 30, débiaisées, poolées sur les transitions, IC bootstrap                                                                                                                                                   |
| R9  | Peu de phases in-the-wild                  | 15 à 25 phases par marché sur 2000–2025                                                                                                                                                                                        | US, Europe et datation sectorielle ; présenté en appui, pas en preuve principale                                                                                                                                                       |
| R10 | BAF synthétique                            | BAF a été produit en appliquant des techniques de génération tabulaire à un jeu réel anonymisé de fraude à l'ouverture de compte : des demandes d'ouverture, pas des transactions ; huit mois, donc sept frontières mensuelles | formulation « dérive synthétique réaliste » ; martingales de test conformes (Vovk et al.) sous échangeabilité intra-mois ; les 18 features du cadrage sont à recouper avec la datasheet (une trentaine d'attributs, à ma connaissance) |
| R11 | Degrés de liberté du chercheur             | D, familles et seuils choisis après coup                                                                                                                                                                                       | hash de configuration gelé avant P3 ; période 2023–2025 intouchée jusqu'au gel                                                                                                                                                         |
| R12 | Références invérifiables                   | Drive vs. Decay et TAU-JEPA sans trace publique repérée                                                                                                                                                                        | versions arXiv avant mai 2027 ; à défaut, citation comme travaux non publiés                                                                                                                                                           |
| R13 | Paradoxe d'efficience                      | un Sharpe sans frictions élevé et persistant serait arbitré ; G0(b) échoue                                                                                                                                                     | contingence C1                                                                                                                                                                                                                         |
| R14 | Propriété intellectuelle, licences         | clauses CIFRE de LUSIS ; licence EUROFIDAI sans redistribution                                                                                                                                                                 | accord écrit avant tout dépôt public ; pipeline exécutable de bout en bout sur données S&P 500 publiques                                                                                                                               |
| R15 | Caractéristiques EUROFIDAI                 | fondamentaux point-in-time à confirmer, la base couvrant d'abord prix et événements                                                                                                                                            | canal caractéristiques limité à l'univers S&P 500 de CD-DFM si nécessaire ; EUROFIDAI réservé au test d'échelle en N                                                                                                                   |

- **C1 (échec de G0b).** Bascule vers les dérives de second ordre (rotations factorielles, déformations de $\Sigma_t$) et la tête paire. Un ratio de variance de 1,5 offre 24× le budget KL d'une dérive de SR = 1 (ADD oracle de 117 jours à ARL₀ = 252) ; un ratio de 2 en offre 77× (36 jours).
- **C2.** Domaines à fort rapport signal/bruit (BAF, SWaT/WADI), où l'Article B situe déjà le rendement de la calibration exacte.
- **C3 (échec de G2).** Article théorie, encodeur impair, audit et résultat JEPA négatif documenté (NeurIPS), ou version appliquée (ICAIF).
- **C4 (indisponibilité de José).** CA-T-JEPA minimal (≤ 1 M paramètres) développé côté surveillance, sans les garanties Drive vs. Decay.

## 4. Gouvernance et répartition avec José Lucas De Melo Costa

| Rôle CRediT       | Raphael                                                                              | José Lucas                                                   |
| ----------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| Conceptualization | lead : thèse, planchers, continuité avec l'Article B                                 | support : architecture, hypothèse de biais implicite         |
| Methodology       | lead : surveillance, calibration, protocole semi-synthétique, audit                  | lead : pré-entraînement, anti-collapsus, têtes impaire/paire |
| Formal analysis   | lead : Props 1–3, lemme, absorption                                                  | support : biais implicite JEPA (V1)                          |
| Software          | lead : `data_loader` finance, `injection`, `sequential_monitors`, `benchmark_runner` | lead : `jepa_pretrain`, `representation_extractor`           |
| Data curation     | EUROFIDAI, S&P 500, caractéristiques point-in-time                                   | BAF                                                          |
| Investigation     | expériences finance, in-the-wild                                                     | expériences BAF, ablations SSL (MAE, TAU-JEPA)               |
| Validation        | tests de contrat côté surveillance, reproductibilité bit à bit                       | collapsus, RankMe, transmission                              |
| Writing           | théorie, surveillance, finance ; relecture de tout                                   | représentation, BAF ; relecture de tout                      |

Contrat d'interface :

```text
data_loader      -> panel.parquet  (date, asset_id, ret:f32, in_universe:bool)   # R in R^{T x N}
                 -> chars.parquet  (date, asset_id, c_1..c_P)  # disponibles à l'ouverture de t
                 -> splits.yaml    pretrain [t0,t1) | calib [t1,t2) | monitor [t2,t3) | embargo >= L_ctx + 5
injection        -> panel_inj.parquet + tau_star.json   # dans l'espace des rendements, jamais dans z
jepa_pretrain    -> ckpt/<hash>/   poids gelés + config + hash des données d'entraînement
representation_extractor(ckpt, panel)
                 -> z_<hash>.npz   Z_odd in R^{T x D}, Z_even in R^{T x D'}, option Z_asset in R^{T x N x d}
                 + sidecar JSON    hashes (ckpt, données, splits), drapeaux impair/pair, stats de normalisation gelées
sequential_monitors(Z | panel, calib) -> alarms.csv    # numpy seul, aucun import torch
benchmark_runner -> results/<run_hash>.csv   # une ligne par réplication : seed, famille, D, ARL0, ADD, alarme
```

Règles de découplage :
1. Le module de surveillance n'importe jamais le code JEPA ; le module JEPA ne voit jamais injections ni alarmes.
2. Les injections traversent l'encodeur gelé, ce qui teste la transmission.
3. Quatre tests de contrat bloquent toute fusion : non-anticipation (perturber $x_{t+1:T}$ laisse $z_{1:t}$ identique bit à bit), imparité ($\|\phi(-x)+\phi(x)\|_\infty\le10^{-6}$ sur la tête impaire), déterminisme (deux exécutions, mêmes bits, BLAS mono-thread, inférence CPU), absence de statistiques de test.
4. Chaque figure lit un CSV, jamais un état en mémoire.

Raphael arbitre théorie et surveillance, José arbitre architecture et entraînement. Le protocole d'évaluation est co-signé et gelé avant P3 ; un point hebdomadaire de 30 minutes suit les jalons ; un fichier CODEOWNERS attribue chaque module. Je ne peux pas figurer comme auteur : les politiques de NeurIPS, d'ICML et de l'ACM excluent les LLM de l'autorat. Mes dérivations et mon code doivent être relus et assumés par un auteur humain, et l'usage déclaré selon la politique de la conférence.

## 5. Stratégie de publication

**Cible principale : NeurIPS 2027, main track.** L'échéance NeurIPS 2027, extrapolée du cycle 2026 en l'absence d'appel officiel, tombe autour du 21 mai 2027, résumés le 14 mai, mais l'article complet de NeurIPS 2026 était dû le 6 mai : le plan gèle donc le manuscrit le 30 avril. Cela laisse environ 30 semaines, assez pour P0–P4 et leurs jalons. La ligne éditoriale correspond au contenu : un résultat énoncé avec ses hypothèses et vérifié numériquement, une ablation qui isole la contribution de la représentation, un second domaine hors finance, un code exécutable sur données publiques. La communauté JEPA y siège, et José y a publié.

**Écartés.** ICML 2027 : la date projetée depuis le cycle 2026 est le 22 janvier 2027 pour l'article, le 16 janvier pour le résumé, soit 14,5 semaines, incompatibles avec G1 et G2. KDD 2027 : le cycle 1 est clos (résumés le 19 juillet, articles le 26 juillet 2026, notification le 14 novembre) et l'appel renvoie à une échéance de février 2027 pour le cycle 2, sans date précise. Si l'Article B est dans le cycle 1 et se voit refusé, sa resoumission naturelle est le cycle 2 : deux articles de la même équipe sur le même plancher dans le même vivier de reviewers. Février est en outre trop tôt pour G2.

**Repli.** ICLR 2028, réceptif aux travaux JEPA. L'échéance ICLR 2027 était le 24 septembre 2026 ; si 2027 suit le même calendrier, la fenêtre entre la notification NeurIPS et l'échéance ICLR sera serrée et devra être vérifiée dès la publication des dates.

**ICAIF 2027.** L'échéance tombe historiquement début août (à vérifier), pendant la revue NeurIPS : la double soumission l'exclut comme repli après NeurIPS. ICAIF est une alternative à décider au jalon G2 du 1er mars : si G1 passe et G2 échoue, la version appliquée (encodeur impair, facteurs CD-DFM, recensement EUROFIDAI) y trouve sa ligne éditoriale.

**Workshops NeurIPS.** En 2026, la date suggérée pour les contributions aux workshops était le 29 août. Un workshop non archivant reste compatible avec une soumission principale en cours, sous réserve de sa politique ; l'existence d'un workshop finance en 2027 ne se vérifiera qu'à la publication de la liste. Usage : visibilité, pas cible.

L'Article B doit être sur arXiv avant mai 2027 si la politique d'anonymat de KDD le permet. À défaut, l'Article C réénonce le plancher de façon autonome et cite l'Article B à la troisième personne.

## 6. Livrables du 12 au 25 octobre 2026

- **A1 — Note théorique v0** (LaTeX, anglais, environ 8 pages) : Propositions 1–3, lemme d'encodeur impair, critère d'absorption, preuves. Chaque énoncé est accompagné de la décision de design qu'il fixe et de la prédiction qui le réfuterait.
- **A2 — `floor_calculator.py` et validation Monte Carlo.** Le prototype de $M(D)$ est déjà validé à 4 % près ; extension au CUSUM pire cas de Lorden, aux priors mal accordés et à l'efficacité des capteurs de signe, avec CSV et figure ADD–D.
- **A3 — Notebook d'audit informationnel S&P 500** : spectre, η, corrélations de signe, test de symétrie centrale, SR de dérive débiaisé par transition Pagan-Sossounov dans trois sous-espaces (marché, K = 11 facteurs CD-DFM ou PCA, caractéristiques orthogonalisées), part des phases dans le budget. Dépendance : le panel de l'Article B ou l'univers des 239 titres de CD-DFM, avec leurs caractéristiques.
- **A4 — Squelette du dépôt**, `INTERFACE.md` et les quatre tests de contrat.
- **A5 — Pilote de l'échelle linéaire** sur fond S&P 500 symétrisé : B0, B1, B2, B3, familles F1–F3.

**Premier jalon empirique vérifiable, le 25 octobre : le test d'échappement.** Fond S&P 500 symétrisé, $N\in\{8,16,32,64,128,239\}$, dérive F2 d'amplitude calibrée pour que l'oracle détecte en environ un an à $N=239$. Trois critères falsifiables : FPR des flux de signe à ±1 point du nominal, l'exactitude étant garantie par construction, ce qui valide la chaîne ; ADD mesuré à ±15 % de la prédiction des Propositions 2–3 ; exposant $\hat\beta$ proche de 0 pour le pooling sur F3 et strictement positif, IC excluant 0, pour le PCA résiduel sur F2. Un échec sur le deuxième critère impose de réviser la théorie avant tout autre chantier.

**[Strategic Advice]**

- Livraison en Markdown dans le fil, sans Doc ni artefact, conformément à la préférence « aucun conteneur sans demande explicite ». Horodatage : seule la date est injectée, aucune heure.
- Angle mort principal : la valeur ajoutée propre du JEPA sur la localisation en finance est probablement faible. Une normalisation non apprise capte déjà 0,82 sur N1, et CD-DFM couvre une partie de N2. Les chances les plus sérieuses du JEPA se trouvent dans le tabulaire hétérogène (BAF) et les dérives de second ordre ; le plan garde les deux issues publiables pour cette raison.
- La Proposition 3 décrit le délai d'un détecteur à mélange accordé. Son statut de borne inférieure de second ordre, via la redondance de Clarke-Barron, reste à démontrer : ne pas l'énoncer comme borne dans le papier avant preuve.
- Les nombres produits ici sont reproductibles : $M(D)$ (analytique et Monte Carlo à 300 réplications), pénalité de dépassement sous GARCH (2 000 trajectoires), angles du dictionnaire, budgets de second ordre, critère d'absorption. Les scripts de travail rejoignent le dépôt avec A2. L'échelle d'efficacité (0,44 à 0,82) repose sur une volatilité log-normale avec s = 0,9 choisie pour l'illustration ; l'estimation de Phase 0 la remplacera.
- Hypothèses non vérifiées : Drive vs. Decay et TAU-JEPA (aucune trace publique repérée par mes recherches), le nombre de features de BAF, la disponibilité de caractéristiques point-in-time pour EUROFIDAI, le statut de l'Article B (supposé dans le cycle 1 de KDD 2027). Les dates NeurIPS et ICML 2027 sont des projections, pas des annonces.
- Si l'Article B est dans le cycle 1, son rebuttal passe avant A1–A5 : la période de rebuttal du cycle 1 de KDD 2027 court du 29 septembre au 13 octobre 2026.
- Branche écartée la plus coûteuse à rouvrir : TAU-JEPA comme chemin surveillé. Si José tient à ce socle, le cantonner au prétexte de pré-entraînement.Quatre points du cadrage actuel sont faux ou manquants ; une fois corrigés, la thèse tient.

1. **η ≈ 0,9 contredit les données du projet.** Sur les 239 titres S&P 500 de Lehalle & Alouadi, le facteur de marché explique R² = 0,36 de la variance. La corrélation de signe ρ̂ ≈ 0,26 de l'Article B correspond, par la relation gaussienne ρ_signe = (2/π)·arcsin ρ, à une corrélation de rendements de 0,40 : η ≈ 0,40. Avec γ = 0,5, la formule G = γ/(1−η) de `KL_PCA_PIVOT.md` donne G ≈ 0,8, soit une perte. Cette formule mesure un rapport signal/bruit par direction. Elle omet le terme de largeur (breadth), qui croît avec N et constitue la seule échappatoire non bornée.
2. **Un JEPA à masquage inter-actifs ne peut pas isoler le signal idiosyncratique.** Il apprend ce qui se prédit depuis les actifs de contexte, donc la structure systématique. La cible atteignable est la dérive orthogonale au mode de marché et pilotée par les caractéristiques, pas l'idiosyncratique au sens des modèles factoriels.
3. **Surveiller ‖z_target − ẑ‖² branche un capteur d'échelle sur une dérive de localisation.** La Proposition d'orthogonalité de l'Article B le cantonne au second ordre. Un résidu de prédiction est de plus aveugle à toute dérive cohérente que le prédicteur reproduit depuis le contexte.
4. **La taxe dimensionnelle manque.** Ignorer la direction de la dérive dans un sous-espace de dimension D multiplie l'ADD par 2,0 à D = 10 et par 3,9 à D = 64, à ARL₀ = 504 (formule analytique validée par Monte Carlo à 4 % près, §1.2). Un latent de 128 dimensions surveillé tel quel paie 5,2× avant toute considération de KL. Le gain d'un espace latent ne vient pas de la KL (DPI) ; il vient de la compression de la dimension de l'alternative composite.

Titre retenu : *JEPA-Drift: Escaping the Sharpe Ceiling of Sequential Drift Detection through Latent Information Concentration*. « Concentrating Kullback-Leibler Divergence » se lit comme une hausse de KL, qu'un reviewer familier de la DPI attaquera d'emblée. Si le jalon G2 échoue, l'article sort sous *Latent Information Floors: What Learned Representations Can and Cannot Buy for Sequential Drift Detection* ; le protocole garde les deux issues publiables.

## 1. Analyse critique et positionnement

### 1.1 Du linéaire au non linéaire sans violer la DPI

Notations. $x_t \in \mathbb{R}^N$ : rendements du jour $t$ ; $C_t \in \mathbb{R}^{N\times P}$ : caractéristiques prédéterminées ($\mathcal{F}_{t-1}$-mesurables) ; $\Sigma_t$ : covariance conditionnelle ; après la rupture en $\tau^*$, la moyenne conditionnelle se déplace de $\Delta\mu_t$. Pour une représentation $\phi$, $\mathcal{I}_\phi$ désigne le taux d'information de Kullback-Leibler par observation du processus $\phi(x_t;C_t)$ au sens de Lai (1998), et $\mathcal{I}_x$ celui des données brutes.

**Proposition 1 (hiérarchie informationnelle, alternatives de localisation locales).**
$$\tfrac12\,\overline{\Delta\mu}^{\top}\bar\Sigma^{-1}\overline{\Delta\mu}\;\le\;\tfrac12\,\mathbb{E}\!\left[\Delta\mu_t^{\top}\Sigma_t^{-1}\Delta\mu_t\right]\;\le\;\tfrac12\,\mathbb{E}\!\left[\Delta\mu_t^{\top}\mathcal{J}_t\,\Delta\mu_t\right]=\mathcal{I}_x,\qquad \mathcal{I}_\phi\le\mathcal{I}_x\ \ \forall\phi,$$
avec $\bar\Sigma=\mathbb{E}[\Sigma_t]$ et $\mathcal{J}_t$ l'information de Fisher conditionnelle de localisation. La première inégalité découle de la convexité jointe de $(a,S)\mapsto a^\top S^{-1}a$ (Jensen), la deuxième de $\mathcal{J}_t\succeq\Sigma_t^{-1}$ (Cramér-Rao, égalité ssi gaussien conditionnel), la dernière de la DPI. Le terme de gauche borne tout moniteur linéaire statique.

Un encodeur non linéaire ne crée pas d'information. Il récupère ce que la classe linéaire statique jette, par trois canaux, seules sources légitimes d'un gain JEPA :

- **(N1) Volatilité commune.** L'écart $\mathbb{E}[\sigma_t^2]\,\mathbb{E}[\sigma_t^{-2}]$ est le gain de Jensen que l'Article B n'atteignait qu'avec un oracle à paramètres GARCH connus par anticipation (×10,6 sur le krach de 2020). En univarié, $\sigma_t$ ne s'obtient que par un modèle ajusté sur le passé. Dans la coupe, la dispersion du jour le mesure sans modèle, avec une erreur relative en $O(N_{\text{eff}}^{-1/2})$, et une statistique homogène de degré 0, inaccessible à toute application linéaire non nulle, l'exploite en ligne.
- **(N2) Chargements variables pilotés par les caractéristiques** (IPCA, CD-DFM) : écart entre $(\overline{\Delta\mu},\bar\Sigma)$ et $(\Delta\mu_t,\Sigma_t)$.
- **(N3) Non-gaussianité résiduelle** : écart entre $\mathcal{J}_t$ et $\Sigma_t^{-1}$ une fois la volatilité retirée.

**Définition (concentration).** Pour une famille $\phi_D$ de dimension $D$, la rétention vaut $r_\phi(D)=\mathcal{I}_{\phi_D}/\mathcal{I}_x\in[0,1]$. La thèse s'énonce $\max_D r_{\text{JEPA}}(D)/M(D)>\max_D r_{\text{lin}}(D)/M(D)$, où $M$ est la taxe dimensionnelle de la Proposition 3. JEPA gagne en retenant plus d'information à faible dimension.

Le plafond du gain JEPA sur le meilleur modèle linéaire se mesure donc avant tout pré-entraînement. Pour le canal N1, sous volatilité commune log-normale ($s$ = écart-type de $\ln\sigma_t^2$, fixé à 0,9 pour l'illustration), l'efficacité relative au rapport de vraisemblance conditionnel s'ordonne ainsi :

| Moniteur sur une même projection $u$                          | Efficacité                          | Calibration                          |
| ------------------------------------------------------------- | ----------------------------------- | ------------------------------------ |
| CUSUM de moyenne, variance inconditionnelle                   | $e^{-s^2}=0{,}44$                   | faussée (§3.2)                       |
| CUSUM de signe, mise fixe (Article B)                         | $\tfrac{2}{\pi}e^{-s^2/4}=0{,}52$   | exacte                               |
| e-détecteur de signe, mise $\propto 1/\hat\sigma_{t\mid t-1}$ | $2/\pi=0{,}64$ (prévision parfaite) | exacte, quelle que soit $\hat\sigma$ |
| statistique auto-normalisée de degré 0 ($N\to\infty$)         | $e^{-s^2/4}=0{,}82$                 | pivot exact sous échelle commune     |
| RV conditionnel, $\sigma_t$ connu                             | $1$                                 | oracle                               |

Une normalisation transversale non apprise (dé-moyennage puis division par la dispersion du jour, soit une LayerNorm appliquée au vecteur de coupe) atteint déjà 0,82. Sur N1, il ne reste au JEPA qu'un facteur 1,22. Sans ce témoin, le gain attribué au JEPA risque d'être celui d'une couche de normalisation.

**Corrections de `KL_PCA_PIVOT.md`.**
- Le calcul du §4 suppose une variance résiduelle isotrope et compare des normes euclidiennes. L'objet correct est la norme de Mahalanobis résiduelle, qui porte un facteur d'ordre $N-1$ quand la dérive résiduelle est dispersée.
- « On jette $v_1$ » jette un canal d'information : $\Delta\mu^\top\Sigma^{-1}\Delta\mu=\sum_k(v_k^\top\Delta\mu)^2/\lambda_k$ est additif sur les directions propres. Le mode de marché se surveille à part (moniteur de l'Article B), et les deux flux se combinent par produit d'e-processes.
- $\alpha=0{,}05$ avec $\ln(1/\alpha)\approx3$ correspond à ARL₀ = 20 jours, une fausse alarme par mois : le point permissif du recensement de l'Article B. Au point opérationnel ARL₀ = 252, $\ln(1/\alpha_0)=5{,}53$, et détecter en 60 jours exige SR = 6,8 en univarié, pas 5,0.
- Le « paradoxe du hedge fund » n'est déplacé qu'à moitié. $\mathrm{SR}_x$ est exactement le Sharpe sans frictions du portefeuille tangent à la dérive ; un détecteur qui conclut en 60 jours certifie des Sharpe sans frictions d'environ 6,8 sur la durée du régime. L'échappatoire vaut dans la mesure où Sharpe sans frictions et Sharpe net divergent.

### 1.2 Plancher de délai dans l'espace latent

**Proposition 2 (plancher oracle).** Sous la condition de taux d'information de Lai (1998), à savoir la convergence r-rapide du log-rapport de vraisemblance normalisé vers $\mathcal{I}_z$, tout temps d'arrêt $T$ adapté à la filtration latente avec $\mathrm{ARL}_0(T)\ge1/\alpha_0$ vérifie, quand $\alpha_0\to0$ et sous modèle gaussien conditionnel :
$$\mathrm{ADD}_z\;\ge\;\frac{504\,\ln(1/\alpha_0)}{\mathrm{SR}_z^2}\bigl(1+o(1)\bigr),\qquad \mathrm{SR}_z^2:=252\,\mathbb{E}\!\left[\Delta\mu_{z,t}^{\top}\Sigma_{z,t}^{-1}\Delta\mu_{z,t}\right].$$
$\mathrm{SR}_z$ est le Sharpe annualisé du portefeuille tangent à la dérive dans l'espace latent, puisque $\max_w(w^\top\Delta\mu_z)^2/(w^\top\Sigma_zw)=\Delta\mu_z^\top\Sigma_z^{-1}\Delta\mu_z$ (Cauchy-Schwarz). Le plafond de Sharpe de l'Article B en est le cas $N=D=1$, et la DPI impose $\mathrm{SR}_z\le\mathrm{SR}_x$. À direction connue, $D=1$ suffit : $w^*=\Sigma^{-1}\Delta\mu$ atteint l'égalité. La dimension latente ne sert qu'à couvrir l'incertitude sur la direction.

**Structure factorielle.** Avec $x_t=B_tf_t+\varepsilon_t$, $\mathrm{Cov}(f_t)=\Sigma_F$, $\mathrm{Cov}(\varepsilon_t)=\Psi$ diagonale et $\Delta\mu=B\Delta\lambda+\Delta\alpha$, des facteurs pervasifs donnent, quand $N\to\infty$ :
$$\mathrm{SR}_x^2\;\to\;\underbrace{252\,\Delta\tilde\lambda^{\top}\Sigma_F^{-1}\Delta\tilde\lambda}_{\mathrm{SR}_F^2,\ \text{borné en }N}\;+\;\underbrace{252\,\Delta\alpha_\perp^{\top}\Psi^{-1}\Delta\alpha_\perp}_{\text{largeur},\ \propto N},$$
où $\Delta\alpha_\perp$ est le résidu GLS de $\Delta\alpha$ sur les chargements et $\Delta\tilde\lambda$ en absorbe la partie alignée. La saturation $K_{\text{eff}}\approx1/\hat\rho\approx3{,}8$ de l'Article B correspond à un seul facteur qui dérive : rapporté au Sharpe d'un titre isolé, le premier terme vaut $1/\rho$. Il n'existe que deux échappatoires. Soit plusieurs facteurs dérivent ensemble et le plateau monte à $\mathrm{SR}_F^2/\mathrm{SR}_1^2$, toujours borné ; soit une dérive idiosyncratique se disperse sur beaucoup de titres et le gain croît avec $N$. La table 6 de Lehalle & Alouadi plaide pour la première : sur leur fenêtre de crise (247 jours, une graine, à lire pour le signe selon les auteurs), les facteurs cash-neutral utilities, santé, consommation discrétionnaire, technologie et financières varient de +13 % à −16 %. À 8 % de volatilité annuelle, hypothèse à mesurer, chacun porterait un SR de dérive de 1 à 2.

**Proposition 3 (alternative composite).** Pour une dérive de direction inconnue dans un sous-espace de dimension $D_{\text{eff}}$, le détecteur à mélange gaussien isotrope accordé à l'amplitude (méthode des mélanges de Robbins ; GLR de Siegmund & Venkatraman, 1995) atteint
$$\mathrm{ADD}_z\approx\frac{504\,\ln(1/\alpha_0)}{\mathrm{SR}_z^2}\,M(D_{\text{eff}},\alpha_0),\qquad M=\frac{x}{\ln(1/\alpha_0)},\quad x=\ln\frac{1}{\alpha_0}+\frac{D_{\text{eff}}}{2}\ln\!\Bigl(1+\frac{2x}{D_{\text{eff}}}\Bigr).$$
Le terme $\frac D2\ln(\cdot)$ est la redondance minimax d'une famille à $D$ paramètres (Rissanen ; Clarke & Barron, 1990). Quand $\alpha_0\to0$, il devient d'ordre $\frac D2\ln\ln(1/\alpha_0)$ et négligeable. Aux ARL₀ opérationnels, il domine dès $D\approx10$ ; pour $D\gg\ln(1/\alpha_0)$, $x\approx\sqrt{D\ln(1/\alpha_0)}$.

| $D_{\text{eff}}$        | 1    | 5    | 10   | 20   | 64   | 128  | 500  |
| ----------------------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| $M$, ARL₀ = 252         | 1,24 | 1,71 | 2,08 | 2,62 | 4,10 | 5,50 | 10,2 |
| $M$, ARL₀ = 504         | 1,22 | 1,66 | 2,01 | 2,51 | 3,91 | 5,23 | 9,64 |
| Monte Carlo, ARL₀ = 504 | 1,27 | 1,63 | 2,06 | —    | 3,83 | —    | 9,82 |

Monte Carlo : 300 réplications (150 à $D=500$) ; l'oracle à direction connue donne $M\in[0{,}95;1{,}04]$. Trois conséquences de design en découlent. Le latent surveillé a $D_{\text{eff}}\le10$–16, et un JEPA de dimension 128 ne se surveille qu'à travers une tête de lecture compressée. Un dictionnaire de $M$ directions économiques (facteurs CD-DFM, secteurs, styles) coûte $\ln M$ au lieu de $\frac D2\ln(\cdot)$ mais perd $\cos^2\theta$, où $\theta$ est l'angle entre la dérive blanchie et l'atome le plus proche : à ARL₀ = 504, vingt atomes battent le mélange continu de dimension 10 si $\theta<22°$, de dimension 64 si $\theta<48°$, et jamais celui de dimension 5. Enfin, la loi d'échelle en $N$ devient la signature falsifiable de l'article : $G\propto N^0$ (pooling, dérive de marché, Article B), $G\propto N^{1/2}$ (coupe entière non structurée, la taxe en $\sqrt N$ absorbant la moitié de l'exposant), $G\propto N$ (dérive de largeur pilotée par $P$ caractéristiques, latent structuré de dimension fixe).

**Niveau du moniteur et décomposition du gain.** $\mathrm{ADD}_{\text{mon}}\approx(\Gamma_z^{\text{op}}/e_m)\,\mathrm{ADD}_z$, où $e_m$ vient de la table d'efficacité et $\Gamma_z^{\text{op}}$ est la pénalité de calibration opérationnelle définie au §3.2. Le gain sur l'univarié se factorise :
$$G=\frac{\mathrm{ADD}_{\text{univ}}}{\mathrm{ADD}_{\text{lat}}}=\underbrace{\frac{\mathrm{SR}_z^2}{\mathrm{SR}_1^2}}_{\text{concentration}}\times\underbrace{\frac{M(1)}{M(D_{\text{eff}})}}_{\text{taxe}}\times\underbrace{\frac{e_z\,\Gamma_1^{\text{op}}}{e_1\,\Gamma_z^{\text{op}}}}_{\text{blanchiment}}.$$
Ordre de grandeur : détecter en 252 jours au plus à ARL₀ = 504 exige $\mathrm{SR}_z\ge3{,}53$ (oracle), 4,54 ($D_{\text{eff}}=5$), 5,00 ($D_{\text{eff}}=10$), 6,97 ($D_{\text{eff}}=64$). Ces seuils fixent ce que l'audit de Phase 0 doit trouver dans les données.

### 1.3 Verrous théoriques immédiats

**V1 — Aveuglement jacobien.** Pour une petite dérive, $\Delta\mu_z\approx\mathbb{E}[J_\phi]\,\Delta\mu$ : toute composante dans le noyau de $J_\phi$ disparaît. Dans les réseaux linéaires profonds, le biais implicite des JEPA privilégie les directions prédictives sur les directions de forte variance, à l'inverse de MAE (Littwin et al., NeurIPS 2024). C'est l'argument théorique de JEPA contre PCA pour les directions peu variables mais structurées, et la raison pour laquelle les dérives non prédictibles depuis le contexte sont perdues. Instrument : le rapport de transmission $T(u)=\|\Sigma_z^{-1/2}\mathbb{E}[J_\phi]u\|^2/\|\Sigma^{-1/2}u\|^2$, calculé par différences finies sur les directions injectées ; $T>1$ n'est possible que par les canaux N1–N3. Prédiction testable : à $D$ égal, $T_{\text{JEPA}}>T_{\text{MAE}}$ sur les directions de faible variance.

**V2 — Validité de $H_0$ dans le latent.**

*Lemme (blanchiment par encodeur impair).* Soit $\phi(\cdot\,;C)$ impaire en $x$, $\phi(-x;C)=-\phi(x;C)$, avec $C_t$ et une direction $u_t$ $\mathcal{F}_{t-1}$-mesurables. Si, sous $H_0$, la loi de $x_t$ sachant $\mathcal{F}_{t-1}$ est centralement symétrique et $\mathbb{P}(u_t^\top\phi(x_t;C_t)=0\mid\mathcal{F}_{t-1})=0$, alors $b_t=\mathbf 1\{u_t^\top\phi(x_t;C_t)>0\}$ est i.i.d. Bernoulli(1/2), quelles que soient les dynamiques de volatilité, de corrélation et de queues.

*Preuve.* $g=u_t^\top\phi(\cdot\,;C_t)$ est impaire conditionnellement à $\mathcal{F}_{t-1}$ ; la symétrie donne $\mathbb{P}(g(x_t)>0\mid\mathcal{F}_{t-1})=\mathbb{P}(g(x_t)<0\mid\mathcal{F}_{t-1})=1/2$, et une suite de bits de loi conditionnelle constante 1/2 est i.i.d. ∎

Le lemme étend la propriété de blanchiment de l'Article B du signe d'un rendement au signe d'une projection impaire de toute la coupe. Il fournit aussi la version latente de la Proposition d'orthogonalité. Avec $\phi_{\text{imp/pair}}(x)=\tfrac12[\phi(x)\mp\phi(-x)]$, toute statistique impaire est exactement aveugle à un changement qui préserve la symétrie centrale (volatilité, corrélation, queues), et toute statistique paire ne voit une translation qu'au second ordre. Le JEPA reçoit donc deux têtes : impaire pour le pipeline Concept latent (capteur de signe), paire pour le pipeline Data latent (capteur énergétique recalibré). Si $\phi$ est en outre homogène de degré 0, la statistique entière, pas seulement son signe, a une loi nulle libre de l'échelle commune.

Trois limites s'appliquent. Les égalités (rendements nuls, valeurs manquantes imputées à zéro sur les petites capitalisations) se tranchent par tirage aléatoire, ce qui préserve l'exactitude. L'asymétrie de dépendance de queue (Longin & Solnik, 2001 ; Ang & Chen, 2002) viole la symétrie centrale et impose un recentrage sur un taux $\hat q_u$ estimé, comme pour l'asymétrie dans l'Article B. La prime de risque déplace la médiane, moins dans les directions cash-neutral que sur l'indice (SPY : de 0,541 à 0,554 de jours haussiers sur 2011–2018 dans l'Article B).

**V3 — Agrégation.** Le flux poolé de l'Article B perd sa blancheur au-delà de K = 10, parce que la variance conditionnelle d'une somme de signes suit la corrélation transversale du jour. Le lemme ne couvre qu'un signe par direction. Plusieurs directions se combinent par mélange d'e-processes : une moyenne de martingales de test sous la même filtration reste une martingale de test, quelle que soit la dépendance entre directions. Ni Bonferroni ni bootstrap.

**V4 — Taxe dimensionnelle.** $D_{\text{eff}}\le10$–16, ou priors structurés (dictionnaire, parcimonie), par la Proposition 3.

**V5 — Non-anticipation.** Encodeur pré-entraîné strictement avant la fenêtre surveillée ; caractéristiques datées à leur publication, les fondamentaux trimestriels arrivant avec plusieurs semaines de retard ; statistiques de normalisation gelées ; embargo d'au moins la longueur de contexte plus 5 jours.

## 2. Orchestration et jalons

### 2.1 Phases

| Phase                                       | Fenêtre                 | Contenu                                                                                                                   | Livrable                                 | Jalon         |
| ------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------------- |
| P0 — Théorie et audit                       | 12 oct. – 8 nov. 2026   | Props 1–3, lemme, critère d'absorption ; validation Monte Carlo ; audit S&P 500                                           | note théorique v1, notebook d'audit, CSV | G0, 9 nov.    |
| P1 — Pile de surveillance, échelle linéaire | 26 oct. – 13 déc.       | moniteurs (signe, e-détecteurs, degré 0) ; fonds symétrisés S&P 500 et EUROFIDAI ; familles F1–F4 ; échelle B0–B5         | `benchmark_runner`, courbes ADD–ARL₀     | G1, 14 déc.   |
| P2 — Représentations (José, en parallèle)   | 26 oct. – 17 janv. 2027 | CA-T-JEPA à têtes impaire/paire ; T-JEPA sur BAF ; diagnostics anti-collapsus                                             | checkpoints conformes au contrat         | G2a, 18 janv. |
| P3 — Confrontation, attribution             | 4 janv. – 28 févr.      | JEPA contre l'échelle linéaire ; ablations (normalisation seule, MAE, TAU-JEPA, balayage de D) ; spectres de transmission | tableaux principaux                      | G2, 1er mars  |
| P4 — In-the-wild, BAF, rédaction            | 1er mars – 30 avr.      | régimes datés ; dérive mensuelle BAF ; rapport anytime-valid ; relecture interne mi-avril                                 | manuscrit gelé le 30 avril               | soumission    |

Échelle de référence : B0, indice univarié (signe, Article B) ; B1, pooling équipondéré ; B2, PCA résiduel ; B3, normalisation transversale de degré 0 et rangs transversaux centrés (impairs, invariants d'échelle et de translation) ; B4, facteurs cash-neutral CD-DFM et IPCA ; B5, oracle à direction connue. Les familles de dérive injectées sont calibrées sur les transitions historiques (vecteurs $\Delta\hat\mu$ rétrécis) : F1, primes factorielles $B_t\Delta\lambda$ (plateau attendu) ; F2, largeur $(C_t\Delta\gamma)_\perp$ (croissance attendue en $N$) ; F3, mode de marché (témoin qui doit reproduire la saturation de l'Article B) ; F4, rotation factorielle ou déformation de $\Sigma_t$ (tête paire).

### 2.2 Jalons Go/No-Go

- **G0 (9 nov.)** — (a) Les ADD simulés reproduisent les Propositions 2–3 à ±10 % sur fond gaussien et sur fond GARCH symétrisé. (b) L'audit place le plancher oracle transversal sous la durée d'au moins 25 % des phases datées à ARL₀ = 252, contre 2 sur 66 (3 %) en univarié dans l'Article B. Échec de (b) : contingence C1 ou C2 (§3.4), car par la DPI aucun encodeur ne fera mieux que l'oracle.
- **G1 (14 déc.)** — Le meilleur moniteur de l'échelle linéaire tient sa FPR à ±15 % du nominal sur fonds nuls symétrisés ; les flux de signe étant exacts par construction, cela teste la pile elle-même. Il atteint G ≥ 4 contre l'univarié composite sur événements appariés, et l'exposant d'échappement $\hat\beta$ (pente de $\log G$ en $\log N$) est positif sur F2 avec un IC à 95 % qui exclut 0. Si G0 passe et G1 échoue, l'information existe mais la surveillance la perd : on corrige la pile, pas l'encodeur.
- **G2a (18 janv.)** — Rang effectif RankMe de la tête de lecture ≥ 0,5·D ; $T_{\text{JEPA}}(u)\ge T_{\text{PCA}}(u)$ sur au moins la moitié des directions injectées ; aucun collapsus selon les critères Drive vs. Decay.
- **G2 (1er mars)** — Le JEPA bat le meilleur de B3 et B4 d'un facteur ≥ 1,25 en ADD à ARL₀ égal, sur au moins deux des familles F1, F2, F4, avec un IC à 95 % qui exclut 1 et $D^*\le16$. Échec : titre de repli, résultat JEPA négatif ou conditionnel documenté.

### 2.3 Seuils minimaux pour valider la thèse

**Contre le plafond de Sharpe univarié : G ≥ 4**, composite contre composite ($M(1)$ des deux côtés), sur événements appariés. Un facteur 4 divise par deux le SR requis ; en deçà, la part des régimes datés qui entre dans le budget bouge à peine (64 phases sur 66 hors budget à ARL₀ = 252 dans l'Article B). Le critère lisible par un reviewer reste la part des phases dans le budget, avec une cible de 25 %.

**Contre la saturation transversale : borne inférieure de l'IC de G au-dessus de 3,8**, et non de 2. Le pooling de l'Article B réalise 2× pour un plafond théorique de 3,8, et battre le réalisé ne prouve rien. Une valeur ponctuelle de G ne démontre pas l'échappement ; une pente $\hat\beta>0$ au-delà de $N\approx20$, si.

**Contre le benchmark PCA-orthogonal : ≥ 1,25× (−20 % d'ADD) face au meilleur concurrent linéaire ou non appris (B3, B4).** Passer de $D=5$ à $D=10$ change déjà $M$ de 1,21×, si bien qu'un gain inférieur relève du réglage, pas de la représentation. La normalisation non apprise prend 0,82 sur N1 et laisse au JEPA 1,22× sur ce canal, plus ce que N2 et N3 apporteront, inconnu avant l'audit.

### 2.4 Séquence technique

Le benchmark PCA résiduel passe d'abord côté surveillance ; le pré-entraînement JEPA démarre en parallèle le 26 octobre côté représentation. Trois raisons imposent l'ordre côté surveillance. Un ADD JEPA médiocre reste ininterprétable sans pile calibrée, car il faut savoir si l'information manque (G0), si la calibration fuit (G1) ou si l'encodeur perd la direction (G2a). L'audit et l'échelle linéaire peuvent arrêter ou réorienter le projet avant toute dépense JEPA. L'échelle linéaire fixe enfin le contrat d'interface, des tableaux $Z$, dans lequel le JEPA se branche.

Le parallélisme tient au calendrier. En séquentiel strict, P3 commencerait en mars et laisserait huit semaines à P4. Chemin critique : contrats de données → pile de surveillance → G1 → confrontation → G2 → rédaction.

### 2.5 Arbitrages structurants

| Décision             | Retenu                                                                                                                              | Écarté                                   | Motif de clôture                                                                                                                                                       |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ordre                | linéaire d'abord (surveillance), JEPA en parallèle                                                                                  | JEPA d'abord ; séquentiel strict         | ininterprétable sans pile calibrée ; chemin critique trop long                                                                                                         |
| Architecture finance | CA-T-JEPA : actifs comme jetons, conditionné par $C_t$, équivariant par permutation, têtes impaire/paire, chemin surveillé par jour | TAU-JEPA comme socle du chemin surveillé | fenêtres chevauchantes (Γ_z ≈ L) ; normalisation d'instance temporelle (absorption) ; échantillon T au lieu de N·T. TAU-JEPA reste en ablation comme prétexte temporel |
| Capteur              | signe de projection impaire, e-détecteurs, statistique de degré 0                                                                   | ‖z − ẑ‖²                                 | capteur d'échelle, aveugle aux dérives cohérentes, Γ_z > 1                                                                                                             |
| Calibration finance  | signe exact ; randomisation par inversion de signe pour les statistiques à amplitude                                                | permutation                              | l'échangeabilité échoue sous GARCH                                                                                                                                     |
| Statut de l'encodeur | gelé, rafraîchissement programmé                                                                                                    | adaptatif en ligne                       | critère d'absorption (§3.1)                                                                                                                                            |
| Baseline             | échelle B0–B5 avec CD-DFM, IPCA et normalisation transversale                                                                       | PCA statique seule                       | épouvantail qu'un reviewer relèvera                                                                                                                                    |
| Conférence           | NeurIPS 2027                                                                                                                        | ICML 2027 ; KDD 2027 cycle 2             | calendrier ; chevauchement avec l'Article B (§5)                                                                                                                       |

Un résultat récent montre ce que coûte le capteur écarté : avec un encodeur V-JEPA 2 gelé, le score d'erreur de prédiction atteint 0,89 d'AP sur un banc inter-jeux de données mais 0,29, proche du hasard, sur un banc équitable intra-nuScenes, alors qu'une sonde supervisée retrouve le signal dans les embeddings gelés. Le score de densité implicite des JEPA relève de la tête paire : le terme anti-collapsus d'un JEPA estime implicitement la densité des données, extractible sous le nom de JEPA-SCORE, ce qui en fait un capteur de nouveauté, pas de localisation.

## 3. Arbre des risques et contingences

### 3.1 (i) Absorption selon le statut de l'encodeur

Un encodeur adaptatif de constante de temps $\tau_a$ fait décroître la dérive latente, $\Delta\mu_z(s)=\Delta\mu_z(0)\,e^{-s/\tau_a}$, et l'information cumulée plafonne à $\mathcal{I}_z\tau_a/2$. Le critère de détectabilité et le délai qui en résulte sont :
$$\tau_a>2\,\mathrm{ADD}_{\text{or}},\qquad \mathrm{ADD}=-\frac{\tau_a}{2}\ln\!\Bigl(1-\frac{2\,\mathrm{ADD}_{\text{or}}}{\tau_a}\Bigr),\qquad \mathrm{ADD}_{\text{or}}=\frac{\ln(1/\alpha_0)}{\mathcal{I}_z}.$$
Pour $\tau_a$ = 2,5, 4 et 8 fois $\mathrm{ADD}_{\text{or}}$, le délai vaut 2,01, 1,39 et 1,15 fois l'oracle ; à $\tau_a\le2\,\mathrm{ADD}_{\text{or}}$, la dérive n'est jamais détectée. Comme $\mathrm{ADD}_{\text{or}}$ se compte en centaines de jours pour une dérive de localisation, un encodeur en ligne doit garder plusieurs années de mémoire : il est gelé de fait. C'est la « starvation » que tu as caractérisée entre ensembles adaptatifs (ARF, SRP) et détecteurs externes, transposée à l'encodeur. L'encodeur gelé, lui, n'absorbe rien mais vieillit : l'évolution lente des corrélations et des distributions de caractéristiques déplace la loi nulle latente et produit le pendant « flooding », celui que tu as observé sur tous les flux réels.

L'absorption se cache aussi hors de l'apprentissage : BatchNorm laissée en mode entraînement à l'inférence ; normalisation d'instance temporelle de type RevIN, standard dans PatchTST, qui retire la moyenne de la fenêtre et efface une translation après L jours ; mise à jour EMA du target encoder si l'entraînement continue pendant la surveillance.

Protocole :
1. Référence gelée $\phi_{\text{ref}}$ pré-entraînée sur $[t_0,t_1)$, rafraîchie à des intervalles $T_{\text{ref}}\ge4\,\mathrm{ADD}_{\text{cible}}$ sur une fenêtre qui exclut les $\mathrm{ADD}_{\text{cible}}$ derniers jours.
2. Après alarme confirmée, ré-ancrage : réentraînement sur le nouveau régime avant reprise de la surveillance.
3. Test de contrat : en mode `eval`, aucun buffer ne change ; aucune normalisation calculée sur l'axe temporel dans le chemin surveillé.
4. Vieillissement mesuré : ARL₀ réalisé par tranche annuelle depuis le pré-entraînement, sur fond symétrisé.

### 3.2 (ii) Calibration sous hétéroscédasticité latente

Γ_z a trois sources distinctes dans le latent.

- **Chevauchement temporel.** Un encodeur à fenêtre de L jours produit des latents autocorrélés ; pour une moyenne glissante uniforme, $\Gamma_z^{\text{spec}}=1+2\sum_{k<L}(1-k/L)=L$. Un encodeur temporel à fenêtre de 60 jours inflige Γ_z ≈ 60 à une statistique de premier ordre sans aucun GARCH.
- **Agrégats quadratiques.** ‖z‖² et ‖z − ẑ‖² héritent du clustering de volatilité ($\hat\Gamma\in[2{,}6;15{,}0]$ sur les ETF de l'Article B).
- **Pénalité de dépassement des statistiques de premier ordre**, absente de la définition spectrale de l'Article B. Des rendements non autocorrélés ont $\Gamma^{\text{spec}}=1$, et pourtant un CUSUM de premier ordre calibré en i.i.d. perd sa calibration sous GARCH dès que le seuil est profond. Vérification sur GARCH(0,08 ; 0,90) à innovations gaussiennes, 2 000 trajectoires : à δ = 0,5 et λ = 6, l'ARL₀ passe de 2 587 (i.i.d.) à 889, soit ÷2,9 ; à δ = 1 et λ = 3, de 1 894 à 669. À seuil peu profond (ARL₀ ≈ 190), l'erreur s'inverse (+17 %, côté conservateur). Le CUSUM de signe reste exact (213 contre 214). La pénalité croît avec ARL₀, donc dans la zone opérationnelle : c'est une Lethargy Tax que le facteur spectral ne voit pas.

Protocole :
1. Chemin surveillé par jour, sans fenêtre chevauchante, ou par blocs disjoints au prix d'un retard d'au plus L.
2. Premier ordre : signe de projection impaire (exact), ou e-détecteur par paris avec mises prévisibles $\lambda_t\propto1/\hat\sigma_{t\mid t-1}$, $\hat\sigma$ étant tiré de la dispersion transversale passée. Le modèle de volatilité n'entre que dans la mise, donc dans la puissance, jamais dans la validité (inégalité de Ville).
3. Statistiques à amplitude : calibration par randomisation d'inversion de signe, $x_t\mapsto\epsilon_tx_t$ avec $\epsilon_t$ de Rademacher appliqué à toute la coupe du jour ; exacte sous symétrie conditionnelle sans effet de levier, approchée sinon.
4. Fonds symétrisés : la même transformation appliquée au fond réel conserve $|x_t|$, donc clustering et corrélations, et détruit toute dérive de localisation. Chaque tirage fournit une trajectoire nulle avec la vraie hétéroscédasticité, et l'estimation de l'ARL₀ cesse de dépendre des quelques fausses alarmes que 25 ans de données autorisent. La symétrisation détruit l'effet de levier : un bras placebo sur fond brut (Δ = 0) reste obligatoire, comme dans l'Article B.
5. Mesure : $\Gamma_z^{\text{op}}:=\lambda_{\text{requis}}/\lambda_{\text{iid}}$ à ARL₀ fixé, pour chaque moniteur, sur fonds symétrisés.

### 3.3 (iii) Dimension latente et perte géométrique

La Proposition 3 rend l'ADD en U en fonction de D : la rétention $r(D)$ croît puis sature, la taxe croît en $\sqrt D$. Passer de D = 5 à 10 doit augmenter la rétention de plus de 21 % ; de 20 à 64, de plus de 56 %. L'effondrement spectral partiel des représentations auto-supervisées (Jing et al., ICLR 2022) frappe d'abord les petites valeurs propres, précisément celles où une dérive isotrope porte le plus de KL, puisque la contribution de la direction $k$ vaut $(v_k^\top\Delta\mu)^2/\lambda_k$. Le blanchiment estimé ajoute un biais : une Mahalanobis calculée avec $\hat\Sigma_z^{-1}$ sur $n$ points est gonflée d'un facteur proche de $n/(n-D-1)$ (moyenne de la Wishart inverse), soit +15 % à $n=500$ et $D=64$, ce qui se paie en fausses alarmes.

Protocole : balayage de la tête de lecture $D\in\{2,4,8,16,32\}$ sur un tronc JEPA fixe ; $D^*$ choisi sur la seule fenêtre de calibration ; retrait de Ledoit-Wolf, ou capteurs de signe qui n'inversent aucune matrice ; RankMe rapporté pour chaque $D$ ; spectres de transmission $T(u)$ sur une base fixée a priori (vecteurs propres, facteurs CD-DFM, directions de caractéristiques).

### 3.4 Registre complémentaire et contingences

| #   | Risque                                     | Mécanisme ou signal                                                                                                                                                                                                            | Contournement                                                                                                                                                                                                                          |
| --- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R4  | Comparaison univarié/transversal mal posée | événements différents comparés                                                                                                                                                                                                 | événements appariés : chaque dérive injectée, calibrée sur une transition historique, est mesurée sur l'indice et sur la coupe                                                                                                         |
| R5  | Survivant, look-ahead                      | panel de 97 survivants dans l'Article B ; fondamentaux publiés en retard                                                                                                                                                       | constituants point-in-time (EUROFIDAI) ; fondamentaux datés à leur publication                                                                                                                                                         |
| R6  | Gain de normalisation attribué au JEPA     | LayerNorm transversale = dé-moyennage + degré 0                                                                                                                                                                                | B3 obligatoire dans tout tableau principal                                                                                                                                                                                             |
| R7  | Échantillon SSL en finance                 | T ≈ 6 300 jours ; JEPA ≈ PCA par sur-apprentissage                                                                                                                                                                             | poids partagés entre actifs (1,5–3 M actif-jours) ; modèles ≤ 5 M paramètres                                                                                                                                                           |
| R8  | Audit bruité                               | biais de bruit $252N(1/n_1+1/n_2)\approx482$ en SR² pour N = 239 et deux phases de 250 jours                                                                                                                                   | projections de dimension ≤ 30, débiaisées, poolées sur les transitions, IC bootstrap                                                                                                                                                   |
| R9  | Peu de phases in-the-wild                  | 15 à 25 phases par marché sur 2000–2025                                                                                                                                                                                        | US, Europe et datation sectorielle ; présenté en appui, pas en preuve principale                                                                                                                                                       |
| R10 | BAF synthétique                            | BAF a été produit en appliquant des techniques de génération tabulaire à un jeu réel anonymisé de fraude à l'ouverture de compte : des demandes d'ouverture, pas des transactions ; huit mois, donc sept frontières mensuelles | formulation « dérive synthétique réaliste » ; martingales de test conformes (Vovk et al.) sous échangeabilité intra-mois ; les 18 features du cadrage sont à recouper avec la datasheet (une trentaine d'attributs, à ma connaissance) |
| R11 | Degrés de liberté du chercheur             | D, familles et seuils choisis après coup                                                                                                                                                                                       | hash de configuration gelé avant P3 ; période 2023–2025 intouchée jusqu'au gel                                                                                                                                                         |
| R12 | Références invérifiables                   | Drive vs. Decay et TAU-JEPA sans trace publique repérée                                                                                                                                                                        | versions arXiv avant mai 2027 ; à défaut, citation comme travaux non publiés                                                                                                                                                           |
| R13 | Paradoxe d'efficience                      | un Sharpe sans frictions élevé et persistant serait arbitré ; G0(b) échoue                                                                                                                                                     | contingence C1                                                                                                                                                                                                                         |
| R14 | Propriété intellectuelle, licences         | clauses CIFRE de LUSIS ; licence EUROFIDAI sans redistribution                                                                                                                                                                 | accord écrit avant tout dépôt public ; pipeline exécutable de bout en bout sur données S&P 500 publiques                                                                                                                               |
| R15 | Caractéristiques EUROFIDAI                 | fondamentaux point-in-time à confirmer, la base couvrant d'abord prix et événements                                                                                                                                            | canal caractéristiques limité à l'univers S&P 500 de CD-DFM si nécessaire ; EUROFIDAI réservé au test d'échelle en N                                                                                                                   |

- **C1 (échec de G0b).** Bascule vers les dérives de second ordre (rotations factorielles, déformations de $\Sigma_t$) et la tête paire. Un ratio de variance de 1,5 offre 24× le budget KL d'une dérive de SR = 1 (ADD oracle de 117 jours à ARL₀ = 252) ; un ratio de 2 en offre 77× (36 jours).
- **C2.** Domaines à fort rapport signal/bruit (BAF, SWaT/WADI), où l'Article B situe déjà le rendement de la calibration exacte.
- **C3 (échec de G2).** Article théorie, encodeur impair, audit et résultat JEPA négatif documenté (NeurIPS), ou version appliquée (ICAIF).
- **C4 (indisponibilité de José).** CA-T-JEPA minimal (≤ 1 M paramètres) développé côté surveillance, sans les garanties Drive vs. Decay.

## 4. Gouvernance et répartition avec José Lucas De Melo Costa

| Rôle CRediT       | Raphael                                                                              | José Lucas                                                   |
| ----------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| Conceptualization | lead : thèse, planchers, continuité avec l'Article B                                 | support : architecture, hypothèse de biais implicite         |
| Methodology       | lead : surveillance, calibration, protocole semi-synthétique, audit                  | lead : pré-entraînement, anti-collapsus, têtes impaire/paire |
| Formal analysis   | lead : Props 1–3, lemme, absorption                                                  | support : biais implicite JEPA (V1)                          |
| Software          | lead : `data_loader` finance, `injection`, `sequential_monitors`, `benchmark_runner` | lead : `jepa_pretrain`, `representation_extractor`           |
| Data curation     | EUROFIDAI, S&P 500, caractéristiques point-in-time                                   | BAF                                                          |
| Investigation     | expériences finance, in-the-wild                                                     | expériences BAF, ablations SSL (MAE, TAU-JEPA)               |
| Validation        | tests de contrat côté surveillance, reproductibilité bit à bit                       | collapsus, RankMe, transmission                              |
| Writing           | théorie, surveillance, finance ; relecture de tout                                   | représentation, BAF ; relecture de tout                      |

Contrat d'interface :

```text
data_loader      -> panel.parquet  (date, asset_id, ret:f32, in_universe:bool)   # R in R^{T x N}
                 -> chars.parquet  (date, asset_id, c_1..c_P)  # disponibles à l'ouverture de t
                 -> splits.yaml    pretrain [t0,t1) | calib [t1,t2) | monitor [t2,t3) | embargo >= L_ctx + 5
injection        -> panel_inj.parquet + tau_star.json   # dans l'espace des rendements, jamais dans z
jepa_pretrain    -> ckpt/<hash>/   poids gelés + config + hash des données d'entraînement
representation_extractor(ckpt, panel)
                 -> z_<hash>.npz   Z_odd in R^{T x D}, Z_even in R^{T x D'}, option Z_asset in R^{T x N x d}
                 + sidecar JSON    hashes (ckpt, données, splits), drapeaux impair/pair, stats de normalisation gelées
sequential_monitors(Z | panel, calib) -> alarms.csv    # numpy seul, aucun import torch
benchmark_runner -> results/<run_hash>.csv   # une ligne par réplication : seed, famille, D, ARL0, ADD, alarme
```

Règles de découplage :
1. Le module de surveillance n'importe jamais le code JEPA ; le module JEPA ne voit jamais injections ni alarmes.
2. Les injections traversent l'encodeur gelé, ce qui teste la transmission.
3. Quatre tests de contrat bloquent toute fusion : non-anticipation (perturber $x_{t+1:T}$ laisse $z_{1:t}$ identique bit à bit), imparité ($\|\phi(-x)+\phi(x)\|_\infty\le10^{-6}$ sur la tête impaire), déterminisme (deux exécutions, mêmes bits, BLAS mono-thread, inférence CPU), absence de statistiques de test.
4. Chaque figure lit un CSV, jamais un état en mémoire.

Raphael arbitre théorie et surveillance, José arbitre architecture et entraînement. Le protocole d'évaluation est co-signé et gelé avant P3 ; un point hebdomadaire de 30 minutes suit les jalons ; un fichier CODEOWNERS attribue chaque module. Je ne peux pas figurer comme auteur : les politiques de NeurIPS, d'ICML et de l'ACM excluent les LLM de l'autorat. Mes dérivations et mon code doivent être relus et assumés par un auteur humain, et l'usage déclaré selon la politique de la conférence.

## 5. Stratégie de publication

**Cible principale : NeurIPS 2027, main track.** L'échéance NeurIPS 2027, extrapolée du cycle 2026 en l'absence d'appel officiel, tombe autour du 21 mai 2027, résumés le 14 mai, mais l'article complet de NeurIPS 2026 était dû le 6 mai : le plan gèle donc le manuscrit le 30 avril. Cela laisse environ 30 semaines, assez pour P0–P4 et leurs jalons. La ligne éditoriale correspond au contenu : un résultat énoncé avec ses hypothèses et vérifié numériquement, une ablation qui isole la contribution de la représentation, un second domaine hors finance, un code exécutable sur données publiques. La communauté JEPA y siège, et José y a publié.

**Écartés.** ICML 2027 : la date projetée depuis le cycle 2026 est le 22 janvier 2027 pour l'article, le 16 janvier pour le résumé, soit 14,5 semaines, incompatibles avec G1 et G2. KDD 2027 : le cycle 1 est clos (résumés le 19 juillet, articles le 26 juillet 2026, notification le 14 novembre) et l'appel renvoie à une échéance de février 2027 pour le cycle 2, sans date précise. Si l'Article B est dans le cycle 1 et se voit refusé, sa resoumission naturelle est le cycle 2 : deux articles de la même équipe sur le même plancher dans le même vivier de reviewers. Février est en outre trop tôt pour G2.

**Repli.** ICLR 2028, réceptif aux travaux JEPA. L'échéance ICLR 2027 était le 24 septembre 2026 ; si 2027 suit le même calendrier, la fenêtre entre la notification NeurIPS et l'échéance ICLR sera serrée et devra être vérifiée dès la publication des dates.

**ICAIF 2027.** L'échéance tombe historiquement début août (à vérifier), pendant la revue NeurIPS : la double soumission l'exclut comme repli après NeurIPS. ICAIF est une alternative à décider au jalon G2 du 1er mars : si G1 passe et G2 échoue, la version appliquée (encodeur impair, facteurs CD-DFM, recensement EUROFIDAI) y trouve sa ligne éditoriale.

**Workshops NeurIPS.** En 2026, la date suggérée pour les contributions aux workshops était le 29 août. Un workshop non archivant reste compatible avec une soumission principale en cours, sous réserve de sa politique ; l'existence d'un workshop finance en 2027 ne se vérifiera qu'à la publication de la liste. Usage : visibilité, pas cible.

L'Article B doit être sur arXiv avant mai 2027 si la politique d'anonymat de KDD le permet. À défaut, l'Article C réénonce le plancher de façon autonome et cite l'Article B à la troisième personne.

## 6. Livrables du 12 au 25 octobre 2026

- **A1 — Note théorique v0** (LaTeX, anglais, environ 8 pages) : Propositions 1–3, lemme d'encodeur impair, critère d'absorption, preuves. Chaque énoncé est accompagné de la décision de design qu'il fixe et de la prédiction qui le réfuterait.
- **A2 — `floor_calculator.py` et validation Monte Carlo.** Le prototype de $M(D)$ est déjà validé à 4 % près ; extension au CUSUM pire cas de Lorden, aux priors mal accordés et à l'efficacité des capteurs de signe, avec CSV et figure ADD–D.
- **A3 — Notebook d'audit informationnel S&P 500** : spectre, η, corrélations de signe, test de symétrie centrale, SR de dérive débiaisé par transition Pagan-Sossounov dans trois sous-espaces (marché, K = 11 facteurs CD-DFM ou PCA, caractéristiques orthogonalisées), part des phases dans le budget. Dépendance : le panel de l'Article B ou l'univers des 239 titres de CD-DFM, avec leurs caractéristiques.
- **A4 — Squelette du dépôt**, `INTERFACE.md` et les quatre tests de contrat.
- **A5 — Pilote de l'échelle linéaire** sur fond S&P 500 symétrisé : B0, B1, B2, B3, familles F1–F3.

**Premier jalon empirique vérifiable, le 25 octobre : le test d'échappement.** Fond S&P 500 symétrisé, $N\in\{8,16,32,64,128,239\}$, dérive F2 d'amplitude calibrée pour que l'oracle détecte en environ un an à $N=239$. Trois critères falsifiables : FPR des flux de signe à ±1 point du nominal, l'exactitude étant garantie par construction, ce qui valide la chaîne ; ADD mesuré à ±15 % de la prédiction des Propositions 2–3 ; exposant $\hat\beta$ proche de 0 pour le pooling sur F3 et strictement positif, IC excluant 0, pour le PCA résiduel sur F2. Un échec sur le deuxième critère impose de réviser la théorie avant tout autre chantier.

**[Strategic Advice]**

- Livraison en Markdown dans le fil, sans Doc ni artefact, conformément à la préférence « aucun conteneur sans demande explicite ». Horodatage : seule la date est injectée, aucune heure.
- Angle mort principal : la valeur ajoutée propre du JEPA sur la localisation en finance est probablement faible. Une normalisation non apprise capte déjà 0,82 sur N1, et CD-DFM couvre une partie de N2. Les chances les plus sérieuses du JEPA se trouvent dans le tabulaire hétérogène (BAF) et les dérives de second ordre ; le plan garde les deux issues publiables pour cette raison.
- La Proposition 3 décrit le délai d'un détecteur à mélange accordé. Son statut de borne inférieure de second ordre, via la redondance de Clarke-Barron, reste à démontrer : ne pas l'énoncer comme borne dans le papier avant preuve.
- Les nombres produits ici sont reproductibles : $M(D)$ (analytique et Monte Carlo à 300 réplications), pénalité de dépassement sous GARCH (2 000 trajectoires), angles du dictionnaire, budgets de second ordre, critère d'absorption. Les scripts de travail rejoignent le dépôt avec A2. L'échelle d'efficacité (0,44 à 0,82) repose sur une volatilité log-normale avec s = 0,9 choisie pour l'illustration ; l'estimation de Phase 0 la remplacera.
- Hypothèses non vérifiées : Drive vs. Decay et TAU-JEPA (aucune trace publique repérée par mes recherches), le nombre de features de BAF, la disponibilité de caractéristiques point-in-time pour EUROFIDAI, le statut de l'Article B (supposé dans le cycle 1 de KDD 2027). Les dates NeurIPS et ICML 2027 sont des projections, pas des annonces.
- Si l'Article B est dans le cycle 1, son rebuttal passe avant A1–A5 : la période de rebuttal du cycle 1 de KDD 2027 court du 29 septembre au 13 octobre 2026.
- Branche écartée la plus coûteuse à rouvrir : TAU-JEPA comme chemin surveillé. Si José tient à ce socle, le cantonner au prétexte de pré-entraînement.Quatre points du cadrage actuel sont faux ou manquants ; une fois corrigés, la thèse tient.

1. **η ≈ 0,9 contredit les données du projet.** Sur les 239 titres S&P 500 de Lehalle & Alouadi, le facteur de marché explique R² = 0,36 de la variance. La corrélation de signe ρ̂ ≈ 0,26 de l'Article B correspond, par la relation gaussienne ρ_signe = (2/π)·arcsin ρ, à une corrélation de rendements de 0,40 : η ≈ 0,40. Avec γ = 0,5, la formule G = γ/(1−η) de `KL_PCA_PIVOT.md` donne G ≈ 0,8, soit une perte. Cette formule mesure un rapport signal/bruit par direction. Elle omet le terme de largeur (breadth), qui croît avec N et constitue la seule échappatoire non bornée.
2. **Un JEPA à masquage inter-actifs ne peut pas isoler le signal idiosyncratique.** Il apprend ce qui se prédit depuis les actifs de contexte, donc la structure systématique. La cible atteignable est la dérive orthogonale au mode de marché et pilotée par les caractéristiques, pas l'idiosyncratique au sens des modèles factoriels.
3. **Surveiller ‖z_target − ẑ‖² branche un capteur d'échelle sur une dérive de localisation.** La Proposition d'orthogonalité de l'Article B le cantonne au second ordre. Un résidu de prédiction est de plus aveugle à toute dérive cohérente que le prédicteur reproduit depuis le contexte.
4. **La taxe dimensionnelle manque.** Ignorer la direction de la dérive dans un sous-espace de dimension D multiplie l'ADD par 2,0 à D = 10 et par 3,9 à D = 64, à ARL₀ = 504 (formule analytique validée par Monte Carlo à 4 % près, §1.2). Un latent de 128 dimensions surveillé tel quel paie 5,2× avant toute considération de KL. Le gain d'un espace latent ne vient pas de la KL (DPI) ; il vient de la compression de la dimension de l'alternative composite.

Titre retenu : *JEPA-Drift: Escaping the Sharpe Ceiling of Sequential Drift Detection through Latent Information Concentration*. « Concentrating Kullback-Leibler Divergence » se lit comme une hausse de KL, qu'un reviewer familier de la DPI attaquera d'emblée. Si le jalon G2 échoue, l'article sort sous *Latent Information Floors: What Learned Representations Can and Cannot Buy for Sequential Drift Detection* ; le protocole garde les deux issues publiables.

## 1. Analyse critique et positionnement

### 1.1 Du linéaire au non linéaire sans violer la DPI

Notations. $x_t \in \mathbb{R}^N$ : rendements du jour $t$ ; $C_t \in \mathbb{R}^{N\times P}$ : caractéristiques prédéterminées ($\mathcal{F}_{t-1}$-mesurables) ; $\Sigma_t$ : covariance conditionnelle ; après la rupture en $\tau^*$, la moyenne conditionnelle se déplace de $\Delta\mu_t$. Pour une représentation $\phi$, $\mathcal{I}_\phi$ désigne le taux d'information de Kullback-Leibler par observation du processus $\phi(x_t;C_t)$ au sens de Lai (1998), et $\mathcal{I}_x$ celui des données brutes.

**Proposition 1 (hiérarchie informationnelle, alternatives de localisation locales).**
$$\tfrac12\,\overline{\Delta\mu}^{\top}\bar\Sigma^{-1}\overline{\Delta\mu}\;\le\;\tfrac12\,\mathbb{E}\!\left[\Delta\mu_t^{\top}\Sigma_t^{-1}\Delta\mu_t\right]\;\le\;\tfrac12\,\mathbb{E}\!\left[\Delta\mu_t^{\top}\mathcal{J}_t\,\Delta\mu_t\right]=\mathcal{I}_x,\qquad \mathcal{I}_\phi\le\mathcal{I}_x\ \ \forall\phi,$$
avec $\bar\Sigma=\mathbb{E}[\Sigma_t]$ et $\mathcal{J}_t$ l'information de Fisher conditionnelle de localisation. La première inégalité découle de la convexité jointe de $(a,S)\mapsto a^\top S^{-1}a$ (Jensen), la deuxième de $\mathcal{J}_t\succeq\Sigma_t^{-1}$ (Cramér-Rao, égalité ssi gaussien conditionnel), la dernière de la DPI. Le terme de gauche borne tout moniteur linéaire statique.

Un encodeur non linéaire ne crée pas d'information. Il récupère ce que la classe linéaire statique jette, par trois canaux, seules sources légitimes d'un gain JEPA :

- **(N1) Volatilité commune.** L'écart $\mathbb{E}[\sigma_t^2]\,\mathbb{E}[\sigma_t^{-2}]$ est le gain de Jensen que l'Article B n'atteignait qu'avec un oracle à paramètres GARCH connus par anticipation (×10,6 sur le krach de 2020). En univarié, $\sigma_t$ ne s'obtient que par un modèle ajusté sur le passé. Dans la coupe, la dispersion du jour le mesure sans modèle, avec une erreur relative en $O(N_{\text{eff}}^{-1/2})$, et une statistique homogène de degré 0, inaccessible à toute application linéaire non nulle, l'exploite en ligne.
- **(N2) Chargements variables pilotés par les caractéristiques** (IPCA, CD-DFM) : écart entre $(\overline{\Delta\mu},\bar\Sigma)$ et $(\Delta\mu_t,\Sigma_t)$.
- **(N3) Non-gaussianité résiduelle** : écart entre $\mathcal{J}_t$ et $\Sigma_t^{-1}$ une fois la volatilité retirée.

**Définition (concentration).** Pour une famille $\phi_D$ de dimension $D$, la rétention vaut $r_\phi(D)=\mathcal{I}_{\phi_D}/\mathcal{I}_x\in[0,1]$. La thèse s'énonce $\max_D r_{\text{JEPA}}(D)/M(D)>\max_D r_{\text{lin}}(D)/M(D)$, où $M$ est la taxe dimensionnelle de la Proposition 3. JEPA gagne en retenant plus d'information à faible dimension.

Le plafond du gain JEPA sur le meilleur modèle linéaire se mesure donc avant tout pré-entraînement. Pour le canal N1, sous volatilité commune log-normale ($s$ = écart-type de $\ln\sigma_t^2$, fixé à 0,9 pour l'illustration), l'efficacité relative au rapport de vraisemblance conditionnel s'ordonne ainsi :

| Moniteur sur une même projection $u$                          | Efficacité                          | Calibration                          |
| ------------------------------------------------------------- | ----------------------------------- | ------------------------------------ |
| CUSUM de moyenne, variance inconditionnelle                   | $e^{-s^2}=0{,}44$                   | faussée (§3.2)                       |
| CUSUM de signe, mise fixe (Article B)                         | $\tfrac{2}{\pi}e^{-s^2/4}=0{,}52$   | exacte                               |
| e-détecteur de signe, mise $\propto 1/\hat\sigma_{t\mid t-1}$ | $2/\pi=0{,}64$ (prévision parfaite) | exacte, quelle que soit $\hat\sigma$ |
| statistique auto-normalisée de degré 0 ($N\to\infty$)         | $e^{-s^2/4}=0{,}82$                 | pivot exact sous échelle commune     |
| RV conditionnel, $\sigma_t$ connu                             | $1$                                 | oracle                               |

Une normalisation transversale non apprise (dé-moyennage puis division par la dispersion du jour, soit une LayerNorm appliquée au vecteur de coupe) atteint déjà 0,82. Sur N1, il ne reste au JEPA qu'un facteur 1,22. Sans ce témoin, le gain attribué au JEPA risque d'être celui d'une couche de normalisation.

**Corrections de `KL_PCA_PIVOT.md`.**
- Le calcul du §4 suppose une variance résiduelle isotrope et compare des normes euclidiennes. L'objet correct est la norme de Mahalanobis résiduelle, qui porte un facteur d'ordre $N-1$ quand la dérive résiduelle est dispersée.
- « On jette $v_1$ » jette un canal d'information : $\Delta\mu^\top\Sigma^{-1}\Delta\mu=\sum_k(v_k^\top\Delta\mu)^2/\lambda_k$ est additif sur les directions propres. Le mode de marché se surveille à part (moniteur de l'Article B), et les deux flux se combinent par produit d'e-processes.
- $\alpha=0{,}05$ avec $\ln(1/\alpha)\approx3$ correspond à ARL₀ = 20 jours, une fausse alarme par mois : le point permissif du recensement de l'Article B. Au point opérationnel ARL₀ = 252, $\ln(1/\alpha_0)=5{,}53$, et détecter en 60 jours exige SR = 6,8 en univarié, pas 5,0.
- Le « paradoxe du hedge fund » n'est déplacé qu'à moitié. $\mathrm{SR}_x$ est exactement le Sharpe sans frictions du portefeuille tangent à la dérive ; un détecteur qui conclut en 60 jours certifie des Sharpe sans frictions d'environ 6,8 sur la durée du régime. L'échappatoire vaut dans la mesure où Sharpe sans frictions et Sharpe net divergent.

### 1.2 Plancher de délai dans l'espace latent

**Proposition 2 (plancher oracle).** Sous la condition de taux d'information de Lai (1998), à savoir la convergence r-rapide du log-rapport de vraisemblance normalisé vers $\mathcal{I}_z$, tout temps d'arrêt $T$ adapté à la filtration latente avec $\mathrm{ARL}_0(T)\ge1/\alpha_0$ vérifie, quand $\alpha_0\to0$ et sous modèle gaussien conditionnel :
$$\mathrm{ADD}_z\;\ge\;\frac{504\,\ln(1/\alpha_0)}{\mathrm{SR}_z^2}\bigl(1+o(1)\bigr),\qquad \mathrm{SR}_z^2:=252\,\mathbb{E}\!\left[\Delta\mu_{z,t}^{\top}\Sigma_{z,t}^{-1}\Delta\mu_{z,t}\right].$$
$\mathrm{SR}_z$ est le Sharpe annualisé du portefeuille tangent à la dérive dans l'espace latent, puisque $\max_w(w^\top\Delta\mu_z)^2/(w^\top\Sigma_zw)=\Delta\mu_z^\top\Sigma_z^{-1}\Delta\mu_z$ (Cauchy-Schwarz). Le plafond de Sharpe de l'Article B en est le cas $N=D=1$, et la DPI impose $\mathrm{SR}_z\le\mathrm{SR}_x$. À direction connue, $D=1$ suffit : $w^*=\Sigma^{-1}\Delta\mu$ atteint l'égalité. La dimension latente ne sert qu'à couvrir l'incertitude sur la direction.

**Structure factorielle.** Avec $x_t=B_tf_t+\varepsilon_t$, $\mathrm{Cov}(f_t)=\Sigma_F$, $\mathrm{Cov}(\varepsilon_t)=\Psi$ diagonale et $\Delta\mu=B\Delta\lambda+\Delta\alpha$, des facteurs pervasifs donnent, quand $N\to\infty$ :
$$\mathrm{SR}_x^2\;\to\;\underbrace{252\,\Delta\tilde\lambda^{\top}\Sigma_F^{-1}\Delta\tilde\lambda}_{\mathrm{SR}_F^2,\ \text{borné en }N}\;+\;\underbrace{252\,\Delta\alpha_\perp^{\top}\Psi^{-1}\Delta\alpha_\perp}_{\text{largeur},\ \propto N},$$
où $\Delta\alpha_\perp$ est le résidu GLS de $\Delta\alpha$ sur les chargements et $\Delta\tilde\lambda$ en absorbe la partie alignée. La saturation $K_{\text{eff}}\approx1/\hat\rho\approx3{,}8$ de l'Article B correspond à un seul facteur qui dérive : rapporté au Sharpe d'un titre isolé, le premier terme vaut $1/\rho$. Il n'existe que deux échappatoires. Soit plusieurs facteurs dérivent ensemble et le plateau monte à $\mathrm{SR}_F^2/\mathrm{SR}_1^2$, toujours borné ; soit une dérive idiosyncratique se disperse sur beaucoup de titres et le gain croît avec $N$. La table 6 de Lehalle & Alouadi plaide pour la première : sur leur fenêtre de crise (247 jours, une graine, à lire pour le signe selon les auteurs), les facteurs cash-neutral utilities, santé, consommation discrétionnaire, technologie et financières varient de +13 % à −16 %. À 8 % de volatilité annuelle, hypothèse à mesurer, chacun porterait un SR de dérive de 1 à 2.

**Proposition 3 (alternative composite).** Pour une dérive de direction inconnue dans un sous-espace de dimension $D_{\text{eff}}$, le détecteur à mélange gaussien isotrope accordé à l'amplitude (méthode des mélanges de Robbins ; GLR de Siegmund & Venkatraman, 1995) atteint
$$\mathrm{ADD}_z\approx\frac{504\,\ln(1/\alpha_0)}{\mathrm{SR}_z^2}\,M(D_{\text{eff}},\alpha_0),\qquad M=\frac{x}{\ln(1/\alpha_0)},\quad x=\ln\frac{1}{\alpha_0}+\frac{D_{\text{eff}}}{2}\ln\!\Bigl(1+\frac{2x}{D_{\text{eff}}}\Bigr).$$
Le terme $\frac D2\ln(\cdot)$ est la redondance minimax d'une famille à $D$ paramètres (Rissanen ; Clarke & Barron, 1990). Quand $\alpha_0\to0$, il devient d'ordre $\frac D2\ln\ln(1/\alpha_0)$ et négligeable. Aux ARL₀ opérationnels, il domine dès $D\approx10$ ; pour $D\gg\ln(1/\alpha_0)$, $x\approx\sqrt{D\ln(1/\alpha_0)}$.

| $D_{\text{eff}}$        | 1    | 5    | 10   | 20   | 64   | 128  | 500  |
| ----------------------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| $M$, ARL₀ = 252         | 1,24 | 1,71 | 2,08 | 2,62 | 4,10 | 5,50 | 10,2 |
| $M$, ARL₀ = 504         | 1,22 | 1,66 | 2,01 | 2,51 | 3,91 | 5,23 | 9,64 |
| Monte Carlo, ARL₀ = 504 | 1,27 | 1,63 | 2,06 | —    | 3,83 | —    | 9,82 |

Monte Carlo : 300 réplications (150 à $D=500$) ; l'oracle à direction connue donne $M\in[0{,}95;1{,}04]$. Trois conséquences de design en découlent. Le latent surveillé a $D_{\text{eff}}\le10$–16, et un JEPA de dimension 128 ne se surveille qu'à travers une tête de lecture compressée. Un dictionnaire de $M$ directions économiques (facteurs CD-DFM, secteurs, styles) coûte $\ln M$ au lieu de $\frac D2\ln(\cdot)$ mais perd $\cos^2\theta$, où $\theta$ est l'angle entre la dérive blanchie et l'atome le plus proche : à ARL₀ = 504, vingt atomes battent le mélange continu de dimension 10 si $\theta<22°$, de dimension 64 si $\theta<48°$, et jamais celui de dimension 5. Enfin, la loi d'échelle en $N$ devient la signature falsifiable de l'article : $G\propto N^0$ (pooling, dérive de marché, Article B), $G\propto N^{1/2}$ (coupe entière non structurée, la taxe en $\sqrt N$ absorbant la moitié de l'exposant), $G\propto N$ (dérive de largeur pilotée par $P$ caractéristiques, latent structuré de dimension fixe).

**Niveau du moniteur et décomposition du gain.** $\mathrm{ADD}_{\text{mon}}\approx(\Gamma_z^{\text{op}}/e_m)\,\mathrm{ADD}_z$, où $e_m$ vient de la table d'efficacité et $\Gamma_z^{\text{op}}$ est la pénalité de calibration opérationnelle définie au §3.2. Le gain sur l'univarié se factorise :
$$G=\frac{\mathrm{ADD}_{\text{univ}}}{\mathrm{ADD}_{\text{lat}}}=\underbrace{\frac{\mathrm{SR}_z^2}{\mathrm{SR}_1^2}}_{\text{concentration}}\times\underbrace{\frac{M(1)}{M(D_{\text{eff}})}}_{\text{taxe}}\times\underbrace{\frac{e_z\,\Gamma_1^{\text{op}}}{e_1\,\Gamma_z^{\text{op}}}}_{\text{blanchiment}}.$$
Ordre de grandeur : détecter en 252 jours au plus à ARL₀ = 504 exige $\mathrm{SR}_z\ge3{,}53$ (oracle), 4,54 ($D_{\text{eff}}=5$), 5,00 ($D_{\text{eff}}=10$), 6,97 ($D_{\text{eff}}=64$). Ces seuils fixent ce que l'audit de Phase 0 doit trouver dans les données.

### 1.3 Verrous théoriques immédiats

**V1 — Aveuglement jacobien.** Pour une petite dérive, $\Delta\mu_z\approx\mathbb{E}[J_\phi]\,\Delta\mu$ : toute composante dans le noyau de $J_\phi$ disparaît. Dans les réseaux linéaires profonds, le biais implicite des JEPA privilégie les directions prédictives sur les directions de forte variance, à l'inverse de MAE (Littwin et al., NeurIPS 2024). C'est l'argument théorique de JEPA contre PCA pour les directions peu variables mais structurées, et la raison pour laquelle les dérives non prédictibles depuis le contexte sont perdues. Instrument : le rapport de transmission $T(u)=\|\Sigma_z^{-1/2}\mathbb{E}[J_\phi]u\|^2/\|\Sigma^{-1/2}u\|^2$, calculé par différences finies sur les directions injectées ; $T>1$ n'est possible que par les canaux N1–N3. Prédiction testable : à $D$ égal, $T_{\text{JEPA}}>T_{\text{MAE}}$ sur les directions de faible variance.

**V2 — Validité de $H_0$ dans le latent.**

*Lemme (blanchiment par encodeur impair).* Soit $\phi(\cdot\,;C)$ impaire en $x$, $\phi(-x;C)=-\phi(x;C)$, avec $C_t$ et une direction $u_t$ $\mathcal{F}_{t-1}$-mesurables. Si, sous $H_0$, la loi de $x_t$ sachant $\mathcal{F}_{t-1}$ est centralement symétrique et $\mathbb{P}(u_t^\top\phi(x_t;C_t)=0\mid\mathcal{F}_{t-1})=0$, alors $b_t=\mathbf 1\{u_t^\top\phi(x_t;C_t)>0\}$ est i.i.d. Bernoulli(1/2), quelles que soient les dynamiques de volatilité, de corrélation et de queues.

*Preuve.* $g=u_t^\top\phi(\cdot\,;C_t)$ est impaire conditionnellement à $\mathcal{F}_{t-1}$ ; la symétrie donne $\mathbb{P}(g(x_t)>0\mid\mathcal{F}_{t-1})=\mathbb{P}(g(x_t)<0\mid\mathcal{F}_{t-1})=1/2$, et une suite de bits de loi conditionnelle constante 1/2 est i.i.d. ∎

Le lemme étend la propriété de blanchiment de l'Article B du signe d'un rendement au signe d'une projection impaire de toute la coupe. Il fournit aussi la version latente de la Proposition d'orthogonalité. Avec $\phi_{\text{imp/pair}}(x)=\tfrac12[\phi(x)\mp\phi(-x)]$, toute statistique impaire est exactement aveugle à un changement qui préserve la symétrie centrale (volatilité, corrélation, queues), et toute statistique paire ne voit une translation qu'au second ordre. Le JEPA reçoit donc deux têtes : impaire pour le pipeline Concept latent (capteur de signe), paire pour le pipeline Data latent (capteur énergétique recalibré). Si $\phi$ est en outre homogène de degré 0, la statistique entière, pas seulement son signe, a une loi nulle libre de l'échelle commune.

Trois limites s'appliquent. Les égalités (rendements nuls, valeurs manquantes imputées à zéro sur les petites capitalisations) se tranchent par tirage aléatoire, ce qui préserve l'exactitude. L'asymétrie de dépendance de queue (Longin & Solnik, 2001 ; Ang & Chen, 2002) viole la symétrie centrale et impose un recentrage sur un taux $\hat q_u$ estimé, comme pour l'asymétrie dans l'Article B. La prime de risque déplace la médiane, moins dans les directions cash-neutral que sur l'indice (SPY : de 0,541 à 0,554 de jours haussiers sur 2011–2018 dans l'Article B).

**V3 — Agrégation.** Le flux poolé de l'Article B perd sa blancheur au-delà de K = 10, parce que la variance conditionnelle d'une somme de signes suit la corrélation transversale du jour. Le lemme ne couvre qu'un signe par direction. Plusieurs directions se combinent par mélange d'e-processes : une moyenne de martingales de test sous la même filtration reste une martingale de test, quelle que soit la dépendance entre directions. Ni Bonferroni ni bootstrap.

**V4 — Taxe dimensionnelle.** $D_{\text{eff}}\le10$–16, ou priors structurés (dictionnaire, parcimonie), par la Proposition 3.

**V5 — Non-anticipation.** Encodeur pré-entraîné strictement avant la fenêtre surveillée ; caractéristiques datées à leur publication, les fondamentaux trimestriels arrivant avec plusieurs semaines de retard ; statistiques de normalisation gelées ; embargo d'au moins la longueur de contexte plus 5 jours.

## 2. Orchestration et jalons

### 2.1 Phases

| Phase                                       | Fenêtre                 | Contenu                                                                                                                   | Livrable                                 | Jalon         |
| ------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------------- |
| P0 — Théorie et audit                       | 12 oct. – 8 nov. 2026   | Props 1–3, lemme, critère d'absorption ; validation Monte Carlo ; audit S&P 500                                           | note théorique v1, notebook d'audit, CSV | G0, 9 nov.    |
| P1 — Pile de surveillance, échelle linéaire | 26 oct. – 13 déc.       | moniteurs (signe, e-détecteurs, degré 0) ; fonds symétrisés S&P 500 et EUROFIDAI ; familles F1–F4 ; échelle B0–B5         | `benchmark_runner`, courbes ADD–ARL₀     | G1, 14 déc.   |
| P2 — Représentations (José, en parallèle)   | 26 oct. – 17 janv. 2027 | CA-T-JEPA à têtes impaire/paire ; T-JEPA sur BAF ; diagnostics anti-collapsus                                             | checkpoints conformes au contrat         | G2a, 18 janv. |
| P3 — Confrontation, attribution             | 4 janv. – 28 févr.      | JEPA contre l'échelle linéaire ; ablations (normalisation seule, MAE, TAU-JEPA, balayage de D) ; spectres de transmission | tableaux principaux                      | G2, 1er mars  |
| P4 — In-the-wild, BAF, rédaction            | 1er mars – 30 avr.      | régimes datés ; dérive mensuelle BAF ; rapport anytime-valid ; relecture interne mi-avril                                 | manuscrit gelé le 30 avril               | soumission    |

Échelle de référence : B0, indice univarié (signe, Article B) ; B1, pooling équipondéré ; B2, PCA résiduel ; B3, normalisation transversale de degré 0 et rangs transversaux centrés (impairs, invariants d'échelle et de translation) ; B4, facteurs cash-neutral CD-DFM et IPCA ; B5, oracle à direction connue. Les familles de dérive injectées sont calibrées sur les transitions historiques (vecteurs $\Delta\hat\mu$ rétrécis) : F1, primes factorielles $B_t\Delta\lambda$ (plateau attendu) ; F2, largeur $(C_t\Delta\gamma)_\perp$ (croissance attendue en $N$) ; F3, mode de marché (témoin qui doit reproduire la saturation de l'Article B) ; F4, rotation factorielle ou déformation de $\Sigma_t$ (tête paire).

### 2.2 Jalons Go/No-Go

- **G0 (9 nov.)** — (a) Les ADD simulés reproduisent les Propositions 2–3 à ±10 % sur fond gaussien et sur fond GARCH symétrisé. (b) L'audit place le plancher oracle transversal sous la durée d'au moins 25 % des phases datées à ARL₀ = 252, contre 2 sur 66 (3 %) en univarié dans l'Article B. Échec de (b) : contingence C1 ou C2 (§3.4), car par la DPI aucun encodeur ne fera mieux que l'oracle.
- **G1 (14 déc.)** — Le meilleur moniteur de l'échelle linéaire tient sa FPR à ±15 % du nominal sur fonds nuls symétrisés ; les flux de signe étant exacts par construction, cela teste la pile elle-même. Il atteint G ≥ 4 contre l'univarié composite sur événements appariés, et l'exposant d'échappement $\hat\beta$ (pente de $\log G$ en $\log N$) est positif sur F2 avec un IC à 95 % qui exclut 0. Si G0 passe et G1 échoue, l'information existe mais la surveillance la perd : on corrige la pile, pas l'encodeur.
- **G2a (18 janv.)** — Rang effectif RankMe de la tête de lecture ≥ 0,5·D ; $T_{\text{JEPA}}(u)\ge T_{\text{PCA}}(u)$ sur au moins la moitié des directions injectées ; aucun collapsus selon les critères Drive vs. Decay.
- **G2 (1er mars)** — Le JEPA bat le meilleur de B3 et B4 d'un facteur ≥ 1,25 en ADD à ARL₀ égal, sur au moins deux des familles F1, F2, F4, avec un IC à 95 % qui exclut 1 et $D^*\le16$. Échec : titre de repli, résultat JEPA négatif ou conditionnel documenté.

### 2.3 Seuils minimaux pour valider la thèse

**Contre le plafond de Sharpe univarié : G ≥ 4**, composite contre composite ($M(1)$ des deux côtés), sur événements appariés. Un facteur 4 divise par deux le SR requis ; en deçà, la part des régimes datés qui entre dans le budget bouge à peine (64 phases sur 66 hors budget à ARL₀ = 252 dans l'Article B). Le critère lisible par un reviewer reste la part des phases dans le budget, avec une cible de 25 %.

**Contre la saturation transversale : borne inférieure de l'IC de G au-dessus de 3,8**, et non de 2. Le pooling de l'Article B réalise 2× pour un plafond théorique de 3,8, et battre le réalisé ne prouve rien. Une valeur ponctuelle de G ne démontre pas l'échappement ; une pente $\hat\beta>0$ au-delà de $N\approx20$, si.

**Contre le benchmark PCA-orthogonal : ≥ 1,25× (−20 % d'ADD) face au meilleur concurrent linéaire ou non appris (B3, B4).** Passer de $D=5$ à $D=10$ change déjà $M$ de 1,21×, si bien qu'un gain inférieur relève du réglage, pas de la représentation. La normalisation non apprise prend 0,82 sur N1 et laisse au JEPA 1,22× sur ce canal, plus ce que N2 et N3 apporteront, inconnu avant l'audit.

### 2.4 Séquence technique

Le benchmark PCA résiduel passe d'abord côté surveillance ; le pré-entraînement JEPA démarre en parallèle le 26 octobre côté représentation. Trois raisons imposent l'ordre côté surveillance. Un ADD JEPA médiocre reste ininterprétable sans pile calibrée, car il faut savoir si l'information manque (G0), si la calibration fuit (G1) ou si l'encodeur perd la direction (G2a). L'audit et l'échelle linéaire peuvent arrêter ou réorienter le projet avant toute dépense JEPA. L'échelle linéaire fixe enfin le contrat d'interface, des tableaux $Z$, dans lequel le JEPA se branche.

Le parallélisme tient au calendrier. En séquentiel strict, P3 commencerait en mars et laisserait huit semaines à P4. Chemin critique : contrats de données → pile de surveillance → G1 → confrontation → G2 → rédaction.

### 2.5 Arbitrages structurants

| Décision             | Retenu                                                                                                                              | Écarté                                   | Motif de clôture                                                                                                                                                       |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ordre                | linéaire d'abord (surveillance), JEPA en parallèle                                                                                  | JEPA d'abord ; séquentiel strict         | ininterprétable sans pile calibrée ; chemin critique trop long                                                                                                         |
| Architecture finance | CA-T-JEPA : actifs comme jetons, conditionné par $C_t$, équivariant par permutation, têtes impaire/paire, chemin surveillé par jour | TAU-JEPA comme socle du chemin surveillé | fenêtres chevauchantes (Γ_z ≈ L) ; normalisation d'instance temporelle (absorption) ; échantillon T au lieu de N·T. TAU-JEPA reste en ablation comme prétexte temporel |
| Capteur              | signe de projection impaire, e-détecteurs, statistique de degré 0                                                                   | ‖z − ẑ‖²                                 | capteur d'échelle, aveugle aux dérives cohérentes, Γ_z > 1                                                                                                             |
| Calibration finance  | signe exact ; randomisation par inversion de signe pour les statistiques à amplitude                                                | permutation                              | l'échangeabilité échoue sous GARCH                                                                                                                                     |
| Statut de l'encodeur | gelé, rafraîchissement programmé                                                                                                    | adaptatif en ligne                       | critère d'absorption (§3.1)                                                                                                                                            |
| Baseline             | échelle B0–B5 avec CD-DFM, IPCA et normalisation transversale                                                                       | PCA statique seule                       | épouvantail qu'un reviewer relèvera                                                                                                                                    |
| Conférence           | NeurIPS 2027                                                                                                                        | ICML 2027 ; KDD 2027 cycle 2             | calendrier ; chevauchement avec l'Article B (§5)                                                                                                                       |

Un résultat récent montre ce que coûte le capteur écarté : avec un encodeur V-JEPA 2 gelé, le score d'erreur de prédiction atteint 0,89 d'AP sur un banc inter-jeux de données mais 0,29, proche du hasard, sur un banc équitable intra-nuScenes, alors qu'une sonde supervisée retrouve le signal dans les embeddings gelés. Le score de densité implicite des JEPA relève de la tête paire : le terme anti-collapsus d'un JEPA estime implicitement la densité des données, extractible sous le nom de JEPA-SCORE, ce qui en fait un capteur de nouveauté, pas de localisation.

## 3. Arbre des risques et contingences

### 3.1 (i) Absorption selon le statut de l'encodeur

Un encodeur adaptatif de constante de temps $\tau_a$ fait décroître la dérive latente, $\Delta\mu_z(s)=\Delta\mu_z(0)\,e^{-s/\tau_a}$, et l'information cumulée plafonne à $\mathcal{I}_z\tau_a/2$. Le critère de détectabilité et le délai qui en résulte sont :
$$\tau_a>2\,\mathrm{ADD}_{\text{or}},\qquad \mathrm{ADD}=-\frac{\tau_a}{2}\ln\!\Bigl(1-\frac{2\,\mathrm{ADD}_{\text{or}}}{\tau_a}\Bigr),\qquad \mathrm{ADD}_{\text{or}}=\frac{\ln(1/\alpha_0)}{\mathcal{I}_z}.$$
Pour $\tau_a$ = 2,5, 4 et 8 fois $\mathrm{ADD}_{\text{or}}$, le délai vaut 2,01, 1,39 et 1,15 fois l'oracle ; à $\tau_a\le2\,\mathrm{ADD}_{\text{or}}$, la dérive n'est jamais détectée. Comme $\mathrm{ADD}_{\text{or}}$ se compte en centaines de jours pour une dérive de localisation, un encodeur en ligne doit garder plusieurs années de mémoire : il est gelé de fait. C'est la « starvation » que tu as caractérisée entre ensembles adaptatifs (ARF, SRP) et détecteurs externes, transposée à l'encodeur. L'encodeur gelé, lui, n'absorbe rien mais vieillit : l'évolution lente des corrélations et des distributions de caractéristiques déplace la loi nulle latente et produit le pendant « flooding », celui que tu as observé sur tous les flux réels.

L'absorption se cache aussi hors de l'apprentissage : BatchNorm laissée en mode entraînement à l'inférence ; normalisation d'instance temporelle de type RevIN, standard dans PatchTST, qui retire la moyenne de la fenêtre et efface une translation après L jours ; mise à jour EMA du target encoder si l'entraînement continue pendant la surveillance.

Protocole :
1. Référence gelée $\phi_{\text{ref}}$ pré-entraînée sur $[t_0,t_1)$, rafraîchie à des intervalles $T_{\text{ref}}\ge4\,\mathrm{ADD}_{\text{cible}}$ sur une fenêtre qui exclut les $\mathrm{ADD}_{\text{cible}}$ derniers jours.
2. Après alarme confirmée, ré-ancrage : réentraînement sur le nouveau régime avant reprise de la surveillance.
3. Test de contrat : en mode `eval`, aucun buffer ne change ; aucune normalisation calculée sur l'axe temporel dans le chemin surveillé.
4. Vieillissement mesuré : ARL₀ réalisé par tranche annuelle depuis le pré-entraînement, sur fond symétrisé.

### 3.2 (ii) Calibration sous hétéroscédasticité latente

Γ_z a trois sources distinctes dans le latent.

- **Chevauchement temporel.** Un encodeur à fenêtre de L jours produit des latents autocorrélés ; pour une moyenne glissante uniforme, $\Gamma_z^{\text{spec}}=1+2\sum_{k<L}(1-k/L)=L$. Un encodeur temporel à fenêtre de 60 jours inflige Γ_z ≈ 60 à une statistique de premier ordre sans aucun GARCH.
- **Agrégats quadratiques.** ‖z‖² et ‖z − ẑ‖² héritent du clustering de volatilité ($\hat\Gamma\in[2{,}6;15{,}0]$ sur les ETF de l'Article B).
- **Pénalité de dépassement des statistiques de premier ordre**, absente de la définition spectrale de l'Article B. Des rendements non autocorrélés ont $\Gamma^{\text{spec}}=1$, et pourtant un CUSUM de premier ordre calibré en i.i.d. perd sa calibration sous GARCH dès que le seuil est profond. Vérification sur GARCH(0,08 ; 0,90) à innovations gaussiennes, 2 000 trajectoires : à δ = 0,5 et λ = 6, l'ARL₀ passe de 2 587 (i.i.d.) à 889, soit ÷2,9 ; à δ = 1 et λ = 3, de 1 894 à 669. À seuil peu profond (ARL₀ ≈ 190), l'erreur s'inverse (+17 %, côté conservateur). Le CUSUM de signe reste exact (213 contre 214). La pénalité croît avec ARL₀, donc dans la zone opérationnelle : c'est une Lethargy Tax que le facteur spectral ne voit pas.

Protocole :
1. Chemin surveillé par jour, sans fenêtre chevauchante, ou par blocs disjoints au prix d'un retard d'au plus L.
2. Premier ordre : signe de projection impaire (exact), ou e-détecteur par paris avec mises prévisibles $\lambda_t\propto1/\hat\sigma_{t\mid t-1}$, $\hat\sigma$ étant tiré de la dispersion transversale passée. Le modèle de volatilité n'entre que dans la mise, donc dans la puissance, jamais dans la validité (inégalité de Ville).
3. Statistiques à amplitude : calibration par randomisation d'inversion de signe, $x_t\mapsto\epsilon_tx_t$ avec $\epsilon_t$ de Rademacher appliqué à toute la coupe du jour ; exacte sous symétrie conditionnelle sans effet de levier, approchée sinon.
4. Fonds symétrisés : la même transformation appliquée au fond réel conserve $|x_t|$, donc clustering et corrélations, et détruit toute dérive de localisation. Chaque tirage fournit une trajectoire nulle avec la vraie hétéroscédasticité, et l'estimation de l'ARL₀ cesse de dépendre des quelques fausses alarmes que 25 ans de données autorisent. La symétrisation détruit l'effet de levier : un bras placebo sur fond brut (Δ = 0) reste obligatoire, comme dans l'Article B.
5. Mesure : $\Gamma_z^{\text{op}}:=\lambda_{\text{requis}}/\lambda_{\text{iid}}$ à ARL₀ fixé, pour chaque moniteur, sur fonds symétrisés.

### 3.3 (iii) Dimension latente et perte géométrique

La Proposition 3 rend l'ADD en U en fonction de D : la rétention $r(D)$ croît puis sature, la taxe croît en $\sqrt D$. Passer de D = 5 à 10 doit augmenter la rétention de plus de 21 % ; de 20 à 64, de plus de 56 %. L'effondrement spectral partiel des représentations auto-supervisées (Jing et al., ICLR 2022) frappe d'abord les petites valeurs propres, précisément celles où une dérive isotrope porte le plus de KL, puisque la contribution de la direction $k$ vaut $(v_k^\top\Delta\mu)^2/\lambda_k$. Le blanchiment estimé ajoute un biais : une Mahalanobis calculée avec $\hat\Sigma_z^{-1}$ sur $n$ points est gonflée d'un facteur proche de $n/(n-D-1)$ (moyenne de la Wishart inverse), soit +15 % à $n=500$ et $D=64$, ce qui se paie en fausses alarmes.

Protocole : balayage de la tête de lecture $D\in\{2,4,8,16,32\}$ sur un tronc JEPA fixe ; $D^*$ choisi sur la seule fenêtre de calibration ; retrait de Ledoit-Wolf, ou capteurs de signe qui n'inversent aucune matrice ; RankMe rapporté pour chaque $D$ ; spectres de transmission $T(u)$ sur une base fixée a priori (vecteurs propres, facteurs CD-DFM, directions de caractéristiques).

### 3.4 Registre complémentaire et contingences

| #   | Risque                                     | Mécanisme ou signal                                                                                                                                                                                                            | Contournement                                                                                                                                                                                                                          |
| --- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R4  | Comparaison univarié/transversal mal posée | événements différents comparés                                                                                                                                                                                                 | événements appariés : chaque dérive injectée, calibrée sur une transition historique, est mesurée sur l'indice et sur la coupe                                                                                                         |
| R5  | Survivant, look-ahead                      | panel de 97 survivants dans l'Article B ; fondamentaux publiés en retard                                                                                                                                                       | constituants point-in-time (EUROFIDAI) ; fondamentaux datés à leur publication                                                                                                                                                         |
| R6  | Gain de normalisation attribué au JEPA     | LayerNorm transversale = dé-moyennage + degré 0                                                                                                                                                                                | B3 obligatoire dans tout tableau principal                                                                                                                                                                                             |
| R7  | Échantillon SSL en finance                 | T ≈ 6 300 jours ; JEPA ≈ PCA par sur-apprentissage                                                                                                                                                                             | poids partagés entre actifs (1,5–3 M actif-jours) ; modèles ≤ 5 M paramètres                                                                                                                                                           |
| R8  | Audit bruité                               | biais de bruit $252N(1/n_1+1/n_2)\approx482$ en SR² pour N = 239 et deux phases de 250 jours                                                                                                                                   | projections de dimension ≤ 30, débiaisées, poolées sur les transitions, IC bootstrap                                                                                                                                                   |
| R9  | Peu de phases in-the-wild                  | 15 à 25 phases par marché sur 2000–2025                                                                                                                                                                                        | US, Europe et datation sectorielle ; présenté en appui, pas en preuve principale                                                                                                                                                       |
| R10 | BAF synthétique                            | BAF a été produit en appliquant des techniques de génération tabulaire à un jeu réel anonymisé de fraude à l'ouverture de compte : des demandes d'ouverture, pas des transactions ; huit mois, donc sept frontières mensuelles | formulation « dérive synthétique réaliste » ; martingales de test conformes (Vovk et al.) sous échangeabilité intra-mois ; les 18 features du cadrage sont à recouper avec la datasheet (une trentaine d'attributs, à ma connaissance) |
| R11 | Degrés de liberté du chercheur             | D, familles et seuils choisis après coup                                                                                                                                                                                       | hash de configuration gelé avant P3 ; période 2023–2025 intouchée jusqu'au gel                                                                                                                                                         |
| R12 | Références invérifiables                   | Drive vs. Decay et TAU-JEPA sans trace publique repérée                                                                                                                                                                        | versions arXiv avant mai 2027 ; à défaut, citation comme travaux non publiés                                                                                                                                                           |
| R13 | Paradoxe d'efficience                      | un Sharpe sans frictions élevé et persistant serait arbitré ; G0(b) échoue                                                                                                                                                     | contingence C1                                                                                                                                                                                                                         |
| R14 | Propriété intellectuelle, licences         | clauses CIFRE de LUSIS ; licence EUROFIDAI sans redistribution                                                                                                                                                                 | accord écrit avant tout dépôt public ; pipeline exécutable de bout en bout sur données S&P 500 publiques                                                                                                                               |
| R15 | Caractéristiques EUROFIDAI                 | fondamentaux point-in-time à confirmer, la base couvrant d'abord prix et événements                                                                                                                                            | canal caractéristiques limité à l'univers S&P 500 de CD-DFM si nécessaire ; EUROFIDAI réservé au test d'échelle en N                                                                                                                   |

- **C1 (échec de G0b).** Bascule vers les dérives de second ordre (rotations factorielles, déformations de $\Sigma_t$) et la tête paire. Un ratio de variance de 1,5 offre 24× le budget KL d'une dérive de SR = 1 (ADD oracle de 117 jours à ARL₀ = 252) ; un ratio de 2 en offre 77× (36 jours).
- **C2.** Domaines à fort rapport signal/bruit (BAF, SWaT/WADI), où l'Article B situe déjà le rendement de la calibration exacte.
- **C3 (échec de G2).** Article théorie, encodeur impair, audit et résultat JEPA négatif documenté (NeurIPS), ou version appliquée (ICAIF).
- **C4 (indisponibilité de José).** CA-T-JEPA minimal (≤ 1 M paramètres) développé côté surveillance, sans les garanties Drive vs. Decay.

## 4. Gouvernance et répartition avec José Lucas De Melo Costa

| Rôle CRediT       | Raphael                                                                              | José Lucas                                                   |
| ----------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| Conceptualization | lead : thèse, planchers, continuité avec l'Article B                                 | support : architecture, hypothèse de biais implicite         |
| Methodology       | lead : surveillance, calibration, protocole semi-synthétique, audit                  | lead : pré-entraînement, anti-collapsus, têtes impaire/paire |
| Formal analysis   | lead : Props 1–3, lemme, absorption                                                  | support : biais implicite JEPA (V1)                          |
| Software          | lead : `data_loader` finance, `injection`, `sequential_monitors`, `benchmark_runner` | lead : `jepa_pretrain`, `representation_extractor`           |
| Data curation     | EUROFIDAI, S&P 500, caractéristiques point-in-time                                   | BAF                                                          |
| Investigation     | expériences finance, in-the-wild                                                     | expériences BAF, ablations SSL (MAE, TAU-JEPA)               |
| Validation        | tests de contrat côté surveillance, reproductibilité bit à bit                       | collapsus, RankMe, transmission                              |
| Writing           | théorie, surveillance, finance ; relecture de tout                                   | représentation, BAF ; relecture de tout                      |

Contrat d'interface :

```text
data_loader      -> panel.parquet  (date, asset_id, ret:f32, in_universe:bool)   # R in R^{T x N}
                 -> chars.parquet  (date, asset_id, c_1..c_P)  # disponibles à l'ouverture de t
                 -> splits.yaml    pretrain [t0,t1) | calib [t1,t2) | monitor [t2,t3) | embargo >= L_ctx + 5
injection        -> panel_inj.parquet + tau_star.json   # dans l'espace des rendements, jamais dans z
jepa_pretrain    -> ckpt/<hash>/   poids gelés + config + hash des données d'entraînement
representation_extractor(ckpt, panel)
                 -> z_<hash>.npz   Z_odd in R^{T x D}, Z_even in R^{T x D'}, option Z_asset in R^{T x N x d}
                 + sidecar JSON    hashes (ckpt, données, splits), drapeaux impair/pair, stats de normalisation gelées
sequential_monitors(Z | panel, calib) -> alarms.csv    # numpy seul, aucun import torch
benchmark_runner -> results/<run_hash>.csv   # une ligne par réplication : seed, famille, D, ARL0, ADD, alarme
```

Règles de découplage :
1. Le module de surveillance n'importe jamais le code JEPA ; le module JEPA ne voit jamais injections ni alarmes.
2. Les injections traversent l'encodeur gelé, ce qui teste la transmission.
3. Quatre tests de contrat bloquent toute fusion : non-anticipation (perturber $x_{t+1:T}$ laisse $z_{1:t}$ identique bit à bit), imparité ($\|\phi(-x)+\phi(x)\|_\infty\le10^{-6}$ sur la tête impaire), déterminisme (deux exécutions, mêmes bits, BLAS mono-thread, inférence CPU), absence de statistiques de test.
4. Chaque figure lit un CSV, jamais un état en mémoire.

Raphael arbitre théorie et surveillance, José arbitre architecture et entraînement. Le protocole d'évaluation est co-signé et gelé avant P3 ; un point hebdomadaire de 30 minutes suit les jalons ; un fichier CODEOWNERS attribue chaque module. Je ne peux pas figurer comme auteur : les politiques de NeurIPS, d'ICML et de l'ACM excluent les LLM de l'autorat. Mes dérivations et mon code doivent être relus et assumés par un auteur humain, et l'usage déclaré selon la politique de la conférence.

## 5. Stratégie de publication

**Cible principale : NeurIPS 2027, main track.** L'échéance NeurIPS 2027, extrapolée du cycle 2026 en l'absence d'appel officiel, tombe autour du 21 mai 2027, résumés le 14 mai, mais l'article complet de NeurIPS 2026 était dû le 6 mai : le plan gèle donc le manuscrit le 30 avril. Cela laisse environ 30 semaines, assez pour P0–P4 et leurs jalons. La ligne éditoriale correspond au contenu : un résultat énoncé avec ses hypothèses et vérifié numériquement, une ablation qui isole la contribution de la représentation, un second domaine hors finance, un code exécutable sur données publiques. La communauté JEPA y siège, et José y a publié.

**Écartés.** ICML 2027 : la date projetée depuis le cycle 2026 est le 22 janvier 2027 pour l'article, le 16 janvier pour le résumé, soit 14,5 semaines, incompatibles avec G1 et G2. KDD 2027 : le cycle 1 est clos (résumés le 19 juillet, articles le 26 juillet 2026, notification le 14 novembre) et l'appel renvoie à une échéance de février 2027 pour le cycle 2, sans date précise. Si l'Article B est dans le cycle 1 et se voit refusé, sa resoumission naturelle est le cycle 2 : deux articles de la même équipe sur le même plancher dans le même vivier de reviewers. Février est en outre trop tôt pour G2.

**Repli.** ICLR 2028, réceptif aux travaux JEPA. L'échéance ICLR 2027 était le 24 septembre 2026 ; si 2027 suit le même calendrier, la fenêtre entre la notification NeurIPS et l'échéance ICLR sera serrée et devra être vérifiée dès la publication des dates.

**ICAIF 2027.** L'échéance tombe historiquement début août (à vérifier), pendant la revue NeurIPS : la double soumission l'exclut comme repli après NeurIPS. ICAIF est une alternative à décider au jalon G2 du 1er mars : si G1 passe et G2 échoue, la version appliquée (encodeur impair, facteurs CD-DFM, recensement EUROFIDAI) y trouve sa ligne éditoriale.

**Workshops NeurIPS.** En 2026, la date suggérée pour les contributions aux workshops était le 29 août. Un workshop non archivant reste compatible avec une soumission principale en cours, sous réserve de sa politique ; l'existence d'un workshop finance en 2027 ne se vérifiera qu'à la publication de la liste. Usage : visibilité, pas cible.

L'Article B doit être sur arXiv avant mai 2027 si la politique d'anonymat de KDD le permet. À défaut, l'Article C réénonce le plancher de façon autonome et cite l'Article B à la troisième personne.

## 6. Livrables du 12 au 25 octobre 2026

- **A1 — Note théorique v0** (LaTeX, anglais, environ 8 pages) : Propositions 1–3, lemme d'encodeur impair, critère d'absorption, preuves. Chaque énoncé est accompagné de la décision de design qu'il fixe et de la prédiction qui le réfuterait.
- **A2 — `floor_calculator.py` et validation Monte Carlo.** Le prototype de $M(D)$ est déjà validé à 4 % près ; extension au CUSUM pire cas de Lorden, aux priors mal accordés et à l'efficacité des capteurs de signe, avec CSV et figure ADD–D.
- **A3 — Notebook d'audit informationnel S&P 500** : spectre, η, corrélations de signe, test de symétrie centrale, SR de dérive débiaisé par transition Pagan-Sossounov dans trois sous-espaces (marché, K = 11 facteurs CD-DFM ou PCA, caractéristiques orthogonalisées), part des phases dans le budget. Dépendance : le panel de l'Article B ou l'univers des 239 titres de CD-DFM, avec leurs caractéristiques.
- **A4 — Squelette du dépôt**, `INTERFACE.md` et les quatre tests de contrat.
- **A5 — Pilote de l'échelle linéaire** sur fond S&P 500 symétrisé : B0, B1, B2, B3, familles F1–F3.

**Premier jalon empirique vérifiable, le 25 octobre : le test d'échappement.** Fond S&P 500 symétrisé, $N\in\{8,16,32,64,128,239\}$, dérive F2 d'amplitude calibrée pour que l'oracle détecte en environ un an à $N=239$. Trois critères falsifiables : FPR des flux de signe à ±1 point du nominal, l'exactitude étant garantie par construction, ce qui valide la chaîne ; ADD mesuré à ±15 % de la prédiction des Propositions 2–3 ; exposant $\hat\beta$ proche de 0 pour le pooling sur F3 et strictement positif, IC excluant 0, pour le PCA résiduel sur F2. Un échec sur le deuxième critère impose de réviser la théorie avant tout autre chantier.

**[Strategic Advice]**

- Livraison en Markdown dans le fil, sans Doc ni artefact, conformément à la préférence « aucun conteneur sans demande explicite ». Horodatage : seule la date est injectée, aucune heure.
- Angle mort principal : la valeur ajoutée propre du JEPA sur la localisation en finance est probablement faible. Une normalisation non apprise capte déjà 0,82 sur N1, et CD-DFM couvre une partie de N2. Les chances les plus sérieuses du JEPA se trouvent dans le tabulaire hétérogène (BAF) et les dérives de second ordre ; le plan garde les deux issues publiables pour cette raison.
- La Proposition 3 décrit le délai d'un détecteur à mélange accordé. Son statut de borne inférieure de second ordre, via la redondance de Clarke-Barron, reste à démontrer : ne pas l'énoncer comme borne dans le papier avant preuve.
- Les nombres produits ici sont reproductibles : $M(D)$ (analytique et Monte Carlo à 300 réplications), pénalité de dépassement sous GARCH (2 000 trajectoires), angles du dictionnaire, budgets de second ordre, critère d'absorption. Les scripts de travail rejoignent le dépôt avec A2. L'échelle d'efficacité (0,44 à 0,82) repose sur une volatilité log-normale avec s = 0,9 choisie pour l'illustration ; l'estimation de Phase 0 la remplacera.
- Hypothèses non vérifiées : Drive vs. Decay et TAU-JEPA (aucune trace publique repérée par mes recherches), le nombre de features de BAF, la disponibilité de caractéristiques point-in-time pour EUROFIDAI, le statut de l'Article B (supposé dans le cycle 1 de KDD 2027). Les dates NeurIPS et ICML 2027 sont des projections, pas des annonces.
- Si l'Article B est dans le cycle 1, son rebuttal passe avant A1–A5 : la période de rebuttal du cycle 1 de KDD 2027 court du 29 septembre au 13 octobre 2026.
- Branche écartée la plus coûteuse à rouvrir : TAU-JEPA comme chemin surveillé. Si José tient à ce socle, le cantonner au prétexte de pré-entraînement.