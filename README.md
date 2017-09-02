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
useful to convert this data to formats like NetCDF or CSV that are
supported by the majority of GIS software and tools (like GDAL or QGIS).
To add support for GRIB2 format conversion you must to have
[NOAA wgrib2 tool](http://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/),
an utility to read and write grib2 files.
To install the tool just run the setup script for your OS (by now only
Linux and MacOS available (feel free to add Windows script)):

    ./scripts/setup_linux.sh

    or

    ./scripts/setup_macos.sh

## Usage

To be improved. Just type:

    python3 cams.py -h