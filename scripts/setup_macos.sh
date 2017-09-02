#!/usr/bin/env bash

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

