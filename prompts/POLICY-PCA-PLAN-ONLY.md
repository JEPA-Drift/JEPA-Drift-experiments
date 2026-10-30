# PCA — politique courante : plans Claude uniquement, finalisation 28 prioritaire

Décision directe du chercheur du 2026-10-30, postérieure aux GO initiaux. Cette politique prime sur toute autorisation antérieure de lancer de nouvelles implémentations Claude Code.

- Claude Code : **plans seulement**, permission-mode plan, effort max ou xhigh, Remote Control nommé. Aucun lancement avec dangerously-skip-permissions, aucune implémentation automatique après audit d'un plan.
- Ordre : **28 → 29 → 30 → 31** ; « 20 » dans le message initial était une coquille confirmée. Ne pas amorcer les plans aval avant finalisation du 28.
- Le 28 possède déjà du code et un double smoke /2. Le chercheur demande de le finaliser en premier : Codex peut achever revue, diagnostics, vérifications et intégration de l'existant seulement s'il est conforme. Une correction applicative requise est planifiée ; elle ne réautorise pas une Phase B Claude.
- Dernière instruction du chercheur : la reprise ciblée du 28 dans Mistral Vibe est maintenant autorisée, modèle alias `large-4` (mistral-large-4), thinking high. Décision et périmètre : `prompts/GO-stream-28-closeout-vibe.md`. Cela ne réautorise aucune implémentation Claude ni aucun stream aval.
- Les deux constats de clôture ont été corrigés par Vibe puis revus sans blocage. Le contrat de livraison /2 et ses hashes sont consignés dans `docs/audits/stream-28-delivery.md` ; son intégration reste soumise au dernier make check et aux portes Git. Les anciens artefacts sont conservés localement sans être scellés.
- Conserver tous les fichiers et résultats déjà produits ; aucun reset, stash, écrasement de CSV ou redémarrage général de l'implémentation. Aucun full, aucune évaluation réelle post-2019, aucune dépendance changée.
- Invariants E2 CRLF/SHA-256, E3/D8 et confidentialité inchangés. Aucun commit/push pendant un blocage de conformité. Les intégrations finales restent unitaires, processus éteints.

Le garde local partagé `.git/codex-pca-plan-only` bloque le lanceur Phase B 28 avant tout appel Claude. Les plans pourront être approuvés comme plans uniquement ; une approbation de plan n'est pas un GO d'implémentation.
