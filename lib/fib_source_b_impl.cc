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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "fib_source_b_impl.h"

namespace gr {
    namespace dab {

/*///////////////////////////////////////
 * MCI-FIGs, ready to transmit
 *///////////////////////////////////////

        //ensemble info, CIF counter has to increase with each CIF
        const char fib_source_b_impl::ensemble_info[56] = {0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                                                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        // 000 00110 000 00000 0100000000000000 00 0 0000000000000 00000000

        //service orga with number of service components (last 4 bits have to be modified) and without service component descrition (only 1 service with numSubCh of SubChannels)
        const char fib_source_b_impl::service_orga[40] = {0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
                                                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1};
        //000 00110 000 00010 0100000000000000 0 000 0001

        //service_comp_description, has to be added for each service comp to service_orga (with change of Sub_channel ID!!)
        const char fib_source_b_impl::service_comp_description[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0};
        //00 000000 000000 1 0

        //subchannel orga header, length has to be changed according to the number of subchannel-orga fields
        const char fib_source_b_impl::subchannel_orga_header[16] = {0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1};
        //000 00100 000 00001

        //subchannel orga field (bei mehreren subchannels (int numSubCh > 1) wird dieses Array modifiziert)
        const char fib_source_b_impl::subchannel_orga_field[24] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                                                               0, 0, 1, 0, 1};
        // 000000 0000000000 0 0 100101 short form, protection index 37 (140 CUs, Protection level 1, Bit rate 128 kbit/s)

/*////////////////////////////////////////////
 * SI-FIGs, ready to transmit
*/////////////////////////////////////////////
        //Ensemble label (bit 17 changed to 0)
        const char fib_source_b_impl::ensemble_label[176] = {0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
                                                                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1,
                                                                        0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0,
                                                                        0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1,
                                                                        0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1,
                                                                        1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1,
                                                                        0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1,
                                                                        1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1,
                                                                        0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0,
                                                                        0}; // Ensemble label: "__Galaxy_News___"
        //"001 10101  0000 0 000 0100 000000000000 01011111 01011111 01000111 01100001 01101100 01100001 01111000 01111001 01011111 01001110 01100101 01110111 01110011 01011111 01011111 01011111 0011100011111000"; // Ensemble label: "__Galaxy_News___"

        //Programme Service label
        const char fib_source_b_impl::service_label[176] = {0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0,
                                                                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0,
                                                                       0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1,
                                                                       1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1,
                                                                       0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0,
                                                                       0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0,
                                                                       1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1,
                                                                       0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0};
        //001 10101 0000 0 001 0100000000000000 01011111 01000111 01100001 01101100 01100001 01111000 01111001 01011111 01010010 01100001 01100100 01101001 01101111 00110001 01011111 01011111 0111000111100100

        //Programme Service Component label
        const char fib_source_b_impl::service_component_label[184] = {0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                                                                                 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                                                                 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0,
                                                                                 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0,
                                                                                 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0,
                                                                                 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1,
                                                                                 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1,
                                                                                 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1,
                                                                                 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0,
                                                                                 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1};
        //001 10110 0000 0 100 0 000 0000 0100000000000000 01000001 01110111 01100101 01110011 01101111 01101101 01100101 01011111 01001101 01101001 01111000 01011111 01010110 01101111 01101100 00110001 0000000011111111

        //service component language
        const char fib_source_b_impl::service_comp_language[32] = {0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0,
                                                                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
                                                                              0}; //language German
        //"000 00011  0 0 0 00101 0 0 000000 00001000"; //language German

        //SI_pointer array
        const char* fib_source_b_impl::SI_pointer[num_SI] = {ensemble_label, service_label, service_component_label, service_comp_language};
        const int fib_source_b_impl::SI_size[4] = {176, 176, 184, 32};

        fib_source_b::sptr
        fib_source_b::make(int transmission_mode, int number_subchannels, std::string ensemble_label,
                           std::string programme_service_label, std::string service_comp_label) {
            return gnuradio::get_initial_sptr
                    (new fib_source_b_impl(transmission_mode, number_subchannels, ensemble_label,
                                           programme_service_label, service_comp_label));
        }

        /*
         * The private constructor
         */
        fib_source_b_impl::fib_source_b_impl(int transmission_mode, int number_subchannels, std::string ensemble_label,
                                             std::string programme_service_label, std::string service_comp_label)
                : gr::sync_block("fib_source_b",
                                 gr::io_signature::make(0, 0, 0),
                                 gr::io_signature::make(1, 1, sizeof(char))) {
            t_mode = transmission_mode;
            num_subch = number_subchannels;
            nFIBs_written = 0;
            nSI_written = 0;
            if(t_mode != 3) set_output_multiple(FIB_size * 3);
            else set_output_multiple(FIB_size * 4);
        }

        /*
         * Our virtual destructor.
         */
        fib_source_b_impl::~fib_source_b_impl() {
        }

        /*
         * overwrites an integer value to num_bits bits to the num_bits bits before trigger (overwrites default zeros)), e.g. for number of subchannels in ensemble info or
         */
        void fib_source_b_impl::bit_adaption(char *out_ptr, int number, int num_bits) {
            for (int i = 0; i < num_bits; i++) {
                if (pow(2, num_bits-1-i) > number) {
                    out_ptr[i - num_bits] = 0;
                } else {
                    out_ptr[i - num_bits] = 1;
                    number -= pow(2, num_bits-1-i);
                }
            }
        }

        /*
         * calculates the CIF modulo counters and changes the bits in ensemble_info with bit_adaption
         */
        void fib_source_b_impl::CIF_counter(char* out_ptr, int counter) {
            //mod 250 counter
            int mod_250 = counter%250;
            bit_adaption(out_ptr, mod_250, 8);
            //mod 20 counter
            int mod_20 = ((counter-mod_250)/250)%20;
            bit_adaption(out_ptr - 8, mod_20, 5);
        }

        /*
         * converts string to bits and writes it to the stream
         * outputs the number of written bits to update offset
         */
        int fib_source_b_impl::write_label(char *out_ptr, std::string label, int num_chars) {
            for (std::size_t i = 0; i < label.size(); ++i)
            {
                bit_adaption(out_ptr + (i+1) * 8, (int) label.c_str()[i], 8);
            }
            std::size_t written_size = label.size();
            while(written_size < num_chars){//fill rest of label with spaces
                bit_adaption(out_ptr + (written_size+1) * 8, (int) ' ', 8);
                written_size++;
            }
            return 8*num_chars;
        }

        int
        fib_source_b_impl::work(int noutput_items,
                                gr_vector_const_void_star &input_items,
                                gr_vector_void_star &output_items) {
            char *out = (char *) output_items[0];
            offset = 0;

            do {
                if ((nFIBs_written%3 == 0 && t_mode != 3) || (nFIBs_written%3 != 0 && t_mode == 3)) { //only MCI in this FIB when this FIB ist first in Row (Row are 3 FIBs for T_Mode=1,2,4 or 4 FIBs for T_Mode=3)
/*///////////////////////////////////////////////
 * add first FIB with only MCI (max numSubCh = 3)
 *///////////////////////////////////////////////
                    //ensemble info
                    std::memcpy(out + offset, ensemble_info, size_ensemble_info);
                    offset += size_ensemble_info;
                    //increase CIF counter
                    if(t_mode != 3) CIF_counter(out + offset, nFIBs_written/3);
                    else CIF_counter(out + offset, nFIBs_written/4);

                    //service orga
                    std::memcpy(out + offset, service_orga, size_service_orga);
                    offset += size_service_orga;
                    //change number of service components in service_orga (bit manipulation)
                    bit_adaption(out+offset, num_subch, 4);

                    //service component description (numSubCh times; for every sub_channel different, belongs to Service_Orga)
                    for (int subch_count = 0; subch_count < num_subch; subch_count++) {
                        std::memcpy(out + offset,
                                    service_comp_description,
                                    size_service_comp_description); //add numSubCh with default values
                        offset += size_service_comp_description;
                        //change SubChID and priority for all not-primary channels
                        if (subch_count >= 1) { //is it not the first (=secondary) subchannel?
                            out[offset - 2] = 0; //all additional subchannels are secondary
                            //the SubChannel ID has to increase, to be different (count up from zero)
                            bit_adaption(out + offset - 2, subch_count, 6);
                        }
                    }

                    //subchannel orga
                    //subchannel orga header (write only once for all subchannels)
                    std::memcpy(out + offset, subchannel_orga_header, size_subchannel_orga_header);
                    offset += size_subchannel_orga_header;
                    //change length of FIG header according to number of subchannel orga fields that are added
                    bit_adaption(out + offset - 8, num_subch*(size_subchannel_orga_field/8) + 1, 5);
                    //subchannel orga field
                    for (int subch_count = 0; subch_count < num_subch; subch_count++) {//iterate over all subchannels
                        std::memcpy(out + offset + size_subchannel_orga_field * subch_count, subchannel_orga_field,
                                    size_subchannel_orga_field);
                        offset += size_subchannel_orga_field;
                        if (subch_count >= 1) { //change SubChID and Start Address of SubChannel
                            //the SubChannel ID has to increase, to be different
                            bit_adaption(out + offset - 18, subch_count, 6);
                            //the Start Adress of the next subCh is increased about size_subCh = 140
                            bit_adaption(out + offset - 8, size_subch*subch_count, 10);
                        }
                    }
                    //MCI is set, set EndMarker and padding
                    if (FIB_size -16 - offset >= 8) {//add EndMarker (111 11111) if there is minimum one byte left in FIG (FIG without 16 bit crc16)
                        for (int i = 0; i < 8; i++) { //find:: binde FIC.h ein und verwende die konstaten statt FIB_size
                            out[i + offset] = 1;
                        }
                    }
                    offset += 8;
                    while (offset % FIB_size != 0) {//padding (fill rest of FIB with zeroes, as well the last 16 crc bits)
                        out[offset] = 0;
                        offset++;
                    }
                    nFIBs_written++;
                }//first FIB in row (with only MCI) is finished
                else{
/*///////////////////////////////////////////////
 * write a not primary FIB with SI
 *///////////////////////////////////////////////
                    do {//write SI-FIG in FIB
                        std::memcpy(out + offset, SI_pointer[nSI_written], SI_size[nSI_written]); //write SI in FIB
                        offset += SI_size[nSI_written];
                        nSI_written++;
                        if(nSI_written >= num_SI) nSI_written = 0; //iterate over SI_data so every SI gets to be transmitted some time find:: num_SI ersetzten durch sizeof(SI_size)
                    }while(FIB_size-(offset%FIB_size) - 16 >= SI_size[nSI_written]);
                    //FIB is filled, set endmarker and padding
                    if (FIB_size - 16 - (offset%FIB_size) >= 8) {//add EndMarker (111 11111) if there is minimum one byte left in FIG
                        for (int i = 0; i < 8; i++) {
                            out[i + offset] = 1;
                        }
                    }
                    offset += 8;
                    while (offset%FIB_size != 0) {//padding (fill rest of FIB with zeroes, as well the last 16 crc bits)
                        out[offset] = 0;
                        offset++;
                    }

                    if(nSI_written >= num_SI) nSI_written = 0; //iterate over SI_data so every SI gets to be transmitted some time find:: num_SI ersetzten durch sizeof(SI_size)
                    nFIBs_written++;
                }//FIB finished

            }while((nFIBs_written%3 != 0 && t_mode != 3) || (nFIBs_written%4 != 0 && t_mode == 3)); //finished writing a row of FIBs (3 or 4) (number of FIBS for 1 Transmission Frame)

            // Tell runtime system how many output items we produced.
            if(t_mode != 3) return 3 * FIB_size;
            else return 4 * FIB_size;
        }

    } /* namespace dab */
} /* namespace gr */

