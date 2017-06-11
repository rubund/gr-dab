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
        self.source = blocks.file_source_make(gr.sizeof_char, "debug/170524/.dat")

        # hard bit demapper
        self.s2v = blocks.stream_to_vector_make(gr.sizeof_gr_complex, self.dp.num_carriers)
        self.demap = dab.qpsk_demapper_vcb_make(self.dp.num_carriers)
        self.v2s = blocks.vector_to_stream_make(gr.sizeof_char, self.dp.num_carriers/4)

        # unpuncture
        self.b2f = blocks.char_to_float_make()
        self.unpuncture = dab.unpuncture_ff_make(self.dp.assembled_fic_puncturing_sequence)
        self.f2b = blocks.float_to_char_make()



        self.file_sink = blocks.file_sink_make(gr.sizeof_char, "debug/170524/hardbits_unpunctured.dat")

        self.tb.connect(self.source, self.b2f, self.unpuncture, self.f2b, self.file_sink)
        #self.tb.connect(self.prbs_src, (self.mod2, 1))
        self.tb.run()
        #result = self.sink.data()
        #for item in result:
        #    print(item)

        #print (result)
        pass


if __name__ == '__main__':
    gr_unittest.run(data_printer, "data_printer.xml")
