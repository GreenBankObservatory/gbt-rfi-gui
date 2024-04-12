"""Ingest RFI data from CHIME files into the "CHIME" RFI DB."""

import glob
import numpy as np
import sys
import astropy.units as u
from datetime import timezone, timedelta
from pathlib import Path
from tqdm import tqdm

from django.core.management.base import BaseCommand

from rfi.models import Frequency, Scan, Frontend, Backend, Coordinates, Source, Feed, FrequencyType, Polarization, Project, File, Session

class Command(BaseCommand):
    help = "Ingest data from CHIME data files into the 'CHIME' RFI DB"

    def handle_scan(self, intensities, timestamp, frequencies, session_path, scan_num):
        """Handle a single row from CHIME file

        Each row represents information for a given frequency of a given session
        """

        # one value per row
        session_name = session_path.split("/")[-1]
        frontend, _ = Frontend.objects.get_or_create(name="CHIME")
        backend, _ = Backend.objects.get_or_create(name="CHIME")
        coordinates, _ = Coordinates.objects.get_or_create(azimuth=0, elevation=0)
        source, _ = Source.objects.get_or_create(name="CHIME")
        feed, _ = Feed.objects.get_or_create(number=0, frontend=frontend)
        frequency_type, _ = FrequencyType.objects.get_or_create(name="CHIME")
        polarization, _ = Polarization.objects.get_or_create(name="CHIME")
        project, _ = Project.objects.get_or_create(name="foo")
        file, _ = File.objects.get_or_create(name=session_name, path=session_path)
        session, _ = Session.objects.get_or_create(name=session_name, project=project, file=file)

        scan_to_create = Scan(
                session=session,
                feed=feed,
                frontend=frontend,
                backend=backend,
                coordinates=coordinates,
                source=source,
                frequency_type=frequency_type,
                polarization=polarization,

                number=scan_num,
                mjd=0,
                datetime=timestamp,
                lst=0,
                resolution=0,
                exposure=0,
                tsys=0,
                unit="Jy",
        )


        frequencies_to_create = []
        assert len(frequencies) == len(intensities)
        for f, i in list(zip(frequencies, intensities)):
            frequency = Frequency(
                scan=scan_to_create,
                window=0,
                channel=0,
                frequency=f,
                intensity=i,
            )
            frequencies_to_create.append(frequency)
            # return frequency
        return scan_to_create, frequencies_to_create

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            help="To do a full re-ingestion, use this option. "
            "You will get integrity errors if you use this on a non-empty rfi_query DB",
        )
        parser.add_argument(
            "--rfi-data-path",
            type=Path,
            help="The path to the directory holding our CHIME data files",
            default="/home/scratch/dbautist/CHIME_backup",
        )

    def handle_session(self, intensities, start, end, session):
        """
        Convert the numpy data to DB objects, per session
        """

        # min/max'ed freq. linspace
        frequency = np.linspace(400e6, 800e6, num=1024)*u.Hz
        frequency = frequency.to(u.MHz).value

        # min/max'ed time range
        start_time = start[()].astimezone(timezone.utc)
        end_time = end[()].astimezone(timezone.utc)
        dt = (end_time - start_time).seconds / intensities.shape[0]
        timestamps = [start_time + timedelta(seconds=dt*i) for i in range(len(intensities))]
        all_scan_to_create: list[Scan] = []
        all_frequencies_to_create: list[Frequency] = []
        for scan_num,[ts, intensity] in tqdm(list(enumerate(zip(timestamps, intensities), 1))):
            scan_to_create, frequencies_to_create = self.handle_scan(intensity, ts, frequency, session, scan_num)
            
            all_scan_to_create.append(scan_to_create)
            all_frequencies_to_create.extend(frequencies_to_create) 


        scans_created = Scan.objects.bulk_create(all_scan_to_create, batch_size=20_000)
        print(f"Successfully created {len(scans_created)} Scans")
        freqs_created = Frequency.objects.bulk_create(all_frequencies_to_create, batch_size=20_000)
        print(f"Successfully created {len(freqs_created)} Frequencies")

    def handle(self, *args, rfi_data_path: Path, **options):

        # all projects
        # rfi_data_path = options["rfi_data_path"]
        all_sessions = list(rfi_data_path.iterdir())

        # check if project name is in DB already
        if options["full"]: 
            new_sessions = all_sessions
        else:
            new_sessions = [filename for filename in all_sessions if filename.name not in Scan.objects.values_list("session__name", flat=True).distinct()]
            # new_sessions = [rfi_data_path / session_name for session_name in Scan.objects.exclude(session__name__in=all_sessions).values_list("session__name", flat=True)]
            if not new_sessions:
                print(
                    "There are no new scans since last execution; exiting (no changes made)"
                )
                sys.exit(0)
            print(
                f"There are {len(new_sessions)} new scans since we last ran; continuing with ingestion"
            )

        # gather data
        # for i in range(len(new_sessions)):
        for session_path in tqdm(new_sessions):
            new_files = sorted(str(sp) for sp in Path(session_path).glob("*.npy"))
            # new_files = glob.glob(session_path+"/*npy")

            start_data = np.load(new_files[2], allow_pickle=True)
            end_data = np.load(new_files[1], allow_pickle=True)
            CHIME_data = np.load(new_files[0], allow_pickle=True)

            # per session ingest
            self.handle_session(intensities=CHIME_data, start=start_data, end=end_data, session=str(session_path))