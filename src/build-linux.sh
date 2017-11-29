#!/bin/sh
#
# build-linux.sh
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

VERSION=$(python -c 'import lib; print(lib.__version__)')
NAME=tonino-linux-${VERSION}
RPM_NAME=tonino-${VERSION}
DEB_NAME=tonino-${VERSION}

# fix debian/DEBIAN/control _VERSION_
sed -i "s/_VERSION_/${VERSION}/g" debian/DEBIAN/control


# prepare debian directory

cp doc/changelog debian/usr/share/doc/tonino
cp doc/copyright debian/usr/share/doc/tonino
cp doc/tonino.1 debian/usr/share/man/man1/tonino.1

gzip -9 debian/usr/share/man/man1/artisan.1
gzip -9 debian/usr/share/doc/artisan/changelog


# build CentOS x86_64 .rpm

rm -rf debian/usr/share/tonino
tar -xf dist-centos64.tar -C debian/usr/share
mv debian/usr/share/dist debian/usr/share/tonino
find debian -name .svn -exec rm -rf {} \; > /dev/null 2>&1
chown -R root:root debian
chmod -R go-w debian
chmod 0644 debian/usr/share/tonino/*.so*
rm -f ${RPM_NAME}*x86_64.rpm

cd debian

rm -rf usr/._bin
rm -rf usr/._share
rm -rf usr/bin/._*
rm -rf usr/share/._*
rm -rf usr/share/doc/._*
rm -rf usr/share/doc/artisan/._*
rm -rf usr/share/man/._*
rm -rf usr/share/man/man1/._*
rm -rf usr/share/pixmaps/._*
rm -rf usr/share/applications/._*

/usr/local/bin/fpm -s dir -t rpm -n tonino --license GPL3 -m "Marko Luther & Paul Holleis <marko.luther@gmx.net>" \
--vendor "Tonino GitHub" \
--url "https://github.com/myTonino/Tonino-App" \
--description "Software to update and configure the Tonino roast color meter <http://my-tonino.com>" \
--after-install DEBIAN/postinst \
--before-remove DEBIAN/prerm \
-v ${VERSION} --prefix / usr

/usr/local/bin/fpm -s dir -t deb -n tonino --license GPL3 -m "Marko Luther & Paul Holleis <marko.luther@gmx.net>" \
--vendor "Tonino GitHub" \
--no-auto-depends \
--url "https://github.com/myTonino/Tonino-App" \
--description "Software to update and configure the Tonino roast color meter <http://my-tonino.com>" \
--after-install DEBIAN/postinst \
--before-remove DEBIAN/prerm \
-v ${VERSION} --prefix / usr


mv *.rpm ..
mv *.deb ..
cd ..



