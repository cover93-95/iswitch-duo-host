# NX2Apple Host M3 — shell iOS v1.1

Ce dépôt construit manuellement le shell partagé officiel de **NX2Apple v1.1.0**, vide de tout jeu, pour la mise à jour de l’installation Host M3.

Le workflow est verrouillé sur une révision précise de NX2Apple et produit une IPA non signée avec :

- le Bundle ID source `local.iswitchduo.hostm3` ;
- l’entitlement `com.apple.developer.kernel.increased-memory-limit` ;
- aucun framework `DmGame`, RomFS, shader, clé, certificat ou donnée Nintendo ;
- une police libre Manrope incluse par NX2Apple.

Le framework synthétique créé pendant le build sert uniquement à satisfaire le constructeur officiel et est retiré avant l’archivage. La signature et l’installation restent des opérations locales et manuelles. Les anciens fichiers `shell.patch` et `shell_build.py` sont conservés pour l’historique, mais le workflow v1.1 ne les utilise plus.

## Lancer le build

Dans **Actions → Build iOS shell → Run workflow**, sélectionner la branche `codex/nx2apple-v1.1-shell`, cocher `Construire le shell`, puis télécharger l’artefact `DmShell`.

**Ne jamais ajouter à ce dépôt un fichier de jeu, une clé, un shader, une RomFS, un framework de jeu, un certificat ou un secret.**
