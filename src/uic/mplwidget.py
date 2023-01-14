#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# mplwidget.py
#
# Copyright (c) 2023, Paul Holleis, Marko Luther
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


import matplotlib as mpl # type: ignore

import PyQt6   # @UnusedImport # for mypy typechecking
from PyQt6.QtWidgets import (QSizePolicy, QMenu, QWidget, QVBoxLayout)
from PyQt6.QtGui import (QCursor, QAction)
from PyQt6.QtCore import (Qt,pyqtSlot, QObject)
mpl.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas  # type: ignore
    
from matplotlib.figure import Figure # type: ignore
from matplotlib import rcParams, patheffects, patches # type: ignore
import numpy as np

import logging
from typing import Final, Optional, Any, Tuple

_log: Final = logging.getLogger(__name__)


class MyQAction(QAction):
    def __init__(self, parent:QObject):
        QAction.__init__(self, parent)
        self._key:Optional[tuple[str,float,float]] = None

    def get_key(self) -> Optional[tuple[str,float,float]]:
        return self._key
        
    def set_key(self, value:Optional[tuple[str,float,float]]) -> None:
        self._key = value
    
    key = property(
        fget=get_key,
        fset=set_key
    )

class MplCanvas(FigureCanvas):
    def __init__(self,app) -> None:
        self.app = app
        
        self.x_step:Final = 0.01
        
        self.y_min:Final = 0
        self.y_max:Final = 155
        
        self.x_min_valid:Final = 1.7444
        self.x_max_valid:Final = 2.526666665904
        self.x_SCA_cupping:Final = 2.2807
        
        self.x_max_dark:Final = 1.9729638719
        self.x_max_medium_dark:Final = 2.1152140938
        self.x_max_medium:Final = 2.2444417479
        self.x_max_medium_light:Final = 2.3610963746
        
        # minimum raw Tonino value to be drawn
        self.x_min:Final = self.x_min_valid-0.15 # minimum raw Tonino value to be drawn
        # maximum raw Tonino value to be drawn
        self.x_max:Final = self.x_max_valid+0.15 # maximum raw Tonino value to be drawn

        self.xvalues:np.ndarray[Any, np.dtype[np.floating[Any]]] = np.arange(self.x_min, self.x_max, self.x_step)
        self.yvalues:Optional[np.ndarray[Any, np.dtype[Any]]] = None # is set by update from the polyfit coefficent
        self.yvalues_default:Optional[np.ndarray[Any, np.dtype[Any]]] = None # the default Tonino polyfit curve
        self.yvalues_device:Optional[np.ndarray[Any, np.dtype[Any]]] = None # the device polyfit curve
        
        self.lastMotionX:Optional[float] = None # holds the last x value on mouse movements if any
        self.lastMotionY:Optional[float] = None # holds the last y value on mouse movements if any
               
        self.fig = Figure()
        self.fig.patch.set_facecolor('white')
        self.fig.patch.set_alpha(1.0)
        
        self.annotations:list[Any] = []
        self.indexpoint:Optional[int] = None
        self.mousepress:bool = False
        self.mousedragged:bool = False
        
        # offsets for annotations
        self.xoffset:float = 0.04
        self.yoffset:float = 15
        
        # Tonino color scheme
        self.toninoGray:list[float] = self.toninoColor(92,93,97)
        self.toninoBlue:list[float] = self.toninoColor(74,83,102)
        self.toninoLightBlue:list[float] = self.toninoColor(74,83,102)
        self.toninoRed:list[float] = self.toninoColor(174,33,64)

        # xkcd design settings
        self.RRfontSize:float = 16.0
        rcParams['font.family'] = ['Comic Sans MS']
        rcParams['font.size'] = 14.0
        rcParams['path.effects'] = [
            patheffects.withStroke(linewidth=4, foreground="w")]
        rcParams['axes.linewidth'] = 1.5
        rcParams['lines.linewidth'] = 2.0
        rcParams['figure.facecolor'] = 'white'
        rcParams['grid.linewidth'] = 0.0
        rcParams['axes.unicode_minus'] = False
        rcParams['xtick.major.size'] = 8
        rcParams['xtick.major.width'] = 3
        rcParams['ytick.major.size'] = 8
        rcParams['ytick.major.width'] = 3

        # create and configure axes
        self.ax = self.fig.add_axes((0.1, 0.1, 0.8, 0.8))
        self.ax.spines['right'].set_color('none')
        self.ax.spines['top'].set_color('none')
        self.ax.spines['left'].set_sketch_params(1.2,120.,2.) # scale (amplitude), length (along the line), randomness (shrunk/expanding scale factor)
        self.ax.spines['bottom'].set_sketch_params(1.2,200.,2.)     
        self.ax.spines['left'].set_color(self.toninoBlue) 
        self.ax.spines['bottom'].set_color(self.toninoBlue) 
        self.ax.tick_params(\
            color=self.toninoBlue,
            axis='x',           # changes apply to the x-axis
            which='both',       # both major and minor ticks are affected
            bottom=False,       # ticks along the bottom edge are off
            top=False,          # ticks along the top edge are off
            labelbottom=False,  # labels along the bottom edge are off
            )    
        self.ax.tick_params(\
            color=self.toninoBlue,
            axis='y', 
            which='both',
            right=False,
            direction="out",    # draw the ticks outside of the graph
            labelright=False) 
        self.ax.set_ylim([self.y_min, self.y_max])
        self.ax.set_xlim([self.x_min, self.x_max])
        for t in self.ax.yaxis.get_ticklabels():
            t.set_color(self.toninoBlue)

        # compute the yvalues of the default Tonino scale
        self.yvalues_default = np.poly1d(self.app.scales.getDefaultCoefficents())(self.xvalues)
                
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,  #@UndefinedVariable
                                QSizePolicy.Policy.Expanding,
                                QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)  #@UndefinedVariable
        
        # connect signals
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick) 
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        # draw initial graph
        self.redraw()

    def toninoColor(self,r:int,g:int,b:int) -> list[float]:
        return [r/255.,g/255.,b/255.]

    def updatePolyfit(self) -> None:
        # updates the polyfit line data and calls redraw
        c:Optional[list[float]] = self.app.scales.getCoefficients()
        if c is None:
            self.yvalues = None
        else:
            self.yvalues = np.poly1d(np.array(c))(self.xvalues)
           
        RR:Optional[float] = self.app.scales.getRR() 
        if RR is not None:
            self.ax.set_title("d = %d   RR = %.3f"%(self.app.scales.polyfit_degree,RR), fontsize=self.RRfontSize, color=self.toninoBlue)
        else:
            self.ax.set_title("")
        self.redraw()

    def updateDevicePolyfit(self) -> None:
        # updates the device polyfit line data and calls redraw
        c:Optional[list[float]] = self.app.scales.getDeviceCoefficients()
        if c is None:
            self.yvalues_device = None
        else:
            self.yvalues_device = np.poly1d(np.array(c))(self.xvalues)
        # we do a full redraw to ensure that the default/device curve is redrawn
        self.redraw()

    def rightLowerOffset(self,x:float, y:float) -> Tuple[float,float]:
        return x + self.xoffset, y - 2*self.yoffset

    def leftLowerOffset(self,x:float ,y:float) -> Tuple[float,float]:
        return x - 2*self.xoffset,y - 2*self.yoffset

    def rightUpperOffset(self,x:float, y:float) -> Tuple[float,float]:
        return x + 1.5*self.xoffset,y + 1.5*self.yoffset

    def leftUpperOffset(self,x:float, y:float) -> Tuple[float,float]:
        return x - 2*self.xoffset,y + self.yoffset

    def annotationPosition(self, coordinates: list[list[Any]], i:int, c:list[float]) -> Tuple[float,float]:
        x:float = c[0]
        y:float = c[1]
        if i == 0:
            # first
            if len(coordinates) > 1 and coordinates[1][1] > c[1]:
                # there are others
                x,y = self.rightLowerOffset(x,y)
            else:
                x,y = self.rightUpperOffset(x,y)
        elif i == len(coordinates) - 1:
            # last
            if len(coordinates) > 1 and coordinates[i-1][1] > c[1]:
                # there are others
                x,y = self.rightUpperOffset(x,y)
            else:
                x,y = self.rightLowerOffset(x,y)
        else:
            # middle
            pv:float = coordinates[i-1][1]
            nv:float = coordinates[i+1][1]
            if pv < c[1] and c[1] < nv:
                x,y = self.rightLowerOffset(x,y)
            elif pv < c[1] and c[1] > nv:
                x,y = self.rightUpperOffset(x,y)
            else:
                x,y = self.leftLowerOffset(x,y)
        return x,y

    def annotate_rectangle(self,rect,text:str) -> None:
        rx:float # pylint: disable=unused-variable
        ry:float # pylint: disable=unused-variable
        rx, ry = rect.get_xy()
        cx:float = rx + rect.get_width()/2.0
        cy:float = ry + rect.get_height()/20
        self.ax.annotate(text, (cx, cy),
            color=(0.4,0.4,0.4), 
            fontsize=10, 
            ha='center', 
            va='center',
            path_effects=[])

    def redraw(self) -> None:
        # remove all annotations
        for a in self.annotations:
            a.remove()
        self.annotations = []
        
        while len(self.ax.lines) > 0:
            self.ax.lines[0].remove()
        while len(self.ax.patches) > 0:
            self.ax.patches[0].remove()
        
        # draw dark region
        dark_rect = patches.Rectangle(
            (self.x_min_valid,self.y_min),
            width=(self.x_max_dark - self.x_min_valid),
            height=(self.y_max - self.y_min),
            color=(0.86,0.86,0.86),
            linewidth=None,
            sketch_params=None,
            path_effects=[],
            )
        self.ax.add_patch(dark_rect)
        self.annotate_rectangle(dark_rect,"dark")
        
        # draw medium dark region
        medium_dark_rect = patches.Rectangle(
            (self.x_max_dark,self.y_min),
            width=(self.x_max_medium_dark - self.x_max_dark),
            height=(self.y_max - self.y_min),
            color=(0.89,0.89,0.89),
            linewidth=None,
            sketch_params=None,
            path_effects=[],
            )
        self.ax.add_patch(medium_dark_rect)
        self.annotate_rectangle(medium_dark_rect,"medium\ndark")
        
        # draw medium region
        medium_rect = patches.Rectangle(
            (self.x_max_medium_dark,self.y_min),
            width=(self.x_max_medium - self.x_max_medium_dark),
            height=(self.y_max - self.y_min),
            color=(0.92,0.92,0.92),
            linewidth=None,
            sketch_params=None,
            path_effects=[],
            )
        self.ax.add_patch(medium_rect)
        self.annotate_rectangle(medium_rect,"medium")
        
        # draw medium light region
        medium_light_rect = patches.Rectangle(
            (self.x_max_medium,self.y_min),
            width=(self.x_max_medium_light - self.x_max_medium),
            height=(self.y_max - self.y_min),
            color=(0.95,0.95,0.95),
            linewidth=None,
            sketch_params=None,
            path_effects=[],
            )
        self.ax.add_patch(medium_light_rect)
        self.annotate_rectangle(medium_light_rect,"medium\nlight")
        
        # draw  light region
        light_rect = patches.Rectangle(
            (self.x_max_medium_light,self.y_min),
            width=(self.x_max_valid - self.x_max_medium_light),
            height=(self.y_max - self.y_min),
            color=(0.98,0.98,0.98),
            linewidth=None,
            sketch_params=None,
            path_effects=[],
            )
        self.ax.add_patch(light_rect)
        self.annotate_rectangle(light_rect,"light")
        
        # draw SCA cupping line
        self.ax.axvline(self.x_SCA_cupping,
            color = (0.7,0.7,0.7),
            linestyle = '-',
            linewidth= 2, 
            alpha = .5,
            sketch_params=None,
            path_effects=[]
            )
        
        # add default Tonino curve
        if self.yvalues_device is None:
            self.ax.plot(self.xvalues, self.yvalues_default,color=self.toninoGray,linewidth=1,path_effects=[])

        # add device curve if available
        if self.yvalues_device is not None:
            self.ax.plot(self.xvalues, self.yvalues_device,color=self.toninoBlue)

        # add polyfit curve
        if self.yvalues is not None:
            self.ax.plot(self.xvalues,self.yvalues,color=self.toninoRed)

        # draw annotations at selected coordinates
        if self.app.aw:
            selectedCoordinates:list[list[Any]] = self.app.scales.getSelectedCoordinates()
            coordinates:list[list[Any]] = self.app.scales.getCoordinates()
            annotation_added:list[list[Any]] = [] # coordinates that we already painted the annotation
            for i, c in enumerate(coordinates):
                if  len(c) > 1 and c[2] and c in selectedCoordinates and not c in annotation_added:
                    annotation_added.append(c)
                    x:float
                    y:float
                    x,y = self.annotationPosition(coordinates,i,c)
                    an = self.ax.annotate(c[2],xy=(c[0],c[1]),xytext=(x,y),color=self.toninoGray,
                    arrowprops=dict(shrinkB=5,connectionstyle="arc3,rad=0.2",arrowstyle='->',color=self.toninoGray,relpos=(0,0)))
                    self.annotations.append(an)
            # draw coordinates
            if len(coordinates) > 0:
                cx:list[float] = [c[0] for c in coordinates]
                cy:list[float] = [c[1] for c in coordinates]
                self.ax.plot(cx,cy,color=self.toninoBlue,marker = "o",picker=10,linestyle='', markerfacecolor=self.toninoBlue,markersize=8)
        self.draw()

    def closeToCoordinate(self,event) -> bool:
        res:bool = False
        for c in self.app.scales.getCoordinates():
            if event.xdata and event.ydata and (abs(c[0] - event.xdata) < 0.01 and abs(c[1] - event.ydata) < 3):
                res = True
                break
        return res

    def on_motion(self,event) -> None:
        if not event.inaxes: return
        try:
            if self.lastMotionX and self.lastMotionY and (abs(self.lastMotionX - event.xdata) > 0.01 or abs(self.lastMotionY - event.ydata) > 2):
                self.lastMotionX = None
                self.lastMotionY = None
                self.redraw()
                self.setCursor(Qt.CursorShape.ArrowCursor)
            if self.mousepress:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.mousedragged = True
                self.app.scales.updateCoordinate(self.indexpoint,event.xdata,event.ydata)
            elif not self.lastMotionX and not self.lastMotionY and self.closeToCoordinate(event):
                self.lastMotionX = event.xdata
                self.lastMotionY = event.ydata
                self.setCursor(Qt.CursorShape.OpenHandCursor)
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)

    def on_pick(self,event) -> None:
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        try:
            self.indexpoint = event.ind[-1]
        except Exception: # pylint: disable=broad-except
            self.indexpoint = event.ind
        self.mousepress = True

    def on_release(self,event) -> None:
        if self.mousepress:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            if self.mousedragged:
                self.mousedragged = False
            else:
                self.app.aw.toggleSelection(self.indexpoint)
        self.mousepress = False
        self.indexpoint = None
        self.app.scales.computePolyfit()
        if  self.closeToCoordinate(event):
            self.lastMotionX = event.xdata
            self.lastMotionY = event.ydata
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def onclick(self,event) -> None:
        if event.inaxes and event.button==3:
            # populate menu
            menu:QMenu = QMenu(self) 
            ac:MyQAction = MyQAction(menu)
            ac.setText(self.app.aw.popupadd)
            ac.key = ("add",event.xdata,event.ydata)
            menu.addAction(ac)
            if (self.lastMotionX and self.lastMotionY):
                ac = MyQAction(menu)
                ac.setText(self.app.aw.popupdelete)
                ac.key = ("delete",event.xdata,event.ydata)
                menu.addAction(ac)
            self.mousepress = False
            self.indexpoint = None
            # show menu
            menu.triggered.connect(self.event_popup_action) # type: ignore
            menu.popup(QCursor.pos())

    @pyqtSlot("QAction*")
    def event_popup_action(self, action:MyQAction) -> None:
        if action.key[0] == "add":
            self.app.scales.addCoordinate(action.key[1],action.key[2])
        elif action.key[0] == "delete":
            for i,c in enumerate(self.app.scales.getCoordinates()):
                if abs(c[0] - action.key[1]) < 0.05 and abs(c[1] - action.key[2]) < 3:
                    self.app.scales.deleteCoordinates([i])
                    break


class mplwidget(QWidget):
    def __init__(self, parent:Optional[QWidget] = None):
        QWidget.__init__(self, parent)
        if (parent and parent.parent() and parent.parent().parent()):
            self.app = parent.parent().parent().app # type: ignore
        else:
            self.app = None
        self.canvas = MplCanvas(self.app)
        self.vbl:QVBoxLayout = QVBoxLayout()
        self.vbl.setContentsMargins(1,1,1,1)
        self.vbl.setSpacing(0) 
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)


