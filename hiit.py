#!/usr/bin/env python
import datetime
import matplotlib.pyplot as plt

from fitparse import FitFile

import sys

import os
from os import path
ff = FitFile(os.path.abspath(sys.argv[1]))

mm = ff.get_messages()

ts = []
hr = []

lapmarkers = []

for m in mm:
    try:
        x = m.as_dict()['fields']
    except:
        continue
    h = None
    t = None
    if m.as_dict()['name'] == 'lap':
        valid = False
        for xx in x:
            if xx['name'] == 'lap_trigger':
                if "manual" == xx['value']: valid = True
            if xx['name'] == 'timestamp':
                lapmarker = xx['value']
        if valid:
            lapmarkers.append(lapmarker)
        continue
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

# https://plot.ly/javascript/time-series/
with open(path.splitext(path.basename(sys.argv[1]))[0]+".html",'w') as f:
    f.write('''<head>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>

<body>
  
  <div id="myDiv" style="width: 100%; height: 50%;"><!-- Plotly chart will be drawn inside this DIV --></div>
  <script>
var data = [
  {
''')
    f.write("x: [")
    for t in ts:
        # https://stackoverflow.com/questions/311627/how-to-print-date-in-a-regular-format-in-python
        f.write(t.strftime("'%Y-%m-%d %H:%M:%S', "))
    f.write("],\n")
    f.write("y: [")
    for h in hr:
        f.write("%d, " % (h,))
    f.write("],\n")
    f.write('''    type: 'scatter'
  }
];

Plotly.newPlot('myDiv', data);
  </script>
</body>
''')


plt.plot(ts,hr)
for lapmarker in lapmarkers:
    plt.plot([lapmarker,lapmarker],[0,200])
plt.gcf().autofmt_xdate()
plt.show()

