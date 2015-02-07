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
