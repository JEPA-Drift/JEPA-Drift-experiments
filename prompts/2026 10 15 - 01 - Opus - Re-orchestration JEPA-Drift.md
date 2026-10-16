## TACHE

Rédige un plan d'orchestration détaillé mis à jour en prenant en compte les éléments suivants:
1. Corrige les éventuelles erreurs que tu aurais identifiées en rédigeant les prompts d'orchestration.
2. Conserve le contenu exhaustif théorique et des expériences que tu avais identifié initialement. Tu dois seulement prioriser le déroulement, pas diminuer la cible de travail. Le travail sera éventuellement raccourci si nécessaire si une deadline approche.
3. Je souhaite que l'article s'ouvre (après l'abstract) en présentant concrètement le problème posé par le plafond de sharpe. Il faut donc commencer par exposer la formule du plafond de sharpe. Il faut ensuite exposer de façon claire, simple et précise l'objectif recherché par la méthode proposée qui consiste à trouver un espace de représentation permettant de maximiser la divergence de Kullback-Leibler (les données avant drift / après drift) c'est à dire une représentation permettant de capturer une amplitude élevée avec une covariance minimale. Immédiatement après, avant de commencer les dérivations théoriques détaillées, il faut présenter le problème concret auquel on est confronté lorsqu'on cherche à détecter des drifts sur des données financières réelles. Dans cette présentation, il faut exposer les valeurs des performances de détection obtenues sur des données financières réelles (les séries d'actifs financiers seront ensuite éventuellement complétées ensuite avec des données BAF mais ce n'est pas une priorité) avec les pipelines suivants:
   1. avec le pipeline standard sur un actif.
   2. avec le pipeline standard sur plusieurs actifs en exposant le nombre d'actifs effectifs avec la corrélation comme dans l'article `TheWhiteningAdvantage`.
   3. en utilisant un pipeline modifié qui utilise une PCA.
   Dans cette présentation concrète du problème, il faudra quantifier le gain en performance obtenu à chaque amélioration de pipeline **1.** -> **2.** -> **3.** (pipeline standard mono actif puis pipeline standard multi actifs puis représentation latente PCA).
4. Le développement des dérivations théoriques détaillées, qui peuvent comprendre la formalisation de l'objectif à atteindre avec la représentation (maximisation de la divergence de Kullback-Leibler) et l'éventuel rapprochement avec l'article de C-A Lehalle *"The Fundamental Structure of Risk: From Characteristics to Covariance"* `2607.24410v1.pdf` peuvent être réalisé ensuite.

## CONTRAINTES DE PRESENTATION DU PLAN D'ACTION ET DE L'ARTICLE

Je souhaite que dans ton plan d'action puis dans la rédaction de l'article tu présentes très clairement les éléments suivants (ils pourront être complétés au fil de l'eau). Ces éléments (au moins les 2 premiers) devront être synthétisés dans un tableau au début de l'article.
**1. Les datasets et leur représentation latente:**
   1. Nom/référence du dataset.
   2. Si le dataset est réel ou synthétique.
   3. Brève description du dataset (si synthétique: brève description de la méthode de génération qui pourra être avec détaillée dans le corps de l'article ou en annexe).
   4. Représentation latente des données utilisée: aucune / PCA / JEPA.
   5. Si représentation latente des données préciser brièvement si un sous-ensemble de la représentation latente est conservé, c'est à dire: SI PCA -> quels PCs conservés, SI JEPA -> fine-tuning, compression par dropout, pré-selection des données (ex: Probing/Lasso) etc. 
**2. Les pipelines utilisés:**
   1. Nom/référence du pipeline
   2. Pipeline de *data drift* ou de *concept drift*.
   3. Le drift utilisé est-il réel ou synthétique ?
   4. Mesure "ground truth" du drift: si drift réel -> préciser en quelques mots comment il est détecté (les détails pourront être fournis dans le corps de l'article); si drift synthétique -> préciser comment il a été généré (plus de détails pourront être fournis dans le corps de l'article ou en annexe).
   5. Les données utilisées: description des *features* (prix ? rendements ? features calculées ?) pour *data drift* et des *features+cibles* pour un pipeline de *concept drift*.
   6. Le classifieur utilisé (si pipeline de *concept drift*).
   7. Le détecteur utilisé (famille et détail).
**3. La configuration expérimentale complète: dataset (1.) x pipeline (2.).** Cette configuration doit être clairement exposée AVANT chaque expérience ou chaque nouvelle dérivation théorique. Elle pourra aussi éventuellement faire l'objet d'une présentation dans une liste ou dans un (troisième) tableau synthétique en début d'article. Dans le corps de l'article, avec éventuellement des détails en annexes, il faudra décrire précisément comment s'articule l'utilisation des datasets (**1.**) avec les pipelines (**2.**) si cela n'est pas évident.
