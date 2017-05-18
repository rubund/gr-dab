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

class qa_msc_decode (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

#manual check if data comes threw in transmission mode 1 (default)
    def test_001_t (self):
        self.src = blocks.file_source_make(gr.sizeof_float * 2*1536)
        self.dp = dab.parameters.dab_parameters(1 , 208.064e6)
        self.msc_demod = dab.msc_decode(self.dp, 54, 84, 2, False, False)
        self.sink = blocks.file_sink_make(gr.sizeof_char * self.dp.msc_cu_size)

        self.tb.connect(self.src, self.msc_demod, self.sink)
        self.tb.run ()
        # check data
        pass

if __name__ == '__main__':
    gr_unittest.run(qa_msc_decode, "qa_msc_decode.xml")
