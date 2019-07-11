Quick Start
========

The Tonino app allows to

- configure your Tonino (only the display brightness for now)
- calibrate your Tonino
- create annotated measurements
- create and upload Tonino scales


Setup
-------------------

![](installation.png?raw=true)


1. Install the USB driver

	Download and install the FTDI VCP driver for your platform from [http://www.ftdichip.com/Drivers/VCP.htm](http://www.ftdichip.com/Drivers/VCP.htm)
	
	NOTE: on Ubuntu as well as Mac OS X 10.9 and newer already include the required USB driver, so no additional installation is required on those platforms

2. Install the Tonino app

  **Windows**

> Download and unpack [tonino-win-<version>.zip](https://github.com/myTonino/Tonino-App/releases/latest), then run the Tonino App Windows installer.
    
  **Mac OS X (>=10.7.x)**

> Download and open the Tonino App disk image [tonino-mac-<version>.dmg](https://github.com/myTonino/Tonino-App/releases/latest), then drag the Tonino app icon to your Applications directory.

  **Ubuntu/Debian**

> Download the [tonino-linux-<version>.deb](https://github.com/myTonino/Tonino-App/releases/latest) installer, start a shell and type


 	# sudo dpkg -i tonino-linux-<version>.deb


  **CentOS/Redhat**

> Download the [tonino-linux-<version>.rpm](https://github.com/myTonino/Tonino-App/releases/latest) installer, start a shell and type


 	# sudo rpm -i tonino-linux-<version>.rpm


3. Connect the Tonino


![](connected.png?raw=true)

Just start the app and connect your Tonino to the USB port of the computer. After a moment, the app will display the "`Connected to Tonino`" message on the bottom line of the main window that also indicates its firmware version. Once connected the Tonino will display "`PC`".


Tonino Configuration
-------------------

![](display-brightness.png?raw=true)

Under the application settings (e.g. menu Tonino >> Preferences on the Mac) you can set the display brightness of the connected Tonino. 

On newer models you can also set the screen orientation, a target value and range, as well as give the device a name. If a target value ```tv``` and range ```r``` other than 0 is given, the newer models present readings in the range from ```tv-r``` to ```tv+r``` in green (perfect hit), readings below that interval in blue (too light/cool) and readings above that interval in red (too dark/hot).


Tonino Calibration
-------------------

![](calibration.png?raw=true)

- Calibrating the Tonino without the app

	Remove your Tonino from the USB power source, place your Tonino on the brown calibration disk and reconnecting it to an USB power source. Once the brown disk is recognized, the Tonino will display "`CAL1`". After a moment the display will switch to "`CAL2`", requesting the red disk. Place the Tonino now on the red disk to finalize the calibration process. The Tonino will confirm a successful calibration with "`dOnE`".

- Calibration using the Tonino app

	Start the app and connect your Tonino as described above. Click on "`Calibrate`" to open the calibration window. Place the Tonino on one of the disk and press "`Scan`". The recognized disk symbol will be marked. Place it on the other disk and press "`Scan`" again. Once both disk symbols are marked, finalize the calibration by leaving the dialog with "`OK`".


Tonino Measurements
-------------------

![](measurements.png?raw=true)

Pressing "`Add`" will take a measurement using the connected Tonino and add an entry to the table displayed on the left side of the main window. Each entry consists of a T-value and a name. The name can be changed by double-clicking. The list of measurements can be stored into a *.toni file (menu File >> Save) and loaded again (menu File >> Load).

The visualization on the right side displays the measurements as dots in a coordinate system, labeled by their names if the corresponding entry is selected in the table. The x-axis of that graph represents the raw color values and the y-axis the T-values assigned by the scale in use. The scale of the connected Tonino is visualized as a black line.

The Tonino measurements can be sorted by the underlying raw color values (button "`Sort`"), the selected individuals can be deleted (button "`Delete`") and the table can be initialized (button "`Clear`").

In the top left, three LCD values display the [arithmetic mean](https://en.wikipedia.org/wiki/Arithmetic_mean) of the selected T-values ("`AVG`"), the [standard deviation](https://en.wikipedia.org/wiki/Standard_deviation) ("`DEV`") and the [95% confidence interval](https://en.wikipedia.org/wiki/Confidence_interval) ("`Conf95%`").


Tonino Scales
-------------------


![](scale.png?raw=true)

By default the Tonino displays readings according to the Tonino scale. A scale defines a mathematical mapping from the measured raw sensor values to the T-values as shown on the Tonino display. For example, filter roasts or very light roasts for espresso are assigned T-values higher than 100 by the Tonino scale, roughly corresponding to an Agtron value of 80 on the Gourmet scale.

A new scale can be defined via the Tonino app by taking a set of measurements, assigning each measurement the expected target value (by double-click on the corresponding T-values in the table) and letting the app computing the optimal approximation.

1. Take at least measurements from at least 5 samples, covering the full spectrum of roasts the scale should be applied by using the Tonino connected to the app (button "`Add`"). Note that all dots representing those measurements fall on the black line representing the scale in use by the connected Tonino.

2. Assign each measurement the correct target T-value w.r.t. the new scale, by clicking on its T-value and entering the corresponding number. Note that the dots on the graph will move away from black line.

3. Move the slider from 0 to 1 (linear regression), 2 (quadratic regression) or 3 (cubic regression). The computed approximation is constructed in a way minimizes the sum of the squares of the errors made for each sample (cf. [the method of least squares](https://en.wikipedia.org/wiki/Least_squares)) and drawn as a red line. The rank of the regression is displayed on top of the graph as "`d`" and the R-squared value (the square of the correlation coefficient), indicating the quality of the approximation (lower numbers are better), as "`RR`". You can add *artificial* points by a right-clicks on the graph and dragging them in place to improve the result.

4. If you are happy with the result you can store the scale in a *.toni file and upload it to the connected Tonino (button "`Upload`").

Once uploaded the Tonino will display readings according to this new scale. To return to the Tonino scale, connect the Tonino and press "`Defaults`". Note that this will also remove the calibration and thus requires a re-calibration of the device (see above).

A number of example scales are provided along the app to ease the experimentation.

![](example-scales.png?raw=true)


Tonino Resources
---------------
- [Tonino site](http://my-tonino.com)
- [Tonino app](https://github.com/myTonino/Tonino-App)
- [Tonino firmware](https://github.com/myTonino/Tonino-Firmware)
- [Tonino serial protocol](https://github.com/myTonino/Tonino-Firmware/blob/master/Tonino-Serial.md)
- [Tonino hardware](https://github.com/myTonino/Tonino-Hardware)
- Tonino example scales: [tonino-scales.zip](https://github.com/myTonino/Tonino-App/releases/download/v1.0.16/tonino-scales.zip)  (1.8Kb)
