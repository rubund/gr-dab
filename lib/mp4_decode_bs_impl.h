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

#ifndef INCLUDED_DAB_MP4_DECODE_BS_IMPL_H
#define INCLUDED_DAB_MP4_DECODE_BS_IMPL_H

#include <dab/mp4_decode_bs.h>
#include "dab-constants.h"
#include "neaacdec.h"

namespace gr {
  namespace dab {

    class mp4_decode_bs_impl : public mp4_decode_bs
    {
    private:
      int d_nsamples_produced;
      int d_bit_rate_n;
      int d_superframe_size;
      bool aacInitialized;
      int32_t baudRate;
      uint8_t d_dac_rate, d_sbr_flag, d_aac_channel_mode, d_ps_flag, d_mpeg_surround, d_num_aus;
      uint8_t d_au_start[7];
      uint8_t d_aac_frame[960];

      NeAACDecHandle aacHandle;

      int get_aac_channel_configuration(int16_t m_mpeg_surround_config, uint8_t aacChannelMode);
      bool initialize(uint8_t dacRate,
                      uint8_t sbrFlag,
                      int16_t mpegSurround,
                      uint8_t aacChannelMode);
      void handle_aac_frame(uint8_t *v,
                            int16_t frame_length,
                            uint8_t dacRate,
                            uint8_t sbrFlag,
                            uint8_t mpegSurround,
                            uint8_t aacChannelMode,
                            int* out_sample);
      int16_t MP42PCM(uint8_t dacRate,
                      uint8_t sbrFlag,
                      int16_t mpegSurround,
                      uint8_t aacChannelMode,
                      uint8_t buffer[],
                      int16_t bufferLength,
                      int* out_sample);

    public:
      mp4_decode_bs_impl(int bit_rate_n);
      ~mp4_decode_bs_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_MP4_DECODE_BS_IMPL_H */
