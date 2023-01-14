#!/bin/sh
#
# build-ubuntu.sh
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

QT=/usr/local/Qt-5.4.2/

# ui
find ui -iname "*.ui" | while read f
do
    fullfilename=$(basename $f)
    fn=${fullfilename%.*}
# PyQt5
    pyuic5 -o uic/${fn}.py --from-imports ui/${fn}.ui
# PyQt4
#    pyuic4 -o uic/${fn}.py --from-imports ui/${fn}.ui
done

# qrc
find qrc -iname "*.qrc" | while read f
do
    fullfilename=$(basename $f)
    fn=${fullfilename%.*}
# PyQt5
    pyrcc5 -o uic/${fn}_rc.py qrc/${fn}.qrc
# PyQt4
#    pyrcc4 -o uic/${fn}_rc.py qrc/${fn}.qrc
done

# translations
# PyQt5
pylupdate5 conf/tonino.pro
# PyQt4
#pylupdate4 conf/tonino.pro

lrelease -verbose conf/tonino.pro

# distribution
rm -rf dist
bbfreeze tonino.py
cp -L /usr/lib/i386-linux-gnu/libxml2.so.2 dist
patchelf --set-rpath '${ORIGIN}:${ORIGIN}/../lib' dist/libxml2.so.2
cp -L /usr/lib/libicudata.so.48 dist
patchelf --set-rpath '${ORIGIN}:${ORIGIN}/../lib' dist/libicudata.so.48
cp -L /usr/lib/libicuuc.so.48 dist
patchelf --set-rpath '${ORIGIN}:${ORIGIN}/../lib' dist/libicuuc.so.48
cp -L /usr/lib/libicui18n.so.48 dist
patchelf --set-rpath '${ORIGIN}:${ORIGIN}/../lib' dist/libicui18n.so.48
cp -L /usr/lib/i386-linux-gnu/pkcs11/gnome-keyring-pkcs11.so dist
patchelf --set-rpath '${ORIGIN}:${ORIGIN}/../lib' dist/gnome-keyring-pkcs11.so
cp -R /usr/local/lib/python2.7/dist-packages/matplotlib/mpl-data/ dist
cp conf/tonino-toni.xml dist
cp -R icons dist
cp doc/README.txt dist
cp doc/LICENSE.txt dist
mkdir dist/Resources
mkdir dist/Resources/qt_plugins
mkdir dist/Resources/qt_plugins/imageformats
mkdir dist/Resources/qt_plugins/iconengines
mkdir dist/Resources/qt_plugins/platforms
mkdir dist/Resources/qt_plugins/platformthemes
mkdir dist/includes
mkdir dist/includes/linux
cp includes/tonino-*.hex dist/includes
cp includes/tinyTonino-*.hex dist/includes
cp includes/linux/* dist/includes/linux
cp $QT/plugins/imageformats/libqsvg.so dist/Resources/qt_plugins/imageformats
patchelf --set-rpath '${ORIGIN}/../../..:${ORIGIN}/../../../../lib' dist/Resources/qt_plugins/imageformats/libqsvg.so
cp $QT/plugins/imageformats/libqgif.so dist/Resources/qt_plugins/imageformats
patchelf --set-rpath '${ORIGIN}/../../..:${ORIGIN}/../../../../lib' dist/Resources/qt_plugins/imageformats/libqgif.so
#cp $QT/plugins/imageformats/libqjpeg.so dist/Resources/qt_plugins/imageformats
#patchelf --set-rpath '${ORIGIN}/../../..:${ORIGIN}/../../../../lib' dist/Resources/qt_plugins/imageformats/libqjpeg.so
#cp $QT/plugins/imageformats/libqtiff.so dist/Resources/qt_plugins/imageformats
#patchelf --set-rpath '${ORIGIN}/../../..:${ORIGIN}/../../../../lib' dist/Resources/qt_plugins/imageformats/libqtiff.so
cp $QT/plugins/iconengines/libqsvgicon.so dist/Resources/qt_plugins/iconengines
patchelf --set-rpath '${ORIGIN}/../../..:${ORIGIN}/../../../../lib' dist/Resources/qt_plugins/iconengines/libqsvgicon.so
cp $QT/plugins/platforms/libqxcb.so dist/Resources/qt_plugins/platforms
patchelf --set-rpath '${ORIGIN}/../../..:${ORIGIN}/../../../../lib' dist/Resources/qt_plugins/platforms/libqxcb.so
cp $QT/plugins/platformthemes/libqgtk2.so dist/Resources/qt_plugins/platformthemes
patchelf --set-rpath '${ORIGIN}/../../..:${ORIGIN}/../../../../lib' dist/Resources/qt_plugins/platformthemes/libqgtk2.so
cp conf/qt.conf dist
mkdir dist/translations
cp translations/*.qm dist/translations
cp $QT/translations/qt_de.qm dist/translations
cp $QT/translations/qt_es.qm dist/translations
cp $QT/translations/qt_fr.qm dist/translations
cp $QT/translations/qt_it.qm dist/translations
tar -cf dist-ubuntu.tar dist
