# -*- coding: utf-8 -*-
'''
Created on 2018-05-29
@author: Florian Stallmann
'''

import bkt
import bkt.library.powerpoint as pplib

import logging
import traceback

import os
import io
import json
import uuid

from collections import OrderedDict

D = bkt.dotnet.import_drawing()

from helpers import ShapeFormats #local helper functions


CF_VERSION = "20190613"

class CustomFormat(object):
    '''
    This class represents a single custom format (button in gallery) with all style definitions. It has
    helper function to save and load from json file as well as pickup and apply from/to shape.
    '''
    default_settings = OrderedDict([
        ('Type',              False),
        ('Fill',              True),
        ('Line',              True),
        ('TextFrame',         True),
        ('ParagraphFormat',   True), #per indent level
        ('Font',              True), #per indent level
        ('Size',              False),
        ('Position',          False),

        ('Shadow',            True),
        ('Glow',              True),
        ('SoftEdge',          True),
        ('Reflection',        True),
    ])

    def __init__(self, name, style_setting=None, button_setting=None):
        self.name = name

        settings = CustomFormat.default_settings.copy()
        if style_setting:
            settings.update(style_setting)
        self.style_setting = settings
        
        button = {
            'font': None,
            'fill': None,
            'line': None
        }
        if button_setting:
            button.update(button_setting)
        self.button_setting = button
        
        self.thumbnail_name = None #filename of the thumbnail
        self.design_name = None #name of Master-Design
        self._formats = OrderedDict()


    def add_format(self, name, formats):
        if name not in self.style_setting:
            raise KeyError("Unknown format type")
        self._formats[name] = formats
    
    def get_format(self, name):
        return self._formats[name]
    
    def is_format(self, name):
        return self.style_setting.get(name, False) and name in self._formats


    def to_json(self):
        result = OrderedDict()
        result["name"]           = self.name
        result["style_setting"]  = self.style_setting
        result["button_setting"] = self.button_setting
        result["thumbnail_name"] = self.thumbnail_name
        result["design_name"]    = self.design_name
        result["formats"]        = self._formats
        return result

    @staticmethod
    def from_json(value): #filename+index required for converting older format definitions
        result = CustomFormat(value["name"], value["style_setting"], value["button_setting"])
        result.thumbnail_name = value.get("thumbnail_name", None)
        result.design_name    = value.get("design_name", None)
        for k,v in value["formats"].items():
            result.add_format(k,v)
        return result


    @staticmethod
    def from_shape(shape, style_setting=None):
        ### BUTTON SETTINGS
        button_setting = {}
        if shape.Fill.Visible == -1:
            button_setting['fill'] = shape.Fill.ForeColor.RGB
        if shape.Line.Visible == -1:
            button_setting['line'] = shape.Line.ForeColor.RGB
        if shape.HasTextFrame == -1:
            textrange = shape.TextFrame2.TextRange
            try:
                font_fill = textrange.Characters(1).Font.Fill
            except:
                font_fill = textrange.Font.Fill
            if font_fill.Visible == -1:
                button_setting['font'] = textrange.Font.Fill.ForeColor.RGB
        
        ### CUSTOM FORMAT CREATION
        result = CustomFormat(shape.name, style_setting, button_setting)
        result.design_name = shape.Parent.Design.Name

        ### TYPE
        result.add_format('Type', ShapeFormats._get_type(shape) )
        
        ### BACKGROUND
        result.add_format('Fill', ShapeFormats._get_fill(shape.Fill) )

        ### LINE
        result.add_format('Line', ShapeFormats._get_line(shape.Line) )

        ### TEXTFRAME
        if shape.HasTextFrame == -1:
            result.add_format('TextFrame', ShapeFormats._get_textframe(shape.TextFrame2) )

        ### INDENT LEVEL SPECIFIC FORMATS (PARAGRAPH, FONT)
        if shape.HasTextFrame == -1:
            result.add_format("ParagraphFormat", ShapeFormats._get_indentlevels(shape.TextFrame2, "paragraph") )
            result.add_format("Font", ShapeFormats._get_indentlevels(shape.TextFrame2, "font") )

        ### SHADOW
        result.add_format('Shadow', ShapeFormats._get_shadow(shape.Shadow) )
        result.add_format('Glow', ShapeFormats._get_glow(shape.Glow) )
        result.add_format('SoftEdge', ShapeFormats._get_softedge(shape.SoftEdge) )
        result.add_format('Reflection', ShapeFormats._get_reflection(shape.Reflection) )

        #TODO: Add ThreeD, AnimationSettings

        ### SIZE
        result.add_format('Size', ShapeFormats._get_size(shape) )
        
        ### POSITION
        result.add_format('Position', ShapeFormats._get_position(shape) )

        return result


    def to_shape(self, shape, shape_is_new=False):
        try:
            if self.is_format("Type") or shape_is_new:
                ShapeFormats._set_type(shape, self.get_format("Type"))
        except Exception as e:
            logging.error("Custom formats: Error in setting shape type with error: {}".format(e))

        try:
            if self.is_format("Fill"):
                ShapeFormats._set_fill(shape.fill, self.get_format("Fill"))
        except Exception as e:
            logging.error("Custom formats: Error in setting fill with error: {}".format(e))

        try:
            if self.is_format("Line"):
                ShapeFormats._set_line(shape.line, self.get_format("Line"))
        except Exception as e:
            logging.error("Custom formats: Error in setting line with error: {}".format(e))

        try:
            if self.is_format("TextFrame"):
                ShapeFormats._set_textframe(shape.textframe2, self.get_format("TextFrame"))
        except Exception as e:
            logging.error("Custom formats: Error in setting textframe with error: {}".format(e))

        try:
            # order is important here. shadow must be last as setting glow, reflection or softedge will re-enable shadow
            if self.is_format("Glow"):
                ShapeFormats._set_glow(shape.glow, self.get_format("Glow"))
            if self.is_format("Reflection"):
                ShapeFormats._set_reflection(shape.reflection, self.get_format("Reflection"))
            if self.is_format("SoftEdge"):
                ShapeFormats._set_softedge(shape.softedge, self.get_format("SoftEdge"))
            if self.is_format("Shadow"):
                ShapeFormats._set_shadow(shape.shadow, self.get_format("Shadow"))
        except Exception as e:
            logging.error("Custom formats: Error in setting effects with error: {}".format(e))

        try:
            if self.is_format("Size") or shape_is_new:
                ShapeFormats._set_size(shape, self.get_format("Size"))
        except Exception as e:
            logging.error("Custom formats: Error in setting shape size with error: {}".format(e))

        try:
            if self.is_format("Position") or shape_is_new:
                ShapeFormats._set_position(shape, self.get_format("Position"))
        except Exception as e:
            logging.error("Custom formats: Error in setting shape position with error: {}".format(e))

        try:
            if self.is_format("ParagraphFormat"):
                ShapeFormats._set_indentlevels(shape.TextFrame2, "paragraph", self.get_format("ParagraphFormat"))
        except Exception as e:
            logging.error("Custom formats: Error in setting paragraph format with error: {}".format(e))

        try:
            if self.is_format("Font"):
                ShapeFormats._set_indentlevels(shape.TextFrame2, "font", self.get_format("Font"))
        except Exception as e:
            logging.error("Custom formats: Error in setting font with error: {}".format(e))


class CustomFormatCatalog(object):
    '''
    This class handles the currently active custom format catalog incl. saving and loading catalog files. It also has
    helper functions to generate the thumbnail images and provide data to the gallery.
    '''

    custom_styles = []
    
    config_folder = os.path.join(bkt.helpers.get_fav_folder(), "custom_formats")
    current_file = bkt.settings.get("customformats.default_file", "styles.json")
    initialized = False


    @classmethod
    def _initialize(cls):
        if cls.initialized:
            return
        
        cls.read_from_config(cls.current_file)
        cls.initialized = True

    @classmethod
    def create_new_config(cls, filename):
        file = os.path.join(cls.config_folder, filename)
        if os.path.exists(file):
            raise FileExistsError("file already exists")
        
        cls.current_file = filename
        cls.custom_styles = []
        cls.save_to_config()
        bkt.settings["customformats.default_file"] = filename

    @classmethod
    def save_to_config(cls):
        # bkt.console.show_message("%r" % cls.custom_styles)
        # bkt.console.show_message(json.dumps(cls.custom_styles))
        file = os.path.join(cls.config_folder, cls.current_file)
        if not os.path.exists(cls.config_folder):
            os.makedirs(cls.config_folder)
        
        with io.open(file, 'w') as json_file:
            catalog = OrderedDict()
            catalog["version"] = CF_VERSION
            catalog["filename"] = cls.current_file
            catalog["styles"] = [style.to_json() for style in cls.custom_styles]
            json.dump(catalog, json_file)

    @classmethod
    def read_from_config(cls, filename="styles.json"):
        file = os.path.join(cls.config_folder, filename)
        if not os.path.isfile(file):
            return
        with io.open(file, 'r') as json_file:
            catalog = json.load(json_file, object_pairs_hook=OrderedDict)
            
            if not isinstance(catalog, OrderedDict) or catalog.get("version", 0) != CF_VERSION:
                raise Exception("migration needed") #TODO
            elif catalog.get("filename", "") != filename:
                raise ValueError("catalog file has been renamed")
            
            cls.custom_styles = []
            for style in catalog["styles"]:
                cls.custom_styles.append(CustomFormat.from_json(style))
            # data = json.load(json_file, object_pairs_hook=OrderedDict)
            # bkt.console.show_message("%r" % data)
        cls.current_file = filename
        bkt.settings["customformats.default_file"] = filename


    @classmethod
    def get_custom_style_name(cls, index):
        return cls.custom_styles[index].name

    @classmethod
    def pickup_custom_style(cls, shape, style_setting=None):
        cls.custom_styles.append(CustomFormat.from_shape(shape, style_setting))
        cls._generate_thumbnail_image(len(cls.custom_styles)-1, shape)
        cls.save_to_config()

    @classmethod
    def edit_custom_style(cls, index, style_setting):
        cls.custom_styles[index].style_setting.update(style_setting)
        cls.save_to_config()

    @classmethod
    def delete_custom_style(cls, index):
        file = cls._get_image_filename(index)
        try:
            os.remove(file)
        except OSError:
            pass
        del cls.custom_styles[index]
        cls.save_to_config()


    ### Functions for gallery ###

    @classmethod
    def get_count(cls):
        cls._initialize() #get count is sufficient for initialization as it is always called first
        return len(cls.custom_styles)

    @classmethod
    def get_label(cls, index):
        return "Style {}".format(cls.custom_styles[index].name)

    @classmethod
    def get_screentip(cls, index):
        return "Style {} anwenden".format(cls.custom_styles[index].name)

    @classmethod
    def get_supertip(cls, index):
        default = "Diesen Style auf aktuelle Auswahl anwenden.{}\n\nMit SHIFT-Taste: Neues Shape im gewählten Format anlegen."
        styles = "\n" + "\n".join( ["{}: {}".format(k, "ja" if v else "nein") for k,v in cls.custom_styles[index].style_setting.items()] )
        return default.format(styles)

    @classmethod
    def get_image(cls, index):
        file = cls._get_image_filename(index)

        if os.path.exists(file):
            #version that should not lock the file, which prevents updating of thumbnails:
            with D.Bitmap.FromFile(file) as img:
                thumbnail = D.Bitmap(img)
                img.Dispose()
            return thumbnail
        
        # black image
        # settings = [0, None, None, "X"]
        # return cls.generate_image(size, *settings)
        raise FileNotFoundError("image file not found")


    ### Helpers for image generation ###

    @classmethod
    def _get_image_filename(cls, index):
        if not cls.custom_styles[index].thumbnail_name:
            cls.custom_styles[index].thumbnail_name = "{}_{}.png".format( index+1, uuid.uuid4().hex ) #use uuid to avoid same filenames (e.g. index can change if styles are deleted)
        
        return os.path.join( cls.config_folder, "{}_thumbs".format(os.path.splitext(cls.current_file)[0]), cls.custom_styles[index].thumbnail_name )

    @classmethod
    def _generate_thumbnail_image(cls, index, shape, size=64):
        filename = cls._get_image_filename(index)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        shape.Export(filename, 2) #2=ppShapeFormatPNG, width, height, export-mode: 1=ppRelativeToSlide, 2=ppClipRelativeToSlide, 3=ppScaleToFit, 4=ppScaleXY

        # resize thumbnail image to square
        if os.path.exists(filename):
            try:
                # init croped image
                width = size
                height = size
                image = D.Bitmap(filename)
                bmp = D.Bitmap(width, height)
                graph = D.Graphics.FromImage(bmp)
                # compute scale
                scale = min(float(width) / image.Width, float(height) / image.Height)
                scaleWidth = int(image.Width * scale)
                scaleHeight = int(image.Height * scale)
                # set quality
                graph.InterpolationMode  = D.Drawing2D.InterpolationMode.High
                graph.CompositingQuality = D.Drawing2D.CompositingQuality.HighQuality
                graph.SmoothingMode      = D.Drawing2D.SmoothingMode.AntiAlias
                # redraw and save
                # logging.debug('crop image from %sx%s to %sx%s. rect %s.%s-%sx%s' % (image.Width, image.Height, width, height, int((width - scaleWidth)/2), int((height - scaleHeight)/2), scaleWidth, scaleHeight))
                graph.DrawImage(image, D.Rectangle(int((width - scaleWidth)/2), int((height - scaleHeight)/2), scaleWidth, scaleHeight))

                # close and save files
                image.Dispose()
                bmp.Save(filename)
                bmp.Dispose()
            except:
                logging.error('Creation of croped thumbnail image failed: %s' % filename)
                logging.debug(traceback.format_exc())
            finally:
                if image:
                    image.Dispose()
                if bmp:
                    bmp.Dispose()
        else:
            raise FileNotFoundError("thumbnail image not found")
        
        return filename


### TODO: import styles from presentation, replace existing QuickStyleGallery, replace existing pickup-apply buttons, re-generate thumbnail images for each design ###


class CustomQuickEdit(object):
    '''
    This class orchestrates all custom format functions for the UI and redirects calls to the catalog of custom format.
    '''

    always_keep_theme_color = True #set to true to remain theme color even if RGB value differs due to different color scheme
    always_consider_indentlevels = True #set to true to save paragraphformat and font individually for each indent level

    temp_custom_format = None #temporary custom format, used for advanced pickup-apply stamp


    ### Catalog menu ###

    @staticmethod
    def create_new_style(filename=None):
        import time
        if not filename:
            filename = bkt.ui.show_user_input("Bitte Dateiname für neuen Style-Katalog eingeben", "Dateiname eingeben", "styles_"+time.strftime("%Y%m%d%H%M"))
            if filename is None:
                return
        if not filename.endswith(".json"):
            filename += ".json"

        try:
            CustomFormatCatalog.create_new_config(filename)
        except FileExistsError:
            bkt.helpers.message("Dateiname existiert bereits")


    @staticmethod
    def get_styles():
        def style_button(file):
            return bkt.ribbon.ToggleButton(
                label= file,
                screentip="Lade "+file,
                supertip="Lade Custom-Styles aus dieser Katalog-Datei.",
                get_pressed=bkt.Callback(lambda: file == CustomFormatCatalog.current_file),
                on_toggle_action=bkt.Callback(lambda pressed: CustomFormatCatalog.read_from_config(file))
            )

        def style_list(folder):
            if os.path.exists(folder):
                return os.listdir(CustomFormatCatalog.config_folder)
            else:
                return []

        return bkt.ribbon.Menu(
            xmlns="http://schemas.microsoft.com/office/2009/07/customui",
            id=None,
            children=[
                bkt.ribbon.MenuSeparator(title="Style-Kataloge verwalten"),
            ] + [
                style_button(file)
                for file in style_list(CustomFormatCatalog.config_folder) if file.endswith(".json")
            ] + [
                bkt.ribbon.MenuSeparator(),
                bkt.ribbon.Button(
                    label='Neuen Style-Katalog anlegen',
                    supertip="Neuen Katalog mit definierbarem Namen anlegen.",
                    # image_mso='ModuleInsert',
                    on_action=bkt.Callback(CustomQuickEdit.create_new_style)
                ),
            ]
        )


    ### Gallery funcions ###

    @classmethod
    def show_pickup_window(cls, shape):
        from pickup_style import PickupWindow
        PickupWindow.create_and_show_dialog(CustomFormatCatalog, CustomFormat.default_settings, shape=shape)

    @classmethod
    def show_edit_window(cls, index):
        from pickup_style import PickupWindow
        PickupWindow.create_and_show_dialog(CustomFormatCatalog, CustomFormatCatalog.custom_styles[index].style_setting, index=index)


    @staticmethod
    def _create_shape(context):
        left = (context.presentation.PageSetup.SlideWidth-50)*0.5
        top  = (context.presentation.PageSetup.SlideHeight-50)*0.5
        shp  = context.slide.Shapes.AddShape(1, left, top, 50, 50)
        shp.select()

        #for new shapes always consider type, size and position
        # cls._apply_custom_style_on_shape(shp, cls.custom_styles[index], {'type': True, 'size': True, 'position': True})

        return shp

    @classmethod
    def apply_custom_style(cls, index, context):
        shift = bkt.library.system.get_key_state(bkt.library.system.key_code.SHIFT)
        ctrl  = bkt.library.system.get_key_state(bkt.library.system.key_code.CTRL)
        # alt   = bkt.library.system.get_key_state(bkt.library.system.key_code.ALT)

        if ctrl:
            cls.show_edit_window(index)
        
        else:
            ### APPLY STYLE ###

            ShapeFormats.always_keep_theme_color = cls.always_keep_theme_color
            ShapeFormats.always_consider_indentlevels = cls.always_consider_indentlevels

            if shift or context.selection.Type not in [2,3]:
                #create new shape with this style
                shape = cls._create_shape(context)
                CustomFormatCatalog.custom_styles[index].to_shape(shape, shape_is_new=True)
            else:
                for shape in context.shapes:
                    CustomFormatCatalog.custom_styles[index].to_shape(shape)


    ### Advanced pickup-apply stamp ###

    @classmethod
    def temp_enabled(cls, selection):
        return cls.temp_custom_format is not None and (selection.Type == 2 or selection.Type == 3)

    @classmethod
    def temp_pickup(cls, shape):
        cls.temp_custom_format = CustomFormat.from_shape(shape)

    @classmethod
    def temp_apply(cls, shapes):
        from pickup_style import PickupWindow
        wnd = PickupWindow.create_and_show_dialog(cls, cls.temp_custom_format.style_setting)
        
        if wnd.result:
            cls.temp_custom_format.style_setting.update(wnd.result)
            for shape in shapes:
                cls.temp_custom_format.to_shape(shape)


class FormatLibGallery(bkt.ribbon.Gallery):
    '''
    This is the gallery element to show custom format styles.
    '''
    
    def __init__(self, **kwargs):
        parent_id = kwargs.get('id') or ""
        my_kwargs = dict(
            label = 'Styles anzeigen',
            columns = 6,
            image_mso = 'ShapeQuickStylesHome',
            show_item_label=False,
            screentip="Custom-Styles Gallerie",
            supertip="Zeigt Übersicht über alle Custom-Styles im aktuellen Katalog.",
            children=[
                bkt.ribbon.Button(id=parent_id + "_pickup", label="Neuen Style aufnehmen", supertip="Nimmt Format vom gewählten Shape neu in die Gallerie auf.", image_mso="PickUpStyle", on_action=bkt.Callback(CustomQuickEdit.show_pickup_window, shape=True), get_enabled = bkt.apps.ppt_shapes_exactly1_selected,),
                bkt.ribbon.Button(id=parent_id + "_help1", label="[STRG]+Klick für Bearbeiten und Löschen", supertip="Bei Klick auf ein Custom-Style mit gedrückter STRG-Taste öffnet sich ein Fenster zur Bearbeitung und Löschung dieses Styles.", enabled = False),
                bkt.ribbon.Button(id=parent_id + "_help2", label="[SHIFT]+Klick für Anlage neues Shape", supertip="Bei Klick auf ein Custom-Style mit gedrückter SHIFT-Taste wird immer ein neues Shapes in gewähltem Style angelegt.", enabled = False),
            ]
        )
        my_kwargs.update(kwargs)

        super(FormatLibGallery, self).__init__(**my_kwargs)

    def on_action_indexed(self, selected_item, index, context):
        CustomQuickEdit.apply_custom_style(index, context)
    
    def get_item_count(self):
        return CustomFormatCatalog.get_count()
        
    def get_item_label(self, index):
        return CustomFormatCatalog.get_label(index)
    
    def get_item_screentip(self, index):
        return CustomFormatCatalog.get_screentip(index)
        
    def get_item_supertip(self, index):
        return CustomFormatCatalog.get_supertip(index)
    
    def get_item_image(self, index):
        return CustomFormatCatalog.get_image(index)


customformats_group = bkt.ribbon.Group(
    id="bkt_customformats_group",
    label='Styles',
    image_mso='SmartArtChangeColorsGallery',
    children = [
        FormatLibGallery(id="customformats_gallery", size="large"),
        bkt.ribbon.DynamicMenu(
            id="quickedit_config_menu",
            label="Styles konfiguration",
            supertip="Style-Katalog laden oder neuen Katalog anlegen.",
            image_mso="ShapeReports",
            show_label=False,
            # size="large",
            get_content = bkt.Callback(CustomQuickEdit.get_styles),
        ),
        bkt.ribbon.Button(
            id="quickedit_temp_apply",
            label='Format anwenden',
            image_mso='PasteApplyStyle',
            supertip="Ausgewählte Formate aus Zwischenspeicher auf selektierte Shapes anwenden.",
            show_label=False,
            on_action=bkt.Callback(CustomQuickEdit.temp_apply),
            get_enabled = bkt.Callback(CustomQuickEdit.temp_enabled),
        ),
        bkt.ribbon.Button(
            id="quickedit_temp_pickup",
            label='Format aufnehmen',
            image_mso='PickUpStyle',
            supertip="Format aus selektiertem Shape in Zwischenspeicher aufnehmen.",
            show_label=False,
            on_action=bkt.Callback(CustomQuickEdit.temp_pickup),
            get_enabled = bkt.apps.ppt_shapes_exactly1_selected,
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
        customformats_group,
    ]
), extend=True)
