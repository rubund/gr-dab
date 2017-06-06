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

#include <gnuradio/io_signature.h>
#include "transmission_frame_mux_bb_impl.h"

namespace gr {
    namespace dab {

        transmission_frame_mux_bb::sptr
        transmission_frame_mux_bb::make(int transmission_mode, const std::vector<unsigned int> &subch_size)
        {
            return gnuradio::get_initial_sptr
                    (new transmission_frame_mux_bb_impl(transmission_mode, subch_size));
        }

        /*
         * The private constructor
         */
        transmission_frame_mux_bb_impl::transmission_frame_mux_bb_impl(int transmission_mode,
                                                                       const std::vector<unsigned int> &subch_size)
                : gr::block("transmission_frame_mux_bb",
                            gr::io_signature::make(2, 9, sizeof(unsigned char)),
                            gr::io_signature::make(2, 2, sizeof(unsigned char))),
                  d_transmission_mode(transmission_mode), d_subch_size(subch_size)
        {
            switch (transmission_mode) {
                case 1:
                    d_num_fibs = 12;
                    d_num_cifs = 4;
                    break;
                case 2:
                    d_num_fibs = 3;
                    d_num_cifs = 1;
                    break;
                case 3:
                    d_num_fibs = 4;
                    d_num_cifs = 1;
                    break;
                case 4:
                    d_num_fibs = 6;
                    d_num_cifs = 2;
                    break;
                default:
                    throw fprintf(stderr, "Transmission mode %d doesn't exist", transmission_mode);
            }
            d_vlen_out = d_num_fibs * d_fib_len + d_num_cifs * d_cif_len;
            d_subch_total_len = 0;
            for (int i = 0; i < 7; ++i) {
                d_subch_total_len += subch_size[i];
            }
            if(d_subch_total_len * d_cu_len > d_cif_len)
            {
                throw fprintf(stderr, "subchannels are %d bytes too long for CIF", (d_subch_total_len * d_cu_len - d_cif_len));
            }
            set_output_multiple(d_vlen_out);
        }

        /*
         * Our virtual destructor.
         */
        transmission_frame_mux_bb_impl::~transmission_frame_mux_bb_impl()
        {
        }

        void
        transmission_frame_mux_bb_impl::forecast(int noutput_items, gr_vector_int &ninput_items_required)
        {
            // the first input is always the FIC
            ninput_items_required[0] = d_num_fibs * d_fib_len * (noutput_items / d_vlen_out);
            // the second input is always the PRBS source
            ninput_items_required[1] = d_cif_len * 8;
            for (int i = 0; i < 7; ++i) {
                // the amount of consumed data of each sub-channel depends on its size
                ninput_items_required[i+2] = d_subch_size[i]*d_cu_len * (noutput_items / d_vlen_out);
            }
        }

        int
        transmission_frame_mux_bb_impl::general_work(int noutput_items,
                                                     gr_vector_int &ninput_items,
                                                     gr_vector_const_void_star &input_items,
                                                     gr_vector_void_star &output_items)
        {
            unsigned char *out = (unsigned char *) output_items[0];
            const unsigned char *in;

            // write FIBs
           in = (const unsigned char *) input_items[0];
            for (int i = 0; i < noutput_items/d_vlen_out; ++i) {
                memcpy(out + i * d_vlen_out, in, d_num_fibs*d_fib_len);
                in += d_num_fibs*d_fib_len;
            }
            // write sub-channels
            unsigned int cu_index = 4 * d_num_fibs;
            for (int j = 0; j < 7; ++j) {
                in = (const unsigned char *) input_items[i+2];
                for (int i = 0; i < noutput_items/d_vlen_out; ++i) {
                    memcpy(out + i*d_vlen_out + cu_index*d_cu_len, in, d_subch_size[j]*d_cu_len);
                    in += d_num_fibs*d_fib_len;
                }
                cu_index += d_subch_size[j];
            }
            // fill remaining cus with padding
            in = (const unsigned char *) input_items[1];
            for (int i = 0; i < noutput_items/d_vlen_out; ++i) {

            }



            // Tell runtime system how many input items we consumed on
            // each input stream.
            consume_each(noutput_items);

            // Tell runtime system how many output items we produced.
            return noutput_items;
        }

    } /* namespace dab */
} /* namespace gr */

