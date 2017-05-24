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
        self.dab_params = dab.parameters.dab_parameters(1 , 208.064e6, True)
        self.src01 = blocks.file_source_make(gr.sizeof_float * 2*self.dab_params.num_carriers, "debug/transmission_frame.dat")
        self.src02 = blocks.file_source_make(gr.sizeof_char, "debug/transmission_frame_trigger.dat")
        self.msc = dab.msc_decode(self.dab_params, 54, 84, 2, 1, 1)
        #self.sink = blocks.file_sink_make(gr.sizeof_char * self.dab_params.msc_cu_size, "result.dat")
        self.sink = blocks.file_sink_make(gr.sizeof_float * self.dab_params.num_carriers * 2, "debug/result.dat")

        self.tb.connect(self.src01, (self.msc, 0), self.sink)
        self.tb.connect(self.src02, (self.msc, 1))
        self.tb.run ()
        # check data
        pass

if __name__ == '__main__':
    gr_unittest.run(qa_msc_decode, "qa_msc_decode.xml")
