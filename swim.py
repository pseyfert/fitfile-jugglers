#!/usr/bin/env python
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from fitparse import FitFile

import sys

import os
ff = FitFile(os.path.abspath(sys.argv[1]))

mm = ff.get_messages()

ts = []
hr = []
lastref = datetime.strptime("1970-01-01 00:00:00","%Y-%m-%d %H:%M:%S")
performed_update = False

entrycounter = 0
for m in mm:
    try:
        x = m.as_dict()['fields']
    except:
        continue
    entrycounter += 1
    h = None
    t = []
    if m.as_dict()['name'] != 'hr': continue

    names = []
    for xx in x:
        names.append(xx['name'])

    if 'timestamp' in names:
      for xx in x:
        # reference timestamp
        if xx['name'] == 'timestamp':
            #print "found timestamp"
            #lastref = datetime.strptime(xx['value'],"%Y-%m-%d %H:%M:%S")
            lastref = xx['value']
        performed_update = True
    else:
      for xx in x:
        if xx['name'] == 'filtered_bpm':
            #print "found filtered bpm"
            h = xx['value']
        if xx['name'] == 'event_timestamp':
            #print "found event timestamp"
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
                    print "let's do the time warp again"
                else:
                    print "PANIC"
        except:
            pass
        performed_update = False

        for hh in xrange(len(h)):
            hr.append(h[hh])
            ts.append(lastref + timedelta(seconds=t[hh]))
            #ts.append(t[hh])

import matplotlib

#for t in ts:
#    print t
#for h in hr:
#    print h

print "analyszed " + str(entrycounter) + " entries"
print "got HR values " + str(len(hr))
print "got timestamps" + str(len(ts))

plt.plot(ts,hr)
plt.gcf().autofmt_xdate()
plt.show()
