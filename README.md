# Real-Time Bus Tracking and Passenger Assistance System

This project is a Django-based web application for tracking public buses in real-time. It features Dijkstra's algorithm for shortest path calculation and live GPS updates.

## Tech Stack
- **Backend:** Python, Django, Django REST Framework
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript (AJAX)
- **Map:** Google Maps API
- **Database:** SQLite (default)

## Main Features
1.  **Authentication Module:** Secure login/registration for Passengers and Admins.
2.  **Passenger Dashboard:** View live ETAs, active buses, and notifications.
3.  **Live Tracking:** Google Maps integration with AJAX polling for real-time marker updates.
4.  **Admin Panel:** Manage routes, stops, buses, and schedules via standard Django Admin.
5.  **Route Optimization:** Dijkstra's algorithm to find the fastest path between bus stops.
6.  **Simulation Engine:** A management command to simulate real-time GPS movement.

## Setup Instructions

### 1. Requirements
Ensure you have Python installed. The following libraries were used:
```bash
pip install django djangorestframework channels channels-redis googlemaps geopy
```

### 2. Run Migrations & Seed Data
Initialize the database and load sample routes and buses:
```bash
python manage.py makemigrations tracking
python manage.py migrate
python manage.py shell -c "from tracking.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin')"
python seed_data.py
```

### 3. Start the Server
Run the Django development server:
```bash
python manage.py runserver
```

### 4. Start the GPS Simulation (Optional)
In a separate terminal, run the movement simulator:
```bash
python manage.py simulate_bus
```

### 5. Access the Platform
- **Landing Page:** `http://127.0.0.1:8000/`
- **Admin Dashboard:** `http://127.0.0.1:8000/admin/` (Login: `admin` / `admin123`)
- **Passenger Login:** Use the registration form or login with the admin account to access the dashboard.

## Important Note
To see the live map, you must replace `YOUR_API_KEY_HERE` in `tracking/templates/tracking/live_tracking.html` with a valid Google Maps JavaScript API key.
