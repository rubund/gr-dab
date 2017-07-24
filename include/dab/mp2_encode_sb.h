/* -*- c++ -*- */
/* 
 * Copyright 2017 Moritz Luca Schmid, Communications Engineering Lab (CEL) / Karlsruhe Institute of Technology (KIT).
 *
 * Code from the following third party modules is used:
 * - ODR-AudioEnc, Copyright (C) 2011 Martin Storsjo, (C) 2017 Matthias P. Braendli; Licensed under the Apache License, Version 2.0 (the "License")
 * - libtoolame-dab taken from ODR-AudioEnc, derived from TooLAME, licensed under LGPL v2.1 or later. See libtoolame-dab/LGPL.txt. This is built into a shared library.
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


#ifndef INCLUDED_DAB_MP2_ENCODE_SB_H
#define INCLUDED_DAB_MP2_ENCODE_SB_H

#include <dab/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace dab {

    /*!
     * \brief block to encode a 16bit PCM stream to MPEG2 for DAB
     * \ingroup dab
     *
     */
    class DAB_API mp2_encode_sb : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<mp2_encode_sb> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of dab::mp2_encode_sb.
       *
       * To avoid accidental use of raw pointers, dab::mp2_encode_sb's
       * constructor is in a private implementation
       * class. dab::mp2_encode_sb::make is the public interface for
       * creating new instances.
       */
      static sptr make(int bit_rate_n, int channels, int sample_rate);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_MP2_ENCODE_SB_H */

