# -*- coding: utf-8 -*-
'''
Created on 2017-11-09
@author: Florian Stallmann
'''



import logging
import os

from System import Array, Int32 #SlideRange

import bkt
import bkt.library.powerpoint as pplib

from bkt import dotnet
Forms = dotnet.import_forms()

class ConsolSplit(object):
    trans_table = str.maketrans('\t\n\r\f\v', '     ') #\t\n\r\x0b\x0c

    @classmethod
    def consolidate_ppt_slides(cls, application, presentation):
        fileDialog = Forms.OpenFileDialog()
        fileDialog.Filter = "PowerPoint (*.pptx;*.pptm;*.ppt)|*.pptx;*.pptm;*.ppt|Alle Dateien (*.*)|*.*"
        if presentation.Path:
            fileDialog.InitialDirectory = presentation.Path + '\\'
        fileDialog.Title = "PowerPoint-Dateien auswählen"
        fileDialog.Multiselect = True

        # fileDialog = application.FileDialog(3) #msoFileDialogFilePicker
        # fileDialog.Filters.Add("PowerPoint", "*.ppt; *.pptx; *.pptm", 1)
        # fileDialog.Filters.Add("Alle Dateien", "*.*", 2)
        # if presentation.Path:
        #     fileDialog.InitialFileName = presentation.Path + '\\'
        # fileDialog.title = "PowerPoint-Dateien auswählen"
        # fileDialog.AllowMultiSelect = True

        if not fileDialog.ShowDialog() == Forms.DialogResult.OK:
            return

        for file in fileDialog.FileNames:
            if file == presentation.FullName:
                continue
            try:
                presentation.Slides.InsertFromFile(file, presentation.Slides.Count)
            except:
                pass


    @classmethod
    def export_slide(cls, application, slides, full_name):
        slides[0].Parent.SaveCopyAs(full_name)
        newPres = application.Presentations.Open(full_name, False, False, False) #readonly, untitled, withwindow

        #remove slides (new method with array)
        slideIndices = [slide.SlideIndex for slide in slides]
        removeIndices = list(set(range(1,newPres.Slides.Count+1)) - set(slideIndices))
        if len(removeIndices) > 0:
            newPres.Slides.Range(Array[Int32](removeIndices)).Delete()

        #old method remove slide by slide
        # slideIds = [slide.SlideIndex for slide in slides]
        # removeIds = list(set(range(1,newPres.Slides.Count+1)) - set(slideIds))
        # removeIds.sort()
        # removeIds.reverse()
        # for slideId in removeIds:
        #     newPres.Slides(slideId).Delete()

        #remove all sections
        sections = newPres.SectionProperties
        for i in reversed(range(sections.count)):
            sections.Delete(i+1, 0) #index, deleteSlides=False

        newPres.Save()
        newPres.Close()
    
    @classmethod
    def _get_safe_filename(cls, title):
        # title = title.encode('ascii', 'ignore') #remove unicode characters -> this also removes umlauts
        title = title.translate(cls.trans_table, r'\/:*?"<>|') #replace special whitespace chacaters with space, also delete not allowed characters
        title = title[:64] #max 64 characters of title
        title = title.strip() #remove whitespaces at beginning and end
        return title
    
    @classmethod
    def split_slides_to_ppt(cls, context, slides):
        # if not presentation.Path:
        #     bkt.message.warning("Bitte erst Datei speichern.")
        #     return

        application = context.app
        presentation = context.presentation

        # save_pattern = "[slidenumber]_[slidetitle]"

        fileDialog = Forms.FolderBrowserDialog()
        if presentation.Path:
            fileDialog.SelectedPath = presentation.Path + '\\'
        fileDialog.Description = "Ordner zum Speichern auswählen"
        
        # fileDialog = application.FileDialog(4) #msoFileDialogFolderPicker
        # if presentation.Path:
        #     fileDialog.InitialFileName = presentation.Path + '\\'
        # fileDialog.title = "Ordner zum Speichern auswählen"

        if not fileDialog.ShowDialog() == Forms.DialogResult.OK:
            return
        folder = fileDialog.SelectedPath
        if not os.path.isdir(folder):
            return

        save_pattern = bkt.ui.show_user_input("Bitte Dateinamen-Pattern eingeben:", "Dateiname eingeben", "[slidenumber]_[slidetitle]")
        if save_pattern is None:
            return

        def _get_name(slide):
            try:
                title = cls._get_safe_filename(slide.Shapes.Title.TextFrame.TextRange.Text)
            except:
                title = "UNKNOWN"
            
            filename = save_pattern.replace("[slidenumber]", str(slide.SlideNumber)).replace("[slidetitle]", title)
            return os.path.join(folder, filename + ".pptx") #FIXME: file ending according to current presentation

        def loop(worker):
            error = False
            slides_current = 1.0
            slides_total = presentation.Slides.Count
            worker.ReportProgress(0)
            for slide in presentation.Slides:
                if worker.CancellationPending:
                    break
                worker.ReportProgress(round(slides_current/slides_total*100))
                slides_current += 1.0
                try:
                    cls.export_slide(application, [slide], _get_name(slide))
                except:
                    logging.exception("split_slides_to_ppt error")
                    error = True

            worker.ReportProgress(100)
            if worker.CancellationPending:
                bkt.message.warning("Export durch Nutzer abgebrochen", "BKT: Export")
            elif error:
                bkt.message.warning("Export mit Fehlern abgeschlossen", "BKT: Export")
            else:
                bkt.message("Export erfolgreich abgeschlossen", "BKT: Export")
            os.startfile(folder)

        bkt.ui.execute_with_progress_bar(loop, context, modal=False) #modal=False important so main thread can handle app events and all presentations close properly
    
    @classmethod
    def split_sections_to_ppt(cls, context, slides):
        # if not presentation.Path:
        #     bkt.message.warning("Bitte erst Datei speichern.")
        #     return

        application = context.app
        presentation = context.presentation

        if presentation.SectionProperties.count < 2:
            bkt.message.warning("Präsentation hat weniger als 2 Abschnitte!", "BKT: Export")
            return

        # save_pattern = "[sectionnumber]_[sectiontitle]"

        fileDialog = Forms.FolderBrowserDialog()
        if presentation.Path:
            fileDialog.SelectedPath = presentation.Path + '\\'
        fileDialog.Description = "Ordner zum Speichern auswählen"
        
        # fileDialog = application.FileDialog(4) #msoFileDialogFolderPicker
        # if presentation.Path:
        #     fileDialog.InitialFileName = presentation.Path + '\\'
        # fileDialog.title = "Ordner zum Speichern auswählen"

        if not fileDialog.ShowDialog() == Forms.DialogResult.OK:
            return
        folder = fileDialog.SelectedPath
        if not os.path.isdir(folder):
            return

        save_pattern = bkt.ui.show_user_input("Bitte Dateinamen-Pattern eingeben:", "Dateiname eingeben", "[sectionnumber]_[sectiontitle]")
        if save_pattern is None:
            return

        def _get_name(sections, index):
            try:
                title = cls._get_safe_filename(sections.Name(index))
            except:
                title = "UNKNOWN"
            
            filename = save_pattern.replace("[sectionnumber]", str(index)).replace("[sectiontitle]", title)
            return os.path.join(folder, filename + ".pptx") #FIXME: file ending according to current presentation

        def loop(worker):
            sections = presentation.SectionProperties
            error = False
            sections_current = 1.0
            sections_total = sections.count
            worker.ReportProgress(0)
            for i in range(sections.count):
                if worker.CancellationPending:
                    break
                worker.ReportProgress(round(sections_current/sections_total*100))
                sections_current += 1.0
                try:
                    start = sections.FirstSlide(i+1)
                    if start == -1:
                        continue #empty section
                    count = sections.SlidesCount(i+1)
                    slides = list(iter( presentation.Slides.Range( Array[Int32](list(range(start, start+count))) ) ))
                    cls.export_slide(application, slides, _get_name(sections, i+1))
                except:
                    logging.exception("split_sections_to_ppt error")
                    error = True
                    continue

            worker.ReportProgress(100)
            if worker.CancellationPending:
                bkt.message.warning("Export durch Nutzer abgebrochen", "BKT: Export")
            elif error:
                bkt.message.warning("Export mit Fehlern abgeschlossen", "BKT: Export")
            else:
                bkt.message("Export erfolgreich abgeschlossen", "BKT: Export")
            os.startfile(folder)

        bkt.ui.execute_with_progress_bar(loop, context, modal=False) #modal=False important so main thread can handle app events and all presentations close properly


class FolderToSlides(object):
    filetypes = [".jpg", ".png", ".emf"]

    @classmethod
    def _files_to_slides(cls, context, all_files):
        master_slide_new = False
        try:
            master_slide = context.slide
        except SystemError:
            #nothing appropriate selected
            master_slide = context.presentation.slides.add(1, 11) #ppLayoutTitleOnly
            master_slide_new = True
        
        ref_frame = pplib.BoundingFrame(master_slide, contentarea=True)

        # all_files.sort(reverse=True)
        for root, full_path in reversed(all_files):
            #create slide
            new_slide = master_slide.Duplicate()
            # new_slide.Layout = 11 #ppLayoutTitleOnly
            #add title
            if new_slide.Shapes.HasTitle:
                new_slide.Shapes.Title.Textframe.TextRange.Text = root
            #paste slide
            try:
                new_pic = new_slide.Shapes.AddPicture(full_path, 0, -1, ref_frame.left, ref_frame.top) #FileName, LinkToFile, SaveWithDocument, Left, Top, Width, Height
            except:
                new_slide.Delete()
            else:
                if new_pic.width > ref_frame.width:
                    new_pic.width = ref_frame.width
                if new_pic.height > ref_frame.height:
                    new_pic.height = ref_frame.height
        
        if master_slide_new:
            master_slide.Delete()

    @classmethod
    def folder_to_slides(cls, context):
        fileDialog = Forms.FolderBrowserDialog()
        if context.presentation.Path:
            fileDialog.SelectedPath = context.presentation.Path + '\\'
        fileDialog.Description = "Ordner mit Bildern auswählen"

        # fileDialog = context.app.FileDialog(4) #msoFileDialogFolderPicker
        # if context.presentation.Path:
        #     fileDialog.InitialFileName = context.presentation.Path + '\\'
        # fileDialog.title = "Ordner mit Bildern auswählen"

        if not fileDialog.ShowDialog() == Forms.DialogResult.OK:
            return
        folder = fileDialog.SelectedPath
        if not os.path.isdir(folder):
            return
        
        all_files = []

        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            root,ext = os.path.splitext(file)
            if ext in cls.filetypes:
                all_files.append((root, full_path))

        cls._files_to_slides(context, sorted(all_files))

    @classmethod
    def pictures_to_slides(cls, context):
        fileDialog = Forms.OpenFileDialog()
        _picfilestypes = "; ".join(["*"+f for f in cls.filetypes])
        fileDialog.Filter = "Bilder ("+_picfilestypes+")|"+_picfilestypes+"|SVG (*.svg)|*.svg|Alle Dateien (*.*)|*.*"
        if context.presentation.Path:
            fileDialog.InitialDirectory = context.presentation.Path + '\\'
        fileDialog.Title = "Bild-Dateien auswählen"
        fileDialog.Multiselect = True

        # fileDialog = context.app.FileDialog(3) #msoFileDialogFilePicker
        # fileDialog.Filters.Add("Bilder", , 1)
        # fileDialog.Filters.Add("SVG", "*.svg", 2)
        # fileDialog.Filters.Add("Alle Dateien", "*.*", 3)
        # if context.presentation.Path:
        #     fileDialog.InitialFileName = context.presentation.Path + '\\'
        # fileDialog.Title = "Bild-Dateien auswählen"
        # fileDialog.AllowMultiSelect = True

        if not fileDialog.ShowDialog() == Forms.DialogResult.OK:
            return

        def get_root(path):
            _,file = os.path.split(path)
            root,_ = os.path.splitext(file)
            return root

        all_files = [(get_root(file), file) for file in fileDialog.FileNames]
        cls._files_to_slides(context, all_files)


# consolsplit_gruppe = bkt.ribbon.Group(
#     label='Konsolidieren & Teilen',
#     image_mso='ThemeBrowseForThemes',
#     children = [
#         bkt.ribbon.Button(
#             id = 'consolidate_ppt_slides',
#             label="Folien aus Dateien anfügen",
#             show_label=True,
#             size="large",
#             image_mso='ThemeBrowseForThemes',
#             supertip="Alle Folien aus mehreren PowerPoint-Dateien an diese Präsentation anfügen.",
#             on_action=bkt.Callback(ConsolSplit.consolidate_ppt_slides, application=True, presentation=True),
#         ),
#         bkt.ribbon.Menu(
#             id = 'split_slides_to_ppt',
#             image_mso='ThemeSaveCurrent',
#             label="Folien einzeln speichern",
#             supertip="Folien in einzelne PowerPoint-Dateien speichern.",
#             show_label=True,
#             size="large",
#             item_size="large",
#             children=[
#                 bkt.ribbon.Button(
#                     # id = 'split_slides_to_ppt',
#                     label="Folien einzeln speichern",
#                     image_mso='ThemeSaveCurrent',
#                     description="Jede Folie als einzelne Datei im gewählten Ordner speichern. Die Dateien werden mit Foliennummer nummeriert und nach Folientitel benannt.",
#                     on_action=bkt.Callback(ConsolSplit.split_slides_to_ppt, application=True, presentation=True, slides=True),
#                 ),
#                 bkt.ribbon.Button(
#                     # id = 'split_slides_to_ppt',
#                     label="Abschnitte einzeln speichern",
#                     image_mso='ThemeSaveCurrent',
#                     description="Jeden Abschnitt als einzelne Datei im gewählten Ordner speichern. Die Dateien werden nummeriert und nach Abschnittstitel benannt.",
#                     on_action=bkt.Callback(ConsolSplit.split_sections_to_ppt, application=True, presentation=True, slides=True),
#                 ),
#             ]
#         )
#     ]
# )

# bkt.powerpoint.add_tab(bkt.ribbon.Tab(
#     id="bkt_powerpoint_toolbox_extensions",
#     insert_before_mso="TabHome",
#     label=u'Toolbox 3/3',
#     # get_visible defaults to False during async-startup
#     get_visible=bkt.Callback(lambda:True),
#     children = [
#         consolsplit_gruppe,
#     ]
# ), extend=True)



bkt.powerpoint.add_backstage_control(
    bkt.ribbon.Tab(
        label="Konsol./Teilen",
        title="BKT - Dateien Konsolidieren & Teilen",
        insertAfterMso="TabPublish", #http://youpresent.co.uk/customising-powerpoint-2016-backstage-view/
        columnWidthPercent="50",
        children=[
            bkt.ribbon.FirstColumn(children=[
                bkt.ribbon.Group(id="bkt_consolsplit_consolidate_group", label="Folien aus Dateien anfügen", children=[
                    bkt.ribbon.PrimaryItem(children=[
                        bkt.ribbon.Button(
                            label="Folien aus Dateien anfügen",
                            supertip="Alle Folien aus mehreren PowerPoint-Dateien an diese Präsentation anfügen",
                            image_mso='ThemeBrowseForThemes',
                            on_action=bkt.Callback(ConsolSplit.consolidate_ppt_slides, application=True, presentation=True),
                            is_definitive=True,
                        ),
                    ]),
                    bkt.ribbon.TopItems(children=[
                        bkt.ribbon.Label(label="Alle Folien aus mehreren PowerPoint-Dateien an diese Präsentation anfügen."),
                        bkt.ribbon.Label(label="Dieser Vorgang kann bei großen Dateien und vielen Folien einige Zeit in Anspruch nehmen!"),
                    ]),
                ]),
                bkt.ribbon.Group(id="bkt_consolsplit_pic2slides_group", label="Folien aus Bildern erstellen", children=[
                    bkt.ribbon.PrimaryItem(children=[
                        bkt.ribbon.Menu(
                            label="Folien aus Bildern erstellen",
                            supertip="Mehrere Bild-Dateien (jpg, png, emf) auf jeweils eine Folie einfügen",
                            image_mso='PhotoGalleryProperties',
                            children=[
                                bkt.ribbon.MenuGroup(
                                    item_size="large",
                                    children=[
                                        bkt.ribbon.Button(
                                            label="Bild-Dateien auswählen",
                                            image_mso='PhotoGalleryProperties',
                                            description="Alle Bild-Dateien zum Einfügen einzeln auswählen.",
                                            on_action=bkt.Callback(FolderToSlides.pictures_to_slides, context=True),
                                            is_definitive=True,
                                        ),
                                        bkt.ribbon.Button(
                                            label="Ordner mit Bildern auswählen",
                                            image_mso='OpenFolder',
                                            description="Ordner mit Bild-Dateien zum Einfügen auswählen.",
                                            on_action=bkt.Callback(FolderToSlides.folder_to_slides, context=True),
                                            is_definitive=True,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]),
                    bkt.ribbon.TopItems(children=[
                        bkt.ribbon.Label(label="Mehrere Bild-Dateien (jpg, png, emf) auf jeweils eine Folie einfügen."),
                        bkt.ribbon.Label(label="Die ausgewählte Folie wird für jede Bild-Datei dupliziert und der Dateiname als Titel gesetzt."),
                    ]),
                ]),
                bkt.ribbon.Group(id="bkt_consolsplit_split_group", label="Folien einzeln speichern", children=[
                    bkt.ribbon.PrimaryItem(children=[
                        bkt.ribbon.Menu(
                            label="Folien einzeln speichern",
                            supertip="Alle Folien in einzelne PowerPoint-Dateien im gewählten Ordner speichern",
                            image_mso='ThemeSaveCurrent',
                            children=[
                                bkt.ribbon.MenuGroup(
                                    item_size="large",
                                    children=[
                                        bkt.ribbon.Button(
                                            label="Folien einzeln speichern",
                                            image_mso='ThemeSaveCurrent',
                                            description="Jede Folie einzeln speichern. Die Dateien werden mit Foliennummer nummeriert und nach Folientitel benannt.",
                                            on_action=bkt.Callback(ConsolSplit.split_slides_to_ppt, context=True, slides=True),
                                            is_definitive=True,
                                        ),
                                        bkt.ribbon.Button(
                                            label="Abschnitte einzeln speichern",
                                            image_mso='SectionAdd',
                                            description="Jeden Abschnitt einzeln speichern. Die Dateien werden nummeriert und nach Abschnittstitel benannt.",
                                            on_action=bkt.Callback(ConsolSplit.split_sections_to_ppt, context=True, slides=True),
                                            is_definitive=True,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]),
                    bkt.ribbon.TopItems(children=[
                        bkt.ribbon.Label(label="Alle Folien in einzelne PowerPoint-Dateien im gewählten Ordner speichern."),
                        bkt.ribbon.Label(label="Dieser Vorgang kann bei großen Dateien und vielen Folien einige Zeit in Anspruch nehmen!"),
                    ]),
                ]),
            ])
        ]
    )
)