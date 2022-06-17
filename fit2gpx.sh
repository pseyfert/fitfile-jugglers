fit2gpx () {
	if [[ $# -eq 2 ]]
	then
		gpsbabel -i garmin_fit -f $1 -o gpx,gpxver=1.1,garminextensions -F $2
	else
		gpsbabel -i garmin_fit -f $1 -o gpx,gpxver=1.1,garminextensions -F $1.gpx
	fi
}

