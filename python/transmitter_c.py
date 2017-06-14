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
import dab


class transmitter_c(gr.hier_block2):
    """
    docstring for block transmitter_c
    """
    def __init__(self, dab_params, sampling_rate, num_subch, ensemble_lable, service_label, service_comp_label, service_language, protection_mode, data_rate_n):
        gr.hier_block2.__init__(self,
            "transmitter_c",
            gr.io_signature(0, 0, gr.sizeof_char),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex)) # Output signature
        self.dp = dab_params
        self.sampling_rate = sampling_rate

        # FIC
        self.fic_source = dab.fib_source_b_make(self.dp.mode, num_subch, ensemble_lable, service_label, service_comp_label, service_language, protection_mode, data_rate_n)
        self.fic_encode = dab.fic_encode(self.dp)

        # MSC
        self.msc_encoder()
        for i in range(0, num_subch):
            self.msc_encoder[i] = dab.msc_encode(self.dp, data_rate_n[i], protection_mode[i])

        # MUX
        self.subch_size = 6*data_rate_n
        self.mux = dab.dab_transmission_frame_mux_bb_make(self.dp.mode, num_subch, self.subch_size)

        # OFDM Modulator
        self.mod = dab.ofdm_mod(self.dp)

        # connect everything
        self.connect(self.fic_source, self.fic_encode, (self.mux, 0))
        for i in range(0, num_subch):
            self.connect((self, i), self.msc_encoder[i], (self.mux, i+1))
        self.connect((self.mux, 0), (self.mod, 0))
        self.connect((self.mux, 1), (self.mod, 1))
        self.connect(self.mod, self)

