# Stream 32 — réception technique B1g, publication bas niveau

Date : 15 novembre 2026. Décision Codex : **B1g REÇU, HANDOFF PRÉPARÉ UNIQUEMENT**.
Autorité : GO B-TDD distinct, réception B1f et cycle RED/GREEN/EdgeRED/EdgeGREEN revu.
Cette réception ne clôt ni B1 ni B ; elle n'autorise aucune publication de campagne.

Reçus : publish(temp_dir,output_dir), validation du manifeste et des identités complètes,
gardes de noms partagées, local-only, inventaire et SHA, publication atomique de fixtures,
fsync et préservation avant/après renommage. La lignée et l'autorisation effective restent
les responsabilités du contrôleur, qui doit remettre un handoff vérifié avant appel.

| Observation | Décision | Justification / vérification |
|---|---|---|
| Identités, JSON strict, noms | ACCEPTED | Design/réalisation complets, schéma7champs, gardes explicites et NUL partagé ; aucun cycle. |
| Ordre des listes et chemins | ACCEPTED | Liste HOLD inversée, deux préparations indépendantes, mêmes identités/SHA malgré summary/télémétrie différents. |
| Octets CRLF/CR | MODIFIED | Défaut reproduit en EdgeRED ; read_bytes, décodage UTF8 strict et comparaison des octets canoniques après réparation. |
| Symboliques avant lecture | MODIFIED | Deux lectures interceptées en RED ; temporaire et toutes les entrées contrôlés avant contenu. Sorties liées refusées en premier. |
| Plafond50Mio | ACCEPTED | stat/lstat/fstat par inode, limite exacte admise et limite+1 refusée ; témoins par métadonnées, sans grand fichier ni mesure de performance. |
| Atomicité et autorité de forme | ACCEPTED | Fsync fichiers/temp avant unique replace, parent après ; exceptions avant/après, nonempty et stage/mode/GO absent couverts. |
| Réception de T16/contrôleur ou campagne | REJECTED | Exportateur réel, lignée planifiée, vrai GO, FINAL/reprise/CLI et science encore dus. |

Preuves sous .venv/environnement déterministe/verrou : RED initial3failed104passed,
GuardRED36failed104passed, GREEN initial140passed ; revue suspendant la réception ;
EdgeREDv2 **6failed147passed en5.74s**, puis EdgeGREEN **153passed en4.75s**.
Pyflakes et diff-check propres ; pytest/contrôles GREEN exit0. Tests inchangés pendant les GREEN.
Contre-revue indépendante de la réparation : aucun défaut matériel bloquant identifié dans ce périmètre.
La v1 EdgeRED et la capture quota n'ont jamais été appliquées ; correction de fixture64Kio tracée.

| Pièce | SHA-256 |
|---|---|
| Source finale | `330a9cd5dbe6fecc946e15cae7c12a42fb60a46a52c1a7609ea1071e91789fe0` |
| Tests figés | `5deddfe4c96fad5ecd60a77dee4aca75cb561cfb14f4291451fac2fa163fdee6` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture EdgeGREEN, exit0/erreur vide/is_error=false/session correcte/6SHA conformes | `63b0aada6568d48e87d049975552a4d60993928284de67faa5d30df4878dcd93` |
| Journal pytest EdgeGREEN | `fceba6191adc9e8ee15dbf135b030e9cdd215ec2af3c28d1498ce3cb3903b03a` |
| Journal contrôles EdgeGREEN | `1f17a9343b044c0901c0f91dd96aeb06d8e7353239f9a90f6810d31a7ec81d65` |

Scripts/preuves : logs/stream-32/check-B1g-*.sh et lot-B1g-*.
Revues détaillées : REVIEW-stream-32-B1g-red, -green et -edge-red du15novembre.
Matrice68 :18PASS/0FAIL/50NOT_RUN ; contrats partiels non déclarés PASS.

Suite bornée : tests seuls de l'exportateur scientifique T16, avec de vrais exports FAIR
construits par le code applicatif et des colonnes/provenances ANALYTIC_PROXY vérifiées.
Les CSV directs _b1f_payloads ne constituent toujours pas le témoin T16.
Complétude planifiée/status.json, contrôleur/FINAL/reprise idempotente, chaînage effectif du GO,
CLI/ressources, cohortes/rejeu/graines, raccordements A et T68/os.open restent bloquants pour réception B.
Le répertoire préparé est local ; aucune protection générale contre des modifications concurrentes
entre contrôle et usage n'est revendiquée. Pas de profil ni d'estimation de performance issue des fixtures.

LotC/runtime/smoke/profilage/pilote/full, données réelles/2020+, JEPA et autres streams restent fermés.
Aucun commit/push/réindexation ou RemoteControl ; aucun producteur scellé modifié.
