# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/PreferencesDialogUI.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName("Preferences")
        Preferences.resize(365, 138)
        Preferences.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Preferences)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBoxToninoDisplay = QtWidgets.QGroupBox(Preferences)
        self.groupBoxToninoDisplay.setObjectName("groupBoxToninoDisplay")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBoxToninoDisplay)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.dim_label = QtWidgets.QLabel(self.groupBoxToninoDisplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dim_label.sizePolicy().hasHeightForWidth())
        self.dim_label.setSizePolicy(sizePolicy)
        self.dim_label.setMinimumSize(QtCore.QSize(60, 0))
        self.dim_label.setMaximumSize(QtCore.QSize(60, 16777215))
        self.dim_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.dim_label.setObjectName("dim_label")
        self.horizontalLayout.addWidget(self.dim_label)
        self.displaySlider = QtWidgets.QSlider(self.groupBoxToninoDisplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
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
        self.displaySlider.setObjectName("displaySlider")
        self.horizontalLayout.addWidget(self.displaySlider)
        self.bright_label = QtWidgets.QLabel(self.groupBoxToninoDisplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bright_label.sizePolicy().hasHeightForWidth())
        self.bright_label.setSizePolicy(sizePolicy)
        self.bright_label.setMinimumSize(QtCore.QSize(60, 0))
        self.bright_label.setMaximumSize(QtCore.QSize(60, 16777215))
        self.bright_label.setObjectName("bright_label")
        self.horizontalLayout.addWidget(self.bright_label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.groupBoxToninoDisplay)
        spacerItem2 = QtWidgets.QSpacerItem(20, 34, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Preferences)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Preferences)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        _translate = QtCore.QCoreApplication.translate
        Preferences.setWindowTitle(_translate("Preferences", "Preferences"))
        self.groupBoxToninoDisplay.setTitle(_translate("Preferences", "Tonino Display"))
        self.dim_label.setText(_translate("Preferences", "dim"))
        self.bright_label.setText(_translate("Preferences", "bright"))

from . import icons_rc
