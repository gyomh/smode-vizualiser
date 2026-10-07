#    #########      ###         ###      #########      #########         ###############
# ###               ######   ######   ###         ###   ###      ###      ###
# ###               ###   ###   ###   ###         ###   ###         ###   ###
#    #########      ###   ###   ###   ###         ###   ###         ###   ############
#             ###   ###         ###   ###         ###   ###         ###   ###
#             ###   ###         ###   ###         ###   ###      ###      ###
# ############      ###         ###      #########      #########         ###############
#
# -------------------- "Guillaume Henrion aka [GYOMH]" "09/07/2026" --------------------
# __________________________________________ ___________________________________________
# |                                       | |                                         |
# |    VIZUALISER                         | | Visualisation audio-reactive :          |
# |       V1.3                            | | - Entree DirectSound (canal Left)       |
# |                                       | | - 2 modes : bars / peaks                |
# |_______________________________________| |_________________________________________|
# |    Instructions :                     | | - Degrade arc-en-ciel en masque         |
# | 1- Use Peaks Instead Of Bars          | | - Bandes noires (opacity reglable       |
# |    (coche = peaks, decoche = bars)    | |   selon le mode)                        |
# | 2- Ajuster Freq Max / Amplitude       | | - Pixelate + Feedback (spectrum)        |
# |    Min-Max / N Bands si besoin        | | - Parametres exposes : Freq Max,        |
# | 3- Execute (Launch Mode = Manual)     | |   Amplitude Min/Max, N Bands            |
# |_______________________________________| |_________________________________________|
#
# HISTORIQUE
# V1.0 - 07/07/2026 - Version initiale : modes bars/peaks (CustomEnumeration),
#                      gradient arc-en-ciel, bandes noires, Pixelate+Feedback.
# V1.1 - 09/07/2026 - Selecteur de mode remplace par une checkbox
#                      (Use Peaks Instead Of Bars) ; label/stroke/opacity des
#                      bandes desormais distincts par mode ; en-tete restructure.
# V1.2 - 09/07/2026 - Resolution de la compo (largeur/hauteur) exposee en
#                      parametre (Compo Width / Compo Height) au lieu d'etre
#                      fixee en dur a 1920x1080. Applique aussi sur
#                      rasterizer.resolution de vizCompo/maskCompo/masterCompo
#                      (sinon la compo restait a la taille de la compo parente).
# V1.3 - 09/07/2026 - Fix : rasterizer.resolution demarre en mode "Inherited"
#                      (ignore width/height) -> preset bascule sur "Custom..."
#                      avant de fixer les valeurs. Taille X/Y du Linear Gradient
#                      alignee sur Compo Width/Height (au lieu de 1056.13 fixe).
#

# =============== OPTIONS (visibles/modifiables dans le panneau du Script) ===============
usePeaksInsteadOfBars: Oil.Boolean(False)       # coche = mode "peaks", decoche = mode "bars"
nBands: Oil.PositiveInteger(64)                 # nombre de bandes/points de frequence
freqMaxDefault: Oil.Percentage(0.3)             # valeur initiale du parametre expose "Freq Max"
amplitudeMinDefault: Oil.Percentage(0.0)        # valeur initiale du parametre expose "Amplitude Min"
amplitudeMaxDefault: Oil.Percentage(0.277)      # valeur initiale du parametre expose "Amplitude Max"
compoWidth: Oil.PositiveInteger(1920)           # largeur de la compo (resolution projet)
compoHeight: Oil.PositiveInteger(1080)          # hauteur de la compo (resolution projet)
# ==========================================================================================

MODE = "peaks" if script.usePeaksInsteadOfBars.get() else "bars"
N_BANDS = script.nBands.get()
FREQ_MAX_DEFAULT = script.freqMaxDefault.get()
AMPLITUDE_MIN_DEFAULT = script.amplitudeMinDefault.get()
AMPLITUDE_MAX_DEFAULT = script.amplitudeMaxDefault.get()
COMPO_WIDTH = script.compoWidth.get()
COMPO_HEIGHT = script.compoHeight.get()
RESOLUTION_PRESET_CUSTOM = 40  # InheritableImageResolution.preset : "Custom..." (trouve par
                                # diagnostic ; 41 = "Inherited", qui ignore width/height tant
                                # qu'il reste actif -> il faut basculer sur Custom avant de
                                # fixer width/height, sinon la compo garde la taille du parent.

if MODE == "peaks":
    STROKE_THICKNESS_DEFAULT = 2.0
    VIZ_LABEL = "Vizualiser Peek"
    BANDS_OPACITY = 1.0
else:
    STROKE_THICKNESS_DEFAULT = 10.0
    VIZ_LABEL = "Vizualiser Bars"
    BANDS_OPACITY = 0.5

# --- Supprime l'ancienne version (label depend du mode -> les deux labels possibles) ---
POSSIBLE_LABELS = {"Vizualiser Bars", "Vizualiser Peek"}
oldLayer = None
for l in script.parentElement.layers:
    if l.getFriendlyName() in POSSIBLE_LABELS:
        oldLayer = l
        break
if oldLayer is not None:
    script.parentElement.layers.remove(oldLayer)

vizCompo = Oil.createObject("Compo")
vizCompo.rasterizer.resolution.preset.set(RESOLUTION_PRESET_CUSTOM)
vizCompo.rasterizer.resolution.width.set(COMPO_WIDTH)
vizCompo.rasterizer.resolution.height.set(COMPO_HEIGHT)

# --- Shape : construction des points selon le mode ---
shapeLayer = Oil.createObject("ShapeLayer")
shapeLayer.label = "Waveform"
pathGen = Oil.createObject("PathShapeGenerator")

oscillatingPoints = []  # (Path2dControlPoint, index_bande)

if MODE == "peaks":
    TOTAL_POINTS = N_BANDS * 2 - 1
    for j in range(TOTAL_POINTS):
        t = j / (TOTAL_POINTS - 1)
        cp = Oil.createObject("Path2dControlPoint")
        cp.position.x = t
        cp.position.y = 0.0
        pathGen.path.points.append(cp)
        if j % 2 == 0:
            oscillatingPoints.append((cp, j // 2))

elif MODE == "bars":
    for i in range(N_BANDS):
        x = i / (N_BANDS - 1)
        for role in ("fixed_bottom", "oscillating", "fixed_bottom"):
            cp = Oil.createObject("Path2dControlPoint")
            cp.position.x = x
            cp.position.y = 0.0
            pathGen.path.points.append(cp)
            if role == "oscillating":
                oscillatingPoints.append((cp, i))

else:
    raise ValueError(f"MODE inconnu : {MODE}")

shapeLayer.generator = pathGen
shapeLayer.renderer.fill.enabled = False
shapeLayer.renderer.stroke.enabled = True
shapeLayer.renderer.stroke.thickness.set(STROKE_THICKNESS_DEFAULT)
# Note : shapeLayer n'est PAS ajoute directement a vizCompo.layers - il sert de
# masque au gradient (voir plus bas), pas affiche tel quel.

# --- Compo interne portant la shape, utilisee comme masque ---
# Installee ICI, avant la creation des Links qui ciblent des sous-elements de
# shapeLayer (points, stroke.thickness) - bonne pratique (voir note plus haut).
maskCompo = Oil.createObject("Compo")
maskCompo.rasterizer.resolution.preset.set(RESOLUTION_PRESET_CUSTOM)
maskCompo.rasterizer.resolution.width.set(COMPO_WIDTH)
maskCompo.rasterizer.resolution.height.set(COMPO_HEIGHT)
maskCompo.layers.append(shapeLayer)

# --- Parameter Bank : Freq Max / Amplitude Min / Amplitude Max / Stroke Width ---
# Place en PREMIER dans vizCompo.tools pour un acces facile dans l'UI.
paramBank = Oil.createObject("ParameterBank")
paramBank.label = "Parameters"

freqMaxParam = Oil.createObject("Parameter(Percentage)")
freqMaxParam.label = "Freq Max"
freqMaxParam.value.set(FREQ_MAX_DEFAULT)
paramBank.parameters.append(freqMaxParam)

ampMinParam = Oil.createObject("Parameter(Percentage)")
ampMinParam.label = "Amplitude Min"
ampMinParam.value.set(AMPLITUDE_MIN_DEFAULT)
paramBank.parameters.append(ampMinParam)

ampMaxParam = Oil.createObject("Parameter(Percentage)")
ampMaxParam.label = "Amplitude Max"
ampMaxParam.value.set(AMPLITUDE_MAX_DEFAULT)
paramBank.parameters.append(ampMaxParam)

strokeParam = Oil.createObject("Parameter(PositiveReal)")
strokeParam.label = "Stroke Width"
strokeParam.value.set(STROKE_THICKNESS_DEFAULT)
paramBank.parameters.append(strokeParam)

vizCompo.tools.append(paramBank)

# --- Device audio : canal Left du device DirectSound ---
dsDevice = None
for d in engine.devices.devices:
    if d.getOilClassName() == "JuceAudioDevice" and "DirectSound" in str(d.identifier):
        dsDevice = d
        break
audioChannel = None
for ch in dsDevice.inputChannels:
    if ch.getFriendlyName() == "Left":
        audioChannel = ch
        break

# --- Link Bank : un AudioSpectrumLinkSource par point oscillant ---
linkBank = Oil.createObject("LinkBank")
linkBank.label = "Audio Spectrum"
extractors = []
for cp, idx in oscillatingPoints:
    source = Oil.createObject("AudioSpectrumLinkSource")
    source.extractor.audioChannel.set(audioChannel)
    source.extractor.frequencyInterval.begin.set(idx / N_BANDS * FREQ_MAX_DEFAULT)
    source.extractor.frequencyInterval.end.set((idx + 1) / N_BANDS * FREQ_MAX_DEFAULT)
    source.extractor.amplitudeInterval.begin.set(AMPLITUDE_MIN_DEFAULT)
    source.extractor.amplitudeInterval.end.set(AMPLITUDE_MAX_DEFAULT)

    smoothMod = Oil.createObject("SmoothLinkModifier")
    smoothMod.positiveSpeed.set(20.0)
    smoothMod.negativeSpeed.set(5.0)

    target = Oil.createObject("ParameterLinkTarget")
    target.target.set(cp.position.y)
    target.modifiers.append(smoothMod)

    link = Oil.createObject("Link")
    link.label = f"Band {idx:02d}"
    link.source = source
    link.targets.append(target)
    linkBank.links.append(link)
    extractors.append((source.extractor, idx))

vizCompo.tools.append(linkBank)

# --- Links : Freq Max -> chaque frequencyInterval.begin/end (facteur proportionnel par bande) ---
freqLinkBank = Oil.createObject("LinkBank")
freqLinkBank.label = "Freq Max Scaling"
for extractor, idx in extractors:
    beginFactor = idx / N_BANDS
    endFactor = (idx + 1) / N_BANDS

    beginSource = Oil.createObject("ParameterLinkSource")
    beginSource.target.set(freqMaxParam.value)
    beginMult = Oil.createObject("MultiplyLinkModifier")
    beginMult.factor.set(beginFactor)
    beginSource.modifiers.append(beginMult)
    beginTarget = Oil.createObject("ParameterLinkTarget")
    beginTarget.target.set(extractor.frequencyInterval.begin)
    beginLink = Oil.createObject("Link")
    beginLink.label = f"Band {idx:02d} Freq Begin"
    beginLink.source = beginSource
    beginLink.targets.append(beginTarget)
    freqLinkBank.links.append(beginLink)

    endSource = Oil.createObject("ParameterLinkSource")
    endSource.target.set(freqMaxParam.value)
    endMult = Oil.createObject("MultiplyLinkModifier")
    endMult.factor.set(endFactor)
    endSource.modifiers.append(endMult)
    endTarget = Oil.createObject("ParameterLinkTarget")
    endTarget.target.set(extractor.frequencyInterval.end)
    endLink = Oil.createObject("Link")
    endLink.label = f"Band {idx:02d} Freq End"
    endLink.source = endSource
    endLink.targets.append(endTarget)
    freqLinkBank.links.append(endLink)

vizCompo.tools.append(freqLinkBank)

# --- Links : Amplitude Min/Max -> tous les amplitudeInterval.begin/end (partages) ---
ampMinSource = Oil.createObject("ParameterLinkSource")
ampMinSource.target.set(ampMinParam.value)
ampMinLink = Oil.createObject("Link")
ampMinLink.label = "Amplitude Min"
ampMinLink.source = ampMinSource
for extractor, idx in extractors:
    t = Oil.createObject("ParameterLinkTarget")
    t.target.set(extractor.amplitudeInterval.begin)
    ampMinLink.targets.append(t)

ampMaxSource = Oil.createObject("ParameterLinkSource")
ampMaxSource.target.set(ampMaxParam.value)
ampMaxLink = Oil.createObject("Link")
ampMaxLink.label = "Amplitude Max"
ampMaxLink.source = ampMaxSource
for extractor, idx in extractors:
    t = Oil.createObject("ParameterLinkTarget")
    t.target.set(extractor.amplitudeInterval.end)
    ampMaxLink.targets.append(t)

ampLinkBank = Oil.createObject("LinkBank")
ampLinkBank.label = "Amplitude Range"
ampLinkBank.links.append(ampMinLink)
ampLinkBank.links.append(ampMaxLink)
vizCompo.tools.append(ampLinkBank)

# --- Link : Stroke Width ---
strokeSource = Oil.createObject("ParameterLinkSource")
strokeSource.target.set(strokeParam.value)
strokeTarget = Oil.createObject("ParameterLinkTarget")
strokeTarget.target.set(shapeLayer.renderer.stroke.thickness)
strokeLink = Oil.createObject("Link")
strokeLink.label = "Stroke Width"
strokeLink.source = strokeSource
strokeLink.targets.append(strokeTarget)
strokeLinkBank = Oil.createObject("LinkBank")
strokeLinkBank.label = "Stroke Width"
strokeLinkBank.links.append(strokeLink)
vizCompo.tools.append(strokeLinkBank)

# --- Gradient Texture Generator (arc-en-ciel) avec le waveform en masque ---
gen = Oil.createObject("GradientTextureGenerator")
gen.type = Oil.createObject("Linear2dGradient")
gen.smoothness.set(2.0)
gen.resolution.width.set(COMPO_WIDTH)
gen.resolution.height.set(COMPO_HEIGHT)

gen.gradient = Oil.createObject("QuadritoneColorFunction")
g = gen.gradient
g.beginColor.red.set(0.9825006127357483)
g.beginColor.green.set(0.0)
g.beginColor.blue.set(0.0)
g.beginColor.alpha.set(1.0)
g.endColor.red.set(0.071352519094944)
g.endColor.green.set(0.9704594016075134)
g.endColor.blue.set(0.0)
g.endColor.alpha.set(1.0)
g.intermediateColor1.red.set(1.0)
g.intermediateColor1.green.set(0.6604838371276855)
g.intermediateColor1.blue.set(0.0)
g.intermediateColor1.alpha.set(1.0)
g.intermediateColor2.red.set(0.8387186527252197)
g.intermediateColor2.green.set(1.0)
g.intermediateColor2.blue.set(0.0)
g.intermediateColor2.alpha.set(1.0)
g.intermediatePosition1.set(0.2)
g.intermediatePosition2.set(0.7776660000000001)

gen.position.center.x = 0.5
gen.position.center.y = 0.5
gen.position.rotation.set(0.0)
gen.position.size.width.set(COMPO_WIDTH)
gen.position.size.height.set(COMPO_HEIGHT)

maskMod = Oil.createObject("MaskTextureModifier")
mask = Oil.createObject("TextureLayerTextureMask")
mask.generator = maskCompo
mask.inverse.set(False)
mask.opacity.set(1.0)
mask.resolution.width.set(COMPO_WIDTH)
mask.resolution.height.set(COMPO_HEIGHT)
maskMod.masks.append(mask)
gen.modifiers.append(maskMod)

gradLayer = Oil.createObject("TextureLayer")
gradLayer.generator = gen
gradLayer.label = "Linear Gradient"
vizCompo.layers.append(gradLayer)

# --- Effets de post-traitement sur la Compo "spectrum" (Pixelate + Feedback) ---
# NE PAS mettre les bandes noires dans cette Compo : elles doivent rester EN DEHORS,
# sinon elles subissent aussi le Pixelate/Feedback (voir Compo master plus bas).
PIXELATE_MODE_NUM_PIXELS_WIDTH = 1  # PixelateMode : 0=downscaleFactor, 1=numPixelsWidth, 2=numPixelsHeight
BLENDING_MODE_SCREEN = 10           # BlendingMode : ... 10=screen (trouve par diagnostic)

pixelateMod = Oil.createObject("PixelateTextureModifier")
pixelateMod.mode.set(PIXELATE_MODE_NUM_PIXELS_WIDTH)
pixelateMod.value.set(95.0907)
pixelateMod.intensity.set(0.32)
vizCompo.modifiers.append(pixelateMod)

feedbackMod = Oil.createObject("FeedbackTextureModifier")
feedbackMod.blendingMode.set(BLENDING_MODE_SCREEN)
feedbackMod.intensity.set(1.0)
feedbackMod.feedbackLevel.set(0.8)
vizCompo.modifiers.append(feedbackMod)

# --- vizCompo (spectrum) enveloppee dans une TextureLayer ---
spectrumLayer = Oil.createObject("TextureLayer")
spectrumLayer.generator = vizCompo
spectrumLayer.label = "spectrum"

# --- Bandes noires (CheckerBoardTextureGenerator detourne : cellules tres larges/plates,
# une couleur opaque noire, l'autre transparente -> effet de bandes). EN DEHORS de la
# Compo spectrum, donc PAS affectees par le Pixelate/Feedback ci-dessus. ---
bandsLayer = Oil.createObject("TextureLayer")
bandsLayer.label = "Horizontal Bands"
bandsGen = Oil.createObject("CheckerBoardTextureGenerator")

# IMPORTANT : delier width/height AVANT de les regler, sinon ils restent forces a la
# meme valeur (size.linked / balance.linked = True par defaut).
bandsGen.size.linked.set(False)
bandsGen.size.width.set(-0.3)
bandsGen.size.height.set(0.005)
bandsGen.balance.linked.set(False)
bandsGen.balance.width.set(0.0)
bandsGen.balance.height.set(0.0)
bandsGen.offset.x.set(0.0)
bandsGen.offset.y.set(0.0)
bandsGen.evenColor.red.set(0.0)
bandsGen.evenColor.green.set(0.0)
bandsGen.evenColor.blue.set(0.0)
bandsGen.evenColor.alpha.set(1.0)
bandsGen.oddColor.red.set(0.0)
bandsGen.oddColor.green.set(0.0)
bandsGen.oddColor.blue.set(0.0)
bandsGen.oddColor.alpha.set(0.0)
bandsLayer.generator = bandsGen
bandsLayer.renderer.opacity.set(BANDS_OPACITY)

# --- Compo master : spectrum + Horizontal Bands, cote a cote ---
masterCompo = Oil.createObject("Compo")
masterCompo.rasterizer.resolution.preset.set(RESOLUTION_PRESET_CUSTOM)
masterCompo.rasterizer.resolution.width.set(COMPO_WIDTH)
masterCompo.rasterizer.resolution.height.set(COMPO_HEIGHT)
masterCompo.layers.append(spectrumLayer)
masterCompo.layers.append(bandsLayer)

# --- Wrap dans une TextureLayer + flip vertical + insertion dans la scene ---
vizLayer = Oil.createObject("TextureLayer")
vizLayer.generator = masterCompo
vizLayer.label = VIZ_LABEL
vizLayer.renderer.placement.verticalFlip = True
script.parentElement.layers.append(vizLayer)

result = f"vizualiser recree (mode={MODE}) : {N_BANDS} bandes, master(spectrum + bandes noires)"
