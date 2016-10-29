#
# tonino.pro
#
# The project file for the Tonino application
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


SOURCES = \
    ../lib/main.py \
    ../uic/MainWindowUI.py \
    ../uic/AboutDialogUI.py \
    ../uic/PreferencesDialogUI.py \
    ../uic/CalibDialogUI.py \
    ../uic/TinyCalibDialogUI.py \
    ../uic/TinyCalibDialogUI2.py
    
TRANSLATIONS = \
	../translations/tonino_de.ts \
	../translations/tonino_it.ts \
	../translations/tonino_fr.ts \
	../translations/tonino_nl.ts \
	../translations/tonino_es.ts

CODECFORTR      = UTF-8

CODECFORSRC     = UTF-8