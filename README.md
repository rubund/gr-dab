gr-dab
======

```
 gr-dab - GNU Radio Digital Audio Broadcasting module
 Copyright (C) Andreas Müller, 2011, Moritz Luca Schmid, 2017

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
```


This directory (and the resulting tarball) contains a build tree for
gr-dab.

gr-dab contains everything needed to get audio from DAB and DAB+

Much of the code was developed as part of "Google Summer of Code 2017" by
Moritz Luca Schmid. (the completion of audio reception of DAB and DAB+).
His fork can be found here: https://github.com/kit-cel/gr-dab The fork also
contains everything needed for transmission of DAB radio. It does however have
a number of external dependencies which makes it slightly more tricky to
install than this version without TX.

This package requires that gnuradio-core is already installed.  It
also depends on some GNU Radio prerequisites, such as Boost and
cppunit. Additionally it depends on the FAAD2 library. (ubuntu: sudo apt-get
install libfaad-dev, fedora: sudo dnf install faad2-devel)

To build the examples from the tarball run these commands:

```
  $ mkdir build
  $ cd build
  $ cmake ../
  $ make
  $ sudo make install
  $ sudo ldconfig
```


User guide for the utility **grdab**
------------------------------------

All SDRs supported by gr-osmosdr and which can tune to the DAB frequencies can be used with grdab. grdab currently only supports DAB+


#### "Calibration":

When connecting a new radio, run:

```
grdab adjust
```

This will bring up a GUI where you will see the frequency spectrum and the constellation diagram.

1. Drag the channel selector to a valid DAB+ frequency in your area.
2. Adjust the gain sliders such that frequency looks good.
3. Adjust the ppm slider until the constellation diagram consists of 4 quite confined dots.
4. Then click 'save configuration'
5. Your SDR is now tuned.

Whenever connecting another SDR, you will have to repeat the adjustment procedure above.

#### Check available channels:

To see what channels are available on a chosen frequency, run:

```
grdab info -f <frequency_in_mhz>
```

#### Listen to DAB+:

When you find a channel you can receive audio with:

```
grdab receive -f 227.360 --bit_rate 80 --address 204 --subch_size 60 --protect_level 2 --audiorate 48000
```

Where you replace the different options with the output from *grdab info* for the desired channel. You might have to experiment with a few values for *--audiorate* such as 44100 or 48000.
