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


#ifndef INCLUDED_DAB_CRC16_BB_H
#define INCLUDED_DAB_CRC16_BB_H

#include <dab/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace dab {

    /*!
     * \brief <+description of block+>
     * \ingroup dab
     *
     */
    class DAB_API crc16_bb : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<crc16_bb> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of dab::crc16_bb.
       *
       * To avoid accidental use of raw pointers, dab::crc16_bb's
       * constructor is in a private implementation
       * class. dab::crc16_bb::make is the public interface for
       * creating new instances.
       */
      static sptr make(int length, uint16_t generator, uint16_t initial_state);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_CRC16_BB_H */

