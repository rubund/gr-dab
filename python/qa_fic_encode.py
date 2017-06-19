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

class qa_fic_encode (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        self.symbol_length = 32*4
        self.dab_params = dab.parameters.dab_parameters(1, 208.064e6, True)

        # source
        self.dp = dab.parameters.dab_parameters(1, 208.064e6, True)
        self.fib_src = dab.fib_source_b_make(1, 1, "ensemble1", "service1", "bla", 4, 2, 15)
        #self.source = blocks.file_source_make(gr.sizeof_gr_complex, "debug/170524/ofdm_deinterleaved.dat")

        # encoder
        self.fib_enc = dab.fic_encode(self.dab_params)

        # mapper
        self.s2v_map = blocks.stream_to_vector_make(gr.sizeof_char, self.dp.num_carriers/4)
        self.map = dab.qpsk_mapper_vbc_make(self.dp.num_carriers)
        #self.v2s_map = blocks.vector_to_stream_make(gr.sizeof_gr_complex, self.dp.fic_punctured_codeword_length*4)

        # demapper
        self.soft_interleaver = dab.complex_to_interleaved_float_vcf_make(self.dp.num_carriers)

        # decode
        self.fic_decoder = dab.fic_decode(self.dab_params)

        # control stream
        self.trigger_src = blocks.vector_source_b([1] + [0]*(74), True)






        #self.file_sink = blocks.file_sink_make(gr.sizeof_gr_complex, "debug/170524/.dat")
        self.sink = blocks.vector_sink_c()

        self.tb.connect(self.fib_src,
                        blocks.head_make(gr.sizeof_char, 10000000),
                        self.fib_enc,
                        self.s2v_map,
                        self.map,
                        #self.v2s_map,
                        self.soft_interleaver,
                        self.fic_decoder)
        self.tb.connect(self.trigger_src, (self.fic_decoder, 1))


        self.tb.run ()
        result = self.sink.data()
        for item in result:
           print(item)
        pass


if __name__ == '__main__':
    gr_unittest.run(qa_fic_encode, "qa_fic_encode.xml")
