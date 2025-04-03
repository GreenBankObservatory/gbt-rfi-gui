from datetime import date
from io import StringIO
import pandas as pd
import pytz
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rfi_query.settings")
import django
django.setup()

from rfi.models import Frequency, Scan

most_recent_session = (
			Scan.objects.filter(datetime__lte=date.today())
			.order_by("-datetime")
			.first()
			.session
		)

qs = Frequency.objects.all()
qs = qs.filter(scan__session=most_recent_session)


# get the 'session_level' metadata
header_row = qs[:1]
scan_level_pd = pd.DataFrame(
			header_row.values(
				"scan__frontend__name", "scan__polarization__name",
				"scan__unit", "scan__session__name",  "scan__datetime"
			))
scan_level = scan_level_pd.iloc[0].to_dict()


# make a 2 column dataFrame for the data needed to plot
reading_level = pd.DataFrame(
            qs.values("frequency", "intensity")
        )


with open("test_file.csv", 'w') as f:
    # Write metadata as comments
    for key, value in scan_level.items():
        f.write(f"{key}: {value}\n")
    # Use StringIO to get CSV data as a 
    f.write(f"---------------------------\n")
    csv_buffer = StringIO()
    reading_level.to_csv(csv_buffer, index=False, sep=',')
    f.write(csv_buffer.getvalue())