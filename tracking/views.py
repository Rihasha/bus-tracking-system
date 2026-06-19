from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import User, Bus, Route, BusStop, Notification, Schedule, BusLocationHistory, SOSAlert
from .forms import PassengerRegistrationForm, LoginForm
from .utils import DijkstraAlgorithm
from django.db.models import Avg, Count
import json
import math

def index(request):
    return render(request, 'tracking/index.html')

def register_view(request):
    if request.method == 'POST':
        form = PassengerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = PassengerRegistrationForm()
    return render(request, 'tracking/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'tracking/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    buses = Bus.objects.filter(status='active')
    routes = Route.objects.all()
    notifications = request.user.notifications.all().order_by('-created_at')[:5]
    pending_sos = SOSAlert.objects.filter(status='pending').count() if request.user.role == 'admin' else 0
    return render(request, 'tracking/dashboard.html', {
        'buses': buses,
        'routes': routes,
        'notifications': notifications,
        'pending_sos': pending_sos,
    })

@login_required
def live_tracking(request):
    return render(request, 'tracking/live_tracking.html')

@login_required
def bus_api(request):
    buses = Bus.objects.filter(status='active')
    data = []
    for b in buses:
        data.append({
            'id': b.id,
            'bus_number': b.bus_number,
            'current_lat': float(b.current_lat),
            'current_lon': float(b.current_lon),
            'speed': float(b.speed),
            'status': b.status,
            'current_route__name': b.current_route.name if b.current_route else None,
            # Seat availability data
            'total_seats': b.total_seats,
            'occupied_seats': b.occupied_seats,
            'available_seats': b.available_seats,
            'seat_percentage': b.seat_percentage,
        })
    return JsonResponse(data, safe=False)

@login_required
def get_stops_api(request):
    stops = BusStop.objects.all().values('id', 'name', 'latitude', 'longitude')
    return JsonResponse(list(stops), safe=False)

@login_required
def shortest_path_api(request):
    start_stop_id = request.GET.get('start')
    end_stop_id = request.GET.get('end')
    
    if not start_stop_id or not end_stop_id:
        return JsonResponse({'error': 'Missing start or end stop'}, status=400)
    
    stops = BusStop.objects.all()
    routes = Route.objects.all()
    dijkstra = DijkstraAlgorithm(stops, routes)
    
    path_ids, distance = dijkstra.get_shortest_path(int(start_stop_id), int(end_stop_id))
    
    if path_ids:
        path_stops = []
        for sid in path_ids:
            stop = BusStop.objects.get(id=sid)
            path_stops.append({
                'id': stop.id,
                'name': stop.name,
                'lat': float(stop.latitude),
                'lng': float(stop.longitude)
            })
        return JsonResponse({'path': path_stops, 'distance': distance})
    else:
        return JsonResponse({'error': 'No path found'}, status=404)

@login_required
def route_details(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    stops = route.routestop_set.all().order_by('order')
    return render(request, 'tracking/route_details.html', {'route': route, 'stops': stops})

@login_required
def notifications_page(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'tracking/notifications.html', {'notifications': notifications})

@login_required
def historical_data_view(request):
    history = BusLocationHistory.objects.all().order_by('-timestamp')[:100]
    return render(request, 'tracking/historical_data.html', {'history': history})

@login_required
def export_history_csv(request):
    import csv
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bus_history.csv"'
    writer = csv.writer(response)
    writer.writerow(['Bus Number', 'Latitude', 'Longitude', 'Timestamp'])
    history = BusLocationHistory.objects.all().order_by('-timestamp')
    for h in history:
        writer.writerow([h.bus.bus_number, h.latitude, h.longitude, h.timestamp])
    return response

@login_required
def analytics_dashboard(request):
    avg_speeds = Bus.objects.all().values('bus_number').annotate(avg_speed=Avg('speed'))
    route_traffic = BusLocationHistory.objects.values('bus__current_route__name').annotate(pings=Count('id')).order_by('-pings')
    return render(request, 'tracking/analytics.html', {
        'avg_speeds': avg_speeds,
        'route_traffic': route_traffic
    })

@login_required
def bus_eta_api(request, bus_id, stop_id):
    bus = get_object_or_404(Bus, id=bus_id)
    stop = get_object_or_404(BusStop, id=stop_id)
    
    lat1, lon1 = float(bus.current_lat), float(bus.current_lon)
    lat2, lon2 = float(stop.latitude), float(stop.longitude)
    
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) * math.sin(d_lat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) * math.sin(d_lon / 2))
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    speed = float(bus.speed)
    # Smart prediction: factor in time of day (rush hour slower)
    hour = timezone.now().hour
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        speed_factor = 0.6  # rush hour: 40% slower
    elif 22 <= hour or hour <= 5:
        speed_factor = 1.3  # night: 30% faster
    else:
        speed_factor = 1.0
    
    effective_speed = speed * speed_factor if speed > 0 else 30 * speed_factor
    eta_minutes = (distance / effective_speed) * 60

    return JsonResponse({
        'bus_id': bus.id,
        'bus_number': bus.bus_number,
        'stop_id': stop.id,
        'stop_name': stop.name,
        'distance_km': round(distance, 2),
        'eta_minutes': round(eta_minutes, 1),
        'speed_kmh': round(effective_speed, 1),
        'available_seats': bus.available_seats,
        'seat_percentage': bus.seat_percentage,
    })

@login_required
def update_bus_location_api(request):
    bus_id = request.GET.get('id')
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    speed = request.GET.get('speed', 0)

    if not all([bus_id, lat, lon]):
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    bus = get_object_or_404(Bus, id=bus_id)
    bus.current_lat = lat
    bus.current_lon = lon
    bus.speed = speed
    bus.save()

    BusLocationHistory.objects.create(bus=bus, latitude=lat, longitude=lon)

    from .utils import check_geofencing
    check_geofencing(bus, lat, lon)

    return JsonResponse({'status': 'success', 'bus': bus.bus_number, 'pos': [lat, lon]})

@login_required
def algorithm_details_view(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    return render(request, 'tracking/algorithm_info.html')

# ─── SEAT AVAILABILITY API ───────────────────────────────────────────────────

@login_required
def seat_availability_api(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    return JsonResponse({
        'bus_id': bus.id,
        'bus_number': bus.bus_number,
        'total_seats': bus.total_seats,
        'occupied_seats': bus.occupied_seats,
        'available_seats': bus.available_seats,
        'seat_percentage': bus.seat_percentage,
    })

@login_required
def update_seats_api(request, bus_id):
    """Admin/driver API to update seat count"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    bus = get_object_or_404(Bus, id=bus_id)
    try:
        data = json.loads(request.body)
        occupied = int(data.get('occupied_seats', bus.occupied_seats))
        bus.occupied_seats = min(occupied, bus.total_seats)
        bus.save()
        return JsonResponse({
            'status': 'updated',
            'available_seats': bus.available_seats,
            'seat_percentage': bus.seat_percentage,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ─── SOS ALERT API ──────────────────────────────────────────────────────────

@login_required
def sos_trigger_api(request):
    """Passenger triggers SOS from live_tracking page"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        bus_id = data.get('bus_id')
        lat = data.get('latitude')
        lon = data.get('longitude')
        message = data.get('message', 'Emergency! Immediate assistance needed.')
        bus = Bus.objects.filter(id=bus_id).first() if bus_id else None

        alert = SOSAlert.objects.create(
            user=request.user,
            bus=bus,
            latitude=lat,
            longitude=lon,
            message=message,
        )

        # Notify all admins
        admins = User.objects.filter(role='admin')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"🚨 SOS ALERT from {request.user.username}"
                        f"{' on Bus ' + bus.bus_number if bus else ''}! "
                        f"Message: {message}"
            )

        return JsonResponse({'status': 'sos_sent', 'alert_id': alert.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def sos_list_api(request):
    """Admin: list all pending SOS alerts"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Forbidden'}, status=403)
    alerts = SOSAlert.objects.filter(status='pending').values(
        'id', 'user__username', 'bus__bus_number', 'latitude', 'longitude', 'message', 'created_at'
    )
    return JsonResponse(list(alerts), safe=False)

@login_required
def sos_resolve_api(request, alert_id):
    """Admin: resolve an SOS alert"""
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Forbidden'}, status=403)
    alert = get_object_or_404(SOSAlert, id=alert_id)
    alert.status = 'resolved'
    alert.resolved_at = timezone.now()
    alert.save()
    return JsonResponse({'status': 'resolved'})

@login_required
def sos_dashboard(request):
    """Admin SOS management page"""
    if request.user.role != 'admin':
        return redirect('dashboard')
    alerts = SOSAlert.objects.all()
    return render(request, 'tracking/sos_dashboard.html', {'alerts': alerts})
