#!/usr/bin/env python2
# -*- coding: utf8 -*-

# Andreas Müller, 2008
# andrmuel@ee.ethz.ch
#
# this code may be freely used under GNU GPL conditions

"""
demodulate DAB signal and ouput to constellation sink
"""

from gnuradio import gr, uhd, blocks
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import stdgui2, fftsink2, scopesink2
import dab
from optparse import OptionParser
import wx
import sys, threading, time

class usrp_dab_gui_rx(stdgui2.std_top_block):
	def __init__(self, frame, panel, vbox, argv):
		stdgui2.std_top_block.__init__(self, frame, panel, vbox, argv)

		self.frame = frame
		self.panel = panel

		parser = OptionParser(option_class=eng_option, usage="%prog: [options] <filename>")
  		parser.add_option("-m", "--dab-mode", type="int", default=1,
        	     	help="DAB mode [default=%default]")
		parser.add_option("-F", "--filter-input", action="store_true", default=False,
                          help="Enable FFT filter at input")
		parser.add_option('-c', '--correct-ffe', action="store_true", default=False,
		     help="do fine frequency correction")
		parser.add_option('-u', '--correct-ffe-usrp', action="store_true", default=False,
		     help="do fine frequency correction by retuning the USRP instead of in software")
		parser.add_option('-e', '--equalize-magnitude', action="store_true", default=False,
		     help="do magnitude equalization")
  		parser.add_option("-s", "--resample-fixed", type="eng_float", default=1,
			help="resample by a fixed factor (fractional interpolation)")
		parser.add_option("-S", "--autocorrect-sample-rate", action="store_true", default=False,
                          help="Estimate sample rate offset and resample (dynamic fractional interpolation)")
		parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=(0, 0),
		     help="select USRP Rx side A or B [default=A]")
		parser.add_option("-f", "--freq", type="eng_float", default=227.36e6,
		     help="set frequency to FREQ [default=%default]")
		parser.add_option("-r", "--sample-rate", type="int", default=2000000,
		     help="set sample rate to SAMPLE_RATE [default=%default]")
		parser.add_option("-d", "--decim", type="intx", default=32,
		     help="set decimation rate to DECIM [default=%default]")
		parser.add_option("-g", "--rx-gain", type="eng_float", default=None,
		     help="set receive gain in dB (default is midpoint)")
		parser.add_option('-v', '--verbose', action="store_true", default=False,
		     help="verbose output")
		parser.add_option('-a', '--antenna', type="string", default="TX/RX",
		     help="select antenna")
		(options, args) = parser.parse_args()

		
		self.verbose = options.verbose

		if len(args) == 0:
			if self.verbose:
				print "--> receiving from USRP"
			self.src = uhd.usrp_source("",uhd.io_type.COMPLEX_FLOAT32,1)
			#self.src.set_mux(usrp.determine_rx_mux_value(self.src, options.rx_subdev_spec))
			#self.subdev = usrp.selected_subdev(self.src, options.rx_subdev_spec)
			#if self.verbose:
			#	print "--> using RX dboard " + self.subdev.side_and_name()
			# tune frequency
			self.frequency = options.freq
			self.set_freq(options.freq)

			# set gain      
			if options.rx_gain is None:
				# if no gain was specified, use the mid-point in dB
				g = self.src.get_gain_range()
				options.rx_gain = float(g.start()+g.stop())/2
			self.src.set_gain(options.rx_gain)
			self.sample_rate = 2e6#self.src.adc_rate()/options.decim
			self.src.set_samp_rate(self.sample_rate)
			self.src.set_antenna(options.antenna)
		else:
			if self.verbose:
				print "--> receiving from file: " + args[0]
			self.filename = args[0]
			self.src = gr.file_source(gr.sizeof_gr_complex, self.filename, False)
			self.sample_rate = options.sample_rate
		
		
		self.dab_params = dab.parameters.dab_parameters(mode=options.dab_mode, sample_rate=self.sample_rate, verbose=options.verbose)
		self.rx_params = dab.parameters.receiver_parameters(mode=options.dab_mode, softbits=True, input_fft_filter=options.filter_input, autocorrect_sample_rate=options.autocorrect_sample_rate, sample_rate_correction_factor=options.resample_fixed, verbose=options.verbose, correct_ffe=options.correct_ffe, equalize_magnitude=options.equalize_magnitude)
	
		
		self.demod = dab.ofdm_demod(self.dab_params, self.rx_params, verbose=self.verbose) 

		self.v2s = blocks.vector_to_stream(gr.sizeof_gr_complex, self.dab_params.num_carriers)
		self.scope = scopesink2.scope_sink_c(self.panel, title="DAB constellation sink", sample_rate=self.dab_params.sample_rate, xy_mode=True)

		self.trigsink = blocks.null_sink(gr.sizeof_char)
		self.sink = blocks.null_sink(gr.sizeof_float*self.dab_params.num_carriers*2)

		self.connect(self.src, self.demod, self.sink)
		self.connect((self.demod,1), self.trigsink)
        
		# build GUI
		self.connect(self.demod.deinterleave, self.v2s, self.scope)
		vbox.Add(self.scope.win, 10, wx.EXPAND)
		
		# retune USRP to correct FFE?
		self.correct_ffe_usrp = options.correct_ffe_usrp
		if self.correct_ffe_usrp:
			print "--> correcting FFE on USRP"
			self.run_correct_ffe_thread = True
			self.ffe_updater = threading.Timer(0.1, self.correct_ffe)
			self.ffe_updater.setDaemon(True)
			self.ffe_updater.start()

	def correct_ffe(self):
		while self.run_correct_ffe_thread:
			diff = self.demod.sync.ffs_sample_and_average_arg.ffe_estimate()
			if abs(diff) > self.rx_params.usrp_ffc_min_deviation:
				self.frequency -= diff*self.rx_params.usrp_ffc_adapt_factor
				print "--> updating fine frequency correction: " + str(self.frequency)
				self.set_freq(self.frequency)
			time.sleep(1./self.rx_params.usrp_ffc_retune_frequency)


	def set_freq(self, freq):
		if self.src.set_center_freq(freq): #src.tune(0, self.subdev, freq):
			if self.verbose:
				print "--> retuned to " + str(freq) + " Hz"
			return True
		else:
			print "-> error - cannot tune to " + str(freq) + " Hz"
			return False

if __name__ == '__main__':
	app = stdgui2.stdapp(usrp_dab_gui_rx, "usrp_dab_gui_rx", nstatus=1)
	app.MainLoop()



