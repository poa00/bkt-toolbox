# -*- coding: utf-8 -*-
'''
Created on 29.03.2017

@author: tweuffel
'''

import bkt
# import bkt.library.powerpoint as powerpoint
# import bkt.library.bezier as bezier
# import bkt.library.algorithms
#import System
from datetime import datetime
from System import Environment
import bkt.ui


TOOLBOX_NOTE = "TOOLBOX-NOTE"
TOOLBOX_BACKUP = "TOOLBOX-BACKUP"



class EditModeShapes(object):
    color_rgb = 16777062
    color_theme = 0
    color_brightness = 0
    
    @classmethod
    def addNote(cls, slide, context):
        # Positionsanpassung ermitteln (unter existierenden Shape)
        yPosition = 0
        for cShp in slide.shapes:
            if cShp.Tags.Item(TOOLBOX_NOTE) != "":
                yPosition = cShp.top + cShp.height + 2
        # Shape rechts oben auf slide erstellen
        shp = slide.shapes.AddShape( 1 #msoShapeRectangle
            , 0, yPosition, 300, 20)
        shp.Tags.Add(TOOLBOX_NOTE, "1")
        # Shape-Stil
        shp.Line.Weight = 0
        shp.Line.Visible = 0 #msoFalse
        shp.Fill.Visible = 1 #msoTrue
        if cls.color_theme > 0:
            shp.Fill.ForeColor.ObjectThemeColor = cls.color_theme
            shp.Fill.ForeColor.Brightness = cls.color_brightness
        else:
            shp.Fill.ForeColor.RGB = cls.color_rgb
        # Text-Stil
        shp.TextFrame.TextRange.Font.Color.RGB = 0
        shp.TextFrame.TextRange.Font.Size = 12
        shp.TextFrame.TextRange.Font.Bold = True
        shp.TextFrame.TextRange.ParagraphFormat.Alignment = 1 #ppAlignLeft
        shp.TextFrame.TextRange.ParagraphFormat.Bullet.Visible = False
        shp.TextFrame.VerticalAnchor = 1 #msoAnchorTop
        # Autosize / Text nicht umbrechen
        shp.TextFrame.WordWrap = 1 #msoTrue
        shp.TextFrame.AutoSize = 1 #ppAutoSizeShapeToFitText
        # Innenabstand
        shp.TextFrame.MarginBottom = 3
        shp.TextFrame.MarginTop    = 3
        shp.TextFrame.MarginLeft   = 5
        shp.TextFrame.MarginRight  = 5
        # Text
        dt = datetime.now()
        new_text = dt.strftime("%d.%m.%y %H:%M") + " (" + Environment.UserName + "): EDIT"
        shp.TextFrame.TextRange.Text = new_text
        shp.TextFrame.TextRange.Characters(len(new_text)-3, 4).Select()
        shp.Left = context.app.ActivePresentation.PageSetup.SlideWidth - shp.width
    
    
    @staticmethod
    def toogleNotesOnSlide(slide, context):
        visible = None
        for cShp in slide.shapes:
            if cShp.Tags.Item(TOOLBOX_NOTE) != "":
                if visible == None:
                    visible = 1 if cShp.Visible == 0 else 0
                cShp.Visible = visible
    
    
    @staticmethod
    def toggleNotesOnAllSlides(slide, context):
        visible = None
        for sld in slide.parent.slides:            
            for cShp in sld.shapes:
                if cShp.Tags.Item(TOOLBOX_NOTE) != "":
                    if visible == None:
                        visible = 1 if cShp.Visible == 0 else 0
                    cShp.Visible = visible
    
    
    @staticmethod
    def removeNotesOnSlide(slide, context):
        shapesToRemove = []
        
        for cShp in slide.shapes:
            if cShp.Tags.Item(TOOLBOX_NOTE) != "":
                shapesToRemove.append(cShp)
        
        for cShp in shapesToRemove:
            cShp.Delete()
    
    
    @staticmethod
    def removeNotesOnAllSlides(slide, context):
        for sld in slide.parent.slides:
            shapesToRemove = []
            
            for cShp in sld.shapes:
                if cShp.Tags.Item(TOOLBOX_NOTE) != "":
                    shapesToRemove.append(cShp)
        
            for cShp in shapesToRemove:
                cShp.Delete()

    @classmethod
    def set_color_default(cls):
        cls.color_rgb = 16777062
        cls.color_theme = 0
        cls.color_brightness = 0

    @classmethod
    def set_color_rgb(cls, color):
        cls.color_rgb = color
        cls.color_theme = 0
        cls.color_brightness = 0
        pass

    @classmethod
    def set_color_theme(cls, color_index, brightness):
        cls.color_rgb = 0
        cls.color_theme = color_index
        cls.color_brightness = brightness

    @classmethod
    def get_color(cls):
        return [cls.color_theme, cls.color_brightness, cls.color_rgb]


notes_gruppe = bkt.ribbon.Group(
    label='Notes',
    image='noteAdd',
    children = [
        bkt.ribbon.Button(
            label='Notizen (+)', screentip='Notiz hinzufügen',
            image='noteAdd',
            on_action=bkt.Callback(EditModeShapes.addNote)
        ),
        bkt.ribbon.Button(
            label='Notizen (I/O)', screentip='Notizen auf Folie ein-/ausblenden',
            image='noteToggle',
            on_action=bkt.Callback(EditModeShapes.toogleNotesOnSlide)
        ),
        bkt.ribbon.Button(
            label='Notizen (-)', screentip='Notizen auf Folie löschen',
            image='noteRemove',
            on_action=bkt.Callback(EditModeShapes.removeNotesOnSlide)
        ),
        bkt.ribbon.Button(
            label='Alle Notizen (I/O)', screentip='Alle Notizen ein-/ausblenden',
            image='noteToggleAll',
            on_action=bkt.Callback(EditModeShapes.toggleNotesOnAllSlides)
        ),
        bkt.ribbon.Button(
            label='Alle Notizen (-)', screentip='Alle Notizen löschen',
            image='noteRemoveAll',
            on_action=bkt.Callback(EditModeShapes.removeNotesOnAllSlides)
        ),
        bkt.ribbon.ColorGallery(
            id = 'notes_color',
            label=u'Farbe ändern',
            on_rgb_color_change = bkt.Callback(EditModeShapes.set_color_rgb),
            on_theme_color_change = bkt.Callback(EditModeShapes.set_color_theme),
            get_selected_color = bkt.Callback(EditModeShapes.get_color),
            children=[
                bkt.ribbon.Button(
                    id="notes_color_default",
                    label="Standardfarbe",
                    on_action=bkt.Callback(EditModeShapes.set_color_default),
                    image_mso="ColorTeal",
                )
            ]
            # get_enabled = bkt.apps.ppt_shapes_or_text_selected,
        ),
    ]
)

bkt.powerpoint.add_tab(bkt.ribbon.Tab(
    id="bkt_powerpoint_toolbox_extensions",
    #id_q="nsBKT:powerpoint_toolbox_extensions",
    #insert_after_q="nsBKT:powerpoint_toolbox_advanced",
    insert_before_mso="TabHome",
    label=u'Toolbox 3/3',
    # get_visible defaults to False during async-startup
    get_visible=bkt.Callback(lambda:True),
    children = [
        notes_gruppe,
    ]
), extend=True)

