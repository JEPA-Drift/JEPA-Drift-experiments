# DIRECTIVE THÉORIE — Article C §3 et Annexe A, audit de validité et preuves

**Destinataire : Codex / co-auteur théorique ; ne pas attribuer automatiquement à un stream de code existant.** Créer un plan/GO distinct avant tout changement de `paper/sec3_theory.tex` et `paper/appA_proofs.tex`. Le mandat est de corriger des énoncés sous hypothèses, non de réécrire l'article pour correspondre aux résultats favorables.

## Contexte

L'Article C s'appuie sur une hiérarchie de l'information de localisation, une calibration exacte conditionnelle, un budget d'évidence, une taxe dimensionnelle sous mélange et une proposition d'absorption. Un audit scientifique révèle quatre risques : faire du budget exact `ln gamma / I` une borne universelle du délai à ARL fini ; traiter un mélange isotrope comme valable sur de simples signes marginalement équilibrés ; présenter une dimension optimale entre 2 et 8 comme conséquence nécessaire de la covariance ; présenter la KL d'une tête non linéaire comme exactement égale à une demi-distance de Mahalanobis.

## Tâche

1. **Audit des énoncés existants** : relever dans les deux `.tex` chaque proposition/lemme, hypothèses mesurables, espace probabilisable, état observé et type de conclusion (identité, borne, approximation brownienne, heuristique fluide). Construire une table « phrase actuelle → condition manquante → correction ». Ne pas renuméroter les théorèmes sans cartographie de références.
2. **Budget non asymptotique** : formaliser pour une e-surmartingale positive `E_t` lancée à l'onset, `T_gamma=inf{t:E_t>=gamma}`, la propriété `E_1[sum_{t<=T} I_t]>=ln gamma` sous absolue continuité, intégrabilité et arrêt optionnel appropriés. En déduire `E_1[T]>=504 ln gamma / SR²` seulement pour dérive gaussienne homoscédastique et information constante. Séparer de `ARL0=gamma` : dans la diffusion CUSUM réfléchie, `E0T_h=(e^h-h-1)/I`, `E1T_h=(h-1+e^-h)/I`, et `Phi(gamma I)` est une **approximation du discret**, non une formule exacte pour un CUSUM discret à gamma fini.
3. **DPI et covariables** : si `Z_t=phi(X_t,C_t)`, ne pas écrire `I_z<=I_x` en omettant la distribution/information de `C`. La version non ambiguë est `I_z <= I_(X,C)` ; `I_z<=I_x` peut être donnée sous exogénéité et interprétation conditionnelle identifiée de `X` sachant `C`. Vérifier que toutes les expériences comparent le même jeu informationnel accessible.
4. **Fisher après encodage non linéaire** : pour modèle de localisation régulier `f(x-mu)`, `J_x >= Sigma_x^-1`; le score latent est `s_z(z)=E[s_x(X)|Z=z]` avec `J_z<=J_x`. Si `D_z=E[(Z-m_z)s_x(X)^T]`, prouver `D_z^T Sigma_z^-1 D_z <= J_z`, donnant un proxy de Sharpe tangent `SR_z,tan²=252 delta^T D_z^T Sigma_z^-1 D_z delta`. Ne pas assimiler un décalage de `X` à un décalage de translation de `Z` lorsque `phi` est non linéaire ; refuser toute `KL_z > KL_(X,C)` comme « gain d'information ».
5. **Dimension optimale** : sous modèle gaussien fixé, spectre d'information marginal `q_k=(v_k^T Delta)^2/(2 sigma_k)`, `I(d)=sum_{k<=d}q_k`. Pour taxe affine **explicitement heuristique** `L(d)=A+cd`, `A=ln gamma`, `c=(1+ln A)/2>0`, calculer `V(d+1)>V(d) iff q_(d+1)>c I(d)/(A+cd)` ; si `q_k` strictement décroissants, `H_1>0`, `H_8<0` et aucun `H_d` nul pour `N>=9`, montrer un unique maximum strict dans `[2,8]`. Introduire deux contre-exemples `Delta || v_1` => d*=1 ; `Delta || v_N` => d*=N pour ordre fixe. La décroissance de `sigma_k` seule ne prouve RIEN sur d*. Préciser que pour des JEPA réentraînés indépendamment en dimensions différentes, les espaces ne sont pas emboîtés, donc la formule additive sur les mêmes `q_k` ne s'applique pas en l'état.
6. **Taxe isotrope réellement démontrée** : sous `Z_t | H0 ~ N(0,I_D)`, mélange gaussien `L_n=(1+n s²)^(-D/2) exp(s²||S_n||²/[2(1+n s²)])`. Pour `s²=2I/D` (choix oracle qui suppose I connu), montrer `E1 log L_n=x-(D/2)log(1+2x/D)`, `x=nI`. Le `x*=A+(D/2)log(1+2x*/D)` est une approximation *fluid crossing*, pas l'ADD exact ni un seuil composite universel. Pour `D>>A`, `x*~sqrt(AD)` et `M~sqrt(D/A)`. Reproduire le tableau D=1,2,4,8,16,64,128,500 à gamma=504 à tolérance numérique définie et réserver `FPR(H)`/ARL aux calibrations effectives.
7. **Validité multicanale** : démontrer l'exactitude univariée des signes `sgn(g_t(X_t))` pour `g_t` impair sous symétrie centrale conditionnelle, avec pièces indépendantes aux égalités. Fournir un contre-exemple où chaque bit marginal est Bernoulli(1/2) mais les bits de deux canaux sont parfaitement corrélés. Le mélange gaussien multidimensionnel nécessite le contrôle de la MGF **jointe**, non les seules marges.
8. **Facteur et largeur** : préciser conditions de rang pour `Sigma=B Sigma_F B^T+Psi` et décomposer `Delta^T Sigma^-1 Delta` en terme factoriel borné et largeur GLS ; produire `N^0`, `N^(1/2)`, `N^1` comme scénarios **conditionnels de gains** pré-saturation, pas lois universelles de tout portefeuille ou JEPA. Respecter saturation d'un délai discret >=1 jour.
9. **Covariance et absorption** : KL gaussienne de covariance `0.5[tr(Sigma0^-1 Sigma1)-logdet(Sigma0^-1 Sigma1)-N]`; séparer la puissance du capteur de l'information présente. Sous absorption `I_t=I0 exp(-2(t-1)/tau_a)`, calculer exactement le budget discret `I0/(1-exp(-2/tau_a))`, distinct du budget intégral `I0 tau_a/2`. Énoncer comme **condition suffisante de non-détection certaine impossible** : si la KL totale de trajectoire est <`ln gamma` et `P0(T<inf)<=1/gamma`, alors `P1(T<inf)<1` (DPI sur indicatrice de l'alarme). Ne pas écrire que l'échec est presque sûr ou que tout encodeur online suit l'exponentielle.
10. **Documentation** : mise à jour cohérente figures/diapos/audit, renvois, hypothèses et éventuel erratum du texte « Siegmund–Yakir » si sa forme n'est pas dérivée d'un détecteur identifié. Inclure références vérifiées et identifiants bibliographiques réellement présents, sans DOI ou URL fabriqués. Ne pas réutiliser directement les chiffres exploratoires E6/E10 comme démonstrations de théorème.

## Entrées

`paper/sec3_theory.tex`, `paper/appA_proofs.tex`, `jepadrift/floors.py`, `J1_report.md`, `handover-01-27.md`, `DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26.md`, et le manuscrit de l'Article B comme antériorité. L'audit scientifique précédent sert de proposition de preuve, pas de preuve éditée sans relecture.

## Livrables

Diff LaTeX minimal, annexes avec preuves complètes et hypothèses, table de traçabilité des corrections, petits tests numériques reproductibles pour les valeurs `M(D,gamma)` et le cas Student t7 `J sigma²=1.12`, compilation du document si chaîne LaTeX disponible, et note pour la rédaction des §1/§4/limitations. Tests de cohérence des références et zéro citation inventée.

## Contraintes techniques

Toute assertion finie doit être prouvée sous ses hypothèses exactes ; sinon la qualifier asymptotique ou heuristique. Pas d'expérience ou de changement J4 piloté par la théorie révisée après gel. Aucune modification d'Article B en lecture seule. Édition de papier en anglais selon style `CLAUDE.md`, GO et compte rendu en français, wrapup en anglais.

## Critères de succès

Les bornes et approximations ne sont plus confondues, la DPI s'applique à l'information vraiment observée, les formules de mélange restent conditionnelles, aucun optimum compact n'est déclaré universel, et la section théorie reste autoportante et vérifiable. Un énoncé non prouvable sous hypothèses disponibles est retiré ou transformé en conjecture explicitement nommée.

## Commandes de vérification

```bash
cd "$(git rev-parse --show-toplevel)"  # dans le worktree de ce stream déjà ouvert par Codex
.venv/bin/python -m pytest -q -rs tests/test_floors.py
.venv/bin/make check
# Si une cible de compilation LaTeX existe, l'exécuter dans une copie temporaire
# pour éviter toute modification parasite des artefacts du dépôt.
```

Le plan doit identifier le test des formules réellement disponible avant de lancer cette commande ; si `tests/test_floors.py` n'existe pas, créer un test dédié explicitement nommé et le renseigner dans le wrapup.
