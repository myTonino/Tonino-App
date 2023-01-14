# Form implementation generated from reading ui file 'ui/PreferencesDialogUI.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName("Preferences")
        Preferences.resize(420, 385)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Preferences.sizePolicy().hasHeightForWidth())
        Preferences.setSizePolicy(sizePolicy)
        Preferences.setMaximumSize(QtCore.QSize(420, 400))
        Preferences.setWindowTitle("Preferences")
        Preferences.setToolTip("")
        Preferences.setAccessibleDescription("")
        Preferences.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Preferences)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBoxDefaultScale = QtWidgets.QGroupBox(Preferences)
        self.groupBoxDefaultScale.setToolTip("")
        self.groupBoxDefaultScale.setAccessibleDescription("")
        self.groupBoxDefaultScale.setTitle("Default Scale")
        self.groupBoxDefaultScale.setObjectName("groupBoxDefaultScale")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.groupBoxDefaultScale)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.radioButtonTonino = QtWidgets.QRadioButton(self.groupBoxDefaultScale)
        self.radioButtonTonino.setToolTip("")
        self.radioButtonTonino.setAccessibleDescription("")
        self.radioButtonTonino.setText("Tonino")
        self.radioButtonTonino.setChecked(True)
        self.radioButtonTonino.setObjectName("radioButtonTonino")
        self.horizontalLayout_7.addWidget(self.radioButtonTonino)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem1)
        self.radioButtonAgtron = QtWidgets.QRadioButton(self.groupBoxDefaultScale)
        self.radioButtonAgtron.setToolTip("")
        self.radioButtonAgtron.setAccessibleDescription("")
        self.radioButtonAgtron.setText("Agtron")
        self.radioButtonAgtron.setObjectName("radioButtonAgtron")
        self.horizontalLayout_7.addWidget(self.radioButtonAgtron)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem2)
        self.verticalLayout.addWidget(self.groupBoxDefaultScale)
        self.groupBoxToninoDisplay = QtWidgets.QGroupBox(Preferences)
        self.groupBoxToninoDisplay.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.groupBoxToninoDisplay.setObjectName("groupBoxToninoDisplay")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBoxToninoDisplay)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dim_label = QtWidgets.QLabel(self.groupBoxToninoDisplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dim_label.sizePolicy().hasHeightForWidth())
        self.dim_label.setSizePolicy(sizePolicy)
        self.dim_label.setMinimumSize(QtCore.QSize(60, 0))
        self.dim_label.setMaximumSize(QtCore.QSize(60, 16777215))
        self.dim_label.setToolTip("")
        self.dim_label.setAccessibleDescription("")
        self.dim_label.setText("dim")
        self.dim_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.dim_label.setObjectName("dim_label")
        self.horizontalLayout.addWidget(self.dim_label)
        self.displaySlider = QtWidgets.QSlider(self.groupBoxToninoDisplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.displaySlider.sizePolicy().hasHeightForWidth())
        self.displaySlider.setSizePolicy(sizePolicy)
        self.displaySlider.setMinimumSize(QtCore.QSize(150, 22))
        self.displaySlider.setMaximumSize(QtCore.QSize(150, 22))
        self.displaySlider.setToolTip("")
        self.displaySlider.setAccessibleDescription("")
        self.displaySlider.setMinimum(0)
        self.displaySlider.setMaximum(15)
        self.displaySlider.setPageStep(5)
        self.displaySlider.setProperty("value", 0)
        self.displaySlider.setTracking(False)
        self.displaySlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.displaySlider.setObjectName("displaySlider")
        self.horizontalLayout.addWidget(self.displaySlider)
        self.bright_label = QtWidgets.QLabel(self.groupBoxToninoDisplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bright_label.sizePolicy().hasHeightForWidth())
        self.bright_label.setSizePolicy(sizePolicy)
        self.bright_label.setMinimumSize(QtCore.QSize(60, 0))
        self.bright_label.setMaximumSize(QtCore.QSize(60, 16777215))
        self.bright_label.setToolTip("")
        self.bright_label.setAccessibleDescription("")
        self.bright_label.setText("bright")
        self.bright_label.setObjectName("bright_label")
        self.horizontalLayout.addWidget(self.bright_label)
        self.checkBoxFlip = QtWidgets.QCheckBox(self.groupBoxToninoDisplay)
        self.checkBoxFlip.setToolTip("")
        self.checkBoxFlip.setAccessibleDescription("")
        self.checkBoxFlip.setText("Flip")
        self.checkBoxFlip.setObjectName("checkBoxFlip")
        self.horizontalLayout.addWidget(self.checkBoxFlip)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addWidget(self.groupBoxToninoDisplay)
        self.groupBoxToninoTarget = QtWidgets.QGroupBox(Preferences)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxToninoTarget.sizePolicy().hasHeightForWidth())
        self.groupBoxToninoTarget.setSizePolicy(sizePolicy)
        self.groupBoxToninoTarget.setMinimumSize(QtCore.QSize(0, 120))
        self.groupBoxToninoTarget.setBaseSize(QtCore.QSize(0, 0))
        self.groupBoxToninoTarget.setObjectName("groupBoxToninoTarget")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.groupBoxToninoTarget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 29, 361, 78))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.groupBoxTargetValue = QtWidgets.QGroupBox(self.horizontalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxTargetValue.sizePolicy().hasHeightForWidth())
        self.groupBoxTargetValue.setSizePolicy(sizePolicy)
        self.groupBoxTargetValue.setMinimumSize(QtCore.QSize(0, 30))
        self.groupBoxTargetValue.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.groupBoxTargetValue.setObjectName("groupBoxTargetValue")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBoxTargetValue)
        self.gridLayout.setObjectName("gridLayout")
        self.targetValueSpinBox = QtWidgets.QSpinBox(self.groupBoxTargetValue)
        self.targetValueSpinBox.setMinimumSize(QtCore.QSize(0, 22))
        self.targetValueSpinBox.setToolTip("")
        self.targetValueSpinBox.setAccessibleDescription("")
        self.targetValueSpinBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.targetValueSpinBox.setSuffix("")
        self.targetValueSpinBox.setPrefix("")
        self.targetValueSpinBox.setMaximum(200)
        self.targetValueSpinBox.setSingleStep(1)
        self.targetValueSpinBox.setObjectName("targetValueSpinBox")
        self.gridLayout.addWidget(self.targetValueSpinBox, 0, 0, 1, 1)
        self.horizontalLayout_3.addWidget(self.groupBoxTargetValue)
        self.groupBoxTargetRange = QtWidgets.QGroupBox(self.horizontalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxTargetRange.sizePolicy().hasHeightForWidth())
        self.groupBoxTargetRange.setSizePolicy(sizePolicy)
        self.groupBoxTargetRange.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBoxTargetRange.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.groupBoxTargetRange.setObjectName("groupBoxTargetRange")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBoxTargetRange)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.range_min_label = QtWidgets.QLabel(self.groupBoxTargetRange)
        self.range_min_label.setToolTip("")
        self.range_min_label.setAccessibleDescription("")
        self.range_min_label.setText("0")
        self.range_min_label.setObjectName("range_min_label")
        self.horizontalLayout_2.addWidget(self.range_min_label)
        self.rangeSlider = QtWidgets.QSlider(self.groupBoxTargetRange)
        self.rangeSlider.setMinimumSize(QtCore.QSize(0, 22))
        self.rangeSlider.setToolTip("")
        self.rangeSlider.setAccessibleDescription("")
        self.rangeSlider.setMaximum(5)
        self.rangeSlider.setPageStep(2)
        self.rangeSlider.setProperty("value", 0)
        self.rangeSlider.setTracking(False)
        self.rangeSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.rangeSlider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBothSides)
        self.rangeSlider.setTickInterval(1)
        self.rangeSlider.setObjectName("rangeSlider")
        self.horizontalLayout_2.addWidget(self.rangeSlider)
        self.range_max_label = QtWidgets.QLabel(self.groupBoxTargetRange)
        self.range_max_label.setToolTip("")
        self.range_max_label.setAccessibleDescription("")
        self.range_max_label.setText("5")
        self.range_max_label.setObjectName("range_max_label")
        self.horizontalLayout_2.addWidget(self.range_max_label)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addWidget(self.groupBoxTargetRange)
        self.verticalLayout.addWidget(self.groupBoxToninoTarget)
        self.groupBoxToninoName = QtWidgets.QGroupBox(Preferences)
        self.groupBoxToninoName.setMinimumSize(QtCore.QSize(0, 80))
        self.groupBoxToninoName.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.groupBoxToninoName.setFlat(False)
        self.groupBoxToninoName.setCheckable(False)
        self.groupBoxToninoName.setObjectName("groupBoxToninoName")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.groupBoxToninoName)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem4 = QtWidgets.QSpacerItem(75, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.lineEditName = QtWidgets.QLineEdit(self.groupBoxToninoName)
        self.lineEditName.setToolTip("")
        self.lineEditName.setAccessibleDescription("")
        self.lineEditName.setInputMask("")
        self.lineEditName.setText("")
        self.lineEditName.setMaxLength(8)
        self.lineEditName.setPlaceholderText("")
        self.lineEditName.setObjectName("lineEditName")
        self.horizontalLayout_5.addWidget(self.lineEditName)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_5)
        spacerItem5 = QtWidgets.QSpacerItem(74, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem5)
        self.verticalLayout.addWidget(self.groupBoxToninoName)
        self.buttonBox = QtWidgets.QDialogButtonBox(Preferences)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Preferences)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        _translate = QtCore.QCoreApplication.translate
        self.groupBoxToninoDisplay.setTitle(_translate("Preferences", "Display"))
        self.groupBoxToninoTarget.setTitle(_translate("Preferences", "Target"))
        self.groupBoxTargetValue.setTitle(_translate("Preferences", "Value"))
        self.groupBoxTargetRange.setTitle(_translate("Preferences", "Range"))
        self.groupBoxToninoName.setTitle(_translate("Preferences", "Name"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Preferences = QtWidgets.QDialog()
    ui = Ui_Preferences()
    ui.setupUi(Preferences)
    Preferences.show()
    sys.exit(app.exec())
