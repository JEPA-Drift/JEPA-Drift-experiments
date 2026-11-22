# Stream 32 — réception B2d, géométrie des dérives population

Date : 16 novembre 2026. Décision Codex : **B2d REÇU, PRIMITIVE PURE LIMITÉE**.
Autorité : GO B-TDD, plan v2.1 et réception B2c, empreintes vérifiées.
Reçu : population_drift sur vecteurs fournis, tableaux population figés et indices canoniques.
Aucun échantillonnage, fit, cohorte ou injection de trajectoire exécuté.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Supports et information | ACCEPTED | F0 conditionnel, F1/F2/HEAD quatre axes à I*/4, F3 seul PC1 ; Delta en retours, q exact population, références scalaires/projections non standardisées/KL pleine. |
| HEAD et oracles | ACCEPTED |16profils, q invariant et Delta antisymétrique ; dimensions INFO/PREFIX4/4 sur HEAD et4/20 sur F1/F2. Aucun constat de détectabilité ou puissance. |
| Domaine et statuts | ACCEPTED | Indices Python int stricts, spectre positif noncroissant, mauvais contexte/support incomplet UNSUPPORTED sans troncature ; B0, F0 K18 et readonly contrôlés. |
| Faux positif du premier témoin | REJECTED | V1 jamais appliquée : None confondu avec ValueError. V2 sépare les chemins et conserve24cas/références/tolérances ; trois refus techniques et bornes B0/K18 ajoutés. |
| Finitude suffisante | REJECTED | GREEN initial316passés suspendu ; EdgeRED reproduit trois ValueError manquantes pour q ou Delta entièrement nul par sous-flux. |
| Garde commune | MODIFIED | Postcondition finale exige finitude ET Delta non nul ET q positif par ligne. Comparaisons exactes, aucune norme/tolérance/seuil/clamp/renormalisation ; B0 satisfait les conditions par vacuité. |
| Contrôle subnormal | ACCEPTED | F3 représentable, q exactement égal au plus petit float64 positif, un seul Delta positif non nul ; EdgeRED contrôle passant et EdgeGREEN320passés, pas de rejet global des subnormaux. |
| Préservation | ACCEPTED | Un seul hunk de garde ; son inversion restitue exactement la source121b7018.320tests figés, aucun noyau/helper/import/formule/domaine/scellé modifié par EdgeGREEN. |
| Contre-revue indépendante | ACCEPTED | Quantificateur par ligne, B0 et sous-normal F3 relus ; aucun blocage matériel. Conditions320passés et pyflakes/diff propres observées par Codex ; aucune exécution/import/mutation du relecteur. |
| Domaine scalaire/base | MODIFIED | I_star interne int/float Python (np.float64 compatible), np.float32/np.integer non reçus ; V orthonormale précondition interne documentée, validation/provenance SETUP encore bloquante. Aucun élargissement du helper de ressources. |
| Limite de précision | MODIFIED | Garde d'annulation complète par ligne, sans garantie universelle contre le sous-flux partiel ou l'arrondi de chaque coordonnée. Convention flottante scientifique conservée. |
| Réception globale | REJECTED | Tirages/clé de signes T27, configuration T28, métadonnées sous deux fits T29, SETUP et autres raccordements encore dus. Ni B2 complet ni B1/B reçus. |

Sous .venv, environnement déterministe et verrou partagé :
REDv2 **27failed289passed en12.64s** ; GREEN initial316passed8.44s ;
EdgeRED **3failed317passed en9.36s** ; EdgeGREEN **320passed en8.42s**.
Dernière vérification : pytest/contrôles exit0, pyflakes et diff-check propres ;
`tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Capture EdgeGREEN complète : exit0, erreur vide, success/is_error=false, session PhaseB existante,
six SHA conformes et aucune permission refusée ; lectures Read/Grep, Bash désactivé.

| Pièce | SHA-256 |
|---|---|
| Source finale,74534octets | `6ed9c08ec88ec752795371b0ab79ca6a4e41c6a60439334e80d664adfce3329e` |
| Tests figés,210277octets | `e14ccade3fd8d2292007378e69c41f96379517b660df7558bce84f96f986d985` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture EdgeGREEN complète | `4237db3a3f395cab06f58a78a44a49e3b9bd9b99514f859717a7241f16bc7f5e` |
| Journal pytest EdgeGREEN | `396cfdb9de5de262754b28ff5918bd615fb9785473fa607be9217afaa45e357b` |
| Journal contrôles EdgeGREEN | `6c43aedc8fd66a6e79b04033e3021872b2bde58f8cbcfa7c4c6c8369da0ebae3` |

Revue détaillée : REVIEW-stream-32-B2d-red-20261116.md ; preuves check/lot-B2d-*.
Matrice68 conservée :18PASS/0FAIL/50NOT_RUN ; aucun contrat partiel promu.
Suite bornée B2e : tests seuls des projections apprises et diagnostics population hors ligne,
sur matrices de fixture figées ; aucun fit/tirage/cohorte, aucune calibration ou inférence B3.
T10/T15/T16global, identités/calendriers, FITTED/sampling/graines/DEV/HEAD, CAL/NULL_PLAN/HOLD/ALT,
uint32/CLI/cohortes/A/T68 et CPU hors checkpoints/crash, borne externe, workers/jobs,
gardes driver et mémoire agrégée restent bloquants avant réception B, sans report implicite en C.

Consigne chercheur maintenue : terminer **B2 complet**, puis STOP de cette instance et prompt de
reprise pour une autre Codex sur le modèle00du12novembre. Aucun B3/B4 par cette instance.
Runtime/lotC/smoke de campagne/profilage/pilote/full, réel/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation, RemoteControl ou changement de producteur scellé.
