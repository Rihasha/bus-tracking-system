from django.contrib import admin
from .models import User, Bus, Route, BusStop, RouteStop, Schedule, Notification, BusLocationHistory, SOSAlert

admin.site.register(User)
admin.site.register(BusStop)
admin.site.register(Route)
admin.site.register(RouteStop)
admin.site.register(Schedule)
admin.site.register(Notification)
admin.site.register(BusLocationHistory)

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['bus_number', 'license_plate', 'status', 'current_route', 'speed', 'total_seats', 'occupied_seats', 'last_updated']
    list_editable = ['occupied_seats']
    list_filter = ['status']

@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'bus', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    readonly_fields = ['created_at']
