#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 Moritz Luca Schmid, Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT)..
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

class qa_append_bb (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        data = (
            0x1D, 0x13, 0x06, 0x00, 0x00, 0x01, 0x0B, 0x00, 0x00, 0x05, 0x03, 0x00, 0x00, 0x09, 0x07, 0x00, 0x00, 0x04,
            0x09, 0x00, 0x00, 0x0C, 0x02, 0x00, 0x00, 0x02, 0x08, 0x00, 0x00, 0x0A, 0x00, 0x00)
        expected_result = (
            0x1D, 0x13, 0x06, 0x00, 0x00, 0x01, 0x0B, 0x00, 0x00, 0x05, 0x03, 0x00, 0x00, 0x09, 0x07, 0x00, 0x00, 0x04,
            0x09, 0x00, 0x00, 0x0C, 0x02, 0x00, 0x00, 0x02, 0x08, 0x00, 0x00, 0x0A, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF)
        src = blocks.vector_source_b(data)
        append = dab.append_bb_make(32, 36, 0xFF)
        dst = blocks.vector_sink_b()
        self.tb.connect(src, append, dst)
        self.tb.run ()
        result = dst.data()
        self.assertEqual(expected_result, result)

    def test_002_t (self):
        data = (0x01, 0x02, 0x03)
        expected_result = (0x01, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        src = blocks.vector_source_b(data)
        append = dab.append_bb_make(3, 13)
        dst = blocks.vector_sink_b()
        self.tb.connect(src, append, dst)
        self.tb.run ()
        result = dst.data()
        self.assertEqual(expected_result, result)

if __name__ == '__main__':
    gr_unittest.run(qa_append_bb, "qa_append_bb.xml")
