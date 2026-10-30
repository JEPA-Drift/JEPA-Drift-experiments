# Stream 28 — approbation du plan de clôture, sans GO d'implémentation

**Mise à jour d'autorisation :** ce document décrit l'approbation du plan à sa création. Le GO ultérieur `prompts/GO-stream-28-closeout-vibe.md` autorise maintenant la seule reprise Vibe du 28, avec large-4 et thinking high. Aucun GO d'implémentation Claude n'est donné.

Date : 2026-10-30. Le plan Phase A de 121 lignes a été audité par Codex puis enregistré à `prompts/plans/plan-28-closeout.md`, avec une section « Décision GO intégrée — PLAN UNIQUEMENT ». Source capturée : SHA-256 `f17da53fa8f4dc9b8b3b139da107a157f72857d43d2381b26c510242c26e1789`.

Les correctifs ciblent la taille de lot flottante dans exhaustive_cov et le schema_version /1 résiduel du YAML. Ils prévoient les régressions, les validations de frontière, des sorties closeout neuves, la préservation des artefacts existants, le double smoke et les portes de clôture.

Statut : **PLAN APPROUVÉ ; EXÉCUTION NON AUTORISÉE**. Aucun défaut n'est déclaré corrigé, aucun nouveau test exécuté par cette session de planification, aucun schéma scellé et aucun commit/push effectué. Claude Code reste limité aux plans. Les instructions d'exécution d'un implémenteur, éventuellement Mistral Vibe, seront fournies par le chercheur.

Le Stream 28 n'est pas clôturé : l'application des correctifs, leurs vérifications et l'intégration restent nécessaires. Les streams 29, 30 et 31 restent fermés conformément à la priorité donnée au 28.
