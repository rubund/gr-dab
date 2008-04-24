/* -*- c++ -*- */
/*
 * Copyright 2004 Free Software Foundation, Inc.
 * 
 * This file is part of GNU Radio
 * 
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

/*
 * config.h is generated by configure.  It contains the results
 * of probing for features, options etc.  It should be the first
 * file included in your .cc file.
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <dab_moving_sum_ff.h>
#include <gr_io_signature.h>

/*
 * Create a new instance of dab_moving_sum_ff and return
 * a boost shared_ptr.  This is effectively the public constructor.
 */
dab_moving_sum_ff_sptr 
dab_make_moving_sum_ff (int length)
{
  return dab_moving_sum_ff_sptr (new dab_moving_sum_ff (int length));
}

/*
 * Specify constraints on number of input and output streams.
 * This info is used to construct the input and output signatures
 * (2nd & 3rd args to gr_block's constructor).  The input and
 * output signatures are used by the runtime system to
 * check that a valid number and type of inputs and outputs
 * are connected to this block.  In this case, we accept
 * only 1 input and 1 output.
 */
static const int MIN_IN = 1;	// mininum number of input streams
static const int MAX_IN = 1;	// maximum number of input streams
static const int MIN_OUT = 1;	// minimum number of output streams
static const int MAX_OUT = 1;	// maximum number of output streams

/*
 * The private constructor
 */
dab_moving_sum_ff::dab_moving_sum_ff (int length)
  : gr_sync_block ("moving_sum_ff",
		   gr_make_io_signature (MIN_IN, MAX_IN, sizeof (float)),
		   gr_make_io_signature (MIN_OUT, MAX_OUT, sizeof (float))),
    d_sum(0)
{
  set_length(length);
}

/*
 * Our virtual destructor.
 */
dab_moving_sum_ff::~dab_moving_sum_ff ()
{
  // nothing else required in this example
}

int 
dab_moving_sum_ff::work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items)
{
  const float *in = (const float *) input_items[0];
  float *out = (float *) output_items[0];

  d_sum+=(double)in[0]-(double)in[noutput_items-1];

  // Tell runtime system how many output items we produced.
  return noutput_items;
}
