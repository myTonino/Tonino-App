#!/usr/bin/python3
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
from PyQt6.QtWidgets import (QStyledItemDelegate,QLineEdit, QWidget, QStyleOptionViewItem)
import numpy as np
import numpy.polynomial.polynomial as poly
import numpy.typing as npt
import locale
import random
import math
from ast import literal_eval

from lib import __version__

import logging
from typing import Final, Any, NamedTuple, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from lib.main import Tonino # pylint: disable=unused-import

_log: Final = logging.getLogger(__name__)

# TypedDicts are mutable
class Scale(TypedDict):
    coordinates: list[list[float | str]] # list of either [x:float, y:float, name:str] or [x:float, y:float, name:str, id:float]
    appVersion: str
    degree: int

# NamedTuples are immutable!
class Coordinate(NamedTuple):
    x: float  # internal Tonino value
    y: float  # target Value
    name: str
    uid: float # a random number


class Scales(QAbstractTableModel):

    __slots__ = [ 'app', 'defaultCoefficients', 'deviceCoefficients', 'coefficients', 'RR', 'coordinates', 'polyfit_degree' ]

    def __init__(self, app: 'Tonino', parent:QObject) -> None:
        QAbstractTableModel.__init__(self, parent)
        self.app = app
        self.defaultCoefficients:list[float] = [.0, .0, 102.2727273, -128.4090909] # x3, x2, x, c
        self.deviceCoefficients:list[float] | None = None
        # coefficients are recomputed on loading/setting from coordinates if possible (eg. coordinates are given)
        self.coefficients:list[float] | None = None
        self.RR:float | None = None
        self.coordinates:list[Coordinate] = []
        self.polyfit_degree:int = 0
        # initialize random number generator
        random.seed()

    def computeT(self, x:float) -> float:
        return max(0,float(np.poly1d(self.deviceCoefficients or self.coefficients or self.defaultCoefficients)([x])[0]))

    # accessors and selectors

    # returns coordinate
    def setCoordinateY(self, row:int, y:float) -> None:
        self.coordinates[row] = Coordinate(self.coordinates[row].x, y, self.coordinates[row].name, random.random())

    def setCoordinateName(self, row:int, name:str) -> None:
        self.coordinates[row] = Coordinate(self.coordinates[row].x, self.coordinates[row].y, name, random.random())

    def getCoordinates(self) -> list[Coordinate]:
        return self.coordinates

    def getSelectedCoordinates(self) -> list[Coordinate]:
        if self.app.aw is not None:
            selectedRows = self.app.aw.getSelectedRows()
            return [item for i,item in enumerate(self.coordinates) if i in selectedRows]
        return []

    # compute the coefficients of the given scale and apply to the current coordinates
    def applyScale(self, scale:Scale) -> None:
        # extract coordinates
        coordinates: list[list[float | str]] = scale['coordinates'] if 'coordinates' in scale else []
        # extract degree
        polyfit_degree:int = scale['degree'] if 'degree' in scale else 1
        # compute polyfit
        if len(coordinates) > polyfit_degree:
            xv:npt.NDArray[np.float64] = np.array([e[0] for e in coordinates])
            yv:npt.NDArray[np.float64] = np.array([e[1] for e in coordinates])
            coefficients:list[float]
            coefficients = poly.polyfit(xv,yv,polyfit_degree,full=False)
            coefficients.reverse()
            # apply polyfit
            self.beginResetModel()
            for i, co in enumerate(self.coordinates):
                x = co.x
                name:str = co.name
                newY:float = np.poly1d(coefficients)([x])[0]
                self.coordinates[i] = Coordinate(x, newY, name, random.random())
            self.endResetModel()
            # update Polyfit and trigger the redraw of the matplotlib graph canvas
            self.computePolyfit()

    def setScale(self, scale: Scale) -> None:
        self.beginResetModel()
        self.coordinates = []
        for c in scale['coordinates']:
            if len(c) > 2 and isinstance(c[0], float) and isinstance(c[1], int|float) and isinstance(c[2], str):
                self.coordinates.append(Coordinate(c[0], c[1], c[2], random.random()))
        prev_degree = self.polyfit_degree
        if 'degree' in scale:
            self.polyfit_degree = scale['degree']
            if self.app.aw is not None:
                self.app.aw.ui.degreeSlider.setValue(self.app.scales.getPolyfitDegree())
        self.endResetModel()
        if prev_degree == self.polyfit_degree:
            # the degree did not change and thus the Polyfit was not recomputed yet
            self.computePolyfit()

    def getScale(self) -> Scale:
        return Scale(
            appVersion = __version__,
            degree = self.polyfit_degree,
            coordinates = [[c.x, c.y, c.name] for c in self.coordinates])

    def sortCoordinates(self,col:int = 0, order:Qt.SortOrder | None = None) -> None:
        if order is None:
            order = Qt.SortOrder.AscendingOrder
        selectedCoordinates:list[Coordinate] = self.getSelectedCoordinates()
        self.beginResetModel()
        self.coordinates = sorted(self.coordinates, key=lambda c: c[col], reverse=bool(order))
        self.endResetModel()
        self.redoSelection(selectedCoordinates)
        self.app.contentModified()
        if self.app.aw is not None:
            self.app.aw.ui.tableView.repaint()

    def redoSelection(self, selectedCoordinates:list[Coordinate]) -> None:
        selection:QItemSelection = QItemSelection()
        for i,c in enumerate(self.coordinates):
            if c in selectedCoordinates:
                selection.merge(QItemSelection(self.createIndex(i,0),self.createIndex(i,1)),QItemSelectionModel.SelectionFlag.Select)
        if self.app.aw is not None:
            sm: QItemSelectionModel | None = self.app.aw.ui.tableView.selectionModel()
            if sm is not None:
                sm.select(selection,QItemSelectionModel.SelectionFlag.Select)

    # deletes the coordinates at the given positions
    def deleteCoordinates(self, positions:list[int]) -> None:
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

    def addCoordinates(self, coordinates:list[Coordinate]) -> None:
        _log.debug('addCoordinates(%s)',len(coordinates))
        selectedCoordinates = self.getSelectedCoordinates()
        self.beginResetModel()
        for new_coordinate in coordinates:
            self.coordinates.append(new_coordinate)
        self.endResetModel()
        self.redoSelection(selectedCoordinates)
        self.app.contentModified()
        self.computePolyfit()
        self.autoScroll()

    def addCoordinate(self, x:float, y:int, name:str='') -> None:
        _log.debug('addCoordinate(%s,%s,%s)',x,y,name)
        y2:float = self.float2float(self.computeT(x), 2) if y == 0 else float(y)
        if name == '':
            name = name or str(len(self.coordinates)+1)
        new_coordinate:Coordinate = Coordinate(x, y2, name, random.random())
        self.beginResetModel()
        self.coordinates.append(new_coordinate)
        self.endResetModel()
        self.redoSelection([new_coordinate])
        self.app.contentModified()
        self.computePolyfit()
        self.autoScroll()

    @staticmethod
    def float2float(f:float, n:int = 1) -> float:
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
            xv:npt.NDArray[np.float64] = np.array([c.x for c in self.coordinates])
            yv:npt.NDArray[np.float64] = np.array([c.y for c in self.coordinates])
            c:npt.NDArray[np.float64]
            stats:list[float]
            c, stats = poly.polyfit(xv,yv,self.polyfit_degree,full=True)
            try:
                r2:npt.NDArray[np.float64] = 1 - stats[0] / (yv.size * yv.var())
                if r2.size>0:
                    self.setRR(r2[0])
                else:
                    self.setRR(None)
            except Exception: # pylint: disable=broad-except
                self.setRR(None)
            self.coefficients = list(c)
            self.coefficients.reverse()
            if _log.isEnabledFor(logging.DEBUG):
                _log.debug('polyfit(%s)=%s',self.polyfit_degree,self.coefficients)
                # compute the inverse mapping
                ci:npt.NDArray[np.float64]
                ci = poly.polyfit(yv,xv,self.polyfit_degree,full=False)
                _log.debug('inverse_polyfit(%s)=%s',self.polyfit_degree,list(reversed(list(ci))))
        else:
            self.coefficients = None
            self.setRR(None)
        if self.app.aw is not None:
            self.app.aw.setEnabledUploadButton()
            # trigger the redraw of the matplotlib graph canvas
            self.app.aw.ui.widget.canvas.updatePolyfit()

    def getCoefficients(self) -> list[float] | None:
        return self.coefficients

    def setCoefficients(self,coefficients:list[float] | None) -> None:
        self.coefficients = coefficients

    def getDeviceCoefficients(self) -> list[float] | None:
        return self.deviceCoefficients

    def setDeviceCoefficients(self,coefficients:list[float] | None) -> None:
        self.deviceCoefficients = coefficients
        # trigger the computation of the device curve redraw of the matplotlib graph canvas
        if self.app.aw is not None:
            self.app.aw.ui.widget.canvas.updateDevicePolyfit()

    def getDefaultCoefficents(self) -> list[float]:
        return self.defaultCoefficients

    def getRR(self) -> float | None:
        return self.RR

    def setRR(self, RR:float | None) -> None:
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

    @staticmethod
    def coordinates2text(coordinates:list[Coordinate]) -> str:
        lines = [f"{c.x:.7n} {c.y:d} \"{c.name}\"" for c in coordinates]
        return '\n'.join([str(ll) for ll in lines])

    @staticmethod
    def line2coordinate(line:str) -> Coordinate:
        ll = line.replace('\t',' ').split(' ', 2)
        name = ''
        if len(ll)>2:
            name = str(literal_eval(ll[2]))
        return Coordinate(float(locale.atof(ll[0])), int(ll[1]), name, random.random())

    def text2coordinates(self, txt:str) -> list[Coordinate]:
        return [self.line2coordinate(ll) for ll in txt.replace('\r','\n').split('\n')]


#
# QAbstractTableModel interface
#

    def rowCount(self, _parent:QModelIndex = QModelIndex()) -> int: # noqa: B008
        return len(self.coordinates)

    def columnCount(self, _parent:QModelIndex = QModelIndex()) -> int: # noqa: B008
        if self.app.aw is not None:
            return len(self.app.aw.tableheaders)
        return 0

    # updates the element at row with values c0 and c1 for the first two column values
    def updateCoordinate(self, row:int, c0:float, c1:float) -> None:
        # respect the limits
        # NOSORT
#        if ((row > 0 and c0 <= self.coordinates[row-1][0]) or (row < len(self.coordinates) - 1 and c0 >= self.coordinates[row+1][0])):
#            return
        selectedCoordinates = self.getSelectedCoordinates()
        self.beginResetModel()
        self.coordinates[row] = Coordinate(c0, float(f'{c1:.2f}'.rstrip('0').rstrip('.')), self.coordinates[row].name, random.random())
        self.endResetModel()
        self.computePolyfit()
        selection:QItemSelection = QItemSelection()
        for i,c in enumerate(self.coordinates):
            if c in selectedCoordinates:
                selection.merge(QItemSelection(self.createIndex(i,0),self.createIndex(i,1)),QItemSelectionModel.SelectionFlag.Select)
        if self.app.aw is not None:
            sm: QItemSelectionModel | None = self.app.aw.ui.tableView.selectionModel()
            if sm is not None:
                sm.select(selection,QItemSelectionModel.SelectionFlag.Select)
                self.app.contentModified()

    def data(self, index:QModelIndex, role:int = Qt.ItemDataRole.DisplayRole) -> str | QBrush | int | None:
        if not index.isValid():
            return None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if index.column() == 0:
                v:float = self.getCoordinates()[index.row()].y
                if role == Qt.ItemDataRole.EditRole:
                    return f'{v:.2f}'.rstrip('0').rstrip('.')
                return f'{v:.1f}'
            if index.column() == 1:
                return self.getCoordinates()[index.row()].name
        # set cell color base on value
        elif role == Qt.ItemDataRole.BackgroundRole:
            raw_tonino_value = self.coordinates[index.row()].x
            tonino_value:float = self.coordinates[index.row()].y
            if self.app.aw is None or (raw_tonino_value < self.app.aw.ui.widget.canvas.x_min or raw_tonino_value > self.app.aw.ui.widget.canvas.x_max or tonino_value > 250 or tonino_value < 0):
                return None
            if self.app.darkmode:
                return QBrush(QColor(80,80,80))
            return QBrush(QColor(234,229,216))
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column() == 0:
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return None
#            return super().data(index, role)

    def setData(self, index:QModelIndex, value:Any, _role:int=Qt.ItemDataRole.EditRole) -> bool:
        if value and value != '' and index.isValid() and 0 <= index.row() < len(self.coordinates) and index.column() >= 0 and index.column() < 2:
            if index.column() == 0:
                try:
                    self.setCoordinateY(index.row(), float(value))
                    self.dataChanged.emit(index, index, []) # type: ignore
                    # trigger the redraw of the matplotlib graph canvas
                    self.computePolyfit()
                    self.app.contentModified()
                except Exception: # pylint: disable=broad-except
                    pass
            elif index.column() == 1:
                self.setCoordinateName(index.row(),value)
                #self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index)
                self.dataChanged.emit(index, index, []) # type: ignore
                # trigger the redraw of the matplotlib graph canvas
                if self.app.aw is not None:
                    self.app.aw.ui.widget.canvas.redraw()
                self.app.contentModified()
            return True
        return False

    @staticmethod
    def setHeaderData(_section:int, _orientation:Qt.Orientation, _value:Any, _role:int=Qt.ItemDataRole.EditRole) -> bool:
        return True

    def headerData(self, col:int, orientation:Qt.Orientation, role:int=Qt.ItemDataRole.DisplayRole) -> str | None:
        if self.app.aw is not None and orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.app.aw.tableheaders[col]
        return None

    @staticmethod
    def flags( _index:QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable

    def sort(self, col:int, order:Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        self.sortCoordinates(col+1, order)


#
# Table cell validator
#

class ValidatedItemDelegate(QStyledItemDelegate):

    def __init__(self, parent:QObject | None=None) -> None:
        QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, widget:QWidget|None, option:QStyleOptionViewItem, index:QModelIndex) -> QWidget|None:
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
