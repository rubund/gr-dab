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

"""
receive DAB with USRP
"""

from gnuradio import gr, uhd, blocks
from gnuradio import audio
import dab
import sys, time, threading, math


class usrp_dab_tx(gr.top_block):
    def __init__(self, num_subch, ensemble_label, service_label, language, protection, data_rate_n):
        gr.top_block.__init__(self)

        # set logger level to WARN (no DEBUG logs)
        log = gr.logger("log")
        log.set_level("WARN")

        self.dab_mode = 1
        interp = 64
        self.sample_rate = 128e6 / interp
        self.dab_params = dab.parameters.dab_parameters(self.dab_mode, 2000000, False)

        self.num_subch = num_subch
        self.ensemble_label = ensemble_label
        self.service_label = service_label
        self.language = language
        self.protection = protection
        self.data_rate_n = data_rate_n

        self.fib_src = dab.fib_source_b_make(self.dab_mode, self.num_subch, self.ensemble_label, self.service_label, "", self.language, self.protection, self.data_rate_n)

    def transmit(self):
        rx = usrp_dab_tx()
        rx.run()

