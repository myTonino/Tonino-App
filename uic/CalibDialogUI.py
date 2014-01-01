# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/CalibDialogUI.ui'
#
# Created: Wed Jan  1 20:04:35 2014
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(519, 266)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(0, 0, -1, -1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.calibLowLabel = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calibLowLabel.sizePolicy().hasHeightForWidth())
        self.calibLowLabel.setSizePolicy(sizePolicy)
        self.calibLowLabel.setMinimumSize(QtCore.QSize(200, 200))
        self.calibLowLabel.setMaximumSize(QtCore.QSize(200, 200))
        self.calibLowLabel.setText(_fromUtf8(""))
        self.calibLowLabel.setPixmap(QtGui.QPixmap(_fromUtf8(":/app/icons/calib_low.png")))
        self.calibLowLabel.setScaledContents(True)
        self.calibLowLabel.setObjectName(_fromUtf8("calibLowLabel"))
        self.horizontalLayout_2.addWidget(self.calibLowLabel)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButtonScan = QtGui.QPushButton(Dialog)
        self.pushButtonScan.setObjectName(_fromUtf8("pushButtonScan"))
        self.horizontalLayout.addWidget(self.pushButtonScan)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.calibHighLabel = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calibHighLabel.sizePolicy().hasHeightForWidth())
        self.calibHighLabel.setSizePolicy(sizePolicy)
        self.calibHighLabel.setMinimumSize(QtCore.QSize(200, 200))
        self.calibHighLabel.setMaximumSize(QtCore.QSize(200, 200))
        self.calibHighLabel.setText(_fromUtf8(""))
        self.calibHighLabel.setPixmap(QtGui.QPixmap(_fromUtf8(":/app/icons/calib_high.png")))
        self.calibHighLabel.setScaledContents(True)
        self.calibHighLabel.setObjectName(_fromUtf8("calibHighLabel"))
        self.horizontalLayout_2.addWidget(self.calibHighLabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Calibration", None))
        self.pushButtonScan.setText(_translate("Dialog", "Scan", None))

from . import calib_low_rc
from . import calib_high_rc
