
# Install WGRIB2

export FC=gfortran
export CC=gcc
## Download and compile
wget http://www.ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz
tar -xf wgrib2.tgz
cd grib2
make
## Move to bin folder and add to path
cd ../..
mv ./scripts/grib2 ./bin/
GRIB_PATH=$(pwd)/bin/grib2/wgrib2
sudo echo PATH=\$PATH:${GRIB_PATH} >> /etc/environment
export PATH=$PATH:${GRIB_PATH}


# Setup python libs
pip3 install requests