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

#ifndef INCLUDED_DAB_REED_SOLOMON2_BB_IMPL_H
#define INCLUDED_DAB_REED_SOLOMON2_BB_IMPL_H

#include <dab/reed_solomon2_bb.h>
#include "rscodec.h"

namespace gr {
  namespace dab {
/*! \brief reed solomon error repair
 *
 * Reed Solomon RS(120, 110, t=5) with virtual interleaving; derived from RS(255, 245, t=5). Details see ETSI TS 102 563 clause 6.0 and 6.1.
 * Uses rscodec class for RS decoding/error repair.
 *
 * @param bit_rate_n data rate in multiples of 8kbit/s
 *
 */
    class reed_solomon2_bb_impl : public reed_solomon2_bb
    {
     private:
      int d_bit_rate_n;
      rscodec	d_rs_decoder;
      int d_nproduced;
      int d_nconsumed;
      uint8_t d_rs_in [120];
      uint8_t d_rs_out [110];

     public:
      reed_solomon2_bb_impl(int bit_rate_n);
      ~reed_solomon2_bb_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_REED_SOLOMON2_BB_IMPL_H */

