# Stream 32 — réception du contrôleur DEV B2w

18 novembre 2026. Décision Codex distincte. **B2w REÇU** au titre du GO B-TDD.

Le contrôleur `dev_phase(cfg, mode, context)` lie SETUP vérifié, inventaire prévu, partitions
DEV_LIB/DEV_NULL/DEV_ALT, qbar équilibré, choix d_dev/s2_dev, identités de calibration DEV et
politiques gelées dans le record DEV atomique. Le statut MARKET sans développement reste
représenté par des identités d'application vérifiables. Le rechargement valide l'enregistrement
et son budget sur SETUP/DEV et réutilise les identités et sous-ensembles enregistrés.

| Étape | Résultat mesuré |
| --- | --- |
| RED consolidé | 31 échecs ciblés et 807 passés en 33,88 s. |
| RED avec les témoins groupés | 33 échecs ciblés et 807 passés en 34,98 s. Les 19 absences du contrôleur et les 14 absences du paramètre de règle expliquent tous les échecs. |
| GREEN final | 840 passés en 19,85 s. Pytest exit 0, pyflakes et diff-check propres. Rang non nul valide et trois refus passants sur un record déterministe. |

Aucune assertion reçue supprimée ni affaiblie. Revue indépendante et preuves détaillées dans
`REVIEW-stream-32-B2w-green-final-20261118.md`. Source SHA
`936afa0c13b59bb59d63591b5309c1b582a9b2594668b897a63e906021cb387d`, tests SHA
`73e931a1030a1587012d6b660a1b2b41a25d19e4da85f1d754c81ac51dbb4f59`.
Scellé PCA /2 SHA `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`.

T33, T37 et T51 ont leurs preuves sur fixtures. Identité `policy_id` de sensibilité
vérifiée dans DEV. L'identité de calibration finale et la consommation par CAL, NULL_PLAN,
HOLD puis ALT restent des obligations B3/B4. La comptabilité aux checkpoints est vérifiée.
La préemption, les processus ouvriers et la mémoire agrégée restent à qualifier.
