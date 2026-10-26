# JEPA-Drift — Point Hebdo v3 — StarMath blocks (référence manuelle)

Ce fichier contient les blocs StarMath extraits du Markdown source.
Ils ne sont PAS affichés sur les diapositives. Ils servent au remplacement
manuel ultérieur des équations ASCII dans PowerPoint.

---

## Slide 3 — Les données observées

**ASCII :** `r(i,t) = ln[P(i,t) / P(i,t-1)]`


---

## Slide 7 — Pourquoi la moyenne plafonne

**ASCII :** `gain_limite_sur_ecart_type = 1 / sqrt(rho)`


---

## Slide 8 — L'intuition géométrique de l'ACP

**ASCII :** `score_k(t) = projection_sur_axe_k(t) / echelle_k`


---

## Slide 11 — Variance et information ne sont pas la même chose

**ASCII :** `information_axe = deplacement_moyen^2 / (2 * variance_axe)`


---

## Slide 14 — Une référence sans réseau

**ASCII :** `residu = rendements - composante_marche`


---

## Slide 15 — Deux mécanismes, deux objets

**ASCII :** `eta = moyenne(sigma^2) * moyenne(1/sigma^2) >= 1`


---

## Slide 16 — Le coût de chercher une direction

**ASCII :** `efficacite(d) = information_conservee(d) / cout(d)`


---

## Slide 20 — Évaluer le réseau

**ASCII :** `impaire(r) = [g(r) - g(-r)] / 2`


---

## Slide 21 — La prochaine comparaison décisive

**ASCII :** `G_H = moyenne[min(T_reference,H)] / moyenne[min(T_methode,H)]`


---

## Slide 22 — Variance d'une moyenne corrélée

**ASCII :** `Var(m) = [K*s^2 + K*(K-1)*rho*s^2]/K^2 = s^2*[rho + (1-rho)/K]`


---

**ASCII :** `K_eff = K/[1+(K-1)*rho] ; limite(K_eff) = 1/rho ; limite(gain_ecart_type) = 1/sqrt(rho)`


---

## Slide 23 — Information par axe et perte par projection

**ASCII :** `y_k = v_k' * r ; delta_k = v_k' * Delta ; ell_k = delta_k*y_k/lambda_k - delta_k^2/(2*lambda_k)`


---

**ASCII :** `I_k = E_apres[ell_k] = delta_k^2/(2*lambda_k) ; I(d) = somme(k=1..d, I_k)`


---

**ASCII :** `KL(P1_X,P0_X) = KL(P1_Z,P0_Z) + E_P1_Z[KL(P1_X_sachant_Z,P0_X_sachant_Z)] >= KL(P1_Z,P0_Z)`


---

## Slide 24 — Le potentiel lié à la volatilité

**ASCII :** `A = Delta' * Sigma_0^(-1) * Delta / 2 ; I_conditionnelle = A*E[1/sigma^2] ; I_reference = A/E[sigma^2]`


---

**ASCII :** `eta = I_conditionnelle/I_reference = E[sigma^2]*E[1/sigma^2] >= (E[sigma*(1/sigma)])^2 = 1`


---

## Slide 25 — Intégrer un mélange de directions

**ASCII :** `S_n = somme(t=1..n, z_t) ; L_n = integrale exp(u'*S_n - n*norme(u)^2/2) dPi(u)`


---

**ASCII :** `u'*S_n - a*norme(u)^2/2 = -a*norme(u-S_n/a)^2/2 + norme(S_n)^2/(2*a)`


---

**ASCII :** `L_n = (1+n*s^2)^(-d/2) * exp[s^2*norme(S_n)^2 / (2*(1+n*s^2))]`


---

## Slide 26 — Du mélange au budget

**ASCII :** `E[norme(S_n)^2] = 2*n^2*I + n*d ; E[ln(L_n)] = -(d/2)*ln(1+n*s^2) + s^2*(2*n^2*I+n*d)/(2*(1+n*s^2))`


---

**ASCII :** `E[ln(L_n)] = x - (d/2)*ln(1+2*x/d) ; x_d - (d/2)*ln(1+2*x_d/d) = A`


---

**ASCII :** `x_4/I(4) < x_500/I(500) si et seulement si I(4)/I(500) > x_4/x_500 = 0.162775...`


---

## Slide 27 — Critère de dimension optimale

**ASCII :** `V(d+1)-V(d) = [q_(d+1)*C(d) - I(d)*(C(d+1)-C(d))]/[C(d)*C(d+1)]`


---

**ASCII :** `H_d = q_(d+1)*C(d) - c*I(d) ; H_(d+1)-H_d = [q_(d+2)-q_(d+1)]*C(d+1) < 0`


---

## Slide 28 — Exactitude des signes

**ASCII :** `P[b_t=1 sachant F_(t-1)] = (1-p_0)/2 + p_0/2 = 1/2`


---

**ASCII :** `P[b_1=c_1,...,b_n=c_n] = P[b_1=c_1,...,b_(n-1)=c_(n-1)]/2 = 2^(-n)`


---

## Slide 29 — Information d'un changement de covariance

**ASCII :** `ell(r) = [ln(det(Sigma_0)/det(Sigma_1)) + r'*(Sigma_0^(-1)-Sigma_1^(-1))*r]/2`


---

**ASCII :** `E_1[r'*B*r] = trace(B*Sigma_1) ; KL = [trace(Sigma_0^(-1)*Sigma_1)-ln(det(Sigma_0^(-1)*Sigma_1))-N]/2`


---

**ASCII :** `Sigma_1 = R*Sigma_0*R' ; R'*R = Id ; det(Sigma_1) = det(Sigma_0)`


---

## Slide 30 — Construction de la tâche JEPA

**ASCII :** `m_visible(t) = somme(i dans V, r(i,t)) / nombre(V)`


---

**ASCII :** `r_visible - moyenne_toutes_actions = r_visible - [somme_visible + somme_masquee]/N`


---

## Slide 31 — Budget et premier franchissement

**ASCII :** `I*v_mu''(y) + mu*v_mu'(y) = -1 ; v_mu'(0) = 0 ; v_mu(h) = 0`


---

**ASCII :** `v_-I'(y) = [1-exp(y)]/I ; v_+I'(y) = [exp(-y)-1]/I`


---

**ASCII :** `temps_avant_fausse_alarme = [exp(h)-h-1]/I ; delai_apres_changement = [h-1+exp(-h)]/I`


---

## Slide 32 — Absorption d'un changement

**ASCII :** `I_t = I_0*exp(-2*(t-1)/tau_a) ; B = somme(t>=1,I_t) = I_0/[1-exp(-2/tau_a)]`


---

**ASCII :** `B(t) = I_0*tau_a*[1-exp(-2*t/tau_a)]/2 ; t = -(tau_a/2)*ln(1-2*tau_0/tau_a)`


---

**ASCII :** `A <= E_1[ln(Q_T)] = E_1[ln(Q_T/Lambda_T)] + E_1[ln(Lambda_T)] <= B < A`


---

## Slide 33 — Nombre et orientation des directions candidates

**ASCII :** `L = somme(j=1..K,L_j)/K >= L_j/K ; L_j >= K*gamma implique L >= gamma`


---

**ASCII :** `I_projection = (u'*theta)^2/2 = I*cos(angle)^2 ; budget_jours = [A+ln(K)]/[I*cos(angle)^2]`


---
