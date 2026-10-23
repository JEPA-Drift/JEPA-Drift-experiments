# Transfert du stream 14 vers le stream 17 — extraction partagée

Source : `~/.claude/plans/amor-age-stream-refactored-giraffe.md`, §2.7–2.8 et §3.
Lire ces sections avant de quitter le mode plan. Ce transfert ne constitue pas un GO autonome.

## §3 du plan 14

Fichiers partagés : `extract.py`, `test_contracts.py`, `test_representations.py`, `interface_Z.md`. Le §3
propose l'échafaudage de §2.7–2.8 (`NEEDS_C`, `C=None` dans `extract`, `--ckpt`/`--D`,
`CHAR_CASES`, méta-test, boucles D2) ; l'arbitrage Q7 ci-dessous répartit sa réalisation entre
les deux streams. 17 ajoute `"ipca"` à `REGISTRY`, `NEEDS_C` et `CHAR_CASES`, ainsi que son
propre crochet d'étape pretrain (Γ appris sur `pretrain`), dont 14 n'a pas besoin. La fixture D3 expose aussi des
lignes pretrain. L'ordre de réalisation est arbitré ci-dessous. Toute entrée P4 de 18 dépend de
son propre garde de faisabilité et de l'intégration de 17.

## Contrat partagé à reprendre du §2.7–2.8

- `NEEDS_C` identifie les représentations à caractéristiques ; `extract(..., C=None)` aligne C sur les lignes de
  calib et de monitor. D2/PCA continue sans C et refuse explicitement une représentation qui en a besoin.
- La CLI accepte `--ckpt` et `--D` seulement quand la fabrique concernée les accepte. Le sidecar conserve les
  lignes `C-repr-rows` et ajoute `c_sha256`.
- Les contrats D2 existants restent sur `REGISTRY − NEEDS_C`. `CHAR_CASES` fournit une fixture D3 causale et un
  constructeur par représentation avec caractéristiques ; le méta-test impose
  `NEEDS_C == set(CHAR_CASES) ⊆ REGISTRY`.
- Les tests D3 couvrent non-anticipation, déterminisme entre sous-processus, segment déclaré et absence de
  statistiques de test. Aucun `import torch` n'est ajouté à `jepadrift.representations` au chargement.

## Arbitrage Q7 de l'orchestrateur

Le stream 17 pose en premier l'échafaudage générique dans `extract.py`, `test_contracts.py` et
`test_representations.py` : alignement C, masque et segment `pretrain`, `NEEDS_C` et `CHAR_CASES`
initialisés avec `ipca`, puis ajoute IPCA. Le méta-test compare ces deux registres à chaque étape.
Le stream 14 développe en parallèle le modèle, le pré-entraînement et le staging torch ; avant d'ajouter
`ca_tjepa`, `--ckpt` et `--D` aux fichiers partagés, il intègre le commit de 17 et étend cet échafaudage,
sans en créer une seconde version divergente. Le stream 18 attend le staging torch ; toute entrée P4
reste soumise à la tâche 5 de son propre prompt et à l'intégration de 17.
