import os
import json

import requests

""" A utility function to get a JWT token, using a refresh token from the environment. """


def get_jwt_from_django_api(issuer) -> str:
    username = os.getenv("BATCH_UPLOAD_USERNAME")
    email = os.getenv("BATCH_UPLOAD_EMAIL")
    password = os.getenv("BATCH_UPLOAD_PASSWORD")
    response = requests.post(
        f"{issuer}/user/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data= {
            "username": username,
            "email": email,
            "password": password
        }
    )
    response.raise_for_status()
    return response.json()["access"]


class DjangoAPI:
    """Encapsulate authenticating and making requests to the Django API"""

    def __init__(self, headers=None) -> None: 
        self.url_base = f"{os.getenv('DJANGO_API_HOST')}/api"
        print("url_base --> ", self.url_base)
        jwt = get_jwt_from_django_api(self.url_base)
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {jwt}"})
        if headers is not None:
            self.session.headers.update(headers)

    def get(self, endpoint, params=None, raise_for_status=True):
        """Runs a GET request to the API, using the JWT bearer token, and returns the response."""
        response = self.session.get(
            f"{self.url_base}/{endpoint}",
            params=params,
        )
        if raise_for_status:
            response.raise_for_status()
        return response

    def _save(self, method, endpoint, json_data, raise_for_status=True):
        response = getattr(self.session, method)(
            f"{self.url_base}/{endpoint}",
            json=json_data,
        )
        if raise_for_status:
            response.raise_for_status()
        return response

    def post(self, endpoint, json_data, raise_for_status=True):
        return self._save("post", endpoint, json_data, raise_for_status)

    def put(self, endpoint, json_data, raise_for_status=True):
        return self._save("put", endpoint, json_data, raise_for_status)

    def patch(self, endpoint, json_data, raise_for_status=True):
        return self._save("patch", endpoint, json_data, raise_for_status)