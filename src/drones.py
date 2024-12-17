from pymavlink import mavutil
from pymavlink.mavutil import mavlink as mavlink
from dataTypes import geoLoc
import sys

# Fix from https://stackoverflow.com/questions/70943244/attributeerror-module-collections-has-no-attribute-mutablemapping
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)

import time
from dronekit import connect, VehicleMode, LocationGlobalRelative

class Drone:
    def __init__(self, IP="localhost", portNumber=5762):
        print(f"Connecting to drone at {IP}:{portNumber}")
        self.vehicle = connect(f"tcp:{IP}:{portNumber}", wait_ready=True)
        while not self.vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)
        self.take_off(10)        

    def take_off(self, altitude):
        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

    
        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        self.vehicle.simple_takeoff(altitude)  # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto
        #  (otherwise the command after Vehicle.simple_takeoff will execute
        #   immediately).
        while True:
            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            # Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt >= altitude * 0.95:
                print("Reached target altitude")
                break
            time.sleep(1) 

    # def get_position(self):
    #     msg = self.mavLinkHandle.recv_match(type='GLOBAL_POSITION_INT', blocking=True).to_dict()
    #     return geoLoc(msg['lat']*1e-7, msg['lon']*1e-7, msg['relative_alt']*1e-3)

    def send_to_waypoint(self, waypoint):
        point = LocationGlobalRelative(waypoint.lat, waypoint.lon, waypoint.alt)
        self.vehicle.simple_goto(point)
        
    # def get_sysID(self):
    #     return self.mavLinkHandle.target_system
        
    # def is_waypoint_reached(self, waypoint, threshold=10):
    #     pos = self.get_position()

class DroneManager:
    def __init__(self):
        self.drones = {}

    def add_drone(self, name, IP="localhost", portNumber=5762):
        self.drones[name] = Drone(IP, portNumber)

    def get_drone_position(self, droneID):
        return self.drones[droneID].get_position()

    def send_drone_to_waypoint(self, droneID, waypoint):
        self.drones[droneID].send_to_waypoint(waypoint)

    def createSwarm(self, n):
        for i in range(n):
            self.add_drone(f"Drone{i+1}", portNumber=5762 + i*10)

    def getDroneIDs(self):
        return self.drones.keys()

if __name__ == "__main__":
    dm = DroneManager()
    dm.createSwarm(5)
    print(dm.getDroneIDs())

    for droneID in dm.getDroneIDs():
        input(f"Press Enter to send {droneID} to waypoint")
        dm.send_drone_to_waypoint(droneID, geoLoc(0.027467533748910547, 36.90286865957662, 10))

    # while True:
    #     pos = dm.get_drone_position(droneID = 1)
    #     print(pos.lat, pos.lon, pos.alt)

    # while True:
    #     port = input("Enter port number: ")
    #     drone = Drone(portNumber=port)
    #     id = drone.get_sysID()
    #     print(f"drone sysID: {id}")
    #     print(drone.get_position())