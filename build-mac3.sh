#!/bin/sh
#
# build-mac3.sh
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
export PYTHONPATH="/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages"
# for Qt4:
export PATH=/Library/Frameworks/Python.framework/Versions/3.4/bin:$PATH
# for Qt5:
#export PATH=/Library/Frameworks/Python.framework/Versions/3.3/bin/:/Users/<username>/Qt5.1.1/5.1.1/clang_64/bin/:$PATH

# ui
find ui -iname "*.ui" | while read f
do
    fullfilename=$(basename $f)
    fn=${fullfilename%.*}
# PyQt5
#    pyuic5 -o uic/${fn}.py --from-imports ui/${fn}.ui
# PyQt4
    pyuic4 -o uic/${fn}.py --from-imports ui/${fn}.ui 
done

# qrc
find qrc -iname "*.qrc" | while read f
do
    fullfilename=$(basename $f)
    fn=${fullfilename%.*}
# PyQt5
#    pyrcc5 -py3 -o uic/${fn}_rc.py qrc/${fn}.qrc 
# PyQt4
    pyrcc4 -py3 -o uic/${fn}_rc.py qrc/${fn}.qrc
done

# translations
# PyQt5
#pylupdate5 conf/tonino.pro
# PyQt4
pylupdate4 conf/tonino.pro
lrelease -verbose conf/tonino.pro

# distribution
rm -rf build dist
python3.4 setup-mac3.py py2app
