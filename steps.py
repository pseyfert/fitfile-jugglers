#!/usr/bin/env python
import datetime
import matplotlib.pyplot as plt

from fitparse import FitFile

import sys

import os
from os import path
ff = FitFile(os.path.abspath(sys.argv[1]))

mm = ff.get_messages()

stepsc = []
acttimec = []
diffstepspertime = []
times = []

for m in mm:
    try:
        x = m.as_dict()['fields']
    except:
        continue
    steps = None
    time  = None
    acttime = None
    if m.as_dict()['name'] != 'monitoring': continue
    valid = False
    count = False
    for xx in x:
        if xx['name'] == 'current_activity_type_intensity':
            valid = True
        if xx['name'] == 'activity_type':
            if xx['value'] == 'walking':
                count = True
            if xx['value'] == 'running':
                count = True
        if xx['name'] == 'cycles':
            steps = xx['raw_value']
        if xx['name'] == 'timestamp_16':
            time = xx['value']
        if xx['name'] == 'active_time':
            acttime = xx['value']

    if valid and count and steps is not None and time is not None and acttime is not None:
        stepsc.append(steps)
        acttimec.append(acttime)

        if len(stepsc) > 1:
            times.append(time)
            diffstepspertime.append(0)

            ds = stepsc[-1] - stepsc[-2]
            diffacttime = acttimec[-1] - acttimec[-2]
            dspt = ds/diffacttime

            times.append(time)
            diffstepspertime.append(dspt)
            times.append(time+diffacttime)
            diffstepspertime.append(dspt)

            times.append(time+diffacttime)
            diffstepspertime.append(0)


import matplotlib

plt.plot(times,diffstepspertime)
plt.show()

