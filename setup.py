#!/usr/bin/env python

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

from distutils.core import setup
import cams

setup(name='CAMS tools',
      version=cams.__version__,
      description='Copernicus Atmosphere Monitoring Service (CAMS) downloading and processing tools',
      author=cams.__author__,
      author_email='stopa.krzysztof.k@gmail.com',
      url='https://github.com/kstopa/cams-tools',
      packages=['cams'], requires=['requests']
      )