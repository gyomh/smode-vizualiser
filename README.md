# Smode Vizualiser

*[Version française](README.fr.md)*

> **Experimental, not an official Smode tool.** Built by trial and error against the Oil API (see [smode-oil-reference](https://github.com/gyomh/smode-oil-reference)). Tested on Smode Compose R15.

A Script that **builds an audio-reactive visualiser** in your Smode scene:

- DirectSound input (left channel), **2 modes**: bars or peaks;
- rainbow gradient used as a mask, black bands (opacity depends on the mode);
- Pixelate + Feedback on the spectrum;
- exposed parameters: **Freq Max**, **Amplitude Min / Max**, **N Bands**, Compo Width / Height.

## Install

1. Drag `vizualiser.py` into your Smode project, **Launch Mode = Manual**.
2. Tick or untick **Use Peaks Instead Of Bars**, adjust *N Bands* and the Compo size if needed.
3. Execute. Running it again replaces the previous visualiser.

## License

MIT — see [LICENSE](LICENSE).
