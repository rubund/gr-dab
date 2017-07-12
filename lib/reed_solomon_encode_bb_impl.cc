/* -*- c++ -*- */
/* 
 * Reed-Solomon decoder for DAB+
 * Copyright 2002 Phil Karn, KA9Q
 * May be used under the terms of the GNU General Public License (GPL)
 *
 * Rewritten into a GNU Radio block for gr-dab
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
#include "reed_solomon_encode_bb_impl.h"

using namespace boost;

namespace gr {
  namespace dab {

    reed_solomon_encode_bb::sptr
    reed_solomon_encode_bb::make(int bit_rate_n)
    {
      return gnuradio::get_initial_sptr
        (new reed_solomon_encode_bb_impl(bit_rate_n));
    }

    /*
     * The private constructor
     */
    reed_solomon_encode_bb_impl::reed_solomon_encode_bb_impl(int bit_rate_n)
      : gr::block("reed_solomon_encode_bb",
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
              gr::io_signature::make(1, 1, sizeof(unsigned char)))
    {
      //initialize Reed Solomon
      rs_handle = init_rs_char(8, 0x11D, 0, 1, 10, 135);
      if (!rs_handle) {
        GR_LOG_DEBUG(d_logger, "RS init failed");
      } else {
        GR_LOG_DEBUG(d_logger, "RS init succeeded");
      }
      d_superframe_size_rs = bit_rate_n * 120;
      d_superframe_size_in = bit_rate_n * 110;
      set_output_multiple(d_superframe_size_rs);
    }

    /*
     * Our virtual destructor.
     */
    reed_solomon_encode_bb_impl::~reed_solomon_encode_bb_impl()
    {
      free_rs_char(rs_handle);
    }

    void
    reed_solomon_encode_bb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items*110/120;
    }

    int
    reed_solomon_encode_bb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const unsigned char *in = (const unsigned char *) input_items[0];
      unsigned char *out = (unsigned char *) output_items[0];

      for (int n = 0; n < noutput_items / d_superframe_size_rs; n++){
        //copy data bits to output
        memcpy(&out[d_superframe_size_rs*n], &in[d_superframe_size_in*n], d_superframe_size_in);
        //now calculate parity bits
        // buffer to feed to encoder (110*bit_rate_n, still without parity words)
        unsigned char buf_to_rs_enc[110];
        unsigned char rs_parity[10];
        int col, row;
        // virtual interleaving
        for(row = 0; row < d_bit_rate_n; row++){
          for(col = 0; col < 110; col++){
            buf_to_rs_enc[col] = in[d_superframe_size_in*n + d_bit_rate_n*col + row];
          }
          // RS encoding
          encode_rs_char(rs_handle, buf_to_rs_enc, rs_parity);
          // write parity bytes to output buffer
          /*for(col = 110; col < 120; col++){
            //out[d_superframe_size_rs*n + d_bit_rate_n*col + row] = rs_parity[col-110];
            GR_LOG_DEBUG(d_logger, format("write parity bit at index %d") %(d_superframe_size_rs*n + d_bit_rate_n*col + row));
            //out[d_superframe_size_rs*n + d_bit_rate_n*col + row] = 3;
          }*/
        }
      }

      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each (noutput_items*110/120);

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace dab */
} /* namespace gr */

