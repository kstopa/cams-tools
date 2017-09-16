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
from subprocess import call

from cams.core import Param


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


class Converter:

    @staticmethod
    def convert(grib2_path, path_out, time, format_out=Wgrib2Format.NETCDF):
        """

        :param grib2_in: Grib2 file to be converted
        :param path_out: Output path where each avaiable time (individual grid) will be save.
        :param time: Reference time of the grib2 forecast. Can be get using Time.from_file() method.
        :type time: Time
        :param format_out: One of the ava
        :return:
        """
        files = []
        print("Converting {0} to {1}".format(grib2_path, format_out.value))
        for hour in range(1, time.get_hours_range() + 1):
            hour_num = hour+time.get_base_time()
            out_filename = path.basename(grib2_path).replace(time.value, Converter._format_hour(hour_num)).replace('.grib2', '.{0}'.format(format_out.get_file_extension()))
            out_filepath = path.join(path_out, out_filename)
            cmd = ['wgrib2', grib2_path, '-d', str(hour), format_out.to_cmd(), out_filepath]
            # TODO Add error control. Check if wgrib2 worked
            call(cmd)
            files.append(out_filepath)
        return files

    @staticmethod
    def _format_hour(hour):
        if -10 < hour < 0:
            return '{0}H'.format(hour).replace('-', '-0')
        else:
            return '{:02d}H'.format(hour)

