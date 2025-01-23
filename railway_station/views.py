from datetime import datetime

from django.db.models import Count, F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from railway_station.models import (
    Crew,
    Journey,
    Order,
    Route,
    Station,
    Ticket,
    Train,
    TrainType
)
from railway_station.permissions import IsAdminOrReadOnly
from railway_station.serializers import (
    CrewSerializer,
    JourneyListSerializer,
    JourneyRetrieveSerializer,
    JourneySerializer,
    OrderListSerializer,
    OrderSerializer,
    RouteListSerializer,
    RouteSerializer,
    StationSerializer,
    TicketListSerializer,
    TicketSerializer,
    TrainListSerializer,
    TrainSerializer,
    TrainTypeSerializer
)


class TrainTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        return TrainSerializer


class CrewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = JourneySerializer

    def get_queryset(self):
        queryset = (
            Journey.objects.select_related(
                "train",
                "train__train_type",
                "route",
                "route__source",
                "route__destination",
            )
            .prefetch_related(
                "tickets",
                "crews",
            )
            .annotate(
                tickets_available=(
                    F("train__cargo_num") * F("train__places_in_cargo")
                    - Count("tickets")
                )
            )
        )
        route_source = self.request.query_params.get("source")
        route_destination = self.request.query_params.get("destination")

        departure_time = self.request.query_params.get("departure_time")

        arrival_time = self.request.query_params.get("arrival_time")

        if route_source:
            queryset = queryset.filter(route__source=route_source)

        if route_destination:
            queryset = queryset.filter(route__destination=route_destination)

        if departure_time:
            date = datetime.strptime(departure_time, "%Y-%m-%d").date()
            queryset = queryset.filter(
                departure_time__year=date.year,
                departure_time__month=date.month,
                departure_time__day=date.day,
            )

        if arrival_time:
            date = datetime.strptime(arrival_time, "%Y-%m-%d").date()
            queryset = queryset.filter(
                arrival__time__year=date.year,
                arrival__time__month=date.month,
                arrival__time__day=date.day,
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyRetrieveSerializer
        return JourneySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.INT,
                description="Filter by source id (ex. ?source=2)",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.INT,
                description="Filter by destination id (ex. ?destination=2)",
            ),
            OpenApiParameter(
                "departure_time",
                description="Filter by departure_time id (ex. ?departure_time=2024-12-24)",
            ),
            OpenApiParameter(
                "arrival_time",
                description="Filter by arrival_time id (ex. ?arrival_time=2024-12-24)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        orders = Order.objects.filter(user=self.request.user)
        return Ticket.objects.filter(order__in=orders)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        return TicketSerializer
