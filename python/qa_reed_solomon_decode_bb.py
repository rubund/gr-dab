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
import os

class qa_reed_solomon_decode_bb (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        log = gr.logger("log")
        if os.path.exists("debug/checked_firecode.dat"):
            self.dab_params = dab.parameters.dab_parameters(1, 208.064e6, True)
            self.src = blocks.file_source_make(gr.sizeof_char, "debug/checked_firecode.dat")
            self.solomon = dab.reed_solomon_decode_bb_make(14)
            self.file_sink = blocks.file_sink_make(gr.sizeof_char, "debug/reed_solomon_repaired.dat")
            self.tb.connect(self.src, self.solomon, self.file_sink)
            self.tb.run()
        else:
            log.debug("debug file not found - skipped test")
            log.set_level("WARN")
        pass


if __name__ == '__main__':
    gr_unittest.run(qa_reed_solomon_decode_bb, "qa_reed_solomon_decode_bb.xml")
