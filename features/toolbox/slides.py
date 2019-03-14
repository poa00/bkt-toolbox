# -*- coding: utf-8 -*-
'''
Created on 06.07.2016

@author: rdebeerst
'''

import bkt.ui

# for ui composition
import agenda
import language
from chartlib import chartlib_button


class SendOrSaveSlides(object):
    @classmethod
    def _slide_range_identifier(cls, slides):
        indices = [slide.SlideIndex for slide in slides]
        indices.sort()
        ind_str = str(indices[0])
        last_index = indices[0]
        range_from = last_index
        in_range = False
        for ind in indices[1:]:
            if ind == last_index +1:
                in_range = True
            else:
                if in_range:
                    if last_index - range_from ==1:
                        ind_str += ',' + str(last_index)
                    else:
                        ind_str += '-' + str(last_index)
                in_range = False
                range_from = ind
                ind_str +=',' + str(ind)
            last_index = ind
        if in_range:
            if last_index - range_from ==1:
                ind_str += ',' + str(last_index)
            else:
                ind_str += '-' + str(last_index)
        return ind_str

    @classmethod
    def initial_file_name(cls, presentation, slides=None):
        import time
        
        # bisheriger Dateiname
        fileNameFull = presentation.Name.rsplit('.', 1)
        fileName = fileNameFull[0]
        if len(fileNameFull) > 1:
            fileExt = "." + fileNameFull[1]
        else:
            fileExt = ".pptx"

        # Foliennummern
        if slides is not None:
            if len(slides) == 1:
                fileName = fileName + "_Folie_" + str(slides[0].SlideIndex)
            else:
                fileName = fileName + "_Folien_" + cls._slide_range_identifier(slides)

        # Zeitstempel
        fileName = fileName + "_" + time.strftime("%Y%m%d%H%M")
        # Dateiendung
        fileName = fileName + fileExt

        return fileName

    @classmethod
    def _delete_unselected_slides(cls, slides, newPres):
        # Folien rueckwaerts durchgehen und schauen, ob Index in Range dabei ist
        slideIds = [slide.SlideIndex for slide in slides]
        removeIds = list(set(range(1,newPres.Slides.Count+1)) - set(slideIds))
        removeIds.sort()
        removeIds.reverse()
        for slideId in removeIds:
            newPres.Slides(slideId).Delete()

    @classmethod
    def save_slides(cls, application, slides, fileName):
        # Kopie speichern und öffnen
        slides[0].Parent.SaveCopyAs(fileName)
        newPres = application.Presentations.Open(fileName)

        # Folien entfernen, die nicht ausgewählt waren
        cls._delete_unselected_slides(slides, newPres)

        # Speichern
        newPres.Save()

    @classmethod
    def send_slides(cls, application, slides, filename, fileformat="ppt", remove_sections=True, remove_author=False):
        import tempfile

        from bkt import dotnet
        Outlook = dotnet.import_outlook()

        oApp = Outlook.ApplicationClass()
        oMail = oApp.CreateItem(Outlook.OlItemType.olMailItem)
        oMail.Subject = filename

        # Kopie speichern und öffnen
        fullFileName = tempfile.gettempdir() + "\\" + filename
        application.ActiveWindow.Presentation.SaveCopyAs(fullFileName)
        newPres = application.Presentations.Open(fullFileName)
        
        if slides is not None:
            # Folien entfernen, die nicht ausgewählt waren
            cls._delete_unselected_slides(slides, newPres)
            newPres.Save()

        if remove_sections:
            # Alle Abschnitte entfernen
            sections = newPres.SectionProperties
            for i in reversed(range(sections.count)):
                sections.Delete(i+1, 0) #index, deleteSlides=False
        
        if remove_author:
            newPres.BuiltInDocumentProperties.item["author"].value = ''

        if fileformat != "pdf":
            # PPT anhängen
            oMail.Attachments.Add(fullFileName, Outlook.OlAttachmentType.olByValue)

        if fileformat != "ppt":
            # PDF exportieren und anhängen
            pdfFileName = fullFileName.rsplit('.', 1)[0] + ".pdf"
            #newPres.ExportAsFixedFormat(pdfFileNameRef, 2) #ppFixedFormatTypePDF #ValueError: Could not convert argument 0 for call to ExportAsFixedFormat.
            newPres.SaveCopyAs(pdfFileName, 32) #ppSaveAsPDF
            oMail.Attachments.Add(pdfFileName, Outlook.OlAttachmentType.olByValue)

        # Datei schließen
        newPres.Close()

        # Email anzeigen
        oMail.Display()


class FolienMenu(object):

    @classmethod
    def sendSlidesDialog(cls, context):
        from dialogs.slides_send import SendWindow
        SendWindow.create_and_show_dialog(SendOrSaveSlides, context)


    @classmethod
    def saveSlidesDialog(cls, context):
        slides = context.slides
        fileName = SendOrSaveSlides.initial_file_name(context.presentation, slides)

        fileDialog = context.app.FileDialog(2) #msoFileDialogSaveAs
        fileDialog.InitialFileName = context.presentation.Path + "\\" + fileName

        if len(slides) == 1:
            fileDialog.title = "Ausgewählte Folie speichern unter"
        else:
            fileDialog.title = str(len(slides)) + " ausgewählte Folien speichern unter"

        # Bei Abbruch ist Rückgabewert leer
        if fileDialog.Show() == 0: #msoFalse
            return
        fileName = fileDialog.SelectedItems(1)

        SendOrSaveSlides.save_slides(context.app, slides, fileName)


    SLIDENUMBERING = 'Toolbox-SlideNumbering'

    @classmethod
    def addSlideNumbering(cls, slides, context):
        # Alle Slides durchlaufen
        for sld in slides:
            # msoTextOrientationHorizontal = 1
            shp = sld.shapes.AddTextbox(1 # msoTextOrientationHorizontal
                , 0, 0, 100, 100)
            shp.TextFrame.TextRange.Font.Size = 32
            shp.TextFrame.TextRange.Font.Bold = -1 # msoTrue
            shp.TextFrame.TextRange.Font.Color = 192 + 0 * 256 + 0 * 256**2
            shp.TextFrame.TextRange.ParagraphFormat.Alignment = 3 #ppAlignRight
            shp.TextFrame.TextRange.text = sld.SlideIndex
            shp.TextFrame.MarginBottom = 0
            shp.TextFrame.MarginTop = 0
            shp.TextFrame.MarginRight = 0
            shp.TextFrame.MarginLeft = 0
            shp.Left = context.app.ActivePresentation.PageSetup.SlideWidth - shp.width - 15
            shp.Top = 15
            shp.Tags.Add(cls.SLIDENUMBERING, cls.SLIDENUMBERING)


    @classmethod
    def removeSlideNumbering(cls, slides):
        for slide in slides:
            for shp in slide.shapes:
                # Shape mit SlideNumberTag loeschen
                if shp.Tags.Item(cls.SLIDENUMBERING) == cls.SLIDENUMBERING:
                    shp.Delete()
                    break

    @classmethod
    def toggleSlideNumbering(cls, context):
        hasNumbering = False

        slides = context.app.ActivePresentation.Slides
        # Alle Shapes in allen Slides durchlaufen
        for sld in slides:
            for shp in sld.shapes:
                # Shape mit SlideNumberTag gefunden
                if shp.Tags.Item(cls.SLIDENUMBERING) == cls.SLIDENUMBERING:
                    hasNumbering = True
                    break
            if hasNumbering:
                break

        if hasNumbering:
            cls.removeSlideNumbering(slides)
        else:
            cls.addSlideNumbering(slides, context)
    
    @classmethod
    def remove_all(cls, context):
        try:
            cls.remove_slide_notes(context)
        except:
            pass
        
        try:
            cls.remove_hidden_slides(context)
        except:
            pass
        
        try:
            cls.remove_transitions(context)
        except:
            pass
        
        try:
            cls.remove_animations(context)
        except:
            pass
        
        try:
            cls.remove_slide_comments(context)
        except:
            pass
        
        try:
            cls.remove_doublespaces(context)
        except:
            pass
        
        try:
            cls.remove_empty_placeholders(context)
        except:
            pass
        
        
    @classmethod
    def remove_transitions(cls, context):
        slides = context.app.ActivePresentation.Slides
        for slide in slides:
            slide.SlideShowTransition.EntryEffect = 0
    
    @classmethod
    def remove_animations(cls, context):
        slides = context.app.ActivePresentation.Slides
        for slide in slides:
            for shape in slide.shapes:
                shape.AnimationSettings.Animate = 0

    @classmethod
    def remove_hidden_slides(cls, context):
        slides = context.app.ActivePresentation.Slides
        for slide in list(iter(slides)): #list(iter()) required as delete function will not work on all elements otherwise!
            if slide.SlideShowTransition.Hidden == -1:
                slide.Delete()

    @classmethod
    def remove_slide_notes(cls, context):
        slides = context.app.ActivePresentation.Slides
        for slide in slides:
            for shape in slide.NotesPage.Shapes:
                try:
                    if shape.PlaceholderFormat.type == 2: 
                        # ppt.PpPlaceholderType.ppPlaceholderBody.value__
                        shape.TextFrame.TextRange.Text = ""
                except:
                    # EnvironmentError: System.Runtime.InteropServices.COMException (0x80048240): PlaceholderFormat.Type : Invalid request.  Shape is not a placeholder.
                    pass

    @classmethod
    def remove_slide_comments(cls, context):
        slides = context.app.ActivePresentation.Slides
        for slide in slides:
            for comment in list(iter(slide.Comments)): #list(iter()) required as delete function will not work on all elements otherwise!
                comment.Delete()

    @classmethod
    def remove_doublespaces(cls, context):
        slides = context.app.ActivePresentation.Slides
        for slide in slides:
            for shape in slide.shapes:
                if shape.HasTextFrame == -1:
                    found = True
                    while found is not None:
                        found = shape.TextFrame.TextRange.Replace("  ", " ")
    
    @classmethod
    def remove_empty_placeholders(cls, context):
        slides = context.app.ActivePresentation.Slides
        for sld in slides:
            for plh in list(iter(sld.Shapes.Placeholders)): #list(iter()) required as delete function will not work on all elements otherwise!
                if plh.HasTextFrame == -1 and plh.TextFrame2.HasText == 0:
                    #placeholder is a text placeholder and has no text. note: placeholder can also be a picture, table or diagram without text!
                    plh.Delete()

    @classmethod
    def blackwhite_gray_scale(cls, context):
        slides = context.app.ActivePresentation.Slides
        for sld in slides:
            for shape in slide.shapes:
                if shape.BlackWhiteMode == 1:
                    shape.BlackWhiteMode = 2

    @classmethod
    def remove_author(cls, context):
        context.presentation.BuiltInDocumentProperties.item["author"].value = ''
    




slides_group = bkt.ribbon.Group(
    id="bkt_slide_group",
    label='Folien',
    image_mso='SlideNewGallery',
    children=[
        bkt.mso.control.SlideNewGallery,
        #bkt.mso.control.SlideLayoutGallery,
        chartlib_button,
        bkt.ribbon.Menu(
            label="Mehr",
            show_label=False,
            image_mso='TableDesign',
            screentip="Weitere Slide-Funktionen",
            supertip="Agenda, Foliennummerierung, ...",
            children=[
                bkt.ribbon.MenuSeparator(title="Layout"),
                bkt.mso.control.SlideLayoutGallery,
                bkt.mso.control.SlideReset,
                bkt.mso.control.SectionMenu,
                bkt.ribbon.MenuSeparator(title="Agenda")
                ] + agenda.agendamenu.children + [
                bkt.ribbon.MenuSeparator(title="Funktionen"),
                bkt.ribbon.Button(
                    id = 'slide_no',
                    label='Foliennummerierung ein-/ausblenden',
                    image_mso='NumberInsert',
                    #screentip="Foliennummerierung ein-/ausblenden",
                    supertip="Füge Foliennummerierungen ein, welche sich bei Umsortierung der Folien nicht ändern.\n\nHilfreich bei der Erfassung von Anmerkungen, wenn man während einer Diskussion des Foliensatzes Umsortierungen durchführt.",
                    on_action=bkt.Callback(FolienMenu.toggleSlideNumbering)
                ),
                bkt.ribbon.Button(
                    id = 'save_slides',
                    label='Ausgewählte Folien speichern',
                    image_mso='SaveSelectionToTextBoxGallery',
                    supertip="Speichert die ausgewählten Folien in einer neuen Präsentation.",
                    on_action=bkt.Callback(FolienMenu.saveSlidesDialog)
                ),
                bkt.ribbon.Button(
                    id = 'send_slides',
                    label='Ausgewählte Folien senden',
                    image_mso='FileSendAsAttachment',
                    on_action=bkt.Callback(FolienMenu.sendSlidesDialog)
                ),
                bkt.ribbon.SplitButton(children=[
                    bkt.ribbon.Button(
                        id = 'slide_remove_all',
                        label='Slidedeck aufräumen',
                        image_mso='SlideShowFromCurrent', #AcceptTask, SlideShowFromCurrent, FilePublishSlides
                        supertip="Lösche Notizen, ausgebledete Slides, Übergänge, Animationen, Kommentare, doppelte Leerzeichen, leere Platzhalter.",
                        on_action=bkt.Callback(FolienMenu.remove_all)
                    ),
                    bkt.ribbon.Menu(label="Slidedeck aufräumen", image_mso='SlideShowFromCurrent', children=[
                        bkt.ribbon.MenuSeparator(title="Inhalte"),
                        bkt.ribbon.Button(
                            id = 'slide_remove_hidden_slides',
                            label='Ausgeblendete Slides entfernen',
                            image_mso='SlideHide',
                            supertip="Lösche alle ausgeblendeten Slides im gesamten Foliensatz.",
                            on_action=bkt.Callback(FolienMenu.remove_hidden_slides)
                        ),
                        bkt.ribbon.Button(
                            id = 'slide_remove_notes',
                            label='Notizen entfernen',
                            image_mso='SpeakerNotes',
                            supertip="Lösche alle Notizen im gesamten Foliensatz.",
                            on_action=bkt.Callback(FolienMenu.remove_slide_notes)
                        ),
                        bkt.ribbon.Button(
                            id = 'slide_remove_comments',
                            label='Kommentare entfernen',
                            image_mso='ReviewDeleteComment',
                            supertip="Lösche alle Kommentare im gesamten Foliensatz.",
                            on_action=bkt.Callback(FolienMenu.remove_slide_comments)
                        ),
                        bkt.ribbon.Button(
                            id = 'presentation_remove_author',
                            label='Autor entfernen',
                            image_mso='ContactPictureMenu',
                            supertip="Autor aus den Dokumenteneigenschaften entfernen.",
                            on_action=bkt.Callback(FolienMenu.remove_author)
                        ),
                        bkt.ribbon.MenuSeparator(title="Animationen"),
                        bkt.ribbon.Button(
                            id = 'slide_remove_transitions',
                            label='Folienübergänge entfernen',
                            image_mso='AnimationTransitionGallery',
                            supertip="Lösche alle Übergänge zwischen Folien.",
                            on_action=bkt.Callback(FolienMenu.remove_transitions)
                        ),
                        bkt.ribbon.Button(
                            id = 'slide_remove_animation',
                            label='Shapeanimationen entfernen',
                            image_mso='AnimationGallery',
                            supertip="Lösche alle Shape-Animationen im gesamten Foliensatz.",
                            on_action=bkt.Callback(FolienMenu.remove_animations)
                        ),
                        bkt.ribbon.MenuSeparator(title="Format bereinigen"),
                        bkt.ribbon.Button(
                            id = 'slide_grayscale',
                            label='Automatischen Schwarz-/Weiß-Modus deaktivieren',
                            image_mso='BlackAndWhiteGrayscale',
                            supertip="Ersetze den Schwarz-/Weiß-Modus 'Automatisch' durch 'Graustufen'.",
                            on_action=bkt.Callback(FolienMenu.blackwhite_gray_scale)
                        ),
                        bkt.ribbon.Button(
                            id = 'slide_remove_doublespaces',
                            label='Doppelte Leerzeichen entfernen',
                            image_mso='ParagraphMarks',
                            supertip="Lösche alle doppelten Leerzeichen im gesamten Foliensatz.",
                            on_action=bkt.Callback(FolienMenu.remove_doublespaces)
                        ),
                        bkt.ribbon.Button(
                            id = 'slide_remove_empty_placeholders',
                            label='Leere Platzhalter entfernen',
                            image_mso='HeaderFooterRemoveHeaderWord',
                            supertip="Lösche leere Platzhalter-Textboxen im gesamten Foliensatz.",
                            on_action=bkt.Callback(FolienMenu.remove_empty_placeholders)
                        )
                    ]),
                ]),
                language.sprachen_menu,
                bkt.ribbon.MenuSeparator(title="Ansicht"),
                bkt.ribbon.Menu(label="Masteransichten", image_mso='GroupPresentationViews', children=[
                    bkt.mso.control.ViewSlideMasterView(show_label=True),
                    bkt.mso.control.ViewHandoutMasterView(show_label=True),
                    bkt.mso.control.ViewNotesMasterView(show_label=True),
                ]),
                bkt.ribbon.Menu(label="Farbe/Graustufen", image_mso='ColorGrayscaleMenu', children=[
                    bkt.mso.control.ViewDisplayInColor(show_label=True),
                    bkt.mso.control.ViewDisplayInGrayscale(show_label=True),
                    bkt.mso.control.ViewDisplayInPureBlackAndWhite(show_label=True),
                ]),
                bkt.mso.control.GuidesShowHide(show_label=True),
            ]
        )
    ]
)

    