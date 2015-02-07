/* -*- c++ -*- */

#define DAB_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "dab_swig_doc.i"

%{
#include "dab/moving_sum_ff.h"
#include "dab/ofdm_ffe_all_in_one.h"
%}


%include "dab/moving_sum_ff.h"
GR_SWIG_BLOCK_MAGIC2(dab, moving_sum_ff);
%include "dab/ofdm_ffe_all_in_one.h"
GR_SWIG_BLOCK_MAGIC2(dab, ofdm_ffe_all_in_one);
