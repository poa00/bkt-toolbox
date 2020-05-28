# -*- coding: utf-8 -*-
'''
Created on 21.12.2017

@author: fstallmann
'''

from __future__ import absolute_import

import logging

from System import Array

import bkt
import bkt.library.powerpoint as pplib

from bkt import dotnet
Drawing = dotnet.import_drawing()


class StateShape(object):
    BKT_DIALOG_TAG = 'BKT_DIALOG_STATESHAPE'
    
    @classmethod
    def is_convertable_to_state_shape(cls, shape):
        try:
            return shape.Type == pplib.MsoShapeType['msoGroup']
        except:
            return False

    @classmethod
    def convert_to_state_shape(cls, shapes):
        for shape in shapes:
            try:
                shape.Tags.Add(bkt.contextdialogs.BKT_CONTEXTDIALOG_TAGKEY, cls.BKT_DIALOG_TAG)
                cls.switch_state(shape, pos=0)
            except:
                logging.exception("Error converting to state stape")
                continue

    @classmethod
    def is_state_shape(cls, shape):
        return pplib.TagHelper.has_tag(shape, bkt.contextdialogs.BKT_CONTEXTDIALOG_TAGKEY, cls.BKT_DIALOG_TAG)
        # return shape.Type == pplib.MsoShapeType['msoGroup']
    
    @classmethod
    def are_state_shapes(cls, shapes):
        return all(cls.is_state_shape(s) for s in shapes)
    
    @classmethod
    def switch_state(cls, shape, delta=0, pos=None):
        if not cls.is_state_shape(shape):
            raise ValueError("Shape is not a state shape")
        # ungroup shape, to get list of groups inside grouped items
        # ungrouped_shapes = shape.Ungroup()
        # shapes = list(iter(ungrouped_shapes))
        group = pplib.GroupManager(shape).ungroup()
        shapes = group.child_items
        # shapes.sort(key=lambda s: s.ZOrderPosition)
        # pos = min(max(pos, len(shapes)-1), -(len(shapes)-1)) #pos between -/+ number of shapes in group
        for i, s in enumerate(shapes):
            if pos is None and s.visible == -1:
                pos = i
            s.visible = False
        # for s in shapes[:pos]:
        #     s.ZOrder(0) #0=msoBringToFront, 1=msoSendToBack

        pos = (pos + delta) % len(shapes)
        shapes[pos].visible = True
        group.regroup()
        group.select(replace=False)
        # grp = ungrouped_shapes.Group()
        # grp.Tags.Add(bkt.contextdialogs.BKT_CONTEXTDIALOG_TAGKEY, cls.BKT_DIALOG_TAG)
        # try:
        #     #sometimes throws "Invalid request.  To select a shape, its view must be active.", e.g. right after duplicating the shape
        #     grp.Select(replace=False)
        # except:
        #     grp.Select()


    @classmethod
    def reset_state(cls, shapes):
        for shape in shapes:
            try:
                cls.switch_state(shape, pos=0)
            except:
                logging.exception("Statehape error resetting state")
                continue

    @classmethod
    def next_state(cls, shapes):
        for shape in shapes:
            try:
                cls.switch_state(shape, delta=1)
            except:
                logging.exception("Statehape error switching to next state")
                continue

    @classmethod
    def previous_state(cls, shapes):
        for shape in shapes:
            try:
                cls.switch_state(shape, delta=-1)
            except:
                logging.exception("Statehape error switching to previous state")
                continue

    @classmethod
    def set_state(cls, shapes, value):
        value = int(value)
        for shape in shapes:
            try:
                cls.switch_state(shape, pos=value)
            except:
                logging.exception("Statehape error setting state")
                continue

    # @classmethod
    # def get_show_all(cls, shape):
    #     return cls.is_state_shape(shape) and shape.GroupItems.Range(None).Visible == -1

    # @classmethod
    # def toggle_show_all(cls, shape, pressed):
    #     if not pressed:
    #         cls.switch_state(shape, pos=0)
    #     else:
    #         cls.show_all(shape)

    @classmethod
    def show_all(cls, shape):
        ungrouped_shapes = shape.Ungroup()
        for s in list(iter(ungrouped_shapes)):
            s.visible = True
        ungrouped_shapes.Group().Select()


    @classmethod
    def set_color_fill1(cls, shapes, color_setter):
        for shape in shapes:
            ref_shape = shape.GroupItems[1]
            ref_color = ref_shape.Fill.ForeColor.RGB
            ref_visible = ref_shape.Fill.Visible == -1
            for s in shape.GroupItems:
                if ref_visible and s.Fill.ForeColor.RGB == ref_color or not ref_visible and s.Fill.Visible == 0:
                    color_setter(s.Fill)

    @classmethod
    def set_color_fill2(cls, shapes, color_setter):
        for shape in shapes:
            ref_shape = shape.GroupItems[1]
            ref_color = ref_shape.Fill.ForeColor.RGB if ref_shape.Fill.Visible == -1 else None
            for s in shape.GroupItems:
                if s.Fill.Visible == -1 and s.Fill.ForeColor.RGB != ref_color:
                    color_setter(s.Fill)


    @classmethod
    def set_color_fill_rgb1(cls, shapes, color):
        def set_rgb_color(fill_obj):
            fill_obj.Visible = -1
            fill_obj.ForeColor.RGB = color
        cls.set_color_fill1(shapes, set_rgb_color)

    @classmethod
    def set_color_fill_theme1(cls, shapes, color_index, brightness):
        def set_theme_color(fill_obj):
            fill_obj.Visible = -1
            fill_obj.ForeColor.ObjectThemeColor = color_index
            fill_obj.ForeColor.Brightness = brightness
        cls.set_color_fill1(shapes, set_theme_color)

    @classmethod
    def set_color_fill_none1(cls, shapes):
        def set_none_color(fill_obj):
            fill_obj.Visible = 0
        cls.set_color_fill1(shapes, set_none_color)


    @classmethod
    def set_color_fill_rgb2(cls, shapes, color):
        def set_rgb_color(fill_obj):
            fill_obj.ForeColor.RGB = color
        cls.set_color_fill2(shapes, set_rgb_color)

    @classmethod
    def set_color_fill_theme2(cls, shapes, color_index, brightness):
        def set_theme_color(fill_obj):
            fill_obj.ForeColor.ObjectThemeColor = color_index
            fill_obj.ForeColor.Brightness = brightness
        cls.set_color_fill2(shapes, set_theme_color)


    @classmethod
    def set_color_line_rgb(cls, shapes, color):
        def set_rgb_color(line_obj):
            line_obj.ForeColor.RGB = color
        cls.set_color_line(shapes, set_rgb_color)

    @classmethod
    def set_color_line_theme(cls, shapes, color_index, brightness):
        def set_theme_color(line_obj):
            line_obj.ForeColor.ObjectThemeColor = color_index
            line_obj.ForeColor.Brightness = brightness
        cls.set_color_line(shapes, set_theme_color)

    @classmethod
    def set_color_line(cls, shapes, color_setter):
        for shape in shapes:
            ref_color = None
            for s in shape.GroupItems:
                if ref_color is None:
                    if s.Line.visible == -1:
                        ref_color = s.Line.ForeColor.RGB
                    else:
                        continue
                if s.Line.visible == -1 and s.Line.ForeColor.RGB == ref_color:
                    color_setter(s.Line)


    @staticmethod
    def show_help():
        #TODO
        bkt.message("TODO: show help file, image, or something...")


class LikertScale(bkt.ribbon.Gallery):
    spacing = 5
    size = 20
    #for gallery only:
    color_line = 0
    color_filled = 14540253
    color_empty = 16777215

    likert_sizes = [3,4,5]
    likert_columns = len(likert_sizes)
    likert_shapes = {1: "Quadratisch", 9: "Kreisförmig", 92: "Sternförmig"} #rectangle, oval, star
    likert_buttons = [
        [n,m]
        for n in likert_shapes.keys()
        for m in likert_sizes
    ]
    
    def __init__(self, **kwargs):
        # parent_id = kwargs.get('id') or ""
        my_kwargs = dict(
            label = 'Likert-Scale',
            image = 'likert',
            columns = self.likert_columns,
            screentip="Likert-Scale als Wechselshape einfügen",
            supertip="Eine Likert-Scale als Wechselshape einfügen. Über die Wechselshape-Funktionen kann der Füllstand, sowie die Farben verändert werden.",
            item_width=5*16,
            item_height=16,
        )
        my_kwargs.update(kwargs)

        super(LikertScale, self).__init__(**my_kwargs)

    @classmethod
    def get_item_count(cls):
        return len(cls.likert_buttons)

    @classmethod
    def get_item_screentip(cls, index):
        return "%sen %ser-Likert-Scale einfügen" % (cls.likert_shapes[cls.likert_buttons[index][0]], cls.likert_buttons[index][1])

    @classmethod
    def get_item_image(cls, index):
        return LikertScale.get_likert_image( count=cls.likert_buttons[index][1], shape=cls.likert_buttons[index][0] )

    @classmethod
    def on_action_indexed(cls, selected_item, index, slide):
        cls._create_stateshape_scale(slide, cls.likert_buttons[index][0], cls.likert_buttons[index][1]),

    @staticmethod
    def get_likert_image(size_factor=2, count=3, shape=1):
        img = Drawing.Bitmap(5*16*size_factor, 16*size_factor)
        color_black = Drawing.ColorTranslator.FromOle(0)
        color_grey  = Drawing.ColorTranslator.FromOle(14540253)
        color_white = Drawing.ColorTranslator.FromOle(16777215)
        g = Drawing.Graphics.FromImage(img)
        
        #Draw smooth rectangle/ellipse
        g.SmoothingMode = Drawing.Drawing2D.SmoothingMode.AntiAlias

        pen    = Drawing.Pen(color_black,1*size_factor)
        brush1 = Drawing.SolidBrush(color_grey)
        brush2 = Drawing.SolidBrush(color_white)
        star_points = [(0,6),(5,8),(5,12),(8,9),(12,10),(10,6),(12,2),(8,3),(5,0),(5,4)]
        
        left = 2
        for i in range(count):
            brush = brush2 if i>0 else brush1
            if shape == 92: #star
                points = Array[Drawing.Point]([Drawing.Point(left+l*size_factor,t*size_factor) for t,l in star_points])
                g.FillPolygon(brush, points)
                g.DrawPolygon(pen, points)
            elif shape == 9: #oval
                g.FillEllipse(brush, left, 2, 12*size_factor, 12*size_factor) #left, top, width, height
                g.DrawEllipse(pen, left, 2, 12*size_factor, 12*size_factor) #left, top, width, height
            else: #fallback shape=1 rectangle
                g.FillRectangle(brush, left, 2, 12*size_factor, 12*size_factor) #left, top, width, height
                g.DrawRectangle(pen, left, 2, 12*size_factor, 12*size_factor) #left, top, width, height
            left += 16*size_factor
        return img

    @classmethod
    def _create_single_scale(cls, slide, shape_type=1, state=0, total=3, visible=0):
        # shapecount = slide.Shapes.Count
        left = 90
        for i in range(total):
            left += cls.size + cls.spacing
            s = slide.Shapes.AddShape( shape_type, left, 100, cls.size, cls.size )
            # s.Line.Weight = 0.75
            # s.Line.ForeColor.RGB = cls.color_line
            s.Line.Visible = -1
            s.Line.ForeColor.ObjectThemeColor = 13 #msoThemeColorText1
            s.Fill.Visible = -1
            if i < state:
                # s.Fill.ForeColor.RGB = cls.color_filled
                s.Fill.ForeColor.ObjectThemeColor = 16 #msoThemeColorBackground2
            else:
                # s.Fill.ForeColor.RGB = cls.color_empty
                s.Fill.ForeColor.ObjectThemeColor = 14 #msoThemeColorBackground1

        # grp = slide.Shapes.Range(Array[int](range(shapecount+1, shapecount+1+total))).group()
        grp = pplib.last_n_shapes_on_slide(slide, total).group()
        grp.Visible = visible
        return grp

    @classmethod
    def _create_stateshape_scale(cls, slide, shape_type, total):
        shapecount = slide.Shapes.Count
        for i in range(total+1):
            cls._create_single_scale(slide, shape_type, i, total)
        
        slide.Shapes.Range(shapecount+1).visible = -1 #make first visible
        # grp = slide.Shapes.Range(Array[int](range(shapecount+1, shapecount+1+total+1))).group()
        grp = pplib.last_n_shapes_on_slide(slide, total+1).group()
        grp.LockAspectRatio = -1
        grp.Tags.Add(bkt.contextdialogs.BKT_CONTEXTDIALOG_TAGKEY, StateShape.BKT_DIALOG_TAG)
        grp.select()



class CheckBox(object):
    size = 20

    @classmethod
    def insert_checkbox(cls, slide):
        cls._insert_single_box(slide)
        cls._insert_single_box(slide, u'\x6c')
        cls._insert_single_box(slide, u'\x6e')
        cls._insert_single_box(slide, u'\xfb')
        cls._insert_single_box(slide, u'\xfc', True)
        grp = pplib.last_n_shapes_on_slide(slide, 5).group()
        grp.LockAspectRatio = -1
        grp.Tags.Add(bkt.contextdialogs.BKT_CONTEXTDIALOG_TAGKEY, StateShape.BKT_DIALOG_TAG)
        grp.select()
    
    @classmethod
    def _insert_single_box(cls, slide, char=None, visible=False):
        s = slide.Shapes.AddShape( 1, 100, 100, cls.size, cls.size )
        s.Line.Visible = -1
        s.Line.ForeColor.ObjectThemeColor = 13 #msoThemeColorText1
        s.Fill.ForeColor.ObjectThemeColor = 14 #msoThemeColorBackground1
        s.Fill.Visible = -1
        s.LockAspectRatio = -1

        textframe = s.TextFrame2
        textframe.AutoSize     = 0
        textframe.MarginBottom = 0
        textframe.MarginLeft   = 0
        textframe.MarginRight  = 0
        textframe.MarginTop    = 0
        textframe.HorizontalAnchor = 2
        textframe.VerticalAnchor   = 3

        textrange = textframe.TextRange
        textrange.Font.Bold   = 0
        textrange.Font.Italic = 0
        textrange.Font.Size   = cls.size-2
        textrange.Font.Fill.ForeColor.ObjectThemeColor = 13 #msoThemeColorText1

        if char:
            textrange.InsertSymbol("Wingdings", ord(char)) #symbol: FontName, CharNumber (decimal)
        s.Visible = visible
        return s



likert_button = LikertScale(id="likert_insert")


stateshape_gruppe = bkt.ribbon.Group(
    id="bkt_stateshape_group",
    label='Wechsel-Shapes',
    image_mso='GroupSmartArtQuickStyles',
    children = [
        bkt.ribbon.SplitButton(
            id="stateshape_convert_splitbutton",
            size="large",
            children=[
                bkt.ribbon.Button(
                    id="stateshape_convert",
                    label=u"Konvertieren",
                    image_mso='GroupSmartArtQuickStyles',
                    screentip="Gruppierte Shapes in ein Wechselshape konvertieren",
                    supertip="Bei gruppierten Shapes (Wechsel-Shapes) kann zwischen den Shapes innerhalb der Gruppe gewechselt werden, d.h. es ist immer nur ein Shape der Gruppe sichtbar. Dies ist bspw. nützlich für Ampeln, Skalen, etc.",
                    on_action=bkt.Callback(StateShape.convert_to_state_shape),
                    get_enabled=bkt.Callback(StateShape.is_convertable_to_state_shape),
                ),
                bkt.ribbon.Menu(
                    label="Wechselshapes-Menü",
                    supertip="In Wechselshapes konvertieren oder wieder alle Shapes sichtbar machen",
                    children=[
                        bkt.ribbon.Button(
                            id="stateshape_convert2",
                            label=u"In Wechselshape konvertieren",
                            image_mso='GroupSmartArtQuickStyles',
                            screentip="Gruppierte Shapes in ein Wechselshape konvertieren",
                            supertip="Bei gruppierten Shapes (Wechsel-Shapes) kann zwischen den Shapes innerhalb der Gruppe gewechselt werden, d.h. es ist immer nur ein Shape der Gruppe sichtbar. Dies ist bspw. nützlich für Ampeln, Skalen, etc.",
                            on_action=bkt.Callback(StateShape.convert_to_state_shape),
                            get_enabled=bkt.Callback(StateShape.is_convertable_to_state_shape),
                        ),
                        bkt.ribbon.MenuSeparator(),
                        # bkt.ribbon.ToggleButton(
                        bkt.ribbon.Button(
                            id="stateshape_show_all",
                            label=u"Alle Shapes wieder anzeigen",
                            screentip="Alle Shapes sichtbar machen",
                            supertip="Mit diesem Button können die Shapes innerhalb der Wechselshape-Gruppe eingeblendet werden.",
                            # image_mso='GroupSmartArtQuickStyles',
                            # get_pressed=bkt.Callback(StateShape.get_show_all),
                            # on_toggle_action=bkt.Callback(StateShape.toggle_show_all),
                            on_action=bkt.Callback(StateShape.show_all),
                            get_enabled=bkt.Callback(StateShape.is_state_shape),
                        ),
                    ]
                )
            ]
        ),
        bkt.ribbon.Separator(),
        # bkt.ribbon.LabelControl(label="Wechsel: "),
        bkt.ribbon.Box(box_style="horizontal", children=[
            bkt.ribbon.Button(
                id="stateshape_reset",
                image_mso="Undo",
                label=u"Zurücksetzen",
                show_label=False,
                screentip="Auf erstes Shape zurücksetzen",
                supertip="Setzt alle Wechsel-Shapes auf den ersten Status, d.h. das erste Shape der Gruppe zurück.",
                on_action=bkt.Callback(StateShape.reset_state),
                get_enabled=bkt.Callback(StateShape.are_state_shapes),
            ),
            bkt.ribbon.Button(
                id="stateshape_prev",
                image_mso="PreviousResource",
                label=u'Vorheriges',
                show_label=False,
                screentip="Vorheriges Shape",
                supertip="Wechselt zum vorherigen Status (d.h. Shape in der Gruppe) des Wechsel-Shapes.",
                on_action=bkt.Callback(StateShape.previous_state),
                get_enabled=bkt.Callback(StateShape.are_state_shapes),
            ),
            # bkt.ribbon.EditBox(
            #     id="stateshape_set",
            #     label="Position",
            #     show_label=False,
            #     size_string="#",
            #     on_change=bkt.Callback(StateShape.set_state),
            #     get_enabled=bkt.Callback(StateShape.are_state_shapes),
            #     get_text=bkt.Callback(lambda: None),
            # ),
            bkt.ribbon.Button(
                id="stateshape_next",
                image_mso="NextResource",
                label=u"Nächstes",
                # show_label=False,
                screentip="Nächstes Shape",
                supertip="Wechselt zum nächsten Status (d.h. Shape in der Gruppe) des Wechsel-Shapes.",
                on_action=bkt.Callback(StateShape.next_state),
                get_enabled=bkt.Callback(StateShape.are_state_shapes),
            )
        ]),
        bkt.ribbon.Menu(
            id="stateshape_color_menu",
            label="Farbe ändern",
            supertip="Die Farben von Wechselshapes anpassen",
            image_mso="RecolorColorPicker",
            children=[
                bkt.ribbon.ColorGallery(
                    id="stateshape_color_fill1",
                    label = 'Farbe 1 (Hintergrund) ändern',
                    image_mso = 'ShapeFillColorPicker',
                    screentip="Hintergrundfarbe eines Wechsel-Shapes ändern",
                    supertip="Passt die Hintergrundfarbe aller Shapes im Wechsel-Shape an. Die Hintergrundfarbe ist die Farbe des zuerst gefundenen Shapes.",
                    on_rgb_color_change   = bkt.Callback(StateShape.set_color_fill_rgb1, shapes=True),
                    on_theme_color_change = bkt.Callback(StateShape.set_color_fill_theme1, shapes=True),
                    # get_selected_color    = bkt.Callback(StateShape.get_selected_color1, shapes=True),
                    get_enabled           = bkt.Callback(StateShape.are_state_shapes),
                    children=[
                        bkt.ribbon.Button(
                            label="Kein Hintergrund",
                            supertip="Wechsel-Shape Hintergrundfarbe auf transparent setzen",
                            on_action=bkt.Callback(StateShape.set_color_fill_none1, shapes=True),
                        ),
                    ]
                ),
                bkt.ribbon.ColorGallery(
                    id="stateshape_color_fill2",
                    label = 'Farbe 2 (Vordergrund) ändern',
                    image_mso = 'ShapeFillColorPicker',
                    screentip="Vordergrundfarbe eines Wechsel-Shapes ändern",
                    supertip="Passt die Vordergrundfarbe aller Shapes im Wechsel-Shape an. Die Vordergrundfarbe ist jede Farbe ungleich der Hintergrundfarbe.",
                    on_rgb_color_change   = bkt.Callback(StateShape.set_color_fill_rgb2, shapes=True),
                    on_theme_color_change = bkt.Callback(StateShape.set_color_fill_theme2, shapes=True),
                    # get_selected_color    = bkt.Callback(StateShape.get_selected_color2, shapes=True),
                    get_enabled           = bkt.Callback(StateShape.are_state_shapes),
                ),
                bkt.ribbon.ColorGallery(
                    id="stateshape_color_line",
                    label = 'Linie ändern',
                    image_mso = 'ShapeOutlineColorPicker',
                    screentip="Linie eines Wechsel-Shapes ändern",
                    supertip="Passt die Linienfarbe aller Shapes im Wechsel-Shape an, die der ersten gefundenen Linienfarbe entsprechen.",
                    on_rgb_color_change   = bkt.Callback(StateShape.set_color_line_rgb, shapes=True),
                    on_theme_color_change = bkt.Callback(StateShape.set_color_line_theme, shapes=True),
                    # get_selected_color    = bkt.Callback(StateShape.get_selected_line, shapes=True),
                    get_enabled           = bkt.Callback(StateShape.are_state_shapes),
                ),
            ]
        ),
        # bkt.ribbon.Button(
        #     id="stateshape_help",
        #     image_mso="Help",
        #     label=u"Anleitung",
        #     on_action=bkt.Callback(StateShape.show_help),
        #     # get_enabled=bkt.Callback(StateShape.are_state_shapes),
        # ),
        # likert_button,
    ]
)