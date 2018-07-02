/* -*- c++ -*- */

#define DAB_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "dab_swig_doc.i"

%{
#include "dab/moving_sum_ff.h"
#include "dab/ofdm_ffe_all_in_one.h"
#include "dab/ofdm_sampler.h"
#include "dab/ofdm_coarse_frequency_correct.h"
#include "dab/diff_phasor_vcc.h"
#include "dab/ofdm_remove_first_symbol_vcc.h"
#include "dab/frequency_interleaver_vcc.h"
#include "dab/qpsk_demapper_vcb.h"
#include "dab/complex_to_interleaved_float_vcf.h"
#include "dab/modulo_ff.h"
#include "dab/measure_processing_rate.h"
#include "dab/select_vectors.h"
#include "dab/repartition_vectors.h"
#include "dab/unpuncture_vff.h"
#include "dab/prune_vectors.h"
#include "dab/fib_sink_vb.h"
#include "dab/estimate_sample_rate_bf.h"
#include "dab/fractional_interpolator_triggered_update_cc.h"
#include "dab/magnitude_equalizer_vcc.h"
#include "dab/qpsk_mapper_vbc.h"
#include "dab/ofdm_insert_pilot_vcc.h"
#include "dab/sum_phasor_trig_vcc.h"
#include "dab/ofdm_move_and_insert_zero.h"
#include "dab/insert_null_symbol.h"
#include "dab/time_interleave_bb.h"
#include "dab/time_deinterleave_ff.h"
#include "dab/crc16_bb.h"
#include "dab/fib_source_b.h"
#include "dab/select_subch_vfvf.h"
#include "dab/unpuncture_ff.h"
#include "dab/prune.h"
#include "dab/firecode_check_bb.h"
#include "dab/puncture_bb.h"
#include "dab/dab_transmission_frame_mux_bb.h"
#include "dab/conv_encoder_bb.h"
#include "dab/mapper_bc.h"
#include "dab/mp2_decode_bs.h"
#include "dab/mp4_decode_bs.h"
#include "dab/reed_solomon_decode_bb.h"
#include "dab/reed_solomon_encode_bb.h"
#include "dab/valve_ff.h"
#include "dab/peak_detector_fb.h"
#include "dab/control_stream_to_tag_cc.h"
%}


%include "dab/moving_sum_ff.h"
GR_SWIG_BLOCK_MAGIC2(dab, moving_sum_ff);
%include "dab/ofdm_ffe_all_in_one.h"
GR_SWIG_BLOCK_MAGIC2(dab, ofdm_ffe_all_in_one);
%include "dab/ofdm_sampler.h"
GR_SWIG_BLOCK_MAGIC2(dab, ofdm_sampler);
%include "dab/ofdm_coarse_frequency_correct.h"
GR_SWIG_BLOCK_MAGIC2(dab, ofdm_coarse_frequency_correct);
%include "dab/diff_phasor_vcc.h"
GR_SWIG_BLOCK_MAGIC2(dab, diff_phasor_vcc);
%include "dab/ofdm_remove_first_symbol_vcc.h"
GR_SWIG_BLOCK_MAGIC2(dab, ofdm_remove_first_symbol_vcc);
%include "dab/frequency_interleaver_vcc.h"
GR_SWIG_BLOCK_MAGIC2(dab, frequency_interleaver_vcc);
%include "dab/qpsk_demapper_vcb.h"
GR_SWIG_BLOCK_MAGIC2(dab, qpsk_demapper_vcb);
%include "dab/complex_to_interleaved_float_vcf.h"
GR_SWIG_BLOCK_MAGIC2(dab, complex_to_interleaved_float_vcf);
%include "dab/modulo_ff.h"
GR_SWIG_BLOCK_MAGIC2(dab, modulo_ff);
%include "dab/measure_processing_rate.h"
GR_SWIG_BLOCK_MAGIC2(dab, measure_processing_rate);
%include "dab/select_vectors.h"
GR_SWIG_BLOCK_MAGIC2(dab, select_vectors);
%include "dab/repartition_vectors.h"
GR_SWIG_BLOCK_MAGIC2(dab, repartition_vectors);
%include "dab/unpuncture_vff.h"
GR_SWIG_BLOCK_MAGIC2(dab, unpuncture_vff);
%include "dab/prune_vectors.h"
GR_SWIG_BLOCK_MAGIC2(dab, prune_vectors);
%include "dab/fib_sink_vb.h"
GR_SWIG_BLOCK_MAGIC2(dab, fib_sink_vb);
%include "dab/estimate_sample_rate_bf.h"
GR_SWIG_BLOCK_MAGIC2(dab, estimate_sample_rate_bf);
%include "dab/fractional_interpolator_triggered_update_cc.h"
GR_SWIG_BLOCK_MAGIC2(dab, fractional_interpolator_triggered_update_cc);
%include "dab/magnitude_equalizer_vcc.h"
GR_SWIG_BLOCK_MAGIC2(dab, magnitude_equalizer_vcc);
%include "dab/qpsk_mapper_vbc.h"
GR_SWIG_BLOCK_MAGIC2(dab, qpsk_mapper_vbc);
%include "dab/ofdm_insert_pilot_vcc.h"
GR_SWIG_BLOCK_MAGIC2(dab, ofdm_insert_pilot_vcc);
%include "dab/sum_phasor_trig_vcc.h"
GR_SWIG_BLOCK_MAGIC2(dab, sum_phasor_trig_vcc);
%include "dab/ofdm_move_and_insert_zero.h"
GR_SWIG_BLOCK_MAGIC2(dab, ofdm_move_and_insert_zero);
%include "dab/insert_null_symbol.h"
GR_SWIG_BLOCK_MAGIC2(dab, insert_null_symbol);
%include "dab/time_interleave_bb.h"
GR_SWIG_BLOCK_MAGIC2(dab, time_interleave_bb);
%include "dab/time_deinterleave_ff.h"
GR_SWIG_BLOCK_MAGIC2(dab, time_deinterleave_ff);
%include "dab/crc16_bb.h"
GR_SWIG_BLOCK_MAGIC2(dab, crc16_bb);
%include "dab/fib_source_b.h"
GR_SWIG_BLOCK_MAGIC2(dab, fib_source_b);
%include "dab/select_subch_vfvf.h"
GR_SWIG_BLOCK_MAGIC2(dab, select_subch_vfvf);
%include "dab/unpuncture_ff.h"
GR_SWIG_BLOCK_MAGIC2(dab, unpuncture_ff);
%include "dab/prune.h"
GR_SWIG_BLOCK_MAGIC2(dab, prune);
%include "dab/firecode_check_bb.h"
GR_SWIG_BLOCK_MAGIC2(dab, firecode_check_bb);
%include "dab/puncture_bb.h"
GR_SWIG_BLOCK_MAGIC2(dab, puncture_bb);
%include "dab/dab_transmission_frame_mux_bb.h"
GR_SWIG_BLOCK_MAGIC2(dab, dab_transmission_frame_mux_bb);
%include "dab/conv_encoder_bb.h"
GR_SWIG_BLOCK_MAGIC2(dab, conv_encoder_bb);
%include "dab/mapper_bc.h"
GR_SWIG_BLOCK_MAGIC2(dab, mapper_bc);

%include "dab/mp2_decode_bs.h"
GR_SWIG_BLOCK_MAGIC2(dab, mp2_decode_bs);

%include "dab/mp4_decode_bs.h"
GR_SWIG_BLOCK_MAGIC2(dab, mp4_decode_bs);
%include "dab/reed_solomon_decode_bb.h"
GR_SWIG_BLOCK_MAGIC2(dab, reed_solomon_decode_bb);
%include "dab/reed_solomon_encode_bb.h"
GR_SWIG_BLOCK_MAGIC2(dab, reed_solomon_encode_bb);


%include "dab/valve_ff.h"
GR_SWIG_BLOCK_MAGIC2(dab, valve_ff);
%include "dab/peak_detector_fb.h"
GR_SWIG_BLOCK_MAGIC2(dab, peak_detector_fb);
%include "dab/control_stream_to_tag_cc.h"
GR_SWIG_BLOCK_MAGIC2(dab, control_stream_to_tag_cc);
