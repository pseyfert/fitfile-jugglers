#!/usr/bin/env python

import sys
import os
import matplotlib.pyplot as plt
from matplotlib import gridspec

import numpy as np

from fitparse import FitFile
from pytz import timezone


ff = FitFile(os.path.abspath(sys.argv[1]))

mm = ff.get_messages()

ts = []
hs = []

tvs = []
vs = []
udforv = []
ps = []

ths = []
hrs = []

lapmarkers_UP = []
lapmarkers_RUN = []

flip_DOWN = []
flip_UP = []

total_dist_up = 0.
total_dist_down = 0.

total_height_up = 0.
total_height_down = 0.

downwards = True
lastheight = 10000.
lastflipdist = 0.
lastflipheight = None

for m in mm:
    try:
        x = m.as_dict()['fields']
    except:
        continue
    h = None
    hr = None
    t = None
    tv = None
    th = None
    v = None
    cur_dist = 0.

    if m.as_dict()['name'] == 'lap':

        isup = False
        isrun = False
        for xx in x:
            if xx['name'] == 'Segment':
                if "RUN" == xx['value']:
                    isrun = True
                elif "UP" == xx['value']:
                    isup = True
                else:
                    print("paul, it's ", xx['value'])
            if xx['name'] == 'timestamp':
                lapmarker = xx['value']
        # if isup:
        #     lapmarkers_UP.append(lapmarker)
        # elif isrun:
        #     lapmarkers_RUN.append(lapmarker)
        # else:
        #     print("didn't find segment")
        continue

    if m.as_dict()['name'] != 'record':
        continue

    for xx in x:
        if xx['name'] == 'altitude':
            h = xx['value']
        if xx['name'] == 'speed':
            v = xx['value']
        if xx['name'] == 'timestamp':
            t = xx['value']
        if xx['name'] == 'distance':
            cur_dist = xx['value']
        if xx['name'] == 'heart_rate':
            hr = xx['value']

    if hr is not None and t is not None:
        th = t
        hrs.append(hr)
        ths.append(th)

    if v is not None:
        tv = t

    if h is not None and t is not None:

        if v is not None:
            vs.append(3.6*v)
            udforv.append(downwards)
            try:
                ps.append(60./(3.6*v))
            except ZeroDivisionError:
                ps.append(0.)
            tvs.append(tv)

        if lastflipheight is None:
            lastflipheight = h

        if downwards and h < lastheight:
            lastheight = h
        elif downwards and h < lastheight + 10.:
            pass  # fluctuation
        elif downwards:
            downwards = False
            lastheight = h
            flip_UP.append(t)
            total_dist_down += cur_dist - lastflipdist
            total_height_down += lastflipheight - h
            lastflipdist = cur_dist
            lastflipheight = h
            ps.append(0)
        elif h > lastheight:  # upwards
            lastheight = h
        elif h > lastheight - 4.:  # upwards
            pass  # fluctuation
        else:
            ps.append(0)
            downwards = True
            lastheight = h
            flip_DOWN.append(t)
            total_dist_up += cur_dist - lastflipdist
            total_height_up += h - lastflipheight
            lastflipdist = cur_dist
            lastflipheight = h

        hs.append(h)
        ts.append(t)


print("Distance going down: ", total_dist_down)
print("Distance going up:   ", total_dist_up)
print("")
print("Height going down: ", total_height_down)
print("Height going up:   ", total_height_up)
print("")

# dates = matplotlib.dates.date2num(ts)

maxheight = max(hs)
minheight = min(hs)


def convert_time(times):
    tmp = []
    for t in times:
        if t.tzinfo is None:
            tz = timezone('UTC')
            tmp.append(tz.localize(t).astimezone(timezone('Europe/Zurich')))
        else:
            tmp.append(t.astimezone(timezone('Europe/Zurich')))
    return tmp


ts = convert_time(ts)
ths = convert_time(ths)
tvs = convert_time(tvs)

downvs = np.ma.masked_where(udforv, vs)
upvs = np.ma.masked_where(np.array([not value for value in udforv]), vs)

fig = plt.figure()
gs = gridspec.GridSpec(3, 1, height_ratios=[2, 1, 1])

ax0 = plt.subplot(gs[0])
ax0.plot(ts, hs)
ax0.set_xlim([minheight, maxheight])
ax0.set_xlabel("time")
ax0.set_ylabel("altitude")
for lapmarker in flip_UP:
    ax0.plot([lapmarker, lapmarker], [minheight, maxheight], 'b')
for lapmarker in flip_DOWN:
    ax0.plot([lapmarker, lapmarker], [minheight, maxheight], 'r')
plt.gcf().autofmt_xdate()

ax1 = plt.subplot(gs[1], sharex=ax0)
# ax1.plot(tvs, ps)
# ax1.set_ylabel("pace [min/km]")
ax1.plot(tvs, vs)
ax1.set_ylabel("speed [km/h]")
plt.setp(ax0.get_xticklabels(), visible=False)

ax2 = plt.subplot(gs[2], sharex=ax0)
ax2.plot(ths, hrs)
ax2.set_ylabel("heart rate [bpm]")
plt.setp(ax1.get_xticklabels(), visible=False)

yticks = ax0.yaxis.get_major_ticks()
yticks[-1].label1.set_visible(False)
yticks[0].label1.set_visible(False)
yticks = ax1.yaxis.get_major_ticks()
yticks[-1].label1.set_visible(False)
yticks[0].label1.set_visible(False)

plt.subplots_adjust(hspace=.0)
plt.show()