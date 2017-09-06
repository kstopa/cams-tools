# Copernicus Atmosphere Monitoring Service (CAMS) downloading and processing tools

Download european regional models with analysis and forecast packages by
using CAMS regional services REST API.

More information is available at [CAMS web site](https://atmosphere.copernicus.eu),
[regional CAMS model page](http://www.regional.atmosphere.copernicus.eu) and the
[API documentation](http://www.regional.atmosphere.copernicus.eu/doc/Guide_Numerical_Data_CAMS_new.pdf)


## Features

This utility includes tools for:

 - CLI or API usage.
 - Download of individual packages.
 - Bulk download.
 - GRIB2 to NetCDF conversion (not implemented yet).

## Installation

If you just want to download the data the only requirement is to have Python 3 and
requests library installed. So just run:

    pip3 install requests

### GRIB2 conversion option installation (Optional)

To work with archived packages (available only in GRIB2 format) it is
useful to convert this data to formats like NetCDF, CSV or ASCII grid
that are supported by the majority of GIS software and tools (like GDAL
or QGIS). To add support for GRIB2 format conversion you must to have
[NOAA wgrib2 tool](http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/),
an utility to read and write grib2 files.

To install the tool just run the setup script for your OS (by now only
Linux and MacOS available (feel free to add Windows script)):

    ./scripts/setup_linux.sh

    or

    ./scripts/setup_macos.sh

For some tricks about wgrib2 tool usage check
[this link](http://www.ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/tricks.wgrib2)

## Usage

To be improved. Just type:

### Downloading data

#### CLI usage

    python3 cams.py -h

#### API usage


### Converting with WGRIB2

If you have installed wgrib2 tool in your system the tool can uses it
to convert CAMS GRIB2 data to other formats by using wgib2 tool.
Currently wgrib2 supports:

- netcdf: write data in netcdf v3 format (or v4 if wgrib2 is compiled with this option. Note that in opposite as default NETCDF support this format **conserves geometry information**.
- mysql: export data to a mysql database
- mysql_speed: export data to a mysql database
- spread: write data for Excel spreadsheets
- csv: write in column separated values, another one for spreadsheets
- text: data in text format
- bin: data native binary floating point
- ieee: data in big endian IEEE format
- ijbox: write a rectangular grid of data
- AAIG: arcinfo ascii grid, GIS

After conversion each analysis or forecast time will be given in
separated file replacing the file name TIME information with the hour
with one leading zero (e.g +0H24H code will be converted to +00H, +01H,
.. , +25H).

#### CLI usage

TODO

#### API usage


## License

Copyright &copy; 2017 Krzysztof Stopa (stopa.krzysztof.k@gmail.com)

This file is part of Copernicus Atmosphere Monitoring Service (CAMS)
downloading and processing tools (CAMS tools).

CAMS tools is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or any
later version.

CAMS tools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with CAMS tools. If not, see <http://www.gnu.org/licenses/>.