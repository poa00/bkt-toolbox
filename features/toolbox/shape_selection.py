# -*- coding: utf-8 -*-
'''
Created on 06.02.2018

@author: rdebeerst
'''

import bkt
import bkt.library.powerpoint as pplib

import shapes as mod_shapes

from collections import OrderedDict

import logging


class ShapeSelector(object):
    key_functions = OrderedDict()
    key_functions["shape_type"] =     lambda shp: (shp.Type, shp.AutoShapeType)
    key_functions["shape_width"] =    lambda shp: shp.Width
    key_functions["shape_height"] =   lambda shp: shp.Height
    
    key_functions["pos_left"] =       lambda shp: shp.Left
    key_functions["pos_top"]  =       lambda shp: shp.Top
    key_functions["pos_rotation"] =   lambda shp: shp.Rotation
    
    key_functions["fill_type"] =      lambda shp: (shp.Fill.Visible, shp.Fill.Type)
    key_functions["fill_color"] =     lambda shp: (shp.Fill.Visible, shp.Fill.BackColor.RGB, shp.Fill.ForeColor.RGB)
    
    key_functions["line_weight"] =    lambda shp: (shp.Line.Visible, shp.Line.Weight)
    key_functions["line_style"] =     lambda shp: (shp.Line.Visible, shp.Line.Style, shp.Line.DashStyle)
    key_functions["line_color"] =     lambda shp: (shp.Line.Visible, shp.Line.BackColor.RGB, shp.Line.ForeColor.RGB)
    key_functions["line_begin"] =     lambda shp: (shp.Line.BeginArrowheadLength, shp.Line.BeginArrowheadStyle, shp.Line.BeginArrowheadWidth)
    key_functions["line_end"] =       lambda shp: (shp.Line.EndArrowheadLength, shp.Line.EndArrowheadStyle, shp.Line.EndArrowheadWidth)
    
    key_functions["font_name"] =      lambda shp: shp.TextFrame.TextRange.Font.Name
    key_functions["font_color"] =     lambda shp: shp.TextFrame.TextRange.Font.Color.RGB
    key_functions["font_size"] =      lambda shp: shp.TextFrame.TextRange.Font.Size
    key_functions["font_style"] =     lambda shp: (shp.TextFrame.TextRange.Font.Bold, shp.TextFrame.TextRange.Font.Underline, shp.TextFrame.TextRange.Font.Italic)
    
    key_functions["content_text"] =   lambda shp: shp.TextFrame.TextRange.Text
    key_functions["content_len"] =    lambda shp: len(shp.TextFrame.TextRange.Text)

    @staticmethod
    def _selectByKeys(master_shapes, all_shapes, keys):
        logging.debug("ShapeSelector._selectByKeys")
        cmp_funcs = [ShapeSelector.key_functions[key] for key in keys]

        master_styles= set()
        for shpMaster in master_shapes:
            master_styles.add( tuple(func(shpMaster) for func in cmp_funcs) )

        all_shapes = set(all_shapes) - set(master_shapes)
        logging.debug("ShapeSelector._selectByKeys: set ready, do select")
        for shp in all_shapes:
            try:
                # if all(func(shpMaster) == func(shp) for func in cmp_funcs):
                if tuple(func(shp) for func in cmp_funcs) in master_styles:
                    shp.Select(replace=False)
            except:
                pass
        logging.debug("ShapeSelector._selectByKeys: select done")

    @staticmethod
    def selectionForm(context):
        from dialogs.shape_select import SelectWindow
        wnd = SelectWindow(ShapeSelector, context)
        wnd.show_dialog(modal=True)

        # keys = []
        # values = []
        # for k,v in ShapeSelector.key_functions.items():
        #     keys.append(k)
        #     values.append( (v[0], False) )
        
        # user_form = bkt.ui.UserInputBox("Eigenschaften für Selektion auswählen:", "Shapes selektieren")
        # clb = user_form._add_checked_listbox("comparisons", values, clb_return="CheckedIndices")
        # clb.Height = 275
        # form_return = user_form.show()
        # if len(form_return) == 0 or len(form_return["comparisons"]) == 0:
        #     return

        # ShapeSelector.selectByKeys(context, [keys[sel] for sel in form_return["comparisons"]])

    @classmethod
    def selectShapes(cls, context, shapes):
        context.selection.Unselect()
        for shp in shapes:
            shp.Select(replace=False)

    @classmethod
    def selectByKeys(cls, context, keys, master_shapes=None, unselect=False):
        logging.debug("ShapeSelector.selectByKeys")
        master_shapes = master_shapes or context.shapes
        if unselect:
            cls.selectShapes(context, master_shapes)
            logging.debug("ShapeSelector.selectByKeys: unselect done")
        
        if context.selection.HasChildShapeRange:
            cls._selectByKeys(master_shapes, context.selection.ShapeRange[1].GroupItems, keys)
        else:
            cls._selectByKeys(master_shapes, context.slides[0].Shapes, keys)

    # @staticmethod
    # def selectByShape(shapes, slide):
    #     #slide.Application.ActiveWindow.Selection.Unselect()
    #     for shpMaster in shapes:
    #         for shp in slide.Shapes:
    #             try:
    #                 if shp.Type == shpMaster.Type and shp.AutoShapeType == shpMaster.AutoShapeType:
    #                     shp.Select(replace=False)
    #             except:
    #                 pass
    
    # @staticmethod
    # def selectByFill(shapes, slide):
    #     #slide.Application.ActiveWindow.Selection.Unselect()
    #     for shpMaster in shapes:
    #         for shp in slide.Shapes:
    #             try:
    #                 if shp.Fill.Type == shpMaster.Fill.Type and shp.Fill.ForeColor.RGB == shpMaster.Fill.ForeColor.RGB:
    #                     shp.Select(replace=False)
    #             except:
    #                 pass
    
    # @staticmethod
    # def selectByLine(shapes, slide):
    #     #slide.Application.ActiveWindow.Selection.Unselect()
    #     for shpMaster in shapes:
    #         for shp in slide.shapes:
    #             try:
    #                 if shp.Line.DashStyle == shpMaster.Line.DashStyle and shp.Line.ForeColor.RGB == shpMaster.Line.ForeColor.RGB:
    #                     shp.Select(replace=False)
    #             except:
    #                 pass

    
    @staticmethod
    def invert_selection(slide, selection):
        
        if selection.Type == 2 or selection.Type == 3:
            # shapes or text selected
            selected_shapes = list(iter(selection.shaperange))
        else:
            # slide selected
            selected_shapes = []
        
        slide_shapes = list(iter(slide.shapes))
        
        new_shape_selection = [shape for shape in slide_shapes if not shape in selected_shapes]
        if len(new_shape_selection) == 0:
            selection.Unselect()
        else:
            new_shape_selection[0].Select(replace=True)
            for shape in new_shape_selection:
                shape.Select(replace=False)

    @classmethod
    def _is_within(cls, outer, inner):
        return (outer.visual_x < inner.visual_x and outer.visual_y < inner.visual_y and
                outer.visual_x+outer.visual_width > inner.visual_x+inner.visual_width and outer.visual_y+outer.visual_height > inner.visual_y+inner.visual_height)
        # return (outer.Left < inner.Left and outer.Top < inner.Top and
        #         outer.Left+outer.Width > inner.Left+inner.Width and outer.Top+outer.Height > inner.Top+inner.Height)
    
    @classmethod
    def _is_ontop(cls, lower, upper):
         return (lower.ZOrderPosition < upper.ZOrderPosition)

    @classmethod
    def _has_overlap(cls, shp1, shp2):
        return (shp1.visual_x < shp2.visual_x+shp2.visual_width  and shp1.visual_x+shp1.visual_width > shp2.visual_x and
                shp1.visual_y < shp2.visual_y+shp2.visual_height and shp1.visual_y+shp1.visual_height > shp2.visual_y)
        # return (shp1.Left < shp2.Left+shp2.Width and shp1.Left+shp1.Width > shp2.Left and
        #         shp1.Top < shp2.Top+shp2.Height and shp1.Top+shp1.Height > shp2.Top)
    
    @classmethod
    def select_overlapping(cls, shapes, slide):
        all_shapes = pplib.wrap_shapes(slide.Shapes)
        for shpMaster in pplib.wrap_shapes(shapes):
            for shp in all_shapes:
                if cls._has_overlap(shpMaster, shp):
                    shp.Select(replace=False)
    
    @classmethod
    def select_within(cls, shapes, slide):
        for shpMaster in shapes:
            for shp in slide.Shapes:
                if cls._is_within(shpMaster, shp):
                    shp.Select(replace=False)
    
    @classmethod
    def select_containing(cls, shapes, slide):
        all_shapes = pplib.wrap_shapes(slide.Shapes)
        for shpMaster in pplib.wrap_shapes(shapes):
            for shp in all_shapes:
                if cls._is_ontop(shpMaster, shp) and cls._is_within(shpMaster, shp):
                    shp.Select(replace=False)
    
    @classmethod
    def select_behind(cls, shapes, slide):
        all_shapes = pplib.wrap_shapes(slide.Shapes)
        for shpMaster in pplib.wrap_shapes(shapes):
            for shp in all_shapes:
                if not cls._is_ontop(shpMaster, shp) and cls._is_within(shpMaster, shp):
                    shp.Select(replace=False)






selection_menu = bkt.ribbon.Menu(
    label='Auswahl',
    screentip='Auswahl von Shapes',
    supertip='Auswahl von Shapes, die dem aktuellem Shape bzgl. Typ/Hintergrund/Rahmen ähneln',
    show_label=False,
    image_mso='ObjectsMultiSelect',
    children = [
        bkt.ribbon.MenuSeparator(title="Auswahl von Shapes…"),
        bkt.ribbon.Button(
            id = 'shapes_form',
            image_mso = 'GroupSmartArtQuickStyles',
            label='…mit gleicher Form',
            #show_label=False,
            on_action=bkt.Callback(lambda context: ShapeSelector.selectByKeys(context, ['shape_type']), context=True),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte mit gleicher Form markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die die gleiche Form haben wie eine der selektierten Shapes",
        ),

        bkt.ribbon.Button(
            id = 'shapes_bg',
            image_mso = 'AppointmentColor1',
            label='…mit gleichem Hintergrund',
            #show_label=False,
            on_action=bkt.Callback(lambda context: ShapeSelector.selectByKeys(context, ['fill_type', 'fill_color']), context=True),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte mit gleichem Hintergrund markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die den gleichen Hintergrund (Farbe) haben wie eine der selektierten Shapes",
        ),

        bkt.ribbon.Button(
            id = 'shapes_border',
            image_mso = 'BlackAndWhiteBlackWithWhiteFill',
            label='…mit gleichem Rahmen',
            #show_label=False,
            on_action=bkt.Callback(lambda context: ShapeSelector.selectByKeys(context, ['line_style', 'line_color']), context=True),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte mit gleichem Rahmen markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die den gleichen Rahmen (Farbe, Strichtyp) haben wie eine der selektierten Shapes",
        ),

        bkt.ribbon.Button(
            id = 'shapes_font',
            image_mso = 'FontColorPicker',
            label='…mit gleicher Schriftfarbe',
            #show_label=False,
            on_action=bkt.Callback(lambda context: ShapeSelector.selectByKeys(context, ['font_color']), context=True),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte mit gleicher Schritfarbe markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die die gleiche Schriftfarbe haben wie eine der selektierten Shapes",
        ),

        bkt.ribbon.Button(
            id = 'shapes_text',
            image_mso = 'TextBoxInsert',
            label='…mit gleichem Text',
            #show_label=False,
            on_action=bkt.Callback(lambda context: ShapeSelector.selectByKeys(context, ['content_text']), context=True),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte mit gleichem Text markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die den gleichen Text haben wie eine der selektierten Shapes",
        ),

        bkt.ribbon.Button(
            id = 'shapes_size',
            image_mso = 'ShowEmptyContainers',
            label='…mit gleicher Größe',
            #show_label=False,
            on_action=bkt.Callback(lambda context: ShapeSelector.selectByKeys(context, ['shape_width', 'shape_height']), context=True),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte mit gleicher Größe markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die die gleiche Größe haben wie eine der selektierten Shapes",
        ),
        bkt.ribbon.MenuSeparator(),
        bkt.ribbon.Button(
            id = 'shapes_select_custom',
            image_mso = 'ShowCustomPropertiesPage',
            label='Benutzerdefinierte Auswahl…',
            #show_label=False,
            on_action=bkt.Callback(ShapeSelector.selectionForm, context=True),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte nach Benutzerdefinierter Auswahl markieren",
            supertip="Öffne einen Dialog zur Auswahl der Shape-Eigenschaften, nach welcher die Shapes auf der aktuellen Folie markiert werden sollen.",
        ),

        bkt.ribbon.MenuSeparator(),
        bkt.ribbon.Button(
            id = 'shapes_select_overlapping',
            image_mso = 'SlideShowResolutionGallery',
            label='Überlappend',
            #show_label=False,
            on_action=bkt.Callback(ShapeSelector.select_overlapping),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte überlappend mit gewählten Shapes markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die sich mit einem der selektierten Shapes überlappen.",
        ),
        bkt.ribbon.Button(
            id = 'shapes_select_within',
            image_mso = 'SlideShowResolutionGallery',
            label='Innerhalb',
            #show_label=False,
            on_action=bkt.Callback(ShapeSelector.select_within),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte innerhalb der gewählten Shapes markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die sich vollständig innerhalb eines der selektierten Shapes befinden.",
        ),
        bkt.ribbon.Button(
            id = 'shapes_select_containing',
            image_mso = 'SlideShowResolutionGallery',
            label='Inner- && oberhalb',
            #show_label=False,
            on_action=bkt.Callback(ShapeSelector.select_containing),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte innerhalb und oberhalb der gewählten Shapes markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die sich vollständig innerhalb und oberhalb (d.h. Z-Order ist größer) eines der selektierten Shapes befinden.",
        ),
        bkt.ribbon.Button(
            id = 'shapes_select_behind',
            image_mso = 'SlideShowResolutionGallery',
            label='Inner- && unterhalb',
            #show_label=False,
            on_action=bkt.Callback(ShapeSelector.select_behind),
            get_enabled = bkt.apps.ppt_shapes_or_text_selected,
            screentip="Shape-Objekte innerhalb und unterhalb der gewählten Shapes markieren",
            supertip="Selektiere alle Shapes auf dem aktuellen Slide, die sich vollständig innerhalb und unterhalb (d.h. Z-Order ist kleiner) eines der selektierten Shapes befinden.",
        ),

        bkt.ribbon.MenuSeparator(title="Markieren"),
        bkt.mso.control.SelectionPane,
        bkt.ribbon.Button(
            id = 'shapes_select_invert',
            image_mso = 'ObjectsMultiSelect',
            label='Auswahl invertieren',
            on_action=bkt.Callback(ShapeSelector.invert_selection),
            # get_enabled = bkt.CallbackTypes.get_enabled.dotnet_name,
            supertip="Invertiert die aktuelle Auswahl. Es werden alle Shapes (auch Platzhalter) markiert, die vorher nicht markiert waren.",
        ),
    ]
)



clipboard_group = bkt.ribbon.Group(
    id="bkt_clipboard_group",
    label='Ablage',
    image_mso='ObjectsMultiSelect',
    children=[
        bkt.ribbon.SplitButton(
            show_label=False,
            get_enabled=bkt.Callback(lambda context: context.app.commandbars.GetEnabledMso("Paste"), context=True),
            children=[
                bkt.mso.button.PasteSpecialDialog,
                bkt.ribbon.Menu(
                    label="Einfügen-Menü",
                    children=[
                        bkt.mso.button.PasteSpecialDialog,
                        bkt.ribbon.MenuSeparator(),
                        bkt.ribbon.Button(
                            id='paste_to_slides',
                            label="Auf ausgewählte Folien einfügen",
                            image_mso='Paste',
                            on_action=bkt.Callback(mod_shapes.ShapesMore.paste_to_slides, slides=True),
                        ),
                    ]
                )
            ]
        ),
        #bkt.mso.control.PasteSpecialDialog,
        #bkt.mso.control.Cut,
        bkt.mso.control.CopySplitButton,
        
        selection_menu,
        
        bkt.mso.control.PasteApplyStyle,
        bkt.mso.control.PickUpStyle,
        bkt.mso.control.FormatPainter
    ]
)

