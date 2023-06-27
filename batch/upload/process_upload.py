import click
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from shutil import unpack_archive, ReadError
import glob
import os
import csv
import datetime
from geojson import LineString, MultiLineString, Feature
import logging

from django_api import DjangoAPI

logging.basicConfig()
LOG = logging.getLogger()

@click.command()
@click.option('--data_source_id', default="None",
              help='Datasource to gather')
def hello(data_source_id):
    click.echo(f"Gather data source {data_source_id}!")
    
    data_source_uploader = DataSourceUploader(data_source_id)
    
    data_source_uploader.get_data_source_from_api()
    data_source_uploader.unzip_to_file_paths()
    data_source_uploader.file_paths_to_data_dict()
    data_source_uploader.get_cal_matrix()

    for agency_data_dict in data_source_uploader.data_dict["agency"]:
        agency_uploader = AgencyUploader(data_source_uploader,agency_data_dict)
        agency_uploader.post_agency_to_api()
        agency_uploader.get_route_ids()

        for route_id in agency_uploader.agency_routes_list:
            route_uploader = RouteUploader(data_source_uploader,agency_uploader, route_id)
            route_uploader.write_route_fields()
            route_uploader.get_shape_ids_for_route()
            route_uploader.get_route_lss_and_distance()
            route_uploader.assign_trips_per_day()
            route_uploader.post_route_to_api()

    data_source_uploader.record_upload_status()


class DataSourceUploader():    
    def __init__(self,data_source_id):
        self.api = DjangoAPI()
        self.data_source_id = data_source_id
        self.data_source_update_obj = {
            "last_upload": str(datetime.datetime.now())
        }
        self.data_source_obj = {}
        self.filenames = []
        self.data_dict = {}
        self.cal_matrix = {}
        
    def get_data_source_from_api(self):
        data_source_response = self.api.get(f"datasource/{self.data_source_id}/")
        self.data_source_obj = data_source_response.json()
    
    def record_upload_status(self):
        self.api.put(f"datasource/{self.data_source_id}/update",self.data_source_update_obj)

    def unzip_to_file_paths(self):
        #unzip the gtfs data and return the local filepaths
        zipurl = self.data_source_obj["urls_latest"]
        if not zipurl:
            zipurl = self.data_source_obj["urls_direct_download"]
        if not zipurl:
            self.data_source_update_obj.update({ "last_upload_status": "gtfs file not found"})
        unzip_path = "/tmp/gtfs"
        with urlopen(zipurl) as zipresp, NamedTemporaryFile() as tfile:
            tfile.write(zipresp.read())
            tfile.seek(0)
            try:
                unpack_archive(tfile.name, unzip_path, format = 'zip')
            except ReadError as e:
                self.data_source_update_obj.update({ "last_upload_status": f"shutil ReadError: {e}"})
        os.remove(unzip_path + "/stop_times.txt")
        self.filenames = glob.glob(unzip_path + "/*.txt")
        if unzip_path+"/shapes.txt" not in self.filenames:
            raise Exception("shapes.txt is missing from gtfs data")
        
    def file_paths_to_data_dict(self):
        g = {}
        for filename in self.filenames:
            d = []
            reader = csv.DictReader(open(filename))
            for r in reader:
                d.append(r)
            filelabel = os.path.basename(filename).replace(".txt", "")
            g[filelabel] = d
        self.data_dict = g

    def get_cal_matrix(self):
        if "calendar" not in self.data_dict:
            return
        sm = {}
        for c in self.data_dict["calendar"]:
            service_id = c["service_id"]
            sm[service_id] = c
        self.cal_matrix = sm


class AgencyUploader():
    def __init__(self, data_source, agency_obj):
        self.data_source = data_source
        self.agency_obj = agency_obj
        self.agency_obj_to_post = {**self.agency_obj, "name": self.agency_obj["agency_name"]}
        self.agency_routes_list = []

    def post_agency_to_api(self):
        if "agency_id" not in self.agency_obj_to_post:
            # handle edge case where an agency.txt file omits agency_id
            self.agency_obj_to_post["agency_id"] = self.agency_obj_to_post["name"]
        response = self.data_source.api.post(f"datasource/{self.data_source.data_source_id}/agency/", self.agency_obj_to_post)
        self.agency_obj = response.json()

    def get_route_ids(self):
        # get all the unique route_ids in routes.txt
        if "agency_id" in self.agency_obj:
            self.agency_routes_list = list(
                set(
                    [t["route_id"] for t in self.data_source.data_dict["routes"] if t["agency_id"] == self.agency_obj["agency_id"] and t["route_type"] == "3"]
                )
            )
        else:
            self.agency_routes_list = list(set([t["route_id"] for t in self.data_source.data_dict["routes"] if t["route_type"] == "3"]))


class RouteUploader():
    def __init__(self, data_source, agency, route_id):
        self.data_source = data_source
        self.agency = agency
        self.obj = {}
        self.bad_service_ids_route = []
        self.route_id = route_id
        self.trip_for_route = [t for t in self.data_source.data_dict["trips"] if t["route_id"] == self.route_id]
        self.shape_for_route = []
        self.geometry = None
        self.dst_for_route_shapes = 0

    def write_route_fields(self):
        # write route fields to obj
        this_route = next(
            iter([r for r in self.data_source.data_dict["routes"] if r["route_id"] == self.route_id]), None
        )
        for k in this_route:
            self.obj[k] = this_route[k]

    def get_shape_ids_for_route(self):
        # get shape ids for route, a shape id is valid if used in a trip associated with the route
        shape_for_route = []
        for t in self.trip_for_route:
            if t.get("shape_id", None) not in shape_for_route:
                shape_for_route.append(t.get("shape_id", None))
        self.shape_for_route = shape_for_route

    def get_route_lss_and_distance(self):
        # use shapes to get the MultiLineString and distance for a route
        route_lss = []  # route geo (LineString)
        dst_for_route_shapes = []  # route distance

        for s in self.shape_for_route:
            ordered_shape = [
                {
                    "lon": p["shape_pt_lon"],
                    "lat": p["shape_pt_lat"],
                    "seq": int(p["shape_pt_sequence"]),
                    "dst": p.get("shape_dist_traveled", None),
                }
                for p in self.data_source.data_dict["shapes"]
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
        self.geometry = MultiLineString(route_lss)
        self.obj["route_distance"] = dst_for_route_shapes

    def assign_trips_per_day(self):
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
            for t in self.trip_for_route:
                service_id = t["service_id"]
                try:
                    if self.data_source.cal_matrix[service_id][day] == "1":
                        cal_object[day] += 1
                except:
                    if service_id not in self.bad_service_ids_route:
                        self.bad_service_ids_route.append(service_id)
                    pass
        for k in cal_object:
            self.obj[f"trips_{k}"] = cal_object[k]

    def post_route_to_api(self):
        if self.obj["route_type"] == "3":
            agency_uuid = self.agency.agency_obj["id"]
            data = Feature(geometry=self.geometry, properties=self.obj)
            self.data_source.api.post(f"agency/{agency_uuid}/batch/route", data)


if __name__ == '__main__':
    hello()