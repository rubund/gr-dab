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
import dab

class qa_time_interleave_bb (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        vector01 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18)
        src = blocks.vector_source_b(vector01)
        s2v = blocks.stream_to_vector(gr.sizeof_char, 6)
        time_interleaver = dab.time_interleave_bb(6, [1, 0])
        v2s = blocks.vector_to_stream(gr.sizeof_char, 6)
        dst = blocks.vector_sink_b()
        self.tb.run ()
        result = dst.data()
        print result
        pass


if __name__ == '__main__':
    gr_unittest.run(qa_time_interleave_bb, "qa_time_interleave_bb.xml")
