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
        fib = (0x05, 0x00, 0x10, 0xEA, 0x03, 0x8E, 0x06, 0x02, 0xD3, 0xA6, 0x01, 0x3F, 0x06, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        self.fib_src = blocks.vector_source_b(fib, True)
        self.fib_src_unpack = blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST)

        # encoder
        self.fib_enc = dab.fic_encode(self.dab_params)

        # mapper
        self.s2v_map = blocks.stream_to_vector_make(gr.sizeof_char, self.symbol_length / 4)
        self.map = dab.qpsk_mapper_vbc_make(self.symbol_length)

        # demapper
        self.soft_interleaver = dab.complex_to_interleaved_float_vcf_make(self.symbol_length)
        self.v2s_interleave = blocks.vector_to_stream_make(gr.sizeof_float, self.symbol_length * 2)

        # decode
        self.s2v_fic_dec = blocks.stream_to_vector_make(gr.sizeof_float, 3072)
        self.fic_decoder = dab.fic_decode(self.dab_params)

        # control stream
        self.trigger_src = blocks.vector_source_b([1] + [0]*(74), True)






        self.sink = blocks.file_sink_make(gr.sizeof_char, "debug/generated_fic_encoded.dat")

        self.tb.connect(self.fib_src,
                        self.fib_src_unpack,
                        self.fib_enc,
                        self.s2v_map,
                        self.map,
                        self.soft_interleaver,
                        self.v2s_interleave,
                        self.s2v_fic_dec,
                        self.fic_decoder)
        self.tb.connect(self.trigger_src, (self.fic_decoder, 1))


        self.tb.run ()
        pass


if __name__ == '__main__':
    gr_unittest.run(qa_fic_encode, "qa_fic_encode.xml")
