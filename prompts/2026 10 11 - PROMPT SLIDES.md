RÔLE
Tu es ingénieur Python. Tu mets à jour un script python-pptx existant. La mise en forme est figée : tu ne modifies que les textes et les appels de figures.

ENTRÉES
1. `Generation_slides_Point_Hebdo_template.py` : script modèle de 11 diapositives codées en dur ; palette, géométrie et fonctions utilitaires sont fixées.
2. `DECK_POINT_HEBDO_JEPA_DRIFT_v1.md` : le deck de 12 diapositives, collé à la suite de ce message. Chaque diapositive commence par « ### SLIDE n — TYPE — Titre ».
3. Le dossier `figures/`, qui contient `Fig30_RealCrossSectional_Escape_UPDATED.png`.

SORTIE
Un script complet `Generation_slides_Point_Hebdo_JEPA_Drift.py`, copie modifiée du modèle, qui écrit `/home/m53/2026_10_12_Point_Hebdo_JEPA_Drift.pptx` et affiche le nombre de diapositives (12 attendues).

AUTORISÉ
- Les chaînes de caractères : titres, puces, cellules, bandeaux, badges, pieds de page.
- Les listes de données qui portent ces textes (`sections`, `calibs`, `points`, `headers`, `data_rows`, `cols`) et leur nombre de lignes.
- La duplication d'un bloc existant pour construire une diapositive, l'ordre des blocs, la docstring, `TOTAL_SLIDES = 12`, le chemin de sortie.
- Un appel à `footer_refs` sur toute diapositive dont le deck donne un « Pied ».
- Les figures : ajoute `import os` et une seule constante `FIG_DIR = "figures"` sous la géométrie. Chaque figure est un appel `s.shapes.add_picture(os.path.join(FIG_DIR, "<fichier>"), Inches(x), Inches(y), width=Inches(w))`.

INTERDIT
- Modifier la palette, `SLIDE_W`, `SLIDE_H`, les fonctions utilitaires (`add_rect`, `add_text`, `add_multi_text`, `add_paragraphs`, `header_bar`, `page_num_only`, `badge`, `vertical_bar`, `lettered_circle`, `footer_refs`), les polices, tailles, couleurs, positions et dimensions des blocs, hors des deux exceptions ci-dessous.
- Ajouter une fonction, une bibliothèque autre que `os`, des notes d'orateur, des animations ou des formes dessinées.
- Reformuler, raccourcir ou traduire un texte du deck : recopie-le tel quel, accents et typographie compris.
- Insérer du code LibreOffice Math : dans les encadrés de formule, écris uniquement la ligne « Texte simplifié » du deck.
- Recopier les champs « Notes » et les sections [EQUATIONS] dans les diapositives.

CORRESPONDANCE DECK → BLOCS DU MODÈLE
SLIDE 1 (TITLE) → bloc « SLIDE 1 — TITRE » : lignes 1 à 3 et ligne italique dans `add_paragraphs`, bandeau orange, ligne sous bandeau.
SLIDE 2 → bloc « SLIDE 6 » : en-tête gauche BG_PINK/RED, en-tête droit BG_GREEN_LT/GREEN, paragraphes des deux colonnes, encadré BG_BLUE_LT. Le titre de l'encadré est le titre « Encadré » du deck ; son contenu est la ligne « Texte simplifié » puis la ligne d'explication.
SLIDE 3 → bloc « SLIDE 6 ». La colonne droite garde son en-tête vert ; ses paragraphes sont remplacés par la figure `Fig30_RealCrossSectional_Escape_UPDATED.png` à x = 5.25, y = 1.15, largeur 4.45.
SLIDE 4 → bloc « SLIDE 6 ».
SLIDE 5 → bloc « SLIDE 4 » : deux colonnes, bandeau BG_BLUE_LT, liste `calibs` à 3 lignes (libellé, sous-titre entre parenthèses, description), encadré crème.
SLIDE 6 → bloc « SLIDE 10 » : 5 colonnes aux positions du modèle, 6 lignes, bloc de lecture BG_CREAM ; la dernière puce du bloc est en gras GREEN.
SLIDE 7 → boucle `calibs` du bloc « SLIDE 4 », 7 lignes. EXCEPTION 1 : y = 0.80 + i * 0.58 ; encadré crème final à y = 4.85, hauteur 0.32.
SLIDE 8 → bloc « SLIDE 10 », 5 lignes.
SLIDE 9 → bloc « SLIDE 10 », 6 lignes.
SLIDE 10 → bloc « SLIDE 7 » : bandeau, 4 points (couleur, titre, description).
SLIDE 11 (DIVIDER) → bloc « SLIDE 9 — DIVIDER C » : carré RED contenant « ? », deux lignes de titre, sous-titre.
SLIDE 12 (ANNEX) → bloc « SLIDE 8 » : bandeau, 4 étapes numérotées (ligne en gras puis ligne « Texte simplifié » en italique), bloc BG_PINK dont la première ligne est « Portée : » en gras RED.
Blocs du modèle à supprimer : SLIDE 2 (PLAN), SLIDE 3 et SLIDE 5 (DIVIDER A et B), SLIDE 11 (trois colonnes).
EXCEPTION 2 : dans les tableaux, le fond et la couleur de texte de chaque ligne suivent la colonne « Couleur » du deck, avec les constantes existantes de la palette ; la colonne « Couleur » elle-même n'est pas affichée.

DÉTAILS
- Les en-têtes de colonnes et de bandeaux commencent par deux espaces, comme dans le modèle.
- Une puce « • » du deck = un paragraphe `[("• …", 9, False, TXT_BODY)]`.
- Badges : texte, couleur et largeur `w` indiqués dans le deck.
- Un [VISUAL] sans fichier n'ajoute rien à la diapositive : laisse le commentaire `# VISUEL À DESSINER À LA MAIN : <description du deck>`.
- Les numéros de page restent automatiques.

CONTRÔLES AVANT DE RENDRE
1. Le script s'exécute sans erreur avec python-pptx et produit 12 diapositives.
2. Chaque texte affichable du deck apparaît exactement une fois.
3. Aucune constante de mise en forme n'a changé hors des deux exceptions.
4. Signale sans les corriger les textes qui semblent déborder de leur zone : cellule sur plus de deux lignes, colonne de plus de dix lignes, pied de page de plus de 140 caractères.

FORMAT DE RÉPONSE
Le script complet dans un seul bloc de code Python, puis la liste des signalements du contrôle 4.

EXÉCUTION
Dépendance : pip install python-pptx
Commande, depuis le dossier qui contient figures/ : python Generation_slides_Point_Hebdo_JEPA_Drift.py