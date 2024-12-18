# Fix from https://stackoverflow.com/questions/70943244/attributeerror-module-collections-has-no-attribute-mutablemapping
import sys
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)

from dataTypes import geoLoc
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import itertools
from pymavlink import mavutil

import requests

IP = "localhost"
END_POINT_HANDSHAKE = "handshake"
END_POINT_SENSE = "sense"

URL_HANDSHAKE = f"http://{IP}:8080/{END_POINT_HANDSHAKE}"
URL_SENSE = f"http://{IP}:8080/{END_POINT_SENSE}"


class Drone:
    def __init__(self, sysID, IP, portNumber, takeoff):
        self.sysID = sysID
        self.IP = IP
        self.portNumber = portNumber
        self.takeoff = takeoff

        self.name = f"Drone{sysID}"
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.rhinosFound = 0

        self.printInfo(f"Connecting to {IP}:{portNumber}")
        self.startConnection()

    def startConnection(self):
        self.vehicle = connect(f"tcp:{self.IP}:{self.portNumber}", wait_ready=True)
        
        if self.takeoff:
            while not self.vehicle.is_armable:
                self.printInfo(" Waiting for vehicle to initialise...", wait=True)
                time.sleep(1)
            
            self.arm()
            self.take_off(10)

    def printInfo(self, msg, wait=False):
        if wait:
            sys.stdout.write("\033[F\033[K")
            sys.stdout.write(f"\r{time.strftime('%Y-%m-%d %H:%M:%S')} - {self.name}: {next(self.spinner)} {msg}\n")
        else:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {self.name}: {msg}")        

    def arm(self):
        self.printInfo("Switch to GUIDED and arming motors")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
    
        # Wait for vehicle to arm
        while not self.vehicle.armed:
            self.printInfo(" Waiting for arming...", wait=True)
            time.sleep(1)


    def take_off(self, altitude):
        self.printInfo("Taking off!")
        self.vehicle.simple_takeoff(altitude) 

        while True:
            self.printInfo(f" Altitude: {self.vehicle.location.global_relative_frame.alt}", wait=True)
            # Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt >= altitude * 0.95:
                self.printInfo("Reached target altitude")
                break
            time.sleep(1) 

    def get_position(self) -> geoLoc:
        pos = self.vehicle.location.global_relative_frame
        return geoLoc(pos.lat, pos.lon, pos.alt)

    def send_to_waypoint(self, waypoint):
        point = LocationGlobalRelative(waypoint.lat, waypoint.lon, waypoint.alt)
        self.vehicle.simple_goto(point)
            
    def is_waypoint_reached(self, waypoint : geoLoc, threshold=10):
        pos = self.get_position()
        dist = pos.distance_to(waypoint)
        return dist < threshold
    
    def get_rhinos_found(self):
        return self.rhinosFound
    
    def reset_rhinos_found(self):
        self.rhinosFound = 0

class DroneListener(Drone):
    def __init__(self, sysID, IP, portNumber, mavlinkHandler):
        self.mavlinkHandler = mavlinkHandler
        super().__init__(sysID, IP, portNumber, False)

    def startConnection(self):
        # self.vehicle = mavutil.mavlink_connection(f'udpin:{self.IP}:{self.portNumber}')
        self.vehicle = self.mavlinkHandler

    def get_position(self):
        while True:
            msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            if not msg:
                continue
            elif msg.get_srcSystem()==self.sysID:
                msg = msg.to_dict()
                return geoLoc(msg["lat"] * 1e-7, msg["lon"] * 1e-7, msg["alt"]  * 1e-3)
            else:
                continue

class DroneManager:
    def __init__(self):
        self.drones = {}

    def get_drone_position(self, droneID):
        return self.drones[droneID].get_position()
    
    def get_rhinos_found(self, droneID):
        return self.drones[droneID].get_rhinos_found()
    
    def reset_rhinos_found(self, droneID):
        self.drones[droneID].reset_rhinos_found()

    def send_drone_to_waypoint(self, droneID, waypoint):
        self.drones[droneID].send_to_waypoint(waypoint)

    def getDroneNames(self):
        return [self.drones[droneID].name for droneID in self.drones.keys()]

    def getDroneIDs(self):
        return self.drones.keys()
    
    def rhinoFound(self, droneID):
        self.drones[droneID].rhinosFound += 1

    def createSwarm(self, n, takeoff=True, listenOnly=False):
        if listenOnly:
            mavlinkHandler = mavutil.mavlink_connection(f'udpin:localhost:14550')
            for i in range(n):
                self.drones[i+1] = DroneListener(sysID=i+1, IP="localhost", portNumber=14550, mavlinkHandler=mavlinkHandler)
        else:
            for i in range(n):
                self.drones[i+1] = Drone(sysID=i+1, IP="localhost", portNumber=5762 + i*10, takeoff=takeoff)

    def manualSearch(self, droneID, step=0.01):
        print(f"@@@@ Manual search\n\tDrone ID: {droneID}\n\tPress a,s,d,w to move the drone\n\tPress e to sense\n\tPress q to quit")
        while True:
            key = input()
            if key == "q":
                break
            elif key == "e":
                print(f"@@@@ Sensing with drone {droneID}")
                 # Sense
                response = requests.post(URL_SENSE, json={"drone_id": droneID}).json()["sense_status"]
                print(f"\t\t{response}")
            elif key == "a":
                print(f"@@@@ Moving drone {droneID} west 100m")
                pos = self.drones[droneID].get_position()
                pos.lon -= step
                self.drones[droneID].send_to_waypoint(pos)
            elif key == "d":
                print(f"@@@@ Moving drone {droneID} east 100m")
                pos = self.drones[droneID].get_position()
                pos.lon += step
                self.drones[droneID].send_to_waypoint(pos)
            elif key == "w":
                print(f"@@@@ Moving drone {droneID} north 100m")
                pos = self.drones[droneID].get_position()
                pos.lat += step
                self.drones[droneID].send_to_waypoint(pos)
            elif key == "s":
                print(f"@@@@ Moving drone {droneID} south 100m")
                pos = self.drones[droneID].get_position()
                pos.lat -= step
                self.drones[droneID].send_to_waypoint(pos)
            elif key in ["1", "2", "3", "4", "5"]:
                print(f"@@@@ Switching to drone {key}")
                droneID = int(key)
            else:
                continue

if __name__ == "__main__":
    dm = DroneManager()
    # dm.createSwarm(5, takeoff=True, listenOnly=False)
    dm.createSwarm(5, takeoff=False, listenOnly=False)
    print(dm.getDroneIDs())
    dm.manualSearch(1)

    # for droneID in dm.getDroneIDs():
    #     print(dm.get_drone_position(droneID))


    # dm.send_drone_to_waypoint(1, geoLoc(0.05791118977016864, 36.91820202292705, 10))

    
   

    