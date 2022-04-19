from django.urls import reverse
from rest_framework import status
from .models import Agency
from rest_framework.test import APITestCase
from django.test import TestCase
from gtfs import loadfeeds

class LoadfeedsTests(TestCase):

    def test_loadfeeds(self):
        """
        Ensure ingest of known gtfs file produces expected values for agency url 
        and number of routes in database
        """
        loadfeeds.main('cata')
        qs = Agency.objects.filter(agency_name='CATA')
        num_routes = qs[0].route_set.count()
        self.assertIs(num_routes, 9)
        self.assertEqual(qs[0].agency_url, 'http://www.catabus.com')

class AgencyTests(APITestCase):
    def test_create_account(self):
        """
        Ensure we can create a new agency object.
        """
        print("Hi!")
        url = reverse('agency_list')
        data = {
            'name': 'TestAgency',
            'agency_id': 'TestAgency',
            'agency_name': 'TestAgency',
            'agency_url': 'www.example.com'
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agency.objects.count(), 1)
        self.assertEqual(Agency.objects.get().agency_id, 'TestAgency')