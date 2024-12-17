import random
from dataTypes import geoLoc

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
            rhino_positions.append(geoLoc(lat, lon))
        return rhino_positions

    def get_rhino_positions(self):
        return self.rhino_positions

    def regenerate_rhino_positions(self):
        self.rhino_positions = self._generate_rhino_positions()

    def distance_to_closest_rhino(self, position : geoLoc):
        min_distance = float('inf')
        for rhino_position in self.rhino_positions:
            distance = position.distTo(rhino_position)
            if distance < min_distance:
                min_distance = distance
        return min_distance

   