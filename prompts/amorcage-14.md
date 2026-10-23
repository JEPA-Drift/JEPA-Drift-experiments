# Amorçage — stream 14, CA-T-JEPA

Vérifie d'abord que le stream 8b est fusionné sur `main`. Lis `CLAUDE.md`,
`prompts/streams/INDEX.md` et `prompts/streams/prompt-14-ca-tjepa.md` dans le worktree
`stream-14`. Reste en mode `plan`. `.venv` est un venv Python, pas un préfixe Conda :
le GO autorise l'installation immédiate du verrou conda-forge `cpu_generic` à 65 paquets
dans `.venv/torch-cf`. Développe via `PYTHONPATH` en ajoutant le site-packages torch en fin
de `sys.path`, sans `.pth` dans la `.venv` parente. Ne pose ce `.pth` qu'après `make check`
complet et la régénération J1 avec signature CRLF native et SHA-256 complet vérifiés ;
répète ensuite les contrôles sans shim. Le stream 17 pose le socle C partagé avant ton ajout
de `ca_tjepa`, `--ckpt` et `--D` aux fichiers communs, sans casser D2/PCA.
Le protocole principal n'emploie que les quatre caractéristiques continues causales. Prévois
des générateurs torch locaux, des gardes sur le vrai modèle et le hash J1. Présente les fichiers
touchés et les questions ; intègre les arbitrages Q0/Q1/Q2/Q3/Q5/Q7 déjà accordés dans
`prompts/plans/plan-14.md` avec « Décision GO intégrée », puis implémente après reconnexion
explicite des MCP `graphify` et `jcodemunch`.
Rédige les nouveaux audits en anglais et arrête-toi au commit local vérifié avant fetch, fusion ou push.
