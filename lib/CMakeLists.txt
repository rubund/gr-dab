# Copyright 2011,2012 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIRS})

list(APPEND dab_sources
    moving_sum_ff_impl.cc
    ofdm_ffe_all_in_one_impl.cc
    ofdm_sampler_impl.cc
    ofdm_coarse_frequency_correct_impl.cc
    diff_phasor_vcc_impl.cc
    ofdm_remove_first_symbol_vcc_impl.cc
    frequency_interleaver_vcc_impl.cc
    qpsk_demapper_vcb_impl.cc
    complex_to_interleaved_float_vcf_impl.cc
    modulo_ff_impl.cc
)

set(dab_sources "${dab_sources}" PARENT_SCOPE)
if(NOT dab_sources)
	MESSAGE(STATUS "No C++ sources... skipping lib/")
	return()
endif(NOT dab_sources)

add_library(gnuradio-dab SHARED ${dab_sources})
target_link_libraries(gnuradio-dab ${Boost_LIBRARIES} ${GNURADIO_ALL_LIBRARIES})
set_target_properties(gnuradio-dab PROPERTIES DEFINE_SYMBOL "gnuradio_dab_EXPORTS")

if(APPLE)
    set_target_properties(gnuradio-dab PROPERTIES
        INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib"
    )
endif(APPLE)

########################################################################
# Install built library files
########################################################################
install(TARGETS gnuradio-dab
    LIBRARY DESTINATION lib${LIB_SUFFIX} # .so/.dylib file
    ARCHIVE DESTINATION lib${LIB_SUFFIX} # .lib file
    RUNTIME DESTINATION bin              # .dll file
)

########################################################################
# Build and register unit test
########################################################################
include(GrTest)

include_directories(${CPPUNIT_INCLUDE_DIRS})

list(APPEND test_dab_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/test_dab.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/qa_dab.cc
)

add_executable(test-dab ${test_dab_sources})

target_link_libraries(
  test-dab
  ${GNURADIO_RUNTIME_LIBRARIES}
  ${Boost_LIBRARIES}
  ${CPPUNIT_LIBRARIES}
  gnuradio-dab
)

GR_ADD_TEST(test_dab test-dab)
