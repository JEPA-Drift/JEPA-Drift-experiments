# GO-J1 — Stream 14, suivi Git du CSV J1 en CRLF natif (2026-10-29)

Autorisation du chercheur pour le stream 14 existant uniquement, après le commit C4 `7204730`.

## Constat
Avant toute fusion, `results/e2/e2_cells.csv` DOIT être suivi par Git en CRLF natif, avec le SHA-256 exact
`e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823`. Le fichier du stream 14 et le blob de HEAD sont
actuellement en LF (SHA-256 `206dbe3b…`) ; dans le checkout principal, le fichier de travail est en CRLF mais le blob est
en LF, parce que `core.autocrlf=input`.

## Interdits
Ne modifier ni le code du modèle, ni les paramètres scientifiques, ni les seuils, ni les autres streams, ni `main`, ni
les fichiers GO historiques. Ni fetch, ni push, ni fusion.

## Autorisé et exigé
1. Reconnecter les serveurs MCP graphify et jcodemunch par des appels sûrs avant toute modification ; ni extraction LLM
   Graphify, ni résumés IA jCodeMunch.
2. Consigner cette autorisation dans ce nouveau fichier en français et intégrer la décision dans
   `prompts/plans/plan-14.md` avant l'exécution.
3. Ajouter uniquement, dans un `.gitattributes` à la racine, la règle de chemin exact `results/e2/e2_cells.csv -text`.
   Éditions manuelles par les outils natifs `Edit`/`Write`.
4. Régénérer J1 par la cible déterministe existante `make j1` sous la `.venv` du projet ; inspecter tous les fichiers
   modifiés et s'arrêter si une sortie inattendue ne peut pas être expliquée.
5. Vérifier les octets du CSV avec les assertions Python exactes du chercheur : SHA-256 ci-dessus, présence de CRLF,
   aucun LF isolé.
6. Indexer des chemins explicites ; vérifier que `git ls-files --eol` indique `i/crlf w/crlf attr/-text` et que le blob
   indexé (`git show :results/e2/e2_cells.csv | sha256sum`) vaut `e315e537…`. Si Git normalise le fichier, s'arrêter et
   diagnostiquer au lieu de commiter.
7. Mettre à jour `prompts/wrapups/wrapup-14.md` (en anglais) avec l'état corrigé du blob suivi et le nouveau hash, en
   précisant que C4 avait consigné l'état LF.
8. Exécuter `make prompts-check`, `git diff --check` et `make check` sous `.venv` avec le shim torch ; vérifier
   indépendamment que les quatre gardes torch des contrats s'exécutent sans être ignorées.
9. Un seul commit local Conventional Commit, sans trailer, sans contournement de hook, avec indexation explicite.
10. Rendre le hash du commit, les SHA-256 du fichier et du blob indexé, les comptes de tests et un statut propre. En cas
    d'échec d'une vérification : arrêt avec preuves, modifications laissées en place.
