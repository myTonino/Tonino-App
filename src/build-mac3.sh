#!/bin/sh
#
# build-mac3.sh
#
# Copyright (c) 202022, Paul Holleis, Marko Luther
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

export MACOSX_DEPLOYMENT_TARGET=11.0
export PYTHON=/Library/Frameworks/Python.framework/Versions/3.11

export PYTHONPATH=$PYTHON/lib/python3.11/site-packages

export PATH=$PYTHON/bin:$PYTHON:/lib:$PATH

#export QT_PATH=~/Qt/6.5.3/macos
export QT_PATH=${PYTHONPATH}/PyQt6/Qt6

QTTOOLS=qt6-tools

export PATH=$PATH:$QT_PATH/bin:$QT_PATH/lib
#export DYLD_FRAMEWORK_PATH=$QT_PATH/lib # this works only if Qt version of PyQt is the same as in QT_PATH

# ui
find ui -iname "*.ui" | while read f
do
    fullfilename=$(basename $f)
    fn=${fullfilename%.*}
# PyQt6
    pyuic6 -o uic/${fn}.py -x ui/${fn}.ui
# PyQt5
#    pyuic5 -o uic/${fn}.py --from-imports ui/${fn}.ui
# PyQt4
#    pyuic4 -o uic/${fn}.py --from-imports ui/${fn}.ui
done

# qrc
# NOT AVAILABLE ON PyQt6
#find qrc -iname "*.qrc" | while read f
#do
#    fullfilename=$(basename $f)
#    fn=${fullfilename%.*}
# PyQt5
#    pyrcc5 -o uic/${fn}_rc.py qrc/${fn}.qrc
#done

# translations
# PyQt6
./pylupdate6pro conf/tonino.pro

#$QT_PATH/bin/lrelease -verbose conf/tonino.pro
$QTTOOLS lrelease -verbose translations/*.ts


# distribution
rm -rf build dist
$PYTHON/bin/python3 setup_mac3.py py2app
