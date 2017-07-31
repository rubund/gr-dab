#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4.QtCore import QThread
import sys
import os
import user_frontend
import usrp_dab_rx
import json

class receive_thread(QThread):

    def __init__(self, frequency, bit_rate, address, size, protection, use_usrp, path):
        QThread.__init__(self)

        self.frequency = frequency
        self.bit_rate = bit_rate
        self.address = address
        self.size = size
        self.protection = protection
        self.use_usrp = use_usrp
        self.path = path
        self.record = False

    def __del__(self):
        self.wait()

    def stop_reception(self):
        self.rx.stop()
        self.rx.wait()

    def run(self):
        print 'start reception'
        try:
            self.rx = usrp_dab_rx.usrp_dab_rx(self.frequency, self.bit_rate, self.address, self.size, self.protection, self.use_usrp, self.path, self.record)
            self.rx.start()

        except RuntimeError:
            print 'error'

    def get_ensemble_info(self):
        # load string mci and convert it to dictionary
        #self.ensemble_info = json.loads(self.rx.get_ensemble_info())
        self.ensemble_info = json.loads("{\"SWR_BW_N\":{\"country_ID\":1}}")
        json.dumps(self.ensemble_info)
        return self.ensemble_info

    def get_service_info(self):
        # load string mci and convert it to dictionary
        print "service info:"
        print self.rx.get_service_info()
        self.service_info = json.loads(self.rx.get_service_info())
        #self.service_info = json.loads("[{\"reference\":736,\"ID\":2,\"primary\":true},{\"reference\":736,\"ID\":3,\"primary\":false},{\"reference\":234,\"ID\":5,\"primary\":true}]")
        json.dumps(self.service_info)
        return self.service_info

    def get_service_labels(self):
        print "service labels:"
        print self.rx.get_service_labels()
        self.service_labels = json.loads(self.rx.get_service_labels())
        #self.service_labels = json.loads("[{\"label\":\"SWR1_BW         \",\"reference\":736},{\"label\":\"SWR2            \",\"reference\":234}]")
        json.dumps(self.service_labels)
        return self.service_labels

    def get_subch_info(self):
        print "subchannel info"
        print self.rx.get_subch_info()
        # load string mci and convert it to dictionary
        self.subch_info = json.loads(self.rx.get_subch_info())
        #self.subch_info = json.loads("[{\"ID\":2, \"address\":54, \"protect\":2,\"size\":84},{\"ID\":3, \"address\":54, \"protect\":2,\"size\":84},{\"ID\":5, \"address\":234, \"protect\":2,\"size\":84}]")
        json.dumps(self.subch_info)
        return self.subch_info

    def set_volume(self, volume):
        self.rx.set_volume(volume)

    def set_record(self, record):
        self.record = record





class DABstep(QtGui.QMainWindow, user_frontend.Ui_MainWindow):
    def __init__(self, parent=None):
        super(DABstep, self).__init__(parent)
        self.setupUi(self)

        self.modes = {"rec": 0, "trans": 1, "dev": 2}
        self.mode = self.modes["rec"]

        self.frequency = 208.064e6
        self.bit_rate = 112
        self.address = 0
        self.size = 84
        self.protection = 2
        self.volume = 80
        self.subch = -1
        self.need_new_init = True


        self.file_path = "None"
        self.src_is_USRP = True


        # change of source by radio buttons
        self.rbtn_USRP.clicked.connect(self.src2USRP)
        self.rbtn_File.clicked.connect(self.src2File)
        # set file path
        self.btn_file_path.clicked.connect(self.set_file_path)
        # init button initializes receiver with center frequency
        self.btn_init.clicked.connect(self.init)
        # update button updates services in table
        self.btn_update_info.clicked.connect(self.update_service_info)
        # a click on a cell of the service table let the text box show more info to the selected service
        self.table_mci.cellClicked.connect(self.selected_subch)
        # a click on the play button compiles receiver with new subch info and plays the audio
        self.btn_play.clicked.connect(self.play_audio)
        # stop button click stops audio reception
        self.btn_stop.clicked.connect(self.stop_reception)
        # volume slider moved
        self.slider_volume.valueChanged.connect(self.set_volume)
        # record button
        self.btn_record.clicked.connect(self.record_audio)


        self.btn_debug.clicked.connect(self.test)


    def load_rec_mode(self):
        self.btn_receive.setDefault(True)
        self.btn_transmit.setDefault(False)
        self.mode = self.modes["rec"]

        # show all reception specific items
        self.btn_update_info.show()
        self.table_mci.show()
        # hide all irrelevant items for reception mode
        self.formLayout.hide()

    def load_trans_mode(self):
        self.btn_receive.setDefault(False)
        self.btn_transmit.setDefault(True)
        self.mode = self.modes["trans"]

        # show all transmission specific items
        self.formLayout.show()
        # hide all irrelevant items for reception mode
        self.btn_update_info.hide()
        self.table_mci.hide()

    def src2USRP(self):
        self.btn_file_path.setEnabled(False)
        self.label_path.setEnabled(False)
        self.spinbox_frequency.setEnabled(True)
        self.label_frequency.setEnabled(True)
        self.src_is_USRP = True

    def src2File(self):
        self.btn_file_path.setEnabled(True)
        self.label_path.setEnabled(True)
        self.spinbox_frequency.setEnabled(False)
        self.label_frequency.setEnabled(False)
        self.src_is_USRP = False

    def set_file_path(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Pick a file with recorded IQ samples")
        if path:  # if user didn't pick a directory don't continue
            self.file_path = str(path)
            self.label_path.setText(path)


    def init(self):
        # write center frequency from spin box value
        self.frequency = self.spinbox_frequency.value()
        # create a new Thread for reception and start it
        self.my_receiver = receive_thread(self.frequency, self.bit_rate, self.address, self.size, self.protection, self.src_is_USRP, self.file_path)
        self.my_receiver.start()
        print "finished initializing"

    def stop_reception(self):
        self.my_receiver.stop_reception()
        self.btn_stop.setEnabled(False)
        self.btn_play.setText("Play")
        self.btn_play.setEnabled(True)
        self.slider_volume.setEnabled(False)
        self.btn_record.setEnabled(True)
        self.my_receiver.set_record(False)

    def play_audio(self):
        if not self.slider_volume.isEnabled():
            # play button pressed
            self.btn_play.setText("Mute")
            self.btn_stop.setEnabled(True)
            self.slider_volume.setEnabled(True)
            self.slider_volume.setValue(self.volume)
            self.set_volume()
            if self.need_new_init:
                self.my_receiver = receive_thread(self.frequency, self.bit_rate, self.address, self.size, self.protection, self.src_is_USRP, self.file_path)
                self.my_receiver.start()
        else:
            # mute button pressed
            self.btn_play.setText("Play")
            self.volume = self.slider_volume.value()
            self.slider_volume.setValue(0)
            self.slider_volume.setEnabled(False)
            self.set_volume()
            self.need_new_init = False

    def record_audio(self):
        self.btn_record.setEnabled(False)
        self.btn_play.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.my_receiver = receive_thread(self.frequency, self.bit_rate, self.address, self.size, self.protection,
                                          self.src_is_USRP, self.file_path)
        self.my_receiver.set_record(True)
        self.my_receiver.start()


    def set_volume(self):
        print self.slider_volume.value()/100
        self.my_receiver.set_volume(float(self.slider_volume.value())/100)

    def update_service_info(self):
        # remove all old data first
        while (self.table_mci.rowCount() > 0):
            self.table_mci.removeRow(0)

        # get new data from FIC
        service_data = self.my_receiver.get_service_info()
        service_labels = self.my_receiver.get_service_labels()

        for n, key in enumerate(sorted(service_data, key=lambda service_data:service_data['ID'])):
            # add a new row
            self.table_mci.insertRow(n)
            # print ID in first collumn
            self.table_mci.setItem(n, 0, QtGui.QTableWidgetItem(str(key['ID'])))
            # print reference (later label)
            self.table_mci.setItem(n, 1, QtGui.QTableWidgetItem((item for item in service_labels if item['reference'] == key['reference']).next()['label']))
            # print type
            self.table_mci.setItem(n, 2, QtGui.QTableWidgetItem("primary" if key['primary'] == True else "secondary"))

    def selected_subch(self):

        # enable play button
        self.btn_play.setEnabled(True)
        self.btn_record.setEnabled(True)
        if self.table_mci.currentRow() is self.subch:
            self.need_new_init = False
        else:
            # new subch was selected
            self.subch = self.table_mci.currentRow()
            self.need_new_init = True
            self.btn_play.setText("Play")
            self.slider_volume.setEnabled(False)




        # clear text edit
        self.txt_info.clear()
        # get selected sub-channel by its ID
        ID = self.table_mci.item(self.table_mci.currentRow(), 0).text()
        reference = (item for item in self.my_receiver.get_service_info() if item['ID'] == int(ID)).next()['reference']
        # get dicts to specific service and sub-channel
        ensemble_data = self.my_receiver.get_ensemble_info()
        service_data = (item for item in self.my_receiver.get_service_info() if item['ID'] == int(ID)).next()
        service_label = (item for item in self.my_receiver.get_service_labels() if item['reference'] == int(reference)).next()
        subch_data = (item for item in self.my_receiver.get_subch_info() if item['ID'] == int(ID)).next()

        # update sub-channel info for receiver
        self.address = int(subch_data['address'])
        print int(subch_data['address'])
        self.size = int(subch_data['size'])
        print int(subch_data['size'])

        # ensemble info
        self.txt_info.insertPlainText("Ensemble: " + ensemble_data.keys()[0] + "\n")
        self.txt_info.insertPlainText("Country: " + str(ensemble_data.values()[0]['country_ID']) + "\n") #TODO: lookup table for country IDs

        # service info
        self.txt_info.insertPlainText("Service: " + service_label['label'] + "\n")
        self.txt_info.insertPlainText("Type: " + ("primary" if service_data['primary'] == True else "secondary") + "\n")

        # sub-channel info





    def test(self):
        ensemble_data = self.my_receiver.get_ensemble_info()
        print ensemble_data.keys()[0]






def main():
    app = QtGui.QApplication(sys.argv)
    form = DABstep()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
