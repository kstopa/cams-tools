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

import argparse
import datetime

from cams.regional import PackageSpecies, Model, PackageLevel, Time, PackageType, Format, Downloader
from cams.tools import Converter, Wgrib2Format


def main():
    parser = argparse.ArgumentParser(description='Tool for CAMS data forecast and analysis download.')
    parser.add_argument('--model', help='CHIMERE|EMEP|ENSEMBLE|EURAD|LOTOSEUROS|MATCH|MOCAGE|SILAM', default='ENSEMBLE')
    parser.add_argument('--type', help='FORECAST|ANALYSIS|ANALYSISREPORT|FORECASTREPORT', default='FORECAST')
    parser.add_argument('--species',
                        help='CO|NH3|NMVOC|NO|NO2|O3|PANS|PM10|PM25|SO2|BIRCHPOLLEN|OLIVEPOLLEN|GRASSPOLLEN|ALLSPECIES(for analysis and forecast reports only)',
                        default='ALLSPECIES')
    parser.add_argument('--level', help='SURFACE|ALLLEVELS', default='SURFACE')
    parser.add_argument('--time', help='_24H_1H|0H24H|25H48H|49H72H|73H96H', default='ALLTIMES')
    parser.add_argument('--reference', help='Reference date of the forecast formatted as yyyy-mm-dd',
                        default=datetime.date.today().strftime("%Y-%m-%d"))
    parser.add_argument('--format', help='GRIB2|NETCDF|TXT', default='GRIB2')
    parser.add_argument('--out', help='Path to the folder where data will be saved', default='./')
    parser.add_argument('--convert',
                        help='Convert downloaded data with wgrib2 to one of the available formats netcdf|mysql|mysql_speed')
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
        reference_date = datetime.datetime.strptime(args.reference, "%Y-%m-%d")
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
                time = Time.from_filename(path.basename(df))
                Converter.convert(df, args.out, time, to_format)
        return 0
    else:
        print("Error: invalid value for {0}".format(param_err))
        parser.print_help()
        return -1

if __name__ == '__main__':
    main()

