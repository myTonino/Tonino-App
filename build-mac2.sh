#!/bin/sh
#
# build-mac2.sh
#
# Copyright (c) 2014, Paul Holleis, Marko Luther
# All rights reserved.
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

export MACOSX_DEPLOYMENT_TARGET=10.6
export PYTHONPATH="/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages"
export PATH=/Library/Frameworks/Python.framework/Versions/2.7/bin/:$PATH

# ui
find ui -iname "*.ui" | while read f
do
    fullfilename=$(basename $f)
    fn=${fullfilename%.*}
    pyuic4 -o uic/${fn}.py --from-imports ui/${fn}.ui 
done

# qrc
find qrc -iname "*.qrc" | while read f
do
    fullfilename=$(basename $f)
    fn=${fullfilename%.*}
    pyrcc4 -o uic/${fn}_rc.py qrc/${fn}.qrc 
done

# translations
pylupdate4 conf/tonino.pro
lrelease -verbose conf/tonino.pro

# distribution
rm -rf build dist
python setup-mac2.py py2app
