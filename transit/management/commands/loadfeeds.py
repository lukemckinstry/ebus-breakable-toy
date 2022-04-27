import os, sys
import glob
import csv
import urllib.request
import zipfile
import logging

from django.contrib.gis.geos import LineString, MultiLineString
from django.core.management.base import BaseCommand, CommandError

from transit.models import Agency, Route

logging.basicConfig()
LOG = logging.getLogger()


def get_gtfs_agency_zips(sample):
    pwd = os.path.dirname(os.path.abspath(__file__))
    LOG.debug(pwd)
    if sample:
        LOG.info("retrieve sample gtfs file {}".format(sample))
        try:
            resultFilePath, responseHeaders = urllib.request.urlretrieve(
                sample, pwd + "/sample.zip"
            )
        except:
            LOG.error("unable to download file from url: {}".format(sample))
            return
        print(responseHeaders)
        LOG.info("saved sample gtfs file to {}".format(resultFilePath))

    files = glob.glob(pwd + "/*.zip")
    LOG.info(files)

    return files


def make_data_dict(filenames):
    g = {}
    for filename in filenames:
        d = []
        reader = csv.DictReader(open(filename))
        for r in reader:
            d.append(r)
        filelabel = os.path.basename(filename).replace(".txt", "")
        g[filelabel] = d
    return g


def get_cal_matrix(dd):
    sm = {}
    for c in dd["calendar"]:
        service_id = c["service_id"]
        sm[service_id] = c
    return sm


def write_agency_to_db(obj):

    agency_id = obj.get("agency_id", "")
    agency_name = obj.get("agency_name", "")

    if Agency.objects.filter(agency_name=agency_name, agency_id=agency_id).exists():
        a = Agency.objects.get(agency_name=agency_name, agency_id=agency_id)
        a_obj = a

    else:

        agency_url = obj.get("agency_url", "")
        agency_timezone = obj.get("agency_timezone", "")
        agency_lang = obj.get("agency_lang", "")
        agency_phone = obj.get("agency_phone", "")
        agency_fare_url = obj.get("agency_fare_url", "")
        agency_email = obj.get("agency_email", "")

        a = Agency.objects.update_or_create(
            agency_id=agency_id,
            agency_name=agency_name,
            agency_url=agency_url,
            agency_timezone=agency_timezone,
            agency_lang=agency_lang,
            agency_phone=agency_phone,
            agency_fare_url=agency_fare_url,
            agency_email=agency_email,
        )

        a_obj = a[0]

    return {"uuid": a_obj.id, "agency_id": a_obj.agency_id}


def write_route_to_db(obj):

    agency = Agency.objects.get(id=obj.get("agency_uuid"))
    route_id = obj.get("route_id", "")

    Route.objects.update_or_create(
        route_id=route_id,
        agency_id=agency.id,
        route_short_name=obj.get("route_short_name", ""),
        route_long_name=obj.get("route_long_name", ""),
        route_desc=obj.get("route_desc", ""),
        route_type=obj.get("route_type", ""),
        route_url=obj.get("route_url", ""),
        route_color=obj.get("route_color", ""),
        route_text_color=obj.get("route_text_color", ""),
        route_sort_order=obj.get("route_sort_order", ""),
        trips_monday=obj.get("monday", ""),
        trips_tuesday=obj.get("tuesday", ""),
        trips_wednesday=obj.get("wednesday", ""),
        trips_thursday=obj.get("thursday", ""),
        trips_friday=obj.get("friday", ""),
        trips_saturday=obj.get("saturday", ""),
        trips_sunday=obj.get("sunday", ""),
        mpoly=obj.get("mpoly", ""),
        route_distance=obj.get("route_distance", ""),
    )


def read_write_gtfs(dd, ziplabel):

    return_obj = {}

    try:
        cal_matrix = get_cal_matrix(dd)
    except:
        return_obj["cal_matrix"] = False
        pass

    ####
    # write agency to db
    ####

    if "agency" not in dd:
        return_obj["agency_file"] = False
        return return_obj

    bad_service_ids = []

    for agencydd in dd["agency"]:
        agency = write_agency_to_db(agencydd)
        agency_id = agency["agency_id"]
        agency_uuid = agency["uuid"]

        LOG.debug("agency_id: {} \t agency_uuid: {}".format(agency_id, agency_uuid))

        if "agency_id" in next(iter(dd["routes"]), None):
            LOG.debug("agency_id is in routes")
            uu_routes = list(
                set(
                    [t["route_id"] for t in dd["routes"] if t["agency_id"] == agency_id]
                )
            )
        else:
            LOG.debug("agency_id not in routes")
            uu_routes = list(set([t["route_id"] for t in dd["routes"]]))

        LOG.info("ready to write # route: {}".format(len(uu_routes)))

        for route in uu_routes:

            bad_service_ids_route = []

            obj = {"agency_uuid": agency_uuid}

            # write route gtfs fields to obj
            this_route = next(
                iter([r for r in dd["routes"] if r["route_id"] == route]), None
            )
            for k in this_route:
                obj[k] = this_route[k]

            # get trips for route
            trip_for_route = [t for t in dd["trips"] if t["route_id"] == route]

            ####
            # write routes geo to obj
            ####

            shape_for_route = []
            for t in trip_for_route:
                if t.get("shape_id", None) not in shape_for_route:
                    shape_for_route.append(t.get("shape_id", None))

            route_lss = []  # route geo (LineString)
            dst_for_route_shapes = []  # route distance

            for s in shape_for_route:
                ordered_shape = [
                    {
                        "lon": p["shape_pt_lon"],
                        "lat": p["shape_pt_lat"],
                        "seq": int(p["shape_pt_sequence"]),
                        "dst": p.get("shape_dist_traveled", None),
                    }
                    for p in dd["shapes"]
                    if p["shape_id"] == s
                ]

                sorted_shape = sorted(ordered_shape, key=lambda i: i["seq"])

                # shape distance
                try:
                    shape_dist = max([float(s["dst"]) for s in ordered_shape])
                except:
                    shape_dist = None
                dst_for_route_shapes.append(shape_dist)

                # shape geo
                shape_geo = [
                    tuple([float(s["lon"]), float(s["lat"])]) for s in sorted_shape
                ]
                geos_ls = LineString(shape_geo, srid=4326)
                route_lss.append(geos_ls)

            try:
                obj["route_distance"] = sum(dst_for_route_shapes) / len(
                    dst_for_route_shapes
                )
            except:
                obj["route_distance"] = 0
            obj["mpoly"] = MultiLineString(route_lss)

            ####
            # number of trips per day
            ####
            cal_object = {
                i: 0
                for i in [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]
            }

            for day in cal_object:
                for t in trip_for_route:
                    service_id = t["service_id"]
                    try:
                        if cal_matrix[service_id][day] == "1":
                            cal_object[day] += 1
                    except:
                        if service_id not in bad_service_ids_route:
                            bad_service_ids_route.append(service_id)
                        pass
            for k in cal_object:
                obj[k] = cal_object[k]

            LOG.info("bad service_ids per route {}".format(len(bad_service_ids_route)))

            for bsid in bad_service_ids_route:
                if bsid not in bad_service_ids:
                    bad_service_ids.append(bsid)

            ####
            # write route obj to database
            ####

            try:
                if obj["route_type"] == "3":
                    write_route_to_db(obj)
            except:
                pass

    uu_service_ids = list(set([t["service_id"] for t in dd["trips"]]))
    LOG.info("the agency has {} unique service ids".format(len(uu_service_ids)))

    uu_trips = list(set([t["trip_id"] for t in dd["trips"]]))
    LOG.info("the agency has {} unique trips ".format(len(uu_trips)))

    uu_shapes = list(set([t["shape_id"] for t in dd["shapes"]]))
    LOG.info("the agency has {} unique shapes ".format(len(uu_shapes)))

    return_obj["uu_service_ids"] = len(uu_service_ids)
    return_obj["uu_trips"] = len(uu_trips)
    return_obj["uu_shapes"] = len(uu_shapes)

    if len(bad_service_ids) > 0:
        if "bad_service_ids" not in return_obj:
            return_obj["bad_service_ids"] = bad_service_ids
        else:
            return_obj["bad_service_ids"].extend(bad_service_ids)
            return_obj["bad_service_ids"] = list(set(return_obj["bad_service_ids"]))

    return return_obj


def check_route_types(dd):
    route_types = {}
    for t in dd["routes"]:
        if t["route_type"] not in route_types:
            route_types[t["route_type"]] = 0
        else:
            route_types[t["route_type"]] += 1
    LOG.debug("route types ", route_types)


def process_zip(az):
    agencies = []
    az_obj = {}
    ziplabel = os.path.basename(os.path.normpath(az))
    pwd = os.path.dirname(os.path.abspath(__file__))
    if zipfile.is_zipfile(az):
        pth = pwd + "/tmp/"
        with zipfile.ZipFile(az, "r") as zip_ref:
            zip_ref.extractall(pth)
            filenames = glob.glob(pth + "/*.txt")
            dd = make_data_dict(filenames)
            return_obj = read_write_gtfs(dd, ziplabel)
            az_obj = return_obj
            for f in glob.glob(pth + "/*.txt"):
                os.remove(f)
        return az_obj
    else:
        return {"bad_zipfile": True}  # bad zipfile


def iter_agencies(agency_zips):

    LOG.info("iter_agencies")

    # display results
    statuses = {}
    # ptable = PrettyTable()

    for az in agency_zips:
        obj = process_zip(az)
        statuses[az] = obj

    for file_name in statuses:
        stat = statuses[file_name]
        msg = []
        msg.append(os.path.basename(os.path.normpath(file_name)))
        msg.append("" if "bad_zipfile" not in stat else "x")
        msg.append("" if "agency_file" not in stat else "x")
        msg.append("" if "cal_matrix" not in stat else "x")
        msg.append("" if "bad_service_ids" not in stat else stat["bad_service_ids"])
        msg.append("" if "uu_service_ids" not in stat else stat["uu_service_ids"])
        msg.append("" if "uu_trips" not in stat else stat["uu_trips"])
        msg.append("" if "uu_shapes" not in stat else stat["uu_shapes"])

    LOG.info("All done!")


class Command(BaseCommand):
    help = "Loads data from gtfs transit feed files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Set log level to debug",
        )

        parser.add_argument(
            "--sample",
            nargs="?",
            default=None,
            const="https://storage.googleapis.com/storage/v1/b/mdb-latest/o/us-pennsylvania-centre-county-transit-authority-cata-gtfs-1236.zip?alt=media",
            help="Download a sample gtfs file (option to provide a download url)",
        )

    def handle(self, *args, **options):

        if options["debug"]:
            LOG.setLevel(logging.DEBUG)
        else:
            LOG.setLevel(logging.INFO)
        LOG.info("Going to gather gtfs feed zips")
        gtfs_agency_zips = get_gtfs_agency_zips(options["sample"])
        if not gtfs_agency_zips:
            LOG.info(
                "no gtfs files found in {}, rerun script with --sample to download a file".format(
                    os.path.dirname(os.path.abspath(__file__))
                )
            )
            return
        LOG.info("zips: %s", gtfs_agency_zips)
        iter_agencies(gtfs_agency_zips)

        return
