#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4.QtCore import QThread
from PyQt4.QtCore import QTimer
import sys
import os
import user_frontend
import usrp_dab_rx
import usrp_dab_tx
import json


#################################
# RECEIVER THREAD
#################################
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
            self.rx = usrp_dab_rx.usrp_dab_rx(self.frequency, self.bit_rate, self.address, self.size, self.protection,
                                              self.use_usrp, self.path, self.record)
            self.rx.start()

        except RuntimeError:
            print 'error'

    def get_ensemble_info(self):
        # load string mci and convert it to dictionary
        self.ensemble_info = json.loads(self.rx.get_ensemble_info())
        #self.ensemble_info = json.loads("{\"SWR_BW_N\":{\"country_ID\":1}}")
        json.dumps(self.ensemble_info)
        return self.ensemble_info

    def get_service_info(self):
        # load string mci and convert it to dictionary
        print "service info:"
        print self.rx.get_service_info()
        self.service_info = json.loads(self.rx.get_service_info())
        # self.service_info = json.loads("[{\"reference\":736,\"ID\":2,\"primary\":true},{\"reference\":736,\"ID\":3,\"primary\":false},{\"reference\":234,\"ID\":5,\"primary\":true}]")
        json.dumps(self.service_info)
        return self.service_info

    def get_service_labels(self):
        print "service labels:"
        print self.rx.get_service_labels()
        self.service_labels = json.loads(self.rx.get_service_labels())
        # self.service_labels = json.loads("[{\"label\":\"SWR1_BW         \",\"reference\":736},{\"label\":\"SWR2            \",\"reference\":234}]")
        json.dumps(self.service_labels)
        return self.service_labels

    def get_subch_info(self):
        print "subchannel info"
        print self.rx.get_subch_info()
        # load string mci and convert it to dictionary
        self.subch_info = json.loads(self.rx.get_subch_info())
        # self.subch_info = json.loads("[{\"ID\":2, \"address\":54, \"protect\":2,\"size\":84},{\"ID\":3, \"address\":54, \"protect\":2,\"size\":84},{\"ID\":5, \"address\":234, \"protect\":2,\"size\":84}]")
        json.dumps(self.subch_info)
        return self.subch_info

    def get_programme_type(self):
        print "programme type"
        print self.rx.get_programme_type()
        # load string mci and convert it to dictionary
        self.programme_type = json.loads(self.rx.get_programme_type())
        json.dumps(self.programme_type)
        return self.programme_type

    def set_volume(self, volume):
        self.rx.set_volume(volume)

    def set_record(self, record):
        self.record = record

    def get_sample_rate(self):
        return self.rx.get_sample_rate()

    def get_snr(self):
        return self.rx.get_snr()


#################################
# TRANSMITTER THREAD
#################################
class transmit_thread(QThread):
    def __init__(self, frequency, num_subch, ensemble_label, service_label, language, protection, data_rate_n,
                 src_paths, use_usrp, sink_path, selected_audio):
        QThread.__init__(self)

        self.frequency = frequency
        self.num_subch = num_subch
        self.ensemble_label = ensemble_label
        self.service_label = service_label
        self.language = language
        self.protection = protection
        self.data_rate_n = data_rate_n
        self.src_paths = src_paths
        self.use_usrp = use_usrp
        self.sink_path = sink_path
        self.selected_audio = selected_audio
        print "initialized transmitter thread"

    def __del__(self):
        self.wait()

    def stop_transmitter(self):
        self.tx.stop()
        self.tx.wait()

    def run(self):
        try:
            self.tx = usrp_dab_tx.usrp_dab_tx(self.frequency, self.num_subch, self.ensemble_label, self.service_label,
                                              self.language, self.protection, self.data_rate_n, self.src_paths, self.selected_audio,
                                              self.use_usrp, self.sink_path)
            print 'transmission flow graph set up'
            self.tx.start()

        except RuntimeError:
            print 'flowgraph stopped due to runtime error'

    def set_volume(self, volume):
        self.tx.set_volume(volume)


class DABstep(QtGui.QMainWindow, user_frontend.Ui_MainWindow):
    def __init__(self, parent=None):
        super(DABstep, self).__init__(parent)
        self.setupUi(self)

        self.modes = {"rec": 0, "trans": 1, "dev": 2}
        self.mode = self.modes["rec"]

        self.frequency = 208.064e6
        self.bit_rate = 8
        self.address = 0
        self.size = 6
        self.protection = 2
        self.volume = 80
        self.subch = -1
        self.need_new_init = True

        self.file_path = "None"
        self.src_is_USRP = True

        # tab change
        self.mode_tabs.currentChanged.connect(self.change_tab)
        self.table = lookup_table()


        ######################################################################
        # TAB RECEPTION
        ######################################################################

        # table stretch
        #self.table_mci.horizontalHeade
        # timer for update of SNR
        self.snr_timer = QTimer()
        self.snr_timer.timeout.connect(self.snr_update)
        # change of source by radio buttons
        self.rbtn_USRP.clicked.connect(self.src2USRP)
        self.rbtn_File.clicked.connect(self.src2File)
        # set file path
        self.btn_file_path.clicked.connect(self.set_file_path)
        # init button initializes receiver with center frequency
        self.btn_init.clicked.connect(self.init_receiver)
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

        ######################################################################
        # TAB TRANSMISSION
        ######################################################################
        # change of sink by radio buttons
        self.t_rbtn_USRP.clicked.connect(self.t_set_sink_USRP)
        self.t_rbtn_File.clicked.connect(self.t_set_sink_File)
        # create dict for service components
        self.components = [
            {"label": self.t_label_comp1, "data_rate_label": self.t_label_rate1, "data_rate": self.t_spin_rate1,
             "protection_label": self.t_label_prot1, "protection": self.t_spin_prot1, "enabled": True,
             "src_label": self.t_label_comp_src1, "src_path_disp": self.t_label_path_src1,
             "src_btn": self.t_btn_path_src1, "src_path":"None"},
            {"label": self.t_label_comp2, "data_rate_label": self.t_label_rate2, "data_rate": self.t_spin_rate2,
             "protection_label": self.t_label_prot2, "protection": self.t_spin_prot2, "enabled": False,
             "src_label": self.t_label_comp_src2, "src_path_disp": self.t_label_path_src2,
             "src_btn": self.t_btn_path_src2, "src_path":"None"},
            {"label": self.t_label_comp3, "data_rate_label": self.t_label_rate3, "data_rate": self.t_spin_rate3,
             "protection_label": self.t_label_prot3, "protection": self.t_spin_prot3, "enabled": False,
             "src_label": self.t_label_comp_src3, "src_path_disp": self.t_label_path_src3,
             "src_btn": self.t_btn_path_src3, "src_path":"None"},
            {"label": self.t_label_comp4, "data_rate_label": self.t_label_rate4, "data_rate": self.t_spin_rate4,
             "protection_label": self.t_label_prot4, "protection": self.t_spin_prot4, "enabled": False,
             "src_label": self.t_label_comp_src4, "src_path_disp": self.t_label_path_src4,
             "src_btn": self.t_btn_path_src4, "src_path":"None"},
            {"label": self.t_label_comp5, "data_rate_label": self.t_label_rate5, "data_rate": self.t_spin_rate5,
             "protection_label": self.t_label_prot5, "protection": self.t_spin_prot5, "enabled": False,
             "src_label": self.t_label_comp_src5, "src_path_disp": self.t_label_path_src5,
             "src_btn": self.t_btn_path_src5, "src_path":"None"},
            {"label": self.t_label_comp6, "data_rate_label": self.t_label_rate6, "data_rate": self.t_spin_rate6,
             "protection_label": self.t_label_prot6, "protection": self.t_spin_prot6, "enabled": False,
             "src_label": self.t_label_comp_src6, "src_path_disp": self.t_label_path_src6,
             "src_btn": self.t_btn_path_src6, "src_path":"None"},
            {"label": self.t_label_comp7, "data_rate_label": self.t_label_rate7, "data_rate": self.t_spin_rate7,
             "protection_label": self.t_label_prot7, "protection": self.t_spin_prot7, "enabled": False,
             "src_label": self.t_label_comp_src7, "src_path_disp": self.t_label_path_src7,
             "src_btn": self.t_btn_path_src7, "src_path":"None"}]
        # update service components initially to hide the service components 2-7
        self.t_update_service_components()
        # provide suggestions for language combo box
        for i in range(0,len(self.table.languages)):
            self.t_combo_language.addItem(self.table.languages[i])
        # provide suggestions for country combo box
        for i in range(0,len(self.table.country_ID_ECC_E0)):
            self.t_combo_country.addItem(self.table.country_ID_ECC_E0[i])
        # update dict "components" and display of service components if spinbox "number of channels" is changed
        self.t_spin_num_subch.valueChanged.connect(self.t_change_num_subch)
        # write ensemble/service info when init is pressed
        self.t_btn_init.pressed.connect(self.t_init_transmitter)
        # start flowgraph when play btn pressed
        self.t_btn_play.pressed.connect(self.t_run_transmitter)
        # stop button pressed
        self.t_btn_stop.pressed.connect(self.t_stop_transmitter)
        # path for File sink path
        self.t_btn_file_path.pressed.connect(self.t_set_file_path)
        # path selection for all 7 (possible) sub channels
        self.t_btn_path_src1.pressed.connect(self.t_set_subch_path1)
        self.t_btn_path_src2.pressed.connect(self.t_set_subch_path2)
        self.t_btn_path_src3.pressed.connect(self.t_set_subch_path3)
        self.t_btn_path_src4.pressed.connect(self.t_set_subch_path4)
        self.t_btn_path_src5.pressed.connect(self.t_set_subch_path5)
        self.t_btn_path_src6.pressed.connect(self.t_set_subch_path6)
        self.t_btn_path_src7.pressed.connect(self.t_set_subch_path7)
        # select subch for audio player
        self.t_spin_listen_to_component.valueChanged.connect(self.t_changed_audio_component)
        # set volume if volume slider is changed
        self.t_slider_volume.valueChanged.connect(self.t_set_volume)


    def change_tab(self):
        if self.mode_tabs.currentWidget() is self.tab_transmission:
            print "changed to transmission mode"
            self.t_update_service_components()

        elif self.mode_tabs.currentWidget() is self.tab_reception:
            print "changed to reception mode"
        else:
            print "changed to unknown tab"

    ################################
    # Transmitter functions
    ################################

    def t_set_sink_USRP(self):
        self.t_btn_file_path.setEnabled(False)
        self.t_label_sink.setEnabled(False)
        self.t_spinbox_frequency.setEnabled(True)
        self.t_label_frequency.setEnabled(True)

    def t_set_sink_File(self):
        self.t_btn_file_path.setEnabled(True)
        self.t_label_sink.setEnabled(True)
        self.t_spinbox_frequency.setEnabled(False)
        self.t_label_frequency.setEnabled(False)

    def t_change_num_subch(self):
        num_subch = self.t_spin_num_subch.value()
        if 0 <= num_subch <= 7:
            for n in range(0, 7):
                if n < num_subch:
                    self.components[n]["enabled"] = True
                else:
                    self.components[n]["enabled"] = False
        self.t_update_service_components()
        self.t_spin_listen_to_component.setMaximum(num_subch)

    def t_update_service_components(self):
        for component in self.components:
            if component["enabled"] is False:
                component["label"].hide()
                component["data_rate_label"].hide()
                component["data_rate"].hide()
                component["protection_label"].hide()
                component["protection"].hide()
                component["src_label"].hide()
                component["src_path_disp"].hide()
                component["src_btn"].hide()
            else:
                component["label"].show()
                component["data_rate_label"].show()
                component["data_rate"].show()
                component["protection_label"].show()
                component["protection"].show()
                component["src_label"].show()
                component["src_path_disp"].show()
                component["src_btn"].show()

    def t_init_transmitter(self):
        print "init transmitter"
        arguments_incomplete = False
        # produce array for protection and data_rate and src_paths
        protection_array = [None] * self.t_spin_num_subch.value()
        data_rate_n_array = [None] * self.t_spin_num_subch.value()
        audio_paths = ["None"] * self.t_spin_num_subch.value()
        for i in range(0, self.t_spin_num_subch.value()):
            protection_array[i] = self.components[i]["protection"].value()
            data_rate_n_array[i] = self.components[i]["data_rate"].value()/8
            if self.components[i]["src_path"] is "None":
                # highlight the path which is not selected
                self.components[i]["src_path_disp"].setStyleSheet('color: red')
                arguments_incomplete = True
                print "path " + str(i+1) + " not selected"
            else:
                audio_paths[i] = self.components[i]["src_path"]

        print protection_array
        print data_rate_n_array
        print audio_paths
        print self.t_combo_language.currentIndex()

        # check if File path for sink is chosen if option enabled
        if self.t_rbtn_File.isChecked() and (str(self.t_label_sink.text()) == "select path"):
            self.t_label_sink.setStyleSheet('color: red')
            arguments_incomplete = True

        if arguments_incomplete is False:
            self.my_transmitter = transmit_thread(self.t_spinbox_frequency.value(),
                                              self.t_spin_num_subch.value(),
                                              str(self.t_edit_ensemble_label.text()),
                                              str(self.t_edit_service_label.text()),
                                              self.t_combo_language.currentIndex(),
                                              protection_array, data_rate_n_array,
                                              audio_paths,
                                              self.t_rbtn_USRP.isChecked(),
                                              str(self.t_label_sink.text())+ "/" +str(self.t_edit_file_name.text()),
                                              self.t_spin_listen_to_component.value())
            # enable play button
            self.t_btn_play.setEnabled(True)
            self.t_label_status.setText("ready to transmit")

    def t_run_transmitter(self):
        self.t_btn_stop.setEnabled(True)
        self.t_slider_volume.setEnabled(True)
        self.t_label_status.setText("transmitting..")
        self.my_transmitter.start()

    def t_set_volume(self):
        self.my_transmitter.set_volume(float(self.t_slider_volume.value())/100)

    def t_stop_transmitter(self):
        self.my_transmitter.stop_transmitter()
        self.t_btn_stop.setEnabled(False)
        self.t_slider_volume.setEnabled(False)
        self.t_label_status.setText("not running")

    def t_set_file_path(self):
        path = QtGui.QFileDialog.getExistingDirectory(self, "Pick a folder for your file sink")
        if path:  # if user didn't pick a directory don't continue
            # display path in path label
            self.t_label_sink.setText(path)
            self.t_label_sink.setStyleSheet('color: black')

    def t_set_subch_path1(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Pick a .wav file as audio source")
        if path:  # if user didn't pick a directory don't continue
            # set new path in dict components
            self.components[0]["src_path"] = str(path)
            # display path in path label
            self.components[0]["src_path_disp"].setText(path)
            self.components[0]["src_path_disp"].setStyleSheet('color: black')

    def t_set_subch_path2(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Pick a .wav file as audio source")
        if path:  # if user didn't pick a directory don't continue
            # set new path in dict components
            self.components[1]["src_path"] = str(path)
            # display path in path label
            self.components[1]["src_path_disp"].setText(path)
            self.components[1]["src_path_disp"].setStyleSheet('color: black')

    def t_set_subch_path3(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Pick a .wav file as audio source")
        if path:  # if user didn't pick a directory don't continue
            # set new path in dict components
            self.components[2]["src_path"] = str(path)
            # display path in path label
            self.components[2]["src_path_disp"].setText(path)
            self.components[2]["src_path_disp"].setStyleSheet('color: black')

    def t_set_subch_path4(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Pick a .wav file as audio source")
        if path:  # if user didn't pick a directory don't continue
            # set new path in dict components
            self.components[3]["src_path"] = str(path)
            # display path in path label
            self.components[3]["src_path_disp"].setText(path)
            self.components[3]["src_path_disp"].setStyleSheet('color: black')

    def t_set_subch_path5(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Pick a .wav file as audio source")
        if path:  # if user didn't pick a directory don't continue
            # set new path in dict components
            self.components[4]["src_path"] = str(path)
            # display path in path label
            self.components[4]["src_path_disp"].setText(path)
            self.components[4]["src_path_disp"].setStyleSheet('color: black')

    def t_set_subch_path6(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Pick a .wav file as audio source")
        if path:  # if user didn't pick a directory don't continue
            # set new path in dict components
            self.components[5]["src_path"] = str(path)
            # display path in path label
            self.components[5]["src_path_disp"].setText(path)
            self.components[5]["src_path_disp"].setStyleSheet('color: black')

    def t_set_subch_path7(self):
        path = QtGui.QFileDialog.getOpenFileName(self, "Pick a .wav file as audio source")
        if path:  # if user didn't pick a directory don't continue
            # set new path in dict components
            self.components[6]["src_path"] = str(path)
            # display path in path label
            self.components[6]["src_path_disp"].setText(path)
        self.components[7]["src_path_disp"].setStyleSheet('color: black')

    def t_changed_audio_component(self):
        if hasattr(self, 'my_transmitter'):
            print "set audio sink"


    ################################
    # Receiver functions
    ################################

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

    def init_receiver(self):
        # write center frequency from spin box value
        self.frequency = self.spinbox_frequency.value()
        self.snr_timer.stop()
        # create a new Thread for reception and start it
        self.my_receiver = receive_thread(self.frequency, self.bit_rate, self.address, self.size, self.protection,
                                          self.src_is_USRP, self.file_path)
        self.my_receiver.start()
        self.snr_timer.start(1000)
        print "finished initializing"

    def snr_update(self):
        self.label_SNR.setText(str(self.my_receiver.get_snr()))
        SNR = int(self.my_receiver.get_snr())
        self.bar_snr.setValue(SNR)
        if SNR > 10:
            self.setStyleSheet("""QProgressBar::chunk { background: "green"; }""")
        elif 5 < SNR <= 10:
            self.setStyleSheet("""QProgressBar::chunk { background: "yellow"; }""")
        else:
            self.setStyleSheet("""QProgressBar::chunk { background: "red"; }""")
        print "color set to blue"

    def stop_reception(self):
        self.my_receiver.stop_reception()
        self.btn_stop.setEnabled(False)
        self.btn_play.setText("Play")
        self.btn_play.setEnabled(True)
        self.slider_volume.setEnabled(False)
        self.btn_record.setEnabled(True)
        self.my_receiver.set_record(False)
        self.snr_timer.stop()

    def play_audio(self):
        if not self.slider_volume.isEnabled():
            # play button pressed
            self.btn_play.setText("Mute")
            self.btn_stop.setEnabled(True)
            self.slider_volume.setEnabled(True)
            self.slider_volume.setValue(self.volume)
            self.set_volume()
            if self.need_new_init:
                self.snr_timer.stop()
                self.my_receiver = receive_thread(self.frequency, self.bit_rate, self.address, self.size,
                                                  self.protection, self.src_is_USRP, self.file_path)
                self.my_receiver.start()
        else:
            # mute button pressed
            self.btn_play.setText("Play")
            self.volume = self.slider_volume.value()
            self.slider_volume.setValue(0)
            self.slider_volume.setEnabled(False)
            self.set_volume()
            self.need_new_init = False
        self.snr_timer.start(1000)

    def record_audio(self):
        self.btn_record.setEnabled(False)
        self.btn_play.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.my_receiver = receive_thread(self.frequency, self.bit_rate, self.address, self.size, self.protection,
                                          self.src_is_USRP, self.file_path)
        self.my_receiver.set_record(True)
        self.my_receiver.start()
        self.snr_timer.stop()

    def set_volume(self):
        print self.slider_volume.value() / 100
        self.my_receiver.set_volume(float(self.slider_volume.value()) / 100)

    def update_service_info(self):
        # remove all old data first
        while (self.table_mci.rowCount() > 0):
            self.table_mci.removeRow(0)

        # get new data from FIC
        service_data = self.my_receiver.get_service_info()
        service_labels = self.my_receiver.get_service_labels()

        for n, key in enumerate(sorted(service_data, key=lambda service_data: service_data['ID'])):
            # add a new row
            self.table_mci.insertRow(n)
            # print ID in first collumn
            self.table_mci.setItem(n, 0, QtGui.QTableWidgetItem(str(key['ID'])))
            # print reference (later label)
            self.table_mci.setItem(n, 1, QtGui.QTableWidgetItem(
                (item for item in service_labels if item['reference'] == key['reference']).next()['label']))
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
        service_label = (item for item in self.my_receiver.get_service_labels() if
                         item['reference'] == int(reference)).next()
        subch_data = (item for item in self.my_receiver.get_subch_info() if item['ID'] == int(ID)).next()
        #programme_type = (item for item in self.my_receiver.get_programme_type() if item['reference'] == int(reference)).next()
        programme_type = next((item for item in self.my_receiver.get_programme_type() if item["reference"] == reference), {"programme_type":0,"language":0})


        # update sub-channel info for receiver
        self.address = int(subch_data['address'])
        print "set address to: " + str(subch_data['address'])
        self.size = int(subch_data['size'])
        print "set address to: " + str(subch_data['size'])
        self.protection = int(subch_data['protection'])
        print "set protection mode to: " + str(subch_data['protection'])
        self.bit_rate = self.size * 8/6
        print "set bit rate to: " + str(self.bit_rate)

        # ensemble info
        self.txt_info.insertPlainText("Ensemble: " + ensemble_data.keys()[0] + "\n")
        self.txt_info.insertPlainText(
            "Country: " + str(self.table.country_ID_ECC_E0[int(ensemble_data.values()[0]['country_ID'])] + "\n"))  # TODO: lookup table for country IDs

        # service info
        self.txt_info.insertPlainText("Service: " + service_label['label'] + "\n")
        self.txt_info.insertPlainText("Bit rate: " + str(subch_data['size']*8/6) + " kbit/s" + "\n")
        self.txt_info.insertPlainText("Protection Level: " + self.table.protection_EEP_set_A[subch_data['protection']] + "\n")

        self.txt_info.insertPlainText("Type: " + ("primary" if service_data['primary'] == True else "secondary") + "\n")
        self.txt_info.insertPlainText("DAB version: " + ("DAB+" if service_data['DAB+'] == True else "DAB") + "\n")
        self.label_dabplus.setText(("DAB+" if service_data['DAB+'] == True else "DAB "))

        # sub-channel info
        self.txt_info.insertPlainText("Programme Type: " + str(self.table.programme_types[int(programme_type['programme_type'])]) + "\n")
        self.txt_info.insertPlainText(
            "Programme Language: " + str(self.table.languages[int(programme_type['language'])]) + "\n")

    def test(self):
        self.bar_snr.setValue(19)


        print "did test"

class lookup_table:
    languages = [
        "unknown language",
        "Albanian",
        "Breton",
        "Catalan",
        "Croatian",
        "Welsh",
        "Czech",
        "Danish",
        "German",
        "English",
        "Spanish",
        "Esperanto",
        "Estonian",
        "Basque",
        "Faroese",
        "French",
        "Frisian",
        "Irish",
        "Gaelic",
        "Galician",
        "Icelandic",
        "Italian",
        "Lappish",
        "Latin",
        "Latvian",
        "Luxembourgian",
        "Lithuanian",
        "Hungarian",
        "Maltese",
        "Dutch",
        "Norwegian",
        "Occitan",
        "Polish",
        "Postuguese",
        "Romanian",
        "Romansh",
        "Serbian",
        "Slovak",
        "Slovene",
        "Finnish",
        "Swedish",
        "Tuskish",
        "Flemish",
        "Walloon"
    ]
    programme_types = [
        "No programme type",
        "News",
        "Current Affairs",
        "Information",
        "Sport",
        "Education",
        "Drama",
        "Culture",
        "Science",
        "Varied",
        "Pop Music",
        "Rock Music",
        "Easy Listening Music",
        "Light Classical",
        "Serious Classical",
        "Other Music",
        "Weather/meteorology",
        "Finance/Business",
        "Children's programmes",
        "Social Affairs",
        "Religion",
        "Phone In",
        "Travel",
        "Leisure",
        "Jazz Music",
        "Country Music",
        "National Music",
        "Oldies Music",
        "Folk Music",
        "Documentary",
        "None",
        "None"
    ]
    country_ID_ECC_E0 = [
        "None",
        "Germany",
        "Algeria",
        "Andorra",
        "Israel",
        "Italy",
        "Belgium",
        "Russian Federation",
        "Azores (Portugal)",
        "Albania",
        "Austria",
        "Hungary",
        "Malta",
        "Germany",
        "Canaries (Spain)",
        "Egypt"
    ]
    protection_EEP_set_A = [
        "1-A",
        "2-A",
        "3-A",
        "4-A"
    ]

def main():
    app = QtGui.QApplication(sys.argv)
    form = DABstep()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
