/* -*- c++ -*- */
/*
 * Copyright belongs to Andreas Mueller
 * Modified 2017 by Moritz Luca Schmid, Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT).
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
#ifndef INCLUDED_DAB_FIB_SINK_VB_IMPL_H
#define INCLUDED_DAB_FIB_SINK_VB_IMPL_H

#include <dab/fib_sink_vb.h>

namespace gr {
    namespace dab {
/*! \brief sink for DAB FIBs, interprets MSC and SI
 *
 */
        class fib_sink_vb_impl : public fib_sink_vb {

        private:
          unsigned char frame [32];
            int process_fib(const unsigned char *fib);
            int process_fig(uint8_t type, const unsigned char *data, uint8_t length);


        public:
            fib_sink_vb_impl();
            int work(int noutput_items,
                     gr_vector_const_void_star &input_items,
                     gr_vector_void_star &output_items);
        };
    }
}

#endif /* INCLUDED_DAB_FIB_SINK_B_H */