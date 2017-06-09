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

class qa_msc_encode (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        self.dab_params = dab.parameters.dab_parameters(1, 208.064e6, True)
        fib = (0xF1, 0x02)
        self.fib_src = blocks.vector_source_b(fib, True)
        self.fib_enc = dab.fic_encode(self.dab_params)
        self.sink = blocks.file_sink_make(gr.sizeof_char, "debug/generated_fic_encoded.dat")

        self.tb.connect(self.fib_src, self.fib_enc, self.sink)
        self.tb.run ()
        pass


if __name__ == '__main__':
    gr_unittest.run(qa_msc_encode, "qa_msc_encode.xml")
