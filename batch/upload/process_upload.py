import click
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from shutil import unpack_archive, ReadError
import glob
import os
import csv
import copy
import json
import datetime
from geojson import LineString, MultiLineString, Feature
import logging

from django_api import DjangoAPI

logging.basicConfig()
LOG = logging.getLogger()

@click.command()
@click.option('--count', default=3, help='Number of greetings.')
@click.option('--name', default="Luke",
              help='The person to greet.')
@click.option('--data_source_id', default="None",
              help='Datasource to gather')
def hello(count, name, data_source_id):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")
    click.echo(f"Gather data source {data_source_id}!")
    api = DjangoAPI()
    data_source_update_obj = {
        "last_upload": str(datetime.datetime.now())
    }
    data_source_response = api.get(f"datasource/{data_source_id}/")
    data_source_json = data_source_response.json()
    data_source_upload_detail = process_zip(data_source_json,api)
    data_source_update_obj.update(data_source_upload_detail)
    response = api.put(f"datasource/{data_source_id}/update",data_source_update_obj, raise_for_status=False)
    if not response.ok:
        click.echo(response.json())

def list_route_ids(dd,agency_id):
    # gets all the unique route_id's in routes.txt
    if "agency_id" in next(iter(dd["routes"]), None):
        click.echo("agency_id is in routes")
        return list(
            set(
                [t["route_id"] for t in dd["routes"] if t["agency_id"] == agency_id and t["route_type"] == "3"]
            )
        )
    else:
        click.echo("agency_id not in routes")
        return list(set([t["route_id"] for t in dd["routes"] if t["route_type"] == "3"]))

def write_route_fields(dd,route,obj):
    # write route fields to obj
    this_route = next(
        iter([r for r in dd["routes"] if r["route_id"] == route]), None
    )
    for k in this_route:
        obj[k] = this_route[k]
    return obj

def get_shape_ids_for_route(trip_for_route):
    # get shape ids for route, a shape id is valid if used in a trip associated with the route
    shape_for_route = []
    for t in trip_for_route:
        if t.get("shape_id", None) not in shape_for_route:
            shape_for_route.append(t.get("shape_id", None))
    return shape_for_route

def get_route_lss_and_distance(dd,shape_for_route, unzip_path):
    #get the MultiLineString and distance for a route
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
        geos_ls = LineString(shape_geo)
        route_lss.append(geos_ls)

    try:
        dst_for_route_shapes = sum(dst_for_route_shapes) / len(
            dst_for_route_shapes
        )
    except:
        dst_for_route_shapes = 0
    return MultiLineString(route_lss), dst_for_route_shapes

def assign_trips_per_day(trip_for_route,cal_matrix,bad_service_ids_route,obj):
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
        obj[f"trips_{k}"] = cal_object[k]
    return obj
    


def read_write_gtfs(dd, data_source_obj, unzip_path, api ):
    data_source_id = data_source_obj["id"]
    return_obj = {}
    try:
        cal_matrix = get_cal_matrix(dd)
    except:
        return_obj["cal_matrix"] = False
        pass

    ####
    # update agency db record
    ####

    if "agency" not in dd:
        return_obj["agency_file"] = False
        return return_obj

    bad_service_ids = []

    for agencydd in dd["agency"]:
        agencydd = {**agencydd, "name": agencydd["agency_name"]}
        if "agency_id" not in agencydd:
            agencydd["agency_id"] = agencydd["name"]
        response = api.post(f"datasource/{data_source_id}/agency/", agencydd)
        agency_obj = response.json()
        agency_uuid, agency_id = agency_obj["id"], agency_obj["agency_id"]

        click.echo(f"agency_uuid: ${agency_uuid}")

        uu_routes = list_route_ids(dd,agency_id)

        click.echo("ready to write # route: {}".format(len(uu_routes)))

        for route in uu_routes:

            bad_service_ids_route = []

            obj = {"agency_id": agency_id}
            obj = write_route_fields(dd,route,obj)

            ####
            # write routes geo to obj
            ####
            trip_for_route = [t for t in dd["trips"] if t["route_id"] == route]
            shape_for_route = get_shape_ids_for_route(trip_for_route)
            route_lss, dst_for_route_shapes = get_route_lss_and_distance(dd,shape_for_route, unzip_path)
            geometry = route_lss
            obj["route_distance"] = dst_for_route_shapes

            ####
            # number of trips per day
            ####
            obj = assign_trips_per_day(trip_for_route,cal_matrix,bad_service_ids_route,obj)
            
            click.echo("bad service_ids per route {}".format(len(bad_service_ids_route)))

            for bsid in bad_service_ids_route:
                if bsid not in bad_service_ids:
                    bad_service_ids.append(bsid)

            ####
            # write route obj to database
            ####

            
            if obj["route_type"] == "3":
                    #write_route_to_db(obj)
                    data = Feature(geometry=geometry, properties=obj)
                    response = api.post(f"agency/{agency_uuid}/batch/route", data, raise_for_status=False)
                    if not response.ok:
                        click.echo(response.json())
            

    # uu_service_ids = list(set([t["service_id"] for t in dd["trips"]]))
    # click.echo("the agency has {} unique service ids".format(len(uu_service_ids)))

    # uu_trips = list(set([t["trip_id"] for t in dd["trips"]]))
    # click.echo("the agency has {} unique trips ".format(len(uu_trips)))

    # uu_shapes = list(set([t["shape_id"] for t in dd["shapes"]]))
    # click.echo("the agency has {} unique shapes ".format(len(uu_shapes)))

    # return_obj["uu_service_ids"] = len(uu_service_ids)
    # return_obj["uu_trips"] = len(uu_trips)
    # return_obj["uu_shapes"] = len(uu_shapes)

    # if len(bad_service_ids) > 0:
    #     if "bad_service_ids" not in return_obj:
    #         return_obj["bad_service_ids"] = bad_service_ids
    #     else:
    #         return_obj["bad_service_ids"].extend(bad_service_ids)
    #         return_obj["bad_service_ids"] = list(set(return_obj["bad_service_ids"]))

    # return return_obj

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

def process_zip(data_source_obj,api):
    zipurl = data_source_obj["urls_latest"]
    if not zipurl:
        zipurl = data_source_obj["urls_direct_download"]
    if not zipurl:
        return { "last_upload_status": "gtfs file not found"}
    unzip_path = "/tmp/gtfs"
    with urlopen(zipurl) as zipresp, NamedTemporaryFile() as tfile:
        tfile.write(zipresp.read())
        tfile.seek(0)
        try:
            unpack_archive(tfile.name, unzip_path, format = 'zip')
        except ReadError as e:
            return { "last_upload_status": f"shutil ReadError: {e}"}

    print(tfile.name)
    os.remove(unzip_path + "/stop_times.txt")
    print(os.listdir(unzip_path))
    filenames = glob.glob(unzip_path + "/*.txt")
    dd = make_data_dict(filenames)
    try:
        return_obj = read_write_gtfs(dd, data_source_obj, unzip_path, api)
    except:
        return { "last_upload_status": "failed"} 
    return { "last_upload_status": "completed"}

    #         az_obj = return_obj
    #         for f in glob.glob(pth + "/*.txt"):
    #             os.remove(f)
    #     return az_obj
    # else:
    #     return {"bad_zipfile": True}  # bad zipfile

if __name__ == '__main__':
    hello()


    #python hello.py --count=3