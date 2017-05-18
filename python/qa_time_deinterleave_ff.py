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

class qa_time_deinterleave_ff (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        vector01 =        (1, 8, 3, 10, 5, 12,   7, 14, 9, 16, 11, 18,  13, 20, 15, 22, 17, 24,   19, 26, 21, 28, 23, 30)
        expected_result = (0, 0, 0,  0, 0,  0,   7,  8, 9, 10, 11, 12,  13, 14, 15, 16, 17, 18,   19, 20, 21, 22, 23, 24)
        src = blocks.vector_source_b(vector01, True)
        b2f = blocks.char_to_float_make()
        s2v = blocks.stream_to_vector(gr.sizeof_float, 6)
        time_deinterleaver = dab.time_deinterleave_ff(6, [0, 1])
        v2s = blocks.vector_to_stream(gr.sizeof_float, 6)
        f2b = blocks.float_to_char_make()
        dst = blocks.vector_sink_b()
        self.tb.connect(src, b2f, s2v, time_deinterleaver, blocks.head_make(gr.sizeof_float*6, 4), v2s, f2b, dst)
        self.tb.run()
        result = dst.data()
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    gr_unittest.run(qa_time_deinterleave_ff, "qa_time_deinterleave_ff.xml")
