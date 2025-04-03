from datetime import date
from io import StringIO
import pandas as pd
import pytz
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rfi_query.settings")
import django
django.setup()

from rfi.models import Frequency, Scan


def make_the_csv(rcvr):
	most_recent_session = (
				Scan.objects.filter(frontend__name=rcvr, datetime__lte=date.today())
				.order_by("-datetime")
				.first()
				.session
			)

	qs = Frequency.objects.all()
	qs = qs.filter(scan__session=most_recent_session)

	# get the 'session_level' metadata
	header_row = qs[:1]
	scan_level = pd.DataFrame(
				header_row.values(
					"scan__frontend__name", "scan__polarization__name",
					"scan__unit", "scan__session__name",  "scan__datetime"
				))
	scan_level.insert(0, "telescope", ["GBT"])
	#scan_level = scan_level_pd.iloc[0]
	file_name = scan_level.iloc[0].scan__session__name

	# make a 2 column dataFrame for the data needed to plot
	reading_level = pd.DataFrame(
	            qs.values("frequency", "intensity")
	        )

	df_merged = pd.concat([scan_level, reading_level], axis=1)
	#df_merged = scan_level.append(reading_level, ignore_index=True)


	headers = ["Instrument", "Receiver", "Polarization", "Inensity_Unit", "Scan_Name", "Scan_DateTime", "Frequency", "Intensity"]
	df_merged.to_csv(file_name+".csv", index=False, sep=',', na_rep=' ', header=headers)

rcvrs = [i['frontend__name'] for i in Scan.objects.values('frontend__name').distinct()]
for rcvr in rcvrs:
	print("Making file for: ", rcvr)
	make_the_csv(rcvr)