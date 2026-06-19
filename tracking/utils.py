import heapq
import math


class DijkstraAlgorithm:
    def __init__(self, stops, routes):
        self.stops = stops
        self.routes = routes
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = {stop.id: [] for stop in self.stops}
        for route in self.routes:
            # Sort route stops by order
            route_stops = route.routestop_set.all().order_by('order')
            for i in range(len(route_stops) - 1):
                stop1 = route_stops[i].stop
                stop2 = route_stops[i+1].stop
                
                # Simple weight: distance or just 1 for now
                dist = self._calculate_distance(stop1.latitude, stop1.longitude, stop2.latitude, stop2.longitude)
                graph[stop1.id].append((stop2.id, dist, route.name))
        return graph

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        # Haversine formula
        import math
        R = 6371  # Earth radius in km
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2) * math.sin(d_lat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) * math.sin(d_lon / 2))
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def get_shortest_path(self, start_stop_id, end_stop_id):
        distances = {stop.id: float('infinity') for stop in self.stops}
        distances[start_stop_id] = 0
        pq = [(0, start_stop_id, [])]
        
        visited = set()

        while pq:
            (current_dist, current_stop_id, path) = heapq.heappop(pq)
            
            if current_stop_id in visited:
                continue
            
            visited.add(current_stop_id)
            new_path = path + [current_stop_id]

            if current_stop_id == end_stop_id:
                return new_path, current_dist

            for neighbor_id, weight, route_name in self.graph.get(current_stop_id, []):
                distance = current_dist + weight
                if distance < distances[neighbor_id]:
                    distances[neighbor_id] = distance
                    heapq.heappush(pq, (distance, neighbor_id, new_path))
        

def check_geofencing(bus, lat, lon):
    from .models import BusStop, User, Notification
    stops = BusStop.objects.all()
    for stop in stops:
        # Haversine distance
        lat1, lon1 = float(lat), float(lon)
        lat2, lon2 = float(stop.latitude), float(stop.longitude)
        R = 6371
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2)**2 + math.cos(math.radians(lat1)) * 
             math.cos(math.radians(lat2)) * math.sin(d_lon / 2)**2)
        dist = R * 2 * math.asin(math.sqrt(a))

        if dist < 0.5: # 500 meters
            msg = f"Alert: Bus #{bus.bus_number} is approaching {stop.name} (ETA < 2 mins)"
            # Send to all passengers for simplicity in this demo
            passengers = User.objects.filter(role='passenger')
            for p in passengers:
                Notification.objects.get_or_create(user=p, message=msg)
