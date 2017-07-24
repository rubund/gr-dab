#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4.QtCore import QThread
import sys
import user_frontend


class reception_thread(QThread):

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        # your logic here

class DABstep(QtGui.QMainWindow, user_frontend.Ui_MainWindow):
    def __init__(self, parent=None):
        super(DABstep, self).__init__(parent)
        self.setupUi(self)
        self.start_reception.clicked.connect(self.receive)

    def receive(self):
        # create a new Thread
        self.my_receiver = reception_thread()

def main():
    app = QtGui.QApplication(sys.argv)
    form = DABstep()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
