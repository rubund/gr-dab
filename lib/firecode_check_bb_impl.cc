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
#include "firecode_check_bb_impl.h"

namespace gr {
  namespace dab {

    firecode_check_bb::sptr
    firecode_check_bb::make(int bit_rate_n)
    {
      return gnuradio::get_initial_sptr
        (new firecode_check_bb_impl(bit_rate_n));
    }

    /*
     * The private constructor
     */
    firecode_check_bb_impl::firecode_check_bb_impl(int bit_rate_n)
      : gr::block("firecode_check_bb",
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
              gr::io_signature::make(1, 1, sizeof(unsigned char)))
    {
        d_frame_size = 24 * bit_rate_n;
        set_output_multiple(5*d_frame_size); //superframe
    }

    /*
     * Our virtual destructor.
     */
    firecode_check_bb_impl::~firecode_check_bb_impl()
    {
    }

    void
    firecode_check_bb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        ninput_items_required[0] = noutput_items; //sync
    }

    int
    firecode_check_bb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const unsigned char *in = (const unsigned char *) input_items[0];
        unsigned char *out = (unsigned char *) output_items[0];
        int n = 0;
        int nsuperframes_produced = 0;

        while(n < noutput_items) {
            //check fire code and if the firecode is OK, handle the frame
            if (fc.check(&in[n * d_frame_size]) /*&& (process_superframe(in + n * d_frame_size))*/)
            {
                GR_LOG_DEBUG(d_logger, format("fire code OK at frame %d") %n);
                for(int i = 0; i < 5 * d_frame_size; i++) {
                    out[nsuperframes_produced * d_frame_size * 5 + i] = in[n*d_frame_size + i];
                }
                n += 5;
                nsuperframes_produced++;
            }
            else
            {
                GR_LOG_DEBUG(d_logger, format("fire code failed at frame %d - shift to left") %n);
                n++;
            }
        }
      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each (noutput_items);

      // Tell runtime system how many output items we produced.
      return nsuperframes_produced * 5*d_frame_size;
    }

  } /* namespace dab */
} /* namespace gr */

