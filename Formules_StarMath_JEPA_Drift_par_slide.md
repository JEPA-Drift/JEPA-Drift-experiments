# Formules LibreOffice Math (StarMath) — JEPA-Drift, par slide

Extraction des sections [EQUATIONS] de `DECK_POINT_HEBDO_JEPA_DRIFT_v1.md`, rédigées sous le formalisme
de la directive `/slides` (skill `slides`, section A : « strictly compliant LibreOffice Math AST »).

Usage : à insérer à la main dans les objets « Formule LibreOffice » des encadrés de formule du PPTX —
`Generation_slides_Point_Hebdo_JEPA_Drift.py` n'y écrit que la ligne « Texte simplifié ».
(Impress : Insertion → Objet → Formule LibreOffice, puis coller le code ci-dessous.)

## Audit de conformité (formalisme /slides, section A)

- 10 formules extraites (F1–F10) : slide 2 (F1–F3), slide 3 (F4–F5), slide 4 (F6), slide 12 (F7–F10).
- 10 conformes telles quelles : macros grecs à casse stricte (`%alpha`, `%DELTA`), accolades sur les
  deux opérandes de chaque `over`, `^` et `_`, accent unaire `bar r`, bornes `sum from{k=1} to{N}`,
  `drarrow` natif, littéral `"3,8"` entre guillemets, espacements `~`, `left`/`right` toujours appairés.
- Aucune correction : extraction verbatim, vérifiée bloc par bloc contre le deck (10/10 identiques).

## SLIDE 1 — TITLE — JEPA-Drift

Aucune formule ([EQUATIONS] Aucune).

## SLIDE 2 — CONTENT — Le point de départ : le plancher de Sharpe

Trois formules. Seule F3 est affichée (encadré « Le plancher de Sharpe (Article B) ») ; F1 et F2
sont les étapes intermédiaires de la dérivation.

### F1 — preuve quotidienne d'une petite dérive

```text
nitalic{KL} approx {{%mu}^{2}} over {2 {%sigma}^{2}} = {{{nitalic{SR}}_{nitalic{jour}}}^{2}} over {2}
```

Texte simplifié : KL ≈ μ² / (2σ²) = SR_jour² / 2

### F2 — délai = seuil ÷ preuve quotidienne

```text
nitalic{ADD} approx {ln left( {1} over {{%alpha}_{0}} right)} over {nitalic{KL}}
```

Texte simplifié : ADD ≈ ln(1/α₀) / KL

### F3 — plancher de Sharpe → encadré « Le plancher de Sharpe (Article B) »

```text
{nitalic{ADD}}_{nitalic{min}} >= {504 cdot ln left( {1} over {{%alpha}_{0}} right)} over {{nitalic{SR}}^{2}}
```

Texte simplifié : ADD_min ≥ 504 · ln(1/α₀) / SR²

## SLIDE 3 — CONTENT — Additionner des actifs corrélés ne suffit pas

Deux formules, accolées dans l'encadré « Pourquoi ça plafonne » (le deck les joint par « ; »).

### F4 — variance de la moyenne de K actifs équicorrélés

```text
nitalic{Var} left( bar r right) = {%sigma}^{2} left( %rho + {1 - %rho} over {K} right)
```

Texte simplifié : Var(moyenne de K actifs) = σ² · (ρ + (1 − ρ)/K)

### F5 — taille effective du panel, quand K grandit

```text
{K}_{nitalic{eff}} = {K} over {1 + left( K - 1 right) %rho} ~ rightarrow ~ {1} over {%rho} approx "3,8"
```

Texte simplifié : K_eff = K / (1 + (K − 1)·ρ) → 1/ρ ≈ 3,8

## SLIDE 4 — CONTENT — L'idée : chercher la dérive là où le marché ne fait pas de bruit

Une formule → encadré « La preuve quotidienne, direction par direction ».

### F6 — décomposition de la preuve quotidienne

```text
nitalic{KL} = {1} over {2} sum from{k=1} to{N} {{left( {{v}_{k}}^{nitalic{T}} %DELTA %mu right)}^{2}} over {{%lambda}_{k}}
```

Texte simplifié : KL = ½ · Σ_k (v_kᵀ Δμ)² / λ_k

## SLIDE 5 — CONTENT — Deux façons de construire l'espace latent

Aucune formule ([EQUATIONS] Aucune).

## SLIDE 6 — TABLE — Ce qui existe, et ce qui manque

Aucune formule ([EQUATIONS] Aucune).

## SLIDE 7 — CONTENT — Les grandes étapes

Aucune formule ([EQUATIONS] Aucune).

## SLIDE 8 — TABLE — Données et protocole de dérive

Aucune formule ([EQUATIONS] Aucune).

## SLIDE 9 — TABLE — Conférences cibles, par échéance

Aucune formule ([EQUATIONS] Aucune).

## SLIDE 10 — CONTENT — Prochaines étapes

Aucune formule ([EQUATIONS] Aucune).

## SLIDE 11 — DIVIDER — Questions et discussion

Aucune formule ([EQUATIONS] Aucune).

## SLIDE 12 — ANNEX — Annexe : d'où vient le plancher de Sharpe

Quatre formules, une par étape numérotée (ligne « Texte simplifié » de chaque étape).

### F7 — étape 1 : preuve quotidienne d'un décalage μ de la moyenne

```text
nitalic{KL} = {{%mu}^{2}} over {2 {%sigma}^{2}} = {{{nitalic{SR}}_{nitalic{jour}}}^{2}} over {2} , ~ {nitalic{SR}}_{nitalic{jour}} = {%mu} over {%sigma}
```

Texte simplifié : KL = μ² / (2σ²) = SR_jour² / 2, avec SR_jour = μ/σ

### F8 — étape 2 : annualisation sur 252 jours de bourse

```text
nitalic{SR} = sqrt{252} cdot {nitalic{SR}}_{nitalic{jour}} ~ drarrow ~ nitalic{KL} = {{nitalic{SR}}^{2}} over {504}
```

Texte simplifié : SR = √252 · SR_jour ⇒ KL = SR² / 504

### F9 — étape 3 : borne de la détection la plus rapide

```text
nitalic{ADD} >= {ln left( {nitalic{ARL}}_{0} right)} over {nitalic{KL}} left( 1 + o(1) right)
```

Texte simplifié : ADD ≥ ln(ARL₀) / KL · (1 + o(1))

### F10 — étape 4 : d'où le plancher

```text
{nitalic{ADD}}_{nitalic{min}} >= {504 cdot ln left( {1} over {{%alpha}_{0}} right)} over {{nitalic{SR}}^{2}} , ~ {%alpha}_{0} = {1} over {{nitalic{ARL}}_{0}}
```

Texte simplifié : ADD_min ≥ 504 · ln(1/α₀) / SR²  □

## Récapitulatif d'insertion

| Slide | Formule | Emplacement dans la diapo |
| ----- | ------- | ------------------------- |
| 2 | F3 | Encadré « Le plancher de Sharpe (Article B) » |
| 2 | F1, F2 | Étapes intermédiaires de la dérivation (non affichées sur la slide) |
| 3 | F4, F5 | Encadré « Pourquoi ça plafonne » (accolées, jointes par « ; ») |
| 4 | F6 | Encadré « La preuve quotidienne, direction par direction » |
| 12 | F7 | Étape 1 |
| 12 | F8 | Étape 2 |
| 12 | F9 | Étape 3 |
| 12 | F10 | Étape 4 |
