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

#ifndef INCLUDED_DAB_FIB_SOURCE_B_IMPL_H
#define INCLUDED_DAB_FIB_SOURCE_B_IMPL_H

#include <dab/fib_source_b.h>

namespace gr {
  namespace dab {

    class fib_source_b_impl : public fib_source_b
    {
     private:
        int t_mode; //transmission mode
        int offset; //offset for writing info to FIBs
        uint16_t nFIBs_written; //FIBs totally written
        void bit_adaption(char* out_ptr, int number, int num_bits); //writes an integer value to num_bits bits, beginning at (overwrites default zeros)

        //Multiplex Channel Info
        const static int size_subch = 140; //see Table 6, Index 37, important for calculation of startAdress of SubCh in CIF (subchannel_orga)
        int num_subch; //number of subchannels
        const static char ensemble_info[56]; //CIF counter changes every FIB
        const static int size_ensemble_info = 56;
        void CIF_counter(char* out_ptr, int counter);//implementation of the mod 20 and mod 250 counter
        const static char service_orga[40]; //const
        const static int size_service_orga = 40;
        const static char service_comp_description[16]; //*numSubCh
        const static int size_service_comp_description = 16;
        const static char subchannel_orga_header[16]; //const
        const static int size_subchannel_orga_header = 16;
        const static char subchannel_orga_field[24]; //*numSubCh
        const static int size_subchannel_orga_field = 24;

        //Service Information
        static char def_ensemble_label[176]; //21*8+8, ensemble label (FIG 1/0)
        const static int size_ensemble_label = 176;
        static char def_programme_service_label[176]; //21*8+8, service label (FIG 1/0)
        const static int size_service_label = 176;
        static char def_service_comp_label[184]; //21*8+8, service component label (FIG 1/0)
        const static int size_service_comp_label = 184;
        const static char def_service_comp_language[32]; //3*8+8, service component language; short form (FIG 0/5)
        const static int size_service_comp_language = 32;
        const static int num_SI = 2; //SI without SI from subchannels
        const static char* SI_pointer[num_SI]; //pointer to iterate the SI data in non-primary FIBs, saves the start adress from each SI_Array
        const static int SI_size[num_SI]; //Saves the lengths of the SI_Arrays
        const static int num_SI_subch = 2; //SI without SI from subchannels
        const static char* SI_subch_pointer[num_SI_subch]; //pointer to iterate the SI data in non-primary FIBs, saves the start adress from each SI_Array
        const static int SI_subch_size[num_SI_subch]; //Saves the lengths of the SI_Arrays
        int nSI_written;
        int write_label(char* out_ptr, std::string label, int num_chars = 16);//default for 16 characters (16 byte)

     public:
      fib_source_b_impl(int transmission_mode, int number_subchannels, std::string ensemble_label, std::string programme_service_label, std::string service_comp_label);
      ~fib_source_b_impl();

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);
    };

  } // namespace dab
} // namespace gr

#endif /* INCLUDED_DAB_FIB_SOURCE_B_IMPL_H */

