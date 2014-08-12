#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# scales.py
#
# Copyright (c) 2014, Paul Holleis, Marko Luther
# All rights reserved.
# 
# 
# LICENSE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4.QtCore import (SIGNAL,QAbstractTableModel,Qt,QSize,QRegExp,QTimer)
from PyQt4.QtGui import (QBrush,QColor,QStyledItemDelegate,QLineEdit,QRegExpValidator,QItemSelection,QItemSelectionModel)

import numpy as np
import numpy.polynomial.polynomial as poly
import locale
import random

from lib import __version__

class Scales(QAbstractTableModel):
    def __init__(self, app=None, parent=None, *args):
        QAbstractTableModel.__init__(self,parent,*args)
        self.app = app
        self.defaultCoefficients = [.0, .0, 102.2727273, -128.4090909] # x3, x2, x, c 
        # old w/b: [.0, .0, 91.24835742, -254.9145861]
        self.deviceCoefficients = None
        # coefficients are recomputed on loading/setting from coordinates if possible (eg. coordinates are given)
        self.coefficients = None
        self.RR = None
        self.coordinates = []
        self.polyfit_degree = 0
        # initialize random number generator
        random.seed()
        
    def computeT(self,x):
        return np.poly1d(self.deviceCoefficients or self.defaultCoefficients)([x])[0]
        
    # accessors and selectors
    
    def getVisibleCoordinates(self):
        if self.coordinates:
            return [c[1:3] for c in self.coordinates]
        else:
            return []
            
    def setVisibleCoordinate(self,row,column,value):
        self.coordinates[row][column+1] = value
        
    def getCoordinates(self):
        return self.coordinates
            
    def getSelectedCoordinates(self):
        selectedRows = self.app.aw.getSelectedRows()
        return [item for i,item in enumerate(self.coordinates) if i in selectedRows]
        
    # compute the coefficients of the given scale and apply to the current coordinates
    def applyScale(self,scale):
        # extract coordinates
        if "coordinates" in scale:
            coordinates = scale["coordinates"]
        else:
            coordinates = []
        # extract degree
        if "degree" in scale:
            polyfit_degree = scale["degree"]
        else:
            polyfit_degree = 1
        # compute polyfit
        if len(coordinates) > polyfit_degree:
            xv = np.array([e[0] for e in coordinates])
            yv = np.array([e[1] for e in coordinates])
            c,_ = poly.polyfit(xv,yv,polyfit_degree,full=True)
            coefficients = list(c)
            coefficients.reverse()
            # apply polyfit          
            self.beginResetModel()
            for i in range(len(self.coordinates)):
                x = self.coordinates[i][0]
                newT = np.poly1d(coefficients)([x])[0]
                self.coordinates[i][1] = int(round(newT))
            self.endResetModel()
            # update Polyfit and trigger the redraw of the matplotlib graph canvas
            self.computePolyfit()
        
    def setScale(self,scale):            
        self.beginResetModel()
        if "coordinates" in scale:
            self.coordinates = scale["coordinates"]
        else:
            self.coordinates = []
        if "degree" in scale:
            self.polyfit_degree = scale["degree"]
            self.app.aw.ui.degreeSlider.setValue(self.app.scales.getPolyfitDegree())
        self.endResetModel()
        self.computePolyfit()
        
    def getScale(self):
        scale = {}
        scale["appVersion"] = __version__
        if self.coordinates:
            scale["coordinates"] = self.coordinates
        scale["degree"] = self.polyfit_degree
        return scale
        
    def sortCoordinates(self,col=0,order=0):
        selectedCoordinates = self.getSelectedCoordinates()
        self.beginResetModel()
        s = sorted(self.coordinates, key=lambda c: c[col],  reverse=order)
        self.coordinates = s
        self.endResetModel()
        self.redoSelection(selectedCoordinates)
        self.app.contentModified()
        
    def redoSelection(self,selectedCoordinates):
        selection = QItemSelection()
        for i,c in enumerate(self.coordinates):
            if c in selectedCoordinates:
                selection.merge(QItemSelection(self.createIndex(i,0),self.createIndex(i,1)),QItemSelectionModel.Select)
        self.app.aw.ui.tableView.selectionModel().select(selection,QItemSelectionModel.Select)
        
    # deletes the coordinates at the given positions
    def deleteCoordinates(self,positions):  
        selectedCoordinates = self.getSelectedCoordinates()
        self.beginResetModel()      
        self.coordinates[:] = [ item for i,item in enumerate(self.coordinates) if i not in positions]
        self.endResetModel()
        self.redoSelection(selectedCoordinates)
        self.app.contentModified()
        self.computePolyfit()
        
    def autoScroll(self):
        QTimer.singleShot(0, self.app.aw.ui.tableView.scrollToBottom)
        
    def addCoordinates(self,coordinates):
        selectedCoordinates = self.getSelectedCoordinates()
        self.beginResetModel()
        for new_coordinate in coordinates:
            if len(new_coordinate) == 4 and \
             isinstance(new_coordinate[0], float) and \
             isinstance(new_coordinate[1], int) and \
             isinstance(new_coordinate[3], float) :
                self.coordinates.append(new_coordinate)
        self.endResetModel()
        self.redoSelection(selectedCoordinates)
        self.app.contentModified()
        self.computePolyfit()
        self.autoScroll()

    def addCoordinate(self,x,y,name=""):
        selectedCoordinates = self.getSelectedCoordinates()
        if y == None:
            # y from I_SCAN, we compute the T value
            y2 = int(round(self.computeT(x)))
            new_coordinate = [x,y2,name or str(len(self.coordinates)+1),random.random()]
        else:
            y2 = int(round(y))
            new_coordinate = [x,y2,name or str(len(self.coordinates)+1),random.random()]
        self.beginResetModel()
        self.coordinates.append(new_coordinate)
        self.coordinates = self.coordinates
        self.endResetModel()
        selectedCoordinates.append(new_coordinate)
        self.redoSelection(selectedCoordinates)
        self.app.contentModified()
        self.computePolyfit()
        self.autoScroll()
            
    def computePolyfit(self):
        if self.polyfit_degree and len(self.coordinates) > self.polyfit_degree:
            xv = np.array([e[0] for e in self.coordinates])
            yv = np.array([e[1] for e in self.coordinates])
            c, stats = poly.polyfit(xv,yv,self.polyfit_degree,full=True)
            r2 = 1 - stats[0] / (yv.size * yv.var())            
            if r2 and len(r2)>0:
                self.setRR(r2[0])
            else:
                self.setRR(None)
            self.coefficients = list(c)
            self.coefficients.reverse()
        else:
            self.coefficients = None
            self.setRR(None)
        self.app.aw.setEnabledUploadButton()
        # trigger the redraw of the matplotlib graph canvas
        self.app.aw.ui.widget.canvas.updatePolyfit()
            
    def getCoefficients(self):
        return self.coefficients
        
    def setCoefficients(self,coefficients):
        self.coefficients = self.coefficients
            
    def getDeviceCoefficients(self):
        return self.deviceCoefficients
        
    def setDeviceCoefficients(self,coefficients):
        self.deviceCoefficients = coefficients
        # trigger the computation of the device curve redraw of the matplotlib graph canvas
        self.app.aw.ui.widget.canvas.updateDevicePolyfit()
        
    def getDefaultCoefficents(self):
        return self.defaultCoefficients
        
    def getRR(self):
        return self.RR
        
    def setRR(self,RR):
        self.RR = RR
        
    def setPolyfitDegree(self,d):
        self.polyfit_degree = d
        self.computePolyfit()
        
    def getPolyfitDegree(self):
        return self.polyfit_degree
        
    def clearCoordinates(self):
        self.beginResetModel()
        self.coordinates = []
        self.endResetModel()
        self.computePolyfit()
        self.app.contentCleared()
        
    def coordinates2text(self,coordinates):
        lines = ["%s %d \"%s\""%('{:.7n}'.format(c[0]),c[1],c[2]) for c in coordinates]
        return "\n".join([str(l) for l in lines])
        
    def line2coordinate(self,line):
        l = line.replace("\t"," ").split(" ",2)
        if len(l) == 2:
            return [locale.atof(l[0]),int(l[1]),"",random.random()]
        else:
            return [locale.atof(l[0]),int(l[1]),str(eval(l[2])),random.random()]
        
    def text2coordinates(self,txt):
        return [self.line2coordinate(l) for l in txt.replace("\r","\n").split("\n")]
        

#
# QAbstractTableModel interface
#        
    
    def rowCount(self,parent):
        return len(self.coordinates)
        
    def columnCount(self,parent):
        return len(self.app.aw.tableheaders)
    
    # updates the element at row with values c0 and c1 for the first two column values        
    def updateCoordinate(self,row,c0,c1):
        # respect the limits
        # NOSORT
        if False and ((row > 0 and c0 <= self.coordinates[row-1][0]) or ((row < len(self.coordinates) - 1 and c0 >= self.coordinates[row+1][0]))):
            return
        else:
            selectedCoordinates = self.getSelectedCoordinates()        
            self.beginResetModel()        
            self.coordinates[row][0] = c0
            self.coordinates[row][1] = int(c1)
            self.endResetModel()
            self.computePolyfit()
            selection = QItemSelection()
            for i,c in enumerate(self.coordinates):
                if c in selectedCoordinates:
                    selection.merge(QItemSelection(self.createIndex(i,0),self.createIndex(i,1)),QItemSelectionModel.Select)
            self.app.aw.ui.tableView.selectionModel().select(selection,QItemSelectionModel.Select)
            self.app.contentModified()

        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole or role ==  Qt.EditRole:
            return self.getVisibleCoordinates()[index.row()][index.column()]
        # set cell color base on value
        elif role == Qt.BackgroundColorRole:
            raw_tonino_value = self.coordinates[index.row()][0]
            tonino_value = self.coordinates[index.row()][1]
            if raw_tonino_value < self.app.aw.ui.widget.canvas.x_min or raw_tonino_value > self.app.aw.ui.widget.canvas.x_max or tonino_value > 200 or tonino_value < 0:
                return None
            else:
                return QBrush(QColor(234,229,216))
        elif role == Qt.TextAlignmentRole:
            if index.column() == 0:
                return Qt.AlignRight | Qt.AlignVCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
        else:
            return None
    
    def setData(self, index, value, role=Qt.EditRole):
        if value and value != "" and index.isValid() and 0 <= index.row() < len(self.coordinates) and index.column() >= 0 and index.column() < 2:
            if index.column() == 0:
                # convert to int
                try:
                    self.setVisibleCoordinate(index.row(),index.column(),int(value))
                    self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
                    # trigger the redraw of the matplotlib graph canvas
                    self.computePolyfit()
                    self.app.contentModified()
                except:
                    pass
            elif index.column() == 1:
                self.setVisibleCoordinate(index.row(),index.column(),value)
                self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
                # trigger the redraw of the matplotlib graph canvas
                self.app.aw.ui.widget.canvas.redraw()
                self.app.contentModified()
            return True
        return False    
    
    def setHeaderData(self,section, orientation, value, role):
        return True
        
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.app.aw.tableheaders[col]
        else:
            return None
        
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
        
        
    def sort(self, col, order):
        self.sortCoordinates(col+1,order)

       

#
# Table cell validator
#   
        
class ValidatedItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        QStyledItemDelegate.__init__(self,parent)
    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0
        if index.column() == 0: #only on the cells in the first column
            editor = QLineEdit(widget)
            # accept only numbers from 0-200
            validator = QRegExpValidator(QRegExp("200|1\d\d|\d\d|\d"), editor)
            editor.setValidator(validator)
            return editor
        return super(ValidatedItemDelegate, self).createEditor(widget, option, index)
