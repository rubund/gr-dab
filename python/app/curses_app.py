#!/usr/bin/env python3

import sys,os
import curses
import threading
import time
#import queue
import yaml
from gnuradio import gr, blocks, audio
import grdab


channel_list_filename = "".join([os.getenv("HOME"),"/.grdab/channels.yaml"])

channel_list = []
if os.path.isfile(channel_list_filename):
    with open(channel_list_filename, "r") as fp:
        channel_list = yaml.load(fp)

samp_rate = samp_rate = 2000000

def draw_menu(stdscr):
    global src
    global dab_dabplus_audio_decoder_ff_0
    global dab_ofdm_demod_0
    global c2f
    global f2c
    global audio_sink_0
    global xrun_monitor
    global fg
    global use_zeromq
    global rpc_mgr_server
    global dab_ofdm_demod_0
    global ppm_shared

    k = 0
    cursor_x = 0
    cursor_y = 0


    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(0)

    kThread = KeyDetecThread(stdscr)

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    selected = 0
    active = 0
    nelem = len(channel_list)
    # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - 1
        elif k == curses.KEY_RIGHT:
            cursor_x = cursor_x + 1
        elif k == curses.KEY_LEFT:
            cursor_x = cursor_x - 1

        previous_active = active

        if k == 259: # key up
            if selected > 0:
                selected -= 1
        elif k == 258: # key down
            if selected < (nelem-1):
                selected += 1
        elif k == 10: # enter
            active = selected

        if k == 10:
            ch = channel_list[active]
            freq = float(ch['frequency'])*1e6
            if use_zeromq:
                rpc_mgr_server.request("set_frequency",[freq])
            else:
                src.set_center_freq(freq, 0)
            new = grdab.dabplus_audio_decoder_ff(grdab.parameters.dab_parameters(mode=1, sample_rate=samp_rate, verbose=False), ch['bit_rate'], ch['address'], ch['subch_size'], ch['protect_level'], True)
            newaudio = audio.sink(48000, '', True)
            sample_rate_correction_factor = 1 + float(ppm_shared)*1e-6
            new_ofdm = grdab.ofdm_demod(
                      grdab.parameters.dab_parameters(
                        mode=1,
                        sample_rate=samp_rate,
                        verbose=False
                      ),
                      grdab.parameters.receiver_parameters(
                        mode=1,
                        softbits=True,
                        input_fft_filter=True,
                        autocorrect_sample_rate=False,
                        sample_rate_correction_factor=sample_rate_correction_factor,
                        always_include_resample=True,
                        verbose=False,
                        correct_ffe=True,
                        equalize_magnitude=True
                      )
                    )
            fg.stop()
            fg.wait()
            xrun_monitor.stop_until_tag()
            fg.disconnect(src, dab_ofdm_demod_0, dab_dabplus_audio_decoder_ff_0)
            fg.disconnect((dab_dabplus_audio_decoder_ff_0, 0), (f2c, 0))
            fg.disconnect((dab_dabplus_audio_decoder_ff_0, 1), (f2c, 1))
            fg.disconnect((c2f, 0), (audio_sink_0, 0))
            fg.disconnect((c2f, 1), (audio_sink_0, 1))
            del dab_dabplus_audio_decoder_ff_0
            del audio_sink_0
            del dab_ofdm_demod_0
            dab_dabplus_audio_decoder_ff_0 = new
            audio_sink_0 = newaudio
            dab_ofdm_demod_0 = new_ofdm
            fg.connect(src, dab_ofdm_demod_0, dab_dabplus_audio_decoder_ff_0)
            fg.connect((dab_dabplus_audio_decoder_ff_0, 0), (f2c, 0))
            fg.connect((dab_dabplus_audio_decoder_ff_0, 1), (f2c, 1))
            fg.connect((c2f, 0), (audio_sink_0, 0))
            fg.connect((c2f, 1), (audio_sink_0, 1))
            time.sleep(1)
            fg.start()

        cursor_x = max(0, cursor_x)
        cursor_x = min(width-1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height-1, cursor_y)

        # Declaration of strings
        title = "Curses example"[:width-1]
        subtitle = "Written by Clay McLeod"[:width-1]
        if k != -1:
          keystr = "Last key pressed: {}".format(k)[:width-1]
        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y)
        if k == 0:
            keystr = "No key press detected..."[:width-1]
        k = 0

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((height // 2) - 2)

        # Rendering some text
        whstr = "Width: {}, Height: {}".format(width, height)
        for i in range(0, len(channel_list)):
            if i == selected:
                stdscr.addstr(i, 0, str(channel_list[i]['name']), curses.color_pair(3))
            elif i == active:
                stdscr.addstr(i, 0, str(channel_list[i]['name']), curses.color_pair(2))
            else:
                stdscr.addstr(i, 0, str(channel_list[i]['name']), curses.color_pair(1))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        stdscr.addstr(start_y + 5, start_x_keystr, keystr)
        stdscr.move(cursor_y, cursor_x)

        # Refresh the screen
        stdscr.refresh()

        
        stdscr.timeout(0)
        kn = stdscr.getch()
        k = kn
        stdscr.timeout(-1)
        # Wait for next input
        #queue.
        if k == -1:
            time.sleep(0.1)

class KeyDetecThread(threading.Thread):

    def __init__(self, stdscr):
        threading.Thread.__init__(self)
        self.running = 1
        self.stdscr = stdscr

    def run(self):
        while self.running:
            k = self.stdscr.getch()

def main(rf_gain, if_gain, bb_gain, ppm, use_zeromq_in=False):
    global src
    global dab_dabplus_audio_decoder_ff_0
    global dab_ofdm_demod_0
    global c2f
    global f2c
    global audio_sink_0
    global fg
    global xrun_monitor
    global use_zeromq
    global rpc_mgr_server
    global dab_ofdm_demod_0
    global ppm_shared
    frequency=220.352e6
    rf_gain=25
    if_gain=0
    bb_gain=0
    audio_sample_rate=48000
    ppm_shared = ppm
    dab_bit_rate=64
    dab_address=304
    dab_subch_size=64
    dab_protect_level=1
    use_zeromq=use_zeromq_in
    if use_zeromq:
        from gnuradio import zeromq
    else:
        import osmosdr
    import time

    if len(channel_list) > 0:
        ch = channel_list[0]
        frequency = float(ch['frequency'])*1e6
    else:
        ch = {"bit_rate" : 64, "address" : 304, "subch_size" : 64, "protect_level" : 1}

    print("Setting frequency: %0.3f MHz" % (frequency/1e6))

    if not use_zeromq:
        osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + '' )
        osmosdr_source_0.set_sample_rate(samp_rate)
        osmosdr_source_0.set_center_freq(frequency, 0)
        osmosdr_source_0.set_freq_corr(0, 0)
        osmosdr_source_0.set_dc_offset_mode(0, 0)
        osmosdr_source_0.set_iq_balance_mode(0, 0)
        osmosdr_source_0.set_gain_mode(False, 0)
        osmosdr_source_0.set_gain(rf_gain, 0)
        osmosdr_source_0.set_if_gain(if_gain, 0)
        osmosdr_source_0.set_bb_gain(bb_gain, 0)
        osmosdr_source_0.set_antenna('', 0)
        osmosdr_source_0.set_bandwidth(2000000, 0)
    else:
        zeromq_source = zeromq.sub_source(gr.sizeof_gr_complex, 1, "tcp://127.0.0.1:10444", 100, False, -1)
        rpc_mgr_server = zeromq.rpc_manager()
        rpc_mgr_server.set_request_socket("tcp://127.0.0.1:10445")
        rpc_mgr_server.request("set_sample_rate",[samp_rate])
        rpc_mgr_server.request("set_rf_gain",[rf_gain])
        rpc_mgr_server.request("set_if_gain",[if_gain])
        rpc_mgr_server.request("set_bb_gain",[bb_gain])
        rpc_mgr_server.request("set_ppm",[0]) # Not using hardware correction since it behaves differently on different hardware
        rpc_mgr_server.request("set_frequency",[frequency])
        time.sleep(0.7)

    sample_rate_correction_factor = 1 + float(ppm_shared)*1e-6
    dab_ofdm_demod_0 = grdab.ofdm_demod(
              grdab.parameters.dab_parameters(
                mode=1,
                sample_rate=samp_rate,
                verbose=False
              ),
              grdab.parameters.receiver_parameters(
                mode=1,
                softbits=True,
                input_fft_filter=True,
                autocorrect_sample_rate=False,
                sample_rate_correction_factor=sample_rate_correction_factor,
                always_include_resample=True,
                verbose=False,
                correct_ffe=True,
                equalize_magnitude=True
              )
            )

    dab_dabplus_audio_decoder_ff_0 = grdab.dabplus_audio_decoder_ff(grdab.parameters.dab_parameters(mode=1, sample_rate=samp_rate, verbose=False), ch['bit_rate'], ch['address'], ch['subch_size'], ch['protect_level'], True)

    xrun_monitor = grdab.xrun_monitor_cc(100000)
    xrun_monitor.set_report_fill(False)
    f2c = blocks.float_to_complex()
    c2f = blocks.complex_to_float()

    audio_sink_0 = audio.sink(audio_sample_rate, '', True)


    fg = gr.top_block()

    if not use_zeromq:
        src = osmosdr_source_0
    else:
        src = zeromq_source

    fg.connect(src, dab_ofdm_demod_0, dab_dabplus_audio_decoder_ff_0)
    fg.connect((dab_dabplus_audio_decoder_ff_0, 0), (f2c, 0))
    fg.connect((dab_dabplus_audio_decoder_ff_0, 1), (f2c, 1))
    fg.connect(f2c, xrun_monitor)
    fg.connect(xrun_monitor, c2f)
    fg.connect((c2f, 0), (audio_sink_0, 0))
    fg.connect((c2f, 1), (audio_sink_0, 1))




    fg.start()
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
