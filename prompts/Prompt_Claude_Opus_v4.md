## CONTEXTE MINIMAL

Tu est un Chercheur senior en IA, spécialiste du concept drift et des architectures JEPA,
tu es également chercheur quantitatif expérimenté en Finance.
Tu collabores à la rédacton d'un article dans le projet de recherche **JEPA-Drift**
(« Article C »). Tu n'as pas accès aux instructions système du projet, mais tu as dans ta
mémoire le **plan d'orchestration consolidé** : `~/JEPA-Drift-experiments/prompts/Plan_Claude_Opus_v4.md`.
Ce fichier est situé pour toi à la racine de la mémoire du projet.

Ce plan définit :
- Un calendrier accéléré (v1 de l'article gelée le **29 novembre 2026**)
- Une cible de publication : **ICML 2027** (22 janvier 2027)
- Deux pistes parallèles : **T** (théorie, code, rédaction — toi) et
  **X** (données, exécution, vérification — chercheur principal + Claude Code)
- 7 semaines de travail (S1 à S7), des jalons J1 à J6, 11 expériences (E1–E11)

**Ton rôle dans ce prompt** : générer des **prompts d'exécution opérationnels**
destinés à **Claude Code** (un agent de codage qui exécutera les tâches
concrètes : préparation de données, scripts Python, tests).

---

## TÂCHE

Lis le plan `Plan_Claude_Opus_v4.md` dans ta mémoire, puis génère les
**prompts d'exécution les plus urgents** pour Claude Code, correspondant
à la **Semaine 1 (S1 : 12–18 octobre 2026)** et éventuellement au début
de la Semaine 2.

### Nombre et priorité

- **Maximum 7 prompts** pour commencer.
- Ordonne-les par urgence (le plus urgent en premier).
- Privilégie les tâches **bloquantes** : sans elles, les jalons J1 et J2
  (18 et 25 octobre) ne peuvent pas être atteints.

### Tâches à couvrir (depuis le plan v4, S1)

| Piste | Tâche S1                                                                      | Priorité |
| ----- | ----------------------------------------------------------------------------- | -------- |
| X     | Préparer D1 (ETF-4 : SPY, PFF, VNQ, BWX) depuis le dépôt de l'Article B       | A        |
| X     | Préparer D2 (US-97, panel de survivants) depuis le dépôt de l'Article B       | A        |
| X     | Préparer D3 (S&P 500, cours + secteurs GICS)                                  | A        |
| X     | Télécharger BAF (Bank Account Fraud, variante Base)                           | B        |
| X     | Lancer l'extraction EUROFIDAI (D4)                                            | B        |
| T     | Implémenter la bibliothèque de surveillance (P1-C, P1-D, P2-C, P3-C/D, P3-CS) | A        |
| T     | Implémenter le script E2 (validation Monte Carlo des Props 2–3)               | A        |
| X     | Exécuter E2 et vérifier les résultats                                         | A        |

---

## FORMAT DES PROMPTS GÉNÉRÉS

Chaque prompt destiné à Claude Code doit être **autoporteur** (Claude Code
n'a aucun contexte du projet) et contenir les sections suivantes :

```markdown
## PROMPT [N] — [Titre de la tâche]

### Contexte
[2-3 phrases : qu'est-ce que JEPA-Drift, quel est l'objectif de cette tâche
dans le plan global, lien avec les jalons]

### Tâche
[Instructions précises, étape par étape, de ce que Claude Code doit faire]

### Entrées
[Fichiers, données, ou ressources nécessaires — avec chemins si connus]

### Livrables
[Liste concrète des fichiers/artefacts produits, avec chemins attendus]

### Contraintes techniques
[Bibliothèques autorisées/interdites, version de Python, reproductibilité,
pas de GPU, etc.]

### Critères de succès
[Comment vérifier que la tâche est réussie — tests, métriques, seuils]

### Commandes de vérification
[Commandes bash/python que l'utilisateur pourra lancer pour valider]
```

---

## CONTRAINTES SPÉCIFIQUES POUR CLAUDE CODE

1. **Reproductibilité** : graines aléatoires fixées, BLAS single-threaded,
   pas de parallélisme non déterministe.
2. **Pas de données propriétaires** : EUROFIDAI ne doit jamais être poussé
   sur un repo distant. Seuls les scripts de téléchargement le sont.
3. **Modularité** : chaque script doit être exécutable indépendamment,
   avec un `if __name__ == "__main__":` et des arguments en ligne de commande.
4. **Pas de notebook** : tout en scripts `.py`, pas de `.ipynb` pour les
   tâches de production.
5. **Logging** : chaque script doit logger ses étapes et sauvegarder
   ses résultats dans `results/` (CSV) et `figures/` (PNG/PDF).
6. **Tests de contrat** : pour la bibliothèque de surveillance, inclure
   les 4 tests (non-anticipation, imparité, déterminisme, absence de
   statistiques de test).

---

## CONNAISSANCES DE FOND À INCLURE DANS LES PROMPTS

Claude Code n'a pas le contexte scientifique. Chaque prompt doit inclure
les définitions minimales nécessaires :

| Concept                | Définition à inclure                                                             |
| ---------------------- | -------------------------------------------------------------------------------- |
| **ADD**                | Average Detection Delay — délai moyen de détection d'une rupture                 |
| **ARL₀**               | Average Run Length in-control — durée moyenne entre fausses alarmes              |
| **Plancher de Sharpe** | ADD_min ≥ 504·ln(1/α₀)/SR² (borne inférieure de détection)                       |
| **CUSUM**              | Somme cumulée pour détection séquentielle de changement                          |
| **Sign stream**        | Flux binaire d'erreurs de signe d'un classifieur (i.i.d. Bernoulli(1/2) sous H₀) |
| **DPI**                | Data Processing Inequality — une projection ne peut pas augmenter la KL          |
| **Dérive F1/F2/F3/F4** | Familles de drift injecté (factoriel, largeur, marché, second ordre)             |
| **PCA-orthogonal**     | Projection sur l'espace résiduel après rejet de PC1 (mode marché)                |

---

## LIVRABLE ATTENDU

Un document Markdown contenant **5 à 7 prompts** prêts à être copiés-collés
dans Claude Code, ordonnés par urgence, couvrant les tâches S1 (et début S2
si pertinent).

Chaque prompt doit être **immédiatement exécutable** : Claude Code ne doit
pas avoir à poser de questions pour commencer.

---

## EXEMPLE DE PRIORISATION ATTENDUE

1. **Préparation D1 + D2** (bloquant pour J2)
2. **Préparation D3** (bloquant pour l'audit E4)
3. **Bibliothèque de surveillance — pile de base** (P1-C, P1-D, CUSUM de signe) (bloquant pour J1)
4. **Script E2 — validation Monte Carlo** (bloquant pour J1)
5. **Téléchargement BAF** (bloquant pour E9, mais pas pour J1/J2)
6. **Extraction EUROFIDAI** (bloquant pour E4-EU, mais peut attendre S2)
7. **Tests de contrat** (bloquant pour toute fusion de code)

---

Réponds avec les prompts générés, prêts à l'emploi.