# Stream 28 — avenant chercheur P0/P1, reprise ciblée à 18:52 UTC

Date : 2026-10-30. Source : instructions directes du chercheur pendant la Phase B. Cet avenant prime sur la règle de calibration du plan v2, le GO initial et les tests hérités. Codex enregistre et orchestre ; Claude Code reste l'unique auteur du code applicatif. Aucun nouveau chantier ni nouvelle Phase A générale.

## Autorisation et ordre

Reprendre la même conversation et les fichiers existants. **P0 d'abord**, avec ses tests ciblés, puis les ajustements P1, la documentation et un nouveau double smoke. Ne pas recréer le runner ni réinitialiser l'implémentation. Aucun full, aucune évaluation réelle post-2019, aucun autre stream, aucun commit/push autonome.

La session précédente est éteinte après quota : « resets 6:50pm (UTC) ». Relance unique **2026-10-30 à 18:52 UTC**, demandée explicitement par le chercheur ; 18:50 UTC correspond à 19:50 CET. Aucun changement de compte, modèle ou effort ; conserver opus/max et Remote Control. Aucun sleep ni boucle de relance.

## P0 — rang prédictif obligatoire

Pour n maxima finis non vides et alpha dans (0,1), remplacer le budget empirique floor(alpha*n) par :

```python
r = floor(Fraction(str(alpha)) * (n + 1)) - 1
```

Si r<0, lever la défaillance dédiée et émettre `CALIBRATION_FAILED` avec effectif insuffisant ; ne pas fabriquer un seuil ou une garantie. Sinon b=sorted_maxima[n-r-1], seuil GT=b, seuil GE=nextafter(b,+inf). Si le seuil nécessaire n'est pas fini, `CALIBRATION_FAILED` explicite. Un seul nextafter, aucune boucle ULP.

Sous échangeabilité des maxima de calibration et du nouveau maximum, P(max_new>b)<=(r+1)/(n+1)<=alpha ; les égalités sont conservatrices. La garantie est marginale sur calibration et nouvelle trajectoire, conditionnellement aux choix/paramètres déjà figés sur fit et nuisance indépendants. Elle n'est ni une garantie conditionnelle à chaque seuil réalisé ni une propriété d'e-processus. `anytime_valid=False` et le statut de quasi-vraisemblance restent inchangés.

Ne pas annoncer cette garantie pour une trajectoire historique et des fenêtres nulles chevauchantes. Un taux holdout peut différer de la borne : c'est une observation indépendante, pas la borne elle-même. Aucun ajustement sur le holdout pour forcer 5 %.

### Schéma avant gel

Version autorisée : **pca_drift_benchmark/2**, remplaçant /1 pour les nouveaux artefacts. calibration.csv distingue :
- `calibration_fraction` : fréquence empirique des alarmes de calibration ;
- `threshold_rule` : `predictive_exchangeable_rank_v2` ;
- `predictive_bound` : (r+1)/(n+1) uniquement lorsque la garantie est applicable, sinon NA ;
- `guarantee_basis` : `EXCHANGEABLE_SYNTHETIC_PATH_MAXIMA` ou `NOT_ESTABLISHED_HISTORICAL_WINDOWS` ;
- `rank_r` et `n_cal` permettent de retrouver le numérateur et le dénominateur exacts ;
- aggregates.csv conserve `fpr`, `fpr_lo`, `fpr_hi` et n comme FPR effectivement observée sur holdout, sans les remplacer par alpha ou predictive_bound.

Reporter règle, hypothèses et empreintes dans le manifest et la documentation. Le discriminant de calibration dans les identifiants devient predictive_exchangeable_rank_v2 ; conserver les contrats de réutilisation E1/E2 et MIX E3/E2 k20. Aucun mélange de cellules /1 et /2.

### Tests obligatoires

- n=40, alpha=.05 : r=1, borne 2/41.
- n=2000, alpha=.05 : r=99, borne 100/2001 (test de rang déterministe, pas un run full).
- n=1, alpha=.05 : CALIBRATION_FAILED ; adapter aussi les anciens tests n=5 à .05 qui acceptaient un seuil.
- Ex aequo, GE/GT, seuil GE non fini, maxima invalides, explication des insuffisances.
- Garantie applicable aux trajectoires synthétiques échangeables ; absente pour les fenêtres historiques chevauchantes et la trajectoire réelle.
- Colonnes et empreintes séparant taux empirique, borne prédictive et FPR holdout ; fixtures minuscules adaptées sans changer alpha du smoke ni des expériences.

## P1 — corrections mesurées, sans nouvelle définition scientifique

1. **mixture_cost** : garder l'équation et brentq ; encadrement dynamique par doublement avec validation de finitude des paramètres, bornes et évaluations, et échec explicite si aucun encadrement fini n'est obtenu. L'existant double déjà : compléter ses contrôles, pas une nouvelle méthode.
2. **Dimensions** : scan_statistic infère p=Z.shape[-1] ; vérifier au point de construction du flux quadratique que p=d(d+1)//2. Le flux vech n'est pas présumé gaussien isotrope ; rester en quasi-vraisemblance calibrée. Garder tous les tau.
3. **Exhaustif** : conserver les extractions (lot,d,d), solve/slogdet par lots, plafond effectif <=20000 et <=mémoire disponible. L'existant réutilise déjà les valeurs d'un même sous-ensemble pour plusieurs k : préserver cette propriété. Ajouter les contrôles de temps/mémoire entre tous les lots, même à l'intérieur d'un même d. Dépassement -> BLOCKED_RESOURCE, jamais de recherche approchée. Tester les bornes du lot, l'arrêt entre lots et la réutilisation.
4. **RNG** : conserver SeedSequence et la hiérarchie de clés du plan. Domaines stables, sans chemins absolus ; vérifier l'unicité des clés sémantiques/entropies pour les rôles effectivement exécutés avant les tirages. Le CRC32 existant peut être conservé sur le vocabulaire fini si les collisions de cet ensemble sont explicitement détectées/refusées ; aucune garantie universelle attribuée au CRC32, aucun changement de graine pour contourner un résultat. Tester les rôles exécutés et le refus d'une collision injectée.

## Résultats existants et nouveaux smoke

Le smoke /1 présent dans results/pca_drift_benchmark/smoke/ est **pré-avenant**, non scellé et non admissible comme preuve de la règle prédictive. Le conserver octet pour octet, avec ses anciens logs et partitions. Son journal indique 36.5 s, 0.308 Gio RSS et 358 partitions calculées ; le journal TDD indique 41 tests réussis avant P0. Aucun double smoke corrigé n'est encore exécuté.

Nouveaux chemins autorisés, neufs :
- primaire : results/pca_drift_benchmark/smoke_predictive_v2/ ; logs/pca_drift_benchmark/smoke_predictive_v2/ ;
- répétition : logs/pca_drift_benchmark/smoke_predictive_v2_repeat/out/ et sous-répertoire log/.

N239, H250, n_center=n_cal=n_null=n_alt=40, deux fonds A/B30/C, un processus/threads=1, .venv partagé, 8 Gio et 30 minutes par invocation, inchangés. Les anciennes partitions ne sont pas reprises avec un fingerprint modifié. Comparer les sept fichiers et l'identité scientifique, rapporter les deux durées, RSS et hashes ; ne pas inventer un succès si le quota ou le budget interrompt la reprise.

## Livrable et clôture

Décrire les diffs réellement appliqués, les nouveaux tests et sorties exactes, le double smoke corrigé, le coût mesuré et les limites. P0 est identifiable séparément dans la trace de tests/diff, sans commit intermédiaire par Claude. Préserver E2 disque/index CRLF/SHA-256 et E3/D8 ; rien sous la propriété des streams 29–31. Codex seul audite, invoque la clôture formelle, vérifie make check, réindexe et intègre, après extinction des processus. Aucun gel du schéma avant vérification de P0 et du nouveau double smoke.
