#!/bin/sh
#
# build-linux.sh
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

VERSION=$(python -c 'import lib; print(lib.__version__)')
NAME=tonino-linux-${VERSION}
RPM_NAME=tonino-${VERSION}

# fix debian/DEBIAN/control _VERSION_
sed -i "s/_VERSION_/${VERSION}/g" debian/DEBIAN/control


# prepare debian directory

cp doc/changelog debian/usr/share/doc/tonino
cp doc/copyright debian/usr/share/doc/tonino
cp doc/tonino.1 debian/usr/share/man/tonino

gzip -9 debian/usr/share/man/man1/tonino.1
gzip -9 debian/usr/share/doc/tonino/changelog


# build CentOS i386 .rpm

rm -rf debian/usr/share/tonino
tar -xf dist-centos.tar -C debian/usr/share
mv debian/usr/share/dist debian/usr/share/tonino
find debian -name .svn -exec rm -rf {} \; > /dev/null 2>&1
chown -R root:root debian
chmod -R go-w debian
chmod 0644 debian/usr/share/tonino/*.so*
rm ${NAME}_i386.deb
fakeroot dpkg --build debian ${NAME}_i386.deb
alien -r ${NAME}_i386.deb
mv ${RPM_NAME}-2.i386.rpm ${NAME}_i386.rpm

# build Ubuntu .deb

rm -rf debian/usr/share/tonino
tar -xf dist-ubuntu.tar -C debian/usr/share
mv debian/usr/share/dist debian/usr/share/tonino
find debian -name .svn -exec rm -rf {} \; > /dev/null 2>&1
chown -R root:root debian
chmod -R go-w debian
chmod 0644 debian/usr/share/tonino/*.so*
rm ${NAME}_i386-glibc2.4.deb
fakeroot dpkg --build debian ${NAME}_i386-glibc2.4.deb

