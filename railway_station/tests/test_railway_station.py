from datetime import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from railway_station.models import TrainType, Station, Route, Train, Crew, Journey, Order, Ticket

TRAIN_TYPE_URL = reverse("railway_station:traintype-list")
JOURNEYS_URL = reverse("railway_station:journey-list")
ORDER_URL = reverse("railway_station:order-list")

class TrainTypeViewSetTest(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin"
        )
        self.normal_user = get_user_model().objects.create_user(
            email="user@user.com", password="user"
        )
        self.client = APIClient()

    def test_admin_can_create_train_type(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(TRAIN_TYPE_URL, {"name": "Cargo"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TrainType.objects.count(), 1)
        self.assertEqual(TrainType.objects.first().name, "Cargo")

    def test_user_cannot_create_train_type(self):
        self.client.force_authenticate(self.normal_user)
        response = self.client.post(TRAIN_TYPE_URL, {"name": "Express"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_train_types(self):
        TrainType.objects.create(name="Cargo")
        TrainType.objects.create(name="Express")
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)


class JourneyViewSetTest(APITestCase):
    def setUp(self):
        super().setUp()
        # Set up test data
        self.source_station = Station.objects.create(name="Source", latitude=12.34, longitude=56.78)
        self.destination_station = Station.objects.create(name="Destination", latitude=23.45, longitude=67.89)
        self.route = Route.objects.create(
            source=self.source_station, destination=self.destination_station, distance=100
        )
        self.train_type = TrainType.objects.create(name="Passenger")
        self.train = Train.objects.create(
            name="Express", cargo_num=2, places_in_cargo=50, train_type=self.train_type
        )
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=datetime(2024, 12, 24, 8, 0),
            arrival_time=datetime(2024, 12, 24, 10, 0),
        )
        self.journey.crews.add(self.crew)
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin"
        )

    def test_list_journeys(self):
        response = self.client.get(JOURNEYS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_journeys_by_source(self):
        response = self.client.get(f"{JOURNEYS_URL}?source={self.source_station.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_journey_tickets_available_annotation(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(JOURNEYS_URL)
        self.assertIn("tickets_available", response.data["results"][0])
        self.assertEqual(response.data["results"][0]["tickets_available"], 100)

