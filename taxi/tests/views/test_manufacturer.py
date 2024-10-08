from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Manufacturer


MANUFACTURER_LIST_URL = reverse("taxi:manufacturer-list")


class PublicManufacturerListViewTest(TestCase):
    def test_login_required(self):
        response = self.client.get(MANUFACTURER_LIST_URL)
        self.assertNotEqual(response.status_code, 200)


class PrivateManufacturerListViewTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="username",
            password="password"
        )
        self.client.force_login(user)
        num_of_manufacturers = 7
        for i in range(num_of_manufacturers):
            Manufacturer.objects.create(
                name=f"Name №{i}",
                country=f"Country {i}"
            )

    def test_retrieve_manufacturers(self):
        response = self.client.get(MANUFACTURER_LIST_URL)
        self.assertEqual(response.status_code, 200)

        manufacturers = Manufacturer.objects.all()
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            list(manufacturers[:5])
        )
        self.assertTrue("search_form" in response.context)
        self.assertTemplateUsed(response, "taxi/manufacturer_list.html")

    def test_pagination_is_five(self):
        response = self.client.get(MANUFACTURER_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["manufacturer_list"]), 5)

    def test_second_pagination_page(self):
        response = self.client.get(MANUFACTURER_LIST_URL + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["manufacturer_list"]), 2)

    def test_valid_search(self):
        name = "№1"
        response = self.client.get(MANUFACTURER_LIST_URL + f"?name={name}")
        self.assertEqual(response.status_code, 200)

        expected_manufacturer = Manufacturer.objects.filter(
            name__icontains=name
        )
        self.assertIsNotNone(expected_manufacturer)
        self.assertTrue(expected_manufacturer.exists())
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            list(expected_manufacturer)
        )

    def test_search_not_found(self):
        response = self.client.get(MANUFACTURER_LIST_URL + "?name=invalid}")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context["manufacturer_list"]), 0)
