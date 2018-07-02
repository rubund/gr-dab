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

#include <gnuradio/io_signature.h>
#include "ofdm_remove_first_symbol_vcc_impl.h"

namespace gr {
  namespace dab {

ofdm_remove_first_symbol_vcc::sptr
ofdm_remove_first_symbol_vcc::make(unsigned int vlen)
{
  return gnuradio::get_initial_sptr
    (new ofdm_remove_first_symbol_vcc_impl(vlen));
}

ofdm_remove_first_symbol_vcc_impl::ofdm_remove_first_symbol_vcc_impl(unsigned int vlen)
  : gr::block("ofdm_remove_first_symbol_vcc",
             gr::io_signature::make (1, 1, sizeof(gr_complex)*vlen),
             gr::io_signature::make (1, 1, sizeof(gr_complex)*vlen)),
  d_vlen(vlen), d_start(0)
{
    set_tag_propagation_policy(TPP_DONT);
}

void 
ofdm_remove_first_symbol_vcc_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
  //int in_req  = noutput_items; + 1 + noutput_items/76; // at most every 76th symbol is thrown away (depends on the DAB mode)
  int in_req = noutput_items; // altough more may be needed, try to produce output even with only one input - if it's a pilot, we can just consume it ...
  unsigned ninputs = ninput_items_required.size ();
  for (unsigned int i = 0; i < ninputs; i++)
    ninput_items_required[i] = in_req;
}


int 
ofdm_remove_first_symbol_vcc_impl::general_work (int noutput_items,
                        gr_vector_int &ninput_items,
                        gr_vector_const_void_star &input_items,
                        gr_vector_void_star &output_items)
{
  const gr_complex *iptr = (const gr_complex *) input_items[0];
  
  gr_complex *optr = (gr_complex *) output_items[0];

  int n_consumed = 0;
  int n_produced = 0;

  std::vector<int> tag_positions;
  int next_tag_position = -1;
  int next_tag_position_index = -1;

  std::vector<tag_t> tags;
  get_tags_in_range(tags, 0, nitems_read(0), nitems_read(0) + ninput_items[0], pmt::mp("first"));
  for(int i=0;i<tags.size();i++) {
      int current;
      current = tags[i].offset - nitems_read(0);
      tag_positions.push_back(current);
      next_tag_position_index = 0;
  }
  if(next_tag_position_index >= 0) {
      next_tag_position = tag_positions[next_tag_position_index];
  }

  for (n_consumed=0; n_consumed<ninput_items[0] && n_consumed<ninput_items[1] && n_produced<noutput_items; n_consumed++) {

    if (next_tag_position == n_consumed) { /* frame_start */
      next_tag_position_index++;
      if (next_tag_position_index == tag_positions.size()) {
        next_tag_position_index = -1;
        next_tag_position = -1;
      }
      else {
        next_tag_position = tag_positions[next_tag_position_index];
      }

      d_start = 1;
      iptr += d_vlen;
    } else {
      if (d_start == 1)
          add_item_tag(0, nitems_written(0) + n_produced, pmt::intern("first"), pmt::intern(""), pmt::intern("ofdm_remove_first_symbol_vcc"));
      n_produced++;
      d_start = 0;
      for (unsigned int j=0; j<d_vlen; j++)
        *optr++ = *iptr++;
    }
  }

  // printf("ninput_items[0]: %d, ninput_items[1]: %d, noutput_items: %d, consumed: %d, produced: %d\n", ninput_items[0], ninput_items[1], noutput_items, n_consumed, n_produced);

  consume_each(n_consumed);
  return n_produced;
}

}
}
