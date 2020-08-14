# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import logging
from math import ceil

import bkt.ui
notify_property = bkt.ui.notify_property

import bkt.library.table as lib_table
import bkt.library.powerpoint as pplib
pt_to_cm = pplib.pt_to_cm
cm_to_pt = pplib.cm_to_pt

# =================
# = FUNCTIONALITY =
# =================


class ShapesAsTable(object):
    
    @classmethod
    def align_shapes(cls, shapes, cols=None, spacing_x=5, spacing_y=5):
        # shapes.sort(key=lambda s: ())
        # init_left = shapes[0].left
        # top = shapes[0].top
        # len_shapes = len(shapes)

        # if rows is None:
        #     rows = len_shapes/cols

        table = lib_table.TableData.from_list(shapes, cols)
        shape_table = lib_table.ShapeTableAlignment(table)
        shape_table.spacing = spacing_x, spacing_y
        shape_table.align()

        # table_list = []
        # col_widths = [0]*cols
        # for i in range(rows):
        #     row = []
        #     for j in range(cols):
        #         n=i*cols+j
        #         if n >= len_shapes:
        #             break
        #         shape = shapes[n]
        #         row.append(shape)
        #         col_widths[j] = max(col_widths[j], shape.width)
        #     table_list.append(row)
        
        # for row in table_list:
        #     row_height = max(row, key=lambda s:s.height)
        #     left = init_left
        #     for i,shape in enumerate(row):
        #         shape.left = left
        #         shape.top = top
        #         left += spacing + col_widths[i]
        #     top += spacing + row_height



# =======================
# = UI MODEL AND WINDOW =
# =======================


class ViewModel(bkt.ui.ViewModelSingleton):
    
    def __init__(self):
        super(ViewModel, self).__init__()
        
        self._len_shapes = 1
        self._align_target = "rows"

        self._target_rows = 1
        self._target_cols = 1

        self._spacing_x = 0.2
        self._spacing_y = 0.2
    
    def set_len(self, len_shapes):
        self._len_shapes = len_shapes

        if self._align_target == "rows":
            self._target_cols = ceil(len_shapes/self._target_rows)
        else:
            self._target_rows = ceil(len_shapes/self._target_cols)

        self.OnPropertyChanged('target_rows')
        self.OnPropertyChanged('target_cols')
    
    @notify_property
    def align_rows(self):
        return self._align_target == "rows"
    @align_rows.setter
    def align_rows(self, value):
        if value:
            self._align_target = "rows"
    
    @notify_property
    def align_cols(self):
        return self._align_target == "cols"
    @align_cols.setter
    def align_cols(self, value):
        if value:
            self._align_target = "cols"
    
    @notify_property
    def spacing_x(self):
        return self._spacing_x
    @spacing_x.setter
    def spacing_x(self, value):
        self._spacing_x = value
    
    @notify_property
    def spacing_y(self):
        return self._spacing_y
    @spacing_y.setter
    def spacing_y(self, value):
        self._spacing_y = value

    @notify_property
    def target_rows(self):
        return self._target_rows
    @target_rows.setter
    def target_rows(self, value):
        self._target_rows = value
        self._target_cols = ceil(self._len_shapes/value)
        self.OnPropertyChanged('target_rows')
        self.OnPropertyChanged('target_cols')
        self.align_rows = True
    
    @notify_property
    def target_cols(self):
        return self._target_cols
    @target_cols.setter
    def target_cols(self, value):
        self._target_cols = value
        self._target_rows = ceil(self._len_shapes/value)
        self.OnPropertyChanged('target_rows')
        self.OnPropertyChanged('target_cols')
        self.align_cols = True


class ShapesAsTableWindow(bkt.ui.WpfWindowAbstract):
    _xamlname = 'table_dialog'
    _vm_class = ViewModel
    
    def __init__(self, context, shapes):
        super(ShapesAsTableWindow, self).__init__(context)

        self.ref_shapes = shapes
        self._vm.set_len(len(shapes))
    
    def align(self, sender, event):
        vm = self._vm
        ShapesAsTable.align_shapes(self.ref_shapes, vm.target_cols, cm_to_pt(vm.spacing_x), cm_to_pt(vm.spacing_y))
        self.Close()