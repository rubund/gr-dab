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

from gnuradio import gr, blocks
from gnuradio import fec
import dab

class msc_encode(gr.hier_block2):
    """
    @brief block to encode the logical frames of a sub-channel produced by an MPEG source

    -get packed bytes from source
    -unpack bytes
    -energy dispersal
    -convolutional encoding
    -puncturing
    -time interleaving
    -output packed bytes
    """
    def __init__(self, dab_params, data_rate_n, protection):
        gr.hier_block2.__init__(self,
            "msc_encode",
            gr.io_signature(1, 1, gr.sizeof_char),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_char)) # Output signature
        self.dp = dab_params
        self.n = data_rate_n
        self.msc_I = self.n * 192
        self.protect = protection

        # unpack
        self.unpack = blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST)

        # energy dispersal
        self.prbs_src = blocks.vector_source_b(self.dp.prbs(self.msc_I), True)
        self.add_mod_2 = blocks.xor_bb()

        # convolutional encoder
        self.conv_pack = blocks.unpacked_to_packed_bb_make(1, gr.GR_MSB_FIRST)
        self.conv_encoder = dab.conv_encoder_bb_make(self.msc_I / 8)
        self.conv_unpack = blocks.packed_to_unpacked_bb_make(1, gr.GR_MSB_FIRST)


        # calculate puncturing factors (EEP, table 33, 34)
        if (self.n > 1 or self.protect != 1):
            self.puncturing_L1 = [6 * self.n - 3, 2 * self.n - 3, 6 * self.n - 3, 4 * self.n - 3]
            self.puncturing_L2 = [3, 4 * self.n + 3, 3, 2 * self.n + 3]
            self.puncturing_PI1 = [24, 14, 8, 3]
            self.puncturing_PI2 = [23, 13, 7, 2]
            # calculate length of punctured codeword (11.3.2)
            self.msc_punctured_codeword_length = self.puncturing_L1[self.protect] * 4 * self.dp.puncturing_vectors_ones[
                self.puncturing_PI1[self.protect]] + self.puncturing_L2[self.protect] * 4 * \
                                                     self.dp.puncturing_vectors_ones[
                                                         self.puncturing_PI2[self.protect]] + 12
            self.assembled_msc_puncturing_sequence = self.puncturing_L1[self.protect] * 4 * self.dp.puncturing_vectors[
                self.puncturing_PI1[self.protect]] + self.puncturing_L2[self.protect] * 4 * self.dp.puncturing_vectors[
                self.puncturing_PI2[self.protect]] + self.dp.puncturing_tail_vector
            print "punctured codeword length: " + str(self.msc_punctured_codeword_length)
            print "puncturing_sequence_length: " + str(len(self.assembled_msc_puncturing_sequence))
            self.msc_conv_codeword_length = 4 * self.msc_I + 24  # 4*I + 24 ()
        # exception in table
        else:
            self.msc_punctured_codeword_length = 5 * 4 * self.dp.puncturing_vectors_ones[13] + 1 * 4 * \
                                                                                               self.dp.puncturing_vectors_ones[
                                                                                                   12] + 12
        # sanity check
        assert (6 * self.n == self.puncturing_L1[self.protect] + self.puncturing_L2[self.protect])

        # puncturing
        self.puncture = dab.puncture_bb_make(self.assembled_msc_puncturing_sequence)

        # time interleaving
        self.s2v_time_interleave = blocks.stream_to_vector_make(gr.sizeof_char, self.msc_punctured_codeword_length)
        self.time_interleaver = dab.time_interleave_bb_make(self.msc_punctured_codeword_length, self.dp.scrambling_vector)
        self.v2s_time_interleave = blocks.vector_to_stream_make(gr.sizeof_char, self.msc_punctured_codeword_length)

        # pack bits
        self.unpacked_to_packed_encoded = blocks.unpacked_to_packed_bb_make(1, gr.GR_MSB_FIRST)

        # connect everything
        self.connect(self,
                     self.unpack,
                     self.add_mod_2,
                     self.conv_pack,
                     self.conv_encoder,
                     self.conv_unpack,
                     self.puncture,
                     self.s2v_time_interleave,
                     self.time_interleaver,
                     self.v2s_time_interleave,
                     self.unpacked_to_packed_encoded,
                     self)

