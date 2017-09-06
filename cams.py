#!/usr/bin/env python3

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

from enum import Enum
from os import path
from subprocess import call
import datetime
import argparse
import requests
import sys


class Param(Enum):

    @classmethod
    def has_value(cls, value):
        return (any(value == item.value for item in cls))

    @classmethod
    def from_filename(cls, filename):
        for item in cls:
            if item.value in filename:
                return item
        return None


class Model(Param):
    CHIMERE = 'CHIMERE'
    EMEP = 'EMEP'
    ENSEMBLE = 'ENSEMBLE'
    EURAD = 'EURAD'
    LOTOSEUROS = 'LOTOSEUROS'
    MATCH = 'MATCH'
    MOCAGE = 'MOCAGE'
    SILAM = 'SILAM'


class PackageType(Param):
    ANALYSIS = 'ANALYSIS'
    FORECAST = 'FORECAST'
    ANALYSIS_REPORT = 'ANALYSISREPORT'
    FORECAST_REPORT = 'FORECASTREPORT'


class PackageSpecies(Param):
    CO = 'CO'
    NH3 = 'NH3'
    NMVOC = 'NMVOC'
    NO = 'NO'
    NO2 = 'NO2'
    O3 = 'O3'
    PANS = 'PANS'
    PM10 = 'PM10'
    PM25 = 'PM25'
    SO2 = 'SO2'
    BIRCH_POLLEN = 'BIRCHPOLLEN'
    OLIVE_POLLEN = 'OLIVEPOLLEN'
    GRASS_POLLEN = 'GRASSPOLLEN'
    ALL_SPECIES = 'ALLSPECIES'


class PackageLevel(Param):
    SURFACE = 'SURFACE'
    ALL_LEVELS = 'ALLLEVELS'


class Time(Param):
    ANALYSIS_24H1H = '-24H-1H'
    FORECAST_0H24H = '0H24H'
    FORECAST_25H48H = '25H48H'
    FORECAST_49H72H = '49H72H'
    FORECAST_73H96H = '73H96H'
    ALLTIMES = 'ALLTIMES'   # Custom option for download all times (not included in REST API)

    def get_base_time(self):
        if self == Time.ANALYSIS_24H1H:
            return -24
        elif self == Time.FORECAST_0H24H:
            return -1   # Forecast 0H24 includes 0 hour with base analysis.
        elif self == Time.FORECAST_25H48H:
            return 24
        elif self == Time.FORECAST_49H72H:
            return 48
        else:
            return 72

    def get_hours_range(self):
        """
        Get the number of hours available in a time period package. Defacto gets the number of bands in a package.
        Usually 24 but in the case of Time.FORECAST_0H24H it also include a band with base analysis (time 00)
        :return: Number of bands available in a time period package.
        """
        if self == Time.FORECAST_0H24H:
            return 25
        else:
            return 24



class Format(Param):
    GRIB2 = 'GRIB2'
    NETCDF = 'NETCDF'
    TXT = 'TXT'

class Wgrib2Format(Param):
    """
        -netcdf: write data in netcdf format
        -mysql: export data to a mysql database
        -mysql_speed: export data to a mysql database
        -spread: write data for spreadsheets
        -csv: write in column separated values, another one for spreadsheets
        -text: data in text format
        -bin: data native binary floating point
        -ieee: data in big endian IEEE format
        -ijbox: write a rectangular grid of data
        -AAIG: arcinfo ascii grid, GIS
    """
    NETCDF = 'netcdf'
    MYSQL = 'mysql'
    MYSQL_SPEED = 'mysql_speed'
    SPREAD = 'spread'
    CSV = 'csv'
    TEXT = 'text'
    BIN = 'bin'
    IEEE = 'ieee'
    IJBOX = 'ijbox'
    AAIG = 'AAIG'

    def get_file_extension(self):
        if self == Wgrib2Format.NETCDF:
            return 'nc'
        elif self == Wgrib2Format.SPREAD:
            return 'xls'
        elif self == Wgrib2Format.CSV:
            return 'csv'
        elif self == Wgrib2Format.TEXT:
            return 'txt'
        elif self == Wgrib2Format.AAIG:
            return 'asc'
        elif self._is_binary_format():
            return 'bin'
        elif self._is_db_format():
            return 'sql'
        else:
            return ''

    def to_cmd(self):
        return '-{0}'.format(self.value)

    def _is_db_format(self):
        if self == Wgrib2Format.MYSQL or self == Wgrib2Format.MYSQL_SPEED:
            return True
        else:
            return False

    def _is_binary_format(self):
        if self == Wgrib2Format.BIN or self == Wgrib2Format.IEEE or self == Wgrib2Format.IJBOX:
            return True
        else:
            return False


class Downloader:
    _base_url = 'https://download.regional.atmosphere.copernicus.eu/services/CAMS50?'
    _token = '__M0bChV6QsoOFqHz31VRqnpr4GhWPtcpaRy3oeZjBNSg__'
    _licence = 'yes'
    _grid = '0.1'

    @staticmethod
    def download(out_path='./', reference_time=datetime.datetime.now(), model=Model.ENSEMBLE,
                 type=PackageType.FORECAST, species=PackageSpecies.ALL_SPECIES, level=PackageLevel.SURFACE,
                 time=Time.FORECAST_0H24H, data_format=Format.GRIB2):
        """
        Online data relate to data less than 30 days old.
        Forecasts and analyses are available in Grib Edition 2 or/and Netcdf Format depending on the model :
        - Available file format for Ensemble data are Grib Edition 2 and Netcdf.
        - Available file format for partners data are Netcdf only.
        
        Archived data means data older than 30 days old. This Regional Air Quality archive is available since October 1st, 2015.
        Below are a few more particularities about Regional Air Quality Archived production :
        - Forecasts and analyses are currently available in Grib Edition2 format for archived products.
        - Analyses issued from Ensemble model are available FOR ALL SPECIES since March 2016. Before this date, only O3 
        and NO2 species were produced by a sufficient number of models to generate reliable Ensemble products. So please,
        don't use analysis data from other pollutants than O3 and NO2 before March 2016.
        
        Note that archived analyses from partner models could be missing, occasionally, in case of production problems. 
        In such a case, please use Ensemble analyses instead.

        :param out_path: path to the folder where data will be stored.
        :param reference_time: Date of the forecast and analysis production
        :type reference_time: datetime
        :param model: Name of one of the available CAMS atmospheric models
        :type model: Model
        :param type: One of the available package types for analysis or forecast products
        :type type: PackageType
        :param species: One of the available package species (O3, CO, etc.)
        :type species: PackageSpecies
        :param level: Surface or all available levels
        :type level: PackageLevel
        :param time: One of the available analysis or forecast times. ALL TIMES is not available.
        :type time: Time
        :param data_format: Downloaded data output format 
        :type data_format: Format
        :return: Path to the downloaded file or None if error
        """
        # TODO check date and package compatibility
        # Referece date is formatted as YYYY-MM-DDT00:00:00Z
        params = 'token=' + Downloader._token +\
                 '&grid=' + Downloader._grid +\
                 '&model=' + model.value +\
                 '&package={0}_{1}_{2}'.format(type.value, species.value, level.value) +\
                 '&time=' + time.value +\
                 '&referencetime={0}T00:00:00Z'.format(reference_time.strftime("%Y-%m-%d")) +\
                 '&format=' + data_format.value +\
                 '&licence=' + Downloader._licence
        print('Requesting {0}'.format(Downloader._base_url + params))
        resp = requests.get(Downloader._base_url + params, stream=True)
        if 'Content-Disposition' in resp.headers:
            file_name = resp.headers['Content-Disposition'].replace('inline; filename="', '').replace('"', '')
            print('Downloading {0}'.format(file_name))
            down_data = 0
            down_file = path.join(out_path, file_name)
            with open(down_file, "wb") as f:
                for data in resp.iter_content(chunk_size=8192):
                    down_data += len(data)
                    f.write(data)
                    sys.stdout.write("\r{0:.2f} Mb".format(down_data / (1000.0 * 1000.0)))
                print('...done!')
            return down_file
        else:
            print('Wrong request. Requested product may be unavailable for given parameters.')
            return None

    @staticmethod
    def downloadAll(out_path='./', reference_time=datetime.datetime.now(), model=Model.ENSEMBLE,
                    species=PackageSpecies.ALL_SPECIES, level=PackageLevel.SURFACE, data_format=Format.GRIB2):
        down_files = []
        for time in Time:
            package_type = PackageType.FORECAST
            if time == Time.ANALYSIS_24H1H:
                package_type = PackageType.ANALYSIS
            # Ignore all time
            if time != Time.ALLTIMES and species == PackageSpecies.ALL_SPECIES:
                for sp in PackageSpecies:
                    if sp != PackageSpecies.ALL_SPECIES:
                        df = Downloader.download(out_path, reference_time, model, package_type, sp, level, time, data_format)
                        down_files.append(df)
            elif time != Time.ALLTIMES:
                # Download just single specie
                df = Downloader.download(out_path, reference_time, model, package_type, species, level, time, data_format)
                down_files.append(df)
        return down_files

class Converter:

    @staticmethod
    def convert(grib2_in, path_out, format_out=Wgrib2Format.NETCDF):
        time = Time.from_filename(path.basename(grib2_in))
        files = []
        print("Converting {0} to {1}".format(path.basename(grib2_in), format_out.value))
        for hour in range(1, time.get_hours_range() + 1):
            hour_num = hour+time.get_base_time()
            out_filename = grib2_in.replace(time.value, Converter._format_hour(hour_num)).replace('.grib2', '.{0}'.format(format_out.get_file_extension()))
            out_filepath = path.join(path_out, out_filename)
            cmd = ['wgrib2', grib2_in, '-d', str(hour), format_out.to_cmd(), out_filepath]
            # TODO Add error control. Check if wgrib2 worked
            call(cmd)
            files.append(out_filepath)
        return files

    @staticmethod
    def _format_hour(hour):
        if -10 < hour < 0 :
            return '{0}H'.format(hour).replace('-', '-0')
        else:
            return '{:02d}H'.format(hour)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tool for CAMS data forecast and analysis download.')
    parser.add_argument('--model', help='CHIMERE|EMEP|ENSEMBLE|EURAD|LOTOSEUROS|MATCH|MOCAGE|SILAM', default='ENSEMBLE')
    parser.add_argument('--type', help='FORECAST|ANALYSIS|ANALYSISREPORT|FORECASTREPORT', default='FORECAST')
    parser.add_argument('--species', help='CO|NH3|NMVOC|NO|NO2|O3|PANS|PM10|PM25|SO2|BIRCHPOLLEN|OLIVEPOLLEN|GRASSPOLLEN|ALLSPECIES(for analysis and forecast reports only)', default='ALLSPECIES')
    parser.add_argument('--level', help='SURFACE|ALLLEVELS', default='SURFACE')
    parser.add_argument('--time', help='_24H_1H|0H24H|25H48H|49H72H|73H96H', default='ALLTIMES')
    parser.add_argument('--reference', help='Reference date of the forecast formatted as yyyy-mm-dd', default=datetime.date.today().strftime("%Y-%m-%d"))
    parser.add_argument('--format', help='GRIB2|NETCDF|TXT', default='GRIB2')
    parser.add_argument('--out', help='Path to the folder where data will be saved', default='./')
    parser.add_argument('--convert', help='Convert downloaded data with wgrib2 to one of the available formats netcdf|mysql|mysql_speed')
    args = parser.parse_args()
    param_err = ''
    if not Model.has_value(args.model):
        param_err += 'Model, '
    if not PackageType.has_value(args.type):
        param_err += 'Package type, '
    if not PackageSpecies.has_value(args.species):
        param_err += 'Package species, '
    if not PackageLevel.has_value(args.level):
        param_err += 'Package level, '
    # Check time is valid and compatible with package type
    args.time = args.time.replace('_', '-')
    if not Time.has_value(args.time):
        param_err += 'Time, '
    if args.time == Time.ANALYSIS_24H1H.value and 'FORECAST' in args.type:
        print("Changed Package type to {0}".format(PackageType.FORECAST.value))
        args.type = PackageType.ANALYSIS
    # Format
    if not Format.has_value(args.format):
        param_err += 'Format, '
    try:
        reference_date =datetime.datetime.strptime(args.reference, "%Y-%m-%d")
    except ValueError:
        param_err += 'Reference date, '
    if args.convert and not Wgrib2Format.has_value(args.convert):
        param_err += "wgrib2 conversion format, "
    # Download if no errors
    if not param_err:
        model = Model(args.model)
        type = PackageType(args.type)
        species = PackageSpecies(args.species)
        level = PackageLevel(args.level)
        time = Time(args.time)
        out_format = Format(args.format)
        down_files = []
        # Download bulk or single data
        if (species == PackageSpecies.ALL_SPECIES or time == Time.ALLTIMES) and args.format != Format.TXT:
            down_files = Downloader.downloadAll(args.out, reference_date, model, species, level, out_format)
        else:
            df = Downloader.download(args.out, reference_date, Model(args.model),
                                PackageType(args.type), PackageSpecies(args.species), PackageLevel(args.level),
                                Time(args.time), Format(args.format))
            down_files.append(df)
        # Convert
        if args.convert and out_format == Format.GRIB2:
            to_format = Wgrib2Format(args.convert)
            for df in down_files:
                Converter.convert(df, args.out, to_format)


    else:
        print("Error: invalid value for {0}".format(param_err))
        parser.print_help()



