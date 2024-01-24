#!/usr/bin/env python

import sys
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib
from tzwhere import tzwhere
import matplotlib.dates as mdates
from matplotlib import gridspec
from matplotlib.collections import LineCollection

import numpy as np

from fitparse import FitFile
from pytz import timezone

import utils

UPDOWN_tolerance = 7.

tz_utc = timezone('UTC')
epoch = datetime.datetime.utcfromtimestamp(0)
epoch = tz_utc.localize(epoch).astimezone(timezone('Europe/Zurich'))

try:
    ff = FitFile(os.path.abspath(sys.argv[1]))
except IOError as e:
    if e.errno == 2:
        print("Could not open .fit file: {}".format(e.strerror))
    sys.exit(e.errno)

mm = ff.get_messages()

ts = []
hs = []

tvs = []
vs = []
udforv = []
ps = []

ths = []
hrs = []
cds = []
pws = []
pwsl = []
pwsr = []

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

lowesttime = None
highesttime = None

pos_lat = None
pos_long = None

for m in mm:
    try:
        x = m.as_dict()['fields']
    except KeyError:
        continue
    h = None
    hr = None
    cd = None
    pw = None
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
        if (pos_lat is None) or (pos_long is None):
            if xx['name'] == 'position_lat':
                pos_lat = xx['value']
            if xx['name'] == 'position_long':
                pos_long = xx['value']
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
    cd = utils.get_cadence(x)
    pw = utils.get_power(x)
    pwr, pwl = utils.get_power_right_left(x)

    if hr is not None and t is not None:
        th = t
        hrs.append(hr)
        cds.append(cd)
        pws.append(pw)
        pwsl.append(pwl)
        pwsr.append(pwr)
        ths.append(th)

    if v is not None:
        tv = t

    if h is not None and t is not None:

        if v is not None:
            vs.append(3.6 * v)
            udforv.append(downwards)
            try:
                ps.append(60. / (3.6 * v))
            except ZeroDivisionError:
                ps.append(0.)
            tvs.append(tv)

        if lastflipheight is None:
            lastflipheight = h

        if downwards and h < lastheight:
            lastheight = h
            lowesttime = t
        elif downwards and h < lastheight + UPDOWN_tolerance:
            pass  # fluctuation
        elif downwards:
            downwards = False
            lastheight = h
            flip_UP.append(lowesttime)
            lowesttime = None
            total_dist_down += cur_dist - lastflipdist
            total_height_down += lastflipheight - h
            lastflipdist = cur_dist
            lastflipheight = h
            ps.append(0)
        elif h > lastheight:  # upwards
            lastheight = h
            highesttime = t
        elif h > lastheight - UPDOWN_tolerance:  # upwards
            pass  # fluctuation
        else:
            ps.append(0)
            downwards = True
            lastheight = h
            flip_DOWN.append(highesttime)
            highesttime = t
            total_dist_up += cur_dist - lastflipdist
            total_height_up += h - lastflipheight
            lastflipdist = cur_dist
            lastflipheight = h

        hs.append(h)
        ts.append(t)

if pos_lat is not None and pos_long is not None:
    tzwhere = tzwhere.tzwhere()
    timezone_str = tzwhere.tzNameAt(180. / 2**31 * float(pos_lat),
                                    180. / 2**31 * float(pos_long))
    my_timezone = timezone(timezone_str)
else:
    my_timezone = timezone('Europe/Zurich')

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
            tmp.append(tz_utc.localize(t).astimezone(my_timezone))
        else:
            tmp.append(t.astimezone(my_timezone))
    t = matplotlib.dates.date2num(tmp)
    # return tmp
    return t


ts_o = ts
ts = convert_time(ts)
ths = convert_time(ths)
tvs_o = tvs
tvs = convert_time(tvs)
# tvsf = [(tt - epoch).total_seconds() for tt in tvs]
# try:
#     tvsf = matplotlib.dates.date2num(tvs)  # raises if date2num already applied
# except AttributeError:
tvsf = tvs

downvs = np.ma.masked_where(udforv, vs)
upvs = np.ma.masked_where(np.array([not value for value in udforv]), vs)

fig = plt.figure()
gs = gridspec.GridSpec(5, 1, height_ratios=[2, 1, 1, 1, 1])

ax0 = plt.subplot(gs[0])
ax0.plot(ts, hs)
ax0.set_ylim([minheight, maxheight])
ax0.set_xlim((min(tvsf), max(tvsf)))
ax0.set_xlabel("time")
ax0.set_ylabel("altitude")
# FIXME: debug Nones in lapmarkers
for lapmarker in flip_UP:
    if lapmarker is not None:
        ax0.plot([lapmarker, lapmarker], [minheight, maxheight], 'b')
for lapmarker in flip_DOWN:
    if lapmarker is not None:
        ax0.plot([lapmarker, lapmarker], [minheight, maxheight], 'r')
plt.gcf().autofmt_xdate()

ax1 = plt.subplot(gs[1], sharex=ax0)
ax1.set_xlabel("time")
ax1.set_xlim((min(tvsf), max(tvsf)))
# ax1.plot(tvs, ps)
# ax1.set_ylabel("pace [min/km]")

# the hstack just emulates a "zip" but remains in the numpy domain
# tried dstack[0] but that drops the mask
# vstack to change shape (shape influences hstack behaviour)
#
lincol_array_test1 = np.ma.hstack((np.ma.vstack(tvsf), np.ma.vstack(upvs)))
lincol_array_test2 = np.ma.hstack((np.ma.vstack(tvsf), np.ma.vstack(downvs)))
lincol_array_test = np.ma.stack((lincol_array_test1, lincol_array_test2))
line_segments = LineCollection(lincol_array_test, colors=['b', 'r'])
ax1.set_ylim((min(vs), max(vs)))
ax1.add_collection(line_segments)
# ax1.plot(tvs, vs)
ax1.set_ylabel("speed [km/h]")
plt.setp(ax0.get_xticklabels(), visible=False)

ax2 = plt.subplot(gs[2], sharex=ax0)
ax2.plot(ths, hrs)
ax2.set_ylabel("heart rate [bpm]")
ax2.set_xlabel("time")
ax2.set_xlim((min(tvsf), max(tvsf)))
plt.setp(ax1.get_xticklabels(), visible=False)

ax2.set_xlim((min(tvsf), max(tvsf)))
ax2.xaxis.set_major_locator(mdates.HourLocator())
formatter = mdates.DateFormatter('%H:%M')
formatter.set_tzinfo(my_timezone)
ax2.xaxis.set_major_formatter(formatter)
# fig.autofmt_xdate()

ax3 = plt.subplot(gs[3], sharex=ax0)
ax3.plot(ths, cds)
ax3.set_ylabel("cadense [rpm]")
ax3.set_xlabel("time")
ax3.set_xlim((min(tvsf), max(tvsf)))
plt.setp(ax1.get_xticklabels(), visible=False)

ax3.set_xlim((min(tvsf), max(tvsf)))
ax3.xaxis.set_major_locator(mdates.HourLocator())
formatter = mdates.DateFormatter('%H:%M')
formatter.set_tzinfo(my_timezone)
ax3.xaxis.set_major_formatter(formatter)
# fig.autofmt_xdate()

ax4 = plt.subplot(gs[4], sharex=ax0)
if all((p is None for p in pwsl)):
    ax4.plot(ths, pws)
else:
    ax4.plot(ths, pwsl, marker = '<')
    ax4.plot(ths, pwsr, marker = '>')
ax4.set_ylabel("power [Watt]")
ax4.set_xlabel("time")
ax4.set_xlim((min(tvsf), max(tvsf)))
plt.setp(ax1.get_xticklabels(), visible=False)

ax4.set_xlim((min(tvsf), max(tvsf)))
ax4.xaxis.set_major_locator(mdates.HourLocator())
formatter = mdates.DateFormatter('%H:%M')
formatter.set_tzinfo(my_timezone)
ax4.xaxis.set_major_formatter(formatter)
# fig.autofmt_xdate()

yticks = ax0.yaxis.get_major_ticks()
yticks[-1].label1.set_visible(False)
yticks[0].label1.set_visible(False)
yticks = ax1.yaxis.get_major_ticks()
yticks[-1].label1.set_visible(False)
yticks[0].label1.set_visible(False)

plt.subplots_adjust(hspace=.0)

vs = np.array(vs)
hs = np.array(hs)
hrs = np.array(hrs)

def on_xlims_change(event_ax):
    try:
        if on_xlims_change.cache == event_ax.get_xlim():
            return
    except AttributeError:
        pass
    on_xlims_change.cache = event_ax.get_xlim()
    low, high = on_xlims_change.cache

    selected_hs = np.logical_and(ths > low, ths < high)
    selected_vs = np.logical_and(tvs > low, tvs < high)
    # print(f"{hrs.shape=}, {ths.shape=}")
    # print(f"{vs.shape=}, {tvs.shape=}")
    meanspeed = vs[selected_vs].mean()
    meanHR = hrs[selected_hs].mean()
    print(f"mean speed in the range shown is {meanspeed}")
    print(f"mean HR in the range shown is {meanHR}")

for ax in fig.axes:
    ax.callbacks.connect('xlim_changed', on_xlims_change)

plt.show()
