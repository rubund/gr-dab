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

#include <gnuradio/io_signature.h>
#include "mp4_decode_bs_impl.h"
#include <stdexcept>
#include <stdio.h>
#include <sstream>
#include <boost/format.hpp>
#include "neaacdec.h"

using namespace boost;

namespace gr {
  namespace dab {

    mp4_decode_bs::sptr
    mp4_decode_bs::make(int bit_rate_n)
    {
      return gnuradio::get_initial_sptr
              (new mp4_decode_bs_impl(bit_rate_n));
    }

    /*
     * The private constructor
     */
    mp4_decode_bs_impl::mp4_decode_bs_impl(int bit_rate_n)
            : gr::block("mp4_decode_bs",
                        gr::io_signature::make(1, 1, sizeof(unsigned char)),
                        gr::io_signature::make(1, 1, sizeof(int))),
              d_bit_rate_n(bit_rate_n)
    {
      d_superframe_size = bit_rate_n * 110;
      aacInitialized = false;
      baudRate = 48000;
      set_output_multiple(5760); //TODO: right? baudRate*0.12 for output of one superframe
      aacHandle = NeAACDecOpen();
      memset(d_aac_frame, 0, 960);
    }

    /*
     * Our virtual destructor.
     */
    mp4_decode_bs_impl::~mp4_decode_bs_impl()
    {
    }

    void
    mp4_decode_bs_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items; //TODO: how to calculate actual rate?
    }

    // returns aac channel configuration
    int mp4_decode_bs_impl::get_aac_channel_configuration(int16_t m_mpeg_surround_config, uint8_t aacChannelMode)
    {
      switch (m_mpeg_surround_config) {
        case 0:     // no surround
          return aacChannelMode ? 2 : 1;
        case 1:     // 5.1
          return 6;
        case 2:     // 7.1
          return 7;
        default:
          return -1;
      }
    }

    bool mp4_decode_bs_impl::initialize(uint8_t dacRate,
                                        uint8_t sbrFlag,
                                        int16_t mpegSurround,
                                        uint8_t aacChannelMode)
    {
      long unsigned int sample_rate;
      uint8_t channels;
/* AudioSpecificConfig structure (the only way to select 960 transform here!)
 *
 *  00010 = AudioObjectType 2 (AAC LC)
 *  xxxx  = (core) sample rate index
 *  xxxx  = (core) channel config
 *  100   = GASpecificConfig with 960 transform
 *
 * SBR: implicit signaling sufficient - libfaad2
 * automatically assumes SBR on sample rates <= 24 kHz
 * => explicit signaling works, too, but is not necessary here
 *
 * PS:  implicit signaling sufficient - libfaad2
 * therefore always uses stereo output (if PS support was enabled)
 * => explicit signaling not possible, as libfaad2 does not
 * support AudioObjectType 29 (PS)
 */

      int core_sr_index =
              dacRate ? (sbrFlag ? 6 : 3) :
              (sbrFlag ? 8 : 5);   // 24/48/16/32 kHz
      int core_ch_config = get_aac_channel_configuration(mpegSurround,
                                                         aacChannelMode);
      if (core_ch_config == -1) {
        GR_LOG_ERROR(d_logger, "Unrecognized mpeg surround config (ignored)");
        return false;
      }
      uint8_t asc[2];
      asc[0] = 0b00010 << 3 | core_sr_index >> 1;
      asc[1] = (core_sr_index & 0x01) << 7 | core_ch_config << 3 | 0b100;
      long int init_result = NeAACDecInit2(aacHandle,
                                           asc,
                                           sizeof(asc),
                                           &sample_rate,
                                           &channels);
      if (init_result != 0) {
/*      If some error initializing occured, skip the file */
        GR_LOG_ERROR(d_logger, "Error initializing decoding library");
        NeAACDecClose(aacHandle);
        return false;
      }
      return true;
    }

    void mp4_decode_bs_impl::handle_aac_frame(uint8_t *v,
                                              int16_t frame_length,
                                              uint8_t dacRate,
                                              uint8_t sbrFlag,
                                              uint8_t mpegSurround,
                                              uint8_t aacChannelMode,
                                              int *out_sample)
    {
      uint8_t theAudioUnit[2 * 960 + 10];  // sure, large enough

      memcpy(theAudioUnit, v, frame_length);
      memset(&theAudioUnit[frame_length], 0, 10);

      if (((theAudioUnit[0] >> 5) & 07) == 4) {
        int16_t count = theAudioUnit[1];
        uint8_t buffer[count];
        memcpy(buffer, &theAudioUnit[2], count);
        uint8_t L0 = buffer[count - 1];
        uint8_t L1 = buffer[count - 2];
        //my_padhandler. processPAD (buffer, count - 3, L1, L0);
      }

      int tmp = MP42PCM(dacRate,
                        sbrFlag,
                        mpegSurround,
                        aacChannelMode,
                        theAudioUnit,
                        frame_length,
                        out_sample);
      //*error	= tmp == 0;
      GR_LOG_DEBUG(d_logger, format("produced %d samples") % tmp);
    }

    int16_t mp4_decode_bs_impl::MP42PCM(uint8_t dacRate,
                                        uint8_t sbrFlag,
                                        int16_t mpegSurround,
                                        uint8_t aacChannelMode,
                                        uint8_t buffer[],
                                        int16_t bufferLength,
                                        int *out_sample)
    {
      int16_t samples;
      long unsigned int sampleRate;
      int16_t *outBuffer;
      NeAACDecFrameInfo hInfo;
      uint8_t dummy[10000];
      uint8_t channels;

      if (!aacInitialized) {
        if (!initialize(dacRate, sbrFlag, mpegSurround, aacChannelMode))
          return 0;
        aacInitialized = true;
      }

      outBuffer = (int16_t *) NeAACDecDecode(aacHandle,
                                             &hInfo, buffer, bufferLength);
      sampleRate = hInfo.samplerate;

      sampleRate = hInfo.samplerate; //TODO remove one?
      samples = hInfo.samples;
      if ((sampleRate == 24000) ||
          (sampleRate == 32000) ||
          (sampleRate == 48000) ||
          (sampleRate != (long unsigned) baudRate))
      {
        baudRate = sampleRate;
      }

//      fprintf (stderr, "bytes consumed %d\n", (int)(hInfo. bytesconsumed));
//      fprintf (stderr, "samplerate = %d, samples = %d, channels = %d, error = %d, sbr = %d\n", sampleRate, samples,
//               hInfo. channels,
//               hInfo. error,
//               hInfo. sbr);
//      fprintf (stderr, "header = %d\n", hInfo. header_type);
      channels = hInfo.channels;
      if (hInfo.error != 0) {
        fprintf(stderr, "Warning: %s\n",
                faacDecGetErrorMessage(hInfo.error));
        return 0;
      }

      // write samples to output buffer
      if (channels == 2) {
        //audioBuffer  -> putDataIntoBuffer (outBuffer, samples);
        for (int n = 0; n < samples; n++) {
          out_sample[n] = (int) outBuffer[n];
        }
        /*if (audioBuffer -> GetRingBufferReadAvailable () > sampleRate / 8)
          newAudio (sampleRate);*/
      } else if (channels == 1) {
        int16_t *buffer = (int16_t *) alloca(2 * samples);
        int16_t i;
        for (i = 0; i < samples; i++) {
          buffer[2 * i] = ((int16_t *) outBuffer)[i];
          buffer[2 * i + 1] = buffer[2 * i];
        }
        //audioBuffer  -> putDataIntoBuffer (buffer, samples);
        for (int n = 0; n < samples; n++) {
          out_sample[n] = (int) buffer[n];
        }
        /*if (audioBuffer -> GetRingBufferReadAvailable () > sampleRate / 8)
          newAudio (sampleRate);*/
      } else
        GR_LOG_ERROR(d_logger, "Cannot handle these channels");

      d_nsamples_produced += samples;
      return samples / 2; //TODO: for channels == 1 return samples or for loop to samples/2
    }

    int
    mp4_decode_bs_impl::general_work(int noutput_items,
                                     gr_vector_int &ninput_items,
                                     gr_vector_const_void_star &input_items,
                                     gr_vector_void_star &output_items)
    {
      const unsigned char *in = (const unsigned char *) input_items[0];
      int *out = (int *) output_items[0];
      d_nsamples_produced = 0;

      for (int n = 0; n < noutput_items / 5760; n++) {
        //process superframe header
        //	bits 0 .. 15 is firecode
        //	bit 16 is unused
        d_dac_rate = (in[n * d_superframe_size + 2] >> 6) & 01;  // bit 17
        d_sbr_flag = (in[n * d_superframe_size + 2] >> 5) & 01;  // bit 18
        d_aac_channel_mode = (in[n * d_superframe_size + 2] >> 4) & 01;  // bit 19
        d_ps_flag = (in[n * d_superframe_size + 2] >> 3) & 01;  // bit 20
        d_mpeg_surround = (in[n * d_superframe_size + 2] & 07);    // bits 21 .. 23
        GR_LOG_DEBUG(d_logger,
                     format("superframe header: dac_rate %d, sbr_flag %d, aac_mode %d, ps_flag %d, surround %d") %
                     d_dac_rate % d_sbr_flag % d_aac_channel_mode % d_ps_flag % d_mpeg_surround);

        switch (2 * d_dac_rate + d_sbr_flag) {
          default:    // cannot happen
          case 0:
            d_num_aus = 4;
            d_au_start[0] = 8;
            d_au_start[1] = in[n * d_superframe_size + 3] * 16 + (in[4] >> 4);
            d_au_start[2] = (in[n * d_superframe_size + 4] & 0xf) * 256 + in[5];
            d_au_start[3] = in[n * d_superframe_size + 6] * 16 + (in[7] >> 4);
            d_au_start[4] = d_superframe_size;
            break;
//
          case 1:
            d_num_aus = 2;
            d_au_start[n * d_superframe_size + 0] = 5;
            d_au_start[1] = in[n * d_superframe_size + 3] * 16 + (in[4] >> 4);
            d_au_start[2] = d_superframe_size;
            break;
//
          case 2:
            d_num_aus = 6;
            d_au_start[0] = 11;
            d_au_start[1] = in[n * d_superframe_size + 3] * 16 + (in[4] >> 4);
            d_au_start[2] = (in[n * d_superframe_size + 4] & 0xf) * 256 + in[5];
            d_au_start[3] = in[n * d_superframe_size + 6] * 16 + (in[7] >> 4);
            d_au_start[4] = (in[n * d_superframe_size + 7] & 0xf) * 256 + in[8];
            d_au_start[5] = in[n * d_superframe_size + 9] * 16 + (in[10] >> 4);
            d_au_start[6] = d_superframe_size;
            break;
//
          case 3:
            d_num_aus = 3;
            d_au_start[0] = 6;
            d_au_start[1] = in[n * d_superframe_size + 3] * 16 + (in[4] >> 4);
            d_au_start[2] = (in[n * d_superframe_size + 4] & 0xf) * 256 + in[5];
            d_au_start[3] = d_superframe_size;
            break;
        }


/**
  *	OK, the result is N * 110 * 8 bits (still single bit per byte!!!)
  *	extract the AU's, and prepare a buffer,  with the sufficient
  *	lengthy for conversion to PCM samples
  */
        for (int i = 0; i < d_num_aus; i++) {
          int16_t aac_frame_length;

          // sanity check 1
          if (d_au_start[i + 1] < d_au_start[i]) {
            GR_LOG_ERROR(d_logger, "au start address wrong");
            // should not happen, all errors were corrected
          }

          aac_frame_length = d_au_start[i + 1] - d_au_start[i] - 2;
          // just a sanity check
          if ((aac_frame_length >= 960) || (aac_frame_length < 0)) {
            GR_LOG_WARN(d_logger, "aac frame length not in range");
          }

          // first the crc check
          memcpy(d_aac_frame, &in[n * d_superframe_size + d_au_start[i]], aac_frame_length);
          if (check_crc_bytes(d_aac_frame, aac_frame_length)) {
            handle_aac_frame(d_aac_frame,
                             aac_frame_length,
                             d_dac_rate,
                             d_sbr_flag,
                             d_mpeg_surround,
                             d_aac_channel_mode,
                             out + d_nsamples_produced);

          } else {
            GR_LOG_DEBUG(d_logger, "CRC failure with dab+ frame");
          }
        }

      }


      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each((noutput_items/5760) * d_superframe_size);

      // Tell runtime system how many output items we produced.
      return d_nsamples_produced;
    }

  } /* namespace dab */
} /* namespace gr */
