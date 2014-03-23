The Tonino app allows to configure your Tonino roast color meter <http://my-tonino.com> as well as to define and upload custom scales.


HOME

The project home of this app is on GitHub were all source and binary files are available.


<https://github.com/myTonino/Tonino-App>


FEATURES

o runs on Mac OS X >10.6 on Intel, Windows, and Linux
(on OS X >10.7 Mountain Lion you need to tick "Allow applications downloaded from Anywhere" in the Security & Privacy Preference Panel to start the app)
o allows to connect to a Tonino device and trigger the measurements
o designer for custom scales
o save/load of custom scales
o upload of custom scales to a connected Tonino device
o update the firmware of a connected Tonino device



INSTALLATION


o Windows

Just install using the binary installer

o Mac OS X (>=10.6.x)

- Install USB/serial driver from FTDI
   http://www.ftdichip.com/Drivers/VCP.htm
- Download and run the Tonino OS X installer
- Double click on the dmg file you just downloaded
- Double click the disk image which appears on your desktop
- Drag the Tonino application icon to your Applications directory


o Linux

The Linux package is compatible with Ubuntu/Debian and CentOS/Redhat (glibc 2.12). For now, we simply offer a .deb Debian package as well as an .rpm Redhat package that you have to install manually. This can be done by either double clicking the package icon from your file viewer or by entering the following commands in a shell.

Installation on Ubuntu/Debian
# sudo dpkg -i tonino_<version>.deb

Uninstall on Ubuntu/Debian
# sudo dpkg -r tonino


Installation on CentOS/Redhat
# sudo rpm -i tonino_<version>.rpm

Uninstall on CentOS/Redhat
# sudo rpm -e tonino


LICENCE

The Tonino app is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
   
The Tonino app is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
   
Copies of the GNU General Public License has been included with this 
distribution in the file `LICENSE.txt`. An online version is available at
<http://www.gnu.org/licenses/>.



LIBRARIES

The Tonino app uses the following libraries in unmodified forms:

- Python 2.7.x and 3.3.x released under the PSF licence http://www.python.org/psf/
  http://www.python.org/
- QT 4.10.x under the Qt GNU Lesser General Public License version 2.1 (LGPL)
  http://qt-project.org/products/licensing
- Numpy 1.8.x and Scipy 0.13.x, Copyright (c) 2005, NumPy Developers; All Rights Reserved
  http://www.scipy.org/
- PyQt 4.8.x and SIP 4.15.x under the Qt GNU GPL v. 3.0 licence; Copyright (c) 2010 Riverbank Computing Limited
  http://www.riverbankcomputing.co.uk/software/pyqt/
- matplotlib 1.3.x, Copyright (c) 2002-2013 John D. Hunter; All Rights Reserved. Distributed under a licence based on PSF.
  http://matplotlib.sourceforge.net
- py2app 0.7.x under the PSF open source licence; Copyright (c) 2004-2006 Bob Ippolito <bob at redivi.com>
  Copyright (c) 2010-2012 Ronald Oussoren <ronaldoussoren at mac.com>.
  http://packages.python.org/py2app/
- py2exe, Copyright (c) 2000-2005 Thomas Heller, Mark Hammond, Jimmy Retzlaff
  http://www.py2exe.org/
- bbfreeze, Copyright (c) 2007-2012 brainbot technologies AG. Distributed under the zlib/libpng license.


VERSION HISTORY

v1.0.6 (23.3.2014)
 - Adds debug mode 
 - Font fix for OS X 10.9

v1.0.5 (10.3.2014)
 - Adds statistics LCDs+   
 - Improved serial communication

v1.0.4 (4.3.2014)
 - Adds sorting, improved calibration and minor fixes

v1.0.3 (2.2.2014)
 - Update of calibration values and ranges

v1.0.2 (17.1.2014)
 - Improved calibration

v1.0.1 (1.1.2014)
 - Fixes serial communication
 - Fixes device discovery on Windows

v1.0.0 (18.12.2013)
 - Initial release