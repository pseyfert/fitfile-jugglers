#!/usr/bin/env python

import sys
import os
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from fitparse import FitFile
import numpy as np

colors = 16
no_OSM = False
if not no_OSM:
    try:
        import tilemapbase
        background = True
        tilemapbase.init(create=True)
    except ImportError:
        background = False
else:
    background = False


try:
    ff = FitFile(os.path.abspath(sys.argv[1]))
except IOError as e:
    if e.errno == 2:
        print("Could not open .fit file: {}".format(e.strerror))
    sys.exit(e.errno)

message_generator = ff.get_messages()

pos_longs = []
pos_lats = []
speeds = []

for message in message_generator:
    try:
        message_dict = message.as_dict()
    except:
        continue
    if message_dict['name'] != 'record':
        continue

    lat = None
    lon = None
    v = None
    for message_field in message_dict['fields']:
        if message_field['name'] == 'position_lat':
            lat = 180. / 2**31 * message_field['value']
        if message_field['name'] == 'position_long':
            lon = 180. / 2**31 * message_field['value']
        if message_field['name'] == 'speed':
            v = message_field['value']

    if lat is not None and lon is not None:
        pos_lats.append(lat)
        pos_longs.append(lon)
        speeds.append(v if v is not None else 0.0)

min_speed = min(speeds)
max_speed = max(speeds)

speed_intervals = np.linspace(min_speed,
                              max_speed + (max_speed - min_speed) * 0.01,
                              colors + 1)

if background:
    try:
        path = [tilemapbase.project(x, y) for x, y in zip(pos_longs, pos_lats)]
    except ValueError:
        print("something is wrong with the coordinates.")
        sys.exit(1)
    path_x, path_y = zip(*path)

    mid_x = (min(path_x) + max(path_x)) / 2.
    mid_y = (min(path_y) + max(path_y)) / 2.
    size_x = (max(path_x) - min(path_x)) * 1.618033988749894
    size_y = (max(path_y) - min(path_y)) * 1.618033988749894
    size = max(size_x, size_y)

    # the factor 1.05 is empiric
    extent = tilemapbase.Extent.from_centre(mid_x, mid_y, size * 1.05, size)

else:
    path_x, path_y = pos_longs, pos_lats


long_array = []
lat_array = []
dbg = []
for color_index in range(colors):
    mask = [not(speed_intervals[color_index] <= vv and
                vv < speed_intervals[color_index + 1])
            for vv in speeds]
    dbg.append(mask)
    modmask = [mask[0]]
    for i in range(1, len(mask)):
        modmask.append(mask[i] and mask[i - 1])
    long_array.append(np.ma.masked_where(modmask, path_x))
    lat_array.append(np.ma.masked_where(modmask, path_y))

lincol_array_test = np.ma.array(tuple(np.ma.hstack((np.ma.vstack(long_array[color_index]),
                                                   np.ma.vstack(lat_array[color_index])))
                                      for color_index in range(colors)))

mid_speeds = np.array([(speed_intervals[i] + speed_intervals[i + 1]) / 2.
                       for i in range(colors)])
line_segments = LineCollection(lincol_array_test,
                               array=mid_speeds,
                               cmap=plt.get_cmap('jet'))

fig, ax = plt.subplots()
DPI = plt.gcf().get_dpi()
fig.set_size_inches(700 / float(DPI), 700 / float(DPI))

# https://stackoverflow.com/a/20909062
fig.subplots_adjust(hspace=0., wspace=0., left=0., bottom=0., right=1., top=1.)

if background:
    plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.OSM, width=700)  # 1800)
    plotter.plot(ax)

# https://stackoverflow.com/a/21322270
plt.axis('off')

ax.add_collection(line_segments)
# fig.colorbar(line_segments)
# ax.plot(path_x, path_y, "r-")

plt.show()
