# GO — Stream 27: E10 linear stage (F1, P1-C and P3-C)

Date: 2026-10-22.
Recipient: Claude Code instance of the `stream-27` worktree (base `2b0b1cd`).
Form: verbatim transcription, by the instance, of the orchestrator's messages and GO. The GO was given in chat
after four plan reviews in plan mode. The approved plan is `prompts/plans/plan-27.md` (revision 4, harmonized).
The bootstrap is `prompts/amorcage-27.md`. The orchestrator's messages below are reproduced verbatim.

## Instructions given during exploration (verbatim)

> Correction du prompt 27 pendant ton plan : F2 sur D3 dépend du chargeur partagé du stream 8b, absent dans cette branche. L'étape immédiatement exécutable couvre F1 avec P1-C/P3-C ; ne duplique pas le pivot. P1-C existe dans monitors/cusum.py hors du registre PIPELINES. Le prompt canonique sur main vient d'être corrigé ; intègre cette porte au plan. Pour Python et les tests, utilise exclusivement .venv, jamais Trading seul.

> Correction impérative : reste dans le .venv du projet pour toutes les commandes du stream. Ne préfixe plus les appels Bash par `conda activate Trading` ; utilise `.venv/bin/python`, `.venv/bin/pytest` et le PATH du .venv, y compris dans le plan. La session Claude a bien été lancée depuis .venv. Termine maintenant un plan borné avec questions regroupées, avant tout code.
> Les sondes existantes suffisent pour le plan. N'en lance aucune autre. Rédige maintenant un plan borné pour l'étape F1 P1-C/P3-C en intégrant les corrections du prompt 27 sur la branche 5048a96, les variantes P1-C, les garanties distinctes sous symétrie/asymétrie, la limite du recentrage q̂ pour P3-C, les FPR atteints/IC, les PRNG locaux et `.venv`. F2 D3 reste après 8b et P5-C après 16. Regroupe les questions et attends mon GO, sans code.

## Review of the first plan (verbatim)

> Plan 27 : GO suspendu. Stream-27 a été avancé au main local 2b0b1cd ; relis le prompt E10/amorcage corrigé et révise le plan sans coder. Les variantes recentrée/non recentrée doivent partager les mêmes bits de signe, avec pièces locales indépendantes pour chaque zéro y compris la calib qhat ; zéro=négatif est un bras séparé. Le ratio RMST_P1/RMST_P3 est un estimand restreint, borne inférieure d'ADD seulement si P3 non censuré. Des IC Wilson qui se chevauchent ne prouvent pas FPR égal : aucune revendication iso-FPR sans marge fixée et test valide. ref_coins à canaux indépendants est un scénario iid, non FPR universel du dictionnaire P3. Sur fenêtres brutes chevauchantes, n_eff/deff valide ou IC=NA si indicatrice constante/pathologique ; placebo pretrain ajusté sur calib ultérieure = rétrospectif. Meilleur titre choisi sur F1 = oracle exploratoire. Tous les CSV via save_fair_csv ; réutiliser pipelines.horizon_gamma de 8b. Nouveaux audits en anglais, .venv exclusivement, arrêt avant fetch/push/merge ; tout push futur respecte git push origin branche-courante. Présente plan corrigé et questions bloquantes, attends mon GO.

## Review of the second plan (verbatim)

> GO reste suspendu. Révise le plan sans code : (1) nouvelles entrées docs/DEVIATIONS.md et audit trail en anglais, conformément à l'instruction utilisateur actuelle ; (2) fpr_iid n'est exact que pour le bras half d'un flux isolé sous nul valide, pas pour qhat ni pour le dictionnaire P3 ; (3) fpr_ref doit utiliser le nul valide apparié à CHAQUE fond D5 ; pour le brut, garde le même état de représentation et le même qhat puis symétrise seulement la fenêtre surveillée, ou marque le contraste descriptif sans attribution causale ; (4) pour chaque gain du titre médian ou oracle, rapporte le FPR H0 du même titre, avec IC et statut oracle, non la moyenne des 20 titres ; (5) B1=F1 seul, B2=aucune revendication iso-FPR, B3=générateur GJR/choc local au script E10 afin d'éviter le conflit parallèle avec stream 13 sur sim.py, tout en réutilisant sim.garch_panel quand la base suffit. Représente le plan pour revue, sans implémenter.

## Review of the third plan (verbatim)

> GO toujours suspendu. Deux corrections scientifiques supplémentaires au plan révisé : (1) le placebo brut qui garde qhat estimé sur calib brute et symétrise seulement la surveillance n'est pas un nul valide du bras qhat si qhat ≠ 1/2. Nomme-le contraste descriptif distinct, sans fpr_ref ni inflation causale; pour la garantie, limite la référence valide au bras half ou construis un nul calibré symétrisé distinct. (2) le FPR prédit par lattice.exceedance(q) sous choc asymétrique est une référence de bits iid, pas un critère PASS à 99 % pour le fond GARCH avec éventuelle dépendance ou q variable. Rapporte l'écart sans gate de conformité à cette prédiction. Mets à jour plan, sortie et tests; aucun code, puis représente le plan pour revue.

> Complément à la même révision, sans GO : pour la symétrisation du panel, utilise un SEUL signe Rademacher par jour partagé par tous les actifs afin de préserver la dépendance transversale. Sur D5 GJR, re-symétriser après coup le chemin en gardant les magnitudes ne reproduit pas le générateur avec levier (le signe passé influence la volatilité future). Le niveau H0 atteint vient des simulations directes de chaque générateur valide; la re-symétrisation GJR n'est qu'un benchmark diagnostique, pas un nul apparié équivalent. Mets à jour libellés, comparaisons et IC avant de représenter le plan.

## GO (verbatim)

> GO pour la révision 4 du plan stream 27, strictement F1 et P1-C/P3-C. J'approuve B1=F1 seul, B2=aucune revendication iso-FPR, B3=générateur local sans modifier sim.py, et H1–H5. Avant de coder, intègre ce GO au plan et transcris-le dans prompts/GO-stream-27.md. Deux précisions non bloquantes dans l'implémentation : nomme fpr_iid estimation Monte Carlo et fixe une tolérance statistique pour son test; si Wilson est utilisé sur fenêtres brutes symétrisées P3, qualifie son caractère conditionnel/approximatif. Implémente, vérifie sous .venv, commit local, puis arrête-toi avant fetch, push ou merge.

## Harmonization before coding (verbatim)

> Plan mode only. GO for revision 4 is unchanged. Before implementation, harmonize legacy sections in the plan: fpr_iid_mc is a Monte Carlo estimate with a 99 percent binomial tolerance in sections 5 and 10; include design=iid_scenario and reference_kind=symmetrized_window in authorized values; zero_neg on zero-rich backgrounds has an invalid sign-stream null and no FPR guarantee. Update the plan and show Ready to code. Do not implement yet.

## Start signal (verbatim)

> Start implementation now under the approved revision 4 plan and GO. Work only in this stream 27 worktree. Keep the project .venv active, implement F1/P1-C/P3-C as specified, run the plan checks, commit locally with the agreed Conventional Commit message, and stop before fetch, push, or merge. Preserve the four harmonized scientific labels in code, CSV, and audit. Do not seek another planning approval unless a new blocker appears.
