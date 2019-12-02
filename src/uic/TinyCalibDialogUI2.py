# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/TinyCalibDialogUI2.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(520, 266)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(0, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.calibHighLabel = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calibHighLabel.sizePolicy().hasHeightForWidth())
        self.calibHighLabel.setSizePolicy(sizePolicy)
        self.calibHighLabel.setMinimumSize(QtCore.QSize(200, 200))
        self.calibHighLabel.setMaximumSize(QtCore.QSize(200, 200))
        self.calibHighLabel.setText("")
        self.calibHighLabel.setPixmap(QtGui.QPixmap(":/app/icons/calib_high.png"))
        self.calibHighLabel.setScaledContents(True)
        self.calibHighLabel.setObjectName("calibHighLabel")
        self.horizontalLayout_2.addWidget(self.calibHighLabel)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonScan = QtWidgets.QPushButton(Dialog)
        self.pushButtonScan.setObjectName("pushButtonScan")
        self.horizontalLayout.addWidget(self.pushButtonScan)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.calibLowLabel = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calibLowLabel.sizePolicy().hasHeightForWidth())
        self.calibLowLabel.setSizePolicy(sizePolicy)
        self.calibLowLabel.setMinimumSize(QtCore.QSize(200, 200))
        self.calibLowLabel.setMaximumSize(QtCore.QSize(200, 200))
        self.calibLowLabel.setText("")
        self.calibLowLabel.setPixmap(QtGui.QPixmap(":/app/icons/calib_low_tiny.png"))
        self.calibLowLabel.setScaledContents(True)
        self.calibLowLabel.setObjectName("calibLowLabel")
        self.horizontalLayout_2.addWidget(self.calibLowLabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Calibration"))
        self.pushButtonScan.setText(_translate("Dialog", "Scan"))
from . import calib_high_rc
from . import calib_low_tiny_rc
