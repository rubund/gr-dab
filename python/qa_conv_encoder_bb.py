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
from gnuradio import blocks, fec
import dab

class qa_conv_encoder_bb (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    # def test_001_t (self):
    #     data02 = (
    #         0x05, 0x00, 0x10, 0xEA, 0x04, 0x24, 0x06, 0x02, 0xD3, 0xA6, 0x01, 0x3F, 0x06, 0xFF, 0x00, 0x00, 0x00, 0x00,
    #         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4C, 0x89)
    #     src = blocks.vector_source_b(data02)
    #     encoder = dab.conv_encoder_bb_make(32)
    #     dst1 = blocks.vector_sink_b()
    #     self.tb.connect(src, encoder, dst1)
    #     self.tb.run ()
    #     result = dst1.data()
    #     for item in result:
    #        print(item)
    #     #print result
    #     pass

    def test_001_t (self):
        data02 = (
            0x05, 0x00, 0x10, 0xEA, 0x04, 0x24, 0x06, 0x02, 0xD3, 0xA6, 0x01, 0x3F, 0x06, 0xFF, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x4C, 0x89)
        src = blocks.vector_source_b(data02)
        self.conv_encoder_config = fec.cc_encoder_make(32*8, 7, 4, [91, 121, 101, 91], 0, fec.CC_TERMINATED)
        self.conv_encoder = fec.extended_encoder(self.conv_encoder_config, None, "1")
        dst1 = blocks.vector_sink_b()
        self.tb.connect(src, blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST), self.conv_encoder, blocks.unpacked_to_packed_bb_make(1, gr.GR_MSB_FIRST), dst1)
        self.tb.run ()
        result = dst1.data()
        for item in result:
           print(item)
        #print result
        pass

if __name__ == '__main__':
    gr_unittest.run(qa_conv_encoder_bb, "qa_conv_encoder_bb.xml")
