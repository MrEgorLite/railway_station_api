from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class TrainType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=100)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType, on_delete=models.CASCADE, related_name="trains"
    )

    def __str__(self):
        return f"{self.name} ({self.train_type})"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField()

    @staticmethod
    def validate(source: str, destination: str, distance: int, exception: Exception()) -> None:
        if source == destination:
            raise exception("source and destination routes cannot be the same")
        if distance <= 0:
            raise exception("distance must be greater than zero")

    def clean(self):
        super().clean()
        self.validate(self.source.name, self.destination.name, self.distance, ValidationError)

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super().save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="journeys")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew, related_name="journeys")

    @staticmethod
    def validate(departure_time: datetime, arrival_time: datetime, exception: Exception()) -> None:
        if departure_time == arrival_time:
            raise exception("departure_time and arrival_time cannot be the same")

    def clean(self) -> None:
        self.validate(self.departure_time, self.arrival_time, ValidationError)

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super().save(
            force_insert,
            force_update,
            using,
            update_fields
        )


    def __str__(self):
        return (
            f"{self.route.source.name} - "
            f"{self.route.destination.name} "
            f"({self.departure_time} - "
            f"{self.arrival_time})"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    def __str__(self):
        return str(self.tickets)


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    @staticmethod
    def validate_ticket(cargo, seat, cinema_hall, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(cinema_hall, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {train_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None
    ):
        self.full_clean()
        return super().save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    def __str__(self):
        return f"seat: {self.seat}, journey: {str(self.journey)}"
