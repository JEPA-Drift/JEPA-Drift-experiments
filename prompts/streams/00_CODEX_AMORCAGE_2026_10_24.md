# AMORÇAGE — Codex orchestrateur, JEPA-Drift Article C

**Destinataire : Codex**, orchestrateur du dépôt LOCAL `~/JEPA-Drift-experiments`. **Nature : directive stratégique et d'exécution** ; elle n'autorise ni réécriture destructrice d'un worktree existant, ni lancement contre un quota suspendu.

## Mandat et vérité de départ

Tu es le responsable de l'intégration scientifique et technique des streams de l'Article C. Ta mission n'est pas de « faire gagner JEPA » ; elle est de tester, sans fuite ni inflation de fausses alarmes, si l'apprentissage prédictif apporte un gain **incrémental** relativement au retrait du marché et à la normalisation de degré zéro `P3-CS(b)`, ainsi qu'à la baseline IPCA `P4`. La représentation ne crée jamais de KL : pour le même jeu d'informations disponible, `I(Z) <= I(X,C)` par traitement des données. Distingue systématiquement *information présente*, *alignement du détecteur* et *validité/calibration du null*.

Lecture impérative avant toute commande modifiante, dans cet ordre : `CLAUDE.md`, `prompts/wrapups/handover-01-27.md` (priorité absolue à sa section **3.6**, datée du 23/10), `prompts/streams/INDEX.md`, les plans/GO/wrapups des streams actifs, `docs/DEVIATIONS.md`, les contrats `tests/test_contracts.py` et `tests/test_decoupling.py`, puis les directives ci-jointes. Le miroir GitHub n'est **pas** l'autorité pour les états locaux. L'état historique signalé est `main=c2848234bf48bb56699983e7470f0e4bc4a7c3f1`, localement 11 commits devant un `origin/main` relevé à `ef63362` ; c'est un point de comparaison, pas une assertion sur l'état au moment où tu exécutes ce prompt. Vérifie `git rev-parse HEAD`, `git status --short`, `git worktree list --porcelain`, branches, commits et sessions avant d'ordonner quoi que ce soit. En cas de divergence, documente-la, préserve le travail préexistant et réconcilie les plans.

Le transfert constate : 08b et 27 fusionnés ; 12 sans code E1 final ; 13 avec code/plan non commités ; 14 sans code ni checkpoint ; 17 avec socle C partiellement commité, tests non suivis ; 18 sans code ; 23 phase 1 dans sa branche seulement. Ne traite AUCUN de ces statuts comme encore certain sans audit local. La mention historique de quota Claude suspendu jusqu'au 25/10 à 12:00 UTC+1 n'est pas une autorisation de reprise à cette heure : **aucune sollicitation, relance, watcher ou interruption de session Claude avant notification explicite du chercheur**. La préparation de plans, les vérifications ponctuelles en lecture seule et les délégations permises à Vibe restent soumises à la politique locale.

## Invariants absolus, testables

1. **J1 natif, identique à l'octet** : après `make j1`, `results/e2/e2_cells.csv` doit avoir le SHA-256 complet `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` dans son encodage original à retours chariot **CRLF**. Ne jamais convertir silencieusement ce fichier en LF, n'utiliser ni `pandas.to_csv` ni `dos2unix` sur la référence. Les autres empreintes ne se substituent pas à J1. En cas d'échec, **STOP** avant fusion et diagnostic des octets / environnement / version / BLAS ; ne pas changer la valeur attendue.
2. **Gel intégral à l'inférence séquentielle** : paramètres des encodeurs online et target EMA, état du prédicteur, tête, axes, poids de facteurs, estimateurs de référence, moyennes, écarts types, seuils, choix de canaux et hyperparamètres restent inchangés sur `monitor`. Seuls les états internes des détecteurs conçus pour accumuler de l'évidence peuvent évoluer. Une transformation instantanée pure de `x_t` (ex. dispersion quotidienne de degré zéro) reste permise, à distinguer d'une mise à jour d'estimateur entraîné.
3. **Frontières temporelles** : entraînement JEPA sur `pretrain` seulement, avec validation interne prétrain ; `calib` réservée aux ajustements de lecture et de null selon le contrat ; `monitor` jamais lu pour choisir architecture, `d`, arrêt d'entraînement, seuil, spectre ou comparateur. Tenir compte de l'embargo de 65 jours et aligner par dates/manifeste, jamais par numéros de lignes supposés. Les deux indices de calib D3 `[4090,5030)` et `[2834,3775)` du handover sont contradictoires : résoudre l'origine avant jointure, sans correction silencieuse.
4. **Validité du null** : l'exactitude univariée des signes nécessite la **symétrie centrale conditionnelle de l'ensemble de la coupe**, l'imparité du canal et une pièce indépendante aux égalités. Elle n'implique pas l'indépendance entre canaux. Elle est prouvée/validée sur D6, pas sur les rendements bruts réels asymétriques. `qhat` estimé sur `calib` n'est pas une restauration de garantie exacte. Les mélanges gaussianisés nécessitent des hypothèses conjointes propres ; ne jamais extrapoler une garantie marginale.
5. **Comparaisons loyales** : même fond d'injection, mêmes onsets et graines appariées, même horizon `H`, même type de lecture et fausses alarmes `FPR(H)` côte à côte, censure et detection rate explicites. `ARL0`, `FPR(H)` et budget d'évidence sont trois objets distincts. Ne jamais appeler `504 ln(gamma)/SR²` une borne universelle du délai CUSUM à `ARL0=gamma` fini ; le résultat exact concerne le budget d'évidence d'un e-processus lancé à l'onset, sous hypothèses d'intégrabilité.
6. **Données & publication** : D2, D3 et D4 ont un biais de survie/sélection ; D3-GICS statiques ne sont pas point-in-time, donc hors protocole principal. D4 EUROFIDAI ne doit jamais être commité, copié dans des logs ou poussé. Aucun fichier >50 Mo ; dépôts/publications liés aux clauses CIFRE nécessitent l'accord écrit requis. Respecter politique de push, anonymisation, hooks et confidentialité définies par `CLAUDE.md`.
7. **Aucune fusion spéculative** : `make check`, tests de contrat, protocole TDD RED→GREEN, hash des entrées/sorties, `make prompts-check` et GO enregistrés avant exécution. Chaque plan approuvé est conservé dans `prompts/plans/plan-NN.md` ; journaliser les corrections méthodologiques dans `docs/DEVIATIONS.md`. Ne pas exploiter un résultat rétrospectif ou exploratoire comme gain J4.

## Question scientifique principale et jalons

**J2** (E1/E3) : fermer le diagnostic du plafond de pooling et de la calibration, avec tests de FPR à horizon fixé sur D6, plateaux de P2-C, pentes de P3-C sur F2 et tableau des quatre capteurs. Les quatre critères (i)–(iv) originaux doivent rester identifiables, y compris en cas d'échec ; qualifier les échecs par information, alignement, censure ou null. E10 constate des violations de null sur fonds asymétriques, sans invalider l'exactitude D6. Ne pas convertir une garantie `ARL0>=gamma` en un objectif FPR à 5 % quand `gamma=20` et `H=750` : utiliser `gamma_H=H/alpha` si la lecture anytime-valid l'exige.

**J3** (stream 16) : comparer les sorties compactes non dégénérées après préentraînement, y compris la **tête quotidienne** réellement surveillée ; `RankMe >= 0.5 d` est une condition minimale, pas une preuve de contenu informationnel. Trois types de masques sont à traiter comme prétextes distincts ; le masque principal doit être bâti avec des caractéristiques authentiquement disponibles au jour considéré, **pas GICS actuel reconstruit rétrospectivement**.

**J4** (streams 21→22 après 16, 17 et 19, et le complément F4 de 23) : gel préalable dans `configs/FROZEN.json`, comparaison de P5 à la meilleure référence préspécifiée entre P3-CS(b) et P4, gain de délai restreint `G_ADD >= 1.25` sur au moins **deux familles parmi F1/F2/F4**, intervalle excluant 1, FPR comparables, correction de multiplicité fixée avant toute lecture de `monitor`. Le mélange et les variantes exploratoires sont des diagnostics, pas des issues additionnelles de la porte. En cas d'échec : contingence **C3 / titre B**, sans modifier a posteriori families, horizon, cible ou baseline. Pas de revendication de gains JEPA avant gel et résultats E5.

**Statut théorique** : les facteurs N1/N2/N3 sont des potentiels sous hypothèses ; `P3-CS(b)` capte déjà environ 2× par normalisation. L'optimalité `d*∈[2,8]` n'est PAS garantie par le spectre de covariance ; l'information de dérive `q_k` et le coût propre au détecteur décident. La formule de seuil affine de la Slide 4 n'est pas universelle. La Prop. 3 du papier concerne l'atteignabilité et une approximation fluide du mélange isotrope, sous null joint approprié, pas une borne minimax générale.

## Plan d'ordonnancement imposé par les dépendances, non par des dates

**Phase 0 — audit ponctuel non destructeur.** Identifier les worktrees et plans non commités. Calculer l'état HEAD et le statut des sessions. Réconcilier les directives sans écraser les plans/GO déjà validés ; réviser formellement le GO des streams concernés. Mettre `prompts/streams/INDEX.md`, les prompts individuels et le master `Prompts_Claude_Code_v5.md` en phase via `tools/check_prompts.py --sync-master`, puis `make prompts-check` selon le comportement réel du script. Conserver les preuves de modifications.

**Phase 1 — J2 et socles indépendants.** Finir 12 (en gardant son GO antérieur et sa révision finale de plan), 13 (préserver ses fichiers non commités, compléter les tests et analyses), 17 (socle C, IPCA et contrats) ; le 14 peut préparer l'environnement Torch, mais aucune modification partagée de `extract.py` tant que l'intégration du socle de 17 n'est pas maîtrisée. E6 phase 1 de 23 reste conservé, sans allégations F4 générales.

**Phase 2 — architecture et comparateurs.** Exécuter 14 selon son remplacement ci-joint : **bottleneck natif** et anti-fuite pour l'architecture principale ; ACP post-JEPA rétrogradée en ablation non prioritaire. Puis 16, pré-entraînement et checks J3 ; 18 (CD-DFM) si code et licence disponibles, sans bloquer indéfiniment J4 ; 19 (lois d'échelle) et compléments 23/P4-D. Aucun agent ne réécrit l'interface Z-1 ni l'extraction d'un autre worktree en parallèle sans série explicite d'intégration.

**Phase 3 — freeze et J4.** Achever 21, fabriquer manifeste immuable, config + checkpoint + empreintes + modèles de null ; seulement ensuite exécuter 22/E5 et 23/P5-D. 20 transmission, 26 absorption, 25/E8 et domaines externes viennent après les nécessités de la porte. Ne pas redémarrer 27 (déjà fusionné) pour produire un résultat JEPA rétroactivement.

## Protocole d'orchestration headless et délégation (Claude Code & Vibe)

Tu agis en tant que superviseur architectural exclusif : **tu ne modifies aucun code applicatif directement**. Tu orchestres des sous-agents exécutés dans des Git worktrees isolés (`~/JEPA-Drift-stream-NN`), tu audites leurs plans et tu arbitres les intégrations.

### 1. Dimensionnement des sous-agents et serveurs MCP
Chaque invocation headless (`claude -p`) doit fixer le modèle et l'effort :
- **Streams critiques / complexes** (mathématiques, CUSUM, CA-T-JEPA, IPCA, vectorisation) :
  `--model claude-opus-5-5 --effort max` (alias `--model opus --effort max`).
- **Streams secondaires** (hygiène, schémas de données, documentation, typage de surface) :
  `--model opus --effort xhigh` (ou `--model sonnet --effort xhigh`).
- **Délégations Mistral Vibe** : `mistral-large-4`, mode `/thinking high`.
- **Configuration MCP :** Les serveurs d'outils (`graphify`, `jcodemunch`) sont déclarés dans `.mcp.json` à la racine. N'utilise jamais de commande interactive `/mcp` : Claude Code initialise automatiquement les connexions MCP à chaque démarrage headless.

### 2. Protocole bi-phase : planification confinée puis exécution asynchrone

#### Phase A : Génération et capture du plan (Lecture seule)
Invoque l'agent en mode non destructif confiné et redirige la sortie vers `PLAN.md` :
```bash
cd "$WORKTREE_PATH"
claude -p "MODE PLAN : Analyse le codebase, formalise la logique algorithmique, détaille les étapes d'implémentation et les tests associés sans modifier aucun fichier." \
  --model opus --effort max \
  --permission-mode plan > PLAN.md 2> plan_error.log
```
Inspecte `PLAN.md`. Vérifie la rigueur mathématique, l'absence de fuite temporelle, la compatibilité de l'environnement (`.venv`) et la stricte conformité aux contrats. En cas de non-conformité, réitère la Phase A en injectant tes objections dans le prompt.

#### Phase B : Arbitrage GO et lancement détaché
Dès validation formelle du plan (GO), génère le script d'exécution autonome `run_stream.sh` dans le worktree et lance-le en arrière-plan détaché. La permission d'écriture (`--dangerously-skip-permissions`) est **exclusivement autorisée dans ce script détaché non interactif** afin d'éviter tout blocage de terminal :
```bash
cd "$WORKTREE_PATH"
cat << 'EOF' > run_stream.sh
#!/usr/bin/env bash
set -o pipefail
STREAM_NAME=$(basename "$PWD")

claude -c -p "Plan validé. Exécute l'implémentation complète conformément à PLAN.md et valide par les tests." \
  --model opus --effort max \
  --dangerously-skip-permissions > execution.log 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  touch .status_done
else
  echo "FAILED: $EXIT_CODE" >> execution.log
  touch .status_error
fi

if command -v codex >/dev/null 2>&1 && [ -n "${CODEX_THREAD_ID:-}" ]; then
  codex queue --thread "$CODEX_THREAD_ID" --message "Stream $STREAM_NAME terminé (Code: $EXIT_CODE). Prêt pour audit." >/dev/null 2>&1 || true
fi
EOF
chmod +x run_stream.sh
nohup ./run_stream.sh >/dev/null 2>&1 &
echo $! > .claude.pid
```
*Le lancement s'exécute en < 0,2 s et te libère immédiatement pour superviser d'autres flux en parallèle.*

### 3. Frugalité des tokens et surveillance non bloquante
**Il est formellement interdit de consommer des tokens d'inférence en attente active ou de bloquer le shell par des boucles `sleep`.** L'état des flux s'inspecte par un instantané non bloquant :
```bash
echo "=== ÉTAT DES STREAMS ==="
for wt in worktrees/stream-* ~/JEPA-Drift-stream-*; do
  [ ! -d "$wt" ] && continue
  name=$(basename "$wt")
  if [ -f "$wt/.status_done" ]; then
    echo "[$name] STATUT: DONE"
  elif [ -f "$wt/.status_error" ]; then
    echo "[$name] STATUT: ERROR (Voir $wt/execution.log)"
  elif [ -s "$wt/.claude.pid" ] && kill -0 "$(cat "$wt/.claude.pid")" 2>/dev/null; then
    echo "[$name] STATUT: RUNNING (PID $(cat "$wt/.claude.pid"))"
  else
    echo "[$name] STATUT: INACTIF / ARRÊTÉ"
  fi
done
```
- Si tous les flux actifs sont `RUNNING`, rends la main sans relancer de commande d'attente.
- Si un flux affiche `DONE`, procède à l'audit des commits et des résultats en vue de la clôture.
- Si un flux affiche `ERROR`, lis uniquement les 40 dernières lignes d'`execution.log` pour formuler le diagnostic de reprise.

### 4. Clôture, non-régression et intégration
Chaque stream remet : plan/GO, changements de code + tests unitaires, journal de commandes, empreintes SHA-256 des fichiers produits, diagnostics `FPR(H)`, censure/taux de détection et wrapup en anglais.
Avant d'autoriser la fusion sur `main` :
1. Confirme l'extinction du processus : `kill -0 "$(cat .claude.pid)" 2>/dev/null` doit échouer.
2. Vérifie l'absence de verrou Git résiduel :
   ```bash
   GIT_DIR=$(git rev-parse --git-dir)
   test ! -f "$GIT_DIR/index.lock"
   ```
3. Exécute la suite complète de non-régression (`make check`, `make prompts-check` si un prompt est modifié).
4. Supprime les sentinelles (`.status_*`, `.claude.pid`, `run_stream.sh`) avant de libérer le worktree.
5. Intègre sur la base locale correcte : fetch/rebase uniquement, sans écraser les worktrees voisins, sans présumer qu'`origin/main` est plus récent que `main` local.

**Premier compte rendu attendu de Codex, avant toute mutation :** état vérifié de `main` et des worktrees, liste des divergences avec section 3.6 du handover, liste de GO/plan nécessitant révision, disponibilité quota communiquée ou non, statut J1/Torch, et ordre exécutable des dépendances. Si le quota est toujours suspendu, livrer seulement la préparation et les diagnostics non intrusifs.
