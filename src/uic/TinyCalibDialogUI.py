# Form implementation generated from reading ui file 'ui/TinyCalibDialogUI.ui'
#
# Created by: PyQt6 UI code generator 6.6.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(520, 266)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setWindowTitle("Calibration")
        Dialog.setToolTip("")
        Dialog.setAccessibleDescription("")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(0, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.calibLowLabel = QtWidgets.QLabel(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
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
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonScan = QtWidgets.QPushButton(parent=Dialog)
        self.pushButtonScan.setAccessibleDescription("")
        self.pushButtonScan.setText("Scan")
        self.pushButtonScan.setObjectName("pushButtonScan")
        self.horizontalLayout.addWidget(self.pushButtonScan)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.calibHighLabel = QtWidgets.QLabel(parent=Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
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
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())
