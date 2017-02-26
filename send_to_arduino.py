# -*- coding: utf-8 -*-
"""
Created on Thu May 14 15:04:31 2015

@author: reini
"""

import serial
import sys
import getopt
import numpy as np
import re
from progressbar import ETA, Bar, RotatingMarker, ProgressBar, Percentage
#import datetime
#import Skype4Py

def main(argv):
    #default values
    serialport = '/dev/tty.HC-06-DevB'
    resolution = 2
    try:
        opts, args = getopt.getopt(argv, "p:f:r", ["port=", "file=", "res="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt,arg in opts:
        if(opt in ("-p", "--port" )):
            serialport = arg
        if opt in ("-f", "--file"):
            infilename = arg
        if opt in ("-r", "--res"):
            resolution = float(arg)

    # precompile regular expressions
    rex_g = {}
    g_params = set(("X", "Y", "Z", "I", "J", "K", "P", "R", "K", "U", "V", "W", "A", "B", "C"))
    for g_param in g_params:
        rex_g[g_param] = re.compile("(%s[\+\-]?[\d\.]+)\D?" % g_param)
    # regex compilation
    gcodes_rex = re.compile("([G|M][\d|\.]+)\D?")
    new_point = np.zeros((2,1))
    max_point = new_point
    to_send = list()
    with open(infilename,'r') as f:
        for idx,line in enumerate(f):
            # cleanup line
            line = line.strip()
            line = line.upper()
            # filter out some incorrect lines
            # blank lines
            # lines beginning with % or (
            if len(line) == 0 or line[0] == "%" or line[0] == "(":
                continue
            # start of parsing
            params = {}
            for parameter in g_params:
                match = rex_g[parameter].search(line)
                if match:
                    params[parameter] = float(match.group(1)[1:])
                    line = line.replace(match.group(1), "")
            command = gcodes_rex.findall(line)[0]
            if command == 'G00' and 'Z' in params:
                to_send.append('G00 Z{}'.format(int(params['Z'])))
            if command == 'G01' and 'Z' in params and not('X' in params):
                to_send.append('G00 Z{}'.format(int(params['Z'])))
            if command == 'G00' and 'X' in params:
                to_send.append('G01 X{} Y{}'.format(int(params['X']),int(params['Y'])))
                new_point = np.array([[params['X']],[params['Y']]])
                max_point = np.maximum(new_point,max_point)
            if command == 'G01' and 'X' in params:  # we just copy that to the output
                to_send.append('G01 X{} Y{}'.format(int(params['X']),int(params['Y'])))
                new_point = np.array([[params['X']],[params['Y']]])
                max_point = np.maximum(new_point,max_point)
            if command == 'G02' or command == 'G03': # aproximate that with lines
                old_point = new_point
                new_point = np.array([[params['X']],[params['Y']]])
                max_point = np.maximum(new_point,max_point)
                # center of rotation
                c = old_point + np.array([[params['I']],[params['J']]])
                start_point = old_point-c
                end_point = new_point-c
                angle = np.arccos(start_point.transpose().dot(end_point) / (np.linalg.norm(start_point) * np.linalg.norm(end_point)))
                angle = angle.squeeze()
                R = np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
                if np.linalg.norm(end_point-np.matmul(R,start_point)) > 1e-3:
                    angle = angle * -1
                # create intermediate points
                r = np.sqrt(params['I']**2+params['J']**2)
                b = angle * r
#                print params,old_point,new_point,start_point,end_point
                num_to_interpolate = int(np.abs(b/resolution))
                if num_to_interpolate>0:
                    angle = angle / num_to_interpolate
                    R = np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
                    inter_point = start_point
                    c = c.squeeze()
                    for k in range(0,num_to_interpolate):
                        inter_point = np.matmul(R,inter_point)
                        i = inter_point.squeeze()
                        to_send.append('G01 X{} Y{}'.format(int(i[0]+c[0]),int(i[1]+c[1])))
                to_send.append('G01 X{} Y{}'.format(int(params['X']),int(params['Y'])))
    # add homing
    to_send.append('G00 Z10')
    # to_send.append('G01 X{} Y0'.format(new_point.squeeze()[0]))
    to_send.append('G01 X0 Y0')
    to_send.append('M05')
    #print max_point
    if any (new_point>np.array([[3200],[1000]])):
        print 'Image too large! 3200 x 1000 is the maximum!'
    ser = serial.Serial(port=serialport,baudrate=9600,timeout=10)
    widgets = [Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA()]
    pbar = ProgressBar(widgets=widgets).start()
    for line in pbar(to_send):
        #print line
        ser.write('%s\n'%line)
        ser.readline()
    ser.close()


if __name__ == "__main__":
    main(sys.argv[1:])
