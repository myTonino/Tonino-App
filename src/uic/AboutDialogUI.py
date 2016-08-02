# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/AboutDialogUI.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(529, 226)
        Dialog.setWindowTitle("")
        Dialog.setModal(True)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.logoLabel = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logoLabel.sizePolicy().hasHeightForWidth())
        self.logoLabel.setSizePolicy(sizePolicy)
        self.logoLabel.setMinimumSize(QtCore.QSize(200, 200))
        self.logoLabel.setMaximumSize(QtCore.QSize(200, 200))
        self.logoLabel.setText("")
        self.logoLabel.setPixmap(QtGui.QPixmap(":/app/icons/tonino_small.png"))
        self.logoLabel.setScaledContents(True)
        self.logoLabel.setObjectName("logoLabel")
        self.horizontalLayout.addWidget(self.logoLabel)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.nameLabel = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.nameLabel.setFont(font)
        self.nameLabel.setTextFormat(QtCore.Qt.PlainText)
        self.nameLabel.setObjectName("nameLabel")
        self.verticalLayout.addWidget(self.nameLabel)
        self.debugLabel = QtWidgets.QLabel(Dialog)
        self.debugLabel.setText("")
        self.debugLabel.setObjectName("debugLabel")
        self.verticalLayout.addWidget(self.debugLabel)
        self.versionLabel = QtWidgets.QLabel(Dialog)
        self.versionLabel.setObjectName("versionLabel")
        self.verticalLayout.addWidget(self.versionLabel)
        self.copyrightLabel = QtWidgets.QLabel(Dialog)
        self.copyrightLabel.setObjectName("copyrightLabel")
        self.verticalLayout.addWidget(self.copyrightLabel)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalButtonLayout = QtWidgets.QHBoxLayout()
        self.horizontalButtonLayout.setObjectName("horizontalButtonLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalButtonLayout.addItem(spacerItem2)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.horizontalButtonLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalButtonLayout)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout_3.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.nameLabel.setText(_translate("Dialog", "Tonino"))
        self.versionLabel.setText(_translate("Dialog", "Version"))
        self.copyrightLabel.setText(_translate("Dialog", "Copyright © 2016 Marko Luther, Paul Holleis"))
        self.pushButton.setText(_translate("Dialog", "OK"))

from . import icons_rc
