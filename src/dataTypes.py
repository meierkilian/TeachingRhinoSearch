import math
import pymap3d as pm

class geoLoc():
    def __init__(self, lat, lon, alt=None):
        self.lat = float(lat)
        self.lon = float(lon)
        if alt is not None:
            alt = float(alt)
        self.alt = alt
        self._validate()

    def _validate(self):
        if not (-90 <= self.lat <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not (-180 <= self.lon <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        
    def offset(self, east, north, up=None):
        if self.alt:
            lat, lon, alt = pm.enu2geodetic(east, north, up or 0, self.lat, self.lon, self.alt)
            return geoLoc(lat, lon, alt)
        else:
            lat, lon, _ = pm.enu2geodetic(east, north, 0, self.lat, self.lon, 0)
            return geoLoc(lat, lon)
        
    def distTo(self, other : "geoLoc", hzOnly=False):
        if hzOnly:
            _, _, srange = pm.geodetic2aer(self.lat, self.lon, 0, other.lat, other.lon, 0)
        else:
            _, _, srange = pm.geodetic2aer(self.lat, self.lon, self.alt or 0, other.lat, other.lon, other.alt or 0)
        return srange
    
    def __str__(self):
        return f"Latitude: {self.lat:.6f}, Longitude: {self.lon:.6f}, Altitude: {self.alt:.1f}, Google Maps: https://www.google.com/maps/search/{self.lat:.6f},{self.lon:.6f}"
    
class geoCircle():
    def __init__(self, center: geoLoc, radius):
        self.center = center
        self.radius = radius
        self._validate()

    def _validate(self):
        if self.radius < 0:
            raise ValueError("Radius must be positive")
        
    def intersection3circle(self, other1, other2):
        # This function calculates the intersection point of three circles
        # using the method of trilateration.
        # WARNING: This function will return an intersection even if the circles do not intersect in a single point

        x1, y1, _ = pm.geodetic2enu(self.center.lat, self.center.lon, 0, self.center.lat, self.center.lon, 0)
        x2, y2, _ = pm.geodetic2enu(other1.center.lat, other1.center.lon, 0, self.center.lat, self.center.lon, 0)
        x3, y3, _ = pm.geodetic2enu(other2.center.lat, other2.center.lon, 0, self.center.lat, self.center.lon, 0)
        r1, r2, r3 = self.radius, other1.radius, other2.radius

        A = 2 * (x2 - x1)
        B = 2 * (y2 - y1)
        D = 2 * (x3 - x1)
        E = 2 * (y3 - y1)

        C = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
        F = r1**2 - r3**2 - x1**2 + x3**2 - y1**2 + y3**2

        denominator = (A * E - B * D)
        if denominator == 0:
            raise ValueError("The circles do not intersect in a single point")

        x = (C * E - F * B) / denominator
        y = (A * F - D * C) / denominator
       
        lat, lon, _ = pm.enu2geodetic(x, y, 0, self.center.lat, self.center.lon, 0)
        return geoLoc(lat, lon, self.center.alt)
    
if __name__ == "__main__":
    # p1 = geoLoc(0.027467533748910547, 36.90286865957662, 10)
    # p2 = geoLoc(0.028472888028040794, 36.90449713737817, 10)
    # p3 = geoLoc(0.02221388343159939, 36.90697883603347, 10)
    # print(p1.distTo(p1))  # Should print 0.0
    # print(p1.distTo(p2))  # Should print approximately 200m
    # print(p1.distTo(p3))  # Should print approximately 800m
    # print(p2.distTo(p1))  # Should print approximately 200m
    
    p1 = geoLoc(0.027467533748910547, 36.90286865957662)
    p2 = geoLoc(0.028472888028040794, 36.90449713737817)
    p3 = geoLoc(0.02221388343159939, 36.90697883603347)
    c1 = geoCircle(p1, 309)
    c2 = geoCircle(p2, 200)
    c3 = geoCircle(p3, 552)
    # print(c1.intersection3circle(c2, c3))  # Should print the intersection point of the three circles
    
    print(p1)
    print(p1.offset(100, 100))