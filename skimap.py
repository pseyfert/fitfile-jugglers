#!/usr/bin/env python

import sys
import os
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from fitparse import FitFile
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import utils

colormap = 'viridis'  # jet
colors = 16
no_OSM = False
color_scale = utils.get_speed
# color_scale = utils.get_heart_rate
# color_scale = utils.get_cadence
if not no_OSM:
    try:
        import tilemapbase
        tilemapbase.start_logging()
        background = True
        tilemapbase.init(create=True)
    except ImportError:
        print("tilemapbase not installed! disabling osm tiles")
        background = False
else:
    background = False

if background:
    # # from providers import opencyclemap_provider as base_provider
    # # from providers import opensnowmap_base_provider as base_provider
    # try:
        from providers import opensnowmap_slope_provider as slope_provider
        from providers import opensnowmap_base_provider as base_provider
    # except ImportError:
        # from tilemapbase.tiles import build_OSM
        # base_provider = build_OSM()

fig, ax = plt.subplots()
DPI = plt.gcf().get_dpi()
fig.set_size_inches(700 / float(DPI), 700 / float(DPI))


try:
    ff = FitFile(os.path.abspath(sys.argv[1]))
except IOError as e:
    if e.errno == 2:
        print("Could not open .fit file: {}".format(e.strerror))
    sys.exit(e.errno)

message_generator = ff.get_messages()

pos_longs = []
pos_lats = []
color_vals = []

for message in message_generator:
    try:
        message_dict = message.as_dict()
    except AttributeError:
        continue
    if message_dict['name'] != 'record':
        continue

    lat = None
    lon = None
    v = None
    for message_field in message_dict['fields']:
        if message_field['name'] == 'position_lat':
            try:
                lat = 180. / 2**31 * message_field['value']
            except TypeError:
                # happens with etrex touch 35
                lat = None
        if message_field['name'] == 'position_long':
            try:
                lon = 180. / 2**31 * message_field['value']
            except TypeError:
                # happens with etrex touch 35
                lon = None
                pass
    try:
        v = color_scale(message_dict['fields'])
    except TypeError:
        # happens with etrex touch 35
        v = 0
        pass

    if lat is not None and lon is not None:
        pos_lats.append(lat)
        pos_longs.append(lon)
        color_vals.append(v if v is not None else 0.0)

min_color_val = min(color_vals)
max_color_val = max(color_vals)

# add a bit to the max value
max_color_val += (max_color_val - min_color_val) * 0.01

color_intervals = np.linspace(min_color_val,
                              max_color_val,
                              colors + 1)

if background:
    try:
        path = [tilemapbase.project(x, y) for x, y in zip(pos_longs, pos_lats)]
    except ValueError:
        print("something is wrong with the coordinates.")
        sys.exit(1)
    path_x, path_y = zip(*path)
else:
    path_x, path_y = pos_longs, pos_lats

mid_x = (min(path_x) + max(path_x)) / 2.
mid_y = (min(path_y) + max(path_y)) / 2.
size_x = (max(path_x) - min(path_x)) * 1.618033988749894
size_y = (max(path_y) - min(path_y)) * 1.618033988749894
size = max(size_x, size_y)
min_x = mid_x - size / 2.
max_x = mid_x + size / 2.
min_y = mid_y - size / 2.
max_y = mid_y + size / 2.

if background:
    # the factor 1.05 is empiric
    extent = tilemapbase.Extent.from_centre(mid_x, mid_y, size * 1.05, size)
else:
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)

long_array = []
lat_array = []
dbg = []
for color_index in range(colors):
    mask = [(color_intervals[color_index] > vv or vv >= color_intervals[color_index + 1])
            for vv in color_vals]
    dbg.append(mask)
    modmask = [mask[0]]
    for i in range(1, len(mask)):
        modmask.append(mask[i] and mask[i - 1])
    long_array.append(np.ma.masked_where(modmask, path_x))
    lat_array.append(np.ma.masked_where(modmask, path_y))

lincol_array_test = np.ma.array(tuple(np.ma.hstack((np.ma.vstack(long_array[color_index]),
                                                    np.ma.vstack(lat_array[color_index])))
                                      for color_index in range(colors)))

# for the color axis use the middle points of the intervals
mid_color_vals = np.array([(color_intervals[i] + color_intervals[i + 1]) / 2.
                           for i in range(colors)])
line_segments = LineCollection(lincol_array_test,
                               array=mid_color_vals,
                               cmap=plt.get_cmap(colormap))

if background:

    # https://stackoverflow.com/a/20909062
    fig.subplots_adjust(hspace=0., wspace=0., left=0.,
                        bottom=0., right=1., top=1.)

    base_plotter = tilemapbase.Plotter(extent, base_provider, width=2 * 700)
    base_plotter.plot(ax, allow_large=True)
    try:
        slope_plotter = tilemapbase.Plotter(extent, slope_provider, width=2 * 700)
        slope_plotter.plot(ax, allow_large=True)
    except NameError:
        pass

    # https://stackoverflow.com/a/21322270
    plt.axis('off')

    blackline = LineCollection([list(zip(path_x, path_y)), ],
                               linewidths=(2.5,),
                               colors=("black",)
                               )
    ax.add_collection(blackline)

ax.add_collection(line_segments)


cbaxes = inset_axes(ax, width="1.5%", height="61%", loc=1, borderpad=5)
colorbar = fig.colorbar(line_segments, cax=cbaxes)
colorbar.ax.set_ylabel(color_scale.__name__)

def redo_bkg(event_ax):
    print("trying really hard to redraw the background with better res")
    xmin, xmax = event_ax.get_xlim()
    ymax, ymin = event_ax.get_ylim()
    print(f"{xmin=}, {xmax=}, {ymin=}, {ymax=}")
    try:
        if redo_bkg.xcache == event_ax.get_xlim() and redo_bkg.ycache == event_ax.get_ylim():
            print("nothing to be done")
            return
    except AttributeError:
        pass
    redo_bkg.xcache = event_ax.get_xlim()
    redo_bkg.ycache = event_ax.get_ylim()
    xmin, xmax = redo_bkg.xcache
    ymax, ymin = redo_bkg.ycache
    extent = tilemapbase.Extent(xmin, xmax, ymin, ymax)
    base_plotter = tilemapbase.Plotter(extent, base_provider, width=2 * 700)
    base_plotter.plot(event_ax, allow_large=True)
    try:
        slope_plotter = tilemapbase.Plotter(extent, slope_provider, width=2 * 700)
        slope_plotter.plot(event_ax, allow_large=True)
    except NameError:
        pass

    # https://stackoverflow.com/a/21322270
    plt.axis('off')

    event_ax.add_collection(blackline)
    event_ax.add_collection(line_segments)


    cbaxes = inset_axes(event_ax, width="1.5%", height="61%", loc=1, borderpad=5)
    colorbar = fig.colorbar(line_segments, cax=cbaxes)
    colorbar.ax.set_ylabel(color_scale.__name__)
    print("thanks for your patience, done")


ax.callbacks.connect('xlim_changed', redo_bkg)
ax.callbacks.connect('ylim_changed', redo_bkg)

xmin, xmax = ax.get_xlim()
ymax, ymin = ax.get_ylim()
print(f"{xmin=}, {xmax=}, {ymin=}, {ymax=}")
plt.show()
