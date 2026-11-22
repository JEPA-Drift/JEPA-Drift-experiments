# Stream 32 — réception B2o, contrôleur SETUP

Date : 17 novembre 2026. Décision Codex distincte : **B2o REÇU COMME COMPOSANT LIMITÉ**.
Autorité : GO B-TDD et plan v2.1 inchangés, réception B2n conservée.
Cette décision suit la revue des derniers tests et le bilan indépendant de review_plan32.
B2 complet reste non reçu ; aucune nouvelle porte scientifique ou runtime n'est ouverte.

| Observation | Décision | Justification / tests et disposition |
|---|---|---|
| Préconditions et auteur | ACCEPTED | GO B, plan/amendement, source/tests et producteur scellé vérifiés par SHA avant chaque capture et contrôle. Même session native e8ae637e/opus/max ; patches complets relus, contre-revus puis appliqués nativement sur364e. |
| Contrôleur SETUP | ACCEPTED | Extraction commune des paramètres/métadonnées et setup_phase ; frames primitives avant fits, un fit par clé partagé entre applications. Métadonnées, identités incluant moyenne et libellé T7 GAUSSIAN_PROXY reçus conservés. Aucun producteur scellé modifié. |
| Admission et plan | ACCEPTED | Six refus avant effets : autre design avec GO réellement valide, autorisation retirée, GO altéré, autorité de contexte forgée, extra fit non planifié, plan malformé. Exceptions directes, arbres et entrées préservés. |
| Préflight des caches | ACCEPTED | État entier et chaque cache disponible vérifiés avant producteur : T7 corrompu avant Gaussian manquant, DEV sans SETUP, V non carré, N faux. Inventaire exact, dimensions/valeurs V/lam/mean et appartenance des setups engagés contrôlés. |
| Intégrité et reprise | ACCEPTED | NPZ engagé corrompu/manquant, inventaire faux à digest générique valide, appartenance dérivée fausse et JSON sans NPZ refusés. Reprises après frame/fit/métadonnées et orphelin NPZ sans JSON ne reproduisent que les clés manquantes ; octets durables et record/digest égalent la référence terminée avant changement de ROOT. |
| Ressources simulées | ACCEPTED | Checkpoints sur préflight/rechargement/erreur et métadonnées, journal monotone par token ; CPU/mur bloquent aussi le retour complet. Gardes avant producteur et avant commit passantes, statuts exacts et caches préservés. |
| Exceptions et HEAD | ACCEPTED | Refus réels T22 et trace MARKET propagés avec leur CPU, sans relance ni exception masquée. HEAD Gaussian inconclusif engagé avec fit/coordonnées initiaux, puis rechargé sans recalcul ; aucune conclusion de détectabilité ou non-infériorité. |
| Coordonnées et mode | ACCEPTED | N24/N26 et fit_id Gaussian0/1, deux frames/trois fits partagés entre dix métadonnées. FULL avec vrai GO temporaire, smoke de fonction avec authorization=None/go_reference=None et sans GO. Aucun smoke de campagne. |
| TDD et préservation | ACCEPTED | RED réel7failed503passed avant corev2,3failed510passed avant CPU-GREEN,2failed515passed avant BudgetGREEN ; contrôles déjà verts conservés.34nouveaux cas au total depuis B2n,537cas finaux. Ancien préfixe et AST conservés à chaque append ; coreGREENv1 jamais appliqué. Aucun affaiblissement de test. |
| Vérification et contre-revue | ACCEPTED |537passed12.21s, pytest0/contrôles0, pyflakes/diff propres sous .venv/environnement déterministe/verrou partagé. Bilan review_plan32 : aucun témoin B2o précédemment exigé restant manquant ; aucun test exécuté par le relecteur. |
| Portée de réception | MODIFIED | Contrôleur SETUP reçu sur fixtures déterministes et horloges factices. Ces témoins n'attestent ni vraie campagne de fits, ni mémoire agrégée/préemption/performance, ni worker lifecycle ou CPU hors checkpoints. Ces réserves globales restent dues, sans report implicite enC. |
| Réception globale B2 | REJECTED | DEV équilibré à quatre familles, politiques figées, prior commun et raccordement des dérives restent dus. Autres phases/driver/T15/T16global/CLI/T68 et ressources restent bloquants pour leurs lots/contrats respectifs. |

| Pièce | SHA-256 |
|---|---|
| Source finale,96373octets | `96a1e2409f7d71ccff0f51110fccf35380fc9aa95346a4597b966bdf32fda082` |
| Tests,416385octets/537cas | `d772317aab7a2748864a8180a9d89f1e29a9d5b2d7e2f64311e98a73f8d0559c` |
| Producteur PCA/2 inchangé | `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373` |
| Capture finale tests coordonnées | `e828d197fb47a4e632dcf18b3f28481ad6f20c58e931e9a4726cd3478934a659` |
| Journal pytest final | `ca2edf4c04d11022b505c09e755e41a31e7530105e05fabfa658a606bcc003e3` |
| Journal contrôles final | `2a39689b387b792018696d58ac42fef33569451be070d2c768c316b40d4a18c4` |

Commande C0 : `-m pytest tests/test_pca_info_online.py tests/test_check_prompts.py -q --tb=short`.
Décisions détaillées : REVIEW-stream-32-B2o-green-core-v2, cpu-green, budget-green,
recovery-tests, authority-tests, integrity-tests, exception-tests et coordinate-tests du17novembre.
Les captures en quota/timeout ont été rejetées ; leurs reprises réussies sont tracées,
aucun minuteur restant. Tous callbacks B2o traités ; ne réappliquer aucun patch.

Matrice68 conservée :18PASS/0FAIL/50NOT_RUN. T22/T41/T45/T46/T64/T65 et autres contrats
raccordés restent partiels jusqu'à leurs preuves globales ; aucune promotion par cette seule réception.
Suite autorisée dans B2 : tests seuls des briques DEV/politiques/prior/raccordement,
puis revue/RED réel avant chaque nouvelle production et réception distincte.
Terminer B2 COMPLET puis STOP et prompt de reprise Codex sur modèle00du12novembre.
Aucun B3/B4 par cette instance. C/runtime/smoke de campagne/profilage/pilote/full/
réel/2020+/JEPA/autres streams/RemoteControl/commit/push/réindexation restent fermés.
