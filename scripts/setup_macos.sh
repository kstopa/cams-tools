#!/usr/bin/env bash

# Copyright 2017 Krzysztof Stopa (stopa.krzysztof.k@gmail.com)

# This file is part of Copernicus Atmosphere Monitoring Service (CAMS) downloading and
# processing tools (CAMS tools).

# CAMS tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later
# version.

# CAMS tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with CAMS tools.  If not, see <http://www.gnu.org/licenses/>.


# Install WGRIB2 (see http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/ )
brew install gcc6
xcode-select --install

wget http://www.ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz
tar -xf wgrib2.tgz
rm wgrib2.tgz
cd grib2
export FC=/usr/local/bin/gfortran-6
export CC=/usr/local/bin/gcc-6
export CXX=/usr/bin/c++
export F77=ifort
export CFLAGS="-O2 -m64"
export CXXFLAGS="-O2 -m64"
export FFLAGS="-O2 -m64"
gmake
## Move to bin folder and add to path
cd ../..
mv ./scripts/grib2 ./bin/
GRIB_PATH=$(pwd)/bin/grib2/wgrib2
echo "# $(date) Added WGRIB2 tool to PATH"   >> $HOME/.bash_profile
echo PATH=\$PATH:${GRIB_PATH} >> $HOME/.bash_profile
. $HOME/.bash_profile

# Python requirements
pip3 install requests

