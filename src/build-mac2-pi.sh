#!/bin/sh
#
# build-mac2-pi.sh
#
# Copyright (c) 2016, Paul Holleis, Marko Luther
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

export MACOSX_DEPLOYMENT_TARGET=10.7

export PYTHON=/Library/Frameworks/Python.framework/Versions/2.7
export PYTHONPATH=$PYTHON/lib/python2.7/site-packages
export QT_PATH=~/Qt5.4.2/5.4/clang_64

export PATH=$PYTHON/bin:$PYTHON/lib:$PATH
export PATH=$QT_PATH/bin:$QT_PATH/lib:$PATH
#export DYLD_FRAMEWORK_PATH=$QT_PATH/lib


# ui
find ui -iname "*.ui" | while read f
do
    fullfilename=$(basename $f)
    fn=${fullfilename%.*}
    pyuic5 -o uic/${fn}.py --from-imports ui/${fn}.ui
done

# qrc
find qrc -iname "*.qrc" | while read f
do
    fullfilename=$(basename $f)
    fn=${fullfilename%.*}
    pyrcc5 -o uic/${fn}_rc.py qrc/${fn}.qrc 
done

# translations
$PYTHON/bin/pylupdate5 conf/tonino.pro
$QT_PATH/bin/lrelease -verbose conf/tonino.pro

# distribution
rm -rf build dist

pyinstaller --noconfirm \
    --clean \
    --log-level=WARN \
    --osx-bundle-identifier=com.tonino \
    --windowed \
    tonino.spec


# copy translations
mkdir dist/Tonino.app/Contents/Resources/translations
cp $QT_PATH/translations/qt_de.qm dist/Tonino.app/Contents/Resources/translations
cp $QT_PATH/translations/qt_es.qm dist/Tonino.app/Contents/Resources/translations
cp $QT_PATH/translations/qt_fr.qm dist/Tonino.app/Contents/Resources/translations
cp translations/tonino_??.qm dist/Tonino.app/Contents/Resources/translations

# copy firmware and file icon
cp includes/mac/avrdude.conf dist/Tonino.app/Contents/Resources
cp includes/mac/avrdude dist/Tonino.app/Contents/Resources
cp includes/*.hex dist/Tonino.app/Contents/Resources
cp icons/tonino_doc.icns dist/Tonino.app/Contents/Resources

cp doc/README.txt dist
cp doc/LICENSE.txt dist
mkdir dist/scales
cp scales/*.toni dist/scales

# remove the executable 
rm dist/Tonino

$PYTHON/bin/python create_dmg.py