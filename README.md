# Wireless egg-bot (sphere-o-bot)

This is the source repository of my take at the sphere-o-bot from jjrobots. The original project can be found here: http://www.jjrobots.com/product/sphere-o-bot/

## 3D Printing
For this project I've printed the frame from http://www.thingiverse.com/thing:1956649 and the parts from http://www.thingiverse.com/thing:1683764.

## Software
The supplied source code is meant to be used with Inkscape and the gcodetools from http://www.cnc-club.ru/gcodetools. The motors are controlled by a MotorShield V2 from Adafruit and their respective library.

The python file which communicates with the eggbot converts all curves into lines, since my simple interpreter only understands `G01` commands. Afterwards the commands will be sent over the serial interface. It can be called as follows:
```
python send_to_arduino.py -f <gcode-file> -p <port> -r <resolution>
```
where `resolution` is the resolution of the curve interpolation. You can lower this value down to `0.5` for increased resolution on curves, `2` seems to be a good compromise between quality and speed.

## Finished Project
![Eggbot complete](https://github.com/reini1305/eggbot/raw/master/images/complete.jpg)
![Electronics](https://github.com/reini1305/eggbot/raw/master/images/electronics.jpg)
![Frame](https://github.com/reini1305/eggbot/raw/master/images/frame.jpg)
