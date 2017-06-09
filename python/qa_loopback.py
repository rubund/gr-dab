#!/usr/bin/env python2
# -*- coding: utf8 -*-

# Copyright 2017 Moritz Luca Schmid, Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT).
#
#
# this code may be freely used under GNU GPL conditions

"""
send DAB with USRP
"""
from gnuradio import gr, gr_unittest
from gnuradio import uhd, blocks
import dab
import sys

# transmitting a simple dab signal and receiving it
class qa_loopback (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t(self):
        #interp = 64
        #self.sample_rate = 128e6 / interp
        self.dp = dab.parameters.dab_parameters(mode=1, sample_rate=2000000, verbose=True)

        # build transmission frame
        # FIC
        self.fic_src = dab.fib_source_b_make(1, 1, "Galaxy News", "Galaxy Radio", "Awesome Mix", 1, 2, 15)
        self.fic_encoder = dab.fic_encode(self.dp)
        # MSC
        self.data01 = (1, 2, 3, 4)
        self.subch_src_01 = blocks.vector_source_b_make(self.data01, True)
        self.msc_encoder = dab.msc_encode(self.dp, 15, 2)
        # MUX
        self.mux = dab.dab_transmission_frame_mux_bb_make(1, 1, [90])

        # prepare for mod
        self.s2v_data = blocks.stream_to_vector(gr.sizeof_char, 384)
        self.trigsrc = blocks.vector_source_b([1] + [0] * (self.dp.symbols_per_frame - 2), True)

        # ofdm modulation
        self.mod = dab.ofdm_mod(self.dp, verbose=True)


        # build reception frame
        # ofdm demodulation
        self.rx_params = dab.parameters.receiver_parameters(mode=1, softbits=True,
                                                            input_fft_filter=True,
                                                            autocorrect_sample_rate=False,
                                                            sample_rate_correction_factor=1,
                                                            verbose=True, correct_ffe=True,
                                                            equalize_magnitude=True)
        self.demod = dab.ofdm_demod(self.dp, self.rx_params, verbose=True)
        # fic sink
        self.fic_dec = dab.fic_decode(self.dp)
        # msc sink
        # file sink
        self.file_sink = blocks.file_sink_make(gr.sizeof_float*self.dp.num_carriers*2, "debug/loopback_demodulated.dat")
        self.file_sink_trigger = blocks.file_sink_make(gr.sizeof_char, "debug/loopback_demodulated_trigger.dat")

        # debug
        self.file_sink_mux = blocks.file_sink_make(gr.sizeof_char, "debug/loopback_MUX.dat")


        # connect everything
        # transmitter
        self.tb.connect(self.fic_src, self.fic_encoder, (self.mux, 0))
        self.tb.connect(self.subch_src_01, self.msc_encoder, (self.mux, 1))
        self.tb.connect((self.mux, 0), self.s2v_data, (self.mod, 0))
        self.tb.connect(self.trigsrc, (self.mod, 1))
        # loopback
        self.tb.connect(self.mod, self.demod)
        # receiver
        self.tb.connect(self.demod, (self.fic_dec, 0))
        self.tb.connect((self.demod, 1), (self.fic_dec, 1))
        self.tb.connect(self.demod, self.file_sink)
        self.tb.connect((self.demod, 1), self.file_sink_trigger)
        # debug
        self.tb.connect((self.mux, 0), self.file_sink_mux)

        self.tb.run()

if __name__ == '__main__':
    gr_unittest.run(qa_loopback, "qa_loopback.xml")
