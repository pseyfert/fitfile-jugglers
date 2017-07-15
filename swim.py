#!/usr/bin/env python
from datetime import datetime
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
    t = []
    lastref = datetime.strptime("1970-01-01 00:00:00","%Y-%m-%d %H:%M:%S")
    if m.as_dict()['name'] != 'hr': continue

    names = []
    for xx in x:
        names.append(xx['name'])

    performed_update = False
    if 'timestamp' in names:
        # reference timestamp
        if xx['name'] == 'timestamp':
            lastref = datetime.strptime(xx['value'],"%Y-%m-%d %H:%M:%S")
        performed_update = True
    else:
        if xx['name'] == 'filtered_bpm':
            h = xx['value']
        if xx['name'] == 'event_timestamp':
            t.append(xx['value'])


    if type(h) is int:
        print x
        for xx in x:
            print xx
        print
        print
        print
        continue
    if h is not None:
        try:
            if t[0] < ts[-1]:
                if performed_update:
                    pass
                else:
                    print "PANIC"
        except:
            pass
        performed_update = False

        for hh in xrange(len(h)):
            hr.append(h[hh])
            ts.append(lastref + t[hh])

import matplotlib

#for h in hr:
#    print h

print "got HR values " + str(len(hr))
print "got timestamps" + str(len(ts))

plt.plot(ts,hr)
plt.gcf().autofmt_xdate()
plt.show()
