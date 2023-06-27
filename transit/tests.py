from django.urls import reverse
from rest_framework import status
from .models import Agency, Route, DataSource
from transit.user.models import User
from .views import RouteViewSet
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.test import TestCase
from django.core.management import call_command
import json
from django.contrib.gis.geos import GEOSGeometry

class LoadfeedsTests(TestCase):
    def test_loadfeeds(self):
        """
        Ensure ingest of known gtfs file produces expected values for agency url
        and number of routes in database
        """
        args = ["--debug", "--sample"]
        opts = {}
        call_command("loadfeeds", *args, **opts)

        qs = Agency.objects.get(agency_name="CATA")
        num_routes = qs.route_set.count()
        self.assertIs(num_routes, 9)
        self.assertEqual(qs.agency_url, "http://www.catabus.com")


def create_user(self):
    url = reverse("user-register")
    data = {"email": "test@admin.com", "username": "test", "password": "test"}
    response = self.client.post(url, data, format="json")
    return response


def create_data_source(self):
    url = reverse("data-source-list")
    data = {
    "name": "test",
    "mdb_source_id": "1234",
    "location_country_code": "US",
    "location_subdivision_name": "Anystate",
    "location_municipality": "Anytown",
    "provider": "transit agency"
    }
    response = self.client.post(url, data, format="json")

    return response


def create_agency(self, data_source):
    test_data_source_id = data_source.id
    url = reverse("data-source-agency-list", args=[
                test_data_source_id,
            ],)
    data = {
        "name": "TestAgency",
        "agency_id": "TestAgency",
        "agency_name": "TestAgency",
        "agency_url": "www.example.com",
    }
    response = self.client.post(url, data, format="json")

    return response



def create_route(self, agency, user):
    test_agency_uuid = agency.id
    url = reverse("route-create")
    data = {
        "route_id": "999",
        "agency": test_agency_uuid,
        "route_short_name": "",
        "route_long_name": "",
        "route_desc": "Test desc",
        "route_type": "3",
        "route_url": "",
        "route_color": "",
        "route_text_color": "",
        "route_sort_order": "",
        "trips_monday": "0",
        "trips_tuesday": "0",
        "trips_wednesday": "0",
        "trips_thursday": "0",
        "trips_friday": "0",
        "trips_saturday": "0",
        "trips_sunday": "0",
        "zev_charging_infrastructure": "False",
        "zev_notes": "",
        "pct_zev_service": "0.0",
        "num_zev": "0",
    }

    factory = APIRequestFactory()
    view = RouteViewSet.as_view({"post": "create"})

    request = factory.post(url, data, format="json")
    force_authenticate(request, user=user)
    response = view(request)

    return response

geom_1 = { "type": "MultiLineString",
    "coordinates": [
        [ [100.0, 0.0], [101.0, 1.0] ],
        [ [102.0, 2.0], [103.0, 3.0] ]
  ] }

geom_2 = { "type": "MultiLineString",
    "coordinates": [
        [ [50.0, 0.0], [51.0, 1.0] ],
        [ [52.0, 2.0], [53.0, 3.0] ]
  ] }

def data_for_route_with_geometry(geom):
    data = {
        "type": "Feature",
        "geometry": geom
        ,
        "properties":
        {
            "route_id": "999",
            "route_short_name": "W",
            "route_long_name": "W",
            "route_desc": "",
            "route_type": "3",
            "route_url": "http://realtime.catabus.com/InfoPoint/46",
            "route_color": "999900",
            "route_text_color": "FFFFFF",
            "route_sort_order": "21",
            "route_distance": 41527.6023805,
            "trips_monday": 0,
            "trips_tuesday": 0,
            "trips_wednesday": 0,
            "trips_thursday": 0,
            "trips_friday": 0,
            "trips_saturday": 0,
            "trips_sunday": 0
        }
    }
    return data
    


class DataSourceTests(APITestCase):
    def test_create_data_source(self):
        """
        Ensure we can create a new data source object.
        """
        response = create_data_source(self)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DataSource.objects.count(), 1)
        self.assertEqual(DataSource.objects.get().mdb_source_id, "1234")


class AgencyTests(APITestCase):
    def test_create_agency(self):
        """
        Ensure we can create a new agency object.
        """
        _ = create_data_source(self)
        data_source = DataSource.objects.get()
        response = create_agency(self, data_source)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agency.objects.count(), 1)
        self.assertEqual(Agency.objects.get().agency_id, "TestAgency")
        # test upsert on post
        response = create_agency(self, data_source)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agency.objects.count(), 1)


class RouteTests(APITestCase):
    def test_create_route(self):
        """
        Ensure we can create a new route object.
        """
        _ = create_data_source(self)
        data_source = DataSource.objects.get()
        _ = create_agency(self, data_source)
        agency = Agency.objects.get()
        _ = create_user(self)
        user = User.objects.get()
        response = create_route(self, agency, user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(Route.objects.get().route_id, "999")

    def test_list_route_by_agency(self):
        """
        Ensure we can list route objects by agency.
        """
        _ = create_data_source(self)
        data_source = DataSource.objects.get()
        _ = create_agency(self, data_source)
        agency = Agency.objects.get()
        _ = create_user(self)
        user = User.objects.get()
        create_route(self, agency, user)
        test_agency_uuid = agency.id
        url = reverse(
            "route-list",
            args=[
                test_agency_uuid,
            ],
        )

        response = self.client.get(url, format="json")
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)

    def test_update_route(self):
        """
        Ensure we can update a route object.
        """
        _ = create_data_source(self)
        data_source = DataSource.objects.get()
        _ = create_agency(self, data_source)
        agency = Agency.objects.get()
        _ = create_user(self)
        user = User.objects.get()
        _ = create_route(self, agency, user)
        route = Route.objects.get()
        test_route_id = route.id
        url = reverse(
            "route-detail",
            args=[
                test_route_id,
            ],
        )
        data = {
            "id": test_route_id,
            "route_id": "888",
            "agency": agency.id,
            "route_short_name": "",
            "route_long_name": "",
            "route_desc": "Test desc",
            "route_type": "3",
            "route_url": "",
            "route_color": "",
            "route_text_color": "",
            "route_sort_order": "",
            "trips_monday": "0",
            "trips_tuesday": "0",
            "trips_wednesday": "0",
            "trips_thursday": "0",
            "trips_friday": "0",
            "trips_saturday": "0",
            "trips_sunday": "0",
            "zev_charging_infrastructure": "False",
            "zev_notes": "",
            "pct_zev_service": "0.0",
            "num_zev": "0",
        }

        factory = APIRequestFactory()
        view = RouteViewSet.as_view({"put": "update"})

        request = factory.put(url, data, format="json")
        force_authenticate(request, user=user)
        response = view(request, pk=test_route_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(Route.objects.get().route_id, "888")


class RouteBatchTests(APITestCase):
    def test_create_route_with_geometry(self):
        """
        Ensure we can create a new route object with geometry.
        """
        _ = create_agency(self)
        agency = Agency.objects.get()
        #_ = create_user(self)
        #user = User.objects.get()
        url = reverse("route-batch-list",
                args=[
                    agency.id,
                ],
            )
        request_data = data_for_route_with_geometry(geom_1)
        response = self.client.post(url, request_data, format='json')    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(Route.objects.get().route_id, "999")
        # test upsert on post
        response = self.client.post(url, request_data, format='json')    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.count(), 1)

    def test_update_route_with_geometry(self):
        """
        Ensure we can update a route object with geometry.
        """
        _ = create_agency(self)
        agency = Agency.objects.get()
        #_ = create_user(self)
        #user = User.objects.get()
        url = reverse("route-batch-list",
                args=[
                    agency.id,
                ],
            )
        request_data = data_for_route_with_geometry(geom_1)
        response = self.client.post(url, request_data, format='json')
        initial_geom = GEOSGeometry(str(response.data["geometry"]))
        route = Route.objects.get()
        url = reverse("route-batch-detail",
                args=[
                    route.id,
                ],
            )
        request_data = data_for_route_with_geometry(geom_2)
        response = self.client.put(url, request_data, format='json')
        updated_geom = GEOSGeometry(str(response.data["geometry"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(Route.objects.get().route_id, "999")
        self.assertEqual(initial_geom.equals(updated_geom), False)