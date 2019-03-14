# -*- coding: utf-8 -*-

import bkt
import bkt.library.powerpoint as pplib

# langUS = 1033 #msoLanguageIDEnglishUS
# langDE = 1031 #msoLanguageIDGerman
# langUK = 2057 #msoLanguageIDEnglishUK
# langAU = 3079 #msoLanguageIDGermanAustria


class LangSetter(object):
    #FIXME: make this configurable
    langs = [
        #[key, id, name, image]
        ['de', 1031, "Deutsch", "GermanFlag"],
        ['us', 1033, "US English", "USFlag"],
        ['uk', 2057, "UK English", "UKFlag"],
    ]

    @classmethod
    def get_button(cls, language, idtag=""):
        return bkt.ribbon.Button(
                id = 'lang_'+language[0]+idtag,
                label=language[2],
                image=language[3],
                screentip="Sprache auf " + language[2] + " ändern",
                supertip="Setze Sprache für ausgewählten Text bzw. alle ausgewählten Shapes.\nWenn mehrere Folien ausgewählt sind, werden alle Shapes der gewählten Folien geändert.\nWenn nichts ausgewählt ist, werden alle Shapes in der Präsentation sowie die Standardsprache geändert.",
                on_action=bkt.Callback(lambda selection, presentation: cls.set_language(selection, presentation, language[1]), selection=True, presentation=True)
            )

    @classmethod
    def set_language(cls, selection, presentation, langCode):
        shapes = pplib.get_shapes_from_selection(selection)
        slides = pplib.get_slides_from_selection(selection)

        # Set language for selected text, shapes, slides or whole presentation
        if selection.Type == 3 and selection.TextRange2.Length > 0: #text selected
            selection.TextRange2.LanguageID = langCode
        elif len(shapes) > 0:
            #bkt.helpers.message("Setze Sprache für Shapes: " + str(len(shapes)))
            cls.set_language_for_shapes(shapes, langCode)
        elif len(slides) > 1:
            #bkt.helpers.message("Setze Sprache für Slides: " + str(len(slides)))
            if not bkt.helpers.confirmation("Sprache aller Shapes auf ausgewählten Folien ändern?"):
                return
            cls.set_language_for_slides(slides, langCode)
        else:
            #bkt.helpers.message("Setze Sprache für Präsentation")
            if not bkt.helpers.confirmation("Sprache aller Shapes auf allen Folien (inkl. Standardsprache der Präsentation) ändern?"):
                return
            presentation.DefaultLanguageID = langCode
            cls.set_language_for_slides(presentation.slides, langCode)

    @classmethod
    def set_language_for_slides(cls, slides, langCode):
        for slide in slides:
            cls.set_language_for_shapes(slide.shapes, langCode, False)

    @classmethod
    def set_language_for_shapes(cls, shapes, langCode, from_selection=True):
        for textframe in pplib.iterate_shape_textframes(shapes, from_selection):
            textframe.TextRange.LanguageID = langCode


sprachen_gruppe = bkt.ribbon.Group(
    id="bkt_language_group",
    label="Sprache",
    image_mso="GroupLanguage",
    auto_scale=True,
    children=[
        LangSetter.get_button(lang, "_group")
        for lang in LangSetter.langs
    ] + [
        bkt.ribbon.DialogBoxLauncher(idMso='SetLanguage')
    ]
)

sprachen_menu = bkt.ribbon.Menu(
    id="lang_change_menu",
    label="Sprache ändern",
    image_mso="GroupLanguage",
    children=[
        bkt.ribbon.MenuSeparator(title="Sprache von Shapes oder Folien ändern"),
    ] + [
        LangSetter.get_button(lang)
        for lang in LangSetter.langs
    ] + [
        bkt.ribbon.MenuSeparator(),
        bkt.mso.button.SetLanguage,
        bkt.mso.button.Spelling,
    ]
)