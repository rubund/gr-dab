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
from gnuradio import blocks
import dab

class qa_dab_transmission_frame_mux_bb (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

# manual test with validation of FIBs over fib sink
    def test_001_t (self):
        self.dp = dab.parameters.dab_parameters(1, 208.064e6, True)

        # sources
        data01 = (0x01, 0x01)
        data02 = (0x02, 0x02)
        data03 = (0x03, 0x03)
        self.fib_src = dab.fib_source_b_make(1,1,'Galaxy_News', 'Wasteland_Radio', 'Country_Mix01', 0x09, [0], [8])
        self.fib_pack = blocks.unpacked_to_packed_bb_make(1, gr.GR_MSB_FIRST)
        self.subch_src01 = blocks.vector_source_b(data01, True)
        self.subch_src02 = blocks.vector_source_b(data02, True)
        self.subch_src03 = blocks.vector_source_b(data03, True)

        # encoder
        self.fib_enc = dab.fic_encode(self.dp)
        self.msc_encoder = dab.msc_encode(self.dp, 15, 2)
        self.null = blocks.null_source_make(gr.sizeof_char)

        # multiplexer
        self.mux = dab.dab_transmission_frame_mux_bb_make(1, 3, [90, 90, 90])

        # mapper
        self.unpack = blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST)
        self.map = dab.mapper_bc_make(self.dp.num_carriers)

        # demapper
        self.s2v = blocks.stream_to_vector_make(gr.sizeof_gr_complex, self.dp.num_carriers)
        self.soft_interleaver = dab.complex_to_interleaved_float_vcf_make(self.dp.num_carriers)

        # decode
        self.fic_decoder = dab.fic_decode(self.dp)

        # control stream
        self.trigger_src = blocks.vector_source_b([1] + [0] * 74, True)

        self.tb.connect(self.fib_src, self.fib_enc, (self.mux, 0))
        self.tb.connect(self.subch_src01, (self.mux, 1))
        self.tb.connect(self.subch_src02, self.msc_encoder, (self.mux, 2))
        self.tb.connect(self.subch_src03, (self.mux, 3))
        self.tb.connect((self.mux, 0), self.unpack, self.map, self.s2v, self.soft_interleaver, self.fic_decoder)
        self.tb.connect(self.trigger_src, blocks.head_make(gr.sizeof_char, 75*10), (self.fic_decoder, 1))
        self.tb.run ()
        pass





if __name__ == '__main__':
    gr_unittest.run(qa_dab_transmission_frame_mux_bb, "qa_dab_transmission_frame_mux_bb.xml")
