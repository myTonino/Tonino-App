#!/usr/bin/python3
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

from typing import Final, Any, TYPE_CHECKING

if TYPE_CHECKING:
    import PyQt6 # noqa: F401 # @UnusedImport # for mypy typechecking
    from lib.main import Tonino # @UnusedImport # pylint: disable=unused-import
    from lib.scales import Coordinate # @UnusedImport # pylint: disable=unused-import
    from matplotlib.backend_bases import Event # type: ignore # @UnusedImport # pylint: disable=unused-import

from PyQt6.QtWidgets import (QSizePolicy, QMenu, QWidget, QVBoxLayout)
from PyQt6.QtGui import (QCursor, QAction)
from PyQt6.QtCore import (Qt, pyqtSlot, QObject, QSemaphore)
mpl.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas  # type: ignore
    
from matplotlib.text import Text # type: ignore
from matplotlib.figure import Figure # type: ignore
from matplotlib import rcParams, patheffects, patches # type: ignore
from matplotlib.lines import Line2D # type: ignore
import numpy as np
import warnings
import os

import logging

from uic import resources

_log: Final = logging.getLogger(__name__)


class MyQAction(QAction):

    __slots__ = [ '_key' ]
    
    def __init__(self, parent:QObject) -> None:
        QAction.__init__(self, parent)
        self._key:tuple[str, float, float] | None = None

    def get_key(self) -> tuple[str, float, float] | None:
        return self._key
    
    def set_key(self, value:tuple[str, float, float] | None) -> None:
        self._key = value
    
    key:property = property(
        fget=get_key,
        fset=set_key)

class MplCanvas(FigureCanvas):

    __slots__ = [ 'app', 'redrawSemaphore', 'ax_background', 'ax_background_bounds', 'x_step', 'y_min', 'y_max', 'x_min_valid', 'x_max_valid', 
        'x_SCA_cupping', 'x_max_dark', 'l_polyfit', 'l_coordinates', 'l_title', 'toninoColors', 
        'x_max_medium_dark', 'x_max_medium', 'x_max_medium_light', 'x_min', 'x_max', 'xvalues', 'yvalues', 'yvalues_default', 'yvalues_device', 
        'lastMotionX', 'lastMotionY', 'toninoGray', 'toninoBlue', 'toninoLightBlue', 'toninoRed', 'lightBackgroundColor', 'darkBackgroundColor',
        'fig', 'annotations', 'indexpoint', 'mousepress', 'mousedragged', 'xoffset', 'yoffset', 'RRfontSize', 'ax' ]
    
    def __init__(self, app:'Tonino') -> None:
        self.app = app
        
        self.redrawSemaphore = QSemaphore(1)
        
        self.ax_background = None # canvas background for bit blitting
        self.ax_background_bounds:tuple[float] | None = None
        
        self.x_step:Final = 0.01
        
        self.y_min:Final = 15
        self.y_max:Final = 147
        
        self.x_min_valid:Final = 1.7444
        self.x_max_valid:Final = 2.526666665904
        self.x_SCA_cupping:Final = 2.2807
        
        # dynamic artists
        self.l_polyfit:Line2D | None = None
        self.l_coordinates:Line2D | None = None
        self.l_title:Text | None = None
        
        # upper limits of the roast names according to the Agtron scale mapping
        self.x_max_dark:Final = 1.95574986810893
        self.x_max_medium_dark:Final = 2.13434730482587
        self.x_max_medium:Final = 2.27176924538536
        self.x_max_medium_light:Final = 2.37938416691839
        
        # minimum raw Tonino value to be drawn
        self.x_min:Final = self.x_min_valid-0.15 # minimum raw Tonino value to be drawn
        # maximum raw Tonino value to be drawn
        self.x_max:Final = self.x_max_valid+0.15 # maximum raw Tonino value to be drawn

        self.xvalues:np.ndarray[Any, np.dtype[np.floating[Any]]] = np.arange(self.x_min, self.x_max, self.x_step)
        self.yvalues:np.ndarray[Any, np.dtype[Any]] | None = None # is set by update from the polyfit coefficent
        self.yvalues_default:np.ndarray[Any, np.dtype[Any]] | None = np.poly1d(self.app.scales.getDefaultCoefficents())(self.xvalues)  # the default Tonino polyfit curve
        self.yvalues_device:np.ndarray[Any, np.dtype[Any]] | None = None # the device polyfit curve
        
        self.lastMotionX:float | None = None # holds the last x value on mouse movements if any
        self.lastMotionY:float | None = None # holds the last y value on mouse movements if any
        
        # Tonino color scheme associating names to color pairs <light_mode_color, dark_mode_color>
        self.toninoColors:dict[str,tuple[list[float],list[float]]] = {
            'grey':      (self.makeColor(92,93,97), self.makeColor(184,186,194)),
            'blue':      (self.makeColor(74,83,102), self.makeColor(223,231,244)),
            'lightblue': (self.makeColor(74,83,102), self.makeColor(207,221,249)),
            'red':       (self.makeColor(174,33,64), self.makeColor(187,51,83)),
            'background':          (self.makeGreyColor(253), self.makeGreyColor(30)),            
            'dark_coffee':         (self.makeGreyColor(219), self.makeGreyColor(43)),
            'medium_dark_coffee':  (self.makeGreyColor(227), self.makeGreyColor(54)),
            'medium_coffee':       (self.makeGreyColor(235), self.makeGreyColor(69)),
            'medium_light_coffee': (self.makeGreyColor(242), self.makeGreyColor(89)),
            'light_coffee':        (self.makeGreyColor(249), self.makeGreyColor(107)),
            'cupping':             (self.makeGreyColor(178), self.makeGreyColor(214))
        }
               
        self.fig:Figure = Figure()
        
        self.annotations:list[Any] = []
        self.indexpoint:int | None = None
        self.mousepress:bool = False
        self.mousedragged:bool = False
        
        # offsets for annotations
        self.xoffset:float = 0.04
        self.yoffset:float = 9

        # xkcd design settings
        self.RRfontSize:float = 16.0
        
        resourcePath:str = resources.getResourcePath()
        dijkstra_font_path:str = resourcePath + 'dijkstra.ttf'
        if os.path.exists(dijkstra_font_path):
            mpl.font_manager.fontManager.addfont(dijkstra_font_path)
            rcParams['axes.unicode_minus'] = True
            rcParams['font.size'] = 13.0
            rcParams['font.family'] = ['Dijkstra']
        else:
            rcParams['font.family'] = ['Comic Sans MS']
            rcParams['font.size'] = 14.0
        
        rcParams['axes.linewidth'] = 1.5
        rcParams['lines.linewidth'] = 2.0
        rcParams['axes.unicode_minus'] = False
        rcParams['xtick.major.size'] = 8
        rcParams['xtick.major.width'] = 3
        rcParams['ytick.major.size'] = 8
        rcParams['ytick.major.width'] = 3

        # create and configure axes
        self.ax = self.fig.add_axes((0.1, 0.1, 0.8, 0.8))
        self.ax.grid(False)       
        
        self.ax.get_xaxis().set_visible(False)
        self.ax.spines[['right', 'top']].set_visible(False)
        self.ax.spines['left'].set_sketch_params(1.2,120.,2.) # scale (amplitude), length (along the line), randomness (shrunk/expanding scale factor)
        self.ax.spines['bottom'].set_sketch_params(1.2,200.,2.)
        self.ax.tick_params(\
            axis='x',           # changes apply to the x-axis
            which='both',       # both major and minor ticks are affected
            bottom=False,       # ticks along the bottom edge are off
            top=False,          # ticks along the top edge are off
            labelbottom=False,  # labels along the bottom edge are off
            )    
        self.ax.tick_params(\
            axis='y', 
            which='both',
            right=False,
            direction="out",    # draw the ticks outside of the graph
            labelright=False) 
        self.ax.set_ylim([self.y_min, self.y_max])
        self.ax.set_xlim([self.x_min, self.x_max])
        
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


    @staticmethod
    def makeColor(r:int,g:int,b:int) -> list[float]:
        return [r/255.,g/255.,b/255.]
    
    @staticmethod
    def makeGreyColor(c:int) -> list[float]:
        return MplCanvas.makeColor(c,c,c)
    
    def toninoColor(self, color:str) -> list[float]:
        if color in self.toninoColors:
            c = self.toninoColors[color]
            if self.app.darkmode:
                return c[1]
            return c[0]
        return self.makeColort(50,50,50)

    def updatePolyfit(self) -> None:
        # updates the polyfit line data and calls redraw
        c:list[float] | None = self.app.scales.getCoefficients()     
        if c is None:
            self.yvalues = None
        else:
            self.yvalues = np.poly1d(np.array(c))(self.xvalues)
        self.redraw()

    def updateDevicePolyfit(self) -> None:
        # updates the device polyfit line data and calls redraw
        c:list[float] | None = self.app.scales.getDeviceCoefficients()
        if c is None:
            self.yvalues_device = None
        else:
            self.yvalues_device = np.poly1d(np.array(c))(self.xvalues)
        # we do a full redraw to ensure that the default/device curve is redrawn
        self.redraw(force=True)

    def rightLowerOffset(self,x:float, y:float) -> tuple[float,float]:
        return x + self.xoffset, y - 1.5*self.yoffset

    def leftLowerOffset(self,x:float ,y:float) -> tuple[float,float]:
        return x - 2*self.xoffset,y - 2.5*self.yoffset

    def rightUpperOffset(self,x:float, y:float) -> tuple[float,float]:
        return x + self.xoffset,y + 2*self.yoffset

    def leftUpperOffset(self,x:float, y:float) -> tuple[float,float]:
        return x - 1.5*self.xoffset,y + self.yoffset

    def annotationPosition(self, coordinates: list['Coordinate'], i:int, c:'Coordinate') -> tuple[float,float]:
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

    def annotate_rectangle(self, rect:patches.Rectangle, text:str) -> None:
        rx:float # pylint: disable=unused-variable
        ry:float # pylint: disable=unused-variable
        rx, ry = rect.get_xy()
        cx:float = rx + rect.get_width()/2.0
#        cy:float = ry + rect.get_height() - rect.get_height()/15
        cy:float = ry 
        self.ax.annotate(text, (cx, cy),
            xytext=(cx, cy),
            color=self.toninoColor('grey'),
            fontsize=10, 
            ha='center', 
            va='top',
            path_effects=[])
    

    # if force is True a full redraw is issues, otherwise an incremental is preferered redraw
    def redraw(self, force:bool = False, annotations:bool = True) -> None:
        # we try to catch a lock if available but we do not wait
        if self.redrawSemaphore.tryAcquire(1,0):
            try:
                if self.ax_background is None or force or self.ax_background_bounds is None or self.ax_background_bounds != self.fig.bbox.bounds:
                    
                    # initialize all canvas elements
                    
                    blue = self.toninoColor('blue')
                    grey = self.toninoColor('grey')
                    background = self.toninoColor('background')
        
                    # set patch and ax facecolors
                    self.fig.patch.set_facecolor(background)
                    self.ax.set_facecolor(background)
                    
                    # set spine color and path effects
                    for spine in ['left', 'bottom']:
                        self.ax.spines[spine].set(
                            path_effects=[patheffects.withStroke(linewidth=2, foreground=background)],
                            color=grey)
                    
                    # set tick colors
                    self.ax.tick_params(axis='y', colors=grey)
                    
                    # set ticklabels color and path effects
                    for t in self.ax.yaxis.get_ticklabels():
                        t.set_color(grey)
                        t.set_path_effects([patheffects.withStroke(linewidth=2, foreground=background)])
                    
                    # remove all annotations
                    for a in self.annotations:
                        a.remove()
                    self.annotations = []
                    
                    while len(self.ax.lines) > 0:
                        self.ax.lines[0].remove()
                    while len(self.ax.patches) > 0:
                        self.ax.patches[0].remove()
                    
                    # draw dark region
                    dark_rect:patches.Rectangle = patches.Rectangle(
                        (self.x_min_valid,self.y_min),
                        width=(self.x_max_dark - self.x_min_valid),
                        height=(self.y_max - self.y_min),
                        color=self.toninoColor('dark_coffee'),
                        linewidth=None,
                        sketch_params=None,
                        path_effects=[],
                        )
                    self.ax.add_patch(dark_rect)
                    self.annotate_rectangle(dark_rect,"dark")
                    
                    # draw medium dark region
                    medium_dark_rect:patches.Rectangle = patches.Rectangle(
                        (self.x_max_dark,self.y_min),
                        width=(self.x_max_medium_dark - self.x_max_dark),
                        height=(self.y_max - self.y_min),
                        color=self.toninoColor('medium_dark_coffee'),
                        linewidth=None,
                        sketch_params=None,
                        path_effects=[],
                        )
                    self.ax.add_patch(medium_dark_rect)
                    self.annotate_rectangle(medium_dark_rect,"medium\ndark")
                    
                    # draw medium region
                    medium_rect:patches.Rectangle = patches.Rectangle(
                        (self.x_max_medium_dark,self.y_min),
                        width=(self.x_max_medium - self.x_max_medium_dark),
                        height=(self.y_max - self.y_min),
                        color=self.toninoColor('medium_coffee'),
                        linewidth=None,
                        sketch_params=None,
                        path_effects=[],
                        )
                    self.ax.add_patch(medium_rect)
                    self.annotate_rectangle(medium_rect,"medium")
                    
                    # draw medium light region
                    medium_light_rect:patches.Rectangle = patches.Rectangle(
                        (self.x_max_medium,self.y_min),
                        width=(self.x_max_medium_light - self.x_max_medium),
                        height=(self.y_max - self.y_min),
                        color=self.toninoColor('medium_light_coffee'),
                        linewidth=None,
                        sketch_params=None,
                        path_effects=[],
                        )
                    self.ax.add_patch(medium_light_rect)
                    self.annotate_rectangle(medium_light_rect,"medium\nlight")
                    
                    # draw  light region
                    light_rect:patches.Rectangle = patches.Rectangle(
                        (self.x_max_medium_light,self.y_min),
                        width=(self.x_max_valid - self.x_max_medium_light),
                        height=(self.y_max - self.y_min),
                        color=self.toninoColor('light_coffee'),
                        linewidth=None,
                        sketch_params=None,
                        path_effects=[],
                        )
                    self.ax.add_patch(light_rect)
                    self.annotate_rectangle(light_rect,"light")
                    
                    # draw SCA cupping line
                    self.ax.axvline(self.x_SCA_cupping,
                        color = self.toninoColor('cupping'),
                        linestyle = 'dashed',
                        linewidth= 2, 
                        alpha = .5,
                        sketch_params=None,
                        path_effects=[]
                        )
                    
                    if self.yvalues_device is None:
                        # add default Tonino curve
                        self.ax.plot(self.xvalues, self.yvalues_default, color=grey, linewidth=1, path_effects=[])
                    else:
                        # add device curve if available
                        self.ax.plot(self.xvalues, self.yvalues_device, color=blue)
                    
                    # initialize title artist
                    self.l_title = self.ax.set_title("", fontsize=self.RRfontSize, color=grey)
                    
                    # initialize dynamic polyfit curve
                    self.l_polyfit, = self.ax.plot([], [], color=self.toninoColor('red'),
                            path_effects=[patheffects.withStroke(linewidth=3, foreground=background)])
                    
                    # initialize dynamic coordinates
                    self.l_coordinates, = self.ax.plot([],[], color=blue, marker = "o", picker=10,linestyle='', markerfacecolor=blue, markersize=8,
                            path_effects=[patheffects.withStroke(linewidth=2, foreground=background)])
        
                    #plot
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')
                        self.fig.canvas.draw() # NOTE: this needs to be done NOW and not via draw_idle() at any time later, to avoid ghost lines
                            
                    # initialize bitblit background
                    self.ax_background = self.fig.canvas.copy_from_bbox(self.fig.bbox)
                    self.ax_background_bounds = self.fig.bbox.bounds
                
                # restore background
                self.fig.canvas.restore_region(self.ax_background)
                
                if self.l_title is not None:
                    RR:float | None = self.app.scales.getRR()
                    if RR is not None:
                        self.l_title.set_text(f"d = {self.app.scales.polyfit_degree:d}   RR = {RR:.3f}")
                    else:
                        self.l_title.set_text("")
                    self.ax.draw_artist(self.l_title)
                
                # add dynamic polyfit curve
                if self.l_polyfit is not None:
                    if self.yvalues is not None:
                        self.l_polyfit.set_data(self.xvalues,self.yvalues)
                    else:
                        self.l_polyfit.set_data([], [])
                    self.ax.draw_artist(self.l_polyfit)

                coordinates:list['Coordinate'] = self.app.scales.getCoordinates()
                # draw coordinates
                if self.l_coordinates is not None:
                    cx:list[float] = [c[0] for c in coordinates]
                    cy:list[float] = [c[1] for c in coordinates]
                    self.l_coordinates.set_data(cx, cy)
                    self.ax.draw_artist(self.l_coordinates)
                if annotations:
                    # draw annotations at selected coordinates
                    selectedCoordinates:list['Coordinate'] = self.app.scales.getSelectedCoordinates()
                    annotation_added:list['Coordinate'] = [] # coordinates that we already painted the annotation
                    grey = self.toninoColor('grey')
                    background = self.toninoColor('background')
                    for i, c in enumerate(coordinates):
                        if  len(c) > 1 and c[2] and c in selectedCoordinates and c not in annotation_added:
                            annotation_added.append(c)
                            x:float
                            y:float
                            x,y = self.annotationPosition(coordinates,i,c)
                            an = self.ax.annotate(c[2],xy=(c[0],c[1]),xytext=(x,y),color=grey,
                                arrowprops={'shrinkB': 5, 'connectionstyle': 'arc3,rad=0.2', 'arrowstyle': '->', 'color': grey, 'relpos': (0,0)},
                                path_effects=[patheffects.withStroke(linewidth=2, foreground=background)])
                            self.ax.draw_artist(an)
                            self.annotations.append(an)
                
                self.fig.canvas.blit(self.ax.get_figure().bbox)
            except Exception as e: # pylint: disable=broad-except
                _log.exception(e)
            finally:
                if self.redrawSemaphore.available() < 1:
                    self.redrawSemaphore.release(1)

    def closeToCoordinate(self,event:'Event') -> bool:
        res:bool = False
        for c in self.app.scales.getCoordinates():
            if event.xdata and event.ydata and (abs(c[0] - event.xdata) < 0.01 and abs(c[1] - event.ydata) < 3):
                res = True
                break
        return res

    def on_motion(self, event:'Event') -> None:
        if not event.inaxes:
            return
        try:
            if self.lastMotionX is not None and self.lastMotionY is not None and (abs(self.lastMotionX - event.xdata) > 0.01 or abs(self.lastMotionY - event.ydata) > 2):
                self.lastMotionX = None
                self.lastMotionY = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
            if self.mousepress and self.indexpoint is not None:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                if not self.mousedragged:
                    self.app.scales.redoSelection([])
                self.mousedragged = True
                self.app.scales.updateCoordinate(self.indexpoint,event.xdata,event.ydata)
                self.redraw(force=False,annotations=False)
            elif not self.lastMotionX and not self.lastMotionY and self.closeToCoordinate(event):
                self.lastMotionX = event.xdata
                self.lastMotionY = event.ydata
                self.setCursor(Qt.CursorShape.OpenHandCursor)
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)

    def on_pick(self, event:'Event') -> None:
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        try:
            self.indexpoint = event.ind[-1]
        except Exception: # pylint: disable=broad-except
            self.indexpoint = event.ind
        self.mousepress = True

    def on_release(self, event:'Event') -> None:
        if self.mousepress:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            if self.mousedragged:
                self.mousedragged = False
            elif self.app.aw is not None and self.indexpoint is not None:
                self.app.aw.toggleSelection(self.indexpoint)
        self.mousepress = False
        self.indexpoint = None
        self.app.scales.computePolyfit()
        if  self.closeToCoordinate(event):
            self.lastMotionX = event.xdata
            self.lastMotionY = event.ydata
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.redraw(force=True)

    def onclick(self, event:'Event') -> None:
        if self.app.aw is not None and event.inaxes and event.button==3:
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

    __slots__ = [ 'app', 'canvas' ]
    
    def __init__(self, parent:QWidget | None = None) -> None:
        QWidget.__init__(self, parent)
        if (parent and parent.parent() and parent.parent().parent()):
            self.app:Tonino = parent.parent().parent().app # type: ignore
            self.canvas:MplCanvas = MplCanvas(self.app)
            vbl:QVBoxLayout = QVBoxLayout()
            vbl.setContentsMargins(1,1,1,1)
            vbl.setSpacing(0) 
            vbl.addWidget(self.canvas)
            self.setLayout(vbl)


