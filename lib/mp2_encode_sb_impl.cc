/* -*- c++ -*- */
/* 
 * Copyright 2017 Moritz Luca Schmid, Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT).
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <stdexcept>
#include <stdio.h>
#include <sstream>
#include <boost/format.hpp>
#include <gnuradio/io_signature.h>
#include "mp2_encode_sb_impl.h"

using namespace boost;

namespace gr {
  namespace dab {

    mp2_encode_sb::sptr
    mp2_encode_sb::make(int bit_rate_n, int channels, int sample_rate)
    {
      return gnuradio::get_initial_sptr
              (new mp2_encode_sb_impl(bit_rate_n, channels, sample_rate));
    }

    /*
     * The private constructor
     */
    mp2_encode_sb_impl::mp2_encode_sb_impl(int bit_rate_n, int channels, int sample_rate)
            : gr::block("mp2_encode_sb",
                        gr::io_signature::make(channels, channels, sizeof(int16_t)),
                        gr::io_signature::make(1, 1, sizeof(unsigned char))),
              d_bit_rate_n(bit_rate_n), d_channels(channels), d_samp_rate(sample_rate)
    {
      if(init_encoder()){
        GR_LOG_DEBUG(d_logger, "libtoolame-dab init succeeded");
      }
      d_input_size = 1152;
      d_output_size = 4092;
      set_output_multiple(d_output_size);
    }

    /*
     * Our virtual destructor.
     */
    mp2_encode_sb_impl::~mp2_encode_sb_impl()
    {
    }

    bool mp2_encode_sb_impl::init_encoder()
    {
      // initialize
      int err = toolame_init();
      // set samplerate
      if (err == 0) {
        err = toolame_set_samplerate(d_samp_rate);
      }
      // set bitrate
      if (err == 0) {
        err = toolame_set_bitrate(d_bit_rate_n * 8);
      }
      // set psychoacoustic model to default (1)
      if (err == 0) {
        err = toolame_set_psy_model(1);
      }
      // set channel mode to default
      char dab_channel_mode;
      if (d_channels == 2) {
        dab_channel_mode = 'j'; // Default to joint-stereo
      } else if (d_channels == 1) {
        dab_channel_mode = 'm'; // Default to mono
      } else {
        GR_LOG_ERROR(d_logger, format("Unsupported channels number %d") % d_channels);
        return false;
      }
      if (err == 0) {
        err = toolame_set_channel_mode(dab_channel_mode);
      }
      // set padlen to 0 (not supported yet)
      if (err == 0) {
        err = toolame_set_pad(0);
      }

      if (err) {
        GR_LOG_ERROR(d_logger, "libtoolame-dab init failed");
        return false;
      }
      else{
        return true;
      }
    }

    void
    mp2_encode_sb_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items; //TODO change rate
    }

    int
    mp2_encode_sb_impl::general_work(int noutput_items,
                                     gr_vector_int &ninput_items,
                                     gr_vector_const_void_star &input_items,
                                     gr_vector_void_star &output_items)
    {
      GR_LOG_DEBUG(d_logger, format("New buffer with %d samples ###########################################################") %noutput_items);
      const int16_t *in_ch1 = (const int16_t *) input_items[0];
      unsigned char *out = (unsigned char *) output_items[0];
      int16_t input_buffers[2][1152];
      d_nconsumed = 0;
      d_nproduced = 0;

      int padlen = 0;
      unsigned char pad_buf[padlen + 1];
      int numOutBytes;

      for (int i = 0; i < noutput_items/d_output_size; ++i) {
        // write next frame to buffer
        if (d_channels == 1){
          memcpy(input_buffers[0], &in_ch1[d_nconsumed], d_input_size * sizeof(int16_t));
        }
        else if(d_channels == 2) { // merge channels if stereo
          const int16_t *in_ch2 = (const int16_t *) input_items[1];
          memcpy(input_buffers[0], &in_ch1[d_nconsumed], d_input_size * sizeof(int16_t));
          memcpy(input_buffers[1], &in_ch2[d_nconsumed], d_input_size * sizeof(int16_t));
        }
        // encode
        numOutBytes = toolame_encode_frame(input_buffers, pad_buf, padlen, &out[d_nproduced], d_output_size);
        GR_LOG_DEBUG(d_logger, format("Encoded frame successfully: %d consumed, %d produced") %d_input_size %numOutBytes);
        d_nconsumed += d_input_size;
        d_nproduced += numOutBytes;
      }
      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each(d_nconsumed);

      // Tell runtime system how many output items we produced.
      return d_nproduced;
    }

  } /* namespace dab */
} /* namespace gr */

