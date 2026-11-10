# NX2Apple — shell iOS Ocarina 30 FPS

La branche `codex/ocarina-30fps-cool-shell` construit le shell Ocarina vide de tout jeu à partir du moteur corrigé `af062602`. Elle conserve la chaîne de shaders `b70f92017083`, le Bundle ID `local.iswitchduo.botw` et produit la version `1.4.27`.

Le workflow est verrouillé sur une révision précise de NX2Apple et produit une IPA non signée avec :

- le Bundle ID source `local.iswitchduo.botw` ;
- l’entitlement `com.apple.developer.kernel.increased-memory-limit` ;
- aucun framework `DmGame`, RomFS, shader, clé, certificat ou donnée Nintendo ;
- une police libre Manrope incluse par NX2Apple.

Le framework synthétique créé pendant le build sert uniquement à satisfaire le constructeur officiel et est retiré avant l’archivage. La signature et l’installation restent des opérations locales et manuelles. Les anciens fichiers `shell.patch` et `shell_build.py` sont conservés pour l’historique, mais le workflow v1.1 ne les utilise plus.

## Lancer le build

Dans **Actions → Build iOS shell → Run workflow**, sélectionner la branche `codex/nx2apple-v1.1-shell`, cocher `Construire le shell`, puis télécharger l’artefact `DmShell`.

**Ne jamais ajouter à ce dépôt un fichier de jeu, une clé, un shader, une RomFS, un framework de jeu, un certificat ou un secret.**
