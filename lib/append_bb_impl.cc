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
#include <gnuradio/io_signature.h>
#include "append_bb_impl.h"

namespace gr {
  namespace dab {

    append_bb::sptr
    append_bb::make(unsigned int vlen_in, unsigned int vlen_out, uint8_t fillval)
    {
      return gnuradio::get_initial_sptr
        (new append_bb_impl(vlen_in, vlen_out, fillval));
    }

    /*
     * The private constructor
     */
    append_bb_impl::append_bb_impl(unsigned int vlen_in, unsigned int vlen_out, uint8_t fillval)
      : gr::block("append_bb",
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
              gr::io_signature::make(1, 1, sizeof(unsigned char))),
        d_vlen_in(vlen_in), d_vlen_out(vlen_out), d_fillval(fillval)
    {
        try
        {
            if (vlen_in > vlen_out) throw (vlen_in - vlen_out);
        }
        catch (int difference)
        {
            GR_LOG_WARN(d_logger, "out vector shorter than in vector; prune instead of append");
        }

        set_output_multiple(vlen_out);
        set_relative_rate(vlen_out/vlen_in);
    }

    /*
     * Our virtual destructor.
     */
    append_bb_impl::~append_bb_impl()
    {
    }

    void
    append_bb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items - (d_vlen_out - d_vlen_in);
    }

    int
    append_bb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const unsigned char *in = (const unsigned char *) input_items[0];
        unsigned char *out = (unsigned char *) output_items[0];

      for(int i = 0; i < noutput_items/d_vlen_out; i++){
          memcpy(&out[i*d_vlen_out], &in[i*d_vlen_in], d_vlen_in); //copy in vector
          memset(&out[i*d_vlen_out + d_vlen_in], d_fillval, d_vlen_out - d_vlen_in); //append fillval
      }
      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each (noutput_items/d_vlen_out * d_vlen_in);

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace dab */
} /* namespace gr */

