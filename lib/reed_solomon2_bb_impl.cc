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
#include "reed_solomon2_bb_impl.h"

using namespace boost;

namespace gr {
  namespace dab {

    reed_solomon2_bb::sptr
    reed_solomon2_bb::make(int bit_rate_n)
    {
      return gnuradio::get_initial_sptr
        (new reed_solomon2_bb_impl(bit_rate_n));
    }

    /*
     * The private constructor
     */
    reed_solomon2_bb_impl::reed_solomon2_bb_impl(int bit_rate_n)
      : gr::block("reed_solomon2_bb",
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
              gr::io_signature::make(1, 1, sizeof(unsigned char))),
        d_bit_rate_n(bit_rate_n)
    {
      set_output_multiple(d_bit_rate_n * 110);
      rscodec *d_rs_decoder = new rscodec();
    }

    /*
     * Our virtual destructor.
     */
    reed_solomon2_bb_impl::~reed_solomon2_bb_impl()
    {
    }

    void
    reed_solomon2_bb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items * (120 / 110);
    }

    int
    reed_solomon2_bb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const unsigned char *in = (const unsigned char *) input_items[0];
      unsigned char *out = (unsigned char *) output_items[0];
      d_nproduced = 0;
      d_nconsumed = 0;

      for (int i = 0; i < noutput_items / (d_bit_rate_n * 110); i++) {
        for (int j = 0; j < d_bit_rate_n; j++) {
          int16_t ler = 0;
          for (int k = 0; k < 120; k++) {
            d_rs_in[k] = in[d_nconsumed*d_bit_rate_n*120 + (j + k * d_bit_rate_n)];
          }
          ler = d_rs_decoder.dec(d_rs_in, d_rs_out, 135);
          if (ler < 0) {
            GR_LOG_DEBUG(d_logger, "error repair failed"); // cannot correct error -> dump frame
            d_nproduced--;
            break; //dump whole superframe
          } else {
            GR_LOG_DEBUG(d_logger, format("error repair succeeded (%d errors)") %ler);
            for (int k = 0; k < 110; k++) {
              out[d_nproduced * d_bit_rate_n * 110 + j + k * d_bit_rate_n] = d_rs_out[k];
            }
          }
        }
        d_nproduced++;
        d_nconsumed++;
      }

      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each(d_nconsumed *120*d_bit_rate_n);

      // Tell runtime system how many output items we produced.
      return d_nproduced *110*d_bit_rate_n;
    }

  } /* namespace dab */
} /* namespace gr */

