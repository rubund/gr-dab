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

#ifndef INCLUDED_DAB_REED_SOLOMON3_BB_IMPL_H
#define INCLUDED_DAB_REED_SOLOMON3_BB_IMPL_H

#include <dab/reed_solomon3_bb.h>
extern "C" {
#include <fec/fec.h>
}

namespace gr {
  namespace dab {

    class reed_solomon3_bb_impl : public reed_solomon3_bb
    {
     private:
      int d_bit_rate_n;
      int d_superframe_size;
      int d_superframe_size_rs;
      void *rs_handle;
      uint8_t rs_packet[120];
      int corr_pos[10];
      void DecodeSuperframe(uint8_t *sf, size_t sf_len);

     public:
      reed_solomon3_bb_impl(int bit_rate_n);
      ~reed_solomon3_bb_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_REED_SOLOMON3_BB_IMPL_H */

