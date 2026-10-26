# Point hebdo 2026-10-26 v4_CGPT — render check

## Executed structural checks

- Reopened the exported PPTX with python-pptx: 48 slides, ordered 1-48; 20 main slides and 28 annexes.
- Dimensions: 10.00 × 5.62 inches, ratio 1.77936; the canonical template's rounded 16:9 format.
- Equations: 55 ASCII formulas displayed as monospace text with their 'Lecture' explanations. No LaTeX or bitmap rendering.
- Hyperlinks: 8 external relationships, checked against source references on each slide; clickable reference runs embedded in content.
- All 48 speaker notes retain the original Notes field, full canonical bullets, visual specification, and StarMath sources.
- All annex slides (21-48) carry the 'ANNEXE' band at the bottom.
- No displayed StarMath code, Markdown fences, or raw LaTeX; all embedded images decoded successfully.
- No internal names (streams, pipelines, milestones, file paths) detected on any slide.
- Every equation is displayed as its 'Affichage ASCII' line only; StarMath blocks are in the auxiliary file.
- No object outside the slide canvas. Text preflight uses actual font metrics.
- Palette and graphical utilities loaded from the unchanged canonical template; Carlito is the Calibri metric substitute.

## Sources and output SHA-256

| File | SHA-256 |
| --- | --- |
| DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v4_CGPT.md | `af1264b7b5addbef1c4824a8cc27ff11cab5b056c944dfca109cc9027c3a3a94` |
| Generation_slides_Point_Hebdo_template.py | `91ece4e32b8e8e23c8c2594e2ee45ac543825bca883ec4006b1dabc18e379d75` |
| 2026_10_26_Point_Hebdo_JEPA_Drift_v4_CGPT.pptx | `9f9eb08af7f0db7c9c940212616903a3a4d75947cacdcc3b37b01ce5f700d83d` |

## Per-slide control table (48 blocks)

| Slide | Kind | Equations | Links | Notes | Annex band | Off-canvas |
| ---: | --- | ---: | ---: | --- | --- | --- |
| 1 | TITLE | 0 | 0 | retained | n/a | none |
| 2 | TABLE | 0 | 0 | retained | n/a | none |
| 3 | CONTENT | 1 | 0 | retained | n/a | none |
| 4 | TABLE | 0 | 0 | retained | n/a | none |
| 5 | TABLE | 0 | 0 | retained | n/a | none |
| 6 | CONTENT | 1 | 0 | retained | n/a | none |
| 7 | CONTENT | 1 | 0 | retained | n/a | none |
| 8 | CONTENT | 1 | 1 | retained | n/a | none |
| 9 | CONTENT | 1 | 0 | retained | n/a | none |
| 10 | CONTENT | 1 | 1 | retained | n/a | none |
| 11 | CONTENT | 1 | 1 | retained | n/a | none |
| 12 | TABLE | 1 | 0 | retained | n/a | none |
| 13 | TABLE | 1 | 0 | retained | n/a | none |
| 14 | CONTENT | 1 | 0 | retained | n/a | none |
| 15 | CONTENT | 1 | 0 | retained | n/a | none |
| 16 | CONTENT | 1 | 0 | retained | n/a | none |
| 17 | CONTENT | 0 | 1 | retained | n/a | none |
| 18 | CONTENT | 1 | 1 | retained | n/a | none |
| 19 | CONTENT | 1 | 0 | retained | n/a | none |
| 20 | TABLE | 0 | 0 | retained | n/a | none |
| 21 | ANNEX | 2 | 0 | retained | yes | none |
| 22 | ANNEX | 2 | 0 | retained | yes | none |
| 23 | ANNEX | 1 | 2 | retained | yes | none |
| 24 | ANNEX | 2 | 0 | retained | yes | none |
| 25 | ANNEX | 3 | 0 | retained | yes | none |
| 26 | ANNEX | 2 | 0 | retained | yes | none |
| 27 | ANNEX | 1 | 0 | retained | yes | none |
| 28 | ANNEX | 2 | 0 | retained | yes | none |
| 29 | ANNEX | 1 | 0 | retained | yes | none |
| 30 | ANNEX | 2 | 0 | retained | yes | none |
| 31 | ANNEX | 1 | 0 | retained | yes | none |
| 32 | ANNEX | 2 | 0 | retained | yes | none |
| 33 | ANNEX | 1 | 0 | retained | yes | none |
| 34 | ANNEX | 1 | 0 | retained | yes | none |
| 35 | ANNEX | 2 | 0 | retained | yes | none |
| 36 | ANNEX | 1 | 0 | retained | yes | none |
| 37 | ANNEX | 2 | 0 | retained | yes | none |
| 38 | ANNEX | 1 | 0 | retained | yes | none |
| 39 | ANNEX | 1 | 0 | retained | yes | none |
| 40 | ANNEX | 1 | 0 | retained | yes | none |
| 41 | ANNEX | 2 | 0 | retained | yes | none |
| 42 | ANNEX | 1 | 0 | retained | yes | none |
| 43 | ANNEX | 1 | 0 | retained | yes | none |
| 44 | ANNEX | 1 | 0 | retained | yes | none |
| 45 | ANNEX | 1 | 0 | retained | yes | none |
| 46 | ANNEX | 2 | 0 | retained | yes | none |
| 47 | ANNEX | 1 | 1 | retained | yes | none |
| 48 | ANNEX | 1 | 0 | retained | yes | none |

## Equation display check (formula/parole correspondence)

| Slide | ASCII formula (truncated) | StarMath | Lecture |
| ---: | --- | --- | --- |
| 3 | `beta_i(t) = Cov(r_i, r_m | [t-252,t)) / Var(r_m | [t-252,t))` | no | no |
| 6 | `I_t = I_0 * exp[-2*(t-1)/tau_a] ; B_total = I_0 / (1-exp[-2/` | no | no |
| 7 | `q_t = [somme(k dans residuels, z_k(t)^2) - d_R] / sqrt(2*d_R` | no | no |
| 8 | `Sigma_LW = (1-delta)*Sigma_emp + delta*mu*Id ; mu = trace(Si` | no | no |
| 9 | `FPR(H) = P_sans_changement(T_alarme <= H) ; gamma_H = H / al` | no | no |
| 10 | `R = D^(-1/2)*Sigma_emp*D^(-1/2) ; lambda_plus = [1+sqrt(N/T)` | no | no |
| 11 | `KL(P1||P0) = E_P1[log(p1(X)/p0(X))] ; I_k = (v_k' * Delta)^2` | no | no |
| 12 | `P0(b_t=1 | F_(t-1)) = 1/2` | no | no |
| 13 | `G_250 = moyenne[min(T_indice,250)] / moyenne[min(T_ACP,250)]` | no | no |
| 14 | `p_t = r_t - b*(b'*r_t) ; z_t = U'*p_t / ||p_t|| (si ||p_t||>` | no | no |
| 15 | `V(d) = [I(d)/I(500)] / M(d,504) ; x_d = ln(504) + (d/2)*ln(1` | no | no |
| 16 | `V(d+1)>V(d) <=> q_(d+1) > I(d)*[C(d+1)/C(d)-1]` | no | no |
| 18 | `L_var = (1/d)*somme(j=1..d, max(0,1-sd_batch(Z_j))^2)` | no | no |
| 19 | `G_H = E[min(T_reference,H)] / E[min(T_methode,H)]` | no | no |
| 21 | `Var(m) = [K*s2 + K*(K-1)*rho*s2]/K^2 = s2*[rho+(1-rho)/K]` | no | no |
| 21 | `K_eff = K/[1+(K-1)*rho] ; lim(K_eff)=1/rho ; lim(gain_sd)=1/` | no | no |
| 22 | `log(gamma) <= E1[log(E_T)] <= E1[log(Lambda_T)] = E1[somme(t` | no | no |
| 22 | `E1[T] >= log(gamma)/I = 504*log(gamma)/SR^2` | no | no |
| 23 | `I = SR^2/(2*252) ; tau_evidence = log(gamma)/I` | no | no |
| 24 | `I*v_mu''(y) + mu*v_mu'(y) = -1 ; v_mu'(0)=0 ; v_mu(h)=0` | no | no |
| 24 | `ADD_brownian = [h-1+exp(-h)]/I ; ARL0_brownian = [exp(h)-h-1` | no | no |
| 25 | `vol_i(t) = sqrt[somme(s dans W63,(r_i(s)-moyenne_W63(r_i))^2` | no | no |
| 25 | `mom_i(t) = somme(s=t-252..t-22, r_i(s)) ; rev_i(t) = somme(s` | no | no |
| 25 | `char_rang_i(t) = rang_t(i)/n_valides(t) - 0.5` | no | no |
| 26 | `Sigma_emp = (1/T)*somme(t=1..T,(r_t-r_bar)*(r_t-r_bar)')` | no | no |
| 26 | `Sigma_LW = (1-delta)*Sigma_emp + delta*(trace(Sigma_emp)/N)*` | no | no |
| 27 | `R_ij = Sigma_emp_ij / sqrt(Sigma_emp_ii*Sigma_emp_jj) ; n_ab` | no | no |
| 28 | `ell(x) = Delta'*Sigma^(-1)*x - Delta'*Sigma^(-1)*Delta/2` | no | no |
| 28 | `I_full = Delta'*Sigma^(-1)*Delta/2 = somme(k=1..N, (v_k'*Del` | no | no |
| 29 | `KL(P1_X||P0_X) = KL(P1_Z||P0_Z) + E_(Z~P1)[KL(P1_(X|Z)||P0_(` | no | no |
| 30 | `P0(b_t=1 | F_(t-1)) = (1-p0)/2 + p0/2 = 1/2` | no | no |
| 30 | `P0(b_1=c_1,...,b_n=c_n) = 2^(-n)` | no | no |
| 31 | `FPR_observee = somme(rep=1..R, 1{T_rep<=H})/R ; q_hat = somm` | no | no |
| 32 | `q = [somme(k=1..d_R,Z_k^2)-d_R] / sqrt(2*d_R)` | no | no |
| 32 | `KL_cov = [trace(Sigma0^(-1)*Sigma1) - log(det(Sigma0^(-1)*Si` | no | no |
| 33 | `Var(m) = a'*Sigma*a ; Var(m_new)=a'*M*Sigma*M'*a` | no | no |
| 34 | `P=Id-b*b' ; p=P*r ; z=U'*p/||p|| ; z(a*r)=z(r) (a>0)` | no | no |
| 35 | `L_n = integrale exp[u'*S_n - n*||u||^2/2] dNormal(u;0,s^2*Id` | no | no |
| 35 | `u'*S_n - a*||u||^2/2 = -a*||u-S_n/a||^2/2 + ||S_n||^2/(2*a)` | no | no |
| 36 | `L_n = (1+n*s^2)^(-d/2) * exp[s^2*||S_n||^2/(2*(1+n*s^2))]` | no | no |
| 37 | `E1[||S_n||^2] = 2*n^2*I + n*d ; x=n*I` | no | no |
| 37 | `E1[log(L_n)] = x-(d/2)*log(1+2*x/d) ; x_d = A+(d/2)*log(1+2*` | no | no |
| 38 | `I(d) = somme(k=1..d,1/k) ; r(d)=I(d)/I(500) ; V(d)=r(d)/M(d,` | no | no |
| 39 | `V(d+1)-V(d) = [q_(d+1)*C(d) - I(d)*(C(d+1)-C(d))]/[C(d)*C(d+` | no | no |
| 40 | `H_d=q_(d+1)*(a+c*d)-c*I(d) ; H_(d+1)-H_d=[q_(d+2)-q_(d+1)]*[` | no | no |
| 41 | `L = somme(j=1..K,L_j)/K >= L_j/K ; I_u = I*cos(angle)^2` | no | no |
| 41 | `temps_budget ≈ [log(gamma)+log(K)] / [I*cos(angle)^2]` | no | no |
| 42 | `I_t=I_0*exp[-2*(t-1)/tau_a] ; B_total=somme(t>=1,I_t)=I_0/[1` | no | no |
| 43 | `B_total >= KL(P1||P0) >= kl(P1(A_event)||P0(A_event)) ; P1(A` | no | no |
| 44 | `B(t) = I_0*tau_a*[1-exp(-2*t/tau_a)]/2 ; t = -(tau_a/2)*log(` | no | no |
| 45 | `dp_i/dr_j = -1/N (i != j) ; m_V = somme(i dans V,r_i)/taille` | no | no |
| 46 | `L_JEPA = moyenne(i dans M, ||h_hat_i-h_target_i||^2) ; L = L` | no | no |
| 46 | `L_var=(1/d)*somme(j=1..d,max(0,1-sd_batch(Z_j))^2)` | no | no |
| 47 | `M_t = somme(k=1..K, M_k,t)/K ; P0(T<=H) <= H/gamma` | no | no |
| 48 | `ARL0=E0[T] ; FPR(H)=P0(T<=H) ; RMST_H=E1[min(T,H)]` | no | no |

## Render and visual inspection

**LibreOffice is not available on this machine.** No PDF export was attempted.
No PNG contact sheet was generated. Visual inspection of individual pages is pending.
The PPTX was verified structurally (slide count, dimensions, text content,
hyperlinks, notes, equations, tables) but not visually.

## Specific scientific checks

- Slide 1: title slide with chain 'rendements (N actifs) → représentation figée → détecteurs distincts → alarmes'.
- Slide 2: two distinct tables — experimental (4 columns) + theoretical (3 columns).
- Slide 3: matrix panel + 4 characteristics table with windows.
- Slide 4: three-segment timeline with 65-day embargo hatches and '941 j x 239 actifs' label.
- Slide 5: simulations vs symmetrized historical funds table (5 rows).
- Slide 6: exponential decay curve labelled 'modèle théorique — pas un JEPA entraîné'.
- Slide 7: bifurcated pipeline ACP → signs / energy, two distinct detectors, no supervised drift.
- Slide 8: three panels — empirical covariance / Ledoit-Wolf / empirical correlation.
- Slide 9: three dated columns (pretrain/calibration/surveillance) with locks on frozen parameters.
- Slide 10: dimension table (97→6, 239→11) + algorithmic tree.
- Slide 11: two frames — KL definition / pipeline + results (oracle 15j, ACP 373j, degré zéro 446j).
- Slide 12: sign symmetry table (4 rows) with calibrated 4.3947% vs observed 4.425%.
- Slide 13: covariance rotation table (3 rows) with 15°/30°/45° and delay ratios 14.59/67.71/105.42.
- Slide 14: degree-zero normalization — two boxes (normalized residual / residual norm).
- Slide 15: r(d)/M(d)/V(d) table (5 rows) with q_k=1/k scenario, no financial optimum claimed.
- Slide 16: marginal criterion formula, no empty drawing.
- Slide 17: JEPA architecture — visible [r/s, beta, vol, mom, rev] / hidden [beta, vol, mom, rev].
- Slide 18: masking leakage — FAUX (market first) vs LICITE (mask first) + variance penalty.
- Slide 19: three parallel lanes — ACP / degré zéro / JEPA (dashed, NON EXÉCUTÉ).
- Slide 20: final results table (6 rows) — no invented JEPA performance.
- Slides 21-48: each annex explicitly references its main slide; no independent empirical conclusions.
- All equations displayed as ASCII text only; StarMath in auxiliary file.

## Limitations

- No PDF export (LibreOffice unavailable). Visual page inspection not performed.
- Equations are plain monospace text, not native Office Math objects.
- Hyperlink targets checked structurally; no network availability test.
- Visual diagrams are schematic; they do not represent measured data unless stated.
- Text preflight uses Carlito font metrics; minor rendering differences possible in PowerPoint.
