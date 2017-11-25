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


from os import path
import datetime
import requests
import sys

from cams.core import Param

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
        if time == Time.ANALYSIS_24H1H:
            type = PackageType.ANALYSIS
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
                        if df is not None:
                            down_files.append(df)
            elif time != Time.ALLTIMES:
                # Download just single specie
                df = Downloader.download(out_path, reference_time, model, package_type, species, level, time, data_format)
                if df is not None:
                    down_files.append(df)
        return down_files




