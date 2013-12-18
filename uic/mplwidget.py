#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# mplwidget.py
#
# Copyright (c) 2013, Paul Holleis, Marko Luther
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

from PyQt4.QtGui import (QSizePolicy,QMenu,QWidget,QVBoxLayout,QAction,QCursor)
from PyQt4.QtCore import (Qt)
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams
from matplotlib import patheffects
import numpy as np        

class MplCanvas(FigureCanvas):
    def __init__(self,app):
        self.app = app
        
        self.x_min = 3.0 # minimum raw Tonino value to be drawn
        self.x_max = 5.0 # maximum raw Tonino value to be drawn
        self.x_step = 0.01

        self.xvalues = np.arange(self.x_min, self.x_max, self.x_step)
        self.yvalues = None # is set by update from the polyfit coefficent
        self.yvalues_default = None # the default Tonino polyfit curve
        self.yvalues_device = None # the device polyfit curve
        
        self.lastMotionX = None # holds the last x value on mouse movements if any
        self.lastMotionY = None # holds the last y value on mouse movements if any
               
        self.fig = Figure()
        self.fig.patch.set_facecolor('white')
        self.fig.patch.set_alpha(1.0)
        
        self.annotations = []
        self.indexpoint = None
        self.mousepress = False
        self.mousedragged = False
        
        # offsets for annotations
        self.xoffset = 0.04
        self.yoffset = 15
        
        # Tonino color scheme
        self.toninoGray = self.toninoColor(92,93,97)
        self.toninoBlue = self.toninoColor(74,83,102)
        self.toninoLightBlue = self.toninoColor(74,83,102)
        self.toninoRed = self.toninoColor(174,33,64)

        # xkcd design settings
        self.RRfontSize = 16.0
        rcParams['font.family'] = ['Comic Sans MS']
        rcParams['font.size'] = 14.0
        rcParams['path.effects'] = [
            patheffects.withStroke(linewidth=4, foreground="w")]
        rcParams['axes.linewidth'] = 1.5
        rcParams['lines.linewidth'] = 2.0
        rcParams['figure.facecolor'] = 'white'
        rcParams['grid.linewidth'] = 0.0
        rcParams['axes.unicode_minus'] = False
        rcParams['axes.color_cycle'] = ['b', 'r', 'c', 'm']
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
            bottom='off',       # ticks along the bottom edge are off
            top='off',          # ticks along the top edge are off
            labelbottom='off')  # labels along the bottom edge are off
        self.ax.tick_params(\
            color=self.toninoBlue,
            axis='y', 
            which='both',
            right='off',
            labelright='off') 
        self.ax.set_ylim([0, 205])
        self.ax.set_xlim([self.x_min, self.x_max])
        [t.set_color(self.toninoBlue) for t in self.ax.yaxis.get_ticklabels()]

        # compute the yvalues of the default Tonino scale
        self.yvalues_default = np.poly1d(self.app.scales.getDefaultCoefficents())(self.xvalues)
                
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                QSizePolicy.Expanding,
                                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        # connect signals
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick) 
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        # draw initial graph
        self.redraw()

        
    def toninoColor(self,r,g,b):
        return [r/255.,g/255.,b/255.]
        
    def updatePolyfit(self):
        # updates the polyfit line data and calls redraw
        c = self.app.scales.getCoefficients()
        if c == None:
            self.yvalues = None
        else:
            self.yvalues = np.poly1d(np.array(c))(self.xvalues)
           
        RR = self.app.scales.getRR() 
        if RR:
            self.ax.set_title("RR = %.3f"%RR, fontsize=self.RRfontSize, color=self.toninoBlue)
        else:
            self.ax.set_title("")
        self.redraw()
        
    def updateDevicePolyfit(self):
        # updates the device polyfit line data and calls redraw
        c = self.app.scales.getDeviceCoefficients()
        if c == None:
            self.yvalues_device = None
        else:
            self.yvalues_device = np.poly1d(np.array(c))(self.xvalues)
        # we do a full redraw to ensure that the default/device curve is redrawn
        self.redraw(full=True)
        
        
    def rightLowerOffset(self,x,y):
        return x + self.xoffset,y - 2*self.yoffset
        
    def leftLowerOffset(self,x,y):
        return x - 2*self.xoffset,y - 2*self.yoffset
        
    def rightUpperOffset(self,x,y):
        return x + 1.5*self.xoffset,y + 1.5*self.yoffset
        
    def leftUpperOffset(self,x,y):
        return x - 2*self.xoffset,y + self.yoffset
    
    def annotationPosition(self,coordinates,i,c):
        x = c[0]
        y = c[1]
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
            pv = coordinates[i-1][1]
            nv = coordinates[i+1][1]
            if pv < c[1] and c[1] < nv:
                x,y = self.rightLowerOffset(x,y)
            elif pv < c[1] and c[1] > nv:
                x,y = self.rightUpperOffset(x,y)
            else:
                x,y = self.leftLowerOffset(x,y)
        return x,y
        
        
    def redraw(self,full=False):
        # remove all annotations
        for a in self.annotations:
            a.remove()
        self.annotations = []
        if full or (not self.ax.lines):
            self.ax.lines = []
            # add Tonino curve or device curve
            if self.yvalues_device != None:
                self.ax.plot(self.xvalues, self.yvalues_device,color=self.toninoBlue)
            else:
                self.ax.plot(self.xvalues, self.yvalues_default,color=self.toninoBlue)
        else:
            # remove all but first curve
            self.ax.lines = self.ax.lines[:1]
        # add polyfit curve        
        if self.yvalues != None:
            self.ax.plot(self.xvalues,self.yvalues,color=self.toninoRed)
        # draw annotations at selected coordinates
        if self.app.aw:
            selectedCoordinates = self.app.scales.getSelectedCoordinates()
            coordinates = self.app.scales.getCoordinates()
            annotation_added = [] # coordinates that we already painted the annotation
            for i,c in enumerate(coordinates):
                if  len(c) > 1 and c[2] and c in selectedCoordinates and not c in annotation_added:
                    annotation_added.append(c)
                    x,y = self.annotationPosition(coordinates,i,c)
                    an = self.ax.annotate(c[2],xy=(c[0],c[1]),xytext=(x,y),color=self.toninoGray,
                    arrowprops=dict(shrinkB=5,connectionstyle="arc3,rad=0.2",arrowstyle='->',color=self.toninoGray,relpos=(0,0)))
                    self.annotations.append(an)
            # draw coordinates
            if len(coordinates) > 0:
                cx = [c[0] for c in coordinates]
                cy = [c[1] for c in coordinates]
                self.ax.plot(cx,cy,color=self.toninoBlue,marker = "o",picker=10,linestyle='', markerfacecolor=self.toninoBlue,markersize=8)
        self.draw()
            
    def closeToCoordinate(self,event):
        res = False
        for c in self.app.scales.getCoordinates():
            if event.xdata and event.ydata and (abs(c[0] - event.xdata) < 0.01 and abs(c[1] - event.ydata) < 3):
                res = True
                break
        return res
            
    def on_motion(self,event):
        if not event.inaxes: return
        try:
            if self.lastMotionX and self.lastMotionY and (abs(self.lastMotionX - event.xdata) > 0.01 or abs(self.lastMotionY - event.ydata) > 2):
                self.lastMotionX = None
                self.lastMotionY = None
                self.redraw()
                self.setCursor(Qt.ArrowCursor)
            if self.mousepress:
                self.setCursor(Qt.ClosedHandCursor)
                self.mousedragged = True
                self.app.scales.updateCoordinate(self.indexpoint,event.xdata,event.ydata)              
            elif not self.lastMotionX and not self.lastMotionY and self.closeToCoordinate(event):
                self.lastMotionX = event.xdata
                self.lastMotionY = event.ydata
                self.setCursor(Qt.OpenHandCursor)              
        except:
            pass

    def on_pick(self,event):
        self.setCursor(Qt.ClosedHandCursor)
        try:
            self.indexpoint = event.ind[-1]
        except:
            self.indexpoint = event.ind
        self.mousepress = True

    def on_release(self,event):    
        if self.mousepress:
            self.setCursor(Qt.OpenHandCursor)     
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
            self.setCursor(Qt.OpenHandCursor)
                
    def onclick(self,event):
        if event.inaxes and event.button==3:
            # populate menu
            menu = QMenu(self) 
            ac = QAction(menu)
            ac.setText(self.app.aw.popupadd)
            ac.key = ("add",event.xdata,event.ydata)
            menu.addAction(ac)
            if (self.lastMotionX and self.lastMotionY):
                ac = QAction(menu)
                ac.setText(self.app.aw.popupdelete)
                ac.key = ("delete",event.xdata,event.ydata)
                menu.addAction(ac)
            self.mousepress = False
            self.indexpoint = None
            # show menu
            menu.triggered.connect(self.event_popup_action)
            menu.popup(QCursor.pos())
    
    def event_popup_action(self,action):
        if action.key[0] == "add":
            self.app.scales.addCoordinate(action.key[1],action.key[2])
        elif action.key[0] == "delete":
            for i,c in enumerate(self.app.scales.getCoordinates()):
                if abs(c[0] - action.key[1]) < 0.05 and abs(c[1] - action.key[2]) < 3:
                    self.app.scales.deleteCoordinates([i])
                    break
        
        
class mplwidget(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        if (parent and parent.parent()):
            self.app = parent.parent().app
        else:
            self.app = None
        self.canvas = MplCanvas(self.app)
        self.vbl = QVBoxLayout()
        self.vbl.setMargin(0) 
        self.vbl.setSpacing(0) 
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        
        