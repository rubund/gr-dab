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

from gnuradio import gr, blocks
import dab

class msc_decode(gr.hier_block2):
    """
    docstring for block msc_decode
    """
    def __init__(self, dab_params, address, size, protection, verbose, debug):
        gr.hier_block2.__init__(self,
            "msc_decode",
            gr.io_signature(2, 2, gr.sizeof_float * dab_params.num_carriers * 2, gr.sizeof_char),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_char * 32)) # Output signature
        self.dp = dab_params
        self.address = address
        self.size = size
        self.protect = protection
        self.verbose = verbose
        self.debug = debug

        # calculate n factor (multiple of 8kbits etc.)
        self.n = self.size/self.dp.subch_size_multiple_n[self.protect]

        # calculate puncturing factors (EEP, table 33, 34)
        if (self.n > 1 or self.protect != 1):
            self.puncturing_L1 = [6*self.n-3, 2*self.n-3, 6*self.n-3, 4*self.n-3]
            self.puncturing_L2 = [3, 4*self.n+3, 3, 2*self.n+3]
            self.puncturing_PI1 = [24, 14, 8, 3]
            self.puncturing_PI2 = [23, 13, 7, 2]
            # calculate length of punctured codeword (11.3.2)
            self.msc_punctured_codeword_length = self.puncturing_L1[self.protect] * 4 * self.dp.puncturing_vectors_ones[self.puncturing_PI1[self.protect]] + self.puncturing_L2[self.protect] * 4 * self.dp.puncturing_vectors_ones[self.puncturing_PI2[self.protect]] + 12
        #exception in table
        else:
            self.msc_punctured_codeword_length = 5 * 4 * self.dp.puncturing_vectors_ones[13] + 1 * 4 * self.dp.puncturing_vectors_ones[12] + 12



        # MSC selection and block partitioning
        # select OFDM carriers with MSC
        self.select_msc_syms = dab.select_vectors(gr.sizeof_float, self.dp.num_carriers * 2, self.dp.num_msc_syms, self.dp.num_fic_syms)
        # repartition MSC data in CIFs
        self.repartition_msc_to_CIFs = dab.repartition_vectors_make(gr.sizeof_float, self.dp.num_carriers * 2, self.dp.cif_bits, self.dp.num_msc_syms, self.dp.num_cifs)
        # select CUs of one subchannel of each CIF
        self.select_subch = dab.select_vectors_make(gr.sizeof_float, self.dp.cif_bits, self.size, self.address)
        self.nullsink = blocks.null_sink(gr.sizeof_char)


        # Define blocks and connect them
        self.connect((self, 0), (self.select_msc_syms, 0), (self.repartition_msc_to_CIFs, 0), (self.select_subch, 0), (self, 1))
        self.connect((self, 1), (self.select_msc_syms, 1), (self.repartition_msc_to_CIFs, 1), (self.select_subch, 1), self.nullsink)
