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
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_DAB_MAPPER_BC_IMPL_H
#define INCLUDED_DAB_MAPPER_BC_IMPL_H

#define I_SQRT2 0.707106781187

#include <dab/mapper_bc.h>

namespace gr {
  namespace dab {
/*! \brief QPSK mapper according to the DAB standard ETSI EN 300 401 V1.4.1, clause 14.5
 *
 * uses two unpacked bit frames of respectively length symbol_length to form a complex frame of length symbol_length
 * two bits define a complex symbol, the first bit is taken from the the first bit frame at index i, the second bit from the second bit frame at index i, they form the complex symbol at index i
 *
 * @param symbol_length length of output frame
 *
 */
    class mapper_bc_impl : public mapper_bc {
    private:
      int d_symbol_length;

    public:
      mapper_bc_impl(int symbol_length);

      ~mapper_bc_impl();

      // Where all the action really happens
      void forecast(int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_MAPPER_BC_IMPL_H */

