[2026-10-23 17:10 UTC]

# Handover — JEPA-Drift (« Article C »), streams 01–27

**Portée et priorité temporelle.** Les sections 1 à 5 issues du transfert du 22 octobre sont conservées pour transmettre sans perte les spécifications, les résultats et les variables ouvertes. Leurs mentions « en attente », leurs anciennes recettes de lancement et leurs états Git décrivent cette date. Les mises à jour datées ci-dessous font foi au 23 octobre 2026. Tous les chemins d'artefacts sont relatifs à `~/JEPA-Drift-experiments` ; ceux de la branche `stream-23` exigent cette branche tant qu'elle n'est pas fusionnée. Le dépôt distant est `https://github.com/JEPA-Drift/JEPA-Drift-experiments`, mais ses références ne contiennent pas encore les 11 commits d'avance du `main` local, ni les commits des branches 17 et 23.

## 1. Context and Discussion Objectives

- **Initial Queries — rôle :** Claude est co-auteur principal, théoricien en apprentissage statistique et architecte expérimental du projet de recherche « Article C » (JEPA-Drift). Le projet est mené par le chercheur principal, Raphael : AI Engineer chez LUSIS, en thèse CIFRE à l'Université Paris-Saclay (statut FTLV), avec une expérience en finance quantitative, optimisation de portefeuille et gestion d'actifs.
- **Initial Queries — filiation :** le projet prolonge l'« Article B » du même chercheur, « The Whitening Advantage », soumis à KDD 2027. L'Article B établit un plafond informationnel de la détection séquentielle de dérives sur une série univariée de rendements (le « plafond de Sharpe »). Son code public est lu en lecture seule et n'est jamais cloné.
- **Initial Queries — thèse :** une représentation z_t = φ(x_t ; C_t) de la coupe transversale quotidienne concentre la divergence de Kullback–Leibler (KL) d'une dérive dans peu de directions. Notations : x_t ∈ ℝ^N les log-rendements de N actifs ; C_t les caractéristiques connues à l'ouverture de t. Des moniteurs à calibration exacte détectent alors la dérive plus vite qu'un moniteur univarié ou poolé. L'inégalité de traitement des données (DPI) interdit toute hausse de KL : le gain vient uniquement de la concentration (retrait des modes de variance parasites, meilleur conditionnement, alignement de la dérive avec des directions de faible variance résiduelle ou pilotées par les caractéristiques). Taxonomie : drift Data = changement de P(X), capteurs d'échelle ou d'énergie (second ordre) ; drift Concept = changement de P(Y|X) ou de la moyenne conditionnelle, capteurs de signe ou de localisation (premier ordre).
- **Initial Queries — objectif de publication :** publication dans une conférence scientifique internationale de rang B, A ou A*, à partir de fin novembre 2026. Une première version complète de l'article est visée pour fin novembre 2026, avec soumission dès que possible ensuite. La conférence est choisie à ce moment ; `prompts/Plan_Claude_Opus_v2.md` et `v3.md` contiennent une matrice comparative des conférences candidates, à revalider. Titre A : « JEPA-Drift — Escaping the Sharpe Ceiling of Sequential Drift Detection through Latent Information Concentration ». Titre B, si la porte J4 échoue : article centré sur la calibration exacte et la concentration, le JEPA y devenant un résultat conditionnel.
- **Initial Queries — demande d'ouverture du fil :** « continuer » le plan d'orchestration consolidé v4 (`prompts/Plan_Claude_Opus_v4.md`). Le plan distingue deux pistes : T (théorie, code, rédaction : Claude) et X (données, exécution, vérification : le chercheur et les agents de code). Point de départ : la théorie du §3 et la validation Monte Carlo E2 (jalon J1).
- **Requirement Evolution — tour 1 :** Claude livre le lot 1 : `jepadrift/floors.py`, `experiments/e2_floor_validation.py` et ses tests, le §3 en LaTeX avec preuves, un addendum bibliographique. Il établit que le plancher de premier ordre de l'Article B, ADD_min ≥ 504·ln(1/α₀)/SR², n'est qu'une limite γ → ∞ et non une borne d'ADD à γ fini. Il reformule les Props 2–3 sous forme non asymptotique (trois lectures), redéfinit la règle de J1 et pré-exécute E2 : 46/46.
- **Requirement Evolution — tour 2 :** le chercheur interdit à Claude d'implémenter lui-même les streams. Claude clôt l'audit en lecture seule du code de l'Article B, rédige le contenu de la mémoire d'agent et génère 28 prompts d'implémentation pour agents de code, au gabarit de `prompts/Prompt_Claude_Opus_v4.md`.
- **Requirement Evolution — institution côté dépôt :** le chercheur met en place :
  - `AGENTS.md` canonique et `CLAUDE.md` en lien symbolique relatif, pour Claude Code comme pour Mistral Vibe ;
  - la table de routage Opus/Vibe (`prompts/streams/INDEX.md`) ;
  - le cycle plan → revue GO → plan enregistré → exécution → wrapup ;
  - un worktree git par stream ;
  - le push autorisé tant que l'adresse du dépôt n'est ni diffusée ni liée à une publication (soumission anonyme) ;
  - un checkout local de l'Article B.
- **Requirement Evolution — tour 3 :** après l'exécution des streams 1 à 11 et du complément 11b, Claude analyse les résultats et identifie les spécifications invalidées. Il livre un paquet de révisions :
  - modifications A1–A8 d'`AGENTS.md`, I1–I4 d'`INDEX.md` et note de statut d'`Orchestration_Streams_v5.md` ;
  - nouveau prompt 8b ;
  - remplacements complets des prompts 12, 13, 14, 19, 22, 23 et 25 ;
  - modifications ciblées des prompts 15, 16, 17, 18, 20, 21, 24, 26, 27 et 28.

  Le détail est en Section 3.
- **Requirement Evolution — collaborateur :** José Lucas De Melo Costa (co-auteur de T-JEPA, ICLR 2025), prévu au départ comme collaborateur, n'intervient pas. Le projet est mené en autonomie par le chercheur et Claude ; il pourra être sollicité plus tard, aucune tâche n'en dépend.
- **Requirement Evolution — tour 4 :** le présent wrap-up.
- **Stylistic and Operational Constraints — langues :**
  - avec le chercheur, communication en français ;
  - livrables académiques (article, code, docstrings) en anglais ;
  - dans le dépôt : français pour les plans, les revues GO et les entrées de `docs/DEVIATIONS.md` ; anglais pour le code, `docs/sections/`, les wrapups et les commits.
- **Stylistic and Operational Constraints — ton :**
  - direct, sans flatterie ni adoucissement ;
  - constat ou désaccord dans la première proposition ;
  - prémisses de l'utilisateur traitées comme des affirmations à tester ;
  - formatage structuré, critique franche.
- **Stylistic and Operational Constraints — préférences d'interface :**
  - première ligne de chaque réponse : horodatage entre crochets (date seule si l'heure manque), puis une ligne vide ;
  - bloc final « [Strategic Advice] » ; aucune question de relance ;
  - aucun conteneur d'interface (artefact, fichier, canevas) sans demande explicite : livraison en Markdown dans le fil ;
  - blocs extérieurs à quatre accents graves pour les prompts qui contiennent des blocs à trois ;
  - un wrap-up demandé par la directive de wrap-up suit son protocole propre.
- **Stylistic and Operational Constraints — rôle de Claude dans le chat :**
  - rédiger et réviser les prompts des streams ;
  - analyser les wrapups et les résultats ;
  - porter la théorie et la rédaction de l'article (piste T) ;
  - ne jamais implémenter les streams : ce sont les agents de code qui les implémentent.
- **Stylistic and Operational Constraints — gabarit des prompts d'agents :**
  - sections Contexte (2–3 phrases), Tâche, Entrées, Livrables, Contraintes techniques, Critères de succès, Commandes de vérification ;
  - prompts autoporteurs, contenant la consigne « Lire `CLAUDE.md` » et les définitions minimales ;
  - exécutables sans question préalable ;
  - fichiers nommés `prompts/streams/prompt-NN-<slug>.md`.
- **Stylistic and Operational Constraints — rédaction de l'article (anglais) :**
  - longueurs de phrase variées : des phrases de 8–12 mots intercalées entre des périodes de 25–35 mots, jamais trois phrases de même longueur ;
  - aucun méta-commentaire (« In this paper », « This section », plan interne) ;
  - aucun résumé de fin de paragraphe ni annonce du suivant ; au plus un marqueur de transition par paragraphe ;
  - tout adjectif évaluatif ancré dans un nombre ; termes établis conservés tels quels ;
  - lexique proscrit : delve, tapestry, landscape, pivotal, crucially, notably, « it is worth noting », multifaceted, myriad, robust (à préciser), seamless, leverage et harness (verbes), realm, nuanced, underscores, « sheds light on » ;
  - au plus 50 références.
- **Stylistic and Operational Constraints — règles scientifiques transverses :**
  - jamais de phrase suggérant une hausse de KL ou d'information ;
  - toujours déclarer la lecture d'un délai : budget, anytime-valid ou exacte ;
  - la Prop. 3 est un énoncé d'atteignabilité (approximation fluide), pas d'optimalité ;
  - aucune méthode non publiée dans le plan (l'anti-effondrement suit la recette publique : cible EMA, stop-gradient, régularisation de variance).
- **Stylistic and Operational Constraints — localisation du travail, à décrire ainsi :**
  - le répertoire de travail se trouve sur une machine locale (serveur SSH), dans `~/JEPA-Drift-experiments`, synchronisé avec le dépôt GitHub distant `https://github.com/JEPA-Drift/JEPA-Drift-experiments` ;
  - les fichiers de ce dépôt distant sont accessibles directement avec le connecteur (plugin) GitHub ;
  - le code de l'Article B est un checkout local en lecture seule : `~/The-Whitening-Advantage-Experiments`.

## 2. Uncompromising Analytical Assessment

### 2.1 Théorie (`paper/sec3_theory.tex`, preuves dans `paper/appA_proofs.tex`)

- **Validated Results — cadre :**
  - P₀ régit les données avant l'onset (moyenne conditionnelle nulle, covariance Σ_t) ; P₁ les régit après (moyenne décalée de Δμ_t) ; le premier jour après l'onset est t = 1 ;
  - ℓ_t est le log-rapport de vraisemblance conditionnel, I_t = E₁[ℓ_t | F_{t−1}] la KL conditionnelle, 𝓘_y son taux ergodique (au sens de Lai) ;
  - γ est le budget de fausse alarme ; une supermartingale de test est une P₀-surmartingale positive avec E₀ ≤ 1 ;
  - inégalité de Ville : P₀(sup E_n ≥ γ) ≤ 1/γ ;
  - I = SR²/504, où SR est le Sharpe annualisé du portefeuille tangent à la dérive.
- **Validated Results — Prop. 1 (hiérarchie) :**
  - pour des alternatives locales : ½Δμ̄ᵀΣ̄⁻¹Δμ̄ ≤ ½E[Δμ_tᵀΣ_t⁻¹Δμ_t] ≤ ½E[Δμ_tᵀ𝒥_tΔμ_t] = 𝓘_x(1 + o(1)), et 𝓘_z ≤ 𝓘_x ;
  - le terme de gauche borne toute projection linéaire fixe surveillée par ses deux premiers moments inconditionnels ; la seconde inégalité est une égalité si et seulement si x_t est conditionnellement gaussien ;
  - trois canaux récupérables :
    - N1, la volatilité commune : écart de Jensen E[σ²]E[σ⁻²], σ_t étant estimable par la dispersion transversale du jour ;
    - N2, les chargements pilotés par les caractéristiques ;
    - N3, la non-gaussianité résiduelle (𝒥_t ⪰ Σ_t⁻¹) ;
  - rétention : r_φ(D) = 𝓘_{φ_D}/𝓘_x ∈ [0, 1].
- **Validated Results — Lemme 1 (budget d'évidence, exact) :**
  - toute supermartingale de test lancée à l'onset vérifie E₁[Σ_{t≤T_γ} I_t] ≥ ln γ ;
  - si I_t est constant : E₁[T_γ] ≥ τ_γ = ln γ/I = 504·ln γ/SR² ;
  - pour le rapport de vraisemblance, l'écart se réduit au dépassement ;
  - c'est la lecture exacte, non asymptotique, du plafond de Sharpe : un moniteur qui connaît l'onset et la direction a besoin de τ_γ jours en moyenne pour accumuler une évidence γ.
- **Validated Results — Prop. 2 (trois lectures du plancher latent) :**
  - (a) e-détecteur CUSUM arrêté à γ : ARL₀ ≥ γ (Lorden) et ADD·I = h′ − 1 + e^{−h′}, avec h′ = ln γ + 2ρ‖θ‖ et ρ ≈ 0,583 (Siegmund) ;
  - (b) calibration exacte à ARL₀ = γ, où le CUSUM est Lorden-optimal (Moustakides) : I·ADD_min → Φ(γI), avec Φ(g) = h_g − 1 + e^{−h_g} et e^{h_g} − h_g − 1 = g ; asymptotiques : Φ(g) = ln g − 1 + O(ln g/g) quand g → ∞, et Φ(g) = g − (2g)^{3/2}/3 + O(g²) quand g → 0 ;
  - (c) forme Sharpe : I_z ≥ SR_z²/504, avec égalité sous gaussianité conditionnelle. SR_z² ≤ 504·𝓘_x, qui ne vaut SR_x² que si x_t est conditionnellement gaussien : SR_z peut dépasser SR_x par le canal N3.
- **Validated Results — ordres de grandeur (SR = 1, γ = 20 et 252) :**

  | Lecture                           | γ = 20  | γ = 252 |
  | --------------------------------- | ------- | ------- |
  | Budget τ_γ                        | 1 510 j | 2 787 j |
  | E-détecteur CUSUM (anytime-valid) | 1 066 j | 2 322 j |
  | ADD Lorden-optimal (exacte)       | 17 j    | 142 j   |

  - À γ = 252, le délai exact n'est que 1,8 fois plus court que le temps moyen avant fausse alarme.
  - Quand γI ≫ 1, la formule de premier ordre surestime ADD_min d'environ (1 + ln(1/I))/I jours.
- **Validated Results — Corollaire 1 (facteur et largeur, exact à N fini) :**
  - pour Σ = BΣ_FBᵀ + Ψ et Δμ = BΔλ + Δα : Δμᵀ Σ⁻¹ Δμ = Δλ̃ᵀ(Σ_F + K⁻¹)⁻¹Δλ̃ + Δα_⊥ᵀΨ⁻¹Δα_⊥ ;
  - avec K = BᵀΨ⁻¹B, Δα_⊥ le résidu GLS de Δα sur B, et Δλ̃ = Δλ + K⁻¹BᵀΨ⁻¹Δα ;
  - le terme factoriel est borné en N. Pour une dérive de marché à un facteur, le gain du pooling vaut N/(1 + (N − 1)ρ) → 1/ρ (plateau K_eff) ;
  - seul le terme de largeur croît avec N.
- **Validated Results — objectif de concentration :**
  - maximiser r_φ(D)/M(D, γ) ;
  - l'ordre PCA (par variance λ_k) diffère de l'ordre par information de dérive (v_kᵀΔμ)²/λ_k ;
  - les composantes de faible variance portent la plus grande part d'une dérive diffuse (antériorité : Kuncheva & Faithfull 2014 ; Qahtan et al. 2015, à citer dès le §1).
- **Validated Results — Prop. 3 (taxe de dimension) :**
  - e-processus de mélange gaussien isotrope : L_n = (1 + ns²)^{−D/2} exp{s²‖S_n‖²/(2(1 + ns²))}, avec s² = 2I/D ;
  - valide si z_t est conditionnellement sous-gaussien de proxy I_D : coordonnées gaussiennes, ou signes Rademacher indépendants ;
  - identité exacte : E₁[log L_n] = x − (D/2) ln(1 + 2x/D), avec x = nI ;
  - délai fluide : M(D, γ)·τ_γ, avec x* = ln γ + (D/2) ln(1 + 2x*/D) et M ≈ √(D/ln γ) quand D ≫ ln γ ;
  - à γ = 504 : M = 1,22, 2,01, 3,91 et 9,64 pour D = 1, 10, 64 et 500, et 5,2 pour D = 128. D'où une tête surveillée de dimension D ≤ 16 ;
  - dictionnaire de K atomes : multiplicateur (ln γ + ln K)/(cos²ϑ · ln γ), où ϑ est l'angle entre la dérive et l'atome le plus proche.
- **Validated Results — Corollaire 2 (lois d'échelle) :** avec I(N) ∝ N^a et D(N) ∝ N^b, le gain fluide croît comme N^{a−b/2} :
  - N⁰ pour une dérive de marché surveillée par pooling ;
  - N^{1/2} pour une largeur non structurée surveillée dans tout le résiduel par un mélange isotrope ;
  - N¹ pour une largeur portée par un nombre fixe de directions de caractéristiques.
- **Validated Results — Lemme 2 (encodeur impair) :**
  - hypothèses : φ(·; C) impaire en x ; C_t et la direction u_t prévisibles ; loi conditionnelle de x_t centralement symétrique sous P₀ ;
  - conclusion : b_t = 1{u_tᵀφ(x_t; C_t) > 0} est i.i.d. Bernoulli(½), quelles que soient la volatilité, les corrélations et les queues ;
  - les égalités sont tranchées par une pièce indépendante.
- **Validated Results — Corollaire 3 (orthogonalité latente) :**
  - une statistique impaire est aveugle à tout changement qui préserve la symétrie centrale ;
  - une statistique paire ne bouge qu'au second ordre sous translation ;
  - d'où l'architecture à deux têtes : une tête impaire (Concept, flux de signe exacts) et une tête paire (Data, capteurs d'énergie).
- **Validated Results — combinaison des canaux :** on moyenne les supermartingales de test, ce qui reste valide sous toute dépendance ; jamais de produit, qui n'est valide que si les incréments multiplicatifs sont conditionnellement non corrélés.
- **Validated Results — Prop. 4 (absorption) :**
  - modèle : un encodeur adaptatif absorbe la dérive, avec I_t = I_z·e^{−2(t−1)/τ_a} et un budget total B = Σ_t I_t ;
  - si B < ln γ, aucune supermartingale de test lancée à l'onset n'atteint γ presque sûrement ;
  - si τ_a > 2τ_γ, le délai fluide vaut −(τ_a/2) ln(1 − 2τ_γ/τ_a), soit 2,01 ; 1,39 et 1,15 fois τ_γ pour τ_a/τ_γ = 2,5 ; 4 et 8 ;
  - conséquence : un encodeur de référence gelé pendant la surveillance.
- **Validated Results — mémoire de volatilité et efficacité du signe :**
  - le Lemme 1 vaut en temps d'information ;
  - sous volatilité persistante, le délai calendaire d'un moniteur de signe exact dépasse ln γ/Ī d'un terme additif d'ordre CV²(I_t)·τ_int(I_t) ;
  - ce terme est prévu à 13–16 jours et mesuré à 8–11 jours pour un GARCH(0,08 ; 0,90) à innovations t₇ ;
  - efficacité d'un flux de signe = 4f(0)², soit 2/π sous normalité et 0,830 pour une t₇ standardisée.
- **Validated Results — lecture à horizon (tour 3, à confirmer au GO du stream 12) :**
  - pour tout e-détecteur, P∞(alarme avant H) ≤ H/γ ;
  - les expériences de localisation lisent donc l'anytime-valid à γ_H = H/α, avec α = 0,05 ;
  - cette lecture est comparable aux lectures exacte (niveau du treillis ≤ α à H), bootstrap et randomisation (FPR(H) ≈ α) ;
  - les lectures en ARL₀ (γ ∈ {20, 252}) sont réservées à E2 et E3.

### 2.2 E2 et jalon J1

- **Validated Results — résultat global :** J1 est passé. `results/e2/e2_cells.csv` a pour SHA-256 `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`, bit-identique sous numpy 2.4.4 et scipy 1.17.1.
- **Validated Results — grille :** graine 20261018, 46 cellules. Le rapport `results/e2/J1_report.md` donne 2 000 réplications par cellule G1/S1, 1 000 par cellule G2/S2 et 500 pour G2 à D = 64. Quatre bras :
  - G1 : gaussien, D = 1, lectures onset, cusum_t et cusum_x ;
  - G2 : mélange isotrope, D ∈ {1, 2, 5, 10, 20, 64} ;
  - S1 : signe sur GARCH(0,08 ; 0,90) à innovations t₇, symétrisé, avec mise fixe et mise oracle ;
  - S2 : mélange sous-gaussien sur des flux de signe, D ∈ {5, 20}.
- **Validated Results — règle J1 :**
  - bras i.i.d. : ratio mesuré/prédit dans [0,90 ; 1,10], et ARL₀ réalisé de cusum_x à ±10 % de γ ;
  - bras GARCH : horloge d'information Σ I_t à ±10 % ; délai calendaire à ±10 % seulement si le délai prévu dépasse CALENDAR_MIN = 150 jours.
- **Validated Results — écarts maximaux :**
  - G1 : 2,4 % ;
  - G2 : 4,7 % ;
  - S1 : horloge ≤ 3,3 % ; délai calendaire ≤ 2,6 % pour SR ≤ 2, et de +5,7 à +11,8 % à SR = 4 (contrôlé sur l'horloge) ;
  - S2 : 4,6 %.
- **Validated Results — sous H₀ :** moyenne des bits 0,4998 ; autocorrélation +0,0002 ; corrélation croisée −0,0009 (écart-type 0,0010). Les carrés, eux, ont une autocorrélation de +0,067.
- **Validated Results — références G1 à SR = 1 :**
  - γ = 20 : onset 1519,152 ; cusum_t 1050,323 ; cusum_x 16,730 ;
  - γ = 252 : 2815,446 ; 2319,800 ; 145,081 (ARL₀ mesuré 258,49).
- **Validated Results — premier ordre :** il surestime le délai exact d'un facteur 90 (SR = 1, γ = 20) à 3,6 (SR = 4, γ = 252), et celui de l'e-détecteur de 14 à 44 %.

### 2.3 Résultats des streams 1 à 11 et 11b (tous fusionnés sur `main`)

| Stream | Objet                                                 | Résultats vérifiés                                                                                                                                                                                                                                                                                                                                                     |
| ------ | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1      | Socle, lot 1, E2                                      | Voir 2.2 ; arborescence, venv, Makefile, `AGENTS.md` (`CLAUDE.md` en lien)                                                                                                                                                                                                                                                                                             |
| 2      | D1 et D2 depuis le checkout de l'Article B            | **D1** : SPY 6 414 j (2000-01-04 → 2025-07-07), PFF 4 403 j, VNQ 5 014 j, BWX 4 451 j. **D2** : 5 154 j × 97 titres (2005-01-04 → 2025-06-30), 0,66 % de rendements nuls. **Datations** : `lt_spy` 66 phases, `strict_ps` 48, `symmetric` 102. Aller-retour CSV → parquet → numpy bit-identique                                                                        |
| 3      | D3 (S&P 500)                                          | 503/503 constituants actuels, 6 738 j (2000-01-03 → 2026-10-16), 11 secteurs GICS. Liste CD-DFM absente, d'où `d3_239` = les 239 plus longs historiques (C-D3-no239). `d3_500` à 13 % de NaN. Non-anticipation des caractéristiques vérifiée au bit. ρ̂_signe 0,19–0,28 ; K_eff 3,6–5,3                                                                                 |
| 4      | Noyau de surveillance, portage de l'Article B         | Identité R01 : 1 401 cellules conformes dans deux environnements. Identité R08 : 32/32 à 1e-12. Treillis = énumération exhaustive. Flux de signe sous GARCH-t₇ (H = 1 000, L = 47, seuil 9,5) : FPR 0,04275 pour un niveau de 0,042898. E-détecteur SR : ARL₀ 21,87 (γ = 20) et 110,91 (γ = 100)                                                                       |
| 5      | Injections F1–F4, fonds D5 et D6                      | Hash d'E2 inchangé après déplacement de `Garch`. Information cible atteinte à 1e-10 ; F2 orthogonale aux chargements à < 1e-10 ; information de F4 = (d/2)(r − 1 − ln r)                                                                                                                                                                                               |
| 6      | Représentations, interface Z-1                        | K = 5 (D2, λ₊ = 1,7452) et 10 (D3, λ₊ = 2,2619) ; shrinkage Ledoit–Wolf 0,0192 et 0,0252 ; tail10 m = 46 et 123. Extractions de référence `z_85147fd9…` (D2, D = 6) et `z_6c44d64a…` (D3, D = 11)                                                                                                                                                                      |
| 7      | Pipelines P2-C, P3-C, P3-D, P3-CS, P7 et calibrations | **Identité R15** : 56 cellules à 1e-12, dont 54 au bit. **Nul D6** (H = 750) : canaux exacts 0,0385–0,0505 pour un niveau de 0,043947 ; dictionnaire P3-C à γ = 15 000 : 0,0015 ; P3-CS (a) par randomisation : 0,0640. **F2 à SR = 8** : P7 15 j ; P3-C 373 j ; P3-CS (b) 446 j ; P3-CS (a) 1 164 j. **P3-D** sur la calib : Γ^op 7,64 (factoriel) et 25,19 (complet) |
| 8      | Contrats, découplage, hooks                           | 20 contrats et 4 gardes torch ; 6 tests AST de découplage. Les hooks bloquent les chemins EUROFIDAI et les fichiers > 50 Mo                                                                                                                                                                                                                                            |
| 9      | BAF                                                   | 6 variantes × 1 000 000 lignes, 32 colonnes, licence CC BY 4.0. Fraude de 0,87 % (mois 2) à 1,47 % (mois 7)                                                                                                                                                                                                                                                            |
| 10     | EUROFIDAI (D4)                                        | 498 titres, 6 541 j (2001-01-02 → 2026-06-30), places AMS, BRU, EPA, LSE, MIL et XET. `in_universe` couvre 91 % des cellules. Sélection : au moins 5 000 observations ; aucune radiation explicite ; MIL sans données 2024–2026                                                                                                                                        |
| 11     | Audit D2/D3 (2005–2019)                               | Voir l'interprétation, section 2.4                                                                                                                                                                                                                                                                                                                                     |
| 11b    | Bruit de N2, placebo                                  | N2 net du bruit (médiane sur 2 000 fonds) : 1,74–2,40 (D2, F1) ; 1,89–3,04 (D3, F1) ; 1,45–1,88 (D3, F2), et 0,94 pour `rev_21`. Placebo du SR² de marché : réel 19–41 contre ≈ −2,5 sous rotation, excès +21 à +43, p ≤ 0,0015                                                                                                                                        |

### 2.4 Interprétation de Claude

- **La pile de calibration est publiable.** Flux de signe exacts sur D6, identités avec l'Article B au bit près, garanties anytime-valid vérifiées : le socle n'est plus un risque.
- **Aucune information de largeur n'est mesurable aux transitions réelles.**
  - Médianes de SR² débiaisé : marché 40,8 (D2, `lt_spy`) et 38,2 (D3) ; sous-espace factoriel ≈ 0 ; idiosyncratique +16,6 et +8,6 sur D2, −181,6 et −51,7 sur D3 (R9).
  - Le placebo montre que le SR² de marché aux frontières datées relève de la sélection.
  - Conséquence : la preuve de l'article sera semi-synthétique ; les données réelles servent d'appui.
  - Le déclencheur R10 de la contingence C1 est en partie atteint, et E6 (phase linéaire) passe en priorité A.
- **Le goulot est la conception du détecteur, pas seulement l'information.**
  - L'écart P7/P3-C atteint un facteur 25. Il cumule l'efficacité du signe (2/π), la taxe ln K du dictionnaire et surtout l'alignement cos²ϑ entre la dérive et les canaux.
  - Le mélange isotrope est bloqué par la porte d'indépendance, en mode factoriel par une dépendance réelle, en mode complet par simple multiplicité.
  - Le critère J2 (iii) est menacé par construction, d'où le diagnostic a_max.
- **N1 est le canal le plus robuste.**
  - Valeurs : N1 = 1,97 (D2) et 2,00 (D3) ; N2 net de 1,45 à 3,04 ; N3 de 1,21 à 1,25.
  - P3-CS (b), coupe de degré 0 à mise ∝ 1/σ̂, capte N1 sans apprentissage : c'est la référence d'attribution du JEPA.
- **La lecture anytime-valid à γ = 20 est inutilisable sur un horizon long.** Sur 750 jours, les e-détecteurs alarment sur 71 % (P3-C) et 29 % (P2-C) des trajectoires nulles. D'où la lecture γ_H.
- **La symétrie centrale tombe sur données brutes.** Rejets au seuil de Holm 5 % : D2 PC1 (binomial et triplets) et PC3 (binomial) ; D3 PC1 et PC2 (les deux tests), PC3 et `rev_21` (binomial). Exactitude garantie sur D6, pas sur le canal marché brut.
- **Biais de survie.** D3 (constituants actuels) et D4 (sélection d'au moins 5 000 observations) sont des univers de survivants ; l'entrée C-D3-survivor affirme le contraire et doit être corrigée. Pour l'Article B, la sélection des frontières gonfle le SR intra-phase : la part « hors budget » du recensement (80,3 % à γ = 20) est une borne inférieure, ce qui renforce l'énoncé.

### 2.5 Erreurs et impasses

- **Errors and Dead Ends — plancher :** le plancher de premier ordre était lu comme une borne d'ADD à γ fini, dans l'Article B et au §4.2 du plan v4 (« ADD_min ≥ … ; 64 of 66 phases end before their own floor »). C'est faux à γ fini ; seule la lecture budget est exacte. Il faut réécrire le §1 en lecture budget et nommer la composition des datations.
- **Errors and Dead Ends — lot 1 :**
  - un premier passage de S2 à +15–27 % venait d'un p̄ calibré sur un GARCH univarié au lieu du GARCH multivarié (corrigé) ;
  - la règle J1 à deux niveaux et CALENDAR_MIN ont été fixés après un passage rapide : c'est un degré de liberté, déclaré.
- **Errors and Dead Ends — défauts des prompts v5 de Claude :**
  - prompt 5 : F2 demandé sur SYM-D2, qui n'a pas de caractéristiques ;
  - prompt 7 : FPR des e-détecteurs exigé « dans l'IC de la cible », alors qu'une garantie d'ARL₀ ne fixe pas un FPR(H) (cibles redéfinies au GO : C-pipe-null-targets) ;
  - prompt 11 : formule de débiaisage biaisée de 252·d·c·(d + 1)/ν (corrigée par `sr2_debiased`, C-audit-debias) ;
  - prompt 11 : gains prévus calculés aux transitions, qui donnent NaN et un dénominateur sélectionné ;
  - prompt 12 : H_det = 2 000 pour P3-D, alors que la calib ne compte que 941 jours (C-P3D-windows).
- **Errors and Dead Ends — impasses méthodologiques :**
  - P3-CS (a) avec des mises ≤ 0,4 : 35 % de détection (17,5 % pour un CUSUM non standardisé), d'où les mises ±{0,1 ; 0,25 ; 0,5 ; 0,9} et des pivots standardisés ;
  - P3-D sur 2005–2019 : Γ^op ≈ 191 et 2 346 à cause du régime 2008 ;
  - IC percentile simple : il excluait l'estimation débiaisée, d'où un percentile décalé ;
  - fond D6 pour mesurer le bruit de N2 : invalide, car D6 conserve les moments d'ordre 2. Remplacé par une permutation de jours entiers (C-audit-n2-noise) ;
  - rapport réel/placebo : indéfini (médianes placebo ≤ 0), remplacé par l'excès et une p-valeur (C-audit-placebo).
- **Errors and Dead Ends — incidents de processus :**
  - interpréteur Trading (numpy 1.26.4) utilisé au stream 8 : échecs à 1e-16 et commit `--no-verify` `f7bde91`. Corrigé par l'épinglage de la chaîne d'interpréteur (`424b199`) ;
  - `importorskip("torch")` au niveau module sautait les 4 contrats en `.venv` (corrigé par `8ae232e`) ;
  - `GIT_DIR` exporté au hook faussait le manifeste (corrigé par `unset`) ;
  - un `git stash -u` d'une autre instance sur l'arbre partagé, d'où l'adoption des worktrees ;
  - un lien unique `data/raw` dans un worktree casse `test_gitignore_blocks_eurofidai` (C-worktree-data-raw) ;
  - le fixture D1/D2 réécrit des fichiers suivis : encore ouvert, traité par le prompt 8b.
- **Errors and Dead Ends — Article B, texte v87 contre code** (registre de 62 écarts, dont 15 de sévérité D3) :
  - le flux Concept est un flux d'étiquettes 1{r > 0} − q̂ (prédicteur constant), pas l'erreur d'un Hoeffding Tree ;
  - les 66 phases = Lunde–Timmermann sur SPY et Pagan–Sossounov ailleurs ; le PS strict sur les quatre ETF donne 48 phases ;
  - le niveau R08 délivré est de 5,10 % (au-dessus des 5 % nominaux) sous la règle large ;
  - les 4,29 % et 5,03 % du plan v4 sont des niveaux v87 (4,32 % et 5,08 % après re-tirage). Les niveaux se calculent toujours par `lattice.py`, à l'horizon effectivement utilisé.

### 2.6 Pistes explorées

- **Investigated Pathways — approximation brownienne :** corrigée par Siegmund, elle prédit à ±2 % l'ADD du CUSUM calibré exactement (Monte Carlo). L'horloge d'information (identité de Wald) sert de critère exact sur fonds GARCH.
- **Investigated Pathways — lecture et diagnostic proposés :** lecture γ_H = H/α ; diagnostic d'alignement a_max = max_k Δz_k²/‖Δz‖² ; délai prévu du dictionnaire ≈ (ln γ_H + ln K)/(e·a_max·I_z), avec e = 4f̂(0)².
- **Investigated Pathways — mélange directionnel :** moyenne d'e-processus de signe sur des directions aléatoires. Il est valide sous dépendance mais inefficace en grande dimension : max cos² ≈ 2 ln K/D, soit 0,077 pour D = 238 et K = 10⁴. Piste retenue : des mélanges dans le sous-espace des caractéristiques (D ≈ P), que P4 et P5 doivent fournir.
- **Investigated Pathways — mélange isotrope corrigé :** la porte d'indépendance corrigée par Holm au niveau de famille 1 % ne donne qu'une validité approchée. À utiliser en diagnostic, jamais dans un verdict.
- **Investigated Pathways — paris sur moyennes de bits :** parier sur la fraction des signes (P2-C anytime-valid), ou sur la moyenne de bits exacts, donne des différences de martingale bornées : exact sous toute corrélation transversale.
- **Investigated Pathways — outils statistiques de l'audit :**
  - symétrie : test binomial exact et test des triplets de Randles (O(n² log n), variance NSM3::RFPW) ;
  - loi t multivariée : ECME (Liu & Rubin 1995) ;
  - sélection des frontières : rotations circulaires des chaînes de phases ;
  - bruit de N2 : permutation de jours entiers.

### 2.7 Résultats ajoutés et index des artefacts (état du 23 octobre 2026)

| Périmètre | Tableaux et figures | Constat mesuré | Statut |
| --- | --- | --- | --- |
| J1, E2 | `results/e2/e2_cells.csv`, `results/e2/J1_report.md` | 46/46 cellules admises ; SHA-256 CSV `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` sur octets CRLF natifs | `main` local, streams 01–11 |
| Données D1–D3, D7 | `results/data/{d1_d2_profile,d3_profile,baf_profile}.csv`, `data/derived/MANIFEST.json` | D2 : 5 154 × 97 ; D3 : 503 titres actuels, 6 738 jours ; BAF : 6 variantes synthétiques | `main` local |
| Identités et pipelines | `results/identity/{articleB_R01_R08,articleB_R15}.csv`, `results/pipelines/alarms_P3-C_d2_us97_null.csv` | R01 : 1 401 cellules ; R08 : 32/32 ; R15 : 56 cellules ; D6 H = 750 : FPR exact 0,0385–0,0505 pour un niveau 0,043947 | `main` local |
| Audit D2/D3 | `results/audit/{spectrum,eta_by_year,sign_corr,symmetry_tests,drift_sharpe_transitions,channel_ceilings,budget_share,predicted_gains,placebo_selection}.csv`, `figures/audit/{spectrum,symmetry,drift_sharpe,budget_share}.{png,pdf}` | N1 = 1,97–2,00 ; N2 net = 1,45–3,04 selon panel et injection ; N3 = 1,21–1,25 ; sélection et asymétrie brutes mesurées | `main` local, streams 11–11b |
| E10 F1 | `results/e10/e10_cells.csv` (4 004 lignes), `results/e10/e10_gains.csv` (144 lignes), `figures/e10/{fpr_inflation,gains}.{png,pdf}`, `logs/e10/run.log` | Stress tests de l'exactitude des signes, recentrage `qhat`, rapports de délais RMST et placebos bruts | `main` local, stream 27 fusionné |
| E6 F4 phase 1 | `results/e6/e6_cells_phase1.csv` (190 × 50), `figures/e6/e6_phase1_{delays,gadd}.{png,pdf}` | Énergie et PCA sur fonds D5 indépendants et fenêtres D6 chevauchantes ; phase P4-D/P5-D absente | Branche `stream-23` à `3d0bd20`, hors `main` |

**E10, calibration.** `results/e10/e10_cells.csv` a pour SHA-256 `9998f9422794078a515a7ba1a2701802ef9e162b3d183e42fc71e3ec1799da56`; le CSV des gains a pour SHA-256 `4225c18a8101412164b6e99eb78b0e5f4607d153427e276314c4c4e624d2843c`. À H = 750, α = 0,05, γ_H = 15 000, le niveau de treillis du flux `half` exact est 0,0439467. Sous null valide, 317 lignes unitaires ont un taux moyen 0,04425 ; 3 sortent de la région binomiale à 99 %, contre environ 3,2 attendues si les cellules étaient indépendantes. Ce décompte est un contrôle de calibration, pas un test omnibus d'indépendance entre cellules. Le scénario i.i.d. de référence donne 880/20 000 = 0,0440, dans sa tolérance à 99 % [0,0402 ; 0,0477]. La garantie exacte concerne le signe sous symétrie centrale conditionnelle, avec pièce indépendante aux égalités, et non les flux recentrés estimés.

**E10, rupture de l'hypothèse nulle.** Sous choc commun asymétrique, le canal marché `half` exact atteint 0,092 à w = 0,25, contre 0,048 pour le générateur symétrique apparié ; inflation +0,044, IC bootstrap apparié 95 % [0,029 ; 0,060]. À w = 0,50, il atteint 0,3915 contre 0,0445 ; inflation +0,347 [0,323 ; 0,370]. Le dictionnaire anytime-valid atteint 0,101 contre 0,0005 à w = 0,50 : l'appellation anytime-valid dépend toujours de la validité du null des bits. Le recentrage sur `qhat` ramène les différences appariées du canal exact à 0,073 contre 0,070, puis 0,0605 contre 0,0615, avec IC d'inflation couvrant zéro. Son taux reste pourtant 0,059–0,0775 sous des nulls valides, contre environ 0,044 pour `half`, parce que `qhat` est estimé ; aucune exactitude finie n'est revendiquée pour ce bras. Compter les rendements nuls comme négatifs élève la médiane P1-C exacte à 0,0902 avec 5 % de zéros : la convention de pièce est une condition opérationnelle de l'exactitude.

**E10, délais et données brutes.** À SR = 16, le rapport RMST_H du titre médian P1-C au dictionnaire P3-C vaut 7,1–7,9 sur D5 et 5,5–6,4 sur D6, selon le panel. Le dictionnaire n'est alors jamais censuré : son ratio RMST donne une borne inférieure du ratio ADD. À SR = 4, les valeurs 1,8–4,7 (D5) et 1,2–1,4 (D6) ne sont que des rapports restreints, car la censure est fréquente. Sous choc w = 0,50, le dictionnaire `half` a un FPR H₀ de 0,101 contre au plus 0,005 pour le titre : un gain de délai dans ce cas n'est pas un gain à FPR égal. Le placebo brut est rétrospectif : 2 019 fenêtres D2 et 2 020 D3, avec ajustement sur une calib ultérieure. Le canal 0 `half` exact ne donne aucune alarme brute, tandis que sa référence symétrisée vaut 0,0431/0,0495 ; le `qhat` exact donne 0,432 sur D2 (IC HAC 95 % [0,123 ; 0,805]) et 0 sur D3. Les bits bruts ne satisfont pas le modèle i.i.d. à taux constant utilisé par `fpr_pred_iid`; ces nombres ne démontrent ni calibration prospective, ni absence de dérive réelle. Les IC de fenêtres chevauchantes sont souvent `NA`.

**E6, phase 1 sur la branche 23.** Le CSV a pour SHA-256 `4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249` ; 78 lignes viennent des fenêtres D6 et 112 de panels D5. Sur D6, les 941 jours de calib donnent 692 fenêtres de 250 jours ou 442 de 500 jours. Le seuil est ajusté sur ces mêmes fenêtres ; le FPR observé 0 est donc interne à l'échantillon et le palier suivant serait 0,24–0,57, pas une estimation précise d'un niveau 5 %. Les fenêtres sont corrélées et les alarmes se concentrent autour de l'épisode fin 2018. Le rapport G_ADD de 0,86–1,17 reste indéterminé ; `IC=NA` suit le critère conservateur préspécifié de moins de 10 blocs de longueur H, sans présenter ce seuil comme une nécessité générale du bootstrap par blocs ou du `deff`.

Sur D5, 2 000 panels de calibration et 2 000 panels de test indépendants donnent huit FPR principaux entre 0,0480 et 0,0575, dans la région binomiale à 99 % [0,0322 ; 0,0678]. Pour une rotation exploratoire PC1–PC2 et P3-D factoriel K = 1, H = 250, les rapports RMST_H sont 14,59 [13,84 ; 15,42], 67,71 [65,10 ; 70,35] et 105,42 [102,04 ; 109,07]. P1-D ne surveille qu'une hausse d'énergie ; cette rotation diminue la variance de son indice, ce qui explique une partie majeure du contraste. Le contrôle négatif PC2–PC3 reste au niveau nul, et la déformation préspécifiée PC2–PC4 n'atteint que G_ADD 1,03–1,16, indéterminé. L'ampleur de PC1–PC2 ne se généralise donc pas à F4. Les seuils D5 dépendent fortement du panel unique d'ajustement ; le biais de blanchiment hors échantillon (moyenne nulle du score : −1,64 pour K = 10, +3,69 pour le complet) empêche de lire le facteur Γ comme une propriété stable de la représentation.

### 2.8 Synthèse scientifique et portée des résultats

La démonstration acquise porte sur une **chaîne conditionnelle** : identité des routines reprises de l'Article B, formule de budget d'évidence, J1 sous générateurs connus, exactitude des signes quand la symétrie conditionnelle est imposée, et capacité de certains moniteurs linéaires à détecter une covariance injectée. La DPI impose toujours 𝓘_z ≤ 𝓘_x. Aucun résultat courant ne démontre qu'un JEPA augmente l'information, ni qu'il bat une référence linéaire ou P3-CS (b), ni que la dérive brute de D2/D3 est détectable de manière prospective. J2, J3 et J4 restent ouverts.

Trois causes distinctes expliquent les écarts observés : information disponible, alignement de cette information avec les canaux, et validité/calibration de la loi nulle. Les ratios N1/N2/N3 et l'écart P7/P3-C montrent qu'une information latente potentielle peut rester inutilisée par le dictionnaire ; ils ne prédisent pas un gain JEPA. E10 montre qu'un meilleur délai sous un null asymétrique peut refléter un excès de fausses alarmes. E6 montre qu'un très grand ratio peut refléter la cécité unilatérale du comparateur. Les prochains tableaux doivent juxtaposer délai, taux de détection, censure, FPR du même fond et degré d'alignement, avec des fonds injectés fixés avant lecture des résultats.

Les analyses de données brutes restent descriptives. D2, D3 et D4 sont sélectionnés par survie ; les frontières de régime gonflent les Sharpe estimés, et la symétrie centrale est rejetée sur plusieurs canaux. Le placebo par rotation et les fonds D6 sont donc indispensables. `results/audit/predicted_gains.csv` contient des `NaN` informatifs et ne peut pas fournir les gains prévus d'E1/E5. La preuve principale devra venir d'injections contrôlées et appariées, avec les séries réelles comme contexte et test de sensibilité.

## 3. Current State of the System and Handover

### 3.1 Organisation et localisation

- **Current System State — rôles :**
  - le chercheur principal : piste X, revues GO, application des révisions, lancement des agents ;
  - Claude dans le chat : piste T (théorie, rédaction, conception et révision des prompts, analyse des wrapups), sans jamais implémenter de stream ;
  - les agents de code, Claude Code (modèle Opus, effort `xhigh` ou `max`) ou Mistral Vibe (Large-4, `/thinking high`), selon la table de routage d'`INDEX.md`.
- **Current System State — localisation :**
  - répertoire de travail sur une machine locale (serveur SSH) : `~/JEPA-Drift-experiments` ;
  - synchronisé avec le dépôt GitHub distant `https://github.com/JEPA-Drift/JEPA-Drift-experiments`, dont les fichiers sont accessibles directement avec le connecteur (plugin) GitHub ;
  - checkout de l'Article B : `~/The-Whitening-Advantage-Experiments`, en lecture seule, au commit `a05f0d9c654b6692e626080c298acebc0f0a0b5c`. Ne jamais cloner son dépôt distant.
- **Current System State — cycle d'un stream :**
  1. `/plan` sur `prompts/streams/prompt-NN-<slug>.md`, avec des hypothèses explicites et leurs valeurs par défaut ;
  2. revue GO du chercheur dans `prompts/GO-stream-NN.md` ;
  3. plan final enregistré dans `prompts/plans/plan-NN.md`, avec une section « Décision GO intégrée », avant toute ligne de code ;
  4. exécution en TDD dans un worktree `stream-NN` (skills superpowers : executing-plans, test-driven-development, verification-before-completion) ;
  5. fin de stream, dans cet ordre : wrapup `prompts/wrapups/wrapup-NN.md`, puis `tools/reindex_graphify_jcodemunch.sh`, puis `make check`, puis un commit (Conventional Commits, sans trailer), puis `git fetch origin`, rebase sur `origin/main`, contrôle de la plage poussée, et `git push origin stream-NN:main` ;
  6. retrait de la copie non suivie du fichier GO dans l'arbre principal, puis `git merge --ff-only origin/main`.

### 3.2 Avancement

- **Current System State — fait :** streams 1 à 11, plus le complément 11b (sans prompt de stream : sa revue GO a servi de prompt). Tous sont fusionnés sur `main`. Dernier commit relevé : `9a36c2f` (stream 11) ; le hash du push de 11b n'a pas été relevé.
- **Current System State — non démarré :** le prompt 8b (nouveau) et les streams 12 à 28.
- **Current System State — paquet de révisions du tour 3 :** livré dans le fil mais non retrouvé dans le dépôt distant consulté via le connecteur GitHub au moment du wrap-up. Vérifier d'abord : `prompts/streams/prompt-08b-hygiene.md`, la section « Replanification » d'`INDEX.md`, les changements de lecture dans `prompt-12-e1.md`. Le paquet est restitué ci-dessous.
- **Current System State — paquet, `AGENTS.md` :**
  - **A1** : la puce « e-detector » gagne la borne P∞(alarme avant H) ≤ H/γ et la règle d'entrée des e-processus dans [−1, 1] (passer 2·`exact_sign_stream` ou 2·f) ; ajout d'une puce « Readings at a fixed horizon H » : γ_H = H/α ; lecture exacte au treillis à H via `select_threshold(...)["threshold"]` (point milieu), jamais `lam` ; bootstrap (H = 750) et randomisation ; ARL₀ réservé à E2/E3 ; délai = alarm_index − tau_star + 1.
  - **A2** : puce « Gains » : G_floor tiré de la dérive injectée ; G_ADD_av à γ_H égal ; G_ADD_ex au même niveau de treillis à H ; prévisions à partir de la dérive injectée, de l'alignement a_max et de `floors`, jamais de `predicted_gains.csv`.
  - **A3** : section « Data » : ajout des faits de panel et des constats de l'audit (symétrie rejetée ; sélection ; R9).
  - **A4** : « Repository layout » mis à jour (modules réels, `docs/manifests/`, fichiers GO, master synchronisé, Orchestration historique).
  - **A5** : étape 4 de fin de stream unifiée (depuis `main` : `git push origin main` ; depuis un worktree : rebase, puis `git push origin stream-XX:main`, jamais la branche elle-même).
  - **A6** : épinglage du commit de l'Article B.
  - **A7** : nouvelles règles :
    - langues ;
    - style de code : docstrings d'une ligne ; aucun commentaire sauf `# ponytail:` (plafond délibéré) ; aucun `# noqa` ; ports verbatim gelés ; aucune marque d'IA ;
    - workflow GO ;
    - format des wrapups : anglais ; sections Context, Validated Results, Errors and Dead Ends, Current State, Vigilance Points, Recommendations ;
    - garde pré-J4 ;
    - réutilisation de `run_pipeline` et `null_check` avec un `state` sans dérive ;
    - torch seulement dans `.venv` ;
    - `make check` sous 5 minutes.
  - **A8** : en worktree, `data/raw/` est un vrai répertoire, avec un lien par sous-répertoire lu (`d3_yf`, `baf`, `electricity` ; `eurofidai` seulement pour D4).
- **Current System State — paquet, `INDEX.md` et Orchestration :**
  - **I1** : note de révision ;
  - **I2** : étape 4 de push alignée sur A5 ;
  - **I3** : table de routage avec une colonne « État » et les lignes 8b et 11b ; les streams 1–11 sont marqués « fait », 12–28 « révisé » ; prérequis mis à jour (12 : 2–8, 8b, 11 ; 13 : 4–8, 8b ; 14 : 3, 6, 8, 8b ; 17 : 3, 6, 8b ; 19 : 5, 7, 8b, 11, 17 ; 22 : 16, 17, 19, 21, 23 phase 2 ; 23 : phase 1 sur 5 et 7, plus 17 pour P4-D, phase 2 sur 16 ; 25 : 8b et 21) ; streams Opus restants : 12, 13, 14 et 22 ;
  - **I4** : section de replanification, à appliquer sans dates : 8b → {12, 14, 13 décalé, 17, 23 phase 1} → {16, 21, 19, 18, 15} → {22, 23 phase 2, 20, 26} → {25, 24, 27, 28} ;
  - `Orchestration_Streams_v5.md` : ajouter une note qui le déclare historique et renvoie à `INDEX.md`.
- **Current System State — paquet, prompt 8b (nouveau, routé Vibe High) :**
  - `jepadrift/data_loader/chars.py` : `load_chars_tensor(dataset, rows=None) -> (C (T, N, P) float64, names)`, aligné sur `ret_wide.npy`, `dates.npy` et `assets.json` ; NaN conservés ; `impute_zero(C) -> (C0, n_imputed)` ; ValueError pour `d2_us97` ;
  - `jepadrift/stats/drift.py` : `debiased_sr2`, `mbb_indices`, `_ci` (exporté sous le nom `shifted_percentile_ci`), `transitions` et `rotate_phases`, déplacés depuis l'audit sans modification de corps ; l'audit les réexporte ; sorties de l'audit `--quick` identiques au SHA-256 ;
  - `pipelines.horizon_gamma(H, alpha=0.05) = H/alpha` ;
  - fixture D1/D2 reconstruit sous une racine temporaire (monkeypatch de `REPO_ROOT` et des chemins dérivés), avec comparaison des SHA-256 et des entrées D1/D2 du manifeste ; après `make check`, `git status --porcelain` doit être vide ;
  - `tools/check_prompts.py` et cible `make prompts-check` : vérifie que chaque fichier de stream est une sous-chaîne exacte du master ; `--sync-master` réécrit les blocs du master à partir des fichiers de stream ; résultat attendu : 29/29 ;
  - ajout des écarts C-D3-survivor-correction et C-D4-survivor ;
  - mise à jour du layout d'AGENTS.md.
- **Current System State — paquet, texte des deux écarts à ajouter (français ; date du commit à renseigner) :**
  - « C-D3-survivor-correction — biais de survie de D3. Correction de `C-D3-survivor`. Un univers formé des constituants actuels du S&P 500, projeté en arrière jusqu'en 2000, est biaisé par la survie : un titre n'y figure que parce qu'il a survécu et a rejoint l'indice. `d3_239` (les 239 plus longs historiques parmi ces constituants, `C-D3-no239`) l'est doublement. Portée : les expériences sur fonds symétrisés D6 avec dérives injectées en dépendent peu ; les mesures sur données brutes (recensement, E8, placebos) héritent du biais et servent d'appui, jamais de preuve de détectabilité. Aucune donnée n'est modifiée. »
  - « C-D4-survivor — sélection de D4. D4 contient 498 titres EUROFIDAI retenus pour au moins 5 000 observations entre 2001 et 2026 (places AMS, BRU, EPA, LSE, MIL, XET). Cette sélection sur la longueur d'historique est une sélection par la survie ; l'export ne fournit ni date de radiation ni statut (radiations inférées par l'absence de données), et MIL n'a pas de données pour 2024–2026. `in_universe` couvre 91 % des cellules : les appelants choisissent des sous-panels complets sur leur fenêtre (`inject` exige un panel fini). D4 n'a pas de secteur GICS : F2 n'y utilise que les quatre caractéristiques continues. »
- **Current System State — paquet, prompt 12 (E1, remplacement complet) :**
  - **lectures** : à horizon (γ_H = H/α ; exacte au treillis à H ; bootstrap ; randomisation) ;
  - **état** : ajusté sur les lignes de calib d'origine, sans dérive ; jamais `state=None` avec des enregistrements injectés ;
  - **bras A** :
    - convention (a), SR ∈ {2, 4, 8} (SR = 1 est censuré : τ_γ ≈ 5 340 j à γ_H = 40 000) ;
    - familles F3, F1 et F2, F2 sur `d3_239` seulement ;
    - 1 000 onsets par cellule, H = 2 000 ;
    - P1-C sur 20 titres tirés ; P2-C anytime-valid, plus la lecture Article B (bootstrap recalibré sur une symétrisation, H = 750) en secondaire ;
    - P3-C : dictionnaire ; meilleur canal exact et mélange porté par Holm 1 % en diagnostic ;
    - P3-CS (b) en principal, (a) en secondaire ; P7 comme borne ;
    - P3-D à part, à H = 750, comme preuve d'orthogonalité ;
  - **bras B (J2)** :
    - convention (b) : F3 avec un SR RMS par titre ∈ {2, 4} ; F2 avec κ ∈ {1, 2} ;
    - grille d'amplitude réglée pour que le délai médian de P3-C reste dans [20 ; 0,8·H] (degré de liberté consigné) ;
    - N ∈ {8, 16, 32, 64, 97} pour D2 et {8, 16, 32, 64, 128, 239} pour D3 ; 20 sous-ensembles emboîtés ; 200 onsets ;
    - pente de log G_ADD en log N = − pente de log ADD médian ; médiane définie seulement si le taux de détection dépasse 50 % ; a_max(N) rapporté ;
  - **bras C (descriptif)** : parts dans le budget, débiaisées, avec leurs placebos par rotation ; ce sont des bornes supérieures. Alarmes sur données brutes avec recentrage q̂ ; `predicted_gains.csv` cité tel quel ;
  - **prévisions** : à partir des Δ injectés ;
  - **résumé J2**, critères (i) à (iv) avec verdict PASS/FAIL :
    - (i) |FPR − niveau du treillis| ≤ 1 point sur D6, à H ∈ {750, 2 000} ;
    - (ii) pente de P2-C sur F3 nulle pour N ≥ 20 : IC contenant 0, ou borne haute < 0,15 ;
    - (iii) pente de P3-C sur F2 positive, IC excluant 0, avec attribution en cas d'échec ;
    - (iv) table des gains 1 → 2 → 3 → 3-CS à SR = 4 ;
  - **contraintes** : graines (12, cellule, réplication) ; pas de tableau de plus de 2 Go par paquet ; option `--quick` ; aucune ligne de 2020 ou après.
- **Current System State — paquet, prompt 13 (E3) :**
  - fonds : D5 (`sim.Garch`, axe de réplication de `garch_panel` sous test de non-régression), D6 et placebo brut ;
  - FPR(H) à H ∈ {750, 2 000} : 20 000 trajectoires par cellule de signe ;
  - ARL₀ des e-détecteurs à γ ∈ {20, 100, 252}, T_max = 60γ, censure rapportée ;
  - Γ^spec contre Γ^op ; P3-D sur la calib (H ≤ 941), et `pre_monitor` pour H = 2 000 ;
  - asymétrie brute canal par canal, en flux exact et recentré ;
  - pénalité de dépassement, à reproduire à ±5 % : ARL₀ ≈ 2 587 contre ≈ 889 (δ = 0,5, λ = 6) ; 1 894 contre 669 (δ = 1, λ = 3) ; signe 213 contre 214 ;
  - encodeurs à fenêtre L ∈ {5, 20, 60} ;
  - contrôle J2 ; graines (13, cellule, réplication).
- **Current System State — paquet, prompt 14 (CA-T-JEPA) :**
  - torch CPU dans `.venv` : roue compatible avec numpy 2.4.4, épinglée ; `pip freeze` de numpy, scipy et pandas inchangé ; `make j1` redonne `e315e537…` ;
  - caractéristiques par `load_chars_tensor("d3_239")` ;
  - `jepadrift/jepa/representation.py`, sous-classe de `Representation`, dont le `state_hash` inclut le SHA-256 du point de contrôle ;
  - entrée paresseuse `ca_tjepa` dans `representations/extract.REGISTRY` ; extraction par `python -m jepadrift.representations.extract --dataset d3_239 --rep ca_tjepa --ckpt ckpt/<hash>` ;
  - traitement par lots autorisé seulement s'il est bit-identique au traitement jour par jour ;
  - les 4 gardes torch doivent tourner ; déterminisme ; au plus 1 M de paramètres ; architecture inchangée (voir 3.3).
- **Current System State — paquet, prompt 19 (E4) :**
  - `d3_500` et D4 en sous-panels complets ;
  - grilles réglées comme au prompt 12 ;
  - lecture γ_H à H = 2 000 ;
  - SPLL en numpy (`monitors/spll.py`) ;
  - pentes attribuées à l'information ou à l'alignement ; audit réduit par sous-ensemble.
- **Current System State — paquet, prompt 22 (E5) :**
  - références : P3-C, P3-CS (b) et P4-C ;
  - SR ∈ {2, 4, 8} ;
  - r(D) par injection appariée à travers l'encodeur gelé ; a_max rapporté ;
  - porte J4 avec P3-CS (b) ; option mélange exclue des verdicts.
- **Current System State — paquet, prompt 23 (E6) :**
  - phase 1 linéaire (P1-D, P3-D, puis P4-D) et phase 2 avec P5-D ;
  - fonds : fenêtres D6 de la calib à H ∈ {250, 500}, chevauchement signalé ; contrôles D5 indépendants (N = 239, ρ = 0,40, t₇) ;
  - F4 : r ∈ {1,25 ; 1,5 ; 2}, θ ∈ {15°, 30°, 45°}.
- **Current System State — paquet, prompt 25 (E8) :**
  - composition des datations ; placebo par rotation sur chaque mesure ;
  - recentrage q̂ sur données brutes ;
  - parts dans le budget comme bornes supérieures ;
  - comparaison au recensement de l'Article B (80,3 % à γ = 20, R16-out-of-budget-frac) ;
  - exécution seulement avec la configuration gelée.
- **Current System State — paquet, modifications ciblées :**
  - 15 : faits de `preproc.json` ; licence CC BY 4.0 ; écart C-Z-baf (`dates` remplacé par (`month`, `row`)) ; registre paresseux ; règle torch ;
  - 16 : exécutions parallèles, une par processus, résultats indépendants du nombre de processus (`--jobs 9`) ; lecture post hoc ; gardes torch au vert ;
  - 17 : chargeur de caractéristiques ; panels déséquilibrés traités par masque `in_universe`, sans imputation de rendement ;
  - 18 : réutiliser `external/cd-dfm/` ; `external/cddfm-venv/` en cas de conflit ;
  - 20 : mélange comparé sur D5, porte rapportée sur D6 ; lecture γ_H ;
  - 21 : le runner appelle les `main(argv)` existants ; `FROZEN.json` inclut les manifestes de données ; `make freeze` ; `MAPPING.md` initialisé ; note sur le CSV d'E2 en CRLF ; fusion avant le stream 22 ;
  - 24 : `device_fraud_count` exclu ; test d'échangeabilité intra-mois (C-BAF-order) ; prévalence citée ;
  - 26 : lecture γ_H ; vieillissement limité à 2016–2019 avant J4 ;
  - 27 : violations naturelles et rendements nuls réels ; lecture γ_H ;
  - 28 : lien `data/raw/electricity` ; lecture γ_H.
- **Current System State — piste T en attente :**
  - lot 3 : §1 v0 réécrit en lecture budget, Tableaux 1–3 v0, T6–T7 (Γ_z spectral contre opérationnel, échelle d'efficacité des moniteurs) ;
  - amendements du §3 : prévisions de la Prop. 3 sur fonds réels par le multiplicateur de dictionnaire avec l'alignement mesuré ; validité des mélanges sous dépendance ; référence au §2 ;
  - rédaction du §2 puis des §4–§7 au fil des résultats ;
  - Article B : la part hors budget du recensement est une borne inférieure, argument utilisable en version caméra.
- **Current System State — prochaines étapes (ordre, sans calendrier) :**
  1. vérifier, puis appliquer, le paquet de révisions ;
  2. lancer le stream 8b ;
  3. lancer en parallèle 12 et 14 (Opus xhigh), puis 13 (Opus, démarrage décalé ; repli Vibe High si le quota Opus sature), 17 et 23 phase 1 (Vibe) ;
  4. puis 16, 21, 19, 18 et 15 ;
  5. puis 22, 23 phase 2, 20 et 26 ;
  6. puis 25, 24, 27 et 28 ;
  7. choix de la conférence (rang B, A ou A*) à partir de fin novembre 2026.

### 3.3 Plan expérimental en vigueur (plan v4, amendé)

- **Jeux de données :**

  | Jeu | Contenu                                                                                  | Rôle                                                                                                              |
  | --- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
  | D1  | ETF-4 (SPY, PFF, VNQ, BWX)                                                               | Référence univariée, recensement                                                                                  |
  | D2  | US-97, panel de survivants                                                               | Référence du pooling                                                                                              |
  | D3  | S&P 500 : `d3_239`, `d3_500`                                                             | Coupe principale, avec caractéristiques                                                                           |
  | D4  | EUROFIDAI : 498 titres, données propriétaires                                            | Échelle en N, Europe                                                                                              |
  | D5  | Monte Carlo : gaussien i.i.d. ; GARCH(1,1)-t₇                                            | Validation des bornes                                                                                             |
  | D6  | Symétrisés SYM-D2, SYM-D3, SYM-D4 : chaque journée entière reçoit un signe de Rademacher | Conserve \|x\|, les corrélations et la volatilité ; efface les dérives et le levier ; seul support des injections |
  | D7  | BAF                                                                                      | Tabulaire, synthétique                                                                                            |
  | D8  | Electricity (UCI), SWaT, WADI (option)                                                   | Second domaine                                                                                                    |

- **Découpages (D2–D4) :** pretrain [2005-01-01, 2016-01-01), calib [2016-01-01, 2020-01-01), monitor [2020-01-01, fin], avec un embargo de 65 jours de bourse après chaque frontière. Sur `d3_239`, la calib effective court sur les lignes 4090–5030 (941 jours, 2016-04-07 → 2019-12-31). BAF : mois 0–2 (fit), 3 (calib), 4–7 (monitor).
- **Familles de dérives** (injectées dans l'espace des rendements, jamais dans z ; amplitude par convention (a) I_target = SR²/504, ou (b) RMS des Sharpe par titre, valant 1 pour F1/F3 et κ pour F2) :
  - F1 : primes factorielles BΔλ ;
  - F2 : largeur pilotée par les caractéristiques, (C_tΔγ) résidualisée par GLS sur les chargements ;
  - F3 : translation du mode de marché le long de b₁ = v₁√λ₁ ;
  - F4 : second ordre, par déformation X + (√r − 1)V_SV_SᵀX ou par rotation de Givens.
- **Pipelines :**
  - P1-C : flux d'étiquettes (Article B) ou flux de signe exact ;
  - P1-D : énergie, seuil λ = 65·Γ̂ ;
  - P2-C : fraction de signes ;
  - P3-C et P3-D : PCA-orthogonale, PC1 suivie comme canal marché séparé ;
  - P3-KF : PCA « queue », SPLL de Kuncheva ;
  - P3-CS : coupe de degré 0 et rangs ;
  - P4-C et P4-D : IPCA, CD-DFM (facteurs cash-neutral, K = 11) ;
  - P5-C, P5-D, P5-MAE, P5-TEMP, P5-ADAPT : CA-T-JEPA et ses variantes ;
  - P6-D et P6-C : BAF (martingale conforme ; e-détecteur sur l'erreur d'un gradient boosting) ;
  - P7 : oracle à direction connue.
- **Expériences :**

  | Exp. | Section  | Objet                            | Priorité                 |
  | ---- | -------- | -------------------------------- | ------------------------ |
  | E1   | §2       | Le problème : gains 1 → 2 → 3    | A                        |
  | E2   | §5.1     | Validation des bornes (faite)    | A                        |
  | E3   | §5.2     | Calibration sous H₀              | A                        |
  | E4   | §5.3     | Échelle en N, P3-KF              | A/B                      |
  | E5   | §5.4     | JEPA contre références linéaires | A/B/C                    |
  | E6   | §5.5     | Second ordre (F4)                | A (phase 1), B (phase 2) |
  | E7   | §5.6     | Absorption                       | C                        |
  | E8   | §5.7     | Régimes réels                    | A/B                      |
  | E9   | §5.8     | BAF                              | B                        |
  | E10  | Annexe D | Robustesse                       | C                        |
  | E11  | Annexe D | Second domaine                   | C                        |

- **Jalons (critères seulement) :**
  - J1 (passé) : validation E2 ;
  - J2 : critères (i) à (iv) d'E1/E3 ;
  - J3 : RankMe de la tête de lecture ≥ 0,5·D, et E6 phase 1 comme évidence pour C1 ;
  - J4 : configuration gelée (`configs/FROZEN.json`), puis porte d'E5 : G_ADD(meilleur de P3-CS (b) et P4 → P5) ≥ 1,25 sur au moins deux familles parmi F1, F2 et F4, IC excluant 1 → titre A, sinon titre B ;
  - J5 : CSV complets pour tous les items A et B ;
  - J6 : v1 gelée.
- **Seuils de la thèse :**
  - pooling : pente positive au J2, et G_ADD(P2 → meilleur latent) ≥ 2 au plus grand N, IC excluant 1 ;
  - plancher univarié : au moins 25 % des phases datées dans le budget oracle à ARL₀ = 252, contre 2 sur 66 dans l'Article B. Comparaison désormais à faire contre le placebo, à cause de la sélection.
- **Contingences :**
  - C1 : le second ordre devient l'axe principal (un ratio de variance de 1,5 à 2 porte 24 à 77 fois le budget d'une dérive de SR = 1) ;
  - C2 : accent sur les domaines à fort rapport signal sur bruit (BAF, IoT) ;
  - C3 : titre B ;
  - C4 : raccourcissement dans l'ordre E11 → E10 → E7 → dictionnaire (E5-C) → MAE, transmission et prétexte temporel (E5-B) → E6 → E4 sur D4 → E9 ;
  - intouchables : E1, E2, E3, E4 sur D2–D3, le cœur d'E5 et E8 sur le S&P 500.
- **Risques suivis** (registre du plan v4) :

  | Code | Risque                                         | Suite                                                 |
  | ---- | ---------------------------------------------- | ----------------------------------------------------- |
  | R3   | Antériorité des composantes de faible variance | Citer ; reproduire par P3-KF                          |
  | R4   | Absorption                                     | Encodeur gelé, contrats                               |
  | R5   | Calibration latente                            | Flux de signe exacts                                  |
  | R6   | Dimension et géométrie                         | D ≤ 16                                                |
  | R7   | Attribution                                    | P3-CS dans chaque tableau                             |
  | R9   | Audit bruité                                   | Matérialisé                                           |
  | R10  | Localisation rare                              | Partiellement matérialisé                             |
  | R11  | Peu de phases réelles                          | Données réelles en appui seulement                    |
  | R12  | BAF synthétique                                | « Dérive native d'un jeu synthétique »                |
  | R14  | Biais de survie                                | Étendu à D3 et D4                                     |
  | R16  | Entrées de CD-DFM                              | Caractéristiques tirées des rendements                |
  | R18  | Degrés de liberté                              | Gel au J4                                             |
  | R20  | Statut de la Prop. 3                           | Atteignabilité seulement                              |
  | R22  | Propriété intellectuelle                       | Clauses CIFRE de LUSIS ; EUROFIDAI non redistribuable |

- **Structure cible de l'article :**
  - §1 Sharpe ceiling and objective ;
  - §2 Problem on real data ;
  - §3 Concentrating exploitable divergence ;
  - §4 Representations and latent monitors ;
  - §5 Experiments (ordre E2, E3, E4, E5, E6, E8, E9, E7) ;
  - §6 Related work ;
  - §7 Limitations ;
  - annexes : A preuves, B génération des données et des dérives, C tableaux longs, D résultats complémentaires, E reproductibilité ;
  - chaque sous-section expérimentale s'ouvre sur un encadré « Configuration » ;
  - gabarit : budget de 8 pages prévu pour un format de type ICML, à adapter à la conférence retenue.
- **CA-T-JEPA (architecture) :**
  - tronc : un jeton par actif, MLP([x_{i,t}/s_i, C_{i,t}]) ; 2 à 4 couches d'auto-attention équivariantes, sans encodage de position (d_model 64, 4 têtes) ;
  - cible : masquage de 30 à 50 % des actifs ; cible EMA (0,996 → 0,9995) ; prédicteur à requêtes C ;
  - perte : L2 latente, plus un terme de variance de type VICReg ;
  - têtes : impaire ½[g(x) − g(−x)] et paire ½[g(x) + g(−x)], lues par une ACP blanchissante sur la calib, D ∈ {2, 4, 8, 16} ;
  - variantes : MAE et prétexte temporel ;
  - interdits : BatchNorm, RevIN, EMA active à l'extraction ;
  - pré-entraînement sur `d3_239`, segment `pretrain`.

### 3.4 Execution Environment

- **Machine :** Rocky Linux 9.6 (Blue Onyx), x86_64, noyau 5.14.0-570.55.1.el9_6.x86_64 ; AMD EPYC 8224P, 24 cœurs (48 logiques) ; 187 Go de RAM.
- **Interpréteur :** Python 3.12.9 dans `.venv`, construit sur `~/miniforge3/envs/Trading/bin/python`. Chaque commande commence par `source ~/miniforge3/etc/profile.d/conda.sh && conda activate Trading && source .venv/bin/activate`. Ne jamais lancer le python de Trading seul : il embarque numpy 1.26.4 et torch 2.5.1.
- **Paquets de `.venv` :** numpy 2.4.4, scipy 1.17.1, pandas 3.0.6, pyarrow 26.0.0, statsmodels 0.15.0, matplotlib 3.11.2, pytest 9.1.1, pyflakes 4.0.3, PyYAML 6.0.3, yfinance 1.7.0 (avec beautifulsoup4 4.15.0, lxml 6.1.3, requests 2.34.2, curl_cffi), kaggle 1.6.17. BLAS : scipy-openblas 0.3.31. torch est absent de `.venv` ; le stream 14 l'installe.
- **Environnement annexe `external/articleB-venv` :** numpy 1.26.4, scipy 1.16.2, pandas 2.3.2, statsmodels 0.14.5, matplotlib 3.10.6, yfinance 1.2.0, river 0.23.0, joblib 1.4.2, pytest 9.0.3, PyYAML 6.0.3 ; roues openblas64. Usage : identité de l'Article B seulement.
- **make :** GNU Make 4.4.1, issu de l'environnement conda `jepa-make`, via le lien `.venv/bin/make`. Si `.venv` est recréé : `ln -sf ~/miniforge3/envs/jepa-make/bin/make .venv/bin/make`.
- **Variables d'environnement :** OMP_NUM_THREADS = MKL_NUM_THREADS = OPENBLAS_NUM_THREADS = 1, MKL_CBWR = COMPATIBLE, PYTHONHASHSEED = 42 (exportées par le Makefile) ; MPLBACKEND = Agg pour les figures.
- **Graines :** `np.random.SeedSequence` à clés (stream, cellule, réplication) ; pool `spawn` ; résultats indépendants du nombre de processus.
- **Git :** `core.autocrlf=input`. Hooks installés par `make hooks` : `tools/pre-commit` bloque les chemins EUROFIDAI et les fichiers > 50 Mo, réinitialise `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE` et `GIT_QUARANTINE_PATH`, puis lance `make check` ; `tools/pre-push` contrôle la plage poussée.
- **Outils :** reindex de graphify et `jcodemunch-mcp` par `tools/reindex_graphify_jcodemunch.sh`.
- **`make check` :** pyflakes sur `jepadrift`, `experiments` et `tests`, hors `jepadrift/stats/garch.py` ; puis pytest sur `tests/test_contracts.py` et `tests/test_decoupling.py` ; puis pytest sur le reste. Tous les appels pytest portent `--ignore=external`.
- **Recette de worktree :**

```bash
git -C ~/JEPA-Drift-experiments fetch origin
git -C ~/JEPA-Drift-experiments worktree add -b stream-NN ~/JEPA-Drift-stream-NN origin/main
ln -s ~/JEPA-Drift-experiments/.venv ~/JEPA-Drift-stream-NN/.venv
ln -s ~/JEPA-Drift-experiments/external ~/JEPA-Drift-stream-NN/external
mkdir -p ~/JEPA-Drift-stream-NN/data/raw
ln -s ~/JEPA-Drift-experiments/data/raw/d3_yf ~/JEPA-Drift-stream-NN/data/raw/d3_yf
ln -s ~/JEPA-Drift-experiments/data/raw/baf ~/JEPA-Drift-stream-NN/data/raw/baf
```

  Utiliser des chemins absolus développés pour les liens. Lier `eurofidai` seulement si le stream lit D4.

- **Lancement des agents :**

```bash
tmux new-session -d -s s12 'cd ~/JEPA-Drift-experiments && claude --effort xhigh'
tmux send-keys -t s12 "$(cat prompts/streams/prompt-12-e1.md)" Enter
tmux new-session -d -s s17 'cd ~/JEPA-Drift-experiments && vibe'
tmux send-keys -t s17 '/thinking high' Enter
tmux send-keys -t s17 "$(cat prompts/streams/prompt-17-ipca.md)" Enter
```

### 3.5 Critical Points of Vigilance

- **Version du dépôt :** vérifier que le paquet de révisions du tour 3 est appliqué avant tout lancement des streams 12 et suivants. Sinon, ces streams exécuteraient des spécifications invalidées : lecture γ ∈ {20, 252}, F2 sur D2, P3-D à 2 000 jours, gains prévus tirés de l'audit.
- **Lot 1 gelé :** `floors.py`, `test_floors.py`, `sec3_theory.tex`, `appA_proofs.tex` et l'addendum bibliographique ne sont jamais corrigés en place ; les anomalies vont dans `docs/DEVIATIONS.md`. Seul `e2_floor_validation.py` a changé (stream 5 : import depuis `jepadrift.sim`), à sortie identique.
- **Hash d'E2 :** `e315e537…` est calculé sur le fichier disque, en fins de ligne CRLF : ne jamais normaliser. `make j1` réécrit la ligne de durée du résumé et du journal ; les restaurer par `git checkout --` si le hash est inchangé.
- **Détection :**
  - comparer `S > sel["threshold"]` (point milieu), jamais `sel["lam"]` ;
  - entrées des e-processus dans [−1, 1] ;
  - `lattice.arl0` est limité à (L + 1)^sided ≤ 10 000 ;
  - MIX est fixé à H = 5 000 ;
  - la marge d'ARL₀ de l'e-détecteur SR est mince (+9 à +11 %) : un échec d'origine plateforme se consigne, il ne se résout jamais par un nouveau tirage de graines ;
  - `jepadrift/stats/garch.py` reste hors pyflakes et identique à l'octet.
- **Injection :**
  - `inject` exige un panel fini : sous-panel complet pour `d3_500` et D4 ;
  - F2 exige C_t (absent pour D2) ; information réalisée de F2 tirée de `delta` ;
  - τ* dans 2005–2019 avant J4 ;
  - mettre `fit_background` en cache.
- **Représentations :**
  - ajustement sur des lignes sans dérive ;
  - variance de calib des coordonnées blanchies par Ledoit–Wolf comprise entre 0,49 et 1,03 ;
  - `extract` ne couvre que `d2_us97` et `d3_239` ;
  - `transform_panel` boucle jour par jour.
- **Pipelines :**
  - P3-D limité à H ≤ 941 sur la calib ;
  - les cibles nulles des e-détecteurs restent la borne faible H/γ ;
  - la porte du mélange échoue sur D2 ;
  - P3-CS (a) est faible ;
  - le seuil de P2-C sur D6 se calibre sur une symétrisation (λ_boot 33,25 contre 20,05 sur données brutes à K = 20) ;
  - `log_average_betting_eprocess` matérialise un tableau (J, K, T) d'environ 1,6 Go par paquet à H = 2 000.
- **Audit :**
  - R9 matérialisé ;
  - sélection des frontières : SR² de marché aux transitions datées inutilisable comme référence ;
  - N2 brut gonflé par le bruit d'estimation : citer `lw60_net` ;
  - symétrie rejetée sur données brutes (canaux listés en 2.4) ;
  - `predicted_gains.csv` est descriptif ; ses NaN restent NaN.
- **Données :**
  - biais de survie de D2, D3 et D4 ;
  - BAF synthétique : « dérive native d'un jeu synthétique » ;
  - les prix ajustés de Yahoo sont révisés à chaque téléchargement : les panels dérivés commités font foi ;
  - D4 sans GICS ni radiations.
- **Discipline pré-J4 :** aucun choix d'hyperparamètre, de seuil, de D* ou de conception sur la fenêtre de test, et aucune évaluation dessus avant le gel. Ensuite, toute exécution sur la fenêtre de test exige `configs/FROZEN.json`.
- **Concurrence :**
  - ne jamais lancer `git stash`, `git checkout` ou `git reset` dans le worktree d'une autre instance ;
  - indexer par chemin explicite, après un `git status` frais ;
  - ne jamais indexer les liens du worktree ni les fichiers D1/D2 réécrits par le fixture (jusqu'au stream 8b) ;
  - ne pas lire `prompts/plans/plan-11-vibe.md`, obsolète.
- **Données propriétaires :** rien sous `data/raw/eurofidai/` ou `data/derived/d4_eurofidai/` n'est jamais commité, journalisé ou poussé ; aucun fichier de plus de 50 Mo ; le push n'est autorisé que tant que l'adresse du dépôt n'est ni diffusée ni liée à une publication (commits anonymes).
- **Propriété intellectuelle :** les clauses CIFRE de LUSIS imposent un accord écrit avant toute publication liant le dépôt.

### 3.6 État opérationnel daté du 23 octobre 2026 — prévaut sur les mentions historiques de 3.1–3.5

- **Git et portée des résultats :** `main` local est à `c2848234bf48bb56699983e7470f0e4bc4a7c3f1` (fusion du stream 27), avec 11 commits d'avance sur le dernier `origin/main` suivi localement (`ef63362`). Le stream 8b a été fusionné par `33d847d` ; le stream 27 est clos, fusionné, et son worktree a été libéré. Aucun push, rebase ou force push n'a été exécuté dans ce transfert. Au début du présent travail, `main` était propre hors `prompts/wrapups/handover-01-11.md` non suivi ; le nouveau fichier `prompts/wrapups/handover-01-27.md` est également non suivi tant qu'il n'est pas ajouté par une action ultérieure. La disponibilité sur GitHub des résultats E10, E6 et du présent transfert ne doit pas être présumée.
- **Prompts et conventions actuelles :** le paquet v6 et 8b sont appliqués ; `prompts/Orchestration_Streams_v6.md`, `prompts/streams/prompt-08b-hygiene.md`, `prompts/GO-stream-08b.md`, `prompts/wrapups/wrapup-08b.md` et `tools/check_prompts.py` existent. Le contrôle historique `make prompts-check` donnait 29/29. `CLAUDE.md` est maintenant le fichier réel et `AGENTS.md` son lien relatif, à l'inverse de la description historique. La table de modèles de `prompts/streams/INDEX.md` est supplantée par la directive du chercheur : toute session Claude Code lancée par l'orchestrateur doit utiliser **Opus 5.5, effort Max**, depuis `.venv`. Pour quitter `/plan`, faire recharger explicitement les MCP `graphify` et `jcodemunch` dans chaque session.
- **Environnement torch :** le compromis conda-forge `cpu_generic` à 65 paquets pour le stream 14 est accepté. L'étape 1 est un environnement dans `.venv/torch-cf`, ciblé par `PYTHONPATH`. L'étape 2, fichier `.pth` dans `.venv`, ne vient qu'après `make check` et régénération J1 identique à l'octet, en gardant les fins de ligne CRLF natives. Lors du dernier audit ponctuel, `.venv/torch-cf` était absent : PyTorch n'était pas disponible dans `.venv` et les streams 14/18 n'étaient pas débloqués. Les commandes du stream utilisent `.venv/bin/python` et `.venv/bin/pytest`; le Python de Trading ne sert pas à lancer les streams.
- **Convention de lignes D3 :** la section historique 3.3 note la calib `d3_239` aux lignes 4090–5030, tandis que le bilan E6 du stream 23 la note `[2834, 3775)` ; les deux donnent 941 jours et les mêmes dates (2016-04-07 → 2019-12-31). L'origine de cette différence d'indices n'a pas été vérifiée ici : utiliser les dates et le manifeste pour tout alignement, puis résoudre la convention d'index avant une indexation croisée.
- **Quota et supervision :** le chercheur a signalé l'épuisement du quota Claude jusqu'au dimanche 25 octobre 2026 à 12:00 UTC+1 (11:00 UTC). La surveillance périodique `jepa-stream-watch` et son écriture toutes les 30 minutes dans `logs/streams_status.log` ont été arrêtées ; un contrôle ponctuel n'a montré aucun autre watcher périodique. Les sessions Claude Code existantes n'ont pas été interrompues. Ne relancer ni surveillance périodique, ni sollicitation des sessions, avant notification explicite du chercheur que le quota est rétabli ; l'heure annoncée n'est pas une autorisation automatique de reprise.

| Stream | État constaté sans nouvelle exécution Claude | Prochaine condition |
| --- | --- | --- |
| 08b | Fusionné sur `main` ; chargeur de caractéristiques, statistiques partagées, fixture D1/D2 et vérificateur de prompts livrés. | Clos. |
| 12, E1 | Worktree propre à `c284823` ; GO antérieur présent, aucun plan final, code ni CSV E1. | Terminer la revue du plan, surtout réinitialisation CUSUM, fenêtre et critères J2, avant exécution. |
| 13, E3 | Travail non commité : plan révision 3, GO, `experiments/e3_calibration.py`, `jepadrift/stats/intervals.py`, adaptation E10. Aucun test/configuration/CSV E3. | Terminer implémentation et contrôle de FPR, ARL₀, Γ et null brut ; aucune conclusion E3 à ce stade. |
| 14, CA-T-JEPA | Worktree propre à `c284823`, pas de code ni de point de contrôle ; stratégie d'isolation et encodeur EMA approuvés, plan encore soumis aux gardes d'environnement et de J1. | Stager `cpu_generic`, corriger le chemin `make`, contrôler empreintes et CRLF, puis seulement autoriser `.pth` et développement. |
| 17, IPCA | Branche `f67accfd01da7605900ac0230ad5fce1e18b99d7`, premier commit du socle C/extraction partagé ; `tests/test_ipca.py` non suivi. IPCA/P4-C/P4-D et CSV absents. | Reprendre après quota, compléter IPCA et vérifier les contrats ; ne pas annoncer P4 comme livré. |
| 18, CD-DFM | Worktree propre à `c284823`, plan recevable, aucun code/résultat. | Attendre PyTorch effectif du 14 ; le clone externe épinglé à `37a1dfb` ne contient pas `data.dataset`, `preprocess_panel` ni licence : diagnostic documentaire si cette chaîne reste absente. |
| 23, E6 | Branche `3d0bd2071cb86afc6b196b5020ff729204746a93`, phase 1 D5/D6 fusionnée dans cette branche seulement, worktree propre. | P4-D attend 17 ; P5-D et contribution J4 attendent 16. Ne pas fusionner ses conclusions D6 comme une preuve calibrée. |
| 27, E10 | Code, 2 CSV, 4 figures et journal contrôlés ; fusionné sur `main`, worktree retiré. | Clos ; complément F2/P5-C relève de travaux ultérieurs, sans résultat actuel. |

**Streams à venir, idée scientifique.** 15 transpose T-JEPA au tabulaire BAF ; 16 préentraîne les représentations et mesure RankMe/J3 ; 19 mesure les lois d'échelle en N et la PCA de faible variance P3-KF ; 20 étudie la transmission de direction de dérive ; 21 fige la configuration J4 et relie chiffres/figures aux CSV ; 22 compare JEPA aux contrôles linéaires et aux ablations pour E5 ; 24 étudie les dérives Data/Concept de BAF ; 25 recense les régimes réels avec placebos après gel ; 26 teste l'absorption par adaptation versus modèle gelé ; 28 teste le second domaine électrique. Aucun de ces streams n'a encore livré de résultat propre. Les dépendances opérationnelles sont dans `prompts/streams/INDEX.md` et les prompts individuels ; leurs lignes de routage modèle/effort sont historiques.

## 4. Inventory of Attachments and Dependencies

### Files [.py]

- **jepadrift/floors.py:**
  - *Description:* planchers analytiques du §3 (lot 1, gelé ; SHA-256 49b36c5ef1b7995a274243180825731d42a61829c70e00fc7fc72841d39a9170).
  - *Core Functionalities:*
    - conversions et planchers : `kl_from_sharpe`, `sharpe_from_kl`, `first_order_floor`, `evidence_budget`, `onset_lr_delay` ;
    - lectures de Prop. 2 : `brownian_h` (résout e^h − h − 1 = g), `phi`, `cusum_exact` (seuil et délai à ARL₀ = γ), `cusum_threshold` (e-détecteur à ln γ, ARL₀ réalisé) ;
    - taxes et absorption : `mixture_multiplier` (M(D, γ)), `dictionary_multiplier`, `absorption_delay` ;
    - divers : `kl_bernoulli_half`, `factor_information` (scission exacte facteur/largeur) ; constante RHO_GAUSS = 0,5826.
  - *Inputs:* γ, I (nats par jour), θ, D, K, cos²ϑ, τ_a ; matrices B, Σ_F, Ψ.
  - *Outputs:* délais en jours, multiplicateurs, termes d'information.
- **jepadrift/sim.py:**
  - *Description:* générateurs D5 ; `Garch` déplacé à l'identique depuis E2.
  - *Core Functionalities:*
    - constantes NU = 7 et T_SCALE = √(5/7) ; `t_innov` ;
    - `Garch(rng, reps, dim, alpha, beta, burn=1000).draw()` : GARCH(1,1) à volatilité commune, signe tiré par jour, renvoie (x, sig) ;
    - `gaussian_latent(T, D, rng)` ;
    - `garch_panel(T, N, alpha, beta, nu, rng, factor_rho=None, burn=1000)`.
  - *Inputs:* `np.random.Generator` passé explicitement ; α + β < 1 ; ν > 2 ou None ; 0 ≤ ρ < 1.
  - *Outputs:* tableaux float64.
- **jepadrift/injection.py:**
  - *Description:* symétrisation D6 et injection des familles F1–F4 dans l'espace des rendements.
  - *Core Functionalities:*
    - `symmetrize(X, rng) -> (X̃, ε)`, avec un signe par jour ;
    - `fit_background` : Ledoit–Wolf, `eigh_desc`, K facteurs, Ψ ;
    - `gls_residual` ;
    - `inject(X, family, tau_star, I_target, params, rng) -> (X̃, delta, meta)` :
      - F1–F3 : X̃[τ*:] = X[τ*:] + delta ;
      - F4 : X̃[τ*:] = X[τ*:] @ M.T ;
    - `draw_tau_star` ; `write_tau_star` (champs family, tau_star, convention, amplitude, seed, direction, direction_sha256, info, K, calib, shrinkage, c_nan_imputed) ; `_check_panel`.
  - *Inputs:* X 2-D float64 fini (TypeError ou ValueError sinon) ; `params["C"]` (T, N, P) float64 pour F2, NaN → 0 comptés ; `params["K"]` lu pour F1 et F2 seulement.
  - *Outputs:* panel injecté (entrée jamais modifiée), delta, meta sérialisable en JSON.
- **jepadrift/pipelines.py:**
  - *Description:* registre des pipelines ; seul module qui importe à la fois les représentations et les moniteurs.
  - *Core Functionalities:*
    - constantes : MASTER_SEED = 42 ; H_REF = 500 ; H_DET = 750 ; N_CAL = 20 000 ; TARGET_FPR = 0,05 ; B_FLIPS = 2 000 ; HALF_LIFE = 20 ; STAKE_CAP = 0,5 ; PIVOT_BETS = (0,1 ; 0,25 ; 0,5 ; 0,9) ; SIGN_DELTA = 0,1 ; ENERGY_DELTA = 0,5 ; GAMMA = 20,0 ; CHUNK = 64 ; Z99 = 2,5758293035489004 ;
    - lectures par pipeline (READINGS) : P2-C bootstrap ou anytime-valid ; P3-C anytime-valid ou exacte ; P3-D bootstrap ; P3-CS anytime-valid ou randomisation ; P7 anytime-valid ;
    - ports verbatim : `save_fair_csv`, `composition_for` ;
    - préparation : `split_rows`, `make_spec`, `run_id` ;
    - exécution : `fit_pipeline`, `run_pipeline(spec, data, splits, onset_info, state=None, n_jobs=1, out=None)` ;
    - diagnostics et flux : `sign_diagnostics`, `cross_independence`, `residual_energy`, `stakes` ;
    - registre `PIPELINES` et vérifications nulles : `null_target`, `summarize`, `null_specs`, `null_check` (blocs D6 empilés) ;
    - CLI `--pipeline --dataset --null-check --reps --out --log-dir` ;
    - à ajouter par le stream 8b : `horizon_gamma`.
  - *Inputs:* X ou Z, `splits`, enregistrements d'onset, `state` ajusté sur des lignes sans dérive.
  - *Outputs:* `alarms.csv` (colonnes run_id, pipeline, dataset, family, seed, tau_star, alarm_index, delay, detected, threshold, reading), journaux, résumés nuls.
- **jepadrift/monitors/cusum.py:**
  - *Description:* CUSUM portés de l'Article B (R01 l. 110–142 ; R15 l. 343–360), numpy seul.
  - *Core Functionalities:* `strict_cusum`, `get_multiple_alarms`, `get_cusum_trajectory`, `bilateral_delay`, `cusum_max_bilateral`, et leurs versions vectorisées (`strict_cusum_vec`, `bilateral_delay_vec`), bit-identiques aux ports.
  - *Inputs:* flux centrés, δ, seuil.
  - *Outputs:* indice d'alarme (−1 si aucune), trajectoires.
- **jepadrift/monitors/streams.py:**
  - *Description:* constructeurs de flux.
  - *Core Functionalities:* `label_stream(r, q_hat)` = 1{r > 0} − q̂ ; `exact_sign_stream(y, rng)` = 1{y > 0} − ½, zéros tranchés par une pièce ; `energy_stream(r, mu, sigma)` ; `fraction_stream` (port de R15).
  - *Inputs:* rendements ou projections ; générateur aléatoire pour les égalités.
  - *Outputs:* flux centrés.
- **jepadrift/monitors/lattice.py:**
  - *Description:* loi exacte d'un CUSUM sur flux à deux points.
  - *Core Functionalities:*
    - programmation dynamique en unités entières (+a/−b, P(+) = q), unilatérale ou bilatérale, règle stricte ou large ;
    - `exceedance`, `arl0` (résolution dense, (L + 1)^sided ≤ 10 000), `attainable_levels` ;
    - `select_threshold(nominal, H, delta, sided)` renvoie lam, threshold (point milieu (L ± ½)·unité), level et units ;
    - exemple : (0,05, H = 5 000, δ = 0,1, bilatéral) → L = 57, λ = 11,4, seuil 11,5.
  - *Inputs:* niveau nominal, H ou None (ARL₀), δ, sided, q.
  - *Outputs:* niveaux exacts, seuils.
- **jepadrift/monitors/gamma.py:**
  - *Description:* Γ spectral et opérationnel.
  - *Core Functionalities:* `gamma_spectral` (Bartlett, L = ⌊4(n/100)^{2/9}⌋) ; `required_threshold` (λ minimal tel que le FPR ou l'ARL₀ visé tienne).
  - *Inputs:* série de la statistique ; trajectoires nulles ; δ ; α ; mode ; H.
  - *Outputs:* Γ̂, λ_req.
- **jepadrift/monitors/eprocess.py:**
  - *Description:* e-processus et e-détecteurs, en échelle log.
  - *Core Functionalities:*
    - pari à mise prévisible (λ = 2·côté·η₀) ; port de MIX (16 départs × η₀ ∈ {0,05 ; 0,10 ; 0,15} × côtés ±1, H = 5 000) ;
    - `log_edetector` (types SR et CUSUM) ; `log_dictionary_edetector` (moyenne sur les directions ; grille EDETECTOR_ETA0 = {0,05 ; 0,10 ; 0,15 ; 0,20} × côtés) ;
    - mélange sous-gaussien de la Prop. 3 ; `log_average_betting_eprocess` (P3-CS a) ; `first_alarm`.
  - *Inputs:* x ∈ [−1, 1], γ.
  - *Outputs:* log-statistiques, alarmes.
- **jepadrift/monitors/calibration.py:**
  - *Description:* calibrations ; numpy, math, fractions et `jepadrift.monitors` seulement.
  - *Core Functionalities:* `worker_null_window_real` et `worker_race_h1_real` (verbatim R15 l. 431–478) ; `bootstrap_threshold` (quantile de R15 l. 1062) ; `null_windows(x, length, n, rng, flip=True)` (randomisation par inversion de signe).
  - *Inputs:* lignes nulles, longueurs, graines.
  - *Outputs:* seuils, maxima nuls.
- **jepadrift/representations/base.py:**
  - *Description:* interface Z-1 (INTERFACE = "Z-1").
  - *Core Functionalities:* `Representation` : `fit(X_fit, C_fit, dates_fit)`, `transform_day(x_t, C_t)` → {"z_odd", "z_even"}, `transform_panel` (boucle jour par jour), `state_hash()`, `sidecar()` (copie détachée), attribut `odd_head = True`.
  - *Inputs:* tableaux 2-D float64 finis, T ≥ 2, N ≥ 2.
  - *Outputs:* têtes impaire et paire, sidecar JSON.
- **jepadrift/representations/pca.py:**
  - *Description:* PCA-orthogonale (P3-C, P3-D, P3-KF).
  - *Core Functionalities:*
    - `PCAOrthogonal(K="mp", mode="factor"|"full"|"tail10", shrinkage="ledoit_wolf"|None)` ;
    - règle de Marčenko–Pastur `mp_edge`, `mp_count` ; K = n₊ − 1 ;
    - z_odd = x @ (V_sel/√λ_sel) ; z_even = z_odd² ; canaux {"market": [0], "residual": [1..D−1]} ;
    - `check_K`, `pca_directions`.
  - *Inputs:* lignes de calib.
  - *Outputs:* D = K + 1 (factor), N (full) ou m + 1 (tail10).
- **jepadrift/representations/cross_section.py:**
  - *Description:* coupe de degré 0 (P3-CS).
  - *Core Functionalities:* `DegreeZero(b="pc1"|"ones", K="mp", mode)` avec z_odd = Uᵀp/‖p‖ et z_even = [‖p‖] ; `CenteredRanks()` avec z = (r − (N + 1)/2)/N (rangs moyens).
  - *Inputs:* lignes de calib.
  - *Outputs:* pivots bornés, dispersion du jour.
- **jepadrift/representations/extract.py:**
  - *Description:* CLI d'extraction et registre.
  - *Core Functionalities:* REGISTRY = {pca, degree0, ranks} ; DATASETS = {d2_us97, d3_239} ; FIT_SEGMENT = "calib" ; écrit `z_<state_hash>.npz` (Z_odd, Z_even, dates) et le JSON associé ; options `--dataset --rep --mode --K --shrinkage --b --out`, validées contre la signature de la représentation.
  - *Inputs:* `data/derived/<dataset>/`.
  - *Outputs:* `.npz` et sidecar ; lignes transformées depuis le premier jour de pretrain (`d3_239` : lignes 1256–6738).
- **jepadrift/stats/covariance.py:**
  - *Description:* covariance par rétrécissement.
  - *Core Functionalities:* `ledoit_wolf(X) -> (sigma, shrinkage)` ; `eigh_desc(sigma)`, vecteurs propres signés pour une somme positive.
  - *Inputs:* X (n, N).
  - *Outputs:* Σ̂, valeurs et vecteurs propres.
- **jepadrift/stats/garch.py:**
  - *Description:* QMLE GARCH portée à l'identique (R01 l. 72–108).
  - *Core Functionalities:* `_garch_nll`, `fit_garch_qmle` (SLSQP), `compute_gamma_exact`.
  - *Inputs:* série de warm-up.
  - *Outputs:* α, β, Γ̂ ; pour SPY : α = 0,211551, β = 0,729081, Γ̂ = 14,998367977816738.
- **jepadrift/data_loader/articleB.py:**
  - *Description:* construction et chargement de D1 et D2 depuis le checkout de l'Article B.
  - *Core Functionalities:* `load_d1`, `load_d2`, `load_phases(variant)`, `load_splits(dataset)`, `build` (CLI `--build`), `_build_manifest` (fusion des entrées non-D1/D2).
  - *Inputs:* `~/The-Whitening-Advantage-Experiments/data/derived_firstrate/R01_daily_{SPY,PFF,VNQ,BWX}.csv`, `data/derived_equities/R15_panel_logreturns.csv`, CSV de recensement R16.
  - *Outputs:* `data/derived/{d1_etf4,d2_us97}/`, `MANIFEST.json`, `results/data/d1_d2_profile.csv`, `logs/data/build.log` ; tableaux float64, dates, identifiants.
- **jepadrift/data_loader/sp500.py:**
  - *Description:* construction et chargement de D3.
  - *Core Functionalities:* `load_d3_239`, `load_d3_500`, `load_chars`, `load_splits`, `build(refresh)` ; caractéristiques beta_252, vol_63, mom_12_1, rev_21 (transformées en rangs dans [−0,5 ; 0,5]) et GICS one-hot ; `_select_239` ; import paresseux de yfinance.
  - *Inputs:* Wikipedia, Yahoo Finance (cache `data/raw/d3_yf/`), CD-DFM.
  - *Outputs:* `data/derived/{d3_239,d3_500}/`, `results/data/d3_profile.csv`, `logs/data/d3_build.log`.
- **jepadrift/data_loader/baf.py:**
  - *Description:* construction et chargement de D7 (BAF).
  - *Core Functionalities:* `load_baf`, `load_splits`, `load_preproc`, `build` ; import paresseux de kaggle ; prétraitement figé sur les mois 0–2 (z-scores, catégories encodées, inconnues → −1).
  - *Inputs:* API Kaggle (`sgpjesus/bank-account-fraud-dataset-neurips-2022`) ; jeton `~/.kaggle/access_token`.
  - *Outputs:* `data/derived/d7_baf/{base.parquet,splits.yaml,preproc.json}`, `results/data/baf_profile.csv`.
- **jepadrift/data_loader/eurofidai.py:**
  - *Description:* ingestion de D4.
  - *Core Functionalities:* `load_schema`, `read_raw_files`, `compute_returns_from_adjusted`, chargeur de panel, `load_chars_d4`, `load_splits_d4`, `build` ; `in_universe` point-in-time avec filtre de liquidité ; caractéristiques de D3 réutilisées.
  - *Inputs:* `data/raw/eurofidai/` (153 CSV, ignoré par git), `configs/eurofidai_schema.yaml`.
  - *Outputs:* `data/derived/d4_eurofidai/` (ignoré par git).
- **experiments/e2_floor_validation.py:**
  - *Description:* E2, jalon J1 (lot 1 ; importe désormais NU, T_SCALE et Garch de `jepadrift.sim`).
  - *Core Functionalities:* bras G1, G2, S1 et S2 ; contrôle des flux de signe sous H₀ ; règle J1 ; options `--reps --out --alpha --beta --quick`.
  - *Inputs:* argv.
  - *Outputs:* `results/e2/e2_cells.csv` (46 lignes), `e2_j1_summary.txt` ; code de sortie 0 si et seulement si J1 passe.
- **experiments/identity_articleB.py:**
  - *Description:* identités R01, R08 et R15.
  - *Core Functionalities:* reconstruction des six tables de R01 ; colonne `exact_level` de R08 ; `r15_rows(ks=(5, 10, 20), bootstrap, race)` ; `get_deterministic_seed` (verbatim).
  - *Inputs:* checkout de l'Article B, chargeur D1/D2.
  - *Outputs:* `results/identity/articleB_R01_R08.csv` (SHA-256 6d37a97a64ba5d2e2c9b06c3b4f0746df81be06219d6782b4d3fd38b7e37bebb), `articleB_R15.csv` (SHA-256 d78d13e0b0cabfcf3d0a0a90adb0d00956d5f70e7ed49d19d05a6c18b301f7bc), `logs/identity/*.log`.
- **experiments/audit_information.py:**
  - *Description:* audit informationnel (streams 11 et 11b) ; lignes 2005–2019 seulement.
  - *Core Functionalities:*
    - chargement : `load` (contrôle de fenêtre, base de calib vérifiée contre les sidecars) ;
    - spectre et signes : `spectrum_rows`, `eta_rows`, `sign_rows` ;
    - symétrie : `triples_test`, `garch_filter`, `char_directions`, `symmetry_rows` ;
    - dérive : `spy_phases`, `transitions`, `debiased_sr2`, `mbb_indices`, `_ci` ;
    - plafonds des canaux : `n1`, `rolling_lw`, `info_ratio`, `mvt_nu`, `t_ratio`, `ceiling_rows` ;
    - budget et gains : `budget_rows`, `planning_gains`, `predicted_rows` ;
    - stream 11b : `n2_noise`, `_directions`, `rotate_phases`, `placebo_rows` ;
    - `plot`, `main` (options `--datasets --out --fig-dir --log-dir --boot --jobs --quick`).
  - *Inputs:* `data/derived/{d2_us97,d3_239}`, `chars.parquet`, datations de D1.
  - *Outputs:* `results/audit/*.csv`, `figures/audit/*`, `logs/audit/audit.log`.
- **tests/*.py:**
  - *Description:* tests de contrat et unitaires.
  - *Core Functionalities:*
    - par module : `test_floors` (6, gelé), `test_data_d1_d2` (fixture de reconstruction), `test_data_d3`, `test_monitors`, `test_identity_articleB`, `test_injection`, `test_representations`, `test_pipelines`, `test_data_baf`, `test_data_eurofidai` (fixtures et données réelles), `test_audit` ;
    - contrats : `test_contracts` (non-anticipation, imparité, déterminisme, absence de statistiques de test ; 4 gardes torch en `skipif`) ;
    - découplage : `test_decoupling` (6 tests AST) ;
    - `conftest.py` vide à la racine, pour les imports.
  - *Inputs:* données dérivées commitées, checkout de l'Article B.
  - *Outputs:* verdicts pytest.

### Files [.md, .tex, .bib, .csv, .json, .yaml, .npy, .npz, .parquet, .sh, Makefile]

- **AGENTS.md (CLAUDE.md = lien symbolique relatif):**
  - *Description:* mémoire canonique des agents.
  - *Contenu :* objet scientifique, glossaire, données et découpages, layout, règles d'ingénierie, worktrees.
  - *Statut :* les amendements A1–A8 sont en attente.
- **prompts/streams/INDEX.md:**
  - *Description:* table de routage (modèle, effort, prérequis), protocole de fin de stream, mémoire Claude Code et Vibe, lancement tmux.
  - *Statut :* les amendements I1–I4 sont en attente.
- **prompts/streams/prompt-01…28-*.md, prompt-08b-hygiene.md (à créer):**
  - *Description:* prompts des streams.
  - *Statut :* 1–11 exécutés ; 12–28 à remplacer ou modifier selon le paquet du tour 3.
- **prompts/Prompts_Claude_Code_v5.md, prompts/Orchestration_Streams_v5.md:**
  - *Description:* master des prompts (1 493 lignes) et plan de vagues historique.
- **prompts/plans/plan-NN.md, prompts/GO-stream-NN.md, prompts/wrapups/wrapup-NN.md:**
  - *Description:* plans, revues GO et résumés des streams 01 à 11 et 11b.
  - *Notes :* `plan-11-vibe.md` est obsolète ; `plan-03-temp.md` est la copie du chercheur.
- **prompts/Plan_Claude_Opus_v1.md … v4.md, Plan_Claude_Opus_v4_correction.md, Prompt_Claude_Opus_v4.md:**
  - *Description:* note théorique initiale (v1), plans d'orchestration successifs (v4 consolidé), correction du plancher, gabarit des prompts d'agents.
- **paper/sec3_theory.tex, paper/appA_proofs.tex, paper/articleC_biblio_addendum.bib:**
  - *Description:* §3 et annexe A de l'Article C ; addendum bibliographique.
  - *Clés ajoutées :* lorden_1971, moustakides_1986, lai_1998, taylor_1975, robbins_1970, howard_2020, kullback_1959, cover_thomas_2006, boyd_vandenberghe_2004, kuncheva_faithfull_2014, qahtan_2015, kelly_2019, alouadi_lehalle_2026, whitening_2026 (anonymisé).
  - *Clés reprises de la bibliographie v69 de l'Article B :* siegmund_1985, tartakovsky_2014, ville_1939, ramdas_2023, shin_2024, vandervaart_1998, page_1954, pagan_sossounov_2003.
- **docs/DEVIATIONS.md:**
  - *Description:* registre en français des écarts C-<sujet>.
  - *Entrées, streams 1–3 :* C-push-policy, C-eos-protocol, C-plan-recording, C-D2-survivor, C-interface-f64, C-D3-no239, C-D3-survivor (à corriger), C-D3-gics-static, C-D3-provenance, C-D3-manifest-merge.
  - *Entrées, streams 4–7 :* C-R01-parse, C-R01-env, C-garch-pyflakes, C-lattice-midpoint, C-e2-sim, C-inject-F2-norm, C-inject-F2-nan, C-inject-conv-b, C-inject-lw-test, C-repr-mp-K, C-repr-whiten-lw, C-repr-layout, C-repr-even-heads, C-repr-rows, C-pipe-delay, C-pipe-null-targets, C-P2C-port, C-P3D-windows, C-P3CS-design, C-P3C-mixture-gate, C-identity-R15.
  - *Entrées, streams 9–11b :* C-BAF-synthetic, C-audit-debias, C-audit-subspaces, C-audit-transitions, C-audit-ceilings, C-audit-gains, C-worktree-data-raw, C-audit-n2-noise, C-audit-placebo.
- **docs/sections/*.md:**
  - *Description:* notes de conception : monitors, injection, interface_Z, pipelines, contracts, data_baf, data_d1_d2, eurofidai_extraction_spec, articleB_deviations_digest.
- **docs/manifests/d4_manifest.json:**
  - *Description:* empreintes de D4 sans aucune donnée (153 fichiers sources, 7 sorties, 498 titres).
- **data/derived/MANIFEST.json:**
  - *Description:* chaîne SHA-256 des entrées et sorties de D1, D2, D3 et D7 ; sources (commit de l'Article B, yfinance 1.7.0, Wikipedia, commit de CD-DFM, Kaggle).
- **data/derived/d1_etf4/, d2_us97/, d3_239/, d3_500/, d7_baf/ (d4_eurofidai/ ignoré par git):**
  - *Description:* `panel.parquet` (date, asset_id, ret float64, close, in_universe), `ret_wide.npy`, `dates.npy`, `assets.json`, `splits.yaml`, et selon le jeu :
    - `phases_{lt_spy,strict_ps,symmetric}.csv` pour D1 ;
    - `chars.parquet`, `flags.csv` et `selection.json` pour D3 ;
    - `base.parquet` et `preproc.json` pour D7 ;
    - extractions de référence `z_85147fd9f553130ea70a7492770fa3ea4b068f0edf421d878a9e31bed7296f3d.{npz,json}` (D2) et `z_6c44d64a3bf139beeca0939ab0ba821004796a053ec81e9952d44c7ac37ace3f.{npz,json}` (D3).
- **results/:**
  - *Description:* sorties des streams :
    - `e2/{e2_cells.csv,e2_j1_summary.txt,J1_report.md}` ;
    - `data/{d1_d2_profile,d3_profile,baf_profile}.csv` ;
    - `identity/{articleB_R01_R08,articleB_R15}.csv` ;
    - `pipelines/{alarms_P3-C_d2_us97_null.csv (SHA-256 0d892104…),runs_P3-C_d2_us97_null.json}` ;
    - `audit/{spectrum,eta_by_year,sign_corr,symmetry_tests,drift_sharpe_transitions,channel_ceilings,budget_share,predicted_gains,placebo_selection}.csv`.
- **figures/audit/{spectrum,symmetry,drift_sharpe,budget_share}.{png,pdf}:**
  - *Description:* figures de l'audit, tracées depuis les CSV.
- **logs/:**
  - *Description:* `e2/run.log`, `data/{build,d3_build,baf_build}.log`, `identity/identity_articleB_{venv,articleB-venv}.log`, `pipelines/null_P3-C_d2_us97.log`, `representations/extract.log`, `audit/audit.log`.
- **configs/eurofidai_schema.yaml, tests/fixtures/eurofidai_fake/*:**
  - *Description:* correspondance des colonnes réelles d'EUROFIDAI (eurofidai_code, isin_code, stock_exchange_name, quotation_date, adjusted_close, adjust_coef, adjusted_return, capitalization) ; fixtures synthétiques.
- **Makefile, tools/pre-commit, tools/pre-push, tools/reindex_graphify_jcodemunch.sh:**
  - *Description:* cibles test, j1, hooks et check ; hooks git ; réindexation de fin de stream.
- **external/cd-dfm/, external/articleB-venv/ (ignorés par git):**
  - *Description:* clone de CD-DFM (commit épinglé dans le manifeste ; liste des 239 titres absente, panel non redistribuable) ; environnement d'identité de l'Article B.
- **~/The-Whitening-Advantage-Experiments (lecture seule, a05f0d9c654b6692e626080c298acebc0f0a0b5c):**
  - *Description:* code et résultats de l'Article B (R01, R08, R09, R15, R16), `docs/DEVIATIONS.md` (62 écarts).
- **Documents de référence du projet:**
  - *Description:* manuscrit de l'Article B v87 (LaTeX, PDF, bibliographie v69) ; deck de rebuttal KDD v4 (l'objection R11 sur la borne asymptotique y est jugée valide) ; Alouadi & Lehalle, « The Fundamental Structure of Risk: From Characteristics to Covariance », arXiv:2607.24410 (CD-DFM) ; `KL_PCA_PIVOT.md` (pivot initial ; son η ≈ 0,9 a été corrigé par la suite) ; figures de l'Article B.

### Fichiers ajoutés ou changés depuis le transfert du 22 octobre

- **`jepadrift/data_loader/chars.py`, `jepadrift/stats/drift.py`, `jepadrift/pipelines.py` [Python, stream 8b, `main`] :**
  - *Description :* chargement partagé de C avec NaN conservés, statistiques de dérive sorties de l'audit à segments AST identiques, et `horizon_gamma(H, alpha)=H/alpha`.
  - *Entrées/sorties :* D3/D4 alignés aux rendements et aux actifs ; tenseur `C(T,N,P)` et noms ; fonctions de statistiques déjà utilisées par l'audit ; γ_H pour les expériences à horizon.
- **`experiments/e10_robustness.py`, `configs/e10.yaml`, `tests/test_e10.py` [Python/YAML, stream 27, `main`] :**
  - *Description :* E10 F1 linéaire, nulls valides et invalides, P1-C/P3-C, `half`/`qhat`, zéros, placebos et ratios RMST ; 13 tests E10 rapportés.
  - *Entrées/sorties :* D5/D6, représentations P3-C gelées et spécification YAML ; `results/e10/{e10_cells,e10_gains}.csv` et quatre figures. La branche a rapporté `make check` : 22 contrats réussis, 4 ignorés ; 241 autres réussis, 4 ignorés, avant fusion, sans nouvelle exécution pour ce transfert.
- **`experiments/e6_second_order.py`, `configs/e6.yaml`, `tests/test_e6.py` [Python/YAML, branche `stream-23` seulement] :**
  - *Description :* phase 1 F4 avec P1-D/P3-D ; phase 2 refusée tant que le stream 16 manque ; 13 tests E6 rapportés.
  - *Entrées/sorties :* fonds D5/D6, paramètres F4 ; `results/e6/e6_cells_phase1.csv` et quatre figures. Le `make check` rapporté sur cette branche est 22 contrats et 241 autres tests réussis, avec 8 ignorés au total ; il n'a pas été relancé ici.
- **`jepadrift/representations/extract.py`, `tests/test_ipca.py` [Python, branche `stream-17`] :**
  - *Description :* socle partagé de chemin des caractéristiques C dans `extract.py`, commité à `f67accf`; `tests/test_ipca.py` reste non suivi. Aucun module IPCA ni tableau P4 n'est livré.
- **`results/e10/e10_cells.csv`, `results/e10/e10_gains.csv` [CSV, `main`] :**
  - *Description :* 4 004 cellules et 144 ratios ; SHA-256 complets et interprétation en 2.7 ; journal de provenance `logs/e10/run.log` et bilan `prompts/wrapups/wrapup-27.md`.
- **`figures/e10/{fpr_inflation,gains}.{png,pdf}` [PNG/PDF, `main`] :**
  - *Description :* inflation de FPR sous choc asymétrique et ratios de délais restreints ; les quatre fichiers sont produits depuis les CSV E10.
- **`results/e6/e6_cells_phase1.csv` [CSV, branche `stream-23`] :**
  - *Description :* 190 lignes × 50 colonnes, 78 D6 et 112 D5, SHA-256 `4101c867bd3e6bc885d8d03845cda6ac033aa60e02ca94d4d45948166c59d249` ; détails et limites en 2.7.
- **`figures/e6/e6_phase1_{delays,gadd}.{png,pdf}` [PNG/PDF, branche `stream-23`] :**
  - *Description :* délais et gains de la phase linéaire F4, quatre fichiers reconstruits du CSV ; bilan `prompts/wrapups/wrapup-23.md` sur la même branche.
- **`prompts/Orchestration_Streams_v6.md`, `prompts/streams/INDEX.md`, `prompts/amorcage-*.md`, `tools/check_prompts.py` [Markdown/Python, `main`] :**
  - *Description :* spécifications de streams et amorçages ; `INDEX.md` fournit dépendances et états mais sa table modèle/effort ne gouverne plus les lancements ; le vérificateur historique rapporte 29/29 correspondances.
- **`prompts/GO-stream-23-audit.md`, `prompts/wrapups/wrapup-23.md` [Markdown, branche `stream-23`] :**
  - *Description :* arbitrage de la fenêtre contrefactuelle D6, réinitialisation du CUSUM, règle de présentation `IC=NA` sous 10 blocs H et bilan de la phase 1. Le critère de 10 blocs est préspécifié pour ce rapport, non une nécessité théorique universelle.
- **`prompts/wrapups/handover-01-11.md`, `prompts/wrapups/handover-01-27.md` [Markdown, local non suivi] :**
  - *Description :* ancien transfert conservé et présent transfert daté. Ils ne sont accessibles au dépôt GitHub distant qu'après ajout, commit et synchronisation autorisés ; ne pas les confondre avec `prompts/wrapups/wrapup-01-11.md`, qui est un bilan suivi plus court.

## 5. Hypotheses and Conditional Decision Trees

- **Transfer determination :** plusieurs variables bloquantes restent ouvertes. Cette section est donc transmise sous la même protection que le noyau sans perte (Sections 3 et 4).
- **Missing Variables — révisions :** état d'application du paquet de révisions du tour 3 dans `~/JEPA-Drift-experiments`.
- **Missing Variables — GO du stream 12 :** confirmation des choix suivants :
  - lecture γ_H = H/α ;
  - SR ∈ {2, 4, 8} ;
  - F2 limité à D3 et D4 ;
  - P3-D à H = 750 ;
  - grilles d'amplitude ;
  - mélange corrigé par Holm, en diagnostic seulement.
- **Missing Variables — critères et environnement :**
  - issue des critères J2 (i) à (iv) ;
  - existence d'une roue CPU de torch compatible avec numpy 2.4.4 ;
  - tolérance de `tests/test_decoupling.py` aux imports paresseux de `jepadrift.jepa` depuis `representations/extract.py`.
- **Missing Variables — échéances externes :** référence Kuncheva (2013) pour SPLL à vérifier ; notification KDD de l'Article B ; choix de la conférence.
- **Decision Trees — paquet de révisions :**
  - si le paquet n'est pas appliqué, l'appliquer avant tout lancement (8b, puis la vague suivante) ;
  - s'il l'est partiellement, réconcilier les fichiers de stream avec le master par `tools/check_prompts.py`, puis contrôler par `make prompts-check`.
- **Decision Trees — J2 (i) :** en cas d'échec, vérifier l'usage du seuil point milieu, la construction de D6, la pièce aux égalités et l'horizon de calcul du niveau du treillis.
- **Decision Trees — J2 (ii) :** si la pente de P2-C n'est pas nulle au-delà de N ≈ 20, contrôler K_eff (`sign_diagnostics`) et la convention (b) de F3. Le plateau attendu est 1/ρ.
- **Decision Trees — J2 (iii) :** si la pente de P3-C sur F2 n'est pas positive :
  - avec un a_max faible et une pente positive de P3-CS (b) ou du mélange, c'est une limite du détecteur et non une absence d'information : ne pas déclencher C1 ; faire porter la concentration par des mélanges dans le sous-espace des caractéristiques (P4, P5) ;
  - avec un a_max élevé, l'information manque : déclencher C1, avec le second ordre comme axe principal et E6 phase 1 comme preuve.
- **Decision Trees — E3 :**
  - si le FPR brut est inflaté sur les canaux asymétriques, recentrer sur q̂ dans les pipelines sur données réelles et ne revendiquer l'exactitude que sur D6 ;
  - si l'ARL₀ de P2-C anytime-valid sur données brutes tombe sous γ, l'attribuer à l'asymétrie et le documenter.
- **Decision Trees — J3 :** si RankMe < 0,5·D, doubler le poids du terme de variance et passer d_model à 32, avec une seule relance. En cas de nouvel échec, le JEPA devient un résultat conditionnel (titre B).
- **Decision Trees — J4 :** si G_ADD(meilleur de P3-CS (b) et P4 → P5) ≥ 1,25 sur au moins deux familles parmi F1, F2 et F4, IC excluant 1, retenir le titre A ; sinon le titre B (contingence C3).
- **Decision Trees — seuil du plancher univarié :** si la part des phases dans le budget dépasse 25 % mais que le placebo montre une part comparable, l'attribuer à la sélection des frontières ; aucune revendication de détectabilité réelle.
- **Decision Trees — D4 :** D4 reste un appui européen. S'il manque ou si son biais de survie domine, E4 sur D4 passe en dernier dans l'ordre de raccourcissement.
- **Decision Trees — Article B et conférence :**
  - si l'Article B est accepté à KDD, intégrer à la version caméra la lecture budget et l'argument de borne inférieure ; sinon, le préparer pour une nouvelle soumission ;
  - dans tous les cas, mettre à jour la matrice des conférences de l'Article C (rang B, A ou A*) à partir de fin novembre 2026.
- **Decision Trees — compléments :** si C1 et C2 se cumulent (information de localisation rare en finance), l'accent se déplace vers BAF et IoT, mais les intouchables restent E1, E2, E3, E4 sur D2–D3, le cœur d'E5 et E8 sur le S&P 500.

### 5.1 Décision de transfert au 23 octobre 2026

- **Variables résolues depuis la source :** le paquet v6 et 8b a été appliqué ; les écarts C-D3/C-D4 ont été corrigés ; les prompts ont une vérification 29/29 ; le stream 27 a été fusionné. Le GO initial du 12 existe, mais il ne remplace pas un plan final audité. La question de la roue PyTorch a été arbitrée vers l'environnement conda-forge `cpu_generic` à 65 paquets ; son installation et ses tests restent à faire. La règle D6 `IC=NA` sous 10 blocs H a été préspécifiée et corrigée dans le CSV du stream 23, sans devenir une condition générale du bootstrap.
- **Variables toujours ouvertes :** confirmation J2 (E1/E3), J3 (RankMe après stream 16), J4 (E5 après gel), comportement des gardes torch et du découplage après mise en place de l'environnement 14, portée effective du clone CD-DFM, référence SPLL, notification KDD et choix de conférence. E6 P4-D/P5-D et E10 F2/P5-C n'ont pas de résultats. Le taux de fausse alarme réel de `qhat` et sa stationnarité ne disposent pas de garantie exacte.
- **Condition de reprise opérationnelle :** tant que le chercheur n'annonce pas le rétablissement du quota Claude, conserver les sessions existantes sans les interrompre et laisser la surveillance périodique arrêtée. Après notification, reprendre par audit ponctuel des worktrees, puis recharger `graphify` et `jcodemunch` dans chaque session quittant `/plan`. Toute mise à jour de `.pth` attend les contrôles de `make check` et de J1 CRLF du stream 14.
- **Arbre de décision scientifique :** si E1/E3 ne tiennent pas J2, attribuer séparément l'échec à l'information injectée, l'alignement, la censure ou le niveau H₀ avant de modifier un modèle. Si le second ordre n'est fort que sur la rotation exploratoire PC1–PC2, retenir E6 comme preuve ciblée d'une limite des moniteurs unilatéraux, pas comme effet F4 général. Si l'E5 ne bat pas P3-CS (b) et P4 à FPR comparable sous le protocole gelé, choisir la contingence C3 et le titre B ; ne pas ajuster a posteriori les familles ou seuils de J4.

## 6. Strategic Recommendations for the Next Instance

- **Blind Spots — premières lectures :** `AGENTS.md`, `prompts/streams/INDEX.md`, les wrapups 01 à 11 et 11b, `docs/DEVIATIONS.md`, `docs/sections/pipelines.md` et `interface_Z.md`. Puis vérifier dans le dépôt distant, par le connecteur GitHub, la présence du paquet de révisions.
- **Blind Spots — rôle :** ne jamais implémenter un stream dans le chat. Le rôle de l'instance est de concevoir et réviser les prompts, de relire les plans et les revues GO, d'analyser les wrapups et de porter la théorie et la rédaction.
- **Blind Spots — plancher :** ne jamais citer le plancher de premier ordre comme une borne d'ADD à γ fini. Toujours nommer la lecture, et préférer la lecture budget (Lemme 1) pour tout recensement de phases.
- **Blind Spots — gains :** tout gain prévu se calcule à partir des dérives injectées et de l'alignement mesuré, jamais à partir des transitions réelles (sélection, R9).
- **Blind Spots — attribution :** P3-CS (b) capte N1 ≈ 2 sans apprentissage. Toute revendication en faveur du JEPA doit le battre, et les tableaux principaux doivent le contenir.
- **Blind Spots — limites de la théorie :** le mélange isotrope de la Prop. 3 suppose l'indépendance des coordonnées. Sur données réelles, le détecteur valide est le dictionnaire (moyenne) : les prévisions et le texte du §3 doivent l'intégrer (lot 3), et la piste de recherche porte sur des mélanges valides sous dépendance, restreints au sous-espace des caractéristiques.
- **Blind Spots — données réelles :** elles servent d'appui. Les biais de sélection des frontières et de survie (D2, D3, D4) s'appliquent à toute mesure sur données brutes, et chaque mesure par phase doit être accompagnée de son placebo.
- **Blind Spots — degrés de liberté :** grilles d'amplitude, CALENDAR_MIN, porte de Holm et horizons de lecture. Les fixer avant toute lecture du test et les consigner ; le gel du J4 est la seule protection contre R18.
- **Blind Spots — reproductibilité :** les empreintes dépendent de la pile numérique et de la build BLAS. Toute mise à jour de numpy ou de scipy exige de relancer `make j1` et de comparer à `e315e537…`.
- **Blind Spots — localisation :** répertoire de travail sur la machine locale (serveur SSH) `~/JEPA-Drift-experiments`, synchronisé avec `https://github.com/JEPA-Drift/JEPA-Drift-experiments`. Les fichiers du dépôt distant sont lisibles directement avec le connecteur (plugin) GitHub.
- **Blind Spots — objectif :** publication dans une conférence internationale de rang B, A ou A*, à partir de fin novembre 2026. La version visée doit contenir E1, E2, E3, E4 sur D2–D3, le cœur d'E5 et E8 sur le S&P 500 ; les items B et C inachevés y sont présentés comme « en cours ».
- **Blind Spots — notes de module :**
  - le noyau de préférences de l'utilisateur est présent : la pile d'en-têtes S0–S3 est réduite et l'horodatage placé dans la barrière ;
  - l'invariant (g) est appliqué ;
  - `ENG_DEWATERMARKING.md` n'est pas injecté ce tour : sa suspension est sans objet, consignée et non confirmée ; aucune perturbation stylistique n'a été appliquée à ce handover.

### 6.1 [Strategic Advice] — reprise après notification du quota

- Partir de `prompts/wrapups/handover-01-27.md`, puis contrôler l'état Git actuel avant toute hypothèse sur les branches. La section 3.6 prévaut sur les états historiques des sections 3.1–3.5. `prompts/wrapups/wrapup-27.md` documente E10 fusionné ; `prompts/wrapups/wrapup-23.md` est propre à `stream-23`. Vérifier la disponibilité distante avant de diriger une autre IA vers les artefacts GitHub.
- Reprendre 12 et 13 pour J2, 14 pour l'environnement torch et J1, 17 pour IPCA/P4, puis 18 ; garder 23 phase 2 dépendant de 16. Ne pas produire un verdict JEPA ou un titre A à partir des gains linéaires E6/E10. Pour les comparaisons, garder P3-CS (b) et P4, le FPR propre à chaque bras, la censure et l'alignement dans le même tableau.
- Les contrôles de cette rédaction portent sur les fichiers et les empreintes déjà produits ; aucune exécution empirique ni `make check` nouveau n'a été lancée ici. Refaire les vérifications seulement lorsqu'une modification exécutable ou une intégration les justifie. Conserver la signature CRLF de J1 et le calcul de SHA sur le fichier disque.
- Le noyau externe `LIGHT` mentionné par la compétence de wrap-up n'a pas été injecté comme module distinct dans cette session ; son protocole autonome de transfert et les sections protégées ont été appliqués. `ENG_DEWATERMARKING.md` n'a pas été injecté.
