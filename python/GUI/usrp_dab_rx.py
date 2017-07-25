#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 Moritz Luca Schmid, Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT).
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

"""
receive DAB with USRP
"""

from gnuradio import gr, uhd, blocks
from gnuradio import audio
import dab
import sys, time, threading, math


class usrp_dab_rx(gr.top_block):
    def __init__(self, frequency, bit_rate, address, size, protection):
        gr.top_block.__init__(self)



        # set logger level to WARN (no DEBUG logs)
        log = gr.logger("log")
        log.set_level("WARN")

        self.dab_mode = 1
        self.verbose = False

        self.src = uhd.usrp_source("", uhd.io_type.COMPLEX_FLOAT32, 1)
        self.sample_rate = 2e6
        self.src.set_samp_rate(self.sample_rate)
        self.src.set_antenna("TX/RX")

        # set paramters to default mode
        self.softbits = True
        self.filter_input = True
        self.autocorrect_sample_rate = False
        self.resample_fixed = 1
        self.correct_ffe = True
        self.equalize_magnitude = True
        self.frequency = frequency

        self.dab_params = dab.parameters.dab_parameters(self.dab_mode, self.sample_rate, self.verbose)
        self.rx_params = dab.parameters.receiver_parameters(self.dab_mode, self.softbits,
                                                            self.filter_input,
                                                            self.autocorrect_sample_rate,
                                                            self.resample_fixed,
                                                            self.verbose, self.correct_ffe,
                                                            self.equalize_magnitude)

        # create OFDM demodulator block
        self.demod = dab.ofdm_demod(self.dab_params, self.rx_params, self.verbose)

        # create FIC decoder
        self.fic_dec = dab.fic_decode(self.dab_params)

        # create MSC decoder for audio reception
        self.dabplus = dab.dabplus_audio_decoder_ff(self.dab_params, bit_rate, address, size, protection, True)
        self.audio = audio.sink_make(32000)

        # connect everything
        self.connect(self.src, self.demod, (self.fic_dec, 0))
        self.connect((self.demod, 1), (self.fic_dec, 1))
        self.connect((self.demod, 0), (self.dabplus, 0))
        self.connect((self.demod, 1), (self.dabplus, 1))

        # connect audio to sound card
        # left stereo channel
        self.connect((self.dabplus, 0), (self.audio, 0))
        # right stereo channel
        self.connect((self.dabplus, 1), (self.audio, 1))

        # tune frequency
        self.set_freq(self.frequency)

        # set gain
        # if no gain was specified, use the mid-point in dB
        g = self.src.get_gain_range()
        self.rx_gain = float(g.start() + g.stop()) / 2
        self.src.set_gain(self.rx_gain)

    def get_mci(self):
        return self.fic_dec.get_mci()

    def update_ui_function(self):
        while self.run_ui_update_thread:
            var = self.demod.probe_phase_var.level()
            q = int(50 * (math.sqrt(var) / (math.pi / 4)))
            print "--> Phase variance: " + str(var) + "\n"
            print "--> Signal quality: " + '=' * (50 - q) + '>' + '-' * q + "\n"
            time.sleep(0.3)

    def correct_ffe(self):
        while self.run_correct_ffe_thread:
            diff = self.demod.sync.ffs_sample_and_average_arg.ffe_estimate()
            if abs(diff) > self.rx_params.usrp_ffc_min_deviation:
                self.frequency -= diff * self.rx_params.usrp_ffc_adapt_factor
                print "--> updating fine frequency correction: " + str(self.frequency)
                self.set_freq(self.frequency)
            time.sleep(1. / self.rx_params.usrp_ffc_retune_frequency)

    def set_freq(self, freq):
        if self.src.set_center_freq(freq):  # src.tune(0, self.subdev, freq):
            if self.verbose:
                print "--> retuned to " + str(freq) + " Hz"
            return True
        else:
            print "-> error - cannot tune to " + str(freq) + " Hz"
            return False

    def receive(self):
        rx = usrp_dab_rx()
        rx.run()

