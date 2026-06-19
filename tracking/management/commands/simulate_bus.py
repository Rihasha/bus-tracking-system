import time
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from tracking.models import Bus, BusStop, BusLocationHistory

class Command(BaseCommand):
    help = 'Simulates real-time bus GPS updates.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting real-time simulation...'))
        
        while True:
            buses = Bus.objects.filter(status='active', current_route__isnull=False)
            for bus in buses:
                # Randomly shift coordinates slightly to simulate movement
                lat_shift = Decimal(str(random.uniform(-0.0005, 0.0005)))
                lon_shift = Decimal(str(random.uniform(-0.0005, 0.0005)))
                
                bus.current_lat += lat_shift
                bus.current_lon += lon_shift
                bus.speed = Decimal(str(random.randint(20, 50)))
                bus.save()
                
                # Log to history
                BusLocationHistory.objects.create(
                    bus=bus,
                    latitude=bus.current_lat,
                    longitude=bus.current_lon
                )

                # GEOFENCING: Trigger notifications
                from tracking.utils import check_geofencing
                check_geofencing(bus, bus.current_lat, bus.current_lon)
                
                self.stdout.write(f"Updated Bus {bus.bus_number}: {bus.current_lat}, {bus.current_lon}")
            
            time.sleep(5)
