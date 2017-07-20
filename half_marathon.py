#!/usr/bin/env python

print "expects a file HM.gpx with two half marathon races inside"
print "create this with garmin basecamp"

import gpxpy.gpx
from gpxpy import geo as mod_geo
gpxfile=open("HM.gpx","r")
gpx = gpxpy.parse(gpxfile)
secondrace = gpx.tracks[0]
firstrace = gpx.tracks[1]
import matplotlib.pyplot as plt
from matplotlib import gridspec
pace = False
maxx = 0
hraceone = []
xhraceone= []
xraceone = []
yraceone = []
vraceone = []
sraceone = []
traceone = []
hracetwo = []
xhracetwo= []
xracetwo = []
yracetwo = []
vracetwo = []
sracetwo = []
tracetwo = []

def running(ar,N):
    retval = []
    for i in xrange(len(ar)):
        if i < N:
            retval += [sum(ar[0:i+N])/len(ar[0:i+N])]
        elif i+N >= len(ar):
            retval += [sum(ar[i-N:-1])/len(ar[i-N:-1])]
        else:
            retval += [sum(ar[i-N:i+N])/len(ar[i-N:i+N])]
    return retval



for p in xrange(len(firstrace.segments[0].points)):
    xraceone += [mod_geo.length_3d(firstrace.segments[0].points[0:p+1])]
    try:
        hraceone += [firstrace.segments[0].points[p].extensions['hr']]
        xhraceone += [xraceone[-1]]
    except:
        pass
    yraceone += [firstrace.segments[0].points[p].elevation]
    traceone += [firstrace.segments[0].points[p].time]
    try:
        nt = traceone[-1]
        pt = traceone[-2]
        dt = nt-pt
        nx = xraceone[-1]
        px = xraceone[-2]
        ny = yraceone[-1]
        py = yraceone[-2]
        if pace:
            dt = float(dt.seconds)/60.
            vraceone += [dt/(nx-px)*1000]
        else:
            dt = float(dt.seconds)/60./60.
            vraceone += [(nx-px)/dt/1000]
        sraceone += [(ny-py)/(nx-px)]
    except:
        sraceone += [0]
        vraceone += [0]
for p in xrange(len(secondrace.segments[0].points)):
    xracetwo += [mod_geo.length_3d(secondrace.segments[0].points[0:p+1])]
    try:
        hracetwo += [secondrace.segments[0].points[p].extensions['hr']]
        xhracetwo += [xracetwo[-1]]
    except:
        pass
    yracetwo += [secondrace.segments[0].points[p].elevation-200]
    traceone += [secondrace.segments[0].points[p].time]
    try:
        nt = traceone[-1]
        pt = traceone[-2]
        dt = nt-pt
        nx = xracetwo[-1]
        px = xracetwo[-2]
        ny = yracetwo[-1]
        py = yracetwo[-2]
        if pace:
            dt = float(dt.seconds)/60.
            vracetwo += [dt/(nx-px)*1000]
        else:
            dt = float(dt.seconds)/60./60.
            vracetwo += [(nx-px)/dt/1000]
        sracetwo += [(ny-py)/(nx-px)]
    except:
        sracetwo += [0]
        vracetwo += [0]

maxx = max(xraceone[-1],xracetwo[-1])

fig = plt.figure()
gs = gridspec.GridSpec(4, 1, height_ratios=[2, 1, 1, 1])

ax0 = plt.subplot(gs[0])
ax0.plot(xraceone,yraceone)
ax0.plot(xracetwo,yracetwo)
ax0.set_xlim([0,maxx])
ax0.set_xlabel("distance")
ax0.set_ylabel("altitude (minus offset)")

ax1 = plt.subplot(gs[1], sharex = ax0)
ax1.plot(xraceone,running(sraceone,20))
ax1.plot(xracetwo,running(sracetwo,20))
ax1.set_ylabel("slope")
plt.setp(ax0.get_xticklabels(), visible=False)

ax2 = plt.subplot(gs[2], sharex = ax0)
ax2.plot(xraceone,running(vraceone,20))
ax2.plot(xracetwo,running(vracetwo,20))
ax2.set_ylabel("velocity")
plt.setp(ax1.get_xticklabels(), visible=False)

ax3 = plt.subplot(gs[3], sharex = ax0)
ax3.plot(xhraceone,hraceone)
ax3.plot(xhracetwo,hracetwo)
ax3.set_ylabel("heart rate")
plt.setp(ax2.get_xticklabels(), visible=False)

ax0.set_xlim([0,maxx])

yticks = ax0.yaxis.get_major_ticks()
yticks[-1].label1.set_visible(False)
yticks[ 0].label1.set_visible(False)
yticks = ax1.yaxis.get_major_ticks()
yticks[-1].label1.set_visible(False)
yticks[ 0].label1.set_visible(False)
yticks = ax2.yaxis.get_major_ticks()
yticks[-1].label1.set_visible(False)
yticks[ 0].label1.set_visible(False)
yticks = ax3.yaxis.get_major_ticks()
yticks[-1].label1.set_visible(False)
yticks[ 0].label1.set_visible(False)

plt.subplots_adjust(hspace=.0)
plt.show()

#plt.scatter(sraceone,vraceone,c='blue')
#plt.scatter(sracetwo,vracetwo,c='green')
#plt.show()
