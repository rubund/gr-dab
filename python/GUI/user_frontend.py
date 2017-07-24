# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'user_frontend.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(738, 544)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_4 = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Abyssinica SIL"))
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_5.addWidget(self.label_4, QtCore.Qt.AlignHCenter)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.spinBox_3 = QtGui.QSpinBox(self.centralwidget)
        self.spinBox_3.setObjectName(_fromUtf8("spinBox_3"))
        self.horizontalLayout_3.addWidget(self.spinBox_3)
        self.verticalLayout_6.addLayout(self.horizontalLayout_3)
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.verticalLayout_6.addWidget(self.comboBox)
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout_6.addWidget(self.tableWidget)
        self.listWidget = QtGui.QListWidget(self.centralwidget)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout_6.addWidget(self.listWidget)
        self.horizontalLayout_2.addLayout(self.verticalLayout_6)
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.textBrowser = QtGui.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.verticalLayout_7.addWidget(self.textBrowser)
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_7.addWidget(self.line)
        self.label_2 = QtGui.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Abyssinica SIL"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_7.addWidget(self.label_2, QtCore.Qt.AlignHCenter)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout_5.addWidget(self.pushButton_2)
        self.pushButton_3 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.horizontalLayout_5.addWidget(self.pushButton_3)
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout_5.addWidget(self.pushButton)
        self.verticalLayout_7.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_4.addWidget(self.label_3)
        self.horizontalSlider = QtGui.QSlider(self.centralwidget)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.horizontalLayout_4.addWidget(self.horizontalSlider)
        self.verticalLayout_7.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2.addLayout(self.verticalLayout_7)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.spinBox = QtGui.QSpinBox(self.centralwidget)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.verticalLayout_5.addWidget(self.spinBox)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label_4.setText(_translate("MainWindow", "DABstep", None))
        self.label.setText(_translate("MainWindow", "set frequency", None))
        self.comboBox.setItemText(0, _translate("MainWindow", "receive", None))
        self.comboBox.setItemText(1, _translate("MainWindow", "transmit", None))
        self.label_2.setText(_translate("MainWindow", "Audio Player", None))
        self.pushButton_2.setText(_translate("MainWindow", "Play", None))
        self.pushButton_3.setText(_translate("MainWindow", "Stop", None))
        self.pushButton.setText(_translate("MainWindow", "Record", None))
        self.label_3.setText(_translate("MainWindow", "Volume", None))

