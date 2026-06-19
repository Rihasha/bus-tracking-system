from django.core.management.base import BaseCommand
from tracking.models import BusStop, Route, RouteStop, Bus, BusLocationHistory


class Command(BaseCommand):
    help = 'Seed Tamil Nadu bus stops, routes, and buses'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        BusLocationHistory.objects.all().delete()
        RouteStop.objects.all().delete()
        Bus.objects.all().delete()
        Route.objects.all().delete()
        BusStop.objects.all().delete()

        # ── Tamil Nadu Bus Stops ──────────────────────────────────────────────
        stops_data = [
            # Chennai District
            {'name': 'Chennai Central',         'lat': 13.0836, 'lng': 80.2751},
            {'name': 'Chennai Egmore',           'lat': 13.0782, 'lng': 80.2600},
            {'name': 'Chennai Koyambedu',        'lat': 13.0694, 'lng': 80.1948},
            {'name': 'Chennai T.Nagar',          'lat': 13.0416, 'lng': 80.2339},
            {'name': 'Chennai Tambaram',         'lat': 12.9249, 'lng': 80.1000},
            {'name': 'Chennai Guindy',           'lat': 13.0067, 'lng': 80.2206},
            {'name': 'Chennai Anna Nagar',       'lat': 13.0891, 'lng': 80.2102},
            # Major Tamil Nadu Cities
            {'name': 'Coimbatore',               'lat': 11.0168, 'lng': 76.9558},
            {'name': 'Madurai',                  'lat':  9.9252, 'lng': 78.1198},
            {'name': 'Tiruchirappalli (Trichy)',  'lat': 10.7905, 'lng': 78.7047},
            {'name': 'Salem',                    'lat': 11.6643, 'lng': 78.1460},
            {'name': 'Tirunelveli',              'lat':  8.7139, 'lng': 77.7567},
            {'name': 'Vellore',                  'lat': 12.9165, 'lng': 79.1325},
            {'name': 'Erode',                    'lat': 11.3410, 'lng': 77.7172},
            {'name': 'Tiruppur',                 'lat': 11.1085, 'lng': 77.3411},
            {'name': 'Thanjavur',                'lat': 10.7870, 'lng': 79.1378},
            {'name': 'Dindigul',                 'lat': 10.3673, 'lng': 77.9803},
            {'name': 'Kanchipuram',              'lat': 12.8358, 'lng': 79.7085},
            {'name': 'Kumbakonam',               'lat': 10.9602, 'lng': 79.3845},
            {'name': 'Cuddalore',                'lat': 11.7449, 'lng': 79.7680},
        ]

        stop_objs = {}
        for s in stops_data:
            obj = BusStop.objects.create(name=s['name'], latitude=s['lat'], longitude=s['lng'])
            stop_objs[s['name']] = obj
            self.stdout.write(f"  ✔ Stop: {s['name']}")

        # ── Routes ───────────────────────────────────────────────────────────
        routes_data = [
            {
                'name': 'Chennai City Loop',
                'source': 'Chennai Central',
                'destination': 'Chennai Tambaram',
                'stops': [
                    'Chennai Central', 'Chennai Egmore', 'Chennai Anna Nagar',
                    'Chennai T.Nagar', 'Chennai Guindy', 'Chennai Tambaram'
                ]
            },
            {
                'name': 'Chennai - Coimbatore Express',
                'source': 'Chennai Koyambedu',
                'destination': 'Coimbatore',
                'stops': ['Chennai Koyambedu', 'Vellore', 'Salem', 'Erode', 'Tiruppur', 'Coimbatore']
            },
            {
                'name': 'Chennai - Madurai Express',
                'source': 'Chennai Central',
                'destination': 'Madurai',
                'stops': ['Chennai Central', 'Kanchipuram', 'Dindigul', 'Madurai']
            },
            {
                'name': 'Trichy - Thanjavur Route',
                'source': 'Tiruchirappalli (Trichy)',
                'destination': 'Thanjavur',
                'stops': ['Tiruchirappalli (Trichy)', 'Kumbakonam', 'Thanjavur']
            },
            {
                'name': 'Madurai - Tirunelveli Route',
                'source': 'Madurai',
                'destination': 'Tirunelveli',
                'stops': ['Madurai', 'Dindigul', 'Tirunelveli']
            },
        ]

        route_objs = {}
        for r in routes_data:
            route = Route.objects.create(name=r['name'], source=r['source'], destination=r['destination'])
            for i, stop_name in enumerate(r['stops'], start=1):
                RouteStop.objects.create(route=route, stop=stop_objs[stop_name], order=i)
            route_objs[r['name']] = route
            self.stdout.write(f"  ✔ Route: {r['name']}")

        # ── Buses (with Tamil Nadu GPS coordinates) ──────────────────────────
        buses_data = [
            {'bus_number': 'TN01-AB-1001', 'plate': 'TN01AB1001', 'route': 'Chennai City Loop',
             'lat': 13.0836, 'lng': 80.2751, 'speed': 32.5},
            {'bus_number': 'TN01-AB-1002', 'plate': 'TN01AB1002', 'route': 'Chennai City Loop',
             'lat': 13.0416, 'lng': 80.2339, 'speed': 28.0},
            {'bus_number': 'TN37-CD-2001', 'plate': 'TN37CD2001', 'route': 'Chennai - Coimbatore Express',
             'lat': 11.6643, 'lng': 78.1460, 'speed': 65.0},
            {'bus_number': 'TN58-EF-3001', 'plate': 'TN58EF3001', 'route': 'Chennai - Madurai Express',
             'lat': 10.3673, 'lng': 77.9803, 'speed': 72.0},
            {'bus_number': 'TN45-GH-4001', 'plate': 'TN45GH4001', 'route': 'Trichy - Thanjavur Route',
             'lat': 10.7905, 'lng': 78.7047, 'speed': 45.0},
            {'bus_number': 'TN75-IJ-5001', 'plate': 'TN75IJ5001', 'route': 'Madurai - Tirunelveli Route',
             'lat':  9.9252, 'lng': 78.1198, 'speed': 55.0},
        ]

        for b in buses_data:
            bus = Bus.objects.create(
                bus_number=b['bus_number'],
                license_plate=b['plate'],
                status='active',
                current_route=route_objs[b['route']],
                current_lat=b['lat'],
                current_lon=b['lng'],
                speed=b['speed'],
            )
            self.stdout.write(f"  ✔ Bus: {b['bus_number']} on {b['route']}")
            
            # ── Seed Historical Data for this Bus ──
            # Generating some fake historical pings around its current location
            import random
            from django.utils import timezone
            from datetime import timedelta
            
            for i in range(10):
                timestamp = timezone.now() - timedelta(minutes=i*15)
                # Slightly shift coordinates to simulate movement
                h_lat = float(b['lat']) + (random.uniform(-0.01, 0.01))
                h_lon = float(b['lng']) + (random.uniform(-0.01, 0.01))
                BusLocationHistory.objects.create(
                    bus=bus,
                    latitude=h_lat,
                    longitude=h_lon,
                    timestamp=timestamp
                )
            self.stdout.write(f"    ↳ Seeded 10 history logs for {b['bus_number']}")

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seeded {len(stops_data)} Tamil Nadu stops, '
            f'{len(routes_data)} routes, {len(buses_data)} buses, and historical logs successfully!'
        ))
