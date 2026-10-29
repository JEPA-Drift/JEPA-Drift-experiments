# PROMPT 14 — CA-T-JEPA v2 : représentation résiduelle compacte native, masquage sans fuite

**Statut : remplacement intégral proposé de** `prompts/streams/prompt-14-ca-tjepa.md`, à faire valider par Codex via nouveau plan/GO ; il NE modifie pas rétroactivement un GO antérieur. **Agent : Claude Code Opus 5.5 / Max, après signal explicite de rétablissement du quota.** Lire `CLAUDE.md`, le handover section 3.6 et `00_CODEX_AMORCAGE_2026_10_24.md`. Les décisions de conception ci-dessous sont **proposées**, pas des résultats scientifiques déjà mesurés.

## Contexte

L'Article C étudie l'efficacité de surveillance d'une dérive lorsque des représentations compactes concentrent l'information utile sans créer de KL. La baseline **P3-CS(b)** supprime déjà une grande partie de l'échelle commune instantanée sans apprentissage. L'architecture CA-T-JEPA historique apprend d'abord un plongement non linéaire puis applique une ACP blanchissante sur `calib` : la variante principale doit désormais avoir une dimension native compacte, et l'ACP aval doit rester un contrôle éventuel, jamais une nécessité pour P5. Le risque central du prétexte transversal est que le modèle reconstruise le facteur marché, voire voie les actifs masqués au travers de la normalisation ou de la soustraction préalable du marché.

## Tâche

### 0. Environnement, préservation de J1 et ordre d'intégration

- Conserver `.venv/bin/python` 3.12.9 et ses bibliothèques de référence (numpy 2.4.4, scipy 1.17.1, pandas 3.0.6). Appliquer la procédure approuvée conda-forge `pytorch=2.14.1=cpu_generic*` dans `.venv/torch-cf` (verrou 65 paquets) **si et seulement si** le paquet et le verrou existent dans l'environnement local à l'exécution ; ne pas substituer silencieusement une version, un canal ou un build. Si indisponibles : enregistrer le blocage et stopper cette étape sans modifier les versions de référence.
- Étape 1 : shim isolé par `PYTHONPATH` / `sitecustomize.py`, torch importable par `.venv/bin/python`, dépendances scientifiques toujours résolues depuis le parent. Exécuter `make check` (avec `.venv/bin/make`, réparer son lien si nécessaire) puis `make j1`. Contrôler les octets CRLF et le SHA-256 complet `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`.
- Étape 2 : n'ajouter `.pth` dans `.venv` qu'après réussite des deux contrôles ; les répéter sans shim. En cas de divergence, restaurer l'isolation, exposer la différence et **refuser la fusion**. Ne jamais réencoder le CSV de référence. Ne pas activer ni utiliser le Python de Trading pour exécuter les scripts.
- Prérequis de code : le stream 17 détient le socle partagé du passage des caractéristiques `C` à l'extraction. **Ne pas écrire simultanément** `representations/extract.py`, `tests/test_contracts.py` ou l'interface Z-1 depuis 14 et 17. Rebaser/importer le socle validé de 17 avant l'intégration de la fabrique `ca_tjepa`; conserver les changements non suivis de 17.

### 1. Définition de l'entrée et du masque

- Dataset principal : `d3_239`, uniquement `pretrain` pour ajuster les paramètres ; `calib` n'entraîne pas le tronc. Jeton d'actif `i` : rendement courant `x_{i,t}`, divisé par échelle `s_i>0` estimée une fois sur `pretrain`, et quatre caractéristiques continues `C_{i,t}` connues à l'ouverture du jour `t` via `data_loader.chars.load_chars_tensor` puis `impute_zero` ; enregistrer toutes les imputations. **Aucun** GICS statique dans la variante principale. Les analyses sectorielles avec GICS courants sont rétrospectives et hors J4.
- Prétexte principal : masquage **par groupes de caractéristiques point-in-time**, pas par secteur GICS statique. Construire un partitionnement déterministe de titres en groupes à partir des seules caractéristiques `pretrain` (statistiques, dictionnaire et graines figés), puis affecter les titres à ces groupes avec `C_t` connu avant `x_t`. Définir explicitement dans `configs/ca_tjepa.yaml` le nombre de groupes, la part masquée visée (30–50 % des actifs), les règles de groupes vides/absents, le traitement des titres sans caractéristiques et le mécanisme de masquage reproductible. Les groupes doivent être construits sans rendements futurs, sans catégories GICS contemporaines et sans consultations de `monitor`.
- Variante secondaire `mask=random` (actifs indépendants) ; `mask=sector_pit` seulement si l'existence et l'historicité des secteurs point-in-time sont prouvées dans un manifeste ; sinon le programme doit refuser cette option pour la campagne principale. Prévoir `mask=none` pour l'extraction gelée.
- **Ordre non négociable : MASQUER, PUIS ESTIMER les éléments transversaux de contexte.** Il est interdit de calculer sur la coupe complète une moyenne, variance instantanée, quantile, facteur GLS, projection résiduelle, cross-attention ou statistique de normalisation qui serait ensuite injectée aux jetons visibles comme si les actifs masqués étaient inconnus. Exception : une constante apprise auparavant et gelée (`s_i`, chargements `B`, poids `W`, etc.).
- Pour une neutralisation des facteurs `B` et `W` gelés, définir sur l'ensemble visible `V` un estimateur régularisé `f_hat(V)=argmin_f ||W_V^(1/2)(x_V-B_V f)||²+lambda_f||f||²`, avec `lambda_f>0` préspécifié dans `pretrain` (aucune inversion singulière). Les entrées de contexte sont `x_i-B_i f_hat(V)` pour `i in V`. Les **cibles** des actifs masqués peuvent utiliser leurs rendements `x_i` et le **même** `f_hat(V)` (stop-gradient) mais `f_hat(V)` ne peut dépendre d'aucun `x_j` masqué. Utiliser la même règle visible-only pour toute autre échelle quotidienne ; si la protection n'est pas démontrable, supprimer cette normalisation plutôt que tolérer une fuite.
- L'encodeur cible EMA peut voir le contenu de la cible masquée car c'est précisément l'étiquette auto-supervisée. Cependant **aucune information des cibles ne peut revenir au contexte par une normalisation globale, une attention croisée inverse, un état mutable ou un cache**. Tester explicitement le graphe de dépendances du contexte.

### 2. Réseau et bottleneck compact

- `jepadrift/jepa/ca_tjepa.py` : un encodeur de contexte équivariant à la permutation des actifs visibles : MLP par jeton, 2–4 blocs d'auto-attention sans encodage positionnel lié à l'ordre des titres, `d_model=64`, 4 têtes, LayerNorm admise, BatchNorm et normalisation temporelle entraînée sur les jours de `monitor` interdites. Au plus 1 million de paramètres **au total** pour la version principale (documenter précisément les sous-modules comptés).
- Encodeur cible EMA distinct, paramètres mis à jour uniquement lors du pré-entraînement : `xi <- m xi + (1-m) theta`, `m` suivant le calendrier existant 0.996→0.9995 ; cibles arrêtées au gradient. Prédicteur à deux couches alimenté par représentations du contexte et requêtes des caractéristiques des actifs masqués ; perte L2 latente sur ces derniers.
- Sortie **native** `g_theta(x_t,C_t) in R^d` pour `d in {2,4,8,16}`. Le passage de représentations par actif à la sortie quotidienne doit être une fonction équivariante/invariante à l'ordre des actifs, déterministe, explicitement documentée. Aucune ACP, SVD, rotation post hoc choisie sur `calib` ni blanchiment post-JEPA dans le pipeline P5 principal. La largeur `d` est fixée par configuration *avant* l'entraînement ; les modèles de différentes dimensions n'ont pas à être emboîtés.
- Le capteur de marché d'origine doit rester **séparé** du résiduel afin de ne pas confondre échec sur F1 et suppression volontariste de l'information commune. Exposer dans les métadonnées `channels={"market":..., "residual":...}` conformément à la convention Z-1, ou exposer explicitement un capteur de marché externe P3-C sans compter ce canal dans `d` résiduel. Ne jamais réclamer une rétention de KL du résiduel relativement à une dérive exclusivement de marché.
- Imposer les parités des têtes par construction pour les mêmes caractéristiques `C_t` : `z_odd(x,C)=(g(x,C)-g(-x,C))/2`, `z_even(x,C)=(g(x,C)+g(-x,C))/2`. Le nettoyage/centrage du marché et les échelles du jour doivent respecter la parité lorsqu'ils sont recomputés sur `-x`. Pas d'EMA, dropout ou injection de bruit stochastique en `eval`.
- Les capteurs de covariance peuvent exploiter des statistiques paires (par exemple énergie de `z_odd`), mais ne pas rebaptiser automatiquement `z_even` « énergie » si sa valeur signée ou sa définition ne le garantit pas. Documenter précisément les dimensions, la parité, et les modèles de null admissibles pour chaque tête.

### 3. Objectif, anti-effondrement et variantes

- `L_total = L_JEPA + lambda_var L_var + lambda_cov L_cov + lambda_market L_market`. `L_var` : pénalité VICReg de non-effondrement sur la **sortie quotidienne** pour chaque coordonnée active ; `L_cov` : énergie des termes hors diagonale de la covariance inter-jours du lot ; `L_market` : covariance train avec facteur marché, **optionnelle** et coefficient préspécifié car peut retirer un drift utile. Documenter les poids, leur normalisation, l'effectif réel de jours et les cas `B<=1` ou variance nulle. Une isotropie marginale n'implique ni gaussianité ni indépendance des signes.
- Si `g` est appris à partir des vues masquées, définir aussi de façon déterministe la vue complète `mask=none` qui alimente `z_odd`/`z_even` à l'inférence ; la pénalité anti-effondrement doit explicitement toucher cette **vue d'extraction**, pas seulement les embeddings de jetons masqués.
- Variante de contrôle `post_pca_legacy` : ancien schéma JEPA + ACP blanchissante, exécutable uniquement en ablation hors protocole J4 principal et si le code de lecture existe ; ne pas en dépendre pour `P5`. Variantes `mae` et `temporal` : interfaces conservées mais les implémenter seulement si les contrats et la version native sont stabilisés, et uniquement comme résultats secondaires. Une variante `orthogonal_head` peut être enregistrée en expérimentation, non dans la porte J4 sans préspécification avant freeze.
- Inclure un contrôle de prétexte **sans prédictibilité résiduelle** : générateur où les chocs idiosyncratiques sont conditionnellement indépendants après retrait du facteur. La perte de prédiction attendue ne doit pas être interprétée comme un couplage résiduel si le modèle ne dépasse pas le prédicteur constant sur ce contrôle.

### 4. Pré-entraînement, lecture et interface Z

- `experiments/jepa_pretrain.py` : afficher sur stdout une ligne machine-readable `CHECKPOINT_PATH=<chemin_absolu>` après sauvegarde du checkpoint ; AdamW, paramètres fixes approuvés dans `configs/ca_tjepa.yaml`, au plus 200 époques, batch 64 **jours**, CPU et déterminisme. La validation/early stopping utilise exclusivement un découpage temporel **interne à pretrain** avec embargo explicite ; la `calib` externe n'influence ni poids, ni architecture, ni nombre d'époques ni sélection de la variante. Les données `monitor` ne doivent jamais être ouvertes par ce script.
- Artifacts sous `ckpt/<hash>/` ignorés par Git : poids, config complète, manifeste/empreintes, registre de graines, traces de pertes, versions, `d`, méthode de masque, checksum de l'encodeur cible et du tronc. Les seuls sidecars publiables référencent des empreintes, jamais des données confidentielles.
- `jepadrift/jepa/representation.py` implémente `representations.base.Representation` et `fit(X_calib,C_calib,dates)` ; `_fit` ne peut modifier **aucun paramètre ni statistique apprise de `g`**, au plus préparer des éléments de null / calibrage du moniteur expressément séparés et gelés. `state_hash` inclut tous les checkpoints, normalisations, chargements, têtes, choix de canaux et constantes pertinentes ; un chargement avec `state_hash` incohérent échoue.
- `_day(x_t,C_t)` n'utilise que la coupe du jour, les caractéristiques disponibles et l'état gelé ; `transform_panel` jour par jour par défaut. Une vectorisation est admissible uniquement si égalité **bit à bit** avec l'empilement de `_day` est prouvée par test. Empêcher un cache persistant entre jours à l'extraction. Déclarer strictement les canaux et `heads` avec `odd_head` conforme à Z-1.
- Enregistrer paresseusement `ca_tjepa` dans `representations/extract.REGISTRY` seulement après intégration du socle C du stream 17. L'import de `jepadrift.representations` ne doit pas importer torch. `--ckpt` et `--D` doivent vérifier la cohérence avec les poids et le manifeste ; conserver D2/PCA inchangés.

### 5. Batteries TDD et tests négatifs adversariaux (RED avant GREEN)

Écrire les tests AVANT les corrections et vérifier que chaque violation volontaire produit RED :

1. **No-leak sous masque** : deux coupes ayant mêmes rendements visibles et mêmes `C_t`/état figé, mais rendements masqués arbitrairement différents, doivent produire **exactement** les mêmes jetons de contexte, facteurs `f_hat(V)`, échelles de contexte et prédictions avant consultation de la cible. Pour les cibles, l'invariance n'est pas requise. Tester masques aléatoire et groupes.
2. **Ordre de masquage** : un pipeline factice normalisant la coupe complète avant masque doit faire échouer le test précédent ; une neutralisation visible-only doit le réussir, y compris au bord (`|V|` petit, groupes dégénérés).
3. **Parité** : `||z_odd(x)+z_odd(-x)||_infty<=1e-6`, `||z_even(x)-z_even(-x)||_infty<=1e-6`, pour zéro, permutations, fortes amplitudes et cas de facteur marché résiduel. Aux égalités `sign(0)`, tester les pièces indépendantes.
4. **Equivariance/invariance** : permutation commune de `x`, `C`, `B`, `W` et masque puis inversion de permutation : sorties agrégées identiques à la tolérance flottante spécifiée ; pas de positional encoding d'actif.
5. **Gel** : hachages identiques des poids, buffers, normalisations, chargements et tête sur une séquence de `monitor` ; test volontaire avec `EMA.update()` en `_day` doit être RED. Même hachage entre deux extractions.
6. **Frontières** : déplacer artificiellement une valeur future de `monitor` ou `calib` ne change pas le checkpoint sélectionné après pré-entraînement ; ne pas apprendre à partir de `calib` si destinée au readout.
7. **Null et canaux** : test de signes univariés sous D6 avec géométrie figée, **sans** supposer indépendance entre canaux. Si un détecteur gaussien multivarié est réutilisé, vérifier son hypothèse sous-gaussienne jointe ou le désactiver pour cette tête.
8. **Anti-effondrement** : tête quotidienne constante est détectée et pénalisée ; vérifier variance, covariance, RankMe et nombre de coordonnées actives sur prétrain/validation interne. Aucune corrélation au marché annoncée « nulle » sur seule base d'une pénalité.
9. **Torch guards** : quatre gardes réelles de `tests/test_contracts.py` sont exécutées et passent, sans `skip` masqué. Test déterministe CPU, `torch.use_deterministic_algorithms(True)`, `torch.set_num_threads(1)`, `SeedSequence` et `torch.Generator` locaux pour initialisation/masques/batches.
10. **Non-régression** : extraction D2/PCA et autres chemins conservés ; tests de découplage au vert ; environnement parent conservé ; **J1 hash/CRLF inchangé**.

## Entrées

`CLAUDE.md`; `prompts/wrapups/handover-01-27.md`; prompt 14 antérieur et GO/plans ; `jepadrift/representations/{base,extract,cross_section,pca}.py`; `jepadrift/data_loader/chars.py`; résultats `J1_report.md`; promps 16/17/21/22 et conventions `C-repr-rows`; `configs`/manifests de D3. Ne pas déduire une forme de tensor de son nom : vérifier la signature effective des API et conserver leurs contrats.

## Livrables

`jepadrift/jepa/{ca_tjepa,representation}.py`; `experiments/jepa_pretrain.py`; `configs/ca_tjepa.yaml` ; `tests/test_ca_tjepa.py` et tests de contrat existants renforcés ; fabrique paresseuse dans `representations/extract.py` une fois socle 17 fusionné ; verrou torch approuvé ; `docs/sections/ca_tjepa.md` ; rapport d'audit anti-fuite et gestion de masques ; sidecars des checkpoints ; plan/GO/wrapup ; écarts documentés dans `docs/DEVIATIONS.md`.

## Contraintes techniques

Aucun import de `jepadrift.injection` ou `jepadrift.monitors` depuis `jepadrift/jepa`. Pas de BatchNorm ; pas de modèle mutable en surveillance ; `dtype` et état reproductibles ; conformité Python 3.12 et Z-1 ; pas de téléchargement de données à la volée ; coût CPU du smoke <10 minutes si le modèle le permet, sinon mesures/diagnostic et GO explicite avant changement de budget. Pas d'entraînement sur fonds injectés pour obtenir un gain J4. L'usage des termes « secteur » et « groupe de caractéristiques » doit être non ambigu dans code et CSV.

## Critères de succès

Une extraction native compacte `d in {2,4,8,16}` fonctionne sans ACP aval ; les dix familles de tests passent ; aucune fuite d'actif masqué au contexte ; parité, gel et état SHA-256 vérifiables ; au plus 1 M de paramètres ; smoke 2 époques/200 jours reproductible ; `make check` complet, quatre gardes torch sans skip et `make j1` avec signature CRLF native inchangée. Si l'environnement ou un contrat est bloquant : livrer un rapport BLOCKED circonstancié, jamais un succès simulé.

## Commandes de vérification

```bash
cd "$(git rev-parse --show-toplevel)"  # depuis le worktree 14 désigné par Codex
.venv/bin/python -m pytest -q -rs tests/test_ca_tjepa.py tests/test_contracts.py tests/test_decoupling.py
LOG_14=$(mktemp)
.venv/bin/python experiments/jepa_pretrain.py --config configs/ca_tjepa.yaml --smoke | tee "$LOG_14"
CHECKPOINT_14=$(sed -n 's/^CHECKPOINT_PATH=//p' "$LOG_14" | tail -n 1)
test -n "$CHECKPOINT_14" && test -d "$CHECKPOINT_14" || { echo 'Checkpoint absent'; exit 1; }
.venv/bin/python -m jepadrift.representations.extract --dataset d3_239 --rep ca_tjepa --ckpt "$CHECKPOINT_14"
rm -f "$LOG_14"
.venv/bin/make check
.venv/bin/make j1
.venv/bin/python - <<'PY'
from pathlib import Path
import hashlib
p = Path('results/e2/e2_cells.csv')
b = p.read_bytes()
expected = 'e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823'
assert hashlib.sha256(b).hexdigest() == expected
assert b'\r\n' in b and b.replace(b'\r\n', b'').find(b'\n') == -1, 'J1 is not native CRLF'
print('J1 CRLF/SHA-256 PASS')
PY
```

Aucune commande de commit, push, rebase ou fusion ne doit être exécutée si cette vérification échoue. Le placeholder de checkpoint est **uniquement** une valeur produite par le script d'entraînement ; il ne doit jamais être inventé.
