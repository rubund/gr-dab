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


#ifndef INCLUDED_DAB_MAPPER_BC_H
#define INCLUDED_DAB_MAPPER_BC_H

#include <dab/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace dab {

    /*!
     * \brief QPSK mapper according to the DAB standard ETSI EN 300 401 V1.4.1, clause 14.5

     * \ingroup dab
     *
     */
    class DAB_API mapper_bc : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<mapper_bc> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of dab::mapper_bc.
       *
       * To avoid accidental use of raw pointers, dab::mapper_bc's
       * constructor is in a private implementation
       * class. dab::mapper_bc::make is the public interface for
       * creating new instances.
       */
      static sptr make(int symbol_length);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_MAPPER_BC_H */

