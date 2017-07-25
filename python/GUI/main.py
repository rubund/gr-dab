#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4.QtCore import QThread
import sys
import user_frontend
import usrp_dab_rx


class receive_thread(QThread):

    def __init__(self, frequency, bit_rate, address, size, protection):
        QThread.__init__(self)

        self.frequency = frequency
        self.bit_rate = bit_rate
        self.address = address
        self.size = size
        self.protection = protection

    def __del__(self):
        self.wait()

    def stop_reception(self):
        self.rx.stop()
        self.rx.wait()

    def run(self):
        print 'reception running'
        try:
            self.rx = usrp_dab_rx.usrp_dab_rx(self.frequency, self.bit_rate, self.address, self.size, self.protection)
            self.rx.start()

        except RuntimeError:
            print 'error'



class DABstep(QtGui.QMainWindow, user_frontend.Ui_MainWindow):
    def __init__(self, parent=None):
        super(DABstep, self).__init__(parent)
        self.setupUi(self)

        self.frequency = 208.064e6
        self.bit_rate = 112
        self.address = 0
        self.size = 84
        self.protection = 2

        # receive button initializes receiver with center frequency
        self.btn_receive.clicked.connect(self.receive)




    def receive(self):
        # write center frequency from spin box value
        self.frequency = self.spinbox_frequency.value()
        # create a new Thread for reception and start it
        self.my_receiver = receive_thread(self.frequency, self.bit_rate, self.address, self.size, self.protection)
        self.my_receiver.start()



    def stop_reception(self):
        self.my_receiver.stop_reception()
        self.btn_stop.setEnabled(False)
        self.btn_play.setText("Play")
        self.btn_play.setEnabled(True)

    def test(self):
        self.btn_receive.setEnabled(True)
        print 'test'




def main():
    app = QtGui.QApplication(sys.argv)
    form = DABstep()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
