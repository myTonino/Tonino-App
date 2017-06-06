#!/bin/sh
#
# build-rpi3-pi.sh
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


export QT_SELECT="default"
export QTTOOLDIR="/usr/lib/arm-linux-gnueabihf/qt4/bin"
export QTLIBDIR="/usr/lib/arm-linux-gnueabihf"
export QT_PATH=/usr/share/qt4

export QT=/usr/lib/arm-linux-gnueabihf/qt4

rm -f ui/.*.ui
rm -f qrc/.*.qrc

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
lrelease -qt=5 -verbose conf/tonino.pro

# clean build
rm -rf build dist

#pyinstaller 
#    --noconfirm \
#    --clean \
#    --log-level=WARN \
#    -D \
#    tonino-linux.spec
pyinstaller --runtime-hook rthook_pyqt4.py -D -n tonino -y -c --log-level=WARN "tonino.py"

mv dist/tonino dist/tonino.d
mv dist/tonino.d/* dist
rm -rf dist/tonino.d

cp -R /usr/local/lib/python2.7/dist-packages/matplotlib/mpl-data/ dist
rm -rf dist/mpl-data/sample_data
cp conf/tonino-toni.xml dist
cp -R icons dist
cp doc/README.txt dist
cp doc/LICENSE.txt dist
mkdir dist/includes
mkdir dist/includes/linux
cp includes/tonino-*.hex dist/includes
cp includes/tinyTonino-*.hex dist/includes
## sudo apt-get install avrdude
cp /usr/bin/avrdude dist/includes/linux
cp /etc/avrdude.conf dist/includes/linux
cp conf/qt.conf dist
mkdir dist/translations
cp translations/*.qm dist/translations
cp $QT_PATH/translations/qt_de.qm dist/translations
cp $QT_PATH/translations/qt_es.qm dist/translations
cp $QT_PATH/translations/qt_fr.qm dist/translations
#cp $QT_PATH/translations/qt_it.qm dist/translations



## generate the .deb package

cp raspbian/DEBIAN/control debian/DEBIAN/
VERSION=$(python -c 'import lib; print(lib.__version__)')
NAME=tonino-linux-${VERSION}

# fix debian/DEBIAN/control _VERSION_
sed -i "s/_VERSION_/${VERSION}/g" debian/DEBIAN/control


# prepare debian directory

cp doc/changelog debian/usr/share/doc/tonino
cp doc/copyright debian/usr/share/doc/tonino
cp doc/tonino.1 debian/usr/share/man/man1/tonino.1

rm -f debian/usr/share/man/man1/tonino.1.gz
gzip -9 debian/usr/share/man/man1/tonino.1
chmod +r debian/usr/share/man/man1/tonino.1.gz
rm -f debian/usr/share/doc/tonino/changelog.gz
gzip -9 debian/usr/share/doc/tonino/changelog
chmod +r debian/usr/share/doc/tonino/changelog.gz

chmod +r debian/usr/share/applications/tonino.desktop
chmod -x debian/usr/share/applications/tonino.desktop
chmod +rx debian/usr/bin/tonino
chmod -R +r dist
chmod +x dist/icons

# buid .deb package (into /usr/share)

tar -cf dist-rpi.tar dist
rm -rf debian/usr/share/tonino
tar -xf dist-rpi.tar -C debian/usr/share
mv debian/usr/share/dist debian/usr/share/tonino
find debian -name .svn -exec rm -rf {} \; > /dev/null 2>&1
chown -R root:root debian
chmod -R go-w debian
rm ${NAME}_raspbian-jessie.deb
chmod 755 debian/DEBIAN
chmod 755 debian/DEBIAN/postinst
chmod 755 debian/DEBIAN/prerm
dpkg-deb --build debian ${NAME}_raspbian-jessie-py2.deb

