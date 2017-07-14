/* -*- c++ -*- */
/* 
 * Copyright 2017 <+YOU OR YOUR COMPANY+>.
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

#include <gnuradio/io_signature.h>
#include "mp4_encode_sb_impl.h"
#include <stdexcept>
#include <stdio.h>
#include <sstream>
#include <boost/format.hpp>
#include "aacenc_lib.h"

using namespace boost;

namespace gr {
  namespace dab {

    mp4_encode_sb::sptr
    mp4_encode_sb::make(int bit_rate_n, int channels, int samp_rate, int afterburner)
    {
      return gnuradio::get_initial_sptr
              (new mp4_encode_sb_impl(bit_rate_n, channels, samp_rate, afterburner));
    }

    /*
     * The private constructor
     */
    mp4_encode_sb_impl::mp4_encode_sb_impl(int bit_rate_n, int channels, int samp_rate, int afterburner)
            : gr::block("mp4_encode_sb",
                        gr::io_signature::make(1, 1, sizeof(int16_t)),
                        gr::io_signature::make(1, 1, sizeof(unsigned char))),
              d_bit_rate_n(bit_rate_n), d_channels(channels), d_samp_rate(samp_rate), d_afterburner(afterburner)
    {
      // check input arguments
      if(d_bit_rate_n < 1 || bit_rate_n > 24){
        throw std::out_of_range("bit_rate_n out of range (%d)" + d_bit_rate_n);
      }
      if(!(d_samp_rate == 32000 || d_samp_rate == 48000)){
        throw std::invalid_argument("samp_rate must be 32kHz or 48kHz, not %d" + d_samp_rate);
      }
      // prepare AAC encoder
      *d_aot = AOT_NONE;
      if(init_aac_encoder(d_aac_encoder, d_bit_rate_n, d_channels, d_samp_rate, d_afterburner, &d_aot)){
        GR_LOG_INFO(d_logger, "AAC encoder init succeeded");
      }
      else{
        GR_LOG_ERROR(d_logger, "AAC encoder init failed");

      }
    }

    /*
     * Our virtual destructor.
     */
    mp4_encode_sb_impl::~mp4_encode_sb_impl()
    {
    }

    bool mp4_encode_sb_impl::init_aac_encoder(
            HANDLE_AACENCODER *encoder,
            int subchannel_index,
            int channels,
            int sample_rate,
            int afterburner,
            int *aot)
    {
      // set number of channels
      CHANNEL_MODE mode;
      switch (channels) {
        case 1: mode = MODE_1; break;
        case 2: mode = MODE_2; break;
        default:
          GR_LOG_ERROR(d_logger, format("Unsupported channels number %d") %channels);
          return false;
      }

      // allocate encoder instance with required \ref encOpen "configuration"
      if (aacEncOpen(encoder, 0x01|0x02|0x04, channels) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unable to open encoder");
        return false;
      }

      // set AOT \TODO: is PseudoStereo supported???
      if (*aot == AOT_NONE) {
        if(channels == 2 && subchannel_index <= 6) {
          *aot = AOT_DABPLUS_PS;
        }
        else if((channels == 1 && subchannel_index <= 8) || subchannel_index <= 10) {
          *aot = AOT_DABPLUS_SBR;
        }
        else {
          *aot = AOT_DABPLUS_AAC_LC;
        }
      }

      GR_LOG_INFO(d_logger, format("Using %d subchannels. AAC type:%s%s%s. channels=%d, sample_rate=%d")
              %subchannel_index
              %*aot == AOT_DABPLUS_PS ? "HE-AAC v2" : ""
              %*aot == AOT_DABPLUS_SBR ? "HE-AAC" : ""
              %*aot == AOT_DABPLUS_AAC_LC ? "AAC-LC" : ""
              %channels
              %sample_rate);

      // set AAC parameters
      if (aacEncoder_SetParam(*encoder, AACENC_AOT, *aot) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unalbe to set the AOT");
        return false;
      }
      if (aacEncoder_SetParam(*encoder, AACENC_SAMPLERATE, sample_rate) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unalbe to set the sample rate");
        return false;
      }
      if (aacEncoder_SetParam(*encoder, AACENC_CHANNELMODE, mode) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unalbe to set the channel mode");
        return false;
      }
      if (aacEncoder_SetParam(*encoder, AACENC_CHANNELORDER, 1) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unalbe to set the wav channel order");
        return false;
      }
      if (aacEncoder_SetParam(*encoder, AACENC_GRANULE_LENGTH, 960) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unalbe to set the granule length");
        return false;
      }
      if (aacEncoder_SetParam(*encoder, AACENC_TRANSMUX, TT_DABPLUS) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unalbe to set the RAW transmux");
        return false;
      }

      /*if (aacEncoder_SetParam(*encoder, AACENC_BITRATEMODE, AACENC_BR_MODE_SFR)
       * != AACENC_OK) {
          fprintf(stderr, "Unable to set the bitrate mode\n");
          return 1;
      }*/

      GR_LOG_ERROR(d_logger, format("AAC bitrate set to: %d") %subchannel_index*8000);
      if (aacEncoder_SetParam(*encoder, AACENC_BITRATE, subchannel_index*8000) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unalbe to set the bitrate");
        return false;
      }
      if (aacEncoder_SetParam(*encoder, AACENC_AFTERBURNER, afterburner) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unalbe to set the afterburner mode");
        return false;
      }
      if (!afterburner) {
        GR_LOG_WARN(d_logger, "Afterburned disabled");
      }
      if (aacEncEncode(*encoder, NULL, NULL, NULL, NULL) != AACENC_OK) {
        GR_LOG_ERROR(d_logger, "Unalbe to initialize the encoder");
        return false;
      }
      return 0;
    }

    void
    mp4_encode_sb_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;
    }

    int
    mp4_encode_sb_impl::general_work(int noutput_items,
                                     gr_vector_int &ninput_items,
                                     gr_vector_const_void_star &input_items,
                                     gr_vector_void_star &output_items)
    {
      const int16_t *in = (const int16_t *) input_items[0];
      unsigned char *out = (unsigned char*) output_items[0];

      for (int i = 0; i < noutput_items; ++i) {
        out[i] = 3;
      }
      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each(noutput_items);

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace dab */
} /* namespace gr */

