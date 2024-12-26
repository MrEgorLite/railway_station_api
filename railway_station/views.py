from rest_framework import viewsets, mixins

from railway_station.models import (
    TrainType,
    Train,
    Crew,
    Station,
    Route,
    Journey,
    Order,
    Ticket,
)
from railway_station.serializers import (
    TrainSerializer,
    TrainTypeSerializer,
    CrewSerializer,
    StationSerializer,
    RouteSerializer,
    JourneySerializer,
    OrderSerializer,
    TicketSerializer,
    TrainListSerializer,
    RouteListSerializer,
    JourneyListSerializer,
)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        return TrainSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        return JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        orders = Order.objects.filter(user=self.request.user)
        return Ticket.objects.filter(order__in=orders)
