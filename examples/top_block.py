#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Wed May 17 14:26:41 2017
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import dab
import time
import wx


class top_block(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2000000

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_clock_rate(32000000, uhd.ALL_MBOARDS)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(227.36e6, 0)
        self.uhd_usrp_source_0.set_gain(36, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.dab_ofdm_demod_0 = dab.ofdm_demod(
                  dab.parameters.dab_parameters(
                    mode=1,
                    sample_rate=samp_rate,
                    verbose=False
                  ),
                  dab.parameters.receiver_parameters(
                    mode=1,
                    softbits=True,
                    input_fft_filter=True,
                    autocorrect_sample_rate=True,
                    sample_rate_correction_factor=1,
                    verbose=False,
                    correct_ffe=True,
                    equalize_magnitude=True
                  )
                )
          
        self.dab_fic_decode_0 = dab.fic_decode(
                  dab.parameters.dab_parameters(
                    mode=1,
                    sample_rate=samp_rate,
                    verbose=False
                  )
                )
          
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_char*32)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.dab_fic_decode_0, 0), (self.blocks_null_sink_0, 0))    
        self.connect((self.dab_ofdm_demod_0, 0), (self.dab_fic_decode_0, 0))    
        self.connect((self.dab_ofdm_demod_0, 1), (self.dab_fic_decode_0, 1))    
        self.connect((self.uhd_usrp_source_0, 0), (self.dab_ofdm_demod_0, 0))    

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)


def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()
    tb.Start(True)
    tb.Wait()


if __name__ == '__main__':
    main()
