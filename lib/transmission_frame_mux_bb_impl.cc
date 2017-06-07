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
                            gr::io_signature::make(1, 8, sizeof(unsigned char)),
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

            // generate PRBS for padding
            generate_prbs(d_prbs, sizeof(d_prbs));
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

        void
        transmission_frame_mux_bb_impl::generate_prbs(char *out_ptr, int length)
        {
            char bits[9] = {1, 1, 1, 1, 1, 1, 1, 1, 1};
            char newbit;
            for (int i = 0; i < length; ++i) {
                newbit = bits[8] ^ bits[4];
                memcpy(bits+1, bits, 8);
                bits[0] = newbit;
                out_ptr[i] = newbit;
                //printf(newbit);
            }

        }

        int
        transmission_frame_mux_bb_impl::general_work(int noutput_items,
                                                     gr_vector_int &ninput_items,
                                                     gr_vector_const_void_star &input_items,
                                                     gr_vector_void_star &output_items)
        {
            unsigned char *out = (unsigned char *) output_items[0];
            unsigned char *triggerout = (unsigned char *) output_items[1];
            const unsigned char *in;

            // create control stream for ofdm with trigger at start of frame and set zero
            memset(triggerout, 0, noutput_items);
            for(int i = 0; i < noutput_items/d_vlen_out; ++i) {
                triggerout[i*d_vlen_out] = 1;
            }

            // write FIBs
           in = (const unsigned char *) input_items[0];
            for (int i = 0; i < noutput_items/d_vlen_out; ++i) {
                memcpy(out + i * d_vlen_out, in, d_num_fibs*d_fib_len);
                in += d_num_fibs*d_fib_len;
            }
            // write sub-channels
            unsigned int cu_index = 4 * d_num_fibs;
            for (int j = 0; j < 7; ++j) {
                in = (const unsigned char *) input_items[j+1];
                for (int i = 0; i < noutput_items/d_vlen_out; ++i) {
                    memcpy(out + i*d_vlen_out + d_num_fibs*d_fib_len + cu_index*d_cu_len, in, d_subch_size[j]*d_cu_len);
                    in += d_num_fibs*d_fib_len;
                }
                cu_index += d_subch_size[j];
            }
            // fill remaining cus with padding
            in = (const unsigned char *) input_items[1];
            for (int i = 0; i < noutput_items/d_vlen_out; ++i) {
                memcpy(out + i*d_vlen_out + d_num_fibs*d_fib_len + d_subch_total_len*d_cu_len, d_prbs + d_subch_total_len*d_cu_len*8, (d_vlen_out - d_num_fibs*d_fib_len - d_subch_total_len*d_cu_len)*8);
                for (int j = d_subch_total_len*d_cu_len; j < d_subch_total_len; ++j) {
                    unsigned char temp = 0;
                    for (int n = 0; n < 8; ++n)
                        temp = (temp << 1) | (d_prbs[j*8 + n] & 01);
                    out[i*d_vlen_out + d_num_fibs*d_fib_len + j] = temp;
                }
            }

            // Tell runtime system how many input items we consumed on
            // each input stream.
            consume(0, noutput_items/d_vlen_out * d_num_fibs*d_fib_len);
            for (int j = 0; j < 7; ++j) {
                consume(j+1, noutput_items/d_vlen_out * d_subch_size[j]*d_cu_len);
            }

            // Tell runtime system how many output items we produced.
            return noutput_items;
        }

    } /* namespace dab */
} /* namespace gr */

