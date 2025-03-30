import csv
import logging
from math import radians
import numpy as np

from kivy.app import App
from kivy.clock import Clock
from kivy_garden.mapview import MapView, MapMarker
from lineMapLayer import LineMapLayer
from scipy.signal import find_peaks

logging.basicConfig(level=logging.INFO)


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Storage for loaded data
        self.gps_points = []       # List of (lat, lon) from gps_data.csv
        self.accel_z_values = []   # List of Z-axis values from data.csv
        self.current_index = 0     # Current position index in the GPS data
        self.car_marker = None     # Marker representing the moving car
        self.route_layer = None    # Layer for drawing the route line

        # For road-quality detection
        self.batch_size = 5      # Number of Z-axis readings to analyze
        self.detected_peaks = set()  # store the global indices of peaks already marked


    def build(self):
        """
        Initializes the map.
        """
        self.mapview = MapView(zoom=15, lat=50.4501, lon=30.5234)
        return self.mapview

    def on_start(self):
        """
        Called automatically once the application has started.
        1. Load CSV data (GPS + accelerometer)
        2. Create markers and layers
        3. Schedule the update function
        """
        self.load_data()

        # Log how many rows we loaded
        logging.info(f"Loaded {len(self.gps_points)} GPS points from gps_data.csv")
        logging.info(f"Loaded {len(self.accel_z_values)} Z-values from data.csv")

        # If no GPS points loaded, just log and return
        if not self.gps_points:
            logging.error("No GPS data loaded. Check gps_data.csv.")
            return

        # Center the map on the first GPS point
        self.mapview.lat = self.gps_points[0][0]
        self.mapview.lon = self.gps_points[0][1]

        # Create the car marker at the first GPS point
        self.car_marker = MapMarker(
            lat=self.gps_points[0][0],
            lon=self.gps_points[0][1],
            source="images/car.png",  # or use a default marker
            anchor_x=0.5,
            anchor_y=0.5,
        )
        self.mapview.add_widget(self.car_marker)

        # Create a route layer for drawing lines
        self.route_layer = LineMapLayer(coordinates=[], color=[1, 0, 0, 1], width=2)
        # Add the layer to the map
        self.mapview.add_layer(self.route_layer, mode="scatter")

        # Schedule the map updates every second
        Clock.schedule_interval(self.update, 1.0)

    def load_data(self):
        """
        Loads GPS data from gps_data.csv and accelerometer Z-axis data from data.csv.
        Skips headers if present. Checks row lengths to avoid out-of-range errors.
        """
        try:
            # Load GPS data
            with open("gps_data.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                # If your file truly has a header like "lat,lon", keep this:
                next(reader, None)  # Skip header if present
                for row in reader:
                    # Ensure at least 2 columns exist
                    if len(row) < 2:
                        continue
                    lat = float(row[0])
                    lon = float(row[1])
                    self.gps_points.append((lat, lon))

            # Load accelerometer data
            with open("data.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    # Ensure at least 3 columns exist
                    if len(row) < 3:
                        continue
                    z_value = float(row[2])
                    self.accel_z_values.append(z_value)

        except Exception as e:
            logging.error(f"Error loading CSV data: {e}")

    def update(self, dt):
        if self.current_index >= len(self.gps_points):
            Clock.unschedule(self.update)
            return

        gps_point = self.gps_points[self.current_index]
        self.update_car_marker(gps_point)
        self.add_route_point(gps_point)
        self.current_index += 1

        if len(self.accel_z_values) >= self.batch_size:
            self.check_road_quality()

    def update_car_marker(self, point):
        """
        Moves the car marker to a new GPS coordinate.
        """
        lat, lon = point
        if self.car_marker:
            self.car_marker.lat = lat
            self.car_marker.lon = lon
        # Optionally re-center map if desired:
        # self.mapview.center_on(lat, lon)

    def add_route_point(self, point):
        """
        Adds a point to the route line layer so we see the path behind the car.
        """
        if self.route_layer is not None:
            self.route_layer.add_point(point)

    def check_road_quality(self):
        if self.current_index < self.batch_size:
            return

        start_idx = self.current_index - self.batch_size
        end_idx = self.current_index
        z_batch = np.array(self.accel_z_values[start_idx:end_idx])

        # Thresholds
        baseline = 16667
        threshold_high = baseline + 50
        threshold_low = baseline - 50

        # Compute the average of the batch
        avg_z = np.mean(z_batch)

        # Only place one marker for the entire batch
        global_idx = start_idx + (self.batch_size // 2)  # pick the middle index for location

        # Check if we’ve already placed a marker for this batch
        if global_idx in self.detected_peaks:
            return

        self.detected_peaks.add(global_idx)

        # If average is above threshold => bump
        if avg_z > threshold_high:
            if global_idx < len(self.gps_points):
                lat, lon = self.gps_points[global_idx]
                self.set_bump_marker((lat, lon))

        # If average is below threshold => pothole
        elif avg_z < threshold_low:
            if global_idx < len(self.gps_points):
                lat, lon = self.gps_points[global_idx]
                self.set_pothole_marker((lat, lon))

    def set_bump_marker(self, point):
        """
        Places a bump marker on the map at the given GPS coordinate.
        """
        lat, lon = point
        marker = MapMarker(
            lat=lat,
            lon=lon, # your bump icon
            anchor_x=0.5,
            anchor_y=0.5,
        )
        self.mapview.add_widget(marker)

    def set_pothole_marker(self, point):
        """
        Places a pothole marker on the map at the given GPS coordinate.
        """
        lat, lon = point
        marker = MapMarker(
            lat=lat,
            lon=lon,
            source="images/pothole.png",
            anchor_x=0.5,
            anchor_y=0.5,
        )
        self.mapview.add_widget(marker)


if __name__ == "__main__":
    MapViewApp().run()
