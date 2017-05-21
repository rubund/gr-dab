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
import dab, time

class qa_loopback_crc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

#test_crc: loopback to crc16 (included)
    def test_crc001 (self):
        #test with real SI(label) from SWR1
        src_data01 = (0x35, 0x00, 0x10, 0xea, 0x53, 0x57, 0x52, 0x20, 0x42, 0x57, 0x20, 0x4e, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0xff, 0x00, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        src = blocks.vector_source_b(src_data01)
        s2v = blocks.stream_to_vector(gr.sizeof_char, 32)
        repeat = blocks.repeat(gr.sizeof_char * 32, 10)
        crc16 = dab.crc16_bb(32, 0x1021, 0xffff)
        v2s = blocks.vector_to_stream(gr.sizeof_char, 32)
        fibout = blocks.stream_to_vector(1, 32)
        fibsink = dab.fib_sink_vb()
        dst = blocks.vector_sink_b()

        self.tb.connect(src, s2v, repeat, crc16, v2s, fibout, fibsink)
        self.tb.run()
        pass

    def test_crc002 (self):
        #test with produced SI
        src_data02 = (0x35, 0x00, 0x40, 0x00, 0x5f, 0x5f, 0x47, 0x61, 0x6c, 0x61, 0x78, 0x79, 0x5f, 0x4e, 0x65, 0x77, 0x73, 0x5f, 0x5f, 0x5f, 0x38, 0xf8, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        src = blocks.vector_source_b(src_data02)
        s2v = blocks.stream_to_vector(gr.sizeof_char, 32)
        repeat = blocks.repeat(gr.sizeof_char * 32, 10)
        crc16 = dab.crc16_bb(32, 0x1021, 0xffff)
        v2s = blocks.vector_to_stream(gr.sizeof_char, 32)
        fibout = blocks.stream_to_vector(1, 32)
        fibsink = dab.fib_sink_vb()
        dst = blocks.vector_sink_b()

        self.tb.connect(src, s2v, repeat, crc16, v2s, fibout, fibsink)
        self.tb.run()
        pass

#test with fib_source
    def test_003_t (self):
        src = dab.fib_source_b_make(1, 1, 'ensemble', 'service', 'talk')
        fib_unpacked_to_packed = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        s2v = blocks.stream_to_vector(gr.sizeof_char, 32)
        crc16 = dab.crc16_bb(32, 0x1021, 0xffff)
        v2s = blocks.vector_to_stream(gr.sizeof_char, 32)
        fibout = blocks.stream_to_vector(1, 32)
        fibsink = dab.fib_sink_vb()
        dst = blocks.vector_sink_b()

        self.tb.connect(src, fib_unpacked_to_packed, blocks.head(gr.sizeof_char, 1000), s2v, crc16, v2s, fibout, fibsink)
        self.tb.run()

        pass

# #test_energy: loopback to energy_dispersal (included)
# def test_energy002(self):
#     # test with produced SI
#     src_data02 = (
#     0x35, 0x00, 0x40, 0x00, 0x5f, 0x5f, 0x47, 0x61, 0x6c, 0x61, 0x78, 0x79, 0x5f, 0x4e, 0x65, 0x77, 0x73, 0x5f, 0x5f,
#     0x5f, 0x38, 0xf8, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
#     src = blocks.vector_source_b(src_data02)
#     s2v = blocks.stream_to_vector(gr.sizeof_char, 32)
#     repeat = blocks.repeat(gr.sizeof_char * 32, 10)
#     crc16 = dab.crc16_bb(32, 0x1021, 0xffff)
#     add_mod_2 = blocks.xor_bb()
#     self.dp = dab.parameters.dab_parameters(1, 2e6, False)
#     prbs_src = blocks.vector_source_b(self.dp.prbs(self.dp.energy_dispersal_fic_vector_length), True)
#     fib_packed_to_unpacked = blocks.packed_to_unpacked_bb(1, gr.GR_MSB_FIRST)
#     fib_unpacked_to_packed = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
#     v2s = blocks.vector_to_stream(gr.sizeof_char, 32)
#     dst = blocks.vector_sink_b()
#
#     self.tb.connect(src, s2v, crc16, fib_packed_to_unpacked, add_mod_2, fib_unpacked_to_packed, v2s, dst)
#     self.tb.run()
#     result = dst.data()
#     self.assertEqual(src_data02, result)


if __name__ == '__main__':
    gr_unittest.run(qa_loopback_crc, "qa_loopback_crc.xml")
