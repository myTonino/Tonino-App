# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/AboutDialogUI.ui'
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
        Dialog.resize(529, 226)
        Dialog.setWindowTitle(_fromUtf8(""))
        Dialog.setModal(True)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(Dialog)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.logoLabel = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logoLabel.sizePolicy().hasHeightForWidth())
        self.logoLabel.setSizePolicy(sizePolicy)
        self.logoLabel.setMinimumSize(QtCore.QSize(200, 200))
        self.logoLabel.setMaximumSize(QtCore.QSize(200, 200))
        self.logoLabel.setText(_fromUtf8(""))
        self.logoLabel.setPixmap(QtGui.QPixmap(_fromUtf8(":/app/icons/tonino_small.png")))
        self.logoLabel.setScaledContents(True)
        self.logoLabel.setObjectName(_fromUtf8("logoLabel"))
        self.horizontalLayout.addWidget(self.logoLabel)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.nameLabel = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.nameLabel.setFont(font)
        self.nameLabel.setTextFormat(QtCore.Qt.PlainText)
        self.nameLabel.setObjectName(_fromUtf8("nameLabel"))
        self.verticalLayout.addWidget(self.nameLabel)
        self.debugLabel = QtGui.QLabel(Dialog)
        self.debugLabel.setText(_fromUtf8(""))
        self.debugLabel.setObjectName(_fromUtf8("debugLabel"))
        self.verticalLayout.addWidget(self.debugLabel)
        self.versionLabel = QtGui.QLabel(Dialog)
        self.versionLabel.setObjectName(_fromUtf8("versionLabel"))
        self.verticalLayout.addWidget(self.versionLabel)
        self.copyrightLabel = QtGui.QLabel(Dialog)
        self.copyrightLabel.setObjectName(_fromUtf8("copyrightLabel"))
        self.verticalLayout.addWidget(self.copyrightLabel)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalButtonLayout = QtGui.QHBoxLayout()
        self.horizontalButtonLayout.setObjectName(_fromUtf8("horizontalButtonLayout"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalButtonLayout.addItem(spacerItem2)
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalButtonLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalButtonLayout)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout_3.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        self.nameLabel.setText(_translate("Dialog", "Tonino", None))
        self.versionLabel.setText(_translate("Dialog", "Version", None))
        self.copyrightLabel.setText(_translate("Dialog", "Copyright © 2013 Marko Luther, Paul Holleis", None))
        self.pushButton.setText(_translate("Dialog", "OK", None))

from . import icons_rc
