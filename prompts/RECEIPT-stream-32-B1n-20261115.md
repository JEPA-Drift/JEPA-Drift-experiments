# Stream 32 — réception B1n, inventaire local de finalisation

Date : 15 novembre 2026. Décision Codex : **B1n REÇU, COMPOSANT LIMITÉ**.
Autorité : GO B-TDD et réception B1m. Aucun GO runtime ou scientifique.
T50/T57/T60, B1 et B ne sont pas déclarés intégralement reçus.

Reçu : _local_inventory, partagé entre finalize et _matching_publication. Le manifeste
déclare les partitions scientifiques des six records déjà vérifiés, avec chemins relatifs
et SHA réels, en LOCAL_HASHED_ONLY. La reprise et la propriété du temporaire complet exigent
un inventaire exactement concordant. Aucun NPZ copié dans la publication.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Référence source | ACCEPTED | Empreintes réemployées via _partition_path ; SHA des records vérifiés par _lineage/_load_phase, référence de test contre octets NPZ réels. Aucune nouvelle lecture de tableaux dans l'aide pure. |
| Inventaire complet | ACCEPTED | Union exacte CSV PUBLISHED et toutes les partitions LOCAL_HASHED_ONLY ; record NOT_APPLICABLE vide sans entrée. Deux cas full/pilot de fixture. |
| Séparation des identités | ACCEPTED | Sept champs manifest et quatre champs FINAL conservés ; realization.payloads reste limité aux CSV, phase_digests liant déjà les partitions. Noms relatifs, aucun chemin absolu. |
| Cause commune de reprise | ACCEPTED | Égalité locale dans _matching_publication, partagée par les trois appelants existants : FINAL, publication sans FINAL et temporaire complet. Pas de correction recopiée par branche. |
| Refus et préservation | ACCEPTED | Entrée absente, SHA faux et nom étranger refusés avant FINAL ; temporaire incohérent refusé avant suppression ; contrôle positif exact_local sans builder/recalcul. |
| Témoin reçu renforcé | MODIFIED | Une seule assertion étendue à l'égalité exacte CSV + inventaire local ; deux cas et toutes les autres assertions conservés. Inversion de cette modification et retrait de l'append restituent tous les octets reçus. |
| V1 et correction v2 | MODIFIED | V1 jamais appliquée. V2 ajoute uniquement imports et quatre pièges locaux, première suppression interceptée en RED ; aide globale inchangée. |
| Contre-revue indépendante | ACCEPTED | Aucun défaut matériel dans le composant borné ; aucune exécution/mutation par le relecteur. Codex a vérifié les241cas et pyflakes séparément. |
| Réception globale | REJECTED | Création des masques uint32, bundle/exports T16 complets, calendrier et consommation scientifique, CLI/cohortes/graines/raccordements A/T68 encore dus. |
| Ressources réelles | REJECTED | Réserves B1m maintenues : CPU hors checkpoints/crash, borne externe, workers/jointures/jobs, gardes driver avant engagement/finalisation et mémoire agrégée. Aucun enforcement complet reçu. |

Sous .venv/environnement déterministe/verrou : REDv2 **7failed234passed en9.51s**,
puis GREEN **241passed en8.34s**, pytest/contrôles GREEN exit0, pyflakes/diff-check propres.
Tests167986octets/241cas ciblés dont9registre, inchangés pendant GREEN. Patch source seule
relu/appliqué nativement puis relu, signatures publiques et producteur PCA /2 préservés.

| Pièce | SHA-256 |
|---|---|
| Source finale | `a1c5b5b7304aa0247a160a50cfe71a830da3b79c13f33ff50f7ba4f408d4e364` |
| Tests figés | `145c569366a6ab9b727205d01465e169904290cfe41a199e0ad317396d8ff884` |
| Producteur PCA /2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture GREEN complète | `73fa785b2ab2758cfc150932da30ce55eeef3bf859ee238a3dd666d352f26bb0` |
| Journal pytest GREEN | `1060a4b38ac4d5075c813e9f989f924f27d31b26a480b99597ec172e63e6ff4a` |
| Journal contrôles GREEN | `aaaac7b9885adb97c3c8cf9244bc78f9606d2d2df6a3c25471efa38cdc2d1ad3` |

Revue et dispositions : REVIEW-stream-32-B1n-red-20261115.md ; scripts/preuves check-B1n-*.
Matrice68 :18PASS/0FAIL/50NOT_RUN ; aucune couche partielle promue en contrat complet.
Suite bornée sous le GO B existant : premiers tests B2a du repère population, avant construction
des setups et raccordements des exports qui en dépendent. Ce passage suit la réception de la
tranche B1n ; il ne clôt pas B1/T16 ni ne reporte ses obligations enC. Les compléments d'exports
et de ressources restent bloquants avant réception B, à consommer dans les groupes B2/B3/B4.
LotC/runtime/smoke de campagne/profilage/pilote/full, réel/2020+, JEPA et autres streams fermés.
Aucun commit/push/réindexation, RemoteControl ou changement de producteur scellé.
