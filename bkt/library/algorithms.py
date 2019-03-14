# -*- coding: utf-8 -*-
'''
Created on 11.09.2013

@author: cschmitt
'''
import math
import bkt.helpers as helpers

def median(values):
    v = sorted(values)
    if not v:
        raise ValueError
    n = len(v)
    if n % 2 == 0:
        return (v[n/2-1]+v[n/2])*0.5
    else:
        return v[(n-1)/2]

def mean(values):
    return sum(values)/len(values)

def mid_point(points):
    sum_x = 0
    sum_y = 0
    
    for p in points:
        sum_x +=p[0]
        sum_y +=p[1]
    
    return [sum_x/len(points), sum_y/len(points)]

def is_close(a, b, tolerence=1e-9):
    # refer to https://github.com/PythonCHB/close_pep/blob/master/is_close.py
    if a == b:
        return True
    diff = abs(a-b)
    return (diff <= abs(tolerence * b)) or (diff <= abs(tolerence * a))

def get_bounds2(points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    
    left = min(x)
    top = min(y)
    width = max(x)-left
    height = max(y)-top
    
    return left,top,width,height

def get_bounds(shapes):
    def iter_points():
        for cell in shapes:
            x0 = cell.Left
            y0 = cell.Top
            yield (x0,y0)
            x1 = x0 + cell.Width
            y1 = y0 + cell.Height
            yield (x1,y1)
    
    points = list(iter_points())
    return get_bounds2(points)

def rotate_point(x, y, x0, y0, deg):
    ''' rotate (x,y) arround (x0, y0) '''
    theta = deg*2*math.pi/360
    return x0+(x-x0)*math.cos(theta)+(y-y0)*math.sin(theta), y0-(x-x0)*math.sin(theta)+(y-y0)*math.cos(theta)

def get_bounding_nodes(shape):
    ''' compute bounding nodes (surrounding-square) for rotated shapes '''
    points = [ [ shape.left, shape.top ], [shape.left, shape.top+shape.height], [shape.left+shape.width, shape.top+shape.height], [shape.left+shape.width, shape.top] ]

    x0 = shape.left + shape.width/2
    y0 = shape.top + shape.height/2

    rotated_points = [
        list(rotate_point(p[0], p[1], x0, y0, shape.rotation))
        for p in points
    ]
    return rotated_points


class TableRecognition(object):
    def __init__(self,shapes):
        self.shapes = set(shapes)
        self.table = None
        
    def run(self):
        table = []
        while self.shapes:
            seed = self.collect_seed()
            line = [seed]
            while self.shapes:
                nxt = self.next_in_row(line)
                if nxt is None:
                    break
                self.shapes.discard(nxt)
                line.append(nxt)
            table.append(line)
        self.table = table
        
        #def line_top(line):
        #    return min()
        
        self.table = sorted(table, key=lambda l : min(s.Top for s in l))
        self.correct_columns()
        
    def left_edge(self,col):
        return median(s.Left for s in self.column(col) if s is not None)
    
    def get_column_edges(self):
        num_cols = self.column_count()
        #median_edges = 
        edges = set(self.left_edge(col) for col in xrange(num_cols))
        for col in xrange(num_cols):
            #median_edge = self.left_edge(col)
            #edges.add(median_edge)
            for cell in self.column(col):
                if cell is None:
                    continue
                new_edge = True
                for edge in edges:
                    if abs(edge-cell.Left) <= cell.Width * 0.5:
                        new_edge = False
                        break
                        #MessageBox.Show("adding new edge %r:\r\nmedian_edge=%r, \r\ndist=%r, \r\nwidth/2=%r" % (cell.Left, edge, abs(edge-cell.Left), cell.Width*0.5))
                        #edges.add(cell.Left)
                if new_edge:
                    edges.add(cell.Left)
        
        return list(enumerate(sorted(edges)))

    @property
    def dimension(self):
        return len(self.table), self.column_count()

    def cell(self,i,j):
        row = self.table[i]
        if j < len(row):
            return row[j]
    
    def iter_cells(self):
        rows, cols = self.dimension
        for i in xrange(rows):
            for j in xrange(cols):
                cell = self.cell(i,j)
                if cell is None:
                    continue
                yield i,j,cell
     
    def get_bounds(self):
        def iter_points():
            for _, _, cell in self.iter_cells():
                x0 = cell.Left
                y0 = cell.Top
                yield (x0,y0)
                x1 = x0 + cell.Width
                y1 = y0 + cell.Height
                yield (x1,y1)
        
        points = list(iter_points())
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        
        left = min(x)
        top = min(y)
        width = max(x)-left
        height = max(y)-top
        
        return left,top,width,height
    
    def change_spacing_in_bounds(self,delta):
        spacing_old = self.median_spacing()
        self.align(spacing_old)
        spacing = max(0,spacing_old+delta)
        bounds = self.get_bounds()
        self.fit_content(*bounds, spacing=spacing)
    
    def median_spacing(self):
        def iterate_spacings():
            rows, cols = self.dimension
            for i in xrange(rows):
                for j in xrange(cols):
                    cell = self.cell(i,j)
                    if cell is None:
                        continue
                    if j > 0:
                        left = self.cell(i, j-1)
                        if left is not None:
                            spacing = cell.Left - left.Left - left.Width
                            if spacing > 0:
                                yield spacing
                    if i > 0:        
                        top = self.cell(i-1, j)
                        if top is not None:
                            spacing = cell.Top - top.Top - top.Height
                            if spacing > 0:
                                yield spacing
                            
        spacings = list(iterate_spacings())
        #MessageBox.Show(str(spacings))
        if not spacings:
            return 0
        return median(spacings)
    
    def min_spacing_rows(self):
        rows, cols = self.dimension
        if rows < 2:
            return 0
        cur_min = float('inf')
        for i in xrange(1,rows):
            for j in xrange(cols):
                cell = self.cell(i,j)
                top = self.cell(i-1, j)
                if cell is None or top is None:
                    continue      
                spacing_rows = cell.Top - top.Top - top.Height
                cur_min = min(cur_min, spacing_rows)

        return cur_min
    
    def min_spacing_cols(self):
        rows, cols = self.dimension
        if cols < 2:
            return 0
        cur_min = float('inf')
        for i in xrange(rows):
            for j in xrange(1,cols):
                cell = self.cell(i,j)
                left = self.cell(i, j-1)
                if cell is None or left is None:
                    continue
                spacing_cols = cell.Left - left.Left - left.Width
                cur_min = min(cur_min, spacing_cols)

        return cur_min
    
    def correct_columns(self):
        edges = self.get_column_edges()
        #MessageBox.Show(str(edges))
        num_cols = len(edges)
        
        
        def get_index(cell):
            left = cell.Left
            res = min(edges, key=lambda t : abs(left-t[1]))
            #MessageBox.Show(str(res))
            return res[0]
        
        table = []
        for i,line in enumerate(self.table):
            line_new = [None]*num_cols
            for cell in line:
                if cell is None:
                    continue
                index = get_index(cell)
                if line_new[index] is not None:
                    helpers.log("cell index %d is duplicated in line %d\r\nedges: %r" % (index,i,edges))
                    line_new = list(line)
                    while len(line_new) < num_cols:
                        line_new.append(None)
                    break
                line_new[index] = cell
            table.append(line_new)
            
        col = 0
        while col < num_cols:
            cellset = set(line[col] for line in table)
            if cellset == set([None]):
                for line in table:
                    del line[col]
                num_cols -= 1
            else:
                col += 1
        
        self.table = table
                        
    
    def column_count(self):
        return max(len(line) for line in self.table)
            
    def column(self,col):
        for line in self.table:
            if col < len(line):
                yield line[col]
            else:
                yield None
    
    def transpose(self):
        cols = self.column_count()
        table = []
        for j in xrange(cols):
            table.append(list(self.column(j)))
        self.table = table
        
    def transpose_cell_size(self):
        for line in self.table:
            for cell in line:
                if cell is None:
                    continue
                cell.Width, cell.Height = cell.Height, cell.Width
    
    @property            
    def first_top(self):
        for cell in self.table[0]:
            if cell is not None:
                return cell
    
    @property            
    def first_left(self):
        for cell in self.column(0):
            if cell is not None:
                return cell
    
    def column_width(self,col):
        shapes = [s for s in self.column(col) if s is not None]
        if not shapes:
            return 0
        return max(s.Width for s in shapes)
    
    def row_height(self,row):
        shapes = [s for s in self.table[row] if s is not None]
        if not shapes:
            return 0
        return max(s.Height for s in shapes)
    
    def fit_content(self,left,top,width,height,spacing,fit_cells=False, distribute_cols=False, distribute_rows=False):
        rows, cols = self.dimension

        #tuple = (row spacing, column spacing)
        if type(spacing) == tuple:
            spacing_rows, spacing_cols = spacing
        else:
            spacing_rows = spacing
            spacing_cols = spacing

        if spacing_cols is not None:
            widths = [self.column_width(col) for col in xrange(cols)]
            if distribute_cols:
                widths = [float(sum(widths)) / len(widths)] * len(widths)
                scale_x = 1
            else:
                remaining_width = width - (len(widths)-1)*spacing_cols
                scale_x = float(remaining_width) / float(sum(widths))
        
        if spacing_rows is not None:
            heights = [self.row_height(row) for row in xrange(rows)]
            if distribute_rows:
                heights = [float(sum(heights)) / len(heights)] * len(heights)
                scale_y = 1
            else:
                remaining_height = height - (len(heights)-1)*spacing_rows
                scale_y = float(remaining_height) / float(sum(heights))
        
        def set_size(cell, width=None, height=None):
            if not cell.LockAspectRatio or width is None or height is None:
                if width is not None:
                    cell.Width = width
                if height is not None:
                    cell.Height = height
            else:
                ratio = float(cell.Width)/float(cell.Height)
                if ratio > 1:
                    cell.Width = width
                else:
                    cell.Height = height


        for i in xrange(rows):
            for j in xrange(cols):
                cell = self.cell(i, j)
                if cell is None:
                    continue
                
                #FIXME: this is probably powerpoint specific
                if cell.HasTextFrame == -1 and cell.TextFrame.AutoSize == 1:
                    cell.TextFrame.AutoSize = 0

                width = None
                height = None

                if spacing_cols is not None:
                    width = widths[j]*scale_x if fit_cells else cell.Width*scale_x
                if spacing_rows is not None:
                    height = heights[i]*scale_y if fit_cells else cell.Height*scale_y

                set_size(cell, width, height)
        
        self.align(spacing, left, top)
            
    def align(self, spacing=10, xstart=None, ystart=None, fit_cells=False, align_x="left", align_y="top"):
        num_columns = self.column_count()
        widths = [self.column_width(col) for col in xrange(num_columns)]
        
        #tuple = (row spacing, column spacing)
        if type(spacing) == tuple:
            spacing_rows, spacing_cols = spacing
        else:
            spacing_rows = spacing
            spacing_cols = spacing

        #set x-start coordinate
        left = []
        if xstart is None:
            x = self.first_left.Left
        else:
            x = xstart

        #set y-start coordinate
        if ystart is None:
            y = self.first_top.Top
        else:
            y = ystart

        #calculate x coordinates (columns)
        if spacing_cols is not None:
            for w in widths:
                left.append(x)
                x += w + spacing_cols
        
        #iterate lines
        for line in self.table:
            height = max(s.Height for s in line if s is not None)
            
            for j, shape in enumerate(line):
                if shape is None:
                    continue
                
                if fit_cells:
                    shape.Width = widths[j]
                    shape.Height = height

                if spacing_rows is not None:
                    y_pos = y
                    y_pos += (height - shape.Height) if align_y == "bottom" else 0
                    y_pos += (height - shape.Height)/2 if align_y == "middle" else 0
                    shape.Top = y_pos
                
                if spacing_cols is not None:
                    x_pos = left[j]
                    x_pos += (widths[j] - shape.Width) if align_x == "right" else 0
                    x_pos += (widths[j] - shape.Width)/2 if align_x == "center" else 0
                    shape.Left = x_pos
            
            if spacing_rows is not None:
                y += height + spacing_rows
        
    def next_in_row(self, line):
        ref = line[0]
        refx = ref.Left
        refy = ref.Top
        bound = ref.Height * 0.5
        
        selection = []
        for s in self.shapes:
            if s.Left < refx:
                continue
            if abs(s.Top-refy) > bound:
                continue
            selection.append(s)
            
        if selection:
            return min(selection, key=lambda s : abs(s.Left-refx))
        else:
            return None
        
#        refx = shape.Left + shape.Width
#        refy = shape.top
#        
#        selection = []
#        ref = shape.Left
#        bound = shape.
#        for s in self.shapes:
#            if s is shape:
#                continue
#            m
#        
#        return min(self.shapes, key=self.distfun(refx, refy))

    def collect_next_in_row(self, shape):
        nxt = self.next_in_row(shape)
        self.shapes.discard(nxt)
        return nxt
    
    def distfun(self,refx,refy):
        def dist(s):
            return math.hypot(refx-s.Left, refy-s.Top)
        return dist
    
    def collect_seed(self):
        leftmost = min(s.Left for s in self.shapes)
        topmost =  min(s.Top for s in self.shapes)
        
        seed = min(self.shapes,key=self.distfun(leftmost, topmost))
        self.shapes.discard(seed)
        return seed