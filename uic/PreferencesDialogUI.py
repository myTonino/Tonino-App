# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/PreferencesDialogUI.ui'
#
# Created: Fri Dec 13 14:47:11 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName(_fromUtf8("Preferences"))
        Preferences.resize(365, 138)
        Preferences.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Preferences)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBoxToninoDisplay = QtGui.QGroupBox(Preferences)
        self.groupBoxToninoDisplay.setObjectName(_fromUtf8("groupBoxToninoDisplay"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBoxToninoDisplay)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.dim_label = QtGui.QLabel(self.groupBoxToninoDisplay)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dim_label.sizePolicy().hasHeightForWidth())
        self.dim_label.setSizePolicy(sizePolicy)
        self.dim_label.setMinimumSize(QtCore.QSize(60, 0))
        self.dim_label.setMaximumSize(QtCore.QSize(60, 16777215))
        self.dim_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.dim_label.setObjectName(_fromUtf8("dim_label"))
        self.horizontalLayout.addWidget(self.dim_label)
        self.displaySlider = QtGui.QSlider(self.groupBoxToninoDisplay)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.displaySlider.sizePolicy().hasHeightForWidth())
        self.displaySlider.setSizePolicy(sizePolicy)
        self.displaySlider.setMinimumSize(QtCore.QSize(150, 22))
        self.displaySlider.setMaximumSize(QtCore.QSize(150, 22))
        self.displaySlider.setMinimum(0)
        self.displaySlider.setMaximum(15)
        self.displaySlider.setPageStep(93)
        self.displaySlider.setTracking(False)
        self.displaySlider.setOrientation(QtCore.Qt.Horizontal)
        self.displaySlider.setObjectName(_fromUtf8("displaySlider"))
        self.horizontalLayout.addWidget(self.displaySlider)
        self.bright_label = QtGui.QLabel(self.groupBoxToninoDisplay)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bright_label.sizePolicy().hasHeightForWidth())
        self.bright_label.setSizePolicy(sizePolicy)
        self.bright_label.setMinimumSize(QtCore.QSize(60, 0))
        self.bright_label.setMaximumSize(QtCore.QSize(60, 16777215))
        self.bright_label.setObjectName(_fromUtf8("bright_label"))
        self.horizontalLayout.addWidget(self.bright_label)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.groupBoxToninoDisplay)
        spacerItem2 = QtGui.QSpacerItem(20, 34, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.buttonBox = QtGui.QDialogButtonBox(Preferences)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Preferences)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(_translate("Preferences", "Preferences", None))
        self.groupBoxToninoDisplay.setTitle(_translate("Preferences", "Tonino Display", None))
        self.dim_label.setText(_translate("Preferences", "dim", None))
        self.bright_label.setText(_translate("Preferences", "bright", None))

from . import icons_rc
