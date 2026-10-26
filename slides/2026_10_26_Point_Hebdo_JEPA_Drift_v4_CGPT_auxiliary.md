# JEPA-Drift — Point Hebdo v4_CGPT — StarMath blocks (référence manuelle)

Ce fichier contient les blocs StarMath extraits du Markdown source.
Ils ne sont PAS affichés sur les diapositives. Ils servent au remplacement
manuel ultérieur des équations ASCII dans PowerPoint.

---

## Slide 3 — Données : matrices et caractéristiques disponibles

**ASCII :** `beta_i(t) = Cov(r_i, r_m | [t-252,t)) / Var(r_m | [t-252,t))`


---

## Slide 6 — Absorption : pourquoi figer l'encodeur

**ASCII :** `I_t = I_0 * exp[-2*(t-1)/tau_a] ; B_total = I_0 / (1-exp[-2/tau_a])`


---

## Slide 7 — Data drift, concept drift et deux sorties de moniteurs

**ASCII :** `q_t = [somme(k dans residuels, z_k(t)^2) - d_R] / sqrt(2*d_R)`


---

## Slide 8 — Covariance régularisée et axes : ce que calcule l'ACP

**ASCII :** `Sigma_LW = (1-delta)*Sigma_emp + delta*mu*Id ; mu = trace(Sigma_emp)/N`


---

## Slide 9 — Pipeline ACP calé sur les segments temporels

**ASCII :** `FPR(H) = P_sans_changement(T_alarme <= H) ; gamma_H = H / alpha`


---

## Slide 10 — Comment et pourquoi choisir la dimension ACP ?

**ASCII :** `R = D^(-1/2)*Sigma_emp*D^(-1/2) ; lambda_plus = [1+sqrt(N/T)]^2`


---

## Slide 11 — KL et pipeline ACP : ce qui a été calculé

**ASCII :** `KL(P1||P0) = E_P1[log(p1(X)/p0(X))] ; I_k = (v_k' * Delta)^2 / (2*lambda_k)`


---

## Slide 12 — Symétrie des signes : essais entièrement définis

**ASCII :** `P0(b_t=1 | F_(t-1)) = 1/2`


---

## Slide 13 — Covariance : rotation, étalon et niveau nul

**ASCII :** `G_250 = moyenne[min(T_indice,250)] / moyenne[min(T_ACP,250)]`


---

## Slide 14 — Normalisation transversale sans réseau

**ASCII :** `p_t = r_t - b*(b'*r_t) ; z_t = U'*p_t / ||p_t|| (si ||p_t||>0)`


---

## Slide 15 — Coût et information : expérience théorique complète

**ASCII :** `V(d) = [I(d)/I(500)] / M(d,504) ; x_d = ln(504) + (d/2)*ln(1+2*x_d/d) ; M(d,504) = x_d/ln(504)`


---

## Slide 16 — Critère de dimension optimale conditionnel

**ASCII :** `V(d+1)>V(d) <=> q_(d+1) > I(d)*[C(d+1)/C(d)-1]`


---

## Slide 18 — Masking et anti-collapsus : pipeline JEPA sans fuite

**ASCII :** `L_var = (1/d)*somme(j=1..d, max(0,1-sd_batch(Z_j))^2)`


---

## Slide 19 — JEPA : protocole réel/synthétique et choix avant le test

**ASCII :** `G_H = E[min(T_reference,H)] / E[min(T_methode,H)]`


---

## Slide 21 — A1. Saturation de la moyenne corrélée

**ASCII :** `Var(m) = [K*s2 + K*(K-1)*rho*s2]/K^2 = s2*[rho+(1-rho)/K]`


---

**ASCII :** `K_eff = K/[1+(K-1)*rho] ; lim(K_eff)=1/rho ; lim(gain_sd)=1/sqrt(rho)`


---

## Slide 22 — A2. Budget d'évidence exact

**ASCII :** `log(gamma) <= E1[log(E_T)] <= E1[log(Lambda_T)] = E1[somme(t<=T,I_t)]`


---

**ASCII :** `E1[T] >= log(gamma)/I = 504*log(gamma)/SR^2`


---

## Slide 23 — A2 bis. Trois délais, un même modèle gaussien

**ASCII :** `I = SR^2/(2*252) ; tau_evidence = log(gamma)/I`


---

## Slide 24 — A3. Diffusion réfléchie : dérivation

**ASCII :** `I*v_mu''(y) + mu*v_mu'(y) = -1 ; v_mu'(0)=0 ; v_mu(h)=0`


---

**ASCII :** `ADD_brownian = [h-1+exp(-h)]/I ; ARL0_brownian = [exp(h)-h-1]/I`


---

## Slide 25 — A4. Caractéristiques quotidiennes : formules

**ASCII :** `vol_i(t) = sqrt[somme(s dans W63,(r_i(s)-moyenne_W63(r_i))^2)/nombre(W63)]`


---

**ASCII :** `mom_i(t) = somme(s=t-252..t-22, r_i(s)) ; rev_i(t) = somme(s=t-21..t-1, r_i(s))`


---

**ASCII :** `char_rang_i(t) = rang_t(i)/n_valides(t) - 0.5`


---

## Slide 26 — A5. Covariance et rétrécissement : formule

**ASCII :** `Sigma_emp = (1/T)*somme(t=1..T,(r_t-r_bar)*(r_t-r_bar)')`


---

**ASCII :** `Sigma_LW = (1-delta)*Sigma_emp + delta*(trace(Sigma_emp)/N)*Id ; z_k(t)=v_k'*r_t/sqrt(lambda_k)`


---

## Slide 27 — A5 bis. Corrélation et seuil MP

**ASCII :** `R_ij = Sigma_emp_ij / sqrt(Sigma_emp_ii*Sigma_emp_jj) ; n_above = nombre{lambda_j(R) > (1+sqrt(N/T))^2}`


---

## Slide 28 — A6. KL d'un déplacement gaussien

**ASCII :** `ell(x) = Delta'*Sigma^(-1)*x - Delta'*Sigma^(-1)*Delta/2`


---

**ASCII :** `I_full = Delta'*Sigma^(-1)*Delta/2 = somme(k=1..N, (v_k'*Delta)^2/(2*lambda_k))`


---

## Slide 29 — A6 bis. Inégalité de traitement des données

**ASCII :** `KL(P1_X||P0_X) = KL(P1_Z||P0_Z) + E_(Z~P1)[KL(P1_(X|Z)||P0_(X|Z))] >= KL(P1_Z||P0_Z)`


---

## Slide 30 — A7. Symétrie conditionnelle et signes exacts

**ASCII :** `P0(b_t=1 | F_(t-1)) = (1-p0)/2 + p0/2 = 1/2`


---

**ASCII :** `P0(b_1=c_1,...,b_n=c_n) = 2^(-n)`


---

## Slide 31 — A7 bis. Calibrer un treillis fini et analyser l'asymétrie

**ASCII :** `FPR_observee = somme(rep=1..R, 1{T_rep<=H})/R ; q_hat = somme(t=1..941,1{z_t>0})/941`


---

## Slide 32 — A8. Energie gaussienne et rotations

**ASCII :** `q = [somme(k=1..d_R,Z_k^2)-d_R] / sqrt(2*d_R)`


---

**ASCII :** `KL_cov = [trace(Sigma0^(-1)*Sigma1) - log(det(Sigma0^(-1)*Sigma1)) - N]/2`


---

## Slide 33 — A8 bis. Transformations et comparateur unilatéral

**ASCII :** `Var(m) = a'*Sigma*a ; Var(m_new)=a'*M*Sigma*M'*a`


---

## Slide 34 — A9. Décomposition degré zéro et signes

**ASCII :** `P=Id-b*b' ; p=P*r ; z=U'*p/||p|| ; z(a*r)=z(r) (a>0)`


---

## Slide 35 — A10. Mélange gaussien : intégration détaillée

**ASCII :** `L_n = integrale exp[u'*S_n - n*||u||^2/2] dNormal(u;0,s^2*Id)`


---

**ASCII :** `u'*S_n - a*||u||^2/2 = -a*||u-S_n/a||^2/2 + ||S_n||^2/(2*a)`


---

## Slide 36 — A10 bis. Formule fermée du mélange

**ASCII :** `L_n = (1+n*s^2)^(-d/2) * exp[s^2*||S_n||^2/(2*(1+n*s^2))]`


---

## Slide 37 — A11. Espérance et budget fluide

**ASCII :** `E1[||S_n||^2] = 2*n^2*I + n*d ; x=n*I`


---

**ASCII :** `E1[log(L_n)] = x-(d/2)*log(1+2*x/d) ; x_d = A+(d/2)*log(1+2*x_d/d)`


---

## Slide 38 — A11 bis. Valeurs de V calculées

**ASCII :** `I(d) = somme(k=1..d,1/k) ; r(d)=I(d)/I(500) ; V(d)=r(d)/M(d,504)`


---

## Slide 39 — A12. Critère marginal d'optimalité

**ASCII :** `V(d+1)-V(d) = [q_(d+1)*C(d) - I(d)*(C(d+1)-C(d))]/[C(d)*C(d+1)]`


---

## Slide 40 — A12 bis. Unicité conditionnelle avec coût affine

**ASCII :** `H_d=q_(d+1)*(a+c*d)-c*I(d) ; H_(d+1)-H_d=[q_(d+2)-q_(d+1)]*[a+c*(d+1)] < 0`


---

## Slide 41 — A13. Dictionnaire et alignement

**ASCII :** `L = somme(j=1..K,L_j)/K >= L_j/K ; I_u = I*cos(angle)^2`


---

**ASCII :** `temps_budget ≈ [log(gamma)+log(K)] / [I*cos(angle)^2]`


---

## Slide 42 — A14. Absorption : calcul discret

**ASCII :** `I_t=I_0*exp[-2*(t-1)/tau_a] ; B_total=somme(t>=1,I_t)=I_0/[1-exp(-2/tau_a)]`


---

## Slide 43 — A14 bis. DPI et non-détection certaine

**ASCII :** `B_total >= KL(P1||P0) >= kl(P1(A_event)||P0(A_event)) ; P1(A_event)=1 implique B_total>=log(gamma)`


---

## Slide 44 — A14 ter. Modèle continu de temps fluide

**ASCII :** `B(t) = I_0*tau_a*[1-exp(-2*t/tau_a)]/2 ; t = -(tau_a/2)*log(1-2*tau_0/tau_a)`


---

## Slide 45 — A15. Fuite de cible et masquage JEPA

**ASCII :** `dp_i/dr_j = -1/N (i != j) ; m_V = somme(i dans V,r_i)/taille(V)`


---

## Slide 46 — A15 bis. Perte JEPA, variance des sorties

**ASCII :** `L_JEPA = moyenne(i dans M, ||h_hat_i-h_target_i||^2) ; L = L_JEPA + lambda_v*L_var`


---

**ASCII :** `L_var=(1/d)*somme(j=1..d,max(0,1-sd_batch(Z_j))^2)`


---

## Slide 47 — A16. Combinaison des moniteurs et contrôle de fausse alarme

**ASCII :** `M_t = somme(k=1..K, M_k,t)/K ; P0(T<=H) <= H/gamma`


---

## Slide 48 — A16 bis. Effets de censure, FPR, RMST

**ASCII :** `ARL0=E0[T] ; FPR(H)=P0(T<=H) ; RMST_H=E1[min(T,H)]`


---
