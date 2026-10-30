# Smode Vizualiser

*[English version](README.md)*

> **Expérimental, pas un outil officiel Smode.** Construit par essais et erreurs sur l'API Oil (voir [smode-oil-reference](https://github.com/gyomh/smode-oil-reference)). Testé sur Smode Compose R15.

Un Script qui **construit un visualiseur audio-réactif** dans votre scène Smode :

- entrée DirectSound (canal gauche), **2 modes** : barres ou pics ;
- dégradé arc-en-ciel utilisé comme masque, bandes noires (opacité selon le mode) ;
- Pixelate + Feedback sur le spectre ;
- paramètres exposés : **Freq Max** (Hz), **Amplitude Min / Max** (dB), **N Bands**, Compo Width / Height.

## Installation

1. Glissez `vizualiser.py` dans votre projet Smode, **Launch Mode = Manual**.
2. Cochez ou décochez **Use Peaks Instead Of Bars**, ajustez *N Bands* et la taille de la Compo si besoin.
3. Exécutez. Une nouvelle exécution remplace le visualiseur précédent.

## Licence

MIT — voir [LICENSE](LICENSE).
