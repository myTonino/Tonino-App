# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/PreCalibDialogUI.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(575, 352)
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
        self.logOutput = QtWidgets.QPlainTextEdit(Dialog)
        self.logOutput.setObjectName("logOutput")
        self.horizontalLayout_2.addWidget(self.logOutput)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButtonMaster = QtWidgets.QPushButton(Dialog)
        self.pushButtonMaster.setObjectName("pushButtonMaster")
        self.verticalLayout_3.addWidget(self.pushButtonMaster)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.pushButtonScan = QtWidgets.QPushButton(Dialog)
        self.pushButtonScan.setObjectName("pushButtonScan")
        self.verticalLayout_3.addWidget(self.pushButtonScan)
        self.pushButtonPreCal = QtWidgets.QPushButton(Dialog)
        self.pushButtonPreCal.setObjectName("pushButtonPreCal")
        self.verticalLayout_3.addWidget(self.pushButtonPreCal)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.pushButtonSet = QtWidgets.QPushButton(Dialog)
        self.pushButtonSet.setObjectName("pushButtonSet")
        self.verticalLayout_3.addWidget(self.pushButtonSet)
        self.pushButtonReset = QtWidgets.QPushButton(Dialog)
        self.pushButtonReset.setObjectName("pushButtonReset")
        self.verticalLayout_3.addWidget(self.pushButtonReset)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
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
        Dialog.setWindowTitle(_translate("Dialog", "PreCalibration"))
        self.pushButtonMaster.setText(_translate("Dialog", "Master"))
        self.pushButtonScan.setText(_translate("Dialog", "Scan"))
        self.pushButtonPreCal.setText(_translate("Dialog", "PreCal"))
        self.pushButtonSet.setText(_translate("Dialog", "Set"))
        self.pushButtonReset.setText(_translate("Dialog", "Reset"))
