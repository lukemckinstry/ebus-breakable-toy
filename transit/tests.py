from django.urls import reverse
from rest_framework import status
from .models import Agency
from rest_framework.test import APITestCase


class AgencyTests(APITestCase):
    def test_create_account(self):
        """
        Ensure we can create a new agency object.
        """
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