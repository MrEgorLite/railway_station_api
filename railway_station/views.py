from django_rest.permissions import IsAdminUser, IsStaffUser, IsAuthenticated
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
from railway_station.permissions import IsAdminOrReadOnly
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
    permission_classes = (IsAdminUser, IsStaffUser)
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, IsStaffUser)
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        return TrainSerializer


class CrewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, IsStaffUser)
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, IsStaffUser)
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, IsStaffUser)
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        return JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

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
