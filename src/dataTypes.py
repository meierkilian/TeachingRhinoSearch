import math

class geoLoc():
    def __init__(self, lat, lon, alt=None):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self._validate()

    def _validate(self):
        if not (-90 <= self.lat <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not (-180 <= self.lon <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        
    def distTo(self, other):
        # Using Haversine formula to calculate the distance between two geographical points
        R = 6371*1000  # Radius of the Earth in m
        dlat = math.radians(other.lat - self.lat)
        dlon = math.radians(other.lon - self.lon)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(self.lat)) * math.cos(math.radians(other.lat)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance
    
    def __str__(self):
        return f"Latitude: {self.lat}, Longitude: {self.lon}, Altitude: {self.alt}"
    
if __name__ == "__main__":
    p1 = geoLoc(0.027467533748910547, 36.90286865957662, 10)
    p2 = geoLoc(0.028472888028040794, 36.90449713737817, 10)
    p3 = geoLoc(0.02221388343159939, 36.90697883603347, 10)
    print(p1.distTo(p1))  # Should print 0.0
    print(p1.distTo(p2))  # Should print approximately 200m
    print(p1.distTo(p3))  # Should print approximately 800m
    print(p2.distTo(p1))  # Should print approximately 200m
    