# -*- coding: utf-8 -*-
'''
Created on 2018-05-29
@author: Florian Stallmann
'''

import os.path
import bkt.ui
notify_property = bkt.ui.notify_property


class ViewModel(bkt.ui.ViewModelAsbtract):
    def __init__(self, model, context):
        super(ViewModel, self).__init__()

        self._model = model
        self._context = context

        self._fileformat = "ppt"
        self._slides = "sel"
        self._remove_author = False
        self.update_filename()

    @notify_property
    def filename(self):
        return self._filename
    @filename.setter
    def filename(self, value):
        self._filename = value


    @notify_property
    def fileformat_ppt(self):
        return self._fileformat == "ppt"
    @fileformat_ppt.setter
    def fileformat_ppt(self, value):
        self._fileformat = "ppt"
        self.OnPropertyChanged('rm_se_enabled')

    @notify_property
    def fileformat_pdf(self):
        return self._fileformat == "pdf"
    @fileformat_pdf.setter
    def fileformat_pdf(self, value):
        self._fileformat = "pdf"
        self.OnPropertyChanged('rm_se_enabled')

    @notify_property
    def fileformat_all(self):
        return self._fileformat == "all"
    @fileformat_all.setter
    def fileformat_all(self, value):
        self._fileformat = "all"
        self.OnPropertyChanged('rm_se_enabled')


    @notify_property
    def slides_selected(self):
        return self._slides == "sel"
    @slides_selected.setter
    def slides_selected(self, value):
        self._slides = "sel"
        self.update_filename()

    @notify_property
    def slides_all(self):
        return self._slides == "all"
    @slides_all.setter
    def slides_all(self, value):
        self._slides = "all"
        self.update_filename()


    @notify_property
    def remove_author(self):
        return self._remove_author
    @remove_author.setter
    def remove_author(self, value):
        self._remove_author = value

    @notify_property
    def remove_sections(self):
        return self._remove_sections
    @remove_sections.setter
    def remove_sections(self, value):
        self._remove_sections = value

    @notify_property
    def rm_se_enabled(self):
        return self._fileformat != "pdf"


    def update_filename(self):
        if self._slides == "all":
            self.filename = self._model.initial_file_name(self._context.presentation)
            self.remove_sections = False
        else:
            self.filename = self._model.initial_file_name(self._context.presentation, self._context.slides)
            self.remove_sections = True



class SendWindow(bkt.ui.WpfWindowAbstract):
    _filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'slides_send.xaml')
    # _vm_class = ViewModel

    def __init__(self, model, context):
        self._model = model
        self._vm = ViewModel(model,context)
        self._context = context

        super(SendWindow, self).__init__()

    def cancel(self, sender, event):
        self.Close()
    
    def send_slides(self, sender, event):
        self.Close()
        slides = None if self._vm._slides == "all" else self._context.slides
        self._model.send_slides(self._context.app, slides, self._vm._filename, self._vm._fileformat, self._vm._remove_sections, self._vm._remove_author)