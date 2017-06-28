/* -*- c++ -*- */
/******************************************************************************
** kjmp2 -- a minimal MPEG-1/2 Audio Layer II decoder library                **
** version 1.1                                                               **
*******************************************************************************
** Copyright (C) 2006-2013 Martin J. Fiedler <martin.fiedler@gmx.net>        **
**                                                                           **
** This software is provided 'as-is', without any express or implied         **
** warranty. In no event will the authors be held liable for any damages     **
** arising from the use of this software.                                    **
**                                                                           **
** Permission is granted to anyone to use this software for any purpose,     **
** including commercial applications, and to alter it and redistribute it    **
** freely, subject to the following restrictions:                            **
**   1. The origin of this software must not be misrepresented; you must not **
**      claim that you wrote the original software. If you use this software **
**      in a product, an acknowledgment in the product documentation would   **
**      be appreciated but is not required.                                  **
**   2. Altered source versions must be plainly marked as such, and must not **
**      be misrepresented as being the original software.                    **
**   3. This notice may not be removed or altered from any source            **
**      distribution.                                                        **
******************************************************************************/

/*
*	Code adapted of the original code:
*	whole code is made into a GNU Radio block for use within the gr module gr-dab
* 2017 by Moritz Luca Schmid, Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT).
*
*/

#ifndef INCLUDED_DAB_MP2_DECODE_BS_IMPL_H
#define INCLUDED_DAB_MP2_DECODE_BS_IMPL_H

#include <dab/mp2_decode_bs.h>
#include	<stdio.h>
#include	<stdint.h>
#include	<math.h>
//#include	"pad-handler.h"

namespace gr {
  namespace dab {

#define KJMP2_MAX_FRAME_SIZE    1440  // the maximum size of a frame
#define KJMP2_SAMPLES_PER_FRAME 1152  // the number of samples per frame

// quantizer specification structure
    struct quantizer_spec {
      int32_t nlevels;
      uint8_t grouping;
      uint8_t cw_bits;
    };

    class mp2_decode_bs_impl : public mp2_decode_bs {
    private:
      int d_bit_rate_n;
      int d_bit_rate;
      int16_t	d_voffs;
      int32_t	d_baudRate;
      int16_t		d_mp2_framesize;
      int16_t d_mp2_header_OK;
      int16_t d_mp2_header_count;
      int16_t d_mp2_bit_count;
      int16_t d_number_of_frames;
      int16_t d_error_frames;
      int32_t	bit_window;
      int32_t bits_in_window;

      void set_samplerate	(int32_t);
      int32_t	mp2_samplerate	(uint8_t *);
      struct quantizer_spec *read_allocation (int, int);
      void read_samples (struct quantizer_spec *, int, int *);
      int32_t get_bits (int32_t);

    public:
      mp2_decode_bs_impl(int bit_rate_n);

      ~mp2_decode_bs_impl();

      // Where all the action really happens
      void forecast(int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_MP2_DECODE_BS_IMPL_H */

