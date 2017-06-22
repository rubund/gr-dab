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

from gnuradio import gr, gr_unittest
from gnuradio import blocks, trellis
import dab
from math import sqrt

class qa_conv_encoder_bb (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        self.dp = dab.parameters.dab_parameters(1, 208.064e6, True)
        data02 = (0x05, 0x00, 0x10, 0xEA)
        self.source = blocks.vector_source_b(data02)
        self.conv_encoder = dab.conv_encoder_bb_make(4)
        self.conv_unpack = blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST)
        #self.conv_encoder_config = fec.cc_encoder_make(self.dp.energy_dispersal_fic_vector_length, 7, 4, [0133, 0171, 0145, 0133], 0, fec.CC_TERMINATED)
        #self.conv_cc_encoder = fec.extended_encoder(self.conv_encoder_config, None)

        # mapper
        self.map = dab.mapper_bc_make(32)
        # self.v2s_map = blocks.vector_to_stream_make(gr.sizeof_gr_complex, self.dp.fic_punctured_codeword_length*4)

        # demapper
        self.s2v = blocks.stream_to_vector_make(gr.sizeof_gr_complex, 32)
        self.soft_interleaver = dab.complex_to_interleaved_float_vcf_make(32)
        self.v2s = blocks.vector_to_stream_make(gr.sizeof_float, 2*32)

        # convolutional decoding
        # self.fsm = trellis.fsm(self.dp.conv_code_in_bits, self.dp.conv_code_out_bits, self.dp.conv_code_generator_polynomials)
        self.fsm = trellis.fsm(1, 4, [0133, 0171, 0145, 0133])  # OK (dumped to text and verified partially)
        # self.conv_decode = trellis.viterbi_combined_fb(self.fsm, 20, 0, 0, 1, [1./sqrt(2),-1/sqrt(2)] , trellis.TRELLIS_EUCLIDEAN)
        table = [
            0, 0, 0, 0,
            0, 0, 0, 1,
            0, 0, 1, 0,
            0, 0, 1, 1,
            0, 1, 0, 0,
            0, 1, 0, 1,
            0, 1, 1, 0,
            0, 1, 1, 1,
            1, 0, 0, 0,
            1, 0, 0, 1,
            1, 0, 1, 0,
            1, 0, 1, 1,
            1, 1, 0, 0,
            1, 1, 0, 1,
            1, 1, 1, 0,
            1, 1, 1, 1
        ]
        assert (len(table) / 4 == self.fsm.O())
        table = [(1 - 2 * x) / sqrt(2) for x in table]
        self.conv_decode = trellis.viterbi_combined_fb(self.fsm, 32/4, 0, 0, 4, table, trellis.TRELLIS_EUCLIDEAN)
        self.conv_prune = dab.prune_make(gr.sizeof_char, 32/4, 0, 6)
        self.sink1 = blocks.vector_sink_b()
        self.sink2 = blocks.vector_sink_b()
        self.sink3 = blocks.vector_sink_b()

        self.tb.connect(self.source, self.conv_encoder, self.conv_unpack, self.map, self.s2v, self.soft_interleaver, self.v2s, self.conv_decode, self.sink1)
        self.tb.connect(self.source, blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST), self.sink2)
        self.tb.connect(self.conv_encoder, blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST), self.sink3)
        self.tb.run ()
        result = self.sink1.data()
        data = self.sink2.data()
        encoded = self.sink3.data()
        print data
        print len(data)
        print result
        self.assertEqual(data, result)


if __name__ == '__main__':
    gr_unittest.run(qa_conv_encoder_bb, "qa_conv_encoder_bb.xml")
