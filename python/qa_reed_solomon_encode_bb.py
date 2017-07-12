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
import random
import dab

class qa_reed_solomon_encode_bb (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        self.prbs = [random.randint(0,255) for r in xrange (220)]
        self.src = blocks.vector_source_b(self.prbs)
        self.sink1 = blocks.vector_sink_b_make()
        self.rs_encoder = dab.reed_solomon_encode_bb_make(2)
        self.rs_decoder = dab.reed_solomon_decode_bb_make(2)
        self.sink2 = blocks.vector_sink_b_make()
        self.tb.connect(self.src, self.sink1)
        self.tb.connect(self.src, self.rs_encoder, self.sink2)
        self.tb.run ()
        data = self.sink1.data()
        result = self.sink2.data()
        print data
        print result
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_reed_solomon_encode_bb, "qa_reed_solomon_encode_bb.xml")
