# fitfile-jugglers

## AIM

Use garmin devices without cloud and app. Get the files (copy through usb) and
start nerding yourself.

Watch a lightning talk about the problem [here](https://media.ccc.de/v/FT7A7U).

## what's there (or, well, drafted)

### `fit2gpx.sh`

A command line call to gpsbabel to convert fit files to gpx, with the garmin
extensions enabled (heart rate, cadence for cycling, temperature.)

Does not work at the moment for newer garmin files (2.0) e.g. from the [skiing
app](https://apps.garmin.com/de-DE/apps/47e87496-459b-46a0-8b9d-c344cb0d1df9).

### `half_marathon.py`

Some plotting from the record of a half marathon, when two half marathon runs
are stored in one gpx file, as exported from garmin basecamp.

### `hiit.py`

Show heart rate during a HIIT session. Shows also whenever you hit the lap
button. Interactive matplotlib plot, png output and an interactive html file
(lots of external JS loaded, no idea if the JS module calls home).

### `steps.py`

A parser of the acivity tracking (in `MONITOR/` on garmin watches), shows your
steps throughout the day.

### `swim.py`

Heart rate parsing for indoor swimming. (haven't figured out the timestamps
yet).

## unit tests and references

I would love to let you help and hack around, but, you know, I have
reservations putting some .FIT recordings of myself on the internet (other than
what I somewhat had to share with Garmin, to get a "reference" reading, files
are marked as private there and mostly deleted, but that's on trust basis and I
don't want to make it worse).

## requirements

I'm using [python-fitparse](https://github.com/dtcooper/python-fitparse) commit
5283af577d593bfb11bdc582c7d2df61b6ce3c40 and
[gpxpy](//github.com/pseyfert/gpxpy.git) with my commit
4449b9cb7b852ccd4068b712d99e71e9139826c4 (from
[here](https://github.com/podusowski/gpxpy/commit/e9b73b12b84371e0d4908155835469f2704abfe9)
).


