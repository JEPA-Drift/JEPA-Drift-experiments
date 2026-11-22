# Notification de revue scientifique et technique à Codex — Stream 32, plan natif v2

**Décision de revue du chercheur — 14 novembre 2026.**
Pièce examinée : `ex-cute-la-mission-de-gleaming-bird.md`, intitulée « Plan natif — Stream 32 PCA-INFO-ONLINE (PLAN ONLY, v2 ciblée) », 799 lignes.
**Statut demandé : `PLAN_V2_CORRECTIONS_REQUIRED`; aucun GO technique, pilote ou full émis par cette notification.**
La revue précédente (notification 14) est **globalement satisfaite**. Ne pas rouvrir ses arbitrages A1–A3 / B1–B3 ni réécrire l'architecture ; corriger les anomalies résiduelles ci-dessous dans une v2.1 (amendement versionné), puis soumettre à la revue Codex.

## C1 — CRITICAL : dépendance circulaire des empreintes d'autorisation

**Constats normatifs :**
- §2.3 / §2.4 : `authorize(mode,cfg)` s'exécute *avant* `build_setup`, `DEV`, `CAL`, `NULL_PLAN`.
- §4.1 : `dev_id` inclut `qbar_sha`, `d_dev`, `s2_dev`, issus de DEV ; ces objets ne sont pas connus avant DEV.
- §10 : `n_hold` et `plan_id` sont calculés par NULL_PLAN *après* CAL et dépendent des observations nulles.
- §13 : l'identité scientifique inclut `dev_id`, `calibration_id`, `plan_id`; `run_id = sha16(identity)` sert aussi à nommer les artefacts et les partitions.
- §14 : le GO doit contenir un `scientific_identity_sha256` égal à cette identité *avant toute écriture* ; sinon `AuthorizationRefused`.

**Conclusion :** le pilote exige un digest contenant un résultat DEV non encore calculé ; le full ajoute un digest NULL_PLAN non encore calculé. La précondition est impossible sans exécuter clandestinement les phases censées être protégées. C'est un deadlock conceptuel d'autorisation et d'identité ; ne pas le contourner en acceptant un hash provisoire non vérifié.

**Correction imposée :**
1. Définir un `design_id` **entièrement calculable avant tout tirage** : spécification canonique, code/environnement/inputs, graines et domaines, politiques, définition de DEV et NULL_PLAN, bornes autorisées `n_hold <= n_cap`, rôle/cellules, GO et enveloppe. Aucune statistique réalisée, sélection DEV, seuil calculé, ou valeur de `n_hold` n'y figure.
2. Le GO autorise précisément `design_id` et un périmètre maximal (stages/roles/setups/policies/families, ressources). La vérification doit se faire avant tout calcul, création de sortie scientifique et lancement de worker.
3. Une fois le GO admis, exécuter DEV, CAL puis NULL_PLAN dans un **espace de staging déterministe** dérivé de `design_id`. Produire un `realization_id`/`final_scientific_identity` contenant `dev_id`, seuils, `plan_id`, `n_hold`, empreintes des partitions et des sorties. Les fichiers manifestes finaux sont publiés atomiquement avec cette identité, sans réautorisation rétroactive ni modification de la portée approuvée.
4. Préciser le statut et la reprise en cas de crash entre DEV, CAL, NULL_PLAN, HOLD et manifeste final. `design_id` constant ; la reprise recalcule/contrôle les SHA et refuse toute divergence. `run_id` ne peut pas être requis pour créer un répertoire avant son calcul s'il dépend du `realization_id`. Deux identités séparées, aucune collision de répertoires.
5. `authorization` et la télémétrie restent hors identité scientifique selon un contrat clair ; le GO approuve le *design*, et non une réalisation encore inconnue.

**Tests de sortie de revue :**
- Autorisation valide de pilote et full sur une fixture `DEV/NULL_PLAN` avec résultats variables ⇒ succès **sans SHA futur préconnu**.
- Modification d'un paramètre de design, de code/source approuvé, de seed ou d'une limite ⇒ refus avant tout tirage/écriture.
- Interruption après DEV, CAL et NULL_PLAN puis reprise ⇒ même réalisation finale (SHA scientifiques), aucun recalibrage silencieux.
- `n_hold > n_cap`, partition ou hash de phase incohérent ⇒ refus/STOP.
- `--mode pilot|full` sans GO ⇒ refus, même sur une configuration complète.

## C2 — IMPORTANT : non-infériorité HEAD potentiellement vacueuse à horizon censuré

**Constat :** H2 (§9.3) veut montrer
`E[min(T_INFO,H)] < 1.10 E[min(T_PREFIX,H)]` sur `F_HEAD_RESIDUAL`, avec `H=250`.
Mais, par définition, `E[min(T_INFO,H)] <= 250`. Donc **si**
`E[min(T_PREFIX,H)] > 250/1.10 = 227.27 jours`, H2 est automatiquement vraie quelle que soit la qualité d'INFO, y compris lorsque INFO ne détecte jamais. Ce cas est plausible en présence de censure ; H2 ne constituerait alors aucun contrôle positif.

**Correction demandée :**
- Conserver H2 comme contraste, **mais préenregistrer avant tout ALT confirmatoire une condition de non-vacuité** : le préfixe doit avoir une puissance/détectabilité suffisante sur HEAD, définie par un seuil scientifique explicite (sur RMST_H ou taux de détection au-delà de sa FPR propre). Ne pas fixer ce seuil après avoir vu le test.
- Ajouter un contrôle *géométrique* de la famille HEAD dans la **base FITTED** : les déplacements sont définis sur les PCs de population, et un fit LW peut redistribuer leur information. Vérifier, sans consulter les performances ALT, quelle fraction de l'information HEAD atteint le préfixe canonique ajusté et si HEAD demeure réellement « favorable au préfixe ». Rapporter `DESIGN_CONTROL_INCONCLUSIVE` si l'hypothèse échoue, **sans choisir ex post** un fit plus avantageux.
- Distinguer `H2_NONINFERIORITY_SUCCESS` de `HEAD_POSITIVE_CONTROL_VALID`. Une non-infériorité statistique sans contrôle positif valide n'autorise **pas** de conclure que le classement informationnel « n'abîme pas les cas où le préfixe est bon ».
- Tests déterministes : `RMST_PREFIX=H`, `RMST_INFO=H` ⇒ H2 doit être classée **non probante**, pas comme contrôle positif confirmé ; test de désalignement HEAD FITTED ; test de seuil de non-vacuité sans accès aux autres ALT.

## C3 — IMPORTANT : cohérence du régime de publication et des essais smoke

- §13 : `run_id=sha16(identity)` alors que les exemples CLI permettent des chemins `.../smoke_j1`, `.../smoke_j8` ; expliciter que `--output-dir` est un répertoire libre de **staging** ou un nom de destination, non une identité scientifique. Ne pas faire dépendre les identifiants d'un chemin ou des jobs.
- §14 : `SMOKE_NO_CLAIMS` doit rester purement fonctionnel. Les sorties ALT de smoke ne doivent ni servir au choix de R1, ni à l'ajustement de I*, w, s2, supports, δ_NI ou de la famille Φ. Pour R1, geler les décisions **avant** toute consultation de la puissance smoke/pilote (pas seulement du full).
- §17 : maintenir les chiffres d'unités comme **prévisions non mesurées**, sans garantie de coût CPU. Prévoir une première exécution de bout en bout sous GO runtime testant les deux empreintes et leur reprise, puis le benchmark 1/4/8/12 workers.

## Vérifications déjà positives (à préserver)

- Les méthodes ONLINE ne reçoivent pas d'identité de famille ni de métadonnées oracles, et réutilisent une calibration entre familles (§4).
- Top-q et glouton sont reconnus équivalents pour une KL additive et un coût cardinal (§3.2).
- Le scan adaptatif utilise des masques prévisibles, sans rescoring, et conserve le contrôle des fausses alarmes par calibration de la politique entière (§3.5, §8).
- Le coût M est correctement qualifié de *fluid proxy*, distinct du prior s2 commun et du RMST observé (§3.3, §3.6).
- CP tri-état, équivalence TOST, multiplicité, rôles indépendants et gain contextuel sont correctement distingués (§8–10), sous réserve des imperfections asymptotiques annoncées.
- Les chiffres spectraux EXACT CPV90 N=32/N=239 et RESIDUAL_CPV90 sont cohérents avec le spectre λ prévu, sous réserve du recalcul dans les tests.

## Livrables attendus de Codex

1. **Disposition C1–C3 :** `ACCEPTED`, `MODIFIED` ou `REJECTED` + raison vérifiable (contrat de source, équations et test).
2. **Plan v2.1 ciblé**, avec diagramme de séquencement `design authorization -> DEV -> CAL -> NULL_PLAN -> HOLD -> ALT -> final manifest`, et une table des identités pré-exécution/post-exécution.
3. Une spécification de **non-vacuité du contrôle HEAD**, avec hypothèses et étiquettes de résultat.
4. Les tests supplémentaires intégrés à la matrice TDD sans retirer les 51 tests de v2 ; le code de production doit rester dans le périmètre initial.
5. Revue autonome de Codex, puis seulement une décision explicite de GO technique. Conserver pilote/full sous GO scientifiques séparés.

**Décision : PLAN V2 NON ENCORE APPROUVÉ ; CORRECTIONS CIBLÉES AVANT GO.** Stream 23 déjà clos selon le plan v2. Stream 32 reste P0 ; aucune réouverture d'E4, des producteurs PCA `/2`, d'un JEPA ou de données réelles.
