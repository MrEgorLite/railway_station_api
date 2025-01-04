from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ["id", "name"]


class TrainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Train
        fields = ["id", "name", "cargo_num", "places_in_cargo", "train_type"]


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ["id", "name", "latitude", "longitude"]


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]

    def validate(self, attrs):
        Route.validate(
            attrs["source"],
            attrs["destination"],
            attrs["distance"],
            ValidationError
        )
        return attrs


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )
    destination = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class TicketTakenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat")


class JourneySerializer(serializers.ModelSerializer):
    tickets_available = serializers.IntegerField(read_only=True)
    taken_places = TicketTakenSerializer(
        many=True,
        read_only=True,
        source="tickets"
    )

    class Meta:
        model = Journey
        fields = [
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crews",
            "tickets_available",
            "taken_places",
        ]

    def validate(self, attrs):
        Journey.validate(
            attrs["departure_time"], attrs["arrival_time"], ValidationError
        )
        return attrs


class JourneyListSerializer(JourneySerializer):
    route = serializers.StringRelatedField()
    train = serializers.StringRelatedField()
    crews = serializers.StringRelatedField(many=True)


class JourneyRetrieveSerializer(JourneySerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainSerializer(read_only=True)
    crews = CrewSerializer(many=True, read_only=True)


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ["id", "cargo", "seat", "journey", "order"]
        read_only_fields = ("id", "order")

    def validate(self, attrs):
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            ValidationError
        )
        return attrs


class TicketListSerializer(TicketSerializer):
    journey = serializers.StringRelatedField()


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "user", "tickets"]
        read_only_fields = ["id", "created_at", "user"]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order

class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True)
