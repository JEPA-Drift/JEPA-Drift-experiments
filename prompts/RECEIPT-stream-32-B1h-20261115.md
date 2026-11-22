# Stream 32 — réception technique B1h, exporteur analytique selections.csv

Date : 15 novembre 2026. Décision Codex : **B1h REÇU, COMPOSANT D'EXPORT UNIQUEMENT**.
Autorité : GO B-TDD, réception B1g et cycles RED/GREEN/EdgeRED/EdgeGREEN revus.
Ni T16 global, ni B1 ni B ne sont clôturés ; aucun GO de campagne ou runtime.

Reçu : export_selections(out_dir,design_id,entries), DataFrame calculé sur les masques figés,
écriture FAIR réelle de selections.csv et SHA de ses octets. Schéma12colonnes reçu, I_mean/M_mean,
V_bar moyenne des ratios sur tout H, provenance ANALYTIC_PROXY et information additive qualifiée.
L'exporteur ne sélectionne, ne scanne et n'ajuste rien ; il ne renvoie aucune mesure aux sélecteurs.

| Observation | Décision | Justification / preuve |
|---|---|---|
| T16 sur vrai composant | ACCEPTED | Colonnes/provenances vérifiées après calcul et relecture du vrai CSV, sans constante factice ; valeurs contre sommes indépendantes et M scellé. |
| Statique et plein horizon | ACCEPTED | Masques H=1/H=4, deux gamma, moyenne des ratios distincte du ratio des moyennes et de toute troncature. |
| Provenance statique | MODIFIED | Seul libellé de fixture corrigé vers FIXED_EXANTE_QBAR_MIX ; v1 non appliquée, masque et références conservés. |
| Finitude finale | MODIFIED | Défaut après conversion reproduit en EdgeRED ; métriques matérialisées float64 avant le garde, sans clamp ni rejet global du longdouble. |
| readonly et FAIR | ACCEPTED | Données/octets/flags conservés, longdouble modéré accepté, SHA réel et réécriture round_trip identique. |
| Réception T16 globale / autres exports | REJECTED | Autres colonnes, payloads et raccordements du contrôleur restent dus, avec recontrôle de tous les exports pertinents. |

Preuves sous .venv/environnement déterministe/verrou : REDv2 **16failed153passed en6.23s**,
GREEN initial169passed, réception suspendue ; EdgeRED **1failed170passed en5.36s**,
puis EdgeGREEN **171passed en4.79s**. Pyflakes/diff-check propres, pytest/contrôles GREEN exit0.
Tests inchangés pendant les GREEN, préfixes conservés ; aucun CSV infini produit lors du RED
grâce au piège d'écriture. Contre-revue indépendante : correctif accepté, aucun autre blocage concret.

| Pièce | SHA-256 |
|---|---|
| Source finale | `ca13c4ac8ad4643e3749e644b9765084d7e1396cedb0111d554e76d0b4d09209` |
| Tests figés | `9e6f58b7c017168d743c752413a28c5c735226212251746d9a68a129bb22bec1` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture EdgeGREEN complète, exit0/erreur vide/is_error=false/session correcte/6SHA conformes | `435fd37fe3297f69eef7c91b8b15105333f6a3aee02d97eb6f7aa39a2ec884b5` |
| Journal pytest EdgeGREEN | `8929bbb97a6ced69fe4e68efac7c5bd7c7f17d3fb0611956fb4eff61753e941a` |
| Journal contrôles EdgeGREEN | `3bf527d68170ad2960db6df209530cdebb2e24263bca9da1222507e928e31961` |

Scripts/preuves : check-B1h-*.sh et lot-B1h-* sous logs/stream-32.
Revues : REVIEW-stream-32-B1h-red-20261115.md et REVIEW-stream-32-B1h-green-20261115.md.
Matrice68 :18PASS/0FAIL/50NOT_RUN ; contrats partiels non déclarés PASS.

Suite bornée autorisée : tests seuls de finalisation du handoff, manifeste/FINAL et reprise,
sur records et payloads de fixtures. Aucune étape scientifique ou autre lot activé.
Restent dus : autres colonnes de selections (rho, télémétrie, SHA des masques, I_joint),
calibration/trials/aggregates/issues et RMST empirique/corrélation V/RMST, T16 complet et raccordements A,
complétude planifiée/status, contrôleur/GO/FINAL/reprise/CLI/ressources/cohortes/graines/T68.
Le libellé info_basis est validé dans un ensemble fermé ; sa provenance réelle est due enB2/B3.
LotC/runtime/smoke/profilage/pilote/full, données réelles/2020+, JEPA et autres streams restent fermés.
Aucun commit/push/réindexation ou RemoteControl ; aucun producteur scellé modifié.
