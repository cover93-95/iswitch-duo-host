# Shell iOS

Construit un shell iOS à partir de NX2Apple, à un commit figé, sans aucune donnée de jeu.

Ce dépôt ne contient qu'un workflow. Il ne contient et ne doit jamais contenir :
- de fichier de jeu ou de donnée qui en est extraite ;
- de clé, de certificat ou de profil de signature ;
- de framework de jeu ou d'IPA.

Branche `hostm3-shell` : chaque push sur cette branche construit le shell Host M3 (jeux Switch 1), ou à la main depuis l'onglet Actions. Le premier job vérifie Xcode, le second construit le shell.

Le code construit provient de NX2Apple et de nxnative, sous licence MIT (Copyright (c) 2026 seedds, Copyright (c) 2026 jhaizhou). Il n'est pas copié dans ce dépôt : le workflow le télécharge à un commit figé. Les composants tiers gardent leurs licences, listées dans `dm/third_party/README.md` du moteur. L'IPA utilise la police Manrope (SIL Open Font License) à la place des polices Apple.

Le workflow nomme un identifiant de titre public, celui du test amont : il sélectionne un profil texte du moteur. Aucun fichier de ce jeu n'est utilisé.
