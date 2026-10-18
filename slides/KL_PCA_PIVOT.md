# LE MUR DE L'INFORMATION ET L'ÉCHAPPATOIRE MULTIVARIÉE : VERS L'ARTICLE C

## 1. Le Socle Théorique : L'Impossibilité Univariée
Pour clore l'Article B sur une vérité formelle, il faut raccorder la détection séquentielle à l'efficacité statistique classique. La borne de Lorden-Lai stipule que le délai de détection optimal d'une rupture (ADD) par un algorithme CUSUM est fondamentalement minoré par l'entropie relative :
$$ \mathrm{ADD} \sim \frac{\ln(1/\alpha)}{D_{KL}(f_1 || f_0)} $$
Pour une dérive locale ($\mu \to 0$), le développement de Taylor de cette divergence révèle le pont mathématique avec l'Information de Fisher $\mathcal{I}(0)$ (Kullback, 1959, *Information Theory and Statistics*) :
$$ D_{KL}(f_\mu || f_0) \approx \frac{\mu^2}{2} \mathcal{I}(0) $$
Basseville & Nikiforov (1993, *Detection of Abrupt Changes: Theory and Application*, Chap. 9) démontrent via cette équivalence locale que le rapport des délais minimaux de deux détecteurs séquentiels est asymptotiquement égal à leur Efficacité Relative de Pitman (ARE). 
Sur un signal gaussien univarié, le déplacement relatif $\mu / \sigma$ correspond au Ratio de Sharpe journalier, d'où le plancher informationnel terminal :
$$ \mathrm{ADD} \gtrsim \frac{504 \ln(1/\alpha)}{\mathrm{SR}^2} $$
**Conclusion à graver pour l'Article B :** Le signal univarié financier est "évanescent". Avec un $\mathrm{SR}$ annuel réaliste de l'ordre de $0.5$ à $1.0$, la physique de l'information exige des centaines voire des milliers de jours pour valider une rupture directionnelle.

## 2. Le Paradoxe du Hedge Fund (Pivot Pragmatique)
Face à ce mur, l'intuition première consiste à chercher des paires ou combinaisons linéaires d'actifs qui, par cointégration, généreraient un $\mathrm{SR}$ de 3 ou 4 sur le jeu d'entraînement. 
**Le piège de l'efficience :** C'est une impasse épistémologique. Dégager hors-échantillon un ratio de Sharpe de 3 sur des actifs réels revient à "résoudre le marché" (c'est la performance du fonds Medallion). Si un tel signal existait, les arbitragistes le détruiraient instantanément. Chercher à sauver un modèle de Concept Drift en développant le modèle de trading quantitatif ultime est hors de portée et hors sujet.
**La porte de sortie :** Rien ne nous oblige à construire des combinaisons qui soient *tradables*. Les coûts de transaction, les contraintes de liquidité et le bid-ask bounce détruisent les Sharpe réels, mais un détecteur mathématique s'en moque. Nous pouvons projeter nos données dans un **espace latent**, non investissable, dont le seul but est de concentrer la divergence de Kullback-Leibler pour réveiller le CUSUM.

## 3. Divergence Multivariée et Protocole PCA
Dans un univers à $N$ dimensions, la divergence de KL pour une translation de moyenne $\Delta\boldsymbol{\mu}$ sous matrice de covariance $\Sigma$ s'écrit :
$$ D_{KL} = \frac{1}{2} \Delta\boldsymbol{\mu}^T \Sigma^{-1} \Delta\boldsymbol{\mu} $$
**Condition de succès :** La matrice $\Sigma$ des actions est extrêmement mal conditionnée. Sa valeur propre dominante (PC1, le marché) écrase toutes les autres. L'inversion $\Sigma^{-1}$ anéantit donc mathématiquement tout signal directionnel $\Delta\boldsymbol{\mu}$ qui serait parallèle au marché.
Pour abaisser drastiquement le plancher $\mathrm{ADD}$, le signal doit résider dans l'espace orthogonal à la variance dominante. D'où le protocole opérationnel :

1. **Extraction :** Sur une fenêtre d'étalonnage, calculer $\hat{\Sigma} = V \Lambda V^T$.
2. **Isolement du bruit macro :** Extraire la première composante principale $v_1$ (qui capture typiquement $\eta \approx 80\%$ à $90\%$ de la variance du système).
3. **Le filtrage spatial :** ON JETTE $v_1$. Le marché global est un générateur de *Data Drift* (chocs de volatilité), pas de *Concept Drift* directionnel exploitable. 
4. **Surveillance :** Appliquer le pipeline CONCEPT binarisé sur les projections des séries dans l'espace résiduel $(I - v_1 v_1^T)\mathbf{R}_t$.

## 4. Dérivation Rigoureuse du Gain PCA (Le Nouveau Plancher)
Soit la variance totale initiale $\sigma_{tot}^2$ et la norme d'une dérive d'origine $\|\Delta\boldsymbol{\mu}\|^2$. Le Sharpe introuvable d'origine au carré s'écrit $\mathrm{SR}_{orig}^2 = \frac{\|\Delta\boldsymbol{\mu}\|^2}{\sigma_{tot}^2}$.
Après rejet de PC1, la nouvelle variance résiduelle n'est plus que $\sigma_{res}^2 = (1-\eta) \sigma_{tot}^2$.
Toutefois, la dérive directionnelle perd également de l'énergie. Soit $\gamma \in (0, 1]$ la fraction d'énergie directionnelle préservée (c'est-à-dire non alignée avec le marché) : $\|\Delta\boldsymbol{\mu}_{res}\|^2 = \gamma \|\Delta\boldsymbol{\mu}\|^2$.

Le Sharpe du système résiduel projeté devient :
$$ \mathrm{SR}_{res}^2 = \frac{\gamma \|\Delta\boldsymbol{\mu}\|^2}{(1-\eta) \sigma_{tot}^2} = \left( \frac{\gamma}{1-\eta} \right) \mathrm{SR}_{orig}^2 $$
Le gain sur le multiplicateur de divergence est $G = \frac{\gamma}{1-\eta}$.

**Évaluation Optimiste (Orthogonalité pure) :**
Si la dérive était purement idiosyncratique ($\gamma = 1$) sous une dominance de marché $\eta = 0.9$ : $G = 1 / 0.1 = 10$. Le plancher d'ADD univarié serait divisé par 10.

**Évaluation Réaliste (Hybridation) :**
Comme souligné par mon expérience quantitative, un choc de régime (macro/sectoriel) contamine fortement l'axe de marché. Admetmons que $50\%$ de la translation d'origine soit absorbée et détruite avec PC1 ($\gamma = 0.5$).
Le gain multiplicateur devient $G = \frac{0.5}{0.1} = 5$.
Le nouveau plancher informationnel s'établit à :
$$ \mathrm{ADD}_{PCA} \gtrsim \frac{504 \ln(1/\alpha)}{5 \times \mathrm{SR}_{orig}^2} $$

**L'Ordre de Grandeur (Sharpe Cible) :**
Objectif : Détecter une rupture structurelle en 60 jours, avec $5\%$ de fausses alarmes ($\ln(1/0.05) \approx 3$).
- *Dans le monde univarié :* L'exigence serait de $\mathrm{SR}_{orig} = \sqrt{\frac{504 \times 3}{60}} \approx 5.0$. Totalement impossible (ceci justifie la clôture de l'Article B).
- *Dans l'espace latent multivarié (gain $G=5$) :* Le besoin chute à un Sharpe "brut" de :
$$ \mathrm{SR}_{orig} = \frac{5.0}{\sqrt{5}} \approx 2.24 $$
Un Sharpe d'origine autour de $2.2$ pour des anomalies sectorielles non tradables est élevé, mais physiquement modélisable. L'espace orthogonal fait basculer la détection de "mathématiquement impossible" à "atteignable sous conditions idiosyncratiques".