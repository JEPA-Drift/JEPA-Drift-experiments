# Point hebdo 2026-10-26 v3 — render check

## Executed structural checks

- Reopened the exported PPTX with python-pptx: 33 slides, ordered 1–33; 21 main slides and 12 annexes.
- Dimensions: 10.00 × 5.62 inches, ratio 1.77936; the canonical template's rounded 16:9 format.
- Equations: 39 ASCII formulas displayed as monospace text with their 'Lecture' explanations. No LaTeX or bitmap rendering.
- Hyperlinks: 11 external relationships, checked against source references on each slide; clickable reference runs embedded in content.
- All 33 speaker notes retain the original Notes field, full canonical bullets, visual specification, and StarMath sources.
- All annex slides carry the 'ANNEXE' band at the bottom.
- No displayed StarMath code, Markdown fences, or raw LaTeX; all embedded images decoded successfully.
- No internal names (streams, pipelines, milestones, file paths) detected on any slide.
- Every equation is displayed as its 'Affichage ASCII' line only; StarMath blocks are in the auxiliary file.
- No object outside the slide canvas. Text preflight uses actual font metrics.
- Palette and graphical utilities loaded from the unchanged canonical template; Carlito is the Calibri metric substitute.
- Fig. 30 on slide 7 is embedded byte-for-byte without crop or retouching. All other diagrams are labelled as schematic/theoretical.

## Sources and output SHA-256

| File | SHA-256 |
| --- | --- |
| DECK_POINT_HEBDO_JEPA_DRIFT_2026_10_26_v3.md | `846821a4a6e5a892859f65e7e55d9117932fc7ed1d920d5fcd3c7e73b4511414` |
| Generation_slides_Point_Hebdo_template.py | `91ece4e32b8e8e23c8c2594e2ee45ac543825bca883ec4006b1dabc18e379d75` |
| ../figures/Fig30_RealCrossSectional_Escape_UPDATED.png | `f9277e5f9e33f396e328f971cea132c0714d34f03ce4d21ee021102ea7a018a3` |
| 2026_10_26_Point_Hebdo_JEPA_Drift_v3.pptx | `c7ead349dbf2119a87c403b76106d95049420332b34a96102e4d7096782769b3` |

## Per-slide control table

| Slide | Kind | Equations | Links | Notes | Annex band | Off-canvas |
| ---: | --- | ---: | ---: | --- | --- | --- |
| 1 | TITLE | 0 | 0 | retained | n/a | none |
| 2 | TABLE | 0 | 0 | retained | n/a | none |
| 3 | CONTENT | 1 | 0 | retained | n/a | none |
| 4 | CONTENT | 0 | 0 | retained | n/a | none |
| 5 | CONTENT | 0 | 1 | retained | n/a | none |
| 6 | TABLE | 0 | 0 | retained | n/a | none |
| 7 | CONTENT | 1 | 0 | retained | n/a | none |
| 8 | CONTENT | 1 | 0 | retained | n/a | none |
| 9 | CONTENT | 0 | 2 | retained | n/a | none |
| 10 | CONTENT | 0 | 1 | retained | n/a | none |
| 11 | CONTENT | 1 | 1 | retained | n/a | none |
| 12 | TABLE | 0 | 0 | retained | n/a | none |
| 13 | TABLE | 0 | 0 | retained | n/a | none |
| 14 | CONTENT | 1 | 0 | retained | n/a | none |
| 15 | TABLE | 1 | 0 | retained | n/a | none |
| 16 | CONTENT | 1 | 1 | retained | n/a | none |
| 17 | CONTENT | 0 | 0 | retained | n/a | none |
| 18 | CONTENT | 0 | 1 | retained | n/a | none |
| 19 | CONTENT | 0 | 0 | retained | n/a | none |
| 20 | CONTENT | 1 | 2 | retained | n/a | none |
| 21 | TABLE | 1 | 0 | retained | n/a | none |
| 22 | ANNEX | 2 | 0 | retained | yes | none |
| 23 | ANNEX | 3 | 1 | retained | yes | none |
| 24 | ANNEX | 2 | 0 | retained | yes | none |
| 25 | ANNEX | 3 | 0 | retained | yes | none |
| 26 | ANNEX | 3 | 0 | retained | yes | none |
| 27 | ANNEX | 2 | 0 | retained | yes | none |
| 28 | ANNEX | 2 | 0 | retained | yes | none |
| 29 | ANNEX | 3 | 0 | retained | yes | none |
| 30 | ANNEX | 2 | 0 | retained | yes | none |
| 31 | ANNEX | 3 | 1 | retained | yes | none |
| 32 | ANNEX | 3 | 0 | retained | yes | none |
| 33 | ANNEX | 2 | 0 | retained | yes | none |

## Equation display check

| Slide | ASCII formula (truncated) | Lecture |
| ---: | --- | --- |
| 3 | `r(i,t) = ln[P(i,t) / P(i,t-1)]` | no |
| 7 | `gain_limite_sur_ecart_type = 1 / sqrt(rho)` | no |
| 8 | `score_k(t) = projection_sur_axe_k(t) / echelle_k` | no |
| 11 | `information_axe = deplacement_moyen^2 / (2 * variance_axe)` | no |
| 14 | `residu = rendements - composante_marche` | no |
| 15 | `eta = moyenne(sigma^2) * moyenne(1/sigma^2) >= 1` | no |
| 16 | `efficacite(d) = information_conservee(d) / cout(d)` | no |
| 20 | `impaire(r) = [g(r) - g(-r)] / 2` | no |
| 21 | `G_H = moyenne[min(T_reference,H)] / moyenne[min(T_methode,H)` | no |
| 22 | `Var(m) = [K*s^2 + K*(K-1)*rho*s^2]/K^2 = s^2*[rho + (1-rho)/` | no |
| 22 | `K_eff = K/[1+(K-1)*rho] ; limite(K_eff) = 1/rho ; limite(gai` | no |
| 23 | `y_k = v_k' * r ; delta_k = v_k' * Delta ; ell_k = delta_k*y_` | no |
| 23 | `I_k = E_apres[ell_k] = delta_k^2/(2*lambda_k) ; I(d) = somme` | no |
| 23 | `KL(P1_X,P0_X) = KL(P1_Z,P0_Z) + E_P1_Z[KL(P1_X_sachant_Z,P0_` | no |
| 24 | `A = Delta' * Sigma_0^(-1) * Delta / 2 ; I_conditionnelle = A` | no |
| 24 | `eta = I_conditionnelle/I_reference = E[sigma^2]*E[1/sigma^2]` | no |
| 25 | `S_n = somme(t=1..n, z_t) ; L_n = integrale exp(u'*S_n - n*no` | no |
| 25 | `u'*S_n - a*norme(u)^2/2 = -a*norme(u-S_n/a)^2/2 + norme(S_n)` | no |
| 25 | `L_n = (1+n*s^2)^(-d/2) * exp[s^2*norme(S_n)^2 / (2*(1+n*s^2)` | no |
| 26 | `E[norme(S_n)^2] = 2*n^2*I + n*d ; E[ln(L_n)] = -(d/2)*ln(1+n` | no |
| 26 | `E[ln(L_n)] = x - (d/2)*ln(1+2*x/d) ; x_d - (d/2)*ln(1+2*x_d/` | no |
| 26 | `x_4/I(4) < x_500/I(500) si et seulement si I(4)/I(500) > x_4` | no |
| 27 | `V(d+1)-V(d) = [q_(d+1)*C(d) - I(d)*(C(d+1)-C(d))]/[C(d)*C(d+` | no |
| 27 | `H_d = q_(d+1)*C(d) - c*I(d) ; H_(d+1)-H_d = [q_(d+2)-q_(d+1)` | no |
| 28 | `P[b_t=1 sachant F_(t-1)] = (1-p_0)/2 + p_0/2 = 1/2` | no |
| 28 | `P[b_1=c_1,...,b_n=c_n] = P[b_1=c_1,...,b_(n-1)=c_(n-1)]/2 = ` | no |
| 29 | `ell(r) = [ln(det(Sigma_0)/det(Sigma_1)) + r'*(Sigma_0^(-1)-S` | no |
| 29 | `E_1[r'*B*r] = trace(B*Sigma_1) ; KL = [trace(Sigma_0^(-1)*Si` | no |
| 29 | `Sigma_1 = R*Sigma_0*R' ; R'*R = Id ; det(Sigma_1) = det(Sigm` | no |
| 30 | `m_visible(t) = somme(i dans V, r(i,t)) / nombre(V)` | no |
| 30 | `r_visible - moyenne_toutes_actions = r_visible - [somme_visi` | no |
| 31 | `I*v_mu''(y) + mu*v_mu'(y) = -1 ; v_mu'(0) = 0 ; v_mu(h) = 0` | no |
| 31 | `v_-I'(y) = [1-exp(y)]/I ; v_+I'(y) = [exp(-y)-1]/I` | no |
| 31 | `temps_avant_fausse_alarme = [exp(h)-h-1]/I ; delai_apres_cha` | no |
| 32 | `I_t = I_0*exp(-2*(t-1)/tau_a) ; B = somme(t>=1,I_t) = I_0/[1` | no |
| 32 | `B(t) = I_0*tau_a*[1-exp(-2*t/tau_a)]/2 ; t = -(tau_a/2)*ln(1` | no |
| 32 | `A <= E_1[ln(Q_T)] = E_1[ln(Q_T/Lambda_T)] + E_1[ln(Lambda_T)` | no |
| 33 | `L = somme(j=1..K,L_j)/K >= L_j/K ; L_j >= K*gamma implique L` | no |
| 33 | `I_projection = (u'*theta)^2/2 = I*cos(angle)^2 ; budget_jour` | no |

## Render and visual inspection

**LibreOffice is not available on this machine.** No PDF export was attempted.
No PNG contact sheet was generated. Visual inspection of individual pages is pending.
The PPTX was verified structurally (slide count, dimensions, text content,
hyperlinks, notes, images) but not visually.

## Specific scientific checks

- Slide 1: title slide with chain 'rendements → coordonnées → alarme'.
- Slide 2: table with 3 columns; last column (limites) equally visible.
- Slide 7: original historical Fig. 30 embedded unchanged; labels 'risque de fausse alarme' / 'réduction du budget'.
- Slide 10: table shows 6 and 11 as variance-threshold settings, not detection optima.
- Slide 12: sign guarantee table with 750-day horizon visible; asymmetry limitation stated.
- Slide 13: covariance rotation results; decisive limitation about the comparator stated.
- Slide 15: two mechanisms (1.96 vs 1.97/2.00) clearly distinguished; no arrow to JEPA gain.
- Slide 21: gain criterion 1.25 stated as 'proposé' (proposed), not achieved.
- Slides 22-33: each annex explicitly references its main slide; no independent conclusions.
- All equations displayed as ASCII text only; StarMath in auxiliary file.

## Limitations

- No PDF export (LibreOffice unavailable). Visual page inspection not performed.
- Equations are plain monospace text, not native Office Math objects.
- Hyperlink targets checked structurally; no network availability test.
- Visual diagrams are schematic; they do not represent measured data unless stated.
- Text preflight uses Carlito font metrics; minor rendering differences possible in PowerPoint.
