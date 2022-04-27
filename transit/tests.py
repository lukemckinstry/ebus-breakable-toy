from django.urls import reverse
from rest_framework import status
from .models import Agency, Route
from rest_framework.test import APITestCase
from django.test import TestCase
from django.core.management import call_command
import json


class LoadfeedsTests(TestCase):
    def test_loadfeeds(self):
        """
        Ensure ingest of known gtfs file produces expected values for agency url
        and number of routes in database
        """
        args = ["--debug"]
        opts = {}
        call_command("loadfeeds", *args, **opts)

        qs = Agency.objects.filter(agency_name="CATA")
        num_routes = qs[0].route_set.count()
        self.assertIs(num_routes, 9)
        self.assertEqual(qs[0].agency_url, "http://www.catabus.com")


def create_agency(self):
    url = reverse("agency-list")
    data = {
        "name": "TestAgency",
        "agency_id": "TestAgency",
        "agency_name": "TestAgency",
        "agency_url": "www.example.com",
    }
    response = self.client.post(url, data, format="json")
    return response


def create_route(self, agency):
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
        "zev_charging_infrastrucutre": "False",
        "zev_notes": "",
        "pct_zev_service": "0.0",
        "num_zev": "0",
    }
    response = self.client.post(url, data, format="json")
    return response


class AgencyTests(APITestCase):
    def test_create_agency(self):
        """
        Ensure we can create a new agency object.
        """
        response = create_agency(self)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agency.objects.count(), 1)
        self.assertEqual(Agency.objects.get().agency_id, "TestAgency")


class RouteTests(APITestCase):
    def test_create_route(self):
        """
        Ensure we can create a new route object.
        """
        _ = create_agency(self)
        agency = Agency.objects.get()
        response = create_route(self, agency)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(Route.objects.get().route_id, "999")

    def test_list_route_by_agency(self):
        """
        Ensure we can list route objects by agency.
        """
        _ = create_agency(self)
        agency = Agency.objects.get()
        create_route(self, agency)
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
        _ = create_agency(self)
        agency = Agency.objects.get()
        _ = create_route(self, agency)
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
            "zev_charging_infrastrucutre": "False",
            "zev_notes": "",
            "pct_zev_service": "0.0",
            "num_zev": "0",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(Route.objects.get().route_id, "888")
