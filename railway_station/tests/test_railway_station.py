from datetime import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from railway_station.models import (
    TrainType,
    Station,
    Route,
    Train,
    Crew,
    Journey, Order,
)

TRAIN_TYPES_URL = reverse("railway_station:traintype-list")
TRAINS_URL = reverse("railway_station:train-list")
CREWS_URL = reverse("railway_station:crew-list")
STATIONS_URL = reverse("railway_station:station-list")
ROTES_URL = reverse("railway_station:route-list")
JOURNEYS_URL = reverse("railway_station:journey-list")
ORDERS_URL = reverse("railway_station:order-list")
TICKETS_URL = reverse("railway_station:ticket-list")

class PermissionsTest(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin"
        )
        self.normal_user = get_user_model().objects.create_user(
            email="user@user.com", password="user"
        )
        self.client = APIClient()

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

    def admin_only_pages(self):
        response = self.client.get(TRAIN_TYPES_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(TRAINS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(CREWS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(STATIONS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(ROTES_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def admin_only_edit_pages(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.patch(
            f"{JOURNEYS_URL}1/",
            {
                "departure_time": datetime(2025,11,2,12,30,0)
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class JourneyViewSetTest(APITestCase):
    def setUp(self):
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

        self.client = APIClient()

        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin"
        )
        self.normal_user = get_user_model().objects.create_user(
            email="user@user.com", password="user"
        )

    def test_filter_journeys_by_source(self):
        response = self.client.get(f"{JOURNEYS_URL}?source={self.source_station.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_journey_tickets_available_annotation(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(JOURNEYS_URL)
        self.assertIn("tickets_available", response.data["results"][0])
        self.assertEqual(response.data["results"][0]["tickets_available"], 100)


class RouteViewSetTest(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="admin"
        )
        self.normal_user = get_user_model().objects.create_user(
            email="user@user.com", password="user"
        )
        self.client = APIClient()

        self.source = Station.objects.create(name="Source", latitude=12.34, longitude=56.78)
        self.destination = Station.objects.create(name="Destination", latitude=23.45, longitude=67.89)

    def test_create_route_with_invalid_data(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(
            ROTES_URL,
            {
                "source": self.source,
                "destination": self.source,
                "distance": 1
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(
            ROTES_URL,
            {
                "source": self.source,
                "destination": self.destination,
                "distance": -1
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class OrderViewSetTest(APITestCase):
    def setUp(self):
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

        self.client = APIClient()
        self.normal_user = get_user_model().objects.create_user(
            email="user@user.com", password="user"
        )

    def test_create_order_with_invalid_data(self):
        self.client.force_authenticate(self.normal_user)
        response = self.client.post(
            ORDERS_URL,
            {
                "tickets": [
                    {
                        "cargo": 3,
                        "seat": 1,
                        "journey": self.journey.id,
                    }
                ]
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_make_two_tickets_with_same_place(self):
        self.client.force_authenticate(self.normal_user)
        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "journey": self.journey.id,
                }
            ]
        }
        response = self.client.post(ORDERS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(ORDERS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TicketViewSetTest(APITestCase):
    def setUp(self):
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

        self.client = APIClient()
        self.first_user = get_user_model().objects.create_user(
            email="user@user.com", password="user"
        )
        self.second_user = get_user_model().objects.create_user(
            email="user2@user.com", password="user2"
        )

    def test_show_only_own_tickets(self):
        self.client.force_authenticate(self.first_user)
        response = self.client.post(
            ORDERS_URL,
            {
                "tickets": [
                    {
                        "cargo": 1,
                        "seat": 1,
                        "journey": self.journey.id,
                    }
                ]
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(TICKETS_URL)
        self.assertEqual(len(response.data["results"]), 1)

        self.client.force_authenticate(self.second_user)
        response = self.client.get(TICKETS_URL)
        self.assertEqual(len(response.data["results"]), 0)


