#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
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

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from gnuradio import fec
import dab

class data_printer (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        self.dp = dab.parameters.dab_parameters(1, 208.064e6, True)
        self.source = blocks.file_source_make(gr.sizeof_gr_complex, "debug/170531/single_vectors/complex_symbols.dat")

        # encoder
        self.conv_encoder_config = fec.cc_encoder_make(self.dp.energy_dispersal_fic_vector_length, 7, 4, [91, 121, 101, 91], 0, fec.CC_TERMINATED)
        self.conv_encoder = fec.extended_encoder(self.conv_encoder_config, None, "1")

        # hard bit demapper
        self.s2v = blocks.stream_to_vector_make(gr.sizeof_gr_complex, self.dp.num_carriers)
        self.demap = dab.qpsk_demapper_vcb_make(self.dp.num_carriers)
        self.v2s = blocks.vector_to_stream_make(gr.sizeof_char, self.dp.num_carriers/4)

        # unpuncture
        self.b2f = blocks.char_to_float_make()
        self.unpuncture = dab.unpuncture_ff_make(self.dp.assembled_fic_puncturing_sequence)
        self.f2b = blocks.float_to_char_make()

        # pack / unpack
        self.packed2unpacked = blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST)


        #self.sink = blocks.vector_sink_b()
        self.file_sink = blocks.file_sink_make(gr.sizeof_char, "debug/170531/single_vectors/hardbits_unpacked.dat")

        self.tb.connect(self.source, self.s2v, self.demap, self.v2s, self.packed2unpacked, self.file_sink)
        #self.tb.connect(self.prbs_src, (self.mod2, 1))
        self.tb.run()
        #result = self.sink.data()
        #for item in result:
        #    print(item)

        #print (result)
        pass


if __name__ == '__main__':
    gr_unittest.run(data_printer, "data_printer.xml")
