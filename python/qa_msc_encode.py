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
import os
import dab


class qa_msc_encode(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

# manual check
# debug data has to be produced with python script "/../apps/usrp_dab_rx.py"
    def test_001_t(self):
        if os.path.exists("debug/transmission_frame_generated_blaba.dat"):
            self.dp = dab.parameters.dab_parameters(1, 208.064e6, True)

            self.src = blocks.file_source_make(gr.sizeof_char, "debug/transmission_frame_generated_blaba.dat")
            self.unpack = blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST)

            # mapper
            self.map = dab.mapper_bc_make(self.dp.num_carriers)

            # demapper
            self.s2v = blocks.stream_to_vector_make(gr.sizeof_gr_complex, self.dp.num_carriers)
            self.soft_interleaver = dab.complex_to_interleaved_float_vcf_make(self.dp.num_carriers)

            # decode
            self.fic_decoder = dab.fic_decode(self.dp)
            self.msc_decoder = dab.msc_decode(self.dp, 90, 90, 2)

            # sink
            self.file_sink = blocks.file_sink_make(gr.sizeof_char, "debug/encoder_subch_decoded.dat")

            # control stream
            self.trigger_src = blocks.vector_source_b([1] + [0] * 74, True)

            self.tb.connect(self.src, self.unpack, self.map, self.s2v, self.soft_interleaver, self.msc_decoder)
            self.tb.connect(self.trigger_src, (self.msc_decoder, 1))
            self.tb.run()
        pass


if __name__ == '__main__':
    gr_unittest.run(qa_msc_encode, "qa_msc_encode.xml")
