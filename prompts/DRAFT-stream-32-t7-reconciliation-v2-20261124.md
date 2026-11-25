# Projet de réconciliation T7 — qualification `continuous`

Projet soumis au chercheur. Le registre est `RECONCILIATION_REQUIRED`. Le débit de 2 s est enregistré pour une mesure finale de 1,165511 s. L’inventaire du cas est vide.

| Champ | Valeur proposée |
| --- | --- |
| `schema` | `stream32-t7-resume/1` |
| `stage` | `qualification` |
| `case` | `continuous` |
| `design_id` | `a565c473535afc703fb501612030342fda79f5a92a2d10598696b4abc8021804` |
| `previous_token` | `0958186bcdfb4072b2e6cc51b1831d49` |
| `intent_sha256` historique | `45ee0dcdbe62c7814214e7e45671a490db6b979239ec9884d421669c2cc1c277` |
| `next_intent_sha256` | À renseigner avec le SHA-256 brut de l’INTENT v2 actif et validé |
| `receipt_sha256` | `e13562c9b859ccb5b484826e0a64f90307a60cddcac0309eea830048e48e5380` |
| `inventory_sha256` | `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a` |
| `cpu_charged_seconds` | `2` |
| `reconciliation` | `true` |
| `go_reference` | Chemin et SHA-256 de la décision écrite de reprise à obtenir |

Après fixation du SHA de l’INTENT v2, soumettre la décision écrite `T7_RECONCILIATION_GO ACCORDÉ` et `T7_RESUME_GO ACCORDÉ`. Le document signé `prompts/GO-stream-32-t7-resume-v2-20261124.md` doit reprendre les champs `stage`, `design_id`, `previous_token`, `intent_sha256`, `next_intent_sha256`, `receipt_sha256`, `inventory_sha256`, `cpu_charged_seconds` et `case`. Le JSON d’autorité reprendra les valeurs du tableau et la référence de ce GO signé.

Sur accord écrit, réconcilier sous verrou avec l’INTENT v2 et l’autorité signée. Vérifier `RECONCILED`, le SHA du reçu historique et le débit de 2 s avant la reprise. Le lancement ultérieur de `continuous --jobs 1 --resume` créera un nouveau jeton dans le même registre. Le producteur ouvrira un staging neuf pour ce cas.

[Projet de GO runtime v2](DRAFT-stream-32-t7-runtime-v2-20261124.md) · [Reçu du jeton](../logs/stream-32-t7/qualification/a565c473535afc70/supervisor/0958186bcdfb4072b2e6cc51b1831d49.receipt.json)
