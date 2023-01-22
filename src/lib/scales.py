#!/usr/bin/python
#
# scales.py
#
# Copyright (c) 2022, Paul Holleis, Marko Luther
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



from PyQt6.QtCore import (Qt, QTimer, QAbstractTableModel, QItemSelection,
                          QItemSelectionModel, QModelIndex, QObject, QLocale)
from PyQt6.QtGui import (QBrush, QColor, QDoubleValidator)
from PyQt6.QtWidgets import (QStyledItemDelegate,QLineEdit, QWidget)
import numpy as np
import numpy.polynomial.polynomial as poly
import locale
import random
import math

from lib import __version__

import logging
from typing import Final, Optional, Any

_log: Final = logging.getLogger(__name__)

class Scales(QAbstractTableModel):

    __slots__ = [ 'app', 'defaultCoefficients', 'deviceCoefficients', 'coefficients', 'RR', 'coordinates', 'polyfit_degree' ]

    def __init__(self, app, parent:QObject, *args) -> None:
        QAbstractTableModel.__init__(self,parent,*args)
        self.app = app
        self.defaultCoefficients:list[float] = [.0, .0, 102.2727273, -128.4090909] # x3, x2, x, c
        self.deviceCoefficients:Optional[list[float]] = None
        # coefficients are recomputed on loading/setting from coordinates if possible (eg. coordinates are given)
        self.coefficients:Optional[list[float]] = None
        self.RR:Optional[float] = None
        self.coordinates:list[list[Any]] = [] # list of tuples [x,y,name,r] with x the internal Tonino calue, y the target value, name and the epoc of creation or a random number
        self.polyfit_degree:int = 0
        # initialize random number generator
        random.seed()

    def computeT(self, x:float) -> float:
        return float(np.poly1d(self.deviceCoefficients or self.coefficients or self.defaultCoefficients)([x])[0])

    # accessors and selectors

    def getVisibleCoordinates(self) -> list[list[Any]]:
        if self.coordinates:
            return [c[1:3] for c in self.coordinates]
        else:
            return []

    def setVisibleCoordinate(self, row:int, column:int, value:float) -> None:
        self.coordinates[row][column+1] = value

    def getCoordinates(self) -> list[list[Any]]:
        return self.coordinates

    def getSelectedCoordinates(self) -> list[list[Any]]:
        if self.app.aw is not None:
            selectedRows = self.app.aw.getSelectedRows()
            return [item for i,item in enumerate(self.coordinates) if i in selectedRows]
        return []

    # compute the coefficients of the given scale and apply to the current coordinates
    def applyScale(self,scale) -> None:
        # extract coordinates
        if 'coordinates' in scale:
            coordinates = scale['coordinates']
        else:
            coordinates = []
        # extract degree
        if 'degree' in scale:
            polyfit_degree = scale['degree']
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

    def setScale(self,scale: dict[str, Any]) -> None:
        self.beginResetModel()
        if 'coordinates' in scale:
            self.coordinates = scale['coordinates']
        else:
            self.coordinates = []
        prev_degree = self.polyfit_degree
        if 'degree' in scale:
            self.polyfit_degree = scale['degree']
            if self.app.aw is not None:
                self.app.aw.ui.degreeSlider.setValue(self.app.scales.getPolyfitDegree())
        self.endResetModel()
        if prev_degree == self.polyfit_degree:
            # the degree did not change and thus the Polyfit was not recomputed yet
            self.computePolyfit()

    def getScale(self) -> dict[str, Any]:
        scale:dict[str, Any] = {}
        scale['appVersion'] = __version__
        if self.coordinates:
            scale['coordinates'] = self.coordinates
        scale['degree'] = self.polyfit_degree
        return scale

    def sortCoordinates(self,col:int = 0, order:int = 0) -> None:
        selectedCoordinates = self.getSelectedCoordinates()
        self.beginResetModel()
        self.coordinates = sorted(self.coordinates, key=lambda c: c[col], reverse=bool(order))
        self.endResetModel()
        self.redoSelection(selectedCoordinates)
        self.app.contentModified()
        if self.app.aw is not None:
            self.app.aw.ui.tableView.repaint()

    def redoSelection(self,selectedCoordinates) -> None:
        selection:QItemSelection = QItemSelection()
        for i,c in enumerate(self.coordinates):
            if c in selectedCoordinates:
                selection.merge(QItemSelection(self.createIndex(i,0),self.createIndex(i,1)),QItemSelectionModel.SelectionFlag.Select)
        if self.app.aw is not None:
            self.app.aw.ui.tableView.selectionModel().select(selection,QItemSelectionModel.SelectionFlag.Select)

    # deletes the coordinates at the given positions
    def deleteCoordinates(self,positions) -> None:
        selectedCoordinates = self.getSelectedCoordinates()
        self.beginResetModel()
        self.coordinates[:] = [ item for i,item in enumerate(self.coordinates) if i not in positions]
        self.endResetModel()
        self.redoSelection(selectedCoordinates)
        self.app.contentModified()
        self.computePolyfit()

    def autoScroll(self) -> None:
        if self.app.aw is not None:
            QTimer.singleShot(0, self.app.aw.ui.tableView.scrollToBottom)

    # force a repaint of the table items
    def refresh(self)-> None:
        selectedCoordinates = self.getSelectedCoordinates()
        self.beginResetModel()
        self.endResetModel()
        self.redoSelection(selectedCoordinates)

    def addCoordinates(self,coordinates) -> None:
        _log.debug('addCoordinates(%s)',len(coordinates))
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

    def addCoordinate(self, x:float, y:int, name:str='') -> None:
        _log.debug('addCoordinate(%s,%s,%s)',x,y,name)
        y2:int
        if y == 0:
            # y from I_SCAN, we compute the T value
            y2 = self.float2float(self.computeT(x),2)
        else:
            y2 = self.float2float(y,2)
        if name == '':
            name = name or str(len(self.coordinates)+1)
#            name = f'{self.computeT(x):.1f}'
        new_coordinate = [x,y2,name,random.random()]
        self.beginResetModel()
        self.coordinates.append(new_coordinate)
        self.endResetModel()
        self.redoSelection([new_coordinate])
        self.app.contentModified()
        self.computePolyfit()
        self.autoScroll()

    @staticmethod
    def float2float(f, n=1):
        if f is None:
            return None
        f = float(f)
        if n==0:
            if math.isnan(f):
                return 0
            return int(round(f))
        res = float(f'%.{n}f'%f)
        if math.isnan(res):
            return 0.0
        return res

    def computePolyfit(self) -> None:
        if self.polyfit_degree and len(self.coordinates) > self.polyfit_degree:
            _log.debug('computePolyfit: %s',self.polyfit_degree)
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
            _log.debug('polyfit(%s)=%s',self.polyfit_degree,self.coefficients)
            # compute the inverse mapping
            ci, _ = poly.polyfit(yv,xv,self.polyfit_degree,full=True)
            _log.debug('inverse_polyfit(%s)=%s',self.polyfit_degree,list(reversed(list(ci))))
        else:
            self.coefficients = None
            self.setRR(None)
        if self.app.aw is not None:
            self.app.aw.setEnabledUploadButton()
            # trigger the redraw of the matplotlib graph canvas
            self.app.aw.ui.widget.canvas.updatePolyfit()

    def getCoefficients(self) -> Optional[list[float]]:
        return self.coefficients

    def setCoefficients(self,coefficients:Optional[list[float]]) -> None:
        self.coefficients = coefficients

    def getDeviceCoefficients(self) -> Optional[list[float]]:
        return self.deviceCoefficients

    def setDeviceCoefficients(self,coefficients:Optional[list[float]]) -> None:
        self.deviceCoefficients = coefficients
        # trigger the computation of the device curve redraw of the matplotlib graph canvas
        if self.app.aw is not None:
            self.app.aw.ui.widget.canvas.updateDevicePolyfit()

    def getDefaultCoefficents(self) -> list[float]:
        return self.defaultCoefficients

    def getRR(self) -> Optional[float]:
        return self.RR

    def setRR(self, RR:Optional[float]) -> None:
        self.RR = RR

    def setPolyfitDegree(self, d:int) -> None:
        self.polyfit_degree = d
        self.computePolyfit()

    def getPolyfitDegree(self) -> int:
        return self.polyfit_degree

    def clearCoordinates(self) -> None:
        self.beginResetModel()
        self.coordinates = []
        self.endResetModel()
        self.computePolyfit()
        self.app.contentCleared()

    def coordinates2text(self, coordinates:list[list[Any]]) -> str:
        lines = ["%s %d \"%s\""%(f'{c[0]:.7n}',c[1],c[2]) for c in coordinates]
        return '\n'.join([str(l) for l in lines])

    def line2coordinate(self, line:str) -> list[Any]:
        l = line.replace('\t',' ').split(' ',2)
        if len(l) == 2:
            return [locale.atof(l[0]),int(l[1]),'',random.random()]
        else:
            return [locale.atof(l[0]),int(l[1]),str(eval(l[2])),random.random()] # pylint: disable=eval-used

    def text2coordinates(self, txt:str) -> list[list[Any]]:
        return [self.line2coordinate(l) for l in txt.replace('\r','\n').split('\n')]


#
# QAbstractTableModel interface
#

    def rowCount(self, _parent:QModelIndex = QModelIndex()) -> int:
        return len(self.coordinates)

    def columnCount(self, _parent:QModelIndex = QModelIndex()) -> int:
        if self.app.aw is not None:
            return len(self.app.aw.tableheaders)
        return 0

    # updates the element at row with values c0 and c1 for the first two column values
    def updateCoordinate(self, row:int, c0:float, c1:float) -> None:
        # respect the limits
        # NOSORT
        if False and ((row > 0 and c0 <= self.coordinates[row-1][0]) or (row < len(self.coordinates) - 1 and c0 >= self.coordinates[row+1][0])):
            return
        else:
            selectedCoordinates = self.getSelectedCoordinates()
            self.beginResetModel()
            self.coordinates[row][0] = c0
            self.coordinates[row][1] = float(f'{c1:.2f}'.rstrip('0').rstrip('.'))
            self.endResetModel()
            self.computePolyfit()
            selection:QItemSelection = QItemSelection()
            for i,c in enumerate(self.coordinates):
                if c in selectedCoordinates:
                    selection.merge(QItemSelection(self.createIndex(i,0),self.createIndex(i,1)),QItemSelectionModel.SelectionFlag.Select)
            if self.app.aw is not None:
                self.app.aw.ui.tableView.selectionModel().select(selection,QItemSelectionModel.SelectionFlag.Select)
                self.app.contentModified()

    def data(self, index:QModelIndex, role:int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                v = self.getVisibleCoordinates()[index.row()][index.column()]
                if role == Qt.ItemDataRole.EditRole:
                    return f'{v:.2f}'.rstrip('0').rstrip('.')
                else:
                    return f'{v:.1f}'
            else:
                return self.getVisibleCoordinates()[index.row()][index.column()]
        # set cell color base on value
        elif role == Qt.ItemDataRole.BackgroundRole:
            raw_tonino_value = self.coordinates[index.row()][0]
            tonino_value = self.coordinates[index.row()][1]
            if self.app.aw is None or (raw_tonino_value < self.app.aw.ui.widget.canvas.x_min or raw_tonino_value > self.app.aw.ui.widget.canvas.x_max or tonino_value > 250 or tonino_value < 0):
                return None
            elif self.app.darkmode:
                return QBrush(QColor(80,80,80))
            else:
                return QBrush(QColor(234,229,216))
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column() == 0:
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            else:
                return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        else:
            return None
#            return super().data(index, role)

    def setData(self, index:QModelIndex, value:Any, _role:int=Qt.ItemDataRole.EditRole) -> bool:
        if value and value != '' and index.isValid() and 0 <= index.row() < len(self.coordinates) and index.column() >= 0 and index.column() < 2:
            if index.column() == 0:
                try:
                    self.setVisibleCoordinate(index.row(),index.column(),float(value))
                    self.dataChanged.emit(index, index, []) # type: ignore
                    # trigger the redraw of the matplotlib graph canvas
                    self.computePolyfit()
                    self.app.contentModified()
                except Exception: # pylint: disable=broad-except
                    pass
            elif index.column() == 1:
                self.setVisibleCoordinate(index.row(),index.column(),value)
                #self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
                self.dataChanged.emit(index, index, []) # type: ignore
                # trigger the redraw of the matplotlib graph canvas
                if self.app.aw is not None:
                    self.app.aw.ui.widget.canvas.redraw()
                self.app.contentModified()
            return True
        return False

    def setHeaderData(self, _section:int, _orientation:Qt.Orientation, _value:Any, _role:int=Qt.ItemDataRole.EditRole) -> bool:
        return True

    def headerData(self, col:int, orientation:Qt.Orientation, role:int=Qt.ItemDataRole.DisplayRole) -> Optional[str]:
        if self.app.aw is not None and orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.app.aw.tableheaders[col]
        return None

    def flags(self, _index:QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable

    def sort(self, col:int, order:Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        self.sortCoordinates(col+1,order == Qt.SortOrder.AscendingOrder)


#
# Table cell validator
#

class ValidatedItemDelegate(QStyledItemDelegate):

    def __init__(self, parent:Optional[QObject]=None) -> None:
        QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, widget, option, index:QModelIndex) -> QWidget:
        if not index.isValid():
            return QWidget()
        if index.column() == 0: #only on the cells in the first column
            editor = QLineEdit(widget)
            # accept only numbers from 0-200
            validator = QDoubleValidator(0., 200., 2, editor)
            validator.setLocale(QLocale.c())
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            editor.setValidator(validator)
            return editor
        return super().createEditor(widget, option, index)
