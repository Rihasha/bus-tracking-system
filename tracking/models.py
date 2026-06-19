from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    IS_PASSENGER = 'passenger'
    IS_ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (IS_PASSENGER, 'Passenger'),
        (IS_ADMIN, 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=IS_PASSENGER)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class BusStop(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name

class Route(models.Model):
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    stops = models.ManyToManyField(BusStop, through='RouteStop')

    def __str__(self):
        return self.name

class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(BusStop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

class Bus(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]
    
    bus_number = models.CharField(max_length=20, unique=True)
    license_plate = models.CharField(max_length=20)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    current_route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    current_lat = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    current_lon = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    speed = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    # SEAT AVAILABILITY
    total_seats = models.PositiveIntegerField(default=40)
    occupied_seats = models.PositiveIntegerField(default=0)

    @property
    def available_seats(self):
        return max(0, self.total_seats - self.occupied_seats)

    @property
    def seat_percentage(self):
        if self.total_seats == 0:
            return 0
        return round((self.occupied_seats / self.total_seats) * 100)

    def __str__(self):
        return f"Bus {self.bus_number}"

class Schedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    def __str__(self):
        return f"{self.bus} on {self.route} at {self.departure_time}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"

class BusLocationHistory(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Bus location histories"

# SOS ALERT MODEL
class SOSAlert(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sos_alerts')
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    message = models.TextField(blank=True, default='Emergency! Immediate assistance needed.')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SOS by {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
