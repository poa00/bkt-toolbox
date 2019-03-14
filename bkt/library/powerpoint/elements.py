# -*- coding: utf-8 -*-
'''
Created on 02.11.2017

@author: fstallmann
'''

import helpers as pplib

from bkt import apps, dotnet, CallbackTypes, Callback
Drawing = dotnet.import_drawing()

from bkt.ribbon import Button, Gallery, SymbolsGallery, RoundingSpinnerBox, Item



class TextframeSpinnerBox(RoundingSpinnerBox):
    ### Instance initialization
    attr = 'MarginTop'
    
    def __init__(self, **kwargs):
        '''
        attr examples: MarginTop, MarginBottom, MarginLeft, MarginRight
        '''
        #self.attr is automatically set through RibbonControl attribute handling
        self.fallback_value = 0
        
        my_kwargs = dict(
            size_string = '###',
            round_cm = True,
            convert = 'pt_to_cm',
            get_enabled = apps.ppt_selection_contains_textframe,
        )
        my_kwargs.update(kwargs)
        
        super(TextframeSpinnerBox, self).__init__(**my_kwargs)


    ### Spinner Box callbacks ###
    
    def get_text(self, shapes, selection):
        value = self.get_attr_from_shapes(shapes, selection)
        if value == None: #e.g. no textframe detected
            return None
        elif int(value) == -2147483648: #replace large negative number (values differ between selected items) with fallback value
            return self.fallback_value
        else:
            return value
        
    def on_change(self, shapes, selection, value):
        self.set_attr_for_shapes(shapes, selection, value)


    ### Getter Methods ###
    
    def get_attr_from_shapes(self, shapes, selection):
        '''
        Get attr for shapes
        '''
        for textframe in pplib.iterate_shape_textframes(shapes):
            return self.get_attr_from_textframe(textframe)

    def get_attr_from_textframe(self, textframe):
        return getattr(textframe, self.attr)

        
    ### Setter methods ###
    
    def set_attr_for_shapes(self, shapes, selection, value):
        '''
        Set attr for shapes
        '''
        value = max(0,value)

        for textframe in pplib.iterate_shape_textframes(shapes):
            self.set_attr_for_textframe(textframe, value)

    def set_attr_for_textframe(self, textframe, value):
        setattr(textframe, self.attr, value)




class ParagraphFormatSpinnerBox(RoundingSpinnerBox):
    ### Instance initialization
    attr = 'SpaceBefore'
    
    def __init__(self, **kwargs):
        '''
        attr examples: SpaceBefore, SpaceAfter, LeftIndent, FirstLineIndent, LineSpacing
        '''
        #self.attr is automatically set through RibbonControl attribute handling
        self.fallback_value = 0
        
        my_kwargs = dict(
            size_string = '-###',
            get_enabled = apps.ppt_selection_contains_textframe,
        )

        if self.attr in ["SpaceBefore", "SpaceAfter", "SpaceWithin"]:
            my_kwargs["round_pt"] = True
        else:
            my_kwargs["round_cm"] = True
            my_kwargs["convert"] = "pt_to_cm"
        
        if self.attr in ["LeftIndent", "FirstLineIndent"]:
            my_kwargs["big_step"]         = 0.25
            my_kwargs["small_step"]       = 0.125
            my_kwargs["rounding_factor"]  = 0.125

        my_kwargs.update(kwargs)
        
        super(ParagraphFormatSpinnerBox, self).__init__(**my_kwargs)


    ### Spinner Box callbacks ###
    
    def get_text(self, shapes, selection):
        value = self.get_attr_from_shapes(shapes, selection)
        if value == None: #e.g. no textframe detected
            return None
        elif int(value) == -2147483648: #replace large negative number (values differ between selected items) with fallback value
            return self.fallback_value
        else:
            return value
        
    def on_change(self, shapes, selection, value):
        self.set_attr_for_shapes(shapes, selection, value)


    ### Getter Methods ###
    
    def get_attr_from_shapes(self, shapes, selection):
        if selection.Type == 3:
            # text selected
            try:
                # produces error if no text is selected
                return self._get_attr(selection.TextRange2.Paragraphs(1,1).ParagraphFormat)
            except:
                try:
                    # produces error if there is no textrange, e.g. selection within a chart
                    return self._get_attr(selection.TextRange2.ParagraphFormat)
                except:
                    return None
        
        else:
            # shapes selected
            for textframe in pplib.iterate_shape_textframes(shapes):
                value = self.get_attr_from_textrange(textframe.TextRange)
                try:
                    if int(value) == -2147483648: #different values for each paragraph, so get value from first paragraph
                        value = self._get_attr(textframe.TextRange.Paragraphs(1,1).ParagraphFormat)
                except:
                    pass
                return value

    def get_attr_from_textrange(self, textrange):
        return self._get_attr(textrange.ParagraphFormat)

    def _get_attr(self, par_format):
        if self.attr in ["SpaceBefore", "SpaceAfter", "SpaceWithin"]:
            if (self.attr == "SpaceBefore" and par_format.LineRuleBefore == 0) or (self.attr == "SpaceAfter" and par_format.LineRuleAfter == 0) or (self.attr == "SpaceWithin" and par_format.LineRuleWithin == 0):
                self.huge_step = 10
                self.big_step = 3
                self.small_step = 1
                self.round_at = 0
            else:
                self.huge_step = 0.5
                self.big_step = 0.2
                self.small_step = 0.1
                self.round_at = 1

        return getattr(par_format, self.attr)


    ### Setter methods ###
    
    def set_attr_for_shapes(self, shapes, selection, value):
        if self.attr != "FirstLineIndent": #FirstLineIndent can be negative!
            value = max(0,value)

        if selection.Type == 3:
            # text selected
            self.set_attr_for_textrange(selection.TextRange2, value) #need to use TextRange2 as TextRange does not contain LeftIndent, etc.

        else:
            for textframe in pplib.iterate_shape_textframes(shapes):
                self.set_attr_for_textrange(textframe.TextRange, value)
    
    def set_attr_for_textrange(self, textrange, value): #using textrange instead of textframe!
        if self.attr == "SpaceBefore" and textrange.ParagraphFormat.LineRuleBefore == -2: #if values differ, set the same value as in the first paragraph
            textrange.ParagraphFormat.LineRuleBefore = textrange.Paragraphs(1,1).ParagraphFormat.LineRuleBefore
        if self.attr == "SpaceAfter" and textrange.ParagraphFormat.LineRuleAfter == -2: #if values differ, set the same value as in the first paragraph
            textrange.ParagraphFormat.LineRuleAfter = textrange.Paragraphs(1,1).ParagraphFormat.LineRuleAfter
        if self.attr == "SpaceWithin" and textrange.ParagraphFormat.LineRuleWithin == -2: #if values differ, set the same value as in the first paragraph
            textrange.ParagraphFormat.LineRuleWithin = textrange.Paragraphs(1,1).ParagraphFormat.LineRuleWithin
        
        setattr(textrange.ParagraphFormat, self.attr, value)




class PPTSymbolsGallery(SymbolsGallery):

    def on_action_indexed(self, selected_item, index, context, selection, **kwargs):
        ''' create numberd shape according of settings in clicked element '''
        item = self.symbols[index]
        if selection.Type == 3: #text selected
            selection.TextRange2.Text = "" #remove selected text first and then insert symbol
            self.insert_symbol_into_text(selection.TextRange2, item)
        elif selection.Type == 2: #shapes selected
            self.insert_symbol_into_shapes(pplib.get_shapes_from_selection(selection), item)
        else:
            self.create_symbol_shape(selection.SlideRange(1), item)
    
    def insert_symbol_into_text(self, textrange, item):
        char_inserted = textrange.InsertAfter(item[1]) #symbol text
        if item[0]:
            char_inserted.Font.Name = item[0] #font name
    
    def insert_symbol_into_shapes(self, shapes, item):
        #pplib.iterate_shape_textframes(shapes, lambda textframe: self.insert_symbol_into_text(textframe.TextRange, item))

        for textframe in pplib.iterate_shape_textframes(shapes):
            self.insert_symbol_into_text(textframe.TextRange, item)
        
        # for shape in shapes:
        #     if shape.HasTextFrame == -1:
        #         self.insert_symbol_into_text(shape.TextFrame2.TextRange, item)

    def create_symbol_shape(self, slide, item):
        shape = slide.shapes.addTextbox(
            #office.MsoAutoShapeType.msoShapeRectangle.value__,
            1,
            100,100,200,200)
        
        shape.TextFrame.WordWrap = 0
        shape.TextFrame.AutoSize = 1 #ppAutoSizeShapeToFitText
        shape.TextFrame.MarginBottom = 0
        shape.TextFrame.MarginTop    = 0
        shape.TextFrame.MarginLeft   = 0
        shape.TextFrame.MarginRight  = 0
        if item[0]:
            shape.TextFrame.TextRange.Font.Name = item[0] #font name
        shape.TextFrame.TextRange.Text = item[1] #symbol text
        shape.select()


class LocpinGallery(Gallery):
    def __init__(self, locpin=None, **kwargs):
        self.locpin = locpin or pplib.GlobalLocPin
        self.items = [
            ("fix_locpin_tl", "Shape-Fixpunkt bzw. Fixierung bei Änderung oben-links"),
            ("fix_locpin_tm", "Shape-Fixpunkt bzw. Fixierung bei Änderung oben-mitte"),
            ("fix_locpin_tr", "Shape-Fixpunkt bzw. Fixierung bei Änderung oben-rechts"),
            ("fix_locpin_ml", "Shape-Fixpunkt bzw. Fixierung bei Änderung mitte-links"),
            ("fix_locpin_mm", "Shape-Fixpunkt bzw. Fixierung bei Änderung mitte-mitte"),
            ("fix_locpin_mr", "Shape-Fixpunkt bzw. Fixierung bei Änderung mitte-rechts"),
            ("fix_locpin_bl", "Shape-Fixpunkt bzw. Fixierung bei Änderung unten-links"),
            ("fix_locpin_bm", "Shape-Fixpunkt bzw. Fixierung bei Änderung unten-mitte"),
            ("fix_locpin_br", "Shape-Fixpunkt bzw. Fixierung bei Änderung unten-rechts"), 
        ]
        
        my_kwargs = dict(
            # get_enabled=apps.ppt_shapes_or_text_selected,
            columns="3",
            item_height="16",
            item_width="16",
            on_action_indexed  = Callback(self.locpin_on_action_indexed),
            get_selected_item_index = Callback(self.locpin_get_selected_item_index),
            children = [
                Item(image=gal_item[0], screentip=gal_item[1])
                for gal_item in self.items
            ]
        )
        if not "image" in kwargs and not "image_mso" in kwargs:
            my_kwargs["get_image"] = Callback(self.locpin_get_image)
        my_kwargs.update(kwargs)
        super(LocpinGallery, self).__init__(**my_kwargs)

    def locpin_on_action_indexed(self, selected_item, index):
        self.locpin.index = index

    def locpin_get_selected_item_index(self):
        return self.locpin.index
    
    def locpin_get_image(self, context):
        return context.python_addin.load_image(self.items[self.locpin.index][0])


class PositionGallery(Gallery):
    
    # items: [label, position, reference]
    #   position: [left, top, width, height]
    #       values can be absolute or percentage
    #   reference: CONTENTE / SLIDE / ABS 
    #       values are converted according to reference
    items = [
        [u"Volle Fläche",  [ 0, 0, 1, 1],       'CONTENT'],
        [u"2/3 Links",     [   0,  0, 2./3, 1], 'CONTENT'],
        [u"2/3 Rechts",    [1./3,  0, 2./3, 1], 'CONTENT'],
        
        [u"1/2 Links",     [  0, 0, .5, 1], 'CONTENT'],
        [u"1/2 Mitte",     [.25, 0, .5, 1], 'CONTENT'],
        [u"1/2 Rechts",    [ .5, 0, .5, 1], 'CONTENT'],
        
        [u"1/3 Links",     [  0,  0, 1./3, 1], 'CONTENT'],
        [u"1/3 Mitte",     [1./3, 0, 1./3, 1], 'CONTENT'],
        [u"1/3 Rechts",    [2./3, 0, 1./3, 1], 'CONTENT'],
        
        [u"1/6 Oben",      [ 0,    0, 1, 1./6], 'CONTENT'],
        [u"1/6 Unten",     [ 0, 5./6, 1, 1./6], 'CONTENT']
    ]
    
    def __init__(self, positions=None, label="Standardpositionen", columns=3, **kwargs):
        self.items = positions or PositionGallery.items
        super(PositionGallery, self).__init__(
            label = label,
            columns = columns,
            image_mso='PositionAnchoringGallery',
            supertip=u"Positioniere die ausgewählten Shapes auf eine Standardposition.",
            children=[
                Button(
                    label="Benutzerdef. Bereich festlegen",
                    supertip="Der benutzerdefinierte Bereich wird anhand des gewählten Shapes festgelegt. Dieser Bereich ist anschließend über die Gallery wählbar und wird dauerhaft in der aktuellen Prästentation vorgehalten.",
                    on_action=Callback(self.set_userdefined_area),
                    get_enabled = CallbackTypes.get_enabled.dotnet_name
                )
            ],
            **kwargs
        )
    
    def on_action_indexed(self, selected_item, index, context, **kwargs):
        ''' reposition shapes according of settings in clicked element '''
        item = self.items[index]
        position = item[1]
        reference = item[2]
        #self.change_position(selection, shapes, item[1])
        
        # reference size
        if reference == 'CONTENT':
            presentation = context.app.activewindow.presentation
            ref_left,ref_top,ref_width,ref_height = pplib.slide_content_size(presentation)
        else: # SLIDE / ABS
            presentation = context.app.activewindow.presentation
            ref_left,ref_top = 0, 0
            ref_width,ref_height = presentation.PageSetup.SlideWidth, presentation.PageSetup.SlideHeight
        
        # target size
        left,top,width,height = self.rect_from_definition(position, ref_frame=[ref_left,ref_top,ref_width, ref_height])
        frame = pplib.BoundingFrame.from_rect(left, top, width, height)
        
        if 'on_position_change' in self._callbacks:
            if context:
                return context.invoke_callback(self._callbacks['on_position_change'], target_frame=frame, **kwargs)
    
    
    def get_item_count(self, presentation):
        self.init_userdefined_area_item(presentation)
        return len(self.items)
    
    # def get_enabled(self, shapes):
    #     return True
    
    # def get_item_label(self, index):
    #     item = self.items[index]
    #     return "%s" % getattr(NumberedShapes, 'label_' + item['label'])[index%self.columns]
    
    def get_item_image(self, index, presentation):
        ''' creates an item image with target area according to settings in the specified item '''
        # retrieve item-settings
        item = self.items[index]
        return self.create_image(item[1], item[2], presentation)

    def get_item_screentip(self, index):
        # retrieve item-settings
        item = self.items[index]
        return 'Positionierung: ' + item[0]

    def get_item_supertip(self, index):
        return 'Verwende angezeigten Position/Größe.'
    
    
    def create_image(self, position, reference, presentation):
        # create bitmap, define pen/brush
        height = 40
        width = height*16./9
        img = Drawing.Bitmap(width, height)
        g = Drawing.Graphics.FromImage(img)
        
        
        # reference size
        if reference == 'CONTENT':
            v_offset = height/5
            v_ref = (height*4)/5
            left,top,fill_width,fill_height = self.rect_from_definition(position, ref_frame=[0,v_offset,width, v_ref])
            
        else: # SLIDE / ABS
            ref_width,ref_height = presentation.PageSetup.SlideWidth, presentation.PageSetup.SlideHeight
            left,top,fill_width,fill_height = self.rect_from_definition(position, ref_frame=[0,0,ref_width, ref_height])
            left        =   left     /ref_width * width
            fill_width  = fill_width /ref_width * width
            top         =   top      /ref_height * height
            fill_height = fill_height/ref_height * height
        
        color = Drawing.ColorTranslator.FromHtml('#ffdd0000')
        brush = Drawing.SolidBrush(color)
        g.FillRectangle(brush, Drawing.Rectangle(round(left),round(top), round(fill_width), round(fill_height)))
        
        color = Drawing.ColorTranslator.FromHtml('#ff999999')
        pen = Drawing.Pen(color,1)
        g.DrawRectangle(pen, Drawing.Rectangle(0,0, width-1, height/5-1))
        g.DrawRectangle(pen, Drawing.Rectangle(0,0, width-1, height-1))
        
        return img
    
    
    def rect_from_definition(self, pos_definition, ref_frame=[0,0,640,480]):
        left   = self.length_from_definition(pos_definition[0], ref_frame[2]) + ref_frame[0]
        top    = self.length_from_definition(pos_definition[1], ref_frame[3]) + ref_frame[1]
        width  = self.length_from_definition(pos_definition[2], ref_frame[2])
        height = self.length_from_definition(pos_definition[3], ref_frame[3])
        return left, top, width, height
        
        
    def length_from_definition(self, length_definition, reference):
        if type(length_definition) == list:
            # allow [150, 50%]
            l = 0
            for ldef in length_definition:
                l += self.length_from_definition(ldef, reference)
            return l
            
        elif type(length_definition) in [int, float, long]:
            if length_definition < 0:
                # negative values specify distance 'from right'
                return reference - length_from_definition(-length_definition, reference)
            
            elif length_definition <= 1:
                # percentage values
                return reference * length_definition
            
            else:
                # absolute values
                return length_definition
        else:
            return 10
        
    
    ## userdefined area
    
    def set_userdefined_area(self, presentation, shapes):
        if len(shapes) == 1:
            pplib.define_contentarea(presentation, shapes[0])
        else:
            frame = pplib.BoundingFrame.from_shapes(shapes)
            pplib.define_contentarea(presentation, frame)
        self.init_userdefined_area_item(presentation)
    
    
    def init_userdefined_area_item(self, presentation):
        #due to performance check first if tag exists at all
        if pplib.isset_contentarea(presentation):
            left, top, width, height = pplib.read_contentarea(presentation)
            if len(self.items) == 12:
                self.items.pop()
            self.items.append([u"Benutzerdef. Bereich", [left, top, width, height], 'ABS'])