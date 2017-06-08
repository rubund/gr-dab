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

    def test_001_t (self):
        # manual check if data is multiplexed properly
        fib = (0xFF, 0xFF)
        data01 = (1, 1)
        data02 = (2, 2)
        data03 = (3, 3)
        self.fib_src = blocks.vector_source_b(fib, True)
        self.subch_src01 = blocks.vector_source_b(data01, True)
        self.subch_src02 = blocks.vector_source_b(data02, True)
        self.subch_src03 = blocks.vector_source_b(data03, True)
        self.null = blocks.null_source_make(gr.sizeof_char)
        self.mux = dab.dab_transmission_frame_mux_bb_make(1, 2, [15, 15])
        self.dst = blocks.file_sink_make(gr.sizeof_char, "debug/transmission_frame_generated.dat")
        self.trigger_dst = blocks.file_sink_make(gr.sizeof_char, "debug/transmission_frame_generated_trigger.dat")

        self.tb.connect(self.fib_src, (self.mux, 0))
        self.tb.connect(self.subch_src01, (self.mux, 1))
        self.tb.connect(self.subch_src02, (self.mux, 2))
        self.tb.connect((self.mux, 0), self.dst)
        self.tb.connect((self.mux, 1), blocks.head_make(gr.sizeof_char, 100000), self.trigger_dst)
        self.tb.run ()
        pass





if __name__ == '__main__':
    gr_unittest.run(qa_dab_transmission_frame_mux_bb, "qa_dab_transmission_frame_mux_bb.xml")
