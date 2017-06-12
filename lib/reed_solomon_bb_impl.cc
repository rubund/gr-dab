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
#include "reed_solomon_bb_impl.h"

namespace gr {
  namespace dab {

    reed_solomon_bb::sptr
    reed_solomon_bb::make()
    {
      return gnuradio::get_initial_sptr
        (new reed_solomon_bb_impl());
    }

    /*
     * The private constructor
     */
    reed_solomon_bb_impl::reed_solomon_bb_impl(int bit_rate_n)
      : gr::block("reed_solomon_bb",
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
              gr::io_signature::make(1, 1, sizeof(unsigned char))),
        my_rs_decoder (8, 0435, 0, 1, 10), d_bit_rate_n(bit_rate_n)
    {
      set_output_multiple(d_bit_rate_n*110);
      d_nproduced = 0;
    }

    /*
     * Our virtual destructor.
     */
    reed_solomon_bb_impl::~reed_solomon_bb_impl()
    {
    }

    void
    reed_solomon_bb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items * (120/110);
    }

    int
    reed_solomon_bb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const unsigned char *in = (const unsigned char *) input_items[0];
      unsigned char *out = (unsigned char *) output_items[0];


      for (int j = 0; j < d_bit_rate_n; j ++) {
        int16_t ler	= 0;
        for (int k = 0; k < 120; k ++)
          d_rs_in[k] = in[j + k*d_bit_rate_n];
        ler = my_rsDecoder. dec (d_rs_in, d_rs_out, 135);
        if (ler < 0) {
          continue; //TODO: continue proper coding style?
        }
        for (int k = 0; k < 110; k ++)
          out [j + k*d_bit_rate_n] = d_rs_out [k];
        d_nproduced ++;
      }



      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each (noutput_items * (120/110));

      // Tell runtime system how many output items we produced.
      return d_nproduced * 110;
    }

  } /* namespace dab */
} /* namespace gr */

