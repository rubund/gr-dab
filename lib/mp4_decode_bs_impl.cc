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
#include "crc16.h"
#include "FIC.h"

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
                        gr::io_signature::make(1, 1, sizeof(unsigned char))),
              d_bit_rate_n(bit_rate_n)
    {
      d_superframe_size = bit_rate_n * 110;
      d_aacInitialized = false;
      baudRate = 48000;
      set_output_multiple(d_superframe_size); //TODO: right? baudRate*0.12 for output of one superframe
      aacHandle = NeAACDecOpen();
      //memset(d_aac_frame, 0, 960);
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

    void mp4_decode_bs_impl::handle_aac_frame(const uint8_t *v,
                                              int16_t frame_length,
                                              uint8_t dacRate,
                                              uint8_t sbrFlag,
                                              uint8_t mpegSurround,
                                              uint8_t aacChannelMode)
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
                        frame_length);
      //*error	= tmp == 0;
      GR_LOG_DEBUG(d_logger, format("produced %d samples") % tmp);
    }

    int16_t mp4_decode_bs_impl::MP42PCM(uint8_t dacRate,
                                        uint8_t sbrFlag,
                                        int16_t mpegSurround,
                                        uint8_t aacChannelMode,
                                        uint8_t buffer[],
                                        int16_t bufferLength)
    {
      int16_t samples;
      long unsigned int sampleRate;
      int16_t *outBuffer;
      NeAACDecFrameInfo hInfo;
      uint8_t dummy[10000];
      uint8_t channels;

      if (!d_aacInitialized) {
        if (!initialize(dacRate, sbrFlag, mpegSurround, aacChannelMode))
          return 0;
        d_aacInitialized = true;
        GR_LOG_DEBUG(d_logger, "AAC initialized");
      }

      outBuffer = (int16_t *) NeAACDecDecode(aacHandle,
                                             &hInfo, buffer, bufferLength);
      sampleRate = hInfo.samplerate;

      samples = hInfo.samples;
      if ((sampleRate == 24000) ||
          (sampleRate == 32000) ||
          (sampleRate == 48000) ||
          (sampleRate != (long unsigned) baudRate)) {
        baudRate = sampleRate;
      }
      GR_LOG_ERROR(d_logger, format("bytes consumed %d") % (int) (hInfo.bytesconsumed));
      GR_LOG_ERROR(d_logger,
                   format("samplerate = %d, samples = %d, channels = %d, error = %d, sbr = %d") % sampleRate % samples %
                   (int) (hInfo.channels) % (int) (hInfo.error) % (int) (hInfo.sbr));

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


//      // write samples to output buffer
//      if (channels == 2) {
//        //audioBuffer  -> putDataIntoBuffer (outBuffer, samples);
//        for (int n = 0; n < samples; n++) {
//          out_sample[n] = (int) outBuffer[n];
//        }
//        /*if (audioBuffer -> GetRingBufferReadAvailable () > sampleRate / 8)
//          newAudio (sampleRate);*/
//      } else if (channels == 1) {
//        int16_t *buffer = (int16_t *) alloca(2 * samples);
//        int16_t i;
//        for (i = 0; i < samples; i++) {
//          buffer[2 * i] = ((int16_t *) outBuffer)[i];
//          buffer[2 * i + 1] = buffer[2 * i];
//        }
//        //audioBuffer  -> putDataIntoBuffer (buffer, samples);
//        for (int n = 0; n < samples; n++) {
//          out_sample[n] = (int) buffer[n];
//        }
//        /*if (audioBuffer -> GetRingBufferReadAvailable () > sampleRate / 8)
//          newAudio (sampleRate);*/
//      } else
//        GR_LOG_ERROR(d_logger, "Cannot handle these channels");


      d_nsamples_produced += samples;
      return samples / 2; //TODO: for channels == 1 return samples or for loop to samples/2
    }

    bool mp4_decode_bs_impl::CRC16(uint8_t *data, size_t length)
    {

      uint16_t CRC = 0xFFFF;
      uint16_t poly = 0x1020;

      *(data + length - 2) ^= 0xFF;
      *(data + length - 1) ^= 0xFF;

      for (size_t i = 0; i < length; ++i) {
        for (size_t b = 0; b < 8; ++b) {
          if (((CRC & 0x8000) >> 15) ^ ((data[i] >> (7 - b)) & 0x0001)) {
            CRC <<= 1;
            CRC ^= poly;
            CRC |= 0x0001;
          } else {
            CRC <<= 1;
            CRC &= 0xFFFE;
          }
        }
      }

      *(data + length - 2) ^= 0xFF;
      *(data + length - 1) ^= 0xFF;
      GR_LOG_DEBUG(d_logger, format("CRC = %d") % CRC);
      if (CRC)
        return false;
      else
        return true;
    }

    uint16_t mp4_decode_bs_impl::BinToDec(const uint8_t *data, size_t offset, size_t length)
    {
      uint32_t output = (*(data + offset / 8) << 16) | ((*(data + offset / 8 + 1)) << 8) |
                        (*(data + offset / 8 + 2));      // should be big/little endian save
      output >>= 24 - length - offset % 8;
      output &= (0xFFFF >> (16 - length));
      return static_cast<uint16_t>(output);
    }

    int
    mp4_decode_bs_impl::general_work(int noutput_items,
                                     gr_vector_int &ninput_items,
                                     gr_vector_const_void_star &input_items,
                                     gr_vector_void_star &output_items)
    {
      const unsigned char *in = (const unsigned char *) input_items[0] + d_superframe_size;
      unsigned char *out = (unsigned char *) output_items[0];
      d_nsamples_produced = 0;

      for (int n = 0; n < noutput_items / d_superframe_size; n++) {
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
                     (int) d_dac_rate % (int) d_sbr_flag % (int) d_aac_channel_mode % (int) d_ps_flag %
                     (int) d_mpeg_surround);

        switch (2 * d_dac_rate + d_sbr_flag) {
          default:    // cannot happen
          case 0:
            d_num_aus = 4;
            d_au_start[0] = 8;
            GR_LOG_DEBUG(d_logger, format("au%d start: %d") % 0 % d_au_start[0]);
            d_au_start[1] = in[n * d_superframe_size + 3] * 16 + (in[n * d_superframe_size + 4] >> 4);
            GR_LOG_DEBUG(d_logger, format("au%d start: %d") % 1 % d_au_start[1]);
            d_au_start[2] = (in[n * d_superframe_size + 4] & 0xf) * 256 + in[n * d_superframe_size + 5];
            GR_LOG_DEBUG(d_logger, format("au%d start: %d") % 2 % d_au_start[2]);
            d_au_start[3] = in[n * d_superframe_size + 6] * 16 + (in[n * d_superframe_size + 7] >> 4);
            GR_LOG_DEBUG(d_logger, format("au%d start: %d") % 3 % d_au_start[3]);
            d_au_start[4] = d_superframe_size;
            GR_LOG_DEBUG(d_logger, format("au%d start: %d") % 4 % d_au_start[4]);
            break;
//
          case 1:
            d_num_aus = 2;
            d_au_start[n * d_superframe_size + 0] = 5;
            d_au_start[1] = in[n * d_superframe_size + 3] * 16 + (in[n * d_superframe_size + 4] >> 4);
            d_au_start[2] = d_superframe_size;
            break;
//
          case 2:
            d_num_aus = 6;
            d_au_start[0] = 11;
            d_au_start[1] = in[n * d_superframe_size + 3] * 16 + (in[n * d_superframe_size + 4] >> 4);
            d_au_start[2] = (in[n * d_superframe_size + 4] & 0xf) * 256 + in[n * d_superframe_size + 5];
            d_au_start[3] = in[n * d_superframe_size + 6] * 16 + (in[n * d_superframe_size + 7] >> 4);
            d_au_start[4] = (in[n * d_superframe_size + 7] & 0xf) * 256 + in[8];
            d_au_start[5] = in[n * d_superframe_size + 9] * 16 + (in[n * d_superframe_size + 10] >> 4);
            d_au_start[6] = d_superframe_size;
            break;
//
          case 3:
            d_num_aus = 3;
            d_au_start[0] = 6;
            d_au_start[1] = in[n * d_superframe_size + 3] * 16 + (in[n * d_superframe_size + 4] >> 4);
            d_au_start[2] = (in[n * d_superframe_size + 4] & 0xf) * 256 + in[n * d_superframe_size + 5];
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

          memcpy(d_aac_frame, &in[n * d_superframe_size + d_au_start[i]], aac_frame_length + 2);

          // calculate a some CRCs to compare
          // CRC gr-dab
          uint16_t crc = crc16((char *) &in[n * d_superframe_size + d_au_start[i]], aac_frame_length + 2, FIB_CRC_POLY,
                               FIB_CRC_INITSTATE);
          fprintf(stderr, "gr-dab CRC = %d\n", crc);
          // CRC qt-dab
          check_crc_bytes(&in[n * d_superframe_size + d_au_start[i]], aac_frame_length);
          // CRC SDR
          CRC16_SDR(d_aac_frame, aac_frame_length + 2);



          // first the crc check
          //if (CRC16_SDR(d_aac_frame, aac_frame_length+2)) {
          //uint16_t crc = crc16((char*)&in[n*d_superframe_size + d_au_start[i]], aac_frame_length+2, FIB_CRC_POLY, FIB_CRC_INITSTATE);
          //fprintf(stderr, "crc = %d\n", crc);
          //if (crc == 0){
          /*  GR_LOG_DEBUG(d_logger, format("CRC check of AU %d successful") % i);
            // handle proper AU
            handle_aac_frame(&in[n * d_superframe_size + d_au_start[i]],
                             aac_frame_length,
                             d_dac_rate,
                             d_sbr_flag,
                             d_mpeg_surround,
                             d_aac_channel_mode);
          } else {
            // dump corrupted AU
            GR_LOG_DEBUG(d_logger, format("CRC failure with dab+ frame"));
          }*/
        }
        //############################################################################################################################################################################
// implementation of SDR DAB to compare
        //######################################################################################################################################################################
        // decoding ADTS starts here
        uint8_t dac_sbr = (in[n * d_superframe_size + 2] & 0x60) >> 5;    // (18-19) dec_rate & sbr_flag at once
        uint8_t num_aus = 0;
        uint8_t adts_dacsbr = 0;                      // use last 4 bits
        uint8_t adts_chanconf = 0;                    // last 3 bits for channel index
        uint16_t au_start[7];                       // worst case num_aus+1
        memset(au_start, 0, 7 * sizeof(uint16_t));

        switch (dac_sbr) {
          case 0:                                     // 00b, dac=0, sbr=0
            num_aus = 4;                            // number of Access Units (AUs)
            au_start[0] = 8;                        // address of the first AU
            adts_dacsbr = 0x05;                     // [0 1 0 1] freq index for ADTS header
            break;
          case 1:                                     // 01b, dac=0, sbr=1
            num_aus = 2;                            // number of AUs
            au_start[0] = 5;                        // address of the first AU
            adts_dacsbr = 0x08;                     // [1 0 0 0] freq index for ADTS header
            break;
          case 2:                                     // 10b, dac=1, sbr=0
            num_aus = 6;                            // number of AUs
            au_start[0] = 11;                       // address of the first AU
            adts_dacsbr = 0x03;                     // [0 0 1 1] freq index for ADTS header
            break;
          case 3:                                         // 11b, dac=1, sbr=1
            num_aus = 3;                            // number of AUs
            au_start[0] = 6;                        // address of the first AU
            adts_dacsbr = 0x06;                     // [0 1 1 0] freq index for ADTS header
            break;
        }

        //bool aac_channel_mode = (adts_frame[2]&0x10)>>3;  // (20-bit) 0=mono, 1=stereo
        if (in[n * d_superframe_size + 2] & 0x08) {                             // (21-bit) parametric stereo (PS)
          adts_chanconf = 0x2;                            // [ 0 1 0 ] channel index for ADTS header
        } else {
          adts_chanconf = 0x1;                            // [ 0 0 1 ] channel index for ADTS header
        }
        //uint8_t mpeg_surround_config = adts_frame[2]&0x07;

        for (size_t r = 1; r < num_aus; ++r)                                // addresses of the AUs from 2:last
          au_start[r] = BinToDec(&in[n * d_superframe_size], 24 + 12 * (r - 1), 12);      // start from 25bit, each ADDR has 12bits
        au_start[num_aus] = d_superframe_size;

        GR_LOG_DEBUG(d_logger, "POLSKA reading now:");
        GR_LOG_DEBUG(d_logger,
                     format("superframe header: dac&sbr_flag %d, aac_mode %d, ps_flag %d, surround %d") %
                     (int) dac_sbr % (int) adts_chanconf % (int) d_ps_flag %
                     (int) d_mpeg_surround);

        for (size_t r = 0; r < num_aus; ++r) {
          size_t au_size = au_start[r + 1] - au_start[r] - 2;               // AU size in bytes, without CRC; -2 bytes?
          size_t adts_size = au_size + 7;                             // frame size = au_size bytes of AU + 7 bytes of the adts-header
          GR_LOG_DEBUG(d_logger, format("au%d start: %d") %r % d_au_start[r]);
        }

      }



      //consume items to dump them
      for (int i = 0; i < noutput_items; ++i) {
        out[i] = in[i];
      }

      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each(noutput_items);

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace dab */
} /* namespace gr */
