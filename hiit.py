#!/usr/bin/env python
import datetime
import matplotlib.pyplot as plt

from fitparse import FitFile

import sys

import os
ff = FitFile(os.path.abspath(sys.argv[1]))

mm = ff.get_messages()

ts = []
hr = []
for m in mm:
    try:
        x = m.as_dict()['fields']
    except:
        continue
    h = None
    t = None
    if m.as_dict()['name'] != 'record': continue
    for xx in x:
        if xx['name'] == 'heart_rate':
            h = xx['value']
        if xx['name'] == 'timestamp':
            t = xx['value']
    if h is not None and t is not None:
        hr.append(h)
        ts.append(t)

import matplotlib

print "got HR values " + str(len(hr))
print "got timestamps" + str(len(ts))

dates = matplotlib.dates.date2num(ts)

plt.plot(ts,hr)
plt.gcf().autofmt_xdate()
plt.show()
