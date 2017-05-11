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
import numpy as np
import dab

class qa_fib_source_b (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        FIB_length = 240 #length of FIB in bit without CRC16
        src = dab.fib_source_b(1, 2, '__Galaxy_News', '_Galaxy_Radio1', 'Awesome_Mix_Vol1')
        throttle = blocks.throttle(gr.sizeof_char*1, 32000, True)
        dst = blocks.vector_sink_b();
        self.tb.run(240) #2880 bit = 12 FIBs
        result = dst.data()
        #FIB = result[:10]
        #print result
        assert (1)


if __name__ == '__main__':
    gr_unittest.run(qa_fib_source_b, "qa_fib_source_b.xml")
