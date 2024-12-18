import random
from dataTypes import geoLoc

class RhinoLoc:
    def __init__(self, n, coord1, coord2):
        self.n = n
        self.coord1 = coord1
        self.coord2 = coord2
        self.rhino_positions = self._generate_rhino_positions()
        self.rhino_found = [False] * self.n

    def _generate_rhino_positions(self):
        rhino_positions = []
        for _ in range(self.n):
            lat = random.uniform(self.coord1[0], self.coord2[0])
            lon = random.uniform(self.coord1[1], self.coord2[1])
            rhino_positions.append(geoLoc(lat, lon))
        return rhino_positions

    def get_rhino_positions(self):
        return self.rhino_positions
    
    def get_rhino_found(self):
        return self.rhino_found

    def regenerate_rhino_positions(self):
        self.rhino_positions = self._generate_rhino_positions()
        self.rhino_found = [False] * self.n

    def distance_to_closest_rhino(self, position : geoLoc):
        min_distance = float('inf')
        for i, rhino_position in enumerate(self.rhino_positions):
            if self.rhino_found[i]: # Ignore found rhinos
                continue
            distance = position.distTo(rhino_position)
            if distance < min_distance:
                min_distance = distance
                min_index = i
        print(min_distance, min_index)
        return min_distance, min_index
    
    def senseRhino(self, position : geoLoc, range=2000, foundThreshold=500):
        distance, index = self.distance_to_closest_rhino(position)
        if distance > range:
            return {"state": "out_of_range", "distance": -1}
        elif distance < foundThreshold:
            self.rhino_found[index] = True
            return {"state": "found", "distance": distance}
        else:
            return {"state": "in_range", "distance": distance}
   