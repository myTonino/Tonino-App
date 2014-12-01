#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tonino.py
#
# Copyright (c) 2014, Paul Holleis, Marko Luther
# All rights reserved.
# 
#
# ABOUT
#
# This program allows to configure the Tonino roast color analyzer
#
# 
# LICENSE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Start the application.
"""

import sys
import os
# supress any console/error-log output on all platforms, but Mac OS X
if not sys.platform.startswith("darwin"):
   sys.stderr = sys.stdout = os.devnull

from lib import main

if __name__ == '__main__':
    main.main()


# EOF
