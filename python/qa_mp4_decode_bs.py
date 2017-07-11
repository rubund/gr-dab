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

class qa_mp4_decode_bs (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

# manula check, if header info makes sense and if AAC gives errors
    def test_001_t (self):
        if os.path.exists("debug/reed_solomon_repaired.dat"):
            #self.dab_params = dab.parameters.dab_parameters(1, 208.064e6, True)
            self.src = blocks.file_source_make(gr.sizeof_char, "debug/reed_solomon_repaired.dat")
            self.mp4 = dab.mp4_decode_bs_make(14)
            self.file_sink_left = blocks.file_sink_make(gr.sizeof_short, "debug/PCM_left.dat")
            self.file_sink_right = blocks.file_sink_make(gr.sizeof_short, "debug/PCM_right.dat")
            self.tb.connect(self.src, (self.mp4, 0), self.file_sink_left)
            self.tb.connect((self.mp4, 1), self.file_sink_right)
            self.tb.run()
        else:
            log = gr.logger("log")
            log.debug("debug file not found - skipped test")
            log.set_level("WARN")
        pass


if __name__ == '__main__':
    gr_unittest.run(qa_mp4_decode_bs, "qa_mp4_decode_bs.xml")
