/* -*- c++ -*- */
/* 
 * 2017 Moritz Luca Schmid, Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT).
 * The content of this class is adopted from ODR-DabMod and written into a GNU Radio OutOfTree block.
 *
   Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011 Her Majesty
   the Queen in Right of Canada (Communications Research Center Canada)
   See https://github.com/Opendigitalradio/ODR-DabMod for licensing information of ODR-DabMod.
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


#ifndef INCLUDED_DAB_CONV_ENCODER_BB_H
#define INCLUDED_DAB_CONV_ENCODER_BB_H

#include <dab/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace dab {

    /*! \brief convolutional encoding for DAB without puncturing
     * \ingroup dab
     *
     */
    class DAB_API conv_encoder_bb : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<conv_encoder_bb> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of dab::conv_encoder_bb.
       *
       * To avoid accidental use of raw pointers, dab::conv_encoder_bb's
       * constructor is in a private implementation
       * class. dab::conv_encoder_bb::make is the public interface for
       * creating new instances.
       */
      static sptr make(int framesize);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_CONV_ENCODER_BB_H */

