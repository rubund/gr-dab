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


class usrp_dab_tx(gr.top_block):
    def __init__(self,  frequency, num_subch, ensemble_label, service_label, language, protections, data_rates_n, src_paths, use_usrp, sink_path = "dab_iq_generated.dat"):
        gr.top_block.__init__(self)

        # set logger level to WARN (no DEBUG logs)
        log = gr.logger("log")
        log.set_level("WARN")

        self.dab_mode = 1
        self.frequency = frequency
        interp = 64
        self.sample_rate = 128e6 / interp
        self.dp = dab.parameters.dab_parameters(self.dab_mode, 2000000, False)

        self.num_subch = num_subch
        self.ensemble_label = ensemble_label
        self.service_label = service_label
        self.language = language
        self.protections = protections
        self.data_rates_n = data_rates_n
        self.subch_sizes = 6 * data_rates_n
        self.src_paths = src_paths
        self.use_usrp = use_usrp
        self.sink_path = sink_path

        ########################
        # FIC
        ########################
        # source
        self.fic_src = dab.fib_source_b_make(self.dab_mode, self.num_subch, self.ensemble_label, self.service_label, "", self.language, self.protections, self.data_rates_n)
        # encoder
        self.fic_enc = dab.fic_encode(self.dp)

        ########################
        # MSC
        ########################
        self.msc_sources = [None] * self.num_subch
        self.f2s_left_converters = [blocks.float_to_short_make(1, 32767)] * self.num_subch
        self.f2s_right_converters = [blocks.float_to_short_make(1, 32767)] * self.num_subch
        self.mp4_encoders = [None] * self.num_subch
        self.rs_encoders = [None] * self.num_subch
        self.msc_encoders = [None] * self.num_subch
        for i in range(0, self.num_subch):
            # source
            self.msc_sources[i] = blocks.wavfile_source_make(self.src_paths[i])
            # mp4 encoder and Reed-Solomon encoder
            self.mp4_encoders[i] = dab.mp4_encode_sb_make(self.data_rates_n[i], 2, 32000, 1)
            self.rs_encoders[i] = dab.reed_solomon_encode_bb_make(self.data_rates_n[i])
            # encoder
            self.msc_encoders[i] = dab.msc_encode(self.dp, self.data_rates_n[i], self.protections[i])

        ########################
        # MUX
        ########################
        self.mux = dab.dab_transmission_frame_mux_bb_make(self.dab_mode, self.num_subch, self.subch_sizes)
        self.trigsrc = blocks.vector_source_b([1] + [0] * (self.dp.symbols_per_frame - 1), True)

        ########################
        # Modulator
        ########################
        self.s2v_mod = blocks.stream_to_vector(gr.sizeof_char, 384)
        self.mod = dab.ofdm_mod(self.dp)

        ########################
        # Sink
        ########################
        if self.use_usrp:
            self.sink = uhd.usrp_sink("", uhd.io_type.COMPLEX_FLOAT32, 1)
            self.sink.set_samp_rate(self.sample_rate)
            self.sink.set_antenna("TX/RX")
            self.sink.set_center_freq(self.frequency)
        else:
            self.sink = blocks.file_sink_make(gr.sizeof_gr_complex, "dab_iq_generated.dat")

        ########################
        # Connections
        ########################
        self.connect(self.fic_src, self.fic_enc, (self.mux, 0))
        for i in range(0, self.num_subch):
            self.connect((self.msc_sources[i], 0), self.f2s_left_converters[i], (self.mp4_encoders[i], 0), self.rs_encoders[i], self.msc_encoders[i], (self.mux, i+1))
            self.connect((self.msc_sources[i], 1), self.f2s_right_converters[i], (self.mp4_encoders[i], 1))
        self.connect((self.mux, 0), self.s2v_mod, (self.mod, 0))
        self.connect(self.trigsrc, (self.mod, 1))
        self.connect(self.mod, self.sink)

    def transmit(self):
        tx = usrp_dab_tx()
        tx.run()

