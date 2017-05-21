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

from gnuradio import gr, gr_unittest, fec
from gnuradio import blocks
import dab


class qa_conv_enc (gr_unittest.TestCase):


# test code only for convolutional encoding, not for puncturing


    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        self.dp = dab.parameters.dab_parameters(1, 2e6, False)
        conv_enc_undone = (0x02, 0xBE, 0x3E, 0x8E, 0x16, 0xB9, 0xA5, 0xCD, 0x48, 0xB3, 0x22, 0xB2, 0xAD, 0x76, 0x88, 0x80, 0x42, 0x30, 0x9C, 0xAB, 0x0D, 0xE9, 0xB9, 0x14, 0x2B, 0x4F, 0xD9, 0x25, 0xBF, 0x26, 0xEA, 0xE9)
        #file_src = blocks.file_source_make(gr.sizeof_float, 'fic_decoded_unpacked.dat')
        fib_packed_to_unpacked = blocks.packed_to_unpacked_bb(1, gr.GR_MSB_FIRST)
        fib_unpacked_to_packed = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        src = blocks.vector_source_b(conv_enc_undone)
        #conv_encoder = fec.cc_encoder( ,self.dp.energy_dispersal_fic_vector_length, self.dp.conv_code_constraint_length, self.dp.conv_code_out_bits, self.dp.conv_code_generator_polynomials, self.dp.conv_code_initial_state)
        conv_encoder_config = fec.cc_encoder_make(768, 7, 4, [133, 171, 145, 133], 0)
        conv_encoder = fec.extended_encoder(conv_encoder_config, None, '1010')


        dst = blocks.vector_sink_b()

        self.tb.connect(src, fib_packed_to_unpacked, conv_encoder, fib_unpacked_to_packed, dst)
        self.tb.run ()
        result_data = dst.data()
        print 'src data'
        print conv_enc_undone
        print 'enc data'
        print result_data
        pass


if __name__ == '__main__':
    gr_unittest.run(qa_conv_enc, "qa_conv_enc.xml")
