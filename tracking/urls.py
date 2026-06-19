from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('live-tracking/', views.live_tracking, name='live_tracking'),
    path('api/buses/', views.bus_api, name='bus_api'),
    path('api/stops/', views.get_stops_api, name='stops_api'),
    path('api/shortest-path/', views.shortest_path_api, name='shortest_path_api'),
    path('route/<int:route_id>/', views.route_details, name='route_details'),
    path('notifications/', views.notifications_page, name='notifications'),
    path('historical-data/', views.historical_data_view, name='historical_data'),
    path('export-history/', views.export_history_csv, name='export_history'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('api/eta/<int:bus_id>/<int:stop_id>/', views.bus_eta_api, name='bus_eta_api'),
    path('api/update-location/', views.update_bus_location_api, name='update_bus_location_api'),
    path('admin/algorithm/', views.algorithm_details_view, name='algorithm_details'),
    # Seat availability
    path('api/seats/<int:bus_id>/', views.seat_availability_api, name='seat_availability_api'),
    path('api/seats/<int:bus_id>/update/', views.update_seats_api, name='update_seats_api'),
    # SOS
    path('api/sos/', views.sos_trigger_api, name='sos_trigger_api'),
    path('api/sos/list/', views.sos_list_api, name='sos_list_api'),
    path('api/sos/<int:alert_id>/resolve/', views.sos_resolve_api, name='sos_resolve_api'),
    path('sos-dashboard/', views.sos_dashboard, name='sos_dashboard'),
]
