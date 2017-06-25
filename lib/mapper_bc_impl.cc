/* -*- c++ -*- */
/* 
 * Copyright 2017 by Moritz Luca Schmid, Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT).
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
 * the Free Software Foundation, Inc., 51 Frank1Llin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "mapper_bc_impl.h"

namespace gr {
  namespace dab {

    mapper_bc::sptr
    mapper_bc::make(int symbol_length)
    {
      return gnuradio::get_initial_sptr
        (new mapper_bc_impl(symbol_length));
    }

    /*
     * The private constructor
     */
    mapper_bc_impl::mapper_bc_impl(int symbol_length)
      : gr::block("mapper_bc",
              gr::io_signature::make(1, 1, sizeof(char)),
              gr::io_signature::make(1, 1, sizeof(gr_complex))),
        d_symbol_length(symbol_length)
    {
      set_output_multiple(symbol_length);
    }

    /*
     * Our virtual destructor.
     */
    mapper_bc_impl::~mapper_bc_impl()
    {
    }

    void
    mapper_bc_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items*2;
    }

    int
    mapper_bc_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const char *in = (const char *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];

      // for each symbol
      for(int i = 0; i < noutput_items/d_symbol_length; i++){
        // for d_symbol_length complex outputs
        for(int j = 0; j < d_symbol_length; j++){
          //out[i*2*d_symbol_length + j] = gr_complex(in[(i*2)*d_symbol_length + j], in[(i*2 + 1)*d_symbol_length + j]);
          if(in[(i*2)*d_symbol_length + j] > 0){
            if(in[(i*2 + 1)*d_symbol_length + j] > 0)
              out[i*d_symbol_length + j] = gr_complex(-I_SQRT2, -I_SQRT2); //11
            else
              out[i*d_symbol_length + j] = gr_complex(-I_SQRT2, I_SQRT2); //10
          }
          else{
            if(in[(i*2 + 1)*d_symbol_length + j] > 0)
              out[i*d_symbol_length + j] = gr_complex(I_SQRT2, -I_SQRT2); //01
            else
              out[i*d_symbol_length + j] = gr_complex(I_SQRT2, I_SQRT2); //00
          }
        }
      }
      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each (noutput_items*2);

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace dab */
} /* namespace gr */

