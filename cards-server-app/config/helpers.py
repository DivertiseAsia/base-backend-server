from rest_framework.test import APITestCase
from rest_framework import status
from django.utils.http import urlencode
from django.shortcuts import resolve_url
from django.utils.safestring import SafeText
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils.html import format_html

from user_manager.models import User


def model_admin_url(obj, name: str = None) -> str:
    """
    Creates a URL to the model admin of a particular object

    via: https://stackoverflow.com/questions/6418592/django-admin-linking-to-related-objects
    """
    url = resolve_url(admin_urlname(obj._meta, SafeText("change")), obj.pk)
    return format_html('<a href="{}">{}</a>', url, name or str(obj))


class BaseTestCase(APITestCase):
    def setUp(self):
        self.current_user = None
        self.url = None
        self.query_params = None
        self.response = None
        self.response_json = None

    def given_query_params(self, query_params):
        self.query_params = query_params

    def given_url(self, url):
        self.url = url

    def given_a_new_user(
        self, email="someemail@divertise.asia", password="irrelevant", role=None
    ):
        return User.objects.create_user(email, password=password, role=role)

    def given_logged_in_as_user(self, user):
        self.current_user = user
        self.client.force_login(user)

    def when_user_gets_json(self):
        self.response = self.client.get(self.url, self.query_params, format="json")
        self.response_json = self.response.json()
        return self.response_json

    def when_user_updates_and_gets_json(self, data):
        if self.query_params is not None:
            r = {
                "QUERY_STRING": urlencode(self.query_params, doseq=True),
            }
            self.response = self.client.put(self.url, data, format="json", **r)
        else:
            self.response = self.client.put(self.url, data, format="json")
        self.response_json = self.response.json()
        return self.response_json

    def when_user_posts_and_gets_json(self, data):
        if self.query_params is not None:
            r = {
                "QUERY_STRING": urlencode(self.query_params, doseq=True),
            }
            self.response = self.client.post(self.url, data, format="json", **r)
        else:
            self.response = self.client.post(self.url, data, format="json")
        self.response_json = self.response.json()
        return self.response_json

    def when_user_deletes(self):
        if self.query_params is not None:
            r = {
                "QUERY_STRING": urlencode(self.query_params, doseq=True),
            }
            self.response = self.client.delete(self.url, format="json", **r)
        else:
            self.response = self.client.delete(self.url, format="json")

    def assertResponseSuccess(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def assertResponseCreated(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def assertResponseDeleteSuccess(self):
        self.assertEqual(self.response.status_code, status.HTTP_204_NO_CONTENT)

    def assertResponseBadRequest(self):
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    def assertResponseNotAuthorized(self):
        self.assertEqual(self.response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assertResponseForbidden(self):
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)

    def assertResponseNotFound(self):
        self.assertEqual(self.response.status_code, status.HTTP_404_NOT_FOUND)
