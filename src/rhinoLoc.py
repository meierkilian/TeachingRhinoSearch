import random
import math

class RhinoLoc:
    def __init__(self, n, coord1, coord2):
        self.n = n
        self.coord1 = coord1
        self.coord2 = coord2
        self.rhino_positions = self._generate_rhino_positions()

    def _generate_rhino_positions(self):
        rhino_positions = []
        for _ in range(self.n):
            lat = random.uniform(self.coord1[0], self.coord2[0])
            lon = random.uniform(self.coord1[1], self.coord2[1])
            rhino_positions.append((lat, lon))
        return rhino_positions

    def get_rhino_positions(self):
        return self.rhino_positions

    def regenerate_rhino_positions(self):
        self.rhino_positions = self._generate_rhino_positions()

    def distance_to_closest_rhino(self, position):
        min_distance = float('inf')
        for rhino_position in self.rhino_positions:
            distance = self._calculate_distance(position, rhino_position)
            if distance < min_distance:
                min_distance = distance
        return min_distance

    def _calculate_distance(self, pos1, pos2):
        # Using Haversine formula to calculate the distance between two geographical points
        R = 6371*1000  # Radius of the Earth in m
        lat1, lon1 = pos1
        lat2, lon2 = pos2
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance